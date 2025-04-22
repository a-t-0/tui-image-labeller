from typing import List

from hledger_preprocessor.Currency import Currency

from tui_labeller.tuis.urwid.input_validation.InputType import InputType
from tui_labeller.tuis.urwid.question_data_classes import (
    AISuggestion,
    HorizontalMultipleChoiceQuestionData,
    InputValidationQuestionData,
    VerticalMultipleChoiceQuestionData,
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
            VerticalMultipleChoiceQuestionData(
                question="Belongs to account/category:",
                terminator=True,
                ans_required=True,
                choices=self.belongs_to_options,
                ai_suggestions=[
                    AISuggestion(
                        question="name:uniswap:saving",
                        probability=0.42,
                        model_name="Gary",
                    ),
                    AISuggestion(
                        question="name:uniswap:saving",
                        probability=0.9001,
                        model_name="Yanet",
                    ),
                    AISuggestion(
                        question="assets:cash",
                        probability=0.5,
                        model_name="Barry",
                    ),
                ],
            ),
            VerticalMultipleChoiceQuestionData(
                question="Currency:",
                terminator=True,
                ans_required=True,
                choices=[currency.value for currency in Currency],
                ai_suggestions=[],
            ),
            InputValidationQuestionData(
                question="Amount paid from account:",
                input_type=InputType.FLOAT,
                ans_required=True,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                question="Change returned to account:",
                input_type=InputType.FLOAT,
                ans_required=True,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            HorizontalMultipleChoiceQuestionData(
                question="Add another account (y/n)?",
                ans_required=True,
                choices=["y", "n"],
                ai_suggestions=[],
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

    def get_transaction_question_identifier(self) -> str:
        if not isinstance(self, AccountQuestions):
            raise TypeError(
                f"This {type(self)} is not a AccountQuestions object."
            )
        return self.account_questions[-1].question
