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
    tui: "QuestionnaireApp",
    account_questions: "AccountQuestions",
    start_question_nr: int,
    preserved_answers: List[Tuple[str, Any]],
) -> Tuple[list, List[Tuple[str, Any]]]:
    """Remove account questions after the given question number, validate
    preserved answers, and update accordingly."""
    # Identify account question identifiers
    account_question_identifiers = {
        q.question for q in account_questions.account_questions
    }

    # Validate preserved_answers, filter out None values
    current_questions = tui.questions
    valid_preserved_answers = []
    for item in preserved_answers:
        if item is None:
            continue  # Skip None entries
        if not isinstance(item, tuple) or len(item) not in (2, 3):
            raise ValueError(
                f"Invalid preserved_answers entry: {item}. Expected tuple"
                " (position, question_text, answer) or (question_text,"
                " answer)."
            )
        if len(item) == 3:
            position, question_text, answer = item
        else:  # len(item) == 2
            question_text, answer = item
        valid_preserved_answers.append((question_text, answer))

    # Validate preserved answers against current questions
    for idx, (question_text, _) in enumerate(valid_preserved_answers):
        if (
            idx < len(current_questions)
            and question_text != current_questions[idx].question
        ):
            raise ValueError(
                f"Preserved answer at index {idx} has question"
                f" '{question_text}' but expected"
                f" '{current_questions[idx].question}'"
            )

    first_half = []
    updated_preserved = (
        valid_preserved_answers.copy()
    )  # Create a copy to modify
    non_account_question_found = False

    # Process questions
    for i, tui_question in enumerate(tui.questions):
        if i > start_question_nr:
            if tui_question.question not in account_question_identifiers:
                # Non-account question found after start_question_nr
                non_account_question_found = True
                first_half.append(tui_question)
            else:
                # Account question after start_question_nr, remove it
                if non_account_question_found:
                    # Raise error if account question follows a non-account question
                    raise ValueError(
                        f"Account question '{tui_question.question}' found"
                        f" after a non-account question at index {i}"
                    )
                # Remove corresponding preserved answer, if it exists
                for preserved in updated_preserved:
                    if preserved[0] == tui_question.question:
                        updated_preserved.remove(preserved)
                        break
        else:
            first_half.append(tui_question)

    for q in first_half:
        if q.has_answer():
            input(f"q={q.question}, answer={q.get_answer()}")
        else:
            input(f"q={q.question}, noanswer")
    return first_half, updated_preserved
