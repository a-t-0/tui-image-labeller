from datetime import datetime
from typing import Dict, List, Optional, Union

from hledger_preprocessor.TransactionObjects.Receipt import (  # For image handling
    ExchangedItem,
    Receipt,
)
from typeguard import typechecked

from tui_labeller.input_parser.input_parser import (
    ask_yn_question_is_yes,
    get_float_input,
    get_input_with_az_chars_answer,
)
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
from tui_labeller.tuis.urwid.receipts.ItemQuestionnaire import (
    ItemQuestionnaire,
    get_exchanged_item,
)
from tui_labeller.tuis.urwid.receipts.payments_enum import PaymentTypes


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

    return process_receipt(starter_questions=questions)
    # return Receipt(
    #     shop_name=shop_name,
    #     receipt_owner_account_holder=receipt_owner_account_holder,
    #     receipt_owner_bank=receipt_owner_bank,
    #     receipt_owner_account_holder_type=receipt_owner_account_holder_type,
    #     bought_items=bought_items,
    #     returned_items=returned_items,
    #     the_date=receipt_date,
    #     payed_total_read=payed_total_read,
    #     shop_address=shop_address,
    #     shop_account_nr=shop_account_nr,
    #     subtotal=subtotal,
    #     total_tax=total_tax,
    #     cash_payed=cash_payed,
    #     cash_returned=cash_returned,
    #     receipt_owner_address=receipt_owner_address,
    #     receipt_categorisation=receipt_categorisation,
    # )


@typechecked
def process_receipt(
    starter_questions: List[
        Union[
            InputValidationQuestionData,
            MultipleChoiceQuestionData,
            DateQuestionData,
        ]
    ],
) -> Optional[Receipt]:

    # questions = create_item_questions(item_type, parent_category, parent_date)
    questionnaire_tui: QuestionnaireApp = create_and_run_questionnaire(
        questions=starter_questions,
        header=f"Entering a receipt.",
    )
    # TODO: check if all answers are valid.
    # TODO: check if all answers so far are consistent.
    the_answers: Dict[
        Union[DateTimeQuestion, InputValidationQuestion, MultipleChoiceWidget],
        Union[str, float, int, datetime],
    ] = questionnaire_tui.get_answers()

    for question_widget, answer in the_answers.items():
        if isinstance(question_widget, MultipleChoiceWidget):
            payment_type_question: str = answer

    if payment_type_question is None:
        raise ValueError("Did not find payment type.")
    if (
        payment_type_question == PaymentTypes.CASH.value
        or payment_type_question == PaymentTypes.BOTH.value
    ):
        print("TODO: follow up with cash questions.")
    if (
        payment_type_question == PaymentTypes.CARD.value
        or payment_type_question == PaymentTypes.BOTH.value
    ):
        print("TODO: follow up with pin questions.")
    if payment_type_question == PaymentTypes.OTHER.value:
        raise NotImplementedError("Did not implement other transaction types.")

    return None


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
