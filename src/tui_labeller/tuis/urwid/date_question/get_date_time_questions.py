import urwid

from tui_labeller.file_read_write_helper import write_to_file
from tui_labeller.tuis.urwid.date_question.get_date_time_question import (
    DateTimeEdit,
)


class DateTimeQuestions:
    def __init__(self):
        self.palette = [
            ("normal", "white", "black"),
            ("highlight", "white", "dark red"),
            ("error", "yellow", "dark red"),
        ]

        # Define questions
        self.questions = [
            ("Date (YYYY-MM-DD): ", True),  # date_only=True
            ("Date & Time (YYYY-MM-DD HH:MM): ", False),  # date_only=False
            ("ADate & Time (YYYY-MM-DD HH:MM): ", False),  # date_only=False
        ]

        # Create error display
        self.error_display = urwid.AttrMap(urwid.Text(""), "error")

        # Create pile and inputs list
        self.pile = urwid.Pile([])
        self.inputs = []

        # Create question widgets
        for question_text, date_only in self.questions:
            edit = DateTimeEdit(question_text, date_only=date_only)
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


# def get_date_time_question():
#     date_edit = DateTimeEdit("Date (YYYY-MM-DD): ", date_only=True)
#     datetime_edit = DateTimeEdit("Date & Time (YYYY-MM-DD HH:MM): ")

#     error_display = urwid.Text("")
#     date_edit.error_text = error_display
#     datetime_edit.error_text = error_display

#     pile = urwid.Pile(
#         [
#             urwid.Text("Enter Date and/or Time:"),
#             date_edit,
#             datetime_edit,
#             error_display,
#         ]
#     )

#     fill = urwid.Filler(pile, "top")
#     loop = urwid.MainLoop(fill)

#     write_to_file(filename="eg.txt", content=f"start", append=False)
#     loop.run()
