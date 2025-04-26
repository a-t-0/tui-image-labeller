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
    preserved_answers: dict,
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
        categories=account_questions.categories,
    ).account_questions
    for new_account_question in new_account_questions:
        if isinstance(new_account_question, VerticalMultipleChoiceQuestionData):
            if new_account_question.question == "Belongs to account/category:":
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
    for idx, input_widget in enumerate(new_tui.inputs):
        if new_account_start_idx <= idx < new_account_end_idx:
            continue  # Skip new account questions
        widget = input_widget.base_widget
        question_text = widget.question.question
        if question_text in preserved_answers:
            widget.set_answer(preserved_answers[question_text])

    return new_tui
