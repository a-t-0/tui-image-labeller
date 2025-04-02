from tui_labeller.tuis.urwid.input_validation.InputType import InputType
from tui_labeller.tuis.urwid.question_data_classes import (
    InputValidationQuestionData,
)


class CardPaymentQuestions:
    def __init__(self):
        self.questions = [
            InputValidationQuestionData(
                question="Amount paid by card:\n",
                input_type=InputType.FLOAT,
                ans_required=True,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                question="Change returned (card):\n",
                input_type=InputType.FLOAT,
                ans_required=True,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                question="Account holder name:\n",
                input_type=InputType.LETTERS,
                ans_required=True,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                question="Bank name (e.g., triodos, bitfavo):\n",
                input_type=InputType.LETTERS,
                ans_required=True,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                question="Account type (e.g., checking, credit):\n",
                input_type=InputType.LETTERS,
                ans_required=True,
                ai_suggestions=[],
                history_suggestions=[],
            ),
        ]
