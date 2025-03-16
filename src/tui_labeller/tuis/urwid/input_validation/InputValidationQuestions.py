import urwid

from tui_labeller.tuis.urwid.input_validation.autocomplete_filtering import (
    get_filtered_suggestions,
)
from tui_labeller.tuis.urwid.input_validation.InputValidationQuestion import (
    InputValidationQuestion,
)


class InputValidationQuestions:
    def __init__(self):

        self.questions = [
            (
                "Question 1: ",
                ["apple", "apricot", "avocado"],
                ["car0", "swag", "some"],
            ),
            (
                "Question 2: ",
                ["banana", "blueberry", "blackberry"],
                ["car1", "swag", "some"],
            ),
            (
                "Question 3: ",
                ["cat", "caterpillar", "cactus"],
                ["car2", "swag", "some"],
            ),
        ]
        ai_suggestions_palet_name: str = "ai_suggestions"
        history_suggestions_palet_name: str = "history_suggestions"
        self.palette = [
            ("normal", "white", "black"),
            ("highlight", "white", "dark red"),
            (ai_suggestions_palet_name, "yellow", "dark blue"),
            (history_suggestions_palet_name, "yellow", "dark green"),
        ]

        self.ai_suggestion_box = urwid.AttrMap(
            urwid.Text("", align="left"), ai_suggestions_palet_name
        )
        self.history_suggestion_box = urwid.AttrMap(
            urwid.Text("", align="left"), history_suggestions_palet_name
        )

        self.pile = urwid.Pile([])
        self.inputs = []
        for question, ai_suggestions, history_suggestions in self.questions:
            edit = InputValidationQuestion(
                caption=question,
                ai_suggestions=ai_suggestions,
                history_suggestions=history_suggestions,
                ai_suggestion_box=self.ai_suggestion_box,
                history_suggestion_box=self.history_suggestion_box,
                pile=self.pile,
            )
            attr_edit = urwid.AttrMap(edit, "normal")
            edit.owner = attr_edit
            self.inputs.append(attr_edit)

        descriptor_col_width: int = 12
        """On the RHS of the tuple below, the tuple:(sizing_mode,
        height_or_weight), is:

        sizing_mode: Determines how the widget's size is calculated. Common modes are:
        "pack": The widget determines its own size based on its content (it "packs" itself to its natural size).
        "flow": Used for widgets that can adjust their width based on the available space (not used here).
        "fixed": The widget has a fixed size specified explicitly.
        "weight": The widget's size is proportional to a weight value, sharing available space with other weighted widgets.
        """
        self.pile.contents = [
            (self.inputs[0], ("pack", None)),
            (self.inputs[1], ("pack", None)),
            (self.inputs[2], ("pack", None)),
            (urwid.Divider(), ("pack", None)),
            (
                urwid.Columns(
                    [
                        (descriptor_col_width, urwid.Text("AI suggestions: ")),
                        self.ai_suggestion_box,
                    ]
                ),
                ("pack", None),
            ),
            (
                urwid.Columns(
                    [
                        (
                            descriptor_col_width,
                            urwid.Text("History suggestions: "),
                        ),
                        self.history_suggestion_box,
                    ]
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

    def move_to_next_answer(self, current_pos, key):
        total_inputs = len(self.inputs)
        # Calculate next position with wrap-around
        if current_pos == total_inputs - 1:  # At last question
            next_pos = 0  # Go to first
        elif current_pos == 0 and key == "up":  # At first question going up
            next_pos = total_inputs - 1  # Go to last
        else:
            next_pos = current_pos + (
                1 if key in ["enter", "down", "tab"] else -1
            )

        # Only move if next_pos is within valid range
        if 0 <= next_pos < total_inputs:
            self.pile.focus_position = next_pos
            focused_widget = self.pile.focus
            if isinstance(focused_widget, urwid.AttrMap):
                focused_widget.base_widget.update_autocomplete()

    def handle_unhandled_input_major(self, key):

        # Handle Enter key
        if key == "enter":
            current_pos = self.pile.focus_position
            self.move_to_next_answer(current_pos=current_pos, key=key)
            return

        # Handle Tab key with autocomplete
        if key == "tab":
            current_pos = self.pile.focus_position
            focused_widget = self.pile.focus

            if isinstance(focused_widget, urwid.AttrMap):
                input_widget = focused_widget.base_widget
                remaining_suggestions = get_filtered_suggestions(
                    input_text=input_widget.edit_text,
                    available_suggestions=input_widget.suggestions,
                )
                if len(remaining_suggestions) == 1:
                    new_text = remaining_suggestions[0]
                    input_widget.set_edit_text(new_text)
                    input_widget.set_edit_pos(len(new_text))
                    self.move_to_next_answer(current_pos=current_pos, key=key)
            else:
                raise ValueError(f"focused_widget={focused_widget}")

        # Handle Down key
        if key == "down":
            current_pos = self.pile.focus_position
            self.move_to_next_answer(current_pos=current_pos, key=key)
            return

        # Handle Up key
        if key == "up":
            current_pos = self.pile.focus_position
            self.move_to_next_answer(current_pos=current_pos, key=key)
            return
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
