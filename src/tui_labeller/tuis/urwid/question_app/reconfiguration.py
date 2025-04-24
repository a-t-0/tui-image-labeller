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

    # Collect selected accounts to prevent reuse
    selected_accounts = set()
    for input_widget in tui.inputs:
        widget = input_widget.base_widget
        if isinstance(
            widget,
            (VerticalMultipleChoiceWidget, HorizontalMultipleChoiceWidget),
        ):
            if (
                widget.question.question.startswith("Account for")
                and widget.has_answer()
            ):
                answer = widget.get_answer()
                if answer:
                    selected_accounts.add(answer)

    # Preserve all current answers
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
            # Filter out already selected accounts
            available_accounts = [
                acc
                for acc in account_questions.account_infos
                if acc not in selected_accounts
            ]
            if available_accounts:
                # Find the index of the last account question
                last_account_idx = max(
                    (
                        i
                        for i, q in enumerate(current_questions)
                        if q.question in account_question_identifiers
                    ),
                    default=-1,
                )
                # Generate new account questions with filtered accounts
                new_account_questions = AccountQuestions(
                    account_infos=available_accounts,
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
                # Set focus to the first new account question
                new_tui.set_focus(
                    len(current_questions[: last_account_idx + 1])
                )
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
                # Set focus to the first optional question
                new_tui.set_focus(len(current_questions))
                return new_tui
            # Set focus to the first optional question if already present
            first_optional_idx = next(
                (
                    i
                    for i, q in enumerate(current_questions)
                    if q.question in optional_question_identifiers
                ),
                len(current_questions) - 1,
            )
            tui.set_focus(first_optional_idx)
            return tui

    # Default case: return current TUI with preserved answers and focus on next unanswered question
    for i, input_widget in enumerate(tui.inputs):
        widget = input_widget.base_widget
        question_text = widget.question.question
        if question_text in preserved_answers:
            widget.set_answer(preserved_answers[question_text])
        if not widget.has_answer():
            tui.set_focus(i)
            break
    return tui
