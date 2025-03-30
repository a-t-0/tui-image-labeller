from tui_labeller.tuis.urwid.input_validation.InputType import InputType
from tui_labeller.tuis.urwid.question_data_classes import (
    InputValidationQuestionData,
)


class CardPaymentQuestions:
    def __init__(self):
        self.questions = [
            InputValidationQuestionData(
                caption="Amount paid by card: ",
                input_type=InputType.FLOAT,
                ans_required=True,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                caption="Change returned (card): ",
                input_type=InputType.FLOAT,
                ans_required=True,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                caption="Account holder name: ",
                input_type=InputType.LETTERS,
                ans_required=True,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                caption="Bank name (e.g., triodos, bitfavo): ",
                input_type=InputType.LETTERS,
                ans_required=True,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                caption="Account type (e.g., checking, credit): ",
                input_type=InputType.LETTERS,
                ans_required=True,
                ai_suggestions=[],
                history_suggestions=[],
            ),
        ]
