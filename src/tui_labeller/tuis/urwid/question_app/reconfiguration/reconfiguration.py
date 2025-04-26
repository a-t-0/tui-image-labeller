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
from tui_labeller.tuis.urwid.QuestionnaireApp import (
    QuestionnaireApp,
)
from tui_labeller.tuis.urwid.receipts.AccountQuestions import AccountQuestions
from tui_labeller.tuis.urwid.receipts.OptionalQuestions import OptionalQuestions


@typechecked
def collect_reconfig_answers(tui: "QuestionnaireApp") -> dict:
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
    last_account_question = (
        account_questions.get_transaction_question_identifier()
    )
    current_questions = tui.questions
    reconfig_answers = collect_reconfig_answers(tui)
    selected_accounts = collect_selected_accounts(tui)
    preserved_answers = preserve_current_answers(tui)

    if last_account_question in reconfig_answers:
        if reconfig_answers[last_account_question] == "y":
            return handle_add_account(
                account_questions,
                current_questions,
                preserved_answers,
                selected_accounts,
            )
        elif reconfig_answers[last_account_question] == "n":
            # Remove account questions before adding optional questions
            non_account_questions = [
                q
                for q in current_questions
                if q.question
                not in {q.question for q in account_questions.account_questions}
            ]
            return handle_optional_questions(
                tui,
                optional_questions,
                non_account_questions,
                preserved_answers,
            )

    return set_default_focus_and_answers(tui, preserved_answers)
