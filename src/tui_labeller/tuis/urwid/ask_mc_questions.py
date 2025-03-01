import urwid
from typeguard import typechecked

from tui_labeller.file_read_write_helper import write_to_file
from tui_labeller.tuis.urwid.MultipleChoiceWidget import MultipleChoiceWidget


@typechecked
def built_receipt_from_urwid(
    receipt_owner_account_holder: str,
    receipt_owner_bank: str,
    receipt_owner_account_holder_type: str,
) -> None:

    palette = [
        ("normal", "white", "black"),
        ("selected", "black", "yellow"),
        ("question", "light cyan", "black"),
    ]

    questions = [
        {
            "question": "What is the capital of France?",
            "choices": ["Paris", "London", "Berlin", "Eindje"],
            "correct": "Paris",
        },
        {
            "question": "Which planet is known as the Red Planet?",
            "choices": ["Mars", "Jupiter", "Venus"],
            "correct": "Mars",
        },
        {
            "question": "What is 2 + 2?",
            "choices": ["3", "4", "5"],
            "correct": "4",
        },
    ]

    question_widgets = [
        MultipleChoiceWidget(q["question"], q["choices"], i, len(questions))
        for i, q in enumerate(questions)
    ]

    main_widget = urwid.ListBox(urwid.SimpleFocusListWalker(question_widgets))

    def exit_on_q(key):
        if key in ("q", "Q"):
            raise urwid.ExitMainLoop()

    main_loop = urwid.MainLoop(main_widget, palette, unhandled_input=exit_on_q)
    write_to_file(filename="eg.txt", content=f"START", append=False)
    main_loop.run()
