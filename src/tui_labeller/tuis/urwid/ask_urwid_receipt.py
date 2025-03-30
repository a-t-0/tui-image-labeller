from datetime import datetime
from typing import Dict, Union

from hledger_preprocessor.TransactionObjects.Receipt import (  # For image handling
    ExchangedItem,
    Receipt,
)
from typeguard import typechecked

from tui_labeller.tuis.urwid.date_question.DateTimeQuestion import (
    DateTimeQuestion,
)
from tui_labeller.tuis.urwid.input_validation.InputType import InputType
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
    AISuggestion,
    DateQuestionData,
    HistorySuggestion,
    InputValidationQuestionData,
    MultipleChoiceQuestionData,
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
from tui_labeller.tuis.urwid.receipts.receipt_answer_parser import (
    get_payment_details,
)
from tui_labeller.tuis.urwid.receipts.ReceiptQuestionnaire import (
    ReceiptQuestionnaire,
)


@typechecked
def build_receipt_from_urwid(
    *,
    receipt_owner_account_holder: str,
    receipt_owner_bank: str,
    receipt_owner_account_holder_type: str,
):
    questions = [
        InputValidationQuestionData(
            caption="Receipt category: ",
            input_type=InputType.LETTERS,
            ans_required=True,
            ai_suggestions=[
                AISuggestion("apple", 0.9, "FruitNet"),
                AISuggestion("banana", 0.85, "FruitNet"),
                AISuggestion("forest", 0.6, "TypoCorrector"),
            ],
            history_suggestions=[
                HistorySuggestion("pear", 5),
                HistorySuggestion("peach", 3),
                HistorySuggestion("apple", 2),
            ],
        ),
        DateQuestionData(
            caption="Receipt date & time (YYYY-MM-DD HH:MM):",
            date_only=True,
            ai_suggestions=[
                AISuggestion("2025-03-17 14:30", 0.92, "Datepredictor"),
                AISuggestion("2025-03-17 09:00", 0.88, "TimeMaster"),
                AISuggestion("2025-03-18 12:00", 0.80, "ChronoAI"),
            ],
        ),
        MultipleChoiceQuestionData(
            question="Transaction type",
            choices=[
                pt.value for pt in PaymentTypes
            ],  # Extracts "cash", "card", "both", "other"
            ai_suggestions=[
                AISuggestion(PaymentTypes.CASH.value, 0.99, "ReadAI"),
                AISuggestion(PaymentTypes.CARD.value, 0.1, "SomeAI"),
                AISuggestion(PaymentTypes.BOTH.value, 0.97, "AnotherAI"),
            ],
        ),
    ]

    return process_receipt()


@typechecked
def process_receipt() -> Receipt:
    # Step 1: Run base questionnaire
    pq = ReceiptQuestionnaire()
    tui = create_and_run_questionnaire(
        questions=pq.base_questions,
        header="Entering payment details",
    )
    base_answers = tui.get_answers()

    # Step 2: Determine transaction type and add follow-up questions
    transaction_q = next(
        q for q in base_answers.keys() if q.question == "Transaction type"
    )
    transaction_type = base_answers[transaction_q]

    extra_questions = []
    if transaction_type in [PaymentTypes.CASH.value, PaymentTypes.BOTH.value]:
        extra_questions.extend(CashPaymentQuestions().questions)
    if transaction_type in [PaymentTypes.CARD.value, PaymentTypes.BOTH.value]:
        extra_questions.extend(CardPaymentQuestions().questions)
    if transaction_type == PaymentTypes.OTHER.value:
        raise NotImplementedError("Other transaction types not implemented")

    # Step 3: Run TUI again with extra questions if needed
    all_answers = base_answers
    if extra_questions:
        pq.verify_unique_questions(extra_questions)  # Ensure no duplicates
        extra_tui = create_and_run_questionnaire(
            questions=extra_questions,
            header=f"Additional details for {transaction_type}",
        )
        all_answers.update(extra_tui.get_answers())

    return get_payment_details(answers=all_answers)


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
