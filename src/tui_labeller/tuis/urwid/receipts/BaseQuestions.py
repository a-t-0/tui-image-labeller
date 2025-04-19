from tui_labeller.tuis.urwid.input_validation.InputType import InputType
from tui_labeller.tuis.urwid.question_data_classes import (
    AISuggestion,
    DateQuestionData,
    InputValidationQuestionData,
)


class BaseQuestions:
    def __init__(
        self,
    ):
        self.base_questions = self.create_base_questions()
        self.verify_unique_questions(self.base_questions)

    def create_base_questions(self):
        return [
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
                question="\nBookkeeping expense category:",
                input_type=InputType.LETTERS_SEMICOLON,
                ans_required=True,
                ai_suggestions=[],
                history_suggestions=[],
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
