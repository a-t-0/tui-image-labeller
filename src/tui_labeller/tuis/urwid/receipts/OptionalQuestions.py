from tui_labeller.tuis.urwid.input_validation.InputType import InputType
from tui_labeller.tuis.urwid.question_data_classes import (
    HorizontalMultipleChoiceQuestionData,
    InputValidationQuestionData,
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
                ai_suggestions=[],
                history_suggestions=[],
                ans_required=False,
                reconfigurer=False,
                terminator=False,
            ),
            InputValidationQuestionData(
                question="Shop street:",
                input_type=InputType.LETTERS,
                ai_suggestions=[],
                history_suggestions=[],
                ans_required=False,
                reconfigurer=False,
                terminator=False,
            ),
            InputValidationQuestionData(
                question="Shop zipcode:",
                input_type=InputType.LETTERS,
                ai_suggestions=[],
                history_suggestions=[],
                ans_required=False,
                reconfigurer=False,
                terminator=False,
            ),
            InputValidationQuestionData(
                question="Shop house nr.:",
                input_type=InputType.INTEGER,  # TODO: allow 37a
                ai_suggestions=[],
                history_suggestions=[],
                ans_required=False,
                reconfigurer=False,
                terminator=False,
            ),
            InputValidationQuestionData(
                question="Shop City:",
                input_type=InputType.LETTERS,
                ai_suggestions=[],
                history_suggestions=[],
                ans_required=False,
                reconfigurer=False,
                terminator=False,
            ),
            InputValidationQuestionData(
                question="Shop country:",
                input_type=InputType.LETTERS,
                ai_suggestions=[],
                history_suggestions=[],
                ans_required=False,
                reconfigurer=False,
                terminator=False,
            ),
            InputValidationQuestionData(
                question="\nSubtotal (Optional, press enter to skip):\n",
                input_type=InputType.FLOAT,
                ai_suggestions=[],
                history_suggestions=[],
                ans_required=False,
                reconfigurer=False,
                terminator=False,
            ),
            InputValidationQuestionData(
                question="\nTotal tax (Optional, press enter to skip):\n",
                input_type=InputType.FLOAT,
                ai_suggestions=[],
                history_suggestions=[],
                ans_required=False,
                reconfigurer=False,
                terminator=False,
            ),
            HorizontalMultipleChoiceQuestionData(
                question="\nDone with this receipt?",
                choices=["yes"],
                ai_suggestions=[],
                ans_required=True,
                reconfigurer=False,
                terminator=True,
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
