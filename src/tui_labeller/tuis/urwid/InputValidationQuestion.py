import re
from typing import List

import urwid
from typeguard import typechecked

from tui_labeller.file_read_write_helper import write_to_file


@typechecked
def get_filtered_suggestions(
    *, input_text: str, available_suggestions: List[str]
) -> List[str]:
    """
    Filter suggestions based on input text, matching from start with wildcard support.
    Special case: '*' alone shows all available suggestions.

    Args:
        input_text (str): The text entered by user, can include '*' as wildcard
        available_suggestions (list): List of possible suggestion strings

    Returns:
        list: Filtered suggestions based on input criteria
    """
    input_text = input_text.strip()

    # Special case: if input is '*', return all suggestions
    if input_text == "*":
        return available_suggestions

    # If no input, return all suggestions
    if not input_text:
        return available_suggestions

    # Handle wildcard case
    if "*" in input_text:
        # Split input by wildcard
        parts = input_text.lower().split("*")
        prefix = parts[0]  # What comes before the wildcard

        # Filter suggestions
        filtered = [
            suggestion
            for suggestion in available_suggestions
            if suggestion.lower().startswith(prefix)
            and all(part in suggestion.lower() for part in parts[1:] if part)
        ]
    else:
        # Original filtering for non-wildcard case
        filtered = [
            suggestion
            for suggestion in available_suggestions
            if suggestion.lower().startswith(input_text.lower())
        ]

    # If no matches found, return ['-']
    return filtered if filtered else ["-"]


class InputValidationQuestion(urwid.Edit):
    def __init__(
        self, caption, suggestions=None, autocomplete_box=None, pile=None
    ):
        super().__init__(caption=caption)
        self.suggestions = suggestions or []
        self.autocomplete_box = autocomplete_box
        self.pile = pile
        self._in_autocomplete: bool = False

    def handle_autocomplete(self, key, size):
        """Handle autocomplete logic based on input key and suggestions.

        Args:
            key: The pressed key
            size: The size parameter for keypress
        Returns:
            The result of keypress or None if handled
        Raises:
            ValueError: When autocomplete conditions aren't met
        """
        if not self.suggestions:
            write_to_file(
                filename="eg.txt",
                content=f"self.suggestions={self.suggestions}",
                append=True,
            )
            return super().keypress(size, key)

        # Handle automatic substitution when '*' yields single match
        if "*" in self.edit_text:
            matches = [s for s in self.suggestions if self._match_pattern(s)]
            if len(matches) == 1:
                self.set_edit_text(matches[0])
                self.owner.set_attr_map({None: "normal"})
                write_to_file(
                    filename="eg.txt",
                    content=f"self.edit_text={self.edit_text}",
                    append=True,
                )
                return None
            elif len(matches) == 0:
                raise ValueError("No matches found for pattern")
            # TODO: do stuff here.
            # If multiple matches, continue to tab handling

        # Handle tab key press
        if key == "tab":
            matches = [s for s in self.suggestions if self._match_pattern(s)]

            if len(matches) == 1:
                self.set_edit_text(matches[0])
                self.owner.set_attr_map({None: "normal"})
                return None
            elif len(matches) == 0:
                raise ValueError("No matching suggestion found")
            else:
                raise ValueError("Multiple ambiguous suggestions available")

        return super().keypress(size, key)

    def valid_char(self, ch):
        return len(ch) == 1 and (ch.isalpha() or ch in [":", "*"])

    def keypress(self, size, key):
        write_to_file(
            filename="eg.txt",
            content=f"key={key}, self.edit_text={self.edit_text}",
            append=True,
        )
        if key in ["tab", "*"]:
            return self.handle_autocomplete(key, size)
        elif key == "enter":
            return "enter"
        elif key in ("up", "down"):
            if self.pile:
                current_pos = self.pile.focus_position
                new_pos = current_pos - 1 if key == "up" else current_pos + 1
                if 0 <= new_pos < len(self.pile.contents) - 2:
                    self.pile.focus_position = new_pos
                    focused_widget = self.pile.focus
                    if isinstance(focused_widget, urwid.AttrMap):
                        focused_widget.base_widget.update_autocomplete()
                    return None
            return key
        elif key in ("delete", "backspace", "left", "right"):
            write_to_file(
                filename="eg.txt",
                content=f"self.edit_text={self.edit_text}",
                append=True,
            )
            result = super().keypress(size, key)
            self.update_autocomplete()
            return result
        elif self.valid_char(key):
            result = super().keypress(size, key)
            self.update_autocomplete()
            return result
        return None

    def _match_pattern(self, suggestion):
        pattern = self.edit_text.lower().replace("*", ".*")
        return bool(re.match(f"^{pattern}$", suggestion.lower()))

    def update_autocomplete(self):
        if self._in_autocomplete:  # Prevent recursion
            return

        if not self.autocomplete_box:
            return

        self._in_autocomplete = True  # Set flag
        try:
            remaining_suggestions = get_filtered_suggestions(
                input_text=self.edit_text,
                available_suggestions=self.suggestions,
            )

            suggestions_text = ", ".join(remaining_suggestions)
            write_to_file(
                filename="eg.txt",
                content=f"suggestions_text={suggestions_text}",
                append=True,
            )
            self.autocomplete_box.base_widget.set_text(suggestions_text)
            self.autocomplete_box.base_widget._invalidate()

            if "*" in self.edit_text:
                if len(remaining_suggestions) == 1:
                    # Use set_edit_text instead of direct assignment to avoid triggering signals
                    self.set_edit_text(remaining_suggestions[0])
            else:
                self.owner.set_attr_map({None: "normal"})
        finally:
            self._in_autocomplete = False  # Reset flag


