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


@typechecked
def remove_account_questions(
    current_questions: list,
    account_questions: "AccountQuestions",
    start_question_nr: int,
) -> list:
    """Remove all account questions that appear after the given question
    number."""

    # Identify the set of account question identifiers
    account_question_identifiers = {
        q.question for q in account_questions.account_questions
    }
    print(account_question_identifiers)
    # Find the index in current_questions corresponding to start_question_nr
    question_idx = -1
    for i, q in enumerate(current_questions):
        # Check if the question has a widgets attribute
        if hasattr(q, "widgets"):
            for input_widget in q.widgets:
                # Ensure base_widget and position exist
                if hasattr(input_widget, "base_widget") and hasattr(
                    input_widget.base_widget.question, "position"
                ):
                    if (
                        input_widget.base_widget.question.position
                        == start_question_nr
                    ):
                        question_idx = i
                        break
        if question_idx != -1:
            break

    if question_idx == -1:
        # If the question number is not found, return current questions unchanged
        return current_questions

    # Keep questions up to and including the current block, remove subsequent account questions
    result_questions = current_questions[: question_idx + 1]
    for q in current_questions[question_idx + 1 :]:
        if q.question not in account_question_identifiers:
            result_questions.append(q)
    input("REMVAL SERVICE")
    return result_questions
