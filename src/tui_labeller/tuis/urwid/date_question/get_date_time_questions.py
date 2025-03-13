import urwid

from src.tui_labeller.file_read_write_helper import write_to_file
from src.tui_labeller.tuis.urwid.date_question.get_date_time_question import (
    DateTimeEdit,
)

# (DateTimeEdit class code from previous responses)


def get_date_time_question():
    date_edit = DateTimeEdit("Date (YYYY-MM-DD): ", date_only=True)
    datetime_edit = DateTimeEdit("Date & Time (YYYY-MM-DD HH:MM): ")

    error_display = urwid.Text("")
    date_edit.error_text = error_display
    datetime_edit.error_text = error_display

    pile = urwid.Pile(
        [
            urwid.Text("Enter Date and/or Time:"),
            date_edit,
            datetime_edit,
            error_display,
        ]
    )

    fill = urwid.Filler(pile, "top")
    loop = urwid.MainLoop(fill)

    write_to_file(filename="eg.txt", content=f"start", append=False)
    loop.run()
