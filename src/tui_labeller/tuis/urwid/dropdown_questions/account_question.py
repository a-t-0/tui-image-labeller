from typing import List, Union

import urwid

from tui_labeller.tuis.urwid.question_data_classes import (
    AISuggestion,
    InputValidationQuestionData,
    MultipleChoiceQuestionData,
)
from tui_labeller.tuis.urwid.QuestionnaireApp import QuestionnaireApp


class RowQuestionnaireApp(QuestionnaireApp):
    def _build_questionnaire(self):
        """Build the questionnaire UI with questions in a single row."""
        pile_contents = [(urwid.Text(self.header), ("pack", None))]
        self.nr_of_headers = len(pile_contents)

        # Create widgets for each question
        question_widgets = []
        for i, question in enumerate(self.questions):
            widget = self._create_question_widget(question, len(self.questions))
            self.inputs.append(widget)
            question_widgets.append(
                (widget, ("pack", None))  # Use 'pack' for flow widgets
            )

        # Arrange questions in a single row using Columns
        questions_row = urwid.Columns(question_widgets, dividechars=2)

        # Add the row and suggestion boxes to the pile
        pile_contents.extend(
            [
                (questions_row, ("pack", None)),
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


def create_row_questionnaire():
    """Create a questionnaire with 5 questions in a single row."""
    # Define question data
    questions: List[
        Union[MultipleChoiceQuestionData, InputValidationQuestionData]
    ] = [
        # 1. From account/category (Multiple Choice)
        MultipleChoiceQuestionData(
            question="From account/category",
            choices=["Savings", "Checking", "Cash"],
            ai_suggestions=[
                AISuggestion(
                    question="Savings", probability=0.5, model_name="Hank"
                ),
                AISuggestion(
                    question="Checking", probability=0.3, model_name="Fritz"
                ),
            ],
            terminator=False,
        ),
        # 2. Amount subtracted (Float Input)
        InputValidationQuestionData(
            question="Amount subtracted",
            input_type=float,
            ans_required=False,
            ai_suggestions=[],
            history_suggestions=[],
            default=None,
        ),
        # 3. Amount added (Float Input)
        InputValidationQuestionData(
            question="Amount added",
            input_type=float,
            ans_required=False,
            ai_suggestions=[],
            history_suggestions=[],
            default=None,
        ),
        # 4. Currency (Multiple Choice)
        MultipleChoiceQuestionData(
            question="Currency",
            choices=["USD", "EUR", "GBP"],
            ai_suggestions=[
                AISuggestion(
                    question="USD", probability=0.6, model_name="Hank"
                ),
                AISuggestion(
                    question="EUR", probability=0.2, model_name="Hank"
                ),
            ],
            terminator=False,
        ),
        # 5. Add another? (Yes/No Multiple Choice)
        MultipleChoiceQuestionData(
            question="Add another?",
            choices=["Yes", "No"],
            ai_suggestions=[
                AISuggestion(question="No", probability=0.7, model_name="Hi"),
            ],
            terminator=True,  # Terminates questionnaire on Enter
        ),
    ]

    # Create and return the app
    app = RowQuestionnaireApp(header="Transaction Entry", questions=questions)
    return app


if __name__ == "__main__":
    app = create_row_questionnaire()
    app.run()
