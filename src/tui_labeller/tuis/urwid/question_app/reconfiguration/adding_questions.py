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
        if len(preserved_answers) > idx and (
            preserved_answers[idx]
            and question_text == preserved_answers[idx][0]
        ):
            widget.set_answer(preserved_answers[idx][1])
            input(f"setting widget={preserved_answers[idx][1]}")

    return new_tui


@typechecked
def remove_later_account_questions(
    *,
    current_questions: list,
    account_questions: "AccountQuestions",
    start_question_nr: int,
    preserved_answers: List[Tuple[str, Any]],
) -> Tuple[
    list, List[Tuple[str, Any]]
]:  # Return updated questions and preserved_answers
    """Remove all account questions that appear after the given question
    number, validate preserved answers, and update preserved_answers
    accordingly."""
    input("CALLING REMOVAL")
    # Identify the set of account question identifiers
    account_question_identifiers = {
        q.question for q in account_questions.account_questions
    }

    # Validate preserved_answers: ensure question text at each index matches

    for idx, pair in enumerate(preserved_answers):
        if pair != None:
            question_text = pair[0]
            if (
                idx < len(current_questions)
                and question_text != current_questions[idx].question
            ):
                raise ValueError(
                    f"Preserved answer at index {idx} has question"
                    f" '{question_text}' but expected"
                    f" '{current_questions[idx].question}'"
                )

    # Find the index in current_questions corresponding to start_question_nr
    question_idx = -1
    for i, q in enumerate(current_questions):
        if hasattr(q, "widgets"):
            for input_widget in q.widgets:
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
        # If the question number is not found, return current questions and preserved_answers unchanged
        return current_questions, preserved_answers or []

    # Keep questions up to and including the current block, remove subsequent account questions
    result_questions = current_questions[: question_idx + 1]
    for q in current_questions[question_idx + 1 :]:
        if q.question not in account_question_identifiers:
            result_questions.append(q)

    # Update preserved_answers: remove answers for removed questions and shift indices
    updated_preserved = []
    if preserved_answers:
        for idx, (question_text, answer) in enumerate(preserved_answers):
            # Keep answers for questions that remain in result_questions
            if (
                idx < len(result_questions)
                and question_text == result_questions[idx].question
            ):
                updated_preserved.append((question_text, answer))

    return result_questions, updated_preserved
