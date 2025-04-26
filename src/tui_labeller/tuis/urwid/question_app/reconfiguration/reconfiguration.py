from typing import Any, List, Tuple, Union

from typeguard import typechecked

from tui_labeller.tuis.urwid.date_question.DateTimeQuestion import (
    DateTimeQuestion,
)
from tui_labeller.tuis.urwid.input_validation.InputValidationQuestion import (
    InputValidationQuestion,
)
from tui_labeller.tuis.urwid.multiple_choice_question.HorizontalMultipleChoiceWidget import (
    HorizontalMultipleChoiceWidget,
)
from tui_labeller.tuis.urwid.multiple_choice_question.VerticalMultipleChoiceWidget import (
    VerticalMultipleChoiceWidget,
)
from tui_labeller.tuis.urwid.question_app.generator import create_questionnaire
from tui_labeller.tuis.urwid.question_app.reconfiguration.adding_questions import (
    handle_add_account,
)
from tui_labeller.tuis.urwid.question_app.reconfiguration.removing_questions import (
    remove_later_account_questions,
)
from tui_labeller.tuis.urwid.QuestionnaireApp import (
    QuestionnaireApp,
)
from tui_labeller.tuis.urwid.receipts.AccountQuestions import AccountQuestions
from tui_labeller.tuis.urwid.receipts.OptionalQuestions import OptionalQuestions


@typechecked
def has_later_account_question(
    *,
    current_account_question_index: int,
    reconfig_answers: List[Tuple[int, str, str]],
) -> bool:
    """Check if there is a later account-related reconfiguration question."""
    account_question = "Add another account (y/n)?"
    return any(
        index > current_account_question_index and question == account_question
        for index, question, _ in reconfig_answers
    )


@typechecked
def collect_reconfiguration_questions(
    *, tui: "QuestionnaireApp", answered_only: bool
) -> List[Tuple[int, str, str]]:
    """Collect answers from widgets that trigger reconfiguration as a list of
    (position, question, answer).

    Args:
        tui: The questionnaire application.
        answered_only: If True, collect only questions with answers; if False,
                      collect all reconfiguration questions.

    Returns:
        List of (position, question, answer) tuples.
    """
    reconfig_answers = []
    for index, input_widget in enumerate(tui.inputs):
        widget = input_widget.base_widget
        if isinstance(
            widget,
            HorizontalMultipleChoiceWidget,
        ):
            if widget.question.reconfigurer:
                answer = widget.get_answer() if widget.has_answer() else ""
                if not answered_only or (answered_only and answer):
                    reconfig_answers.append(
                        (index, widget.question.question, answer)
                    )
    return reconfig_answers


@typechecked
def collect_selected_accounts(tui: "QuestionnaireApp") -> set:
    """Collect currently selected accounts to prevent reuse."""
    selected_accounts = set()
    for input_widget in tui.inputs:
        widget = input_widget.base_widget
        if isinstance(
            widget,
            (VerticalMultipleChoiceWidget, HorizontalMultipleChoiceWidget),
        ):
            if (
                widget.question.question.startswith(
                    "Belongs to account/category:"
                )
                and widget.has_answer()
            ):
                answer = widget.get_answer()
                if answer:
                    selected_accounts.add(answer)
    return selected_accounts


@typechecked
def preserve_current_answers(
    *, tui: "QuestionnaireApp"
) -> List[Union[None, Tuple[str, Any]]]:
    """Preserve all current answers from the questionnaire."""

    preserved_answers: List[Union[None, Tuple[str, Any]]] = [
        None for _ in tui.inputs
    ]

    for i, input_widget in enumerate(tui.inputs):
        widget = input_widget.base_widget
        if isinstance(
            widget,
            (
                VerticalMultipleChoiceWidget,
                HorizontalMultipleChoiceWidget,
                DateTimeQuestion,
                InputValidationQuestion,
            ),
        ):
            if widget.has_answer():
                answer = widget.get_answer()
                if answer:
                    preserved_answers[i] = (widget.question.question, answer)
    return preserved_answers


@typechecked
def handle_optional_questions(
    *,
    tui: "QuestionnaireApp",
    optional_questions: "OptionalQuestions",
    current_questions: list,
    preserved_answers: List[Tuple[str, Any]],
) -> "QuestionnaireApp":
    """Handle the addition or focusing of optional questions."""
    optional_question_identifiers = {
        oq.question for oq in optional_questions.optional_questions
    }

    if not any(
        q.base_widget.question.question in optional_question_identifiers
        for q in current_questions
    ):
        new_questions = (
            current_questions + optional_questions.optional_questions
        )
        great_tui = create_questionnaire(
            questions=new_questions,
            header="Answer the receipt questions.",
        )

        return set_default_focus_and_answers(
            tui=great_tui, preserved_answers=preserved_answers
        )
    return tui


@typechecked
def set_default_focus_and_answers(
    tui: "QuestionnaireApp",
    preserved_answers: List[Union[None, Tuple[str, Any]]],
) -> "QuestionnaireApp":
    """Set preserved answers and focus on the next unanswered question."""
    for i, input_widget in enumerate(tui.inputs):

        widget = input_widget.base_widget
        question_text = widget.question.question
        if (
            preserved_answers[i] != None
            and preserved_answers[i][0] == question_text
        ):
            widget.set_answer(preserved_answers[i][1])

    return tui


@typechecked
def get_configuration(
    tui: "QuestionnaireApp",
    account_questions: "AccountQuestions",
    optional_questions: "OptionalQuestions",
) -> "QuestionnaireApp":
    """Reconfigure the questionnaire based on user answers."""
    reconfig_answers: List[Tuple[int, str, str]] = (
        collect_reconfiguration_questions(tui=tui, answered_only=False)
    )
    selected_accounts = collect_selected_accounts(tui)
    preserved_answers: List[Union[None, Tuple[str, Any]]] = (
        preserve_current_answers(tui=tui)
    )
    current_questions = tui.questions  # TODO: switch to input iso str
    transaction_question = (
        account_questions.get_transaction_question_identifier()
    )

    # Process each reconfiguration answer
    for question_nr, question_str, answer in reconfig_answers:
        if question_str != transaction_question:
            continue  # Only process "Add another account (y/n)?" questions

        # Check if there is a later reconfiguration question
        has_later_reconfig: bool = has_later_account_question(
            current_account_question_index=question_nr,
            reconfig_answers=reconfig_answers,
        )

        if answer == "y" and not has_later_reconfig:
            # No later reconfiguration question; add a new block of account questions
            return handle_add_account(
                account_questions,
                current_questions,
                preserved_answers,
                selected_accounts,
            )
        elif answer == "y" and has_later_reconfig:
            pass
        elif answer == "n":
            if has_later_reconfig:
                # Preserve current block and remove all subsequent account questions
                print(f"preserved_answers={preserved_answers}")
                preserved_answers: List[Tuple[str, Any]] = (
                    remove_later_account_questions(
                        tui=tui,
                        account_questions=account_questions,
                        start_question_nr=question_nr,
                        preserved_answers=preserved_answers,
                    )
                )
                return handle_optional_questions(
                    tui=tui,
                    optional_questions=optional_questions,
                    current_questions=tui.inputs,
                    preserved_answers=preserved_answers,
                )

    # If no reconfiguration answers or no action taken, set focus to next unanswered question
    return set_default_focus_and_answers(tui, preserved_answers)
