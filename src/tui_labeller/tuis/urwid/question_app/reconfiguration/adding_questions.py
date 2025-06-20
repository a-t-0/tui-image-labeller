from pprint import pprint
from typing import Any, List, Tuple, Union

from typeguard import typechecked

from tui_labeller.tuis.urwid.question_app.generator import create_questionnaire
from tui_labeller.tuis.urwid.question_data_classes import (
    VerticalMultipleChoiceQuestionData,
)
from tui_labeller.tuis.urwid.QuestionnaireApp import (
    QuestionnaireApp,
)
from tui_labeller.tuis.urwid.receipts.AccountQuestions import AccountQuestions


@typechecked
def handle_add_account(
    account_questions: "AccountQuestions",
    current_questions: list,
    preserved_answers: List[Union[None, Tuple[str, Any]]],
    selected_accounts: set,
) -> "QuestionnaireApp":
    """Handle the addition of a new account question."""
    available_accounts = [
        acc
        for acc in account_questions.belongs_to_options
        if acc not in selected_accounts
    ]
    if not available_accounts:
        raise ValueError(
            "Cannot add another account, as there aren't any unpicked accounts"
            " left."
        )

    # Finds the highest index in current_questions where a question matches any in account_questions.account_questions. Returns -1 if no match is found.
    last_account_idx = max(
        (
            i
            for i, q in enumerate(current_questions)
            if q.question
            in {q.question for q in account_questions.account_questions}
        ),
        default=-1,
    )

    # Create new AccountQuestions with filtered account_infos
    new_account_questions = AccountQuestions(
        account_infos=available_accounts,  # Only include available accounts
        asset_accounts=account_questions.asset_accounts,  # TODO: verify this is necessary and correct.
    ).account_questions
    for new_account_question in new_account_questions:
        if isinstance(new_account_question, VerticalMultipleChoiceQuestionData):
            if (
                new_account_question.question
                == "Belongs to bank/asset_accounts:"
            ):
                new_account_question.choices = available_accounts

    # Insert new_account_questions into current_questions at last_account_idx + 1
    new_questions = (
        current_questions[: last_account_idx + 1]
        + new_account_questions
        + current_questions[last_account_idx + 1 :]
    )

    new_tui = create_questionnaire(
        questions=new_questions,
        header="Answer the receipt questions.",
    )

    # Calculate the range of indices for new account questions
    new_account_start_idx = last_account_idx + 1
    new_account_end_idx = new_account_start_idx + len(new_account_questions)
    # Apply preserved answers only to questions outside the new account questions' indices
    pprint(preserved_answers)
    for idx, input_widget in enumerate(new_tui.inputs):

        widget = input_widget.base_widget
        question_text = widget.question_data.question

        # if idx < len(preserved_answers):
        #     if preserved_answers[idx] and isinstance(preserved_answers[idx],List) and len(preserved_answers[idx])>1:
        #         input(f'Reconsidering question: {question_text}, with preserved answer:{preserved_answers[idx][1]}')
        if new_account_start_idx <= idx < new_account_end_idx:
            print(f"SKIPPING={idx}, question={widget.question_data.question}")
            continue  # Skip new account questions
        elif len(preserved_answers) > idx and (
            preserved_answers[idx]
            and question_text == preserved_answers[idx][0]
        ):
            print(
                f"SETTING={idx},"
                f" question={widget.question_data.question} with:{preserved_answers[idx][1]}"
            )
            widget.set_answer(preserved_answers[idx][1])
        else:
            print(
                f"new_account_start_idx={new_account_start_idx},"
                f" new_account_end_idx={new_account_end_idx}"
            )
            print(
                f"Outside of scope, idx={idx},"
                f" question={widget.question_data.question}"
            )

    return new_tui
