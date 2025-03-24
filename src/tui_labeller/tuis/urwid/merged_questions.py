from typing import List, Union

import urwid

from tui_labeller.file_read_write_helper import write_to_file
from tui_labeller.tuis.urwid.date_question.DateTimeQuestion import (
    DateTimeQuestion,
)
from tui_labeller.tuis.urwid.input_validation.InputValidationQuestion import (
    InputValidationQuestion,
)
from tui_labeller.tuis.urwid.mc_question.MultipleChoiceWidget import (
    MultipleChoiceWidget,
)
from tui_labeller.tuis.urwid.question_data_classes import (
    DateQuestionData,
    InputValidationQuestionData,
    MultipleChoiceQuestionData,
)


class QuestionnaireApp:
    def __init__(
        self,
        questions: List[
            Union[
                DateQuestionData,
                InputValidationQuestionData,
                MultipleChoiceQuestionData,
            ]
        ],
    ):
        """Initialize the questionnaire application with a list of
        questions."""
        self.descriptor_col_width = 20
        self.palette = self._setup_palette()
        self.questions = questions
        self.inputs = []
        self.pile = urwid.Pile([])

        # Setup UI elements
        self.ai_suggestion_box = self._create_suggestion_box("ai_suggestions")
        self.history_suggestion_box = self._create_suggestion_box(
            "history_suggestions"
        )
        self.error_display = urwid.AttrMap(urwid.Text(""), "error")

        # Build questionnaire
        self._build_questionnaire()
        self.fill = urwid.Filler(self.pile, valign="top")
        self.loop = urwid.MainLoop(
            self.fill, self.palette, unhandled_input=self._handle_input
        )

    def _setup_palette(self) -> List[tuple]:
        """Setup color palette for the UI."""
        return [
            ("normal", "white", "black"),
            ("highlight", "white", "dark red"),
            ("error", "yellow", "dark red"),
            ("ai_suggestions", "yellow", "dark blue"),
            ("history_suggestions", "yellow", "dark green"),
            ("mc_question_palette", "light cyan", "black"),
        ]

    def _create_suggestion_box(self, palette_name: str) -> urwid.AttrMap:
        """Create a suggestion box widget with specified palette."""
        return urwid.AttrMap(urwid.Text("", align="left"), palette_name)

    def _create_question_widget(
        self,
        question_data: Union[
            DateQuestionData,
            InputValidationQuestionData,
            MultipleChoiceQuestionData,
        ],
        question_count: int,
    ):
        """Create appropriate widget based on question type."""
        if isinstance(question_data, DateQuestionData):
            widget = DateTimeQuestion(
                caption=question_data.caption,
                date_only=question_data.date_only,
                ai_suggestions=question_data.ai_suggestions,
                ai_suggestion_box=self.ai_suggestion_box,
                pile=self.pile,
            )
            widget.error_text = self.error_display
            attr_widget = urwid.AttrMap(widget, "normal")
            widget.owner = attr_widget
            return attr_widget

        elif isinstance(question_data, InputValidationQuestionData):
            widget = InputValidationQuestion(
                caption=question_data.caption,
                ai_suggestions=question_data.ai_suggestions,
                history_suggestions=question_data.history_suggestions,
                ai_suggestion_box=self.ai_suggestion_box,
                history_suggestion_box=self.history_suggestion_box,
                pile=self.pile,
            )
            attr_widget = urwid.AttrMap(widget, "normal")
            widget.owner = attr_widget
            return attr_widget

        elif isinstance(question_data, MultipleChoiceQuestionData):
            return MultipleChoiceWidget(mc_question=question_data)

    def _build_questionnaire(self):
        """Build the complete questionnaire UI."""
        pile_contents = [(urwid.Text("HEADER:"), ("pack", None))]

        # Create and add all question widgets
        # for i, question in enumerate(self.questions):
        #     widget = self._create_question_widget(question, len(self.questions))
        #     if not isinstance(question, MultipleChoiceQuestionData):
        #         self.inputs.append(widget)
        #     pile_contents.append((widget, ("pack", None)))

        for i, question in enumerate(self.questions):
            widget = self._create_question_widget(question, len(self.questions))
            self.inputs.append(widget)  # Add all widgets to inputs
            pile_contents.append((widget, ("pack", None)))

        # Add suggestion boxes
        pile_contents.extend(
            [
                (urwid.Divider(), ("pack", None)),
                (
                    urwid.Columns(
                        [
                            (
                                self.descriptor_col_width,
                                urwid.Text("AI suggestions: "),
                            ),
                            self.ai_suggestion_box,
                        ]
                    ),
                    ("pack", None),
                ),
                (
                    urwid.Columns(
                        [
                            (
                                self.descriptor_col_width,
                                urwid.Text("History suggestions: "),
                            ),
                            self.history_suggestion_box,
                        ]
                    ),
                    ("pack", None),
                ),
            ]
        )

        self.pile.contents = pile_contents

    def _move_focus(self, current_pos: int, key: str) -> bool:
        """Move focus to next/previous question with wrap-around."""
        nr_of_questions = len(self.questions)
        if not nr_of_questions:
            return False

        if key in ["enter", "down", "tab"]:
            next_pos = (
                0 if current_pos == nr_of_questions - 1 else current_pos + 1
            )
        elif key == "up":
            next_pos = (
                nr_of_questions - 1 if current_pos == 0 else current_pos - 1
            )
        else:
            return False

        if 0 <= next_pos < nr_of_questions:
            self.pile.focus_position = next_pos + 1  # +1 for header
            focused_widget = self.inputs[next_pos].base_widget
            if not isinstance(focused_widget, MultipleChoiceWidget):
                focused_widget.update_autocomplete()
            return True
        return False

    def _handle_input(self, key: str):
        """Handle user keyboard input."""
        current_pos = self.pile.focus_position - 1

        write_to_file(filename="eg.txt", content=f"key={key}", append=True)
        if key in ("enter", "down", "tab", "up"):
            if current_pos >= 0:
                self._move_focus(current_pos=current_pos, key=key)

        elif key == "q":
            self._save_results()
            raise urwid.ExitMainLoop()

        elif key == "next_question":
            if self.pile.focus_position < len(self.questions):
                self.pile.focus_position += 1
            else:
                # TODO: parameterise start question position wrt header at 0.
                self.pile.focus_position = 1
                # TODO: reset edit position of current question to start of edit text.

        elif key == "previous_question":
            if self.pile.focus_position > 1:
                self.pile.focus_position -= 1
            else:
                self._move_focus(current_pos=current_pos, key="up")

    def _save_results(self):
        """Save questionnaire results before exit."""
        results = {}
        for i, input_widget in enumerate(self.inputs):
            results[f"question_{i}"] = input_widget.base_widget.edit_text
        # Add saving logic here if needed
        write_to_file("results.txt", str(results), append=True)

    def run(self):
        """Start the questionnaire application."""
        if self.inputs:
            self.pile.focus_position = 1  # Start at first question
            self.inputs[0].base_widget.initalise_autocomplete_suggestions()
        self.loop.run()


def create_and_run_questionnaire(
    questions: List[
        Union[
            DateQuestionData,
            InputValidationQuestionData,
            MultipleChoiceQuestionData,
        ]
    ],
):
    """Create and run a questionnaire with the given questions."""
    app = QuestionnaireApp(questions)
    write_to_file(filename="eg.txt", content="STARET", append=False)
    app.run()
