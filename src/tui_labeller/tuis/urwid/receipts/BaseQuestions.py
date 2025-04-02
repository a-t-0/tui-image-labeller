from tui_labeller.tuis.urwid.input_validation.InputType import InputType
from tui_labeller.tuis.urwid.question_data_classes import (
    AISuggestion,
    DateQuestionData,
    InputValidationQuestionData,
    MultipleChoiceQuestionData,
)
from tui_labeller.tuis.urwid.receipts.currenncies import Currencies
from tui_labeller.tuis.urwid.receipts.payments_enum import PaymentTypes


class BaseQuestions:
    def __init__(
        self,
    ):
        self.base_questions = self.create_base_questions()
        self.verify_unique_questions(self.base_questions)

    def create_base_questions(self):
        return [
            MultipleChoiceQuestionData(
                question="Currency:\n",
                terminator=False,
                choices=[currenncy.value for currenncy in Currencies],
                ai_suggestions=[
                    AISuggestion(Currencies.EUR.value, 0.99, "ReadAI"),
                    AISuggestion(Currencies.BTC.value, 0.1, "SomeAI"),
                    AISuggestion(Currencies.XMR.value, 0.97, "AnotherAI"),
                ],
            ),
            DateQuestionData(
                "Receipt date and time:\n",
                False,
                [
                    AISuggestion("2025-03-17 14:30", 0.92, "TimeMaster"),
                    AISuggestion("2025-03-17 09:00", 0.88, "TimeMaster"),
                    AISuggestion("2025-03-18 12:00", 0.80, "ChronoAI"),
                ],
            ),
            InputValidationQuestionData(
                question="\nBookkeeping category:\n",
                input_type=InputType.LETTERS_SEMICOLON,
                ans_required=True,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            MultipleChoiceQuestionData(
                question="\nTransaction type",
                terminator=True,
                choices=[pt.value for pt in PaymentTypes],
                ai_suggestions=[
                    AISuggestion(PaymentTypes.CASH.value, 0.99, "ReadAI"),
                    AISuggestion(PaymentTypes.CARD.value, 0.1, "SomeAI"),
                    AISuggestion(PaymentTypes.BOTH.value, 0.97, "AnotherAI"),
                ],
            ),
        ]

    def verify_unique_questions(self, questions):
        seen = set()
        for q in questions:
            question = getattr(q, "question", getattr(q, "question", None))
            if question is None:
                raise ValueError("Question object missing question/question")
            if question in seen:
                raise ValueError(f"Duplicate question question: '{question}'")
            seen.add(question)

    def get_transaction_question_identifier(self) -> str:
        if not isinstance(self, BaseQuestions):
            raise TypeError(f"This {type(self)} is not a BaseQuestions object.")
        return self.base_questions[-1].question
