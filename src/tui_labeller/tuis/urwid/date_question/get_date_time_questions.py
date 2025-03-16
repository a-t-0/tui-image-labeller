import urwid

from tui_labeller.file_read_write_helper import write_to_file
from tui_labeller.tuis.urwid.date_question.get_date_time_question import (
    DateTimeEdit,
)


class DateTimeQuestions:
    def __init__(self):
        ai_suggestions_palet_name: str = "ai_suggestions"
        descriptor_col_width: int = 12

        self.palette = [
            ("normal", "white", "black"),
            ("highlight", "white", "dark red"),
            ("error", "yellow", "dark magenta"),
            (ai_suggestions_palet_name, "yellow", "dark blue"),
        ]

        # Define questions.
        self.questions = [
            ("Date (YYYY-MM-DD): ", True, ["2025-04-04"]),
            ("Date & Time (YYYY-MM-DD HH:MM): ", False, ["2025-04-04-15:55"]),
            ("ADate & Time (YYYY-MM-DD HH:MM): ", False, ["2025-04-04-15:43"]),
        ]

        self.ai_suggestion_box = urwid.AttrMap(
            urwid.Text("", align="left"), ai_suggestions_palet_name
        )

        # Create error display
        self.error_display = urwid.AttrMap(urwid.Text(""), "error")

        # Create pile and inputs list
        self.pile = urwid.Pile([])
        self.inputs = []

        # Create question widgets.
        for question_text, date_only, ai_suggestions in self.questions:
            edit = DateTimeEdit(
                caption=question_text,
                date_only=date_only,
                ai_suggestions=ai_suggestions,
                ai_suggestion_box=self.ai_suggestion_box,
                pile=self.pile,
            )
            edit.error_text = self.error_display
            attr_edit = urwid.AttrMap(edit, "normal")
            edit.owner = attr_edit
            self.inputs.append(attr_edit)

        # Set up pile contents dynamically
        pile_contents = [
            (urwid.Text("Enter Date and/or Time:"), ("pack", None))
        ]
        pile_contents.extend(
            (input_widget, ("pack", None)) for input_widget in self.inputs
        )
        pile_contents.extend(
            [
                (urwid.Divider(), ("pack", None)),
                (
                    urwid.Columns(
                        [
                            (
                                descriptor_col_width,
                                urwid.Text("AI suggestions: "),
                            ),
                            self.ai_suggestion_box,
                        ]
                    ),
                    ("pack", None),
                ),
                (self.error_display, ("pack", None)),
            ]
        )
        self.pile.contents = pile_contents

        self.fill = urwid.Filler(self.pile, valign="top")
        self.loop = urwid.MainLoop(
            self.fill, self.palette, unhandled_input=self.handle_unhandled_input
        )

    def move_to_next_answer(self, current_pos, key):
        total_inputs = len(self.inputs)
        # Calculate next position with wrap-around
        if current_pos == total_inputs - 1 and key in [
            "enter",
            "down",
            "tab",
        ]:  # At last question
            next_pos = 0  # Go to first
        elif current_pos == 0 and key == "up":  # At first question going up
            next_pos = total_inputs - 1  # Go to last
        else:
            next_pos = current_pos + (
                1 if key in ["enter", "down", "tab"] else -1
            )

        # Only move if next_pos is within valid range
        if 0 <= next_pos < total_inputs:
            self.pile.focus_position = next_pos + 1  # +1 because of header text
            return True
        return False

    def handle_unhandled_input(self, key):
        current_pos = self.pile.focus_position - 1  # -1 to account for header
        if key in ("enter", "down", "tab", "up"):

            if current_pos >= 0:  # Ensure we're not on the header
                self.move_to_next_answer(current_pos, key)

        if key == "q":  # Add quit functionality
            # Save results before quitting
            results = {
                "date": self.inputs[0].base_widget.edit_text,
                "datetime": self.inputs[1].base_widget.edit_text,
            }

            raise urwid.ExitMainLoop()

        if key == "next_question":
            if self.pile.focus_position == len(self.inputs):
                self.pile.focus_position = 1
            else:
                self.pile.focus_position += 1  # +1 because of header text
            # raise NotImplementedError("Move to next question")

        if key == "previous_question":
            write_to_file(
                filename="eg.txt",
                content=f"self.inputs={self.inputs}",
                append=True,
            )
            if self.pile.focus_position == 1:
                self.pile.focus_position = len(self.inputs)
            else:
                self.pile.focus_position -= 1  # +1 because of header text

    def run(self):
        if self.inputs:
            self.pile.focus_position = (
                1  # Start at first question (after header)
            )

        write_to_file(filename="eg.txt", content="start", append=False)
        self.loop.run()


def get_date_time_question():
    app = DateTimeQuestions()
    app.run()
