from datetime import datetime
from typing import List, Optional, Union

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
from tui_labeller.tuis.urwid.input_validation.InputType import InputType
from tui_labeller.tuis.urwid.merged_questions import (
    create_and_run_questionnaire,
)
from tui_labeller.tuis.urwid.question_data_classes import (
    AISuggestion,
    DateQuestionData,
    InputValidationQuestionData,
    MultipleChoiceQuestionData,
)


@typechecked
def build_receipt_from_urwid(
    *,
    receipt_owner_account_holder: str,
    receipt_owner_bank: str,
    receipt_owner_account_holder_type: str,
):
    questions = [
        MultipleChoiceQuestionData(
            question="Transaction type",
            choices=["Cash", "Card", "Both", "Other"],
            ai_suggestions=[
                AISuggestion("Cash", 0.99, "ReadAI"),
                AISuggestion("Card", 0.1, "SomeAI"),
                AISuggestion("Both", 0.97, "AnotherAI"),
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
        # Add items
    ]
    receipt_categorisation: str = "swag:something"
    bought_items = get_items(
        item_type="bought",
        parent_category=receipt_categorisation,
        parent_date=datetime.now(),
    )
    returned_items = get_items(
        item_type="returned",
        parent_category=receipt_categorisation,
        parent_date=datetime.now(),
    )

    shop_account_nr: Union[None, str] = get_input_with_az_chars_answer(
        question=f"Shop account number (Optional, press enter to skip):",
        allowed_empty=True,
        allowed_chars=r"[a-zA-Z0-9:]+",
    )
    subtotal = get_float_input(
        question="Subtotal (Optional, press enter to skip): ",
        allow_optional=True,
    )
    total_tax = get_float_input(
        question="Total tax (Optional, press enter to skip): ",
        allow_optional=True,
    )

    receipt_owner_address = input("Receipt owner address (optional): ") or None

    shop_name: str = input(
        "Shop name: "
    )  # TODO: assert it does not have spaces, newlines or tabs.
    shop_address = input("Shop address: ")

    payed_with_cash: bool = ask_yn_question_is_yes(
        question="Did you pay with cash or receive cash? (y/n): "
    )
    cash_payed = False
    cash_returned = None

    # TODO: facilitate cash and wire transactions.
    if payed_with_cash:
        cash_payed = get_float_input(
            question="Amount paid in cash: ", allow_optional=False
        )
        cash_returned = get_float_input(
            question="Change returned: ", allow_optional=False
        )

    payed_by_card: bool = ask_yn_question_is_yes(
        question="Did you pay by card? (y/n): "
    )

    if payed_by_card:
        amount_payed_by_card = get_float_input(
            question="Amount paid by card: ", allow_optional=False
        )
        amount_returned_to_card = get_float_input(
            question="Change returned: ", allow_optional=False
        )

        # Get card details.
        payed_from_default_account: bool = ask_yn_question_is_yes(
            question=(
                "Was the receipt payed"
                f" from:\n{receipt_owner_account_holder}:{receipt_owner_bank}:{receipt_owner_account_holder_type}\n?(y/n)"
            )
        )
        if not payed_from_default_account:
            receipt_owner_account_holder = (
                get_input_with_az_chars_answer(
                    question=input(
                        "What is your name/the name of the account doing the"
                        " transaction?"
                    ),
                    allowed_empty=False,
                ),
            )
            receipt_owner_bank = (
                get_input_with_az_chars_answer(
                    question=input(
                        "What is the bank associated with the account? (E.g."
                        " triodos, bitfavo, uniswap, monero for bank, exchange,"
                        " dex, wallet respectively)"
                    ),
                    allowed_empty=False,
                ),
            )
            receipt_owner_account_holder_type = (
                get_input_with_az_chars_answer(
                    question=input(
                        "What type of account was used (e.g., checking, credit,"
                        " saving)?"
                    ),
                    allowed_empty=False,
                ),
            )
        # TODO: get to account/shop account.

    receipt_categorisation: str = get_input_with_az_chars_answer(
        question=f"Receipt category:",
        allowed_empty=False,
        allowed_chars=r"[a-zA-Z:]+",
    )

    payed_total_read: float = get_float_input(
        question="Payed total:", allow_optional=False
    )
    return Receipt(
        shop_name=shop_name,
        receipt_owner_account_holder=receipt_owner_account_holder,
        receipt_owner_bank=receipt_owner_bank,
        receipt_owner_account_holder_type=receipt_owner_account_holder_type,
        bought_items=bought_items,
        returned_items=returned_items,
        the_date=receipt_date,
        payed_total_read=payed_total_read,
        shop_address=shop_address,
        shop_account_nr=shop_account_nr,
        subtotal=subtotal,
        total_tax=total_tax,
        cash_payed=cash_payed,
        cash_returned=cash_returned,
        receipt_owner_address=receipt_owner_address,
        receipt_categorisation=receipt_categorisation,
    )


def get_items(
    *, item_type: str, parent_category: str, parent_date: datetime
) -> List[ExchangedItem]:
    items = []

    while True:
        # Create questions for current item type
        questions = create_item_questions(
            item_type, parent_category, parent_date
        )
        answers = create_and_run_questionnaire(questions)

        # Construct item from answers
        items.append(
            ExchangedItem(
                quantity=float(answers[2]),
                description=answers[0],
                the_date=parent_date,
                payed_unit_price=float(answers[3]),
                currency=answers[1],
                tax_per_unit=float(answers[5]) if answers[5] else 0,
                group_discount=float(answers[6]) if answers[6] else 0,
                category=answers[4] if answers[4] else parent_category,
                round_amount=None,
            )
        )

        # Check if user wants to add another item (last question)
        if answers[7].lower() != "y":
            break

    # If we're handling bought items, ask about returned items
    if item_type.lower() == "bought":
        return_questions = create_item_questions(
            "returned", parent_category, parent_date
        )
        returned_items = get_items(
            item_type="returned",
            parent_category=parent_category,
            parent_date=parent_date,
        )
        items.extend(returned_items)

    return items


def create_item_questions(
    item_type: str, parent_category: str, parent_date: datetime
):
    return [
        InputValidationQuestionData(
            caption=f"{item_type} item name (a-Z only): ",
            input_type=InputType.LETTERS,
            ai_suggestions=[
                AISuggestion("widget", 0.9, "ItemPredictor"),
                AISuggestion("gadget", 0.85, "ItemPredictor"),
            ],
            history_suggestions=[],
        ),
        InputValidationQuestionData(
            caption="Give price currency (e.g. EUR,BTC,$,YEN): ",
            input_type=InputType.FLOAT,
            ai_suggestions=[
                AISuggestion("USD", 0.95, "CurrencyNet"),
                AISuggestion("EUR", 0.90, "CurrencyNet"),
                AISuggestion("BTC", 0.85, "CurrencyNet"),
            ],
            history_suggestions=[],
        ),
        InputValidationQuestionData(
            caption=f"{item_type} item quantity: ",
            input_type=InputType.FLOAT,
            ai_suggestions=[
                AISuggestion("1", 0.9, "QuantityAI"),
                AISuggestion("2", 0.85, "QuantityAI"),
            ],
            history_suggestions=[],
        ),
        InputValidationQuestionData(
            caption=f"{item_type} item price: ",
            input_type=InputType.FLOAT,
            ai_suggestions=[
                AISuggestion("9.99", 0.9, "PricePredictor"),
                AISuggestion("19.99", 0.85, "PricePredictor"),
            ],
            history_suggestions=[],
        ),
        InputValidationQuestionData(
            caption=(
                f"{item_type} item category (empty is: {parent_category}): "
            ),
            input_type=InputType.LETTERS,
            ai_suggestions=[
                AISuggestion(parent_category, 0.95, "CategoryAI"),
                AISuggestion("general", 0.8, "CategoryAI"),
            ],
            history_suggestions=[],
        ),
        InputValidationQuestionData(
            caption="Tax per item (Optional, press enter for 0): ",
            input_type=InputType.FLOAT,
            ai_suggestions=[
                AISuggestion("0", 0.9, "TaxAI"),
                AISuggestion("1.99", 0.7, "TaxAI"),
            ],
            history_suggestions=[],
        ),
        InputValidationQuestionData(
            caption=(
                "Total discount for this group (Optional, press enter for 0): "
            ),
            input_type=InputType.FLOAT,
            ai_suggestions=[
                AISuggestion("0", 0.9, "DiscountAI"),
                AISuggestion("5.00", 0.7, "DiscountAI"),
            ],
            history_suggestions=[],
        ),
        MultipleChoiceQuestionData(
            question=f"Add another {item_type} item? (y/n): ",
            choices=["yes", "no"],
            ai_suggestions=[],
            terminator=True,
        ),
    ]


def get_items(
    *,
    item_type: str,
    parent_category: str,
    parent_date: datetime,
    retry_on_invalid: bool = True,
) -> List[ExchangedItem]:
    items = []

    def process_single_item() -> Optional[ExchangedItem]:
        # Create questions for current item type
        questions = create_item_questions(
            item_type, parent_category, parent_date
        )
        questionnaire = create_and_run_questionnaire(questions)

        # Get actual answers from the questionnaire object
        # Assuming questionnaire.get_answers() returns the list of answers
        try:
            answers = questionnaire.get_answers()
        except AttributeError:
            print("Error: Could not get answers from questionnaire")
            return None

        print(f"answers={answers}")

        # Check if we got valid answers
        if not answers or len(answers) < 8:
            return None

        # Validate required fields
        try:
            quantity = float(answers[2]) if answers[2] else None
            description = answers[0] if answers[0] else None
            payed_unit_price = float(answers[3]) if answers[3] else None
            currency = answers[1] if answers[1] else None

            if not all([quantity, description, payed_unit_price, currency]):
                return None

            item = ExchangedItem(
                quantity=quantity,
                description=description,
                the_date=parent_date,
                payed_unit_price=payed_unit_price,
                currency=currency,
                tax_per_unit=float(answers[5]) if answers[5] else 0,
                group_discount=float(answers[6]) if answers[6] else 0,
                category=answers[4] if answers[4] else parent_category,
                round_amount=None,
            )
            return item

        except (ValueError, IndexError, TypeError):
            return None

    while True:
        item = process_single_item()

        if item is None and retry_on_invalid:
            print("Required fields missing or invalid. Please try again.")
            continue

        if item:
            items.append(item)

        # Check if user wants to add another item (last question)
        try:
            questionnaire = create_and_run_questionnaire(
                create_item_questions(item_type, parent_category, parent_date)
            )
            answers = questionnaire.get_answers()
            if answers and len(answers) >= 8 and answers[7].lower() != "y":
                break
        except (AttributeError, IndexError):
            break

    # Handle returned items for bought items
    if item_type.lower() == "bought":
        returned_items = get_items(
            item_type="returned",
            parent_category=parent_category,
            parent_date=parent_date,
            retry_on_invalid=True,
        )
        items.extend(returned_items)

    return items
