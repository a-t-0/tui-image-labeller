from typing import List

import urwid
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
        asset_accounts: set[str],
    ):
        """account_infos are <account holder name>:<bank name>:<account_type>
        they are a single string as they come directly from the arg parser."""
        self.account_infos: List[str] = account_infos
        self.asset_accounts: set[str] = asset_accounts
        self.belongs_to_options: List[str] = sorted(
            list(set(list(self.account_infos) + list(self.asset_accounts)))
        )
        self.account_questions = self.create_questions()
        self.verify_unique_questions(self.account_questions)

    def create_questions(self):

        return [
            VerticalMultipleChoiceQuestionData(
                question="Belongs to bank/asset_accounts:",
                ans_required=True,
                reconfigurer=False,
                terminator=False,
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
                nr_of_ans_per_batch=8,
                navigation_display=urwid.AttrMap(
                    urwid.Pile(
                        [
                            urwid.Text(("navigation", "Navigation")),
                            urwid.Text(f"Q          - quit"),
                            urwid.Text(
                                f"\n<- Left, Right -> - Show next batch of"
                                f" answers."
                            ),
                            urwid.Text(
                                f"\nType a number to select that answer."
                            ),
                            urwid.Text(
                                f"\nEnter confirm choice, goto next question."
                            ),
                        ]
                    ),
                    "normal",
                ),
            ),
            VerticalMultipleChoiceQuestionData(
                question="Currency:",
                ans_required=True,
                nr_of_ans_per_batch=8,
                reconfigurer=False,
                terminator=False,
                choices=[currency.value for currency in Currency],
                ai_suggestions=[],
            ),
            InputValidationQuestionData(
                question="Amount paid from account:",
                input_type=InputType.FLOAT,
                ai_suggestions=[],
                history_suggestions=[],
                ans_required=True,
                reconfigurer=False,
                terminator=False,
            ),
            InputValidationQuestionData(
                question="Change returned to account:",
                input_type=InputType.FLOAT,
                ai_suggestions=[],
                history_suggestions=[],
                ans_required=True,
                reconfigurer=False,
                terminator=False,
            ),
            HorizontalMultipleChoiceQuestionData(
                question="Add another account (y/n)?",
                choices=["y", "n"],
                ai_suggestions=[],
                ans_required=True,
                reconfigurer=True,
                terminator=False,
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
