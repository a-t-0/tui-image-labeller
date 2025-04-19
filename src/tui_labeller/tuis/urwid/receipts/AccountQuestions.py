from typing import List

from tui_labeller.tuis.urwid.question_data_classes import (
    MultipleChoiceQuestionData,
)


class AccountQuestions:
    def __init__(
        self,
        account_infos: List[str],
        categories: List[str],
    ):
        self.account_infos: List[str] = account_infos
        self.categories: List[str] = categories
        self.belongs_to_options: List[str] = (
            self.account_infos + self.categories
        )
        self.account_questions = self.create_questions()
        self.verify_unique_questions(self.account_questions)

    def create_questions(self):
        return [
            MultipleChoiceQuestionData(
                question="\n Belongs to account or category:",
                terminator=True,
                choices=self.belongs_to_options,
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

    def get_transaction_question_identifier(self) -> str:
        if not isinstance(self, AccountQuestions):
            raise TypeError(
                f"This {type(self)} is not a AccountQuestions object."
            )
        return self.account_questions[-1].question
