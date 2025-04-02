from tui_labeller.tuis.urwid.input_validation.InputType import InputType
from tui_labeller.tuis.urwid.question_data_classes import (
    AISuggestion,
    InputValidationQuestionData,
    MultipleChoiceQuestionData,
)
from tui_labeller.tuis.urwid.receipts.payments_enum import PaymentTypes


class BaseQuestions:
    def __init__(
        self,
    ):
        self.base_questions = self.create_base_questions()
        self.verify_unique_questions(self.base_questions)

    def create_base_questions(self):
        return [
            InputValidationQuestionData(
                question="Bookkeeping category:\n",
                input_type=InputType.LETTERS_SEMICOLON,
                ans_required=True,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            MultipleChoiceQuestionData(
                question="Transaction type",
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
