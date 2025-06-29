from typing import Any, List, Tuple, Union

from hledger_preprocessor.TransactionObjects.Receipt import (
    Receipt,
)
from typeguard import typechecked
from urwid import AttrMap

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
from tui_labeller.tuis.urwid.question_data_classes import (
    AddressSelectorQuestionData,
    DateQuestionData,
    HorizontalMultipleChoiceQuestionData,
    InputValidationQuestionData,
    VerticalMultipleChoiceQuestionData,
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
    """Collect answers from widgets that trigger reconfiguration."""
    reconfig_answers = []
    for index, input_widget in enumerate(tui.inputs):
        widget = input_widget.base_widget
        if isinstance(widget, HorizontalMultipleChoiceWidget):
            if widget.question_data.reconfigurer:
                answer = widget.get_answer() if widget.has_answer() else ""
                if not answered_only or (answered_only and answer):
                    reconfig_answers.append(
                        (index, widget.question_data.question, answer)
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
                widget.question_data.question.startswith(
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
                if answer != "":
                    preserved_answers[i] = (
                        widget.question_data.question,
                        answer,
                    )
                else:
                    print(
                        f"ANSWER IS:{answer}NOT ANS"
                        f" for:{widget.question_data.question.replace('\n','')}"
                    )
            else:
                print(f"No ans given for = {widget.question_data.question}")
        else:
            print(f"Different input type:{widget.__dict__}")
    return preserved_answers


@typechecked
def handle_manual_address_questions(
    *,
    tui: "QuestionnaireApp",
    optional_questions: "OptionalQuestions",
    current_questions: list,
    preserved_answers: List[Union[None, Tuple[str, Any]]],
) -> "QuestionnaireApp":
    """Add or remove manual address questions based on the address selector
    answer."""
    input("HI")
    address_selector_question = "Select Shop Address:\n"
    address_selector_index = None
    address_selector_answer = None

    # Find the address selector question and its answer
    for index, input_widget in enumerate(tui.inputs):
        widget = input_widget.base_widget
        if (
            isinstance(widget, VerticalMultipleChoiceWidget)
            and widget.question_data.question == address_selector_question
            and widget.has_answer()
        ):
            address_selector_index = index
            address_selector_answer = widget.get_answer()
            break

    # Get manual address question identifiers
    manual_address_questions = optional_questions.get_manual_address_questions()
    manual_question_ids = {q.question for q in manual_address_questions}

    # Check if manual address questions are currently present
    current_question_ids = {
        q.base_widget.question_data.question for q in current_questions
    }
    has_manual_questions = any(
        q in manual_question_ids for q in current_question_ids
    )

    # If "manual address" is selected and manual questions are not present, add them
    if address_selector_answer == "manual address" and not has_manual_questions:
        # Find the position to insert manual address questions (after address selector)
        insert_index = (
            address_selector_index + 1
            if address_selector_index is not None
            else len(current_questions)
        )
        new_questions = (
            current_questions[:insert_index]
            + manual_address_questions
            + current_questions[insert_index:]
        )
        print(f"new_questions={new_questions}")
        converted_questions: List[
            Union[
                DateQuestionData,
                InputValidationQuestionData,
                VerticalMultipleChoiceQuestionData,
                HorizontalMultipleChoiceQuestionData,
                AddressSelectorQuestionData,
            ]
        ] = []
        for i, q in enumerate(new_questions):
            print(f"{i},type={type(q)}")
            if isinstance(q, AttrMap):
                base_widget = q.base_widget
                if not isinstance(
                    base_widget.question_data,
                    (
                        DateQuestionData,
                        InputValidationQuestionData,
                        VerticalMultipleChoiceQuestionData,
                        HorizontalMultipleChoiceQuestionData,
                        AddressSelectorQuestionData,
                    ),
                ):
                    raise ValueError(
                        f"Unexpected type:{base_widget.question_data}"
                    )
                converted_questions.append(base_widget.question_data)

            elif not isinstance(
                q,
                (
                    DateQuestionData,
                    InputValidationQuestionData,
                    VerticalMultipleChoiceQuestionData,
                    HorizontalMultipleChoiceQuestionData,
                    AddressSelectorQuestionData,
                ),
            ):

                converted_questions.append(q.question_data)
            else:
                converted_questions.append(q)

        # Create new questionnaire with updated questions
        new_tui = create_questionnaire(
            questions=converted_questions,
            header="Answer the receipt questions.",
            labelled_receipts=optional_questions.labelled_receipts,
        )
        # Restore preserved answers
        return set_default_focus_and_answers(
            tui=new_tui,
            preserved_answers=preserved_answers,
        )

    # If "manual address" is not selected and manual questions are present, remove them
    elif address_selector_answer != "manual address" and has_manual_questions:
        # Filter out manual address questions
        new_questions = [
            q
            for q in current_questions
            if q.base_widget.question_data.question not in manual_question_ids
        ]
        # Update preserved answers to remove answers for manual address questions
        preserved_answers = [
            ans
            for ans in preserved_answers
            if ans is None or ans[0] not in manual_question_ids
        ]
        # Create new questionnaire with updated questions
        new_tui = create_questionnaire(
            questions=new_questions,
            header="Answer the receipt questions.",
            labelled_receipts=optional_questions.labelled_receipts,
        )
        # Restore preserved answers
        return set_default_focus_and_answers(
            tui=new_tui,
            preserved_answers=preserved_answers,
        )

    # No changes needed
    return tui


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
        q.base_widget.question_data.question in optional_question_identifiers
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
        question_text = widget.question_data.question
        if i < len(preserved_answers):  # New questions may be added.
            if (
                preserved_answers[i] is not None
                and preserved_answers[i][0] == question_text
            ):
                widget.set_answer(preserved_answers[i][1])
    return tui


@typechecked
def get_configuration(
    tui: "QuestionnaireApp",
    account_questions: "AccountQuestions",
    optional_questions: "OptionalQuestions",
    labelled_receipts: List[Receipt],
) -> "QuestionnaireApp":
    """Reconfigure the questionnaire based on user answers."""
    reconfig_answers = collect_reconfiguration_questions(
        tui=tui, answered_only=False
    )
    selected_accounts = collect_selected_accounts(tui)
    preserved_answers = preserve_current_answers(tui=tui)
    print(f"preserved_answers={preserved_answers}")
    current_questions = tui.questions
    transaction_question = (
        account_questions.get_transaction_question_identifier()
    )

    is_address_selector_focused: bool = is_at_address_selector(tui=tui)
    input(f"is_address_selector_focused={is_address_selector_focused}")
    # Handle manual address questions if the address selector is focused
    if is_address_selector_focused:
        tui = handle_manual_address_questions(
            tui=tui,
            optional_questions=optional_questions,
            current_questions=tui.inputs,
            preserved_answers=preserved_answers,
        )

    # Process account-related reconfiguration answers
    for question_nr, question_str, answer in reconfig_answers:
        if question_str != transaction_question:
            continue  # Only process "Add another account (y/n)?" questions

        has_later_reconfig = has_later_account_question(
            current_account_question_index=question_nr,
            reconfig_answers=reconfig_answers,
        )

        if answer == "y" and not has_later_reconfig:
            # Add a new block of account questions
            return handle_add_account(
                account_questions=account_questions,
                current_questions=current_questions,
                preserved_answers=preserved_answers,
                selected_accounts=selected_accounts,
                labelled_receipts=labelled_receipts,
            )
        elif answer == "y" and has_later_reconfig:
            pass
        elif answer == "n":
            if has_later_reconfig:
                # Remove subsequent account questions
                preserved_answers = remove_later_account_questions(
                    tui=tui,
                    account_questions=account_questions,
                    start_question_nr=question_nr,
                    preserved_answers=preserved_answers,
                )
                tui = handle_optional_questions(
                    tui=tui,
                    optional_questions=optional_questions,
                    current_questions=tui.inputs,
                    preserved_answers=preserved_answers,
                )

    # Set focus to the next unanswered question
    return set_default_focus_and_answers(tui, preserved_answers)


@typechecked
def is_at_address_selector(*, tui: QuestionnaireApp) -> bool:
    focused_widget = tui.get_focus_widget()

    if isinstance(focused_widget, VerticalMultipleChoiceWidget):
        if focused_widget.question_data.question == "Select Shop Address:\n":
            return True
    return False
