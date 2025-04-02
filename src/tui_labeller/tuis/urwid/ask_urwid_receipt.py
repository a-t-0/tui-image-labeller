from datetime import datetime
from typing import Any, Dict, List, Union

from hledger_preprocessor.TransactionObjects.Receipt import (  # For image handling
    ExchangedItem,
    Receipt,
)
from typeguard import typechecked

from tui_labeller.tuis.urwid.appending_questions import append_questions_to_list
from tui_labeller.tuis.urwid.date_question.DateTimeQuestion import (
    DateTimeQuestion,
)
from tui_labeller.tuis.urwid.input_validation.InputValidationQuestion import (
    InputValidationQuestion,
)
from tui_labeller.tuis.urwid.mc_question.MultipleChoiceWidget import (
    MultipleChoiceWidget,
)
from tui_labeller.tuis.urwid.merged_questions import (
    QuestionnaireApp,
    create_and_run_questionnaire,
)
from tui_labeller.tuis.urwid.question_data_classes import (
    InputValidationQuestionData,
)
from tui_labeller.tuis.urwid.receipts.CardPaymentQuestions import (
    CardPaymentQuestions,
)
from tui_labeller.tuis.urwid.receipts.CashPaymentQuestions import (
    CashPaymentQuestions,
)
from tui_labeller.tuis.urwid.receipts.ItemQuestionnaire import (
    ItemQuestionnaire,
    get_exchanged_item,
)
from tui_labeller.tuis.urwid.receipts.payments_enum import PaymentTypes
from tui_labeller.tuis.urwid.receipts.ReceiptQuestionnaire import (
    ReceiptQuestionnaire,
)
from tui_labeller.tuis.urwid.removing_questions import (
    remove_specific_questions_from_list,
)


@typechecked
def has_questions(
    *,
    expected_questions: List[InputValidationQuestionData],
    actual_questions: List[Any],
) -> bool:
    """Determine if questions of a specific payment type are present."""

    nr_of_matching_questions: int = nr_of_questions(
        expected_questions=expected_questions, actual_questions=actual_questions
    )

    if nr_of_matching_questions > 0:
        if nr_of_matching_questions != len(expected_questions):
            raise ValueError(
                "Either all or none of the questions must be present. Found"
                f" {nr_of_matching_questions} out of"
                f" {len(expected_questions)} questions."
            )
        return True
    return False


@typechecked
def nr_of_questions(
    expected_questions: List[InputValidationQuestionData],
    actual_questions: List[Any],
) -> int:
    """Count the number of questions of a specific payment type."""
    question_strings = [q.question for q in expected_questions]
    question_count = 0

    for tui_question in actual_questions:
        tui_text = getattr(
            tui_question, "question", getattr(tui_question, "caption", None)
        )
        if tui_text in question_strings:
            question_count += 1

    return question_count


@typechecked
def update_questionnaire(
    *,
    app: QuestionnaireApp,
    new_transaction_type: PaymentTypes,
    cash_questions: List[Any],
    card_questions: List[Any],
    has_cash_questions: bool,
    has_card_questions: bool,
) -> None:
    """Update the questionnaire based on the transaction type."""

    # First handle removal of cash questions if switching away from cash
    if new_transaction_type not in [PaymentTypes.CASH, PaymentTypes.BOTH]:
        if has_cash_questions:
            remove_specific_questions_from_list(
                app=app, expected_questions=cash_questions
            )
            assert (
                nr_of_questions(
                    expected_questions=cash_questions,
                    actual_questions=app.questions,
                )
                == 0
            ), (
                "Expected 0 cash questions remaining, but found"
                f" {nr_of_questions(expected_questions=cash_questions, actual_questions=app.questions)}"
            )

    # Then handle removal of card questions if switching away from card
    if new_transaction_type not in [PaymentTypes.CARD, PaymentTypes.BOTH]:
        if has_card_questions:
            remove_specific_questions_from_list(
                app=app, expected_questions=card_questions
            )
            assert (
                nr_of_questions(
                    expected_questions=card_questions,
                    actual_questions=app.questions,
                )
                == 0
            ), (
                "Expected 0 card questions remaining, but found"
                f" {nr_of_questions(expected_questions=card_questions, actual_questions=app.questions)}"
            )

    # Now handle adding cash questions if needed
    if new_transaction_type in [PaymentTypes.CASH, PaymentTypes.BOTH]:
        if not has_cash_questions:
            append_questions_to_list(app=app, new_questions=cash_questions)
            assert nr_of_questions(
                expected_questions=cash_questions,
                actual_questions=app.questions,
            ) == len(cash_questions), (
                f"Expected {len(cash_questions)} cash questions, but found"
                f" {nr_of_questions(expected_questions=cash_questions, actual_questions=app.questions)}"
            )

    # Finally handle adding card questions if needed
    if new_transaction_type in [PaymentTypes.CARD, PaymentTypes.BOTH]:
        if not has_card_questions:
            append_questions_to_list(app=app, new_questions=card_questions)
            assert nr_of_questions(
                expected_questions=card_questions,
                actual_questions=app.questions,
            ) == len(card_questions), (
                f"Expected {len(card_questions)} card questions, but found"
                f" {nr_of_questions(expected_questions=card_questions, actual_questions=app.questions)}"
            )

    if new_transaction_type == PaymentTypes.OTHER.value:
        raise NotImplementedError("Other transaction types not implemented")


