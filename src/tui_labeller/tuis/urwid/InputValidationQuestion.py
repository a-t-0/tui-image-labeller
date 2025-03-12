import re

import urwid

from tui_labeller.file_read_write_helper import write_to_file
from tui_labeller.tuis.urwid.autocomplete_filtering import (
    get_filtered_suggestions,
)


class InputValidationQuestion(urwid.Edit):
    def __init__(
        self, caption, suggestions=None, autocomplete_box=None, pile=None
    ):
        super().__init__(caption=caption)
        self.suggestions = suggestions or []
        self.autocomplete_box = autocomplete_box
        self.pile = pile
        self._in_autocomplete: bool = False

    def valid_char(self, ch):
        return len(ch) == 1 and (ch.isalpha() or ch in [":", "*"])

    def keypress(self, size, key):
        """Overrides the internal/urwid pip package method "keypress" to map
        incoming keys into separate behaviour."""
        write_to_file(
            filename="eg.txt",
            content=f"key={key}, self.edit_text={self.edit_text}",
            append=True,
        )

        if key == "enter":
            return "enter"
        if key == "tab":
            return "tab"
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
                    # self.set_edit_text(remaining_suggestions[0])
                    new_text = remaining_suggestions[0]
                    self.set_edit_text(new_text)
                    # Move cursor to end of autocompleted word.
                    self.set_edit_pos(len(new_text))
            else:
                self.owner.set_attr_map({None: "normal"})
        finally:
            self._in_autocomplete = False  # Reset flag
