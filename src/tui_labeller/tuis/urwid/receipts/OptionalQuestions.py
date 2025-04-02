from tui_labeller.tuis.urwid.input_validation.InputType import InputType
from tui_labeller.tuis.urwid.question_data_classes import (
    InputValidationQuestionData,
)


class OptionalQuestions:
    def __init__(
        self,
    ):
        self.optional_questions = self.create_base_questions()
        self.verify_unique_questions(self.base_questions)

    def create_base_questions(self):
        return [
            InputValidationQuestionData(
                question="Receipt owner address (optional):\n",
                input_type=InputType.LETTERS,
                ans_required=False,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                question="Shop name:\n",
                input_type=InputType.LETTERS,
                ans_required=False,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                question="Shop address:\n",
                input_type=InputType.LETTERS,
                ans_required=False,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                question="Subtotal (Optional, press enter to skip):\n",
                input_type=InputType.FLOAT,
                ans_required=False,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                question="Total tax (Optional, press enter to skip):\n",
                input_type=InputType.FLOAT,
                ans_required=False,
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
