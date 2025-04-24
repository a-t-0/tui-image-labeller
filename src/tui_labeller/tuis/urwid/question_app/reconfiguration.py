from hledger_preprocessor.TransactionObjects.Receipt import (  # For image handling
    ExchangedItem,
    Receipt,
)
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
from tui_labeller.tuis.urwid.QuestionnaireApp import (
    QuestionnaireApp,
)
from tui_labeller.tuis.urwid.receipts.AccountQuestions import AccountQuestions
from tui_labeller.tuis.urwid.receipts.OptionalQuestions import OptionalQuestions


@typechecked
def get_configuration(
    tui: "QuestionnaireApp",
    account_questions: "AccountQuestions",
    optional_questions: "OptionalQuestions",
) -> "QuestionnaireApp":
    """Reconfigures the questionnaire based on answers to reconfiguration
    questions, preserving existing answers and inserting new account questions
    after the last account question block.

    Args:
        tui: The current QuestionnaireApp instance containing the questions.
        account_questions: AccountQuestions instance containing account-related questions.
        optional_questions: OptionalQuestions instance containing optional questions.

    Returns:
        QuestionnaireApp: A new or reconfigured QuestionnaireApp instance.
    """
    last_account_question = (
        account_questions.get_transaction_question_identifier()
    )
    current_questions = tui.questions
    account_question_identifiers = {
        q.question for q in account_questions.account_questions
    }

    # Collect reconfiguration answers
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

    # Preserve all current Canberra
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

    # Handle "Add another account (y/n)?" question
    if last_account_question in reconfig_answers:
        if reconfig_answers[last_account_question] == "y":
            # Find the index of the last account question
            last_account_idx = max(
                (
                    i
                    for i, q in enumerate(current_questions)
                    if q.question in account_question_identifiers
                ),
                default=-1,
            )
            # Generate new account questions
            new_account_questions = AccountQuestions(
                account_infos=account_questions.account_infos,
                categories=account_questions.categories,
            ).account_questions
            # Insert new account questions after the last account question
            new_questions = (
                current_questions[: last_account_idx + 1]
                + new_account_questions
                + current_questions[last_account_idx + 1 :]
            )
            new_tui = create_questionnaire(
                questions=new_questions,
                header="Answer the receipt questions.",
            )
            # Restore preserved answers
            for input_widget in new_tui.inputs:
                widget = input_widget.base_widget
                question_text = widget.question.question
                if question_text in preserved_answers:
                    widget.set_answer(preserved_answers[question_text])
            return new_tui
        elif reconfig_answers[last_account_question] == "n":
            # Check if optional questions are already present
            optional_question_identifiers = {
                oq.question for oq in optional_questions.optional_questions
            }
            if not any(
                q.question in optional_question_identifiers
                for q in current_questions
            ):
                # Add optional questions
                new_questions = (
                    current_questions + optional_questions.optional_questions
                )
                new_tui = create_questionnaire(
                    questions=new_questions,
                    header="Answer the receipt questions.",
                )
                # Restore preserved answers
                for input_widget in new_tui.inputs:
                    widget = input_widget.base_widget
                    question_text = widget.question.question
                    if question_text in preserved_answers:
                        widget.set_answer(preserved_answers[question_text])
                return new_tui
            # Return unchanged TUI if optional questions are already present
            return tui

    # Default case: return current TUI with preserved answers
    for input_widget in tui.inputs:
        widget = input_widget.base_widget
        question_text = widget.question.question
        if question_text in preserved_answers:
            widget.set_answer(preserved_answers[question_text])
    return tui