@typechecked
def update_questions_based_on_transaction_type(
    *,
    app: QuestionnaireApp,
    current_transaction_type: PaymentTypes,
    nr_of_base_questions: int,
    is_first_run: bool,
) -> PaymentTypes:
    """Main function to update questions based on transaction type."""

    new_transaction_type: PaymentTypes = app.get_question_by_text_and_type(
        question_text="Transaction type",
        question_type=MultipleChoiceWidget,
    )

    if new_transaction_type == current_transaction_type and not is_first_run:
        return new_transaction_type

    cash_questions = CashPaymentQuestions().questions
    card_questions = CardPaymentQuestions().questions
    actual_questions = app.questions

    has_cash_questions = has_questions(
        expected_questions=cash_questions, actual_questions=actual_questions
    )
    has_card_questions = has_questions(
        expected_questions=card_questions, actual_questions=actual_questions
    )

    update_questionnaire(
        app=app,
        new_transaction_type=new_transaction_type,
        cash_questions=cash_questions,
        card_questions=card_questions,
        has_cash_questions=has_cash_questions,
        has_card_questions=has_card_questions,
    )

    if not is_first_run:
        app.run(
            alternative_start_pos=nr_of_base_questions + 1
        )  # TODO: parameterise header.
    else:
        app.run()

    final_transaction_type: PaymentTypes = (
        update_questions_based_on_transaction_type(
            app=app,
            current_transaction_type=new_transaction_type,
            nr_of_base_questions=nr_of_base_questions,
            is_first_run=False,
        )
    )
    return final_transaction_type


@typechecked
def build_receipt_from_urwid(
    *,
    receipt_owner_account_holder: str,
    receipt_owner_bank: str,
    receipt_owner_account_holder_type: str,
) -> Receipt:
    # Step 1: Run base questionnaire
    pq = ReceiptQuestionnaire()
    tui: QuestionnaireApp = create_and_run_questionnaire(
        questions=pq.base_questions,
        header="Entering payment details",
    )

    new_transaction_type: PaymentTypes = tui.get_question_by_text_and_type(
        question_text="Transaction type",
        question_type=MultipleChoiceWidget,
    )

    update_questions_based_on_transaction_type(
        app=tui,
        current_transaction_type=new_transaction_type,  # TODO: improve logic.
        nr_of_base_questions=len(pq.base_questions),
        is_first_run=True,
    )

    # Step 4: Build and return the receipt with final answers
    final_answers = tui.get_answers()
    # Assuming Receipt class takes these parameters and answers
    return Receipt(
        owner_account_holder=receipt_owner_account_holder,
        bank=receipt_owner_bank,
        account_holder_type=receipt_owner_account_holder_type,
        answers=final_answers,
    )


@typechecked
def process_single_item(
    item_type: str,
    parent_category: str,
    parent_date: datetime,
) -> ExchangedItem:
    # Create questions for current item type
    itemQuestionnaire: ItemQuestionnaire = ItemQuestionnaire(
        item_type=item_type,
        parent_category=parent_category,
        parent_date=parent_date,
    )

    # questions = create_item_questions(item_type, parent_category, parent_date)
    questionnaire_tui: QuestionnaireApp = create_and_run_questionnaire(
        questions=itemQuestionnaire.questions,
        header=f"Entering a {item_type} item.",
    )
    # TODO: check if all answers are valid.
    # TODO: check if all answers so far are consistent.
    the_answers: Dict[
        Union[DateTimeQuestion, InputValidationQuestion, MultipleChoiceWidget],
        Union[str, float, int, datetime],
    ] = questionnaire_tui.get_answers()

    item: ExchangedItem = get_exchanged_item(answers=the_answers)
    return item
