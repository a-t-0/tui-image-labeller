import urwid

from src.tui_labeller.file_read_write_helper import write_to_file
from src.tui_labeller.tuis.urwid.autocomplete_filtering import (
    get_filtered_suggestions,
)
from tui_labeller.tuis.urwid.InputValidationQuestion import (
    InputValidationQuestion,
)


class InputValidationQuestions:
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
            self.fill,
            self.palette,
            unhandled_input=self.handle_unhandled_input_major,
        )

    def handle_unhandled_input_major(self, key):
        # TODO: determine if you should move this into the "keypress" method
        # of the InputValidationQuestion object.
        if key == "enter":
            current_pos = self.pile.focus_position
            next_pos = current_pos + 1
            # Check if the next position is within the valid range of input boxes
            if next_pos < len(self.inputs):
                self.pile.focus_position = next_pos
                focused_widget = self.pile.focus
                if isinstance(focused_widget, urwid.AttrMap):
                    focused_widget.base_widget.update_autocomplete()
            return  # Prevent raising ValueE

        # TODO: determine if you should move this into the "keypress" method
        # of the InputValidationQuestion object.
        if key == "tab":
            write_to_file(
                filename="eg.txt",
                content=f"Focused_widget={focused_widget}",
                append=False,
            )
            print(f"Afocused_widget={focused_widget}")
            current_pos = self.pile.focus_position
            focused_widget = self.pile.focus
            if isinstance(focused_widget, urwid.AttrMap):
                input_widget = focused_widget.base_widget
                # Get the filtered suggestions based on current input text
                remaining_suggestions = get_filtered_suggestions(
                    input_text=input_widget.edit_text,
                    available_suggestions=input_widget.suggestions,
                )
                # If there's exactly one suggestion, apply it
                if len(remaining_suggestions) == 1:
                    new_text = remaining_suggestions[0]
                    input_widget.set_edit_text(new_text)
                    input_widget.set_edit_pos(
                        len(new_text)
                    )  # Move cursor to the end
            else:
                print(f"focused_widget={focused_widget}")
            return  # Prevent raising ValueError

        if key == "down":
            current_pos = self.pile.focus_position
            if current_pos == len(self.inputs) - 1:  # If at last question
                self.pile.focus_position = 0  # Go to first question
                focused_widget = self.pile.focus
                if isinstance(focused_widget, urwid.AttrMap):
                    focused_widget.base_widget.update_autocomplete()

        if key == "up":
            current_pos = self.pile.focus_position
            if current_pos == 0:  # If at first question
                self.pile.focus_position = (
                    len(self.inputs) - 1
                )  # Go to last question
                focused_widget = self.pile.focus
                if isinstance(focused_widget, urwid.AttrMap):
                    focused_widget.base_widget.update_autocomplete()
        # TODO: if cursor is at the first question and up is pressed, go to last question.

        # TODO: if cursor is at the last question and down is pressed, go to first question.
        # raise ValueError(f"STOPPED at:{key}")

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
