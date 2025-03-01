import urwid
from typeguard import typechecked


def write_to_file(*, filename, content, append=False):
    """Write content to a file with option to append or overwrite.

    Args:
        filename (str): Name of the file to write to
        content: Content to write (string, list, or any object with __str__)
        append (bool): If True, append to existing file; if False, overwrite (default: False)
    """
    mode = "a" if append else "w"
    with open(filename, mode) as file:
        # Handle different types of content
        if isinstance(content, (list, tuple)):
            file.writelines([str(item) + "\n" for item in content])
        else:
            file.write(str(content) + "\n")


class QuestionWidget(urwid.WidgetWrap):
    def __init__(self, question, choices, question_index, total_questions):
        self.question = question
        self.choices = choices
        self.question_index = question_index
        self.total_questions = total_questions
        self.selected = None
        self.choice_widgets = []
        self.radio_group = []
        self.setup_widgets()

    def get_answer_in_focus(self) -> int:
        """Returns the column index of the answer you just selected."""
        monitored_nr: int = self._wrapped_widget._contents.focus
        the_obj = self._wrapped_widget._contents[monitored_nr]
        for i, elem in enumerate(the_obj):
            if isinstance(elem, urwid.widget.columns.Columns):
                focus_column: int = elem.get_focus_column()
                # write_to_file(filename="eg.txt", content=f'i={i}, elem.dir={dir(elem)}, type={type(elem)}',append=True)
                write_to_file(
                    filename="eg.txt",
                    content=(
                        f"i={i}, FOUNDfocus_column={focus_column},"
                        f" type={type(elem)}"
                    ),
                    append=True,
                )
        if focus_column:
            return focus_column
        if focus_column is None:
            raise ValueError("Did not find which column was in focus.")
        if focus_column == 0:
            return 0

    def setup_widgets(self):
        for label in self.choices:
            radio_button = urwid.RadioButton(
                self.radio_group,
                label,
                state=False,
                on_state_change=self.on_select,
            )
            self.choice_widgets.append(
                urwid.AttrMap(radio_button, "normal", "selected")
            )
        choices_row = urwid.Columns(self.choice_widgets, dividechars=1)
        question_text = urwid.Text(
            ("question", f"Q{self.question_index + 1}: {self.question}")
        )
        pile = urwid.Pile([question_text, urwid.Divider(), choices_row])
        super().__init__(pile)

    def on_select(self, radio_button, new_state):

        if new_state:
            self.selected = radio_button.label
            self.confirm_selection()
            write_to_file(
                filename="eg.txt",
                content=(
                    f"new_state={new_state}, radio_button={radio_button},"
                    f" self.selected={self.selected}"
                ),
                append=True,
            )
        else:
            write_to_file(
                filename="eg.txt",
                content=(
                    f"new_state={new_state}, radio_button={radio_button},"
                    f" self.selected={self.selected}"
                ),
                append=True,
            )

    def confirm_selection(self):
        for widget in self.choice_widgets:
            radio = widget.base_widget
            write_to_file(
                filename="eg.txt",
                content=(
                    f"radio={radio.label}, self.selected={self.selected},"
                    f" dir={widget.get_focus_map()}"
                ),
                append=True,
            )
            if radio.label == self.selected:
                widget.set_attr_map({None: "selected"})
            else:
                radio.set_state(False, do_callback=False)
                widget.set_attr_map({None: "normal"})

    def keypress(self, size, key):
        if key == "enter":
            if self.selected is not None:
                selected_ans_col = self.get_answer_in_focus()

                for i, widget in enumerate(self.choice_widgets):
                    radio = widget.base_widget
                    write_to_file(
                        filename="eg.txt",
                        content=f"widget={widget},selected_ans_col={selected_ans_col}",
                        append=True,
                    )
                    if i == selected_ans_col:
                        if radio.state:
                            radio.set_state(False, do_callback=False)
                            self.selected = None
                        else:
                            radio.set_state(True, do_callback=False)
                            self.selected = radio.label
                    else:
                        radio.set_state(False, do_callback=False)
                self.confirm_selection()
                return None
            else:
                write_to_file(
                    filename="eg.txt", content=f"self={self}", append=True
                )
        return super().keypress(size, key)


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
        QuestionWidget(q["question"], q["choices"], i, len(questions))
        for i, q in enumerate(questions)
    ]

    main_widget = urwid.ListBox(urwid.SimpleFocusListWalker(question_widgets))

    def exit_on_q(key):
        if key in ("q", "Q"):
            raise urwid.ExitMainLoop()

    main_loop = urwid.MainLoop(main_widget, palette, unhandled_input=exit_on_q)
    write_to_file(filename="eg.txt", content=f"START", append=False)
    main_loop.run()
