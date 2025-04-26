from typing import List, Tuple

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
    remove_account_questions,
)
from tui_labeller.tuis.urwid.QuestionnaireApp import (
    QuestionnaireApp,
)
from tui_labeller.tuis.urwid.receipts.AccountQuestions import AccountQuestions
from tui_labeller.tuis.urwid.receipts.OptionalQuestions import OptionalQuestions


@typechecked
def collect_reconfig_answers(
    tui: "QuestionnaireApp",
) -> List[Tuple[int, str, str]]:
    """Collect answers from widgets that trigger reconfiguration as a list of
    (position, question, answer)."""
    reconfig_answers = []
    for index, input_widget in enumerate(tui.inputs):
        widget = input_widget.base_widget
        if isinstance(
            widget,
            (VerticalMultipleChoiceWidget, HorizontalMultipleChoiceWidget),
        ):
            if widget.question.reconfigurer and widget.has_answer():
                answer = widget.get_answer()
                if answer:
                    reconfig_answers.append(
                        (index, widget.question.question, answer)
                    )
    return reconfig_answers


@typechecked
def collect_reconfig_answers_old(tui: "QuestionnaireApp") -> dict:
    """Collect answers from widgets that trigger reconfiguration."""
    reconfig_answers = {}
    for input_widget in tui.inputs:
        widget = input_widget.base_widget
        if isinstance(
            widget,
            (VerticalMultipleChoiceWidget, HorizontalMultipleChoiceWidget),
        ):
            if widget.question.reconfigurer and widget.has_answer():
                answer = widget.get_answer()
                if answer:
                    reconfig_answers[widget.question.question] = answer
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
def preserve_current_answers(tui: "QuestionnaireApp") -> dict:
    """Preserve all current answers from the questionnaire."""
    preserved_answers = {}
    for input_widget in tui.inputs:
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
                    preserved_answers[widget.question.question] = answer
    return preserved_answers


@typechecked
def handle_optional_questions(
    *,
    tui: "QuestionnaireApp",
    optional_questions: "OptionalQuestions",
    current_questions: list,
    preserved_answers: dict,
) -> "QuestionnaireApp":
    """Handle the addition or focusing of optional questions."""
    optional_question_identifiers = {
        oq.question for oq in optional_questions.optional_questions
    }

    if not any(
        q.question in optional_question_identifiers for q in current_questions
    ):
        new_questions = (
            current_questions + optional_questions.optional_questions
        )
        great_tui = create_questionnaire(
            questions=new_questions,
            header="Answer the receipt questions.",
        )

        for input_widget in great_tui.inputs:
            widget = input_widget.base_widget
            question_text = widget.question.question
            if question_text in preserved_answers:
                widget.set_answer(preserved_answers[question_text])

        return great_tui

    first_optional_idx = next(
        (
            i
            for i, q in enumerate(current_questions)
            if q.question in optional_question_identifiers
        ),
        0,  # Focus on first question if no optional questions found
    )
    return tui


@typechecked
def set_default_focus_and_answers(
    tui: "QuestionnaireApp", preserved_answers: dict
) -> "QuestionnaireApp":
    """Set preserved answers and focus on the next unanswered question."""
    for i, input_widget in enumerate(tui.inputs):
        widget = input_widget.base_widget
        question_text = widget.question.question
        if question_text in preserved_answers:
            widget.set_answer(preserved_answers[question_text])
        # if not widget.has_answer():
        #     tui.set_focus(i)
        #     break
    return tui


@typechecked
def get_configuration(
    tui: "QuestionnaireApp",
    account_questions: "AccountQuestions",
    optional_questions: "OptionalQuestions",
) -> "QuestionnaireApp":
    """Reconfigure the questionnaire based on user answers."""
    reconfig_answers: List[Tuple[int, str, str]] = collect_reconfig_answers(tui)
    selected_accounts = collect_selected_accounts(tui)
    preserved_answers = preserve_current_answers(tui)
    current_questions = tui.questions
    transaction_question = (
        account_questions.get_transaction_question_identifier()
    )

    # Process each reconfiguration answer
    for question_nr, question_str, answer in sorted(
        reconfig_answers, key=lambda x: x[0]
    ):
        if question_str != transaction_question:
            continue  # Only process "Add another account (y/n)?" questions

        # Check if there is a later reconfiguration question
        has_later_reconfig = any(
            later_question_nr > question_nr
            and later_question_str == transaction_question
            for later_question_nr, later_question_str, _ in reconfig_answers
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
            # Move focus to the next reconfiguration question
            # next_reconfig_nr = min(
            #     later_question_nr
            #     for later_question_nr, later_question_str, _ in reconfig_answers
            #     if later_question_nr > question_nr and later_question_str == transaction_question
            # )
            # tui.set_focus(next_reconfig_nr)
            # return tui
        elif answer == "n" and has_later_reconfig:
            # Preserve current block and remove all subsequent account questions
            non_account_questions = remove_account_questions(
                current_questions,
                account_questions,
                question_nr,
            )
            return handle_optional_questions(
                tui=tui,
                optional_questions=optional_questions,
                current_questions=non_account_questions,
                preserved_answers=preserved_answers,
            )

    # If no reconfiguration answers or no action taken, set focus to next unanswered question
    return set_default_focus_and_answers(tui, preserved_answers)
