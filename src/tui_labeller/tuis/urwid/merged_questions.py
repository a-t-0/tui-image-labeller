from datetime import datetime
from typing import Dict, List, Optional, Type, Union

import urwid
from typeguard import typechecked

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
from tui_labeller.tuis.urwid.receipts.payments_enum import (
    PaymentTypes,
    str_to_payment_type,
)


class QuestionnaireApp:
    def __init__(
        self,
        header: str,
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
        self.header = header
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
        """Setup color palette for the UI with format:
        <identifier>, <text colour>, <background colour>."""
        return [
            ("normal", "white", ""),
            ("highlight", "white", "dark red"),
            ("direction", "white", "yellow"),
            ("error", "dark red", ""),
            ("ai_suggestions", "yellow", ""),
            ("history_suggestions", "yellow", ""),
            ("mc_question_palette", "light cyan", ""),
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
                question=question_data.question,
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
                question=question_data.question,
                input_type=question_data.input_type,
                ans_required=question_data.ans_required,
                ai_suggestions=question_data.ai_suggestions,
                history_suggestions=question_data.history_suggestions,
                ai_suggestion_box=self.ai_suggestion_box,
                history_suggestion_box=self.history_suggestion_box,
                pile=self.pile,
            )
            if question_data.default is not None:
                widget.set_edit_text(question_data.default)
            attr_widget = urwid.AttrMap(widget, "normal")
            widget.owner = attr_widget
            return attr_widget

        elif isinstance(question_data, MultipleChoiceQuestionData):
            return MultipleChoiceWidget(mc_question=question_data)

    def _build_questionnaire(self):
        """Build the complete questionnaire UI."""
        pile_contents = [(urwid.Text(self.header), ("pack", None))]
        self.nr_of_headers = len(pile_contents)

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

            # return False
            raise ValueError("SHould have questions.")

        if key in ["enter", "down", "tab"]:
            next_pos = (
                0 if current_pos == nr_of_questions - 1 else current_pos + 1
            )
        elif key == "up":
            next_pos = (
                nr_of_questions - 1 if current_pos == 0 else current_pos - 1
            )
        else:
            raise ValueError(
                f"Unexpected key={key}, current_pos={current_pos}."
            )
        raise NotImplementedError(
            f"SHOULD NOT BE REACHED, self.questions = {len(self.questions)}"
        )

    def _handle_input(self, key: str):
        """Handle user keyboard input."""
        current_pos = self.pile.focus_position - 1

        if key in ("enter", "down", "tab", "up"):
            if current_pos >= 0:
                self._move_focus(current_pos=current_pos, key=key)
        elif key == "terminator":
            # raise ValueError("STOOPPPED")
            raise urwid.ExitMainLoop()  # Exit the main loop

        elif key == "q":
            self._save_results()
            raise urwid.ExitMainLoop()

        elif key == "next_question":
            if (
                self.pile.focus_position
                < len(self.questions) - 1 + self.nr_of_headers
            ):
                self.pile.focus_position += 1
            else:
                # TODO: parameterise start question position wrt header at 0.
                self.pile.focus_position = self.nr_of_headers
                # TODO: reset edit position of current question to start of edit text.
            focused_widget = self.inputs[
                self.pile.focus_position - self.nr_of_headers
            ].base_widget

        elif key == "previous_question":
            if self.pile.focus_position > 1:
                self.pile.focus_position -= 1
            else:
                self._move_focus(current_pos=current_pos, key="up")

        # Update the autocomplete suggestions.
        focused_widget = self.inputs[
            self.pile.focus_position - self.nr_of_headers
        ].base_widget
        if not isinstance(focused_widget, MultipleChoiceWidget):
            focused_widget.update_autocomplete()

    def _save_results(self):
        """Save questionnaire results before exit."""
        results = {}
        for i, input_widget in enumerate(self.inputs):
            results[f"question_{i}"] = input_widget.base_widget.edit_text
        # Add saving logic here if needed
        write_to_file("results.txt", str(results), append=True)

    def run(self, alternative_start_pos: Optional[int] = None):
        """Start the questionnaire application."""
        if self.inputs:
            if alternative_start_pos is None:
                self.pile.focus_position = 1  # TODO: parameterise Header.
            else:
                self.pile.focus_position = alternative_start_pos
            self.inputs[1].base_widget.initalise_autocomplete_suggestions()
        self.loop.run()

    @typechecked
    def get_answers(
        self,
    ) -> Dict[
        Union[DateTimeQuestion, InputValidationQuestion, MultipleChoiceWidget],
        Union[str, float, int, datetime],
    ]:
        """Collects answers from all questions in the questionnaire.

        Returns:
            Dict[str, Union[str, float, int, datetime]]: A dictionary mapping question captions
                to their answers. Answer types depend on question type:
                - DateTimeQuestion: datetime
                - InputValidationQuestion: str, float, or int
                - MultipleChoiceWidget: str

        Raises:
            ValueError: If any question's answer cannot be retrieved or validated
        """
        # results: Dict[str, Union[str, float, int, datetime]] = {}
        results: Dict[
            Union[
                DateTimeQuestion, InputValidationQuestion, MultipleChoiceWidget
            ],
            Union[str, float, int, datetime],
        ] = {}

        for i, input_widget in enumerate(self.inputs):
            widget = input_widget.base_widget
            # try:
            if isinstance(widget, DateTimeQuestion):
                answer = widget.get_answer()
                results[widget] = answer

            elif isinstance(widget, InputValidationQuestion):
                answer = widget.get_answer()
                results[widget] = answer

            elif isinstance(widget, MultipleChoiceWidget):
                answer = widget.get_answer()
                results[widget] = answer

            else:
                raise ValueError(
                    f"Unknown widget type at index {i}: {type(widget)}"
                )

            # except ValueError as e:
            #     raise ValueError(
            #         f"Failed to get answer for question {i}: {str(e)}"
            #     ) from e

        return results

    @typechecked
    def get_question_by_text_and_type(
        self,  # Implicitly part of QuestionnaireApp
        question_text: str,
        question_type: Type[
            Union[
                DateTimeQuestion, InputValidationQuestion, MultipleChoiceWidget
            ]
        ],
    ) -> PaymentTypes:
        """Retrieve the first question matching the specified text and type
        from the app's questions.

        Args:
            self: The QuestionnaireApp instance (implicit).
            question_text: The exact text (question or caption) to search for.
            question_type: The type of question to match (e.g., MultipleChoiceWidget).

        Returns:
            PaymentTypes: The first question
                object matching the specified text and type.

        Raises:
            ValueError: If no question with the specified text and type is found.
        """

        for i, input_widget in enumerate(self.inputs):
            widget = input_widget.base_widget
            # write_to_file(filename="eg.txt",content= f"widget={widget}, type={type(widget)}", append=True)
            if isinstance(widget, MultipleChoiceWidget):
                write_to_file(
                    filename="eg.txt", content=f"widget={widget}", append=True
                )
                answer = widget.get_answer()
                write_to_file(
                    filename="eg.txt", content=f"answer={answer}", append=True
                )
                if answer in [pt.value for pt in PaymentTypes]:
                    return str_to_payment_type(value=answer)
                # current_text = getattr(question, "question", getattr(question, "caption", None))
                # if current_text == question_text:
                #     return question

        # Raise ValueError if no matching question is found
        raise ValueError(
            f"No '{question_text}' question of type"
            f" {question_type.__name__} found in the questionnaire"
        )


@typechecked
def create_and_run_questionnaire(
    header: str,
    questions: List[
        Union[
            DateQuestionData,
            InputValidationQuestionData,
            MultipleChoiceQuestionData,
        ]
    ],
) -> QuestionnaireApp:
    """Create and run a questionnaire with the given questions."""
    app = QuestionnaireApp(header=header, questions=questions)
    write_to_file(filename="eg.txt", content="STARTED", append=False)
    return app