class QuestionApp:
    def __init__(self):
        self.questions = [
            ("Question 1: ", ["apple", "apricot", "avocado"]),
            ("Question 2: ", ["banana", "blueberry", "blackberry"]),
            ("Question 3: ", ["cat", "caterpillar", "cactus"]),
        ]

        self.palette = [
            ("normal", "white", "black"),
            ("highlight", "white", "dark red"),
            ("autocomplete", "yellow", "dark blue"),
        ]

        self.autocomplete_box = urwid.AttrMap(
            urwid.Text("", align="left"), "autocomplete"
        )

        self.pile = urwid.Pile([])
        self.inputs = []
        for question, suggestions in self.questions:
            edit = InputValidationQuestion(
                question, suggestions, self.autocomplete_box, self.pile
            )
            attr_edit = urwid.AttrMap(edit, "normal")
            edit.owner = attr_edit
            self.inputs.append(attr_edit)

        self.pile.contents = [
            (self.inputs[0], ("pack", None)),
            (self.inputs[1], ("pack", None)),
            (self.inputs[2], ("pack", None)),
            (urwid.Divider(), ("pack", None)),
            (
                urwid.Columns(
                    [(30, urwid.Text("Autocomplete: ")), self.autocomplete_box]
                ),
                ("pack", None),
            ),
        ]

        self.fill = urwid.Filler(self.pile, valign="top")
        self.loop = urwid.MainLoop(
            self.fill, self.palette, unhandled_input=self.handle_input
        )

    def handle_input(self, key):
        print(f"Unhandled input: {key}")
        write_to_file(
            filename="eg.txt", content=f"Unhandled input: {key}", append=False
        )
        # TODO: if cursor is at the first question and up is pressed, go to last question.

        # TODO: if cursor is at the last question and down is pressed, go to first question.
        raise ValueError(f"STOPPED at:{key}")

    def run(self):
        def update_autocomplete(widget, new_text):
            widget.update_autocomplete()

        for input_widget in self.inputs:
            urwid.connect_signal(
                input_widget.base_widget, "change", update_autocomplete
            )

        if self.inputs:
            self.pile.focus_position = 0
            self.inputs[0].base_widget.update_autocomplete()

        self.loop.run()
