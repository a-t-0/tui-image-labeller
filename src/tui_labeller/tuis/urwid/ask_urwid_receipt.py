from datetime import datetime
from typing import Dict, Union

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
    remove_last_n_questions_from_list,
)


@typechecked
def update_questions_based_on_transaction_type(
    *,
    app: QuestionnaireApp,
    current_transaction_type: PaymentTypes,
) -> PaymentTypes:
    """Update the questionnaire by adding/removing questions based on the new
    transaction type.

    Args:
        app: The running QuestionnaireApp instance.
        current_transaction_type: The transaction type from the previous run.

    Returns:
        The new transaction type after updates.
    """
    new_transaction_type: PaymentTypes = app.get_question_by_text_and_type(
        question_text="Transaction type",
        question_type=MultipleChoiceWidget,
    )

    # If transaction type hasn't changed, no updates needed
    if new_transaction_type == current_transaction_type:
        return new_transaction_type

    # Determine which questions to keep/remove based on new transaction type
    cash_questions = CashPaymentQuestions().questions
    card_questions = CardPaymentQuestions().questions
    current_questions = app.questions

    # Identify existing cash/card questions by their captions
    cash_captions = {
        getattr(q, "question", getattr(q, "caption", None))
        for q in cash_questions
    }
    card_captions = {
        getattr(q, "question", getattr(q, "caption", None))
        for q in card_questions
    }

    # Count how many cash/card questions are currently in the app
    # current_question_captions = {getattr(q, "question", getattr(q, "caption", None)) for q in current_questions}
    cash_questions_present = [
        q
        for q in current_questions
        if getattr(q, "question", getattr(q, "caption", None)) in cash_captions
    ]
    card_questions_present = [
        q
        for q in current_questions
        if getattr(q, "question", getattr(q, "caption", None)) in card_captions
    ]

    # Logic to add/remove questions based on new transaction type
    if new_transaction_type in [
        PaymentTypes.CASH.value,
        PaymentTypes.BOTH.value,
    ]:
        if not cash_questions_present:
            append_questions_to_list(app=app, new_questions=cash_questions)
    else:
        if cash_questions_present:
            remove_last_n_questions_from_list(
                app=app, n=len(cash_questions_present)
            )

    if new_transaction_type in [
        PaymentTypes.CARD.value,
        PaymentTypes.BOTH.value,
    ]:
        if not card_questions_present:
            append_questions_to_list(app=app, new_questions=card_questions)
    else:
        if card_questions_present:
            remove_last_n_questions_from_list(
                app=app, n=len(card_questions_present)
            )

    if new_transaction_type == PaymentTypes.OTHER.value:
        raise NotImplementedError("Other transaction types not implemented")

    # Re-run the questionnaire with updated questions
    app.run()

    input("DONE")
    final_transaction_type: PaymentTypes = (
        update_questions_based_on_transaction_type(
            app=app,
            current_transaction_type=new_transaction_type,
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
    manual_transaction_type: PaymentTypes = PaymentTypes.BOTH

    # base_answers = tui.get_answers()

    # # Step 2: Determine initial transaction type and add follow-up questions
    # transaction_q = next(
    #     q for q in base_answers.keys() if q.question == "Transaction type"
    # )
    # transaction_type = base_answers[transaction_q]

    # extra_questions = []
    # if transaction_type in [PaymentTypes.CASH.value, PaymentTypes.BOTH.value]:
    #     extra_questions.extend(CashPaymentQuestions().questions)
    # if transaction_type in [PaymentTypes.CARD.value, PaymentTypes.BOTH.value]:
    #     extra_questions.extend(CardPaymentQuestions().questions)
    # if transaction_type == PaymentTypes.OTHER.value:
    #     raise NotImplementedError("Other transaction types not implemented")

    # if extra_questions:
    #     append_questions_to_list(app=tui, new_questions=extra_questions)
    #     tui.run()

    # Step 3: Update questions based on new transaction type (handles the TODOs)
    final_transaction_type: PaymentTypes = (
        update_questions_based_on_transaction_type(
            app=tui,
            current_transaction_type=manual_transaction_type,  # TODO: improve logic.
        )
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
