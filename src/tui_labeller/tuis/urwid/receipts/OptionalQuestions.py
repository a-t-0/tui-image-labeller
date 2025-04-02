from tui_labeller.tuis.urwid.input_validation.InputType import InputType
from tui_labeller.tuis.urwid.question_data_classes import (
    InputValidationQuestionData,
    MultipleChoiceQuestionData,
)


class OptionalQuestions:
    def __init__(
        self,
    ):
        self.optional_questions = self.create_base_questions()
        self.verify_unique_questions(self.optional_questions)

    def create_base_questions(self):
        return [
            InputValidationQuestionData(
                question="\nShop name:\n",
                input_type=InputType.LETTERS,
                ans_required=False,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                question="\nShop address:\n",
                input_type=InputType.LETTERS,
                ans_required=False,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                question="\nSubtotal (Optional, press enter to skip):\n",
                input_type=InputType.FLOAT,
                ans_required=False,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                question="\nTotal tax (Optional, press enter to skip):\n",
                input_type=InputType.FLOAT,
                ans_required=False,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                question="\nReceipt owner address (optional):\n",
                input_type=InputType.LETTERS,
                ans_required=False,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            MultipleChoiceQuestionData(
                question="\nDone with this receipt?",
                terminator=True,
                choices=["yes"],
                ai_suggestions=[],
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

    def get_is_done_question_identifier(self) -> str:
        return self.optional_questions[-1].question
