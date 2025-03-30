from datetime import datetime
from typing import Dict, Optional, Union

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

# Depending on the choice above, ask the total cash, pin, both or raise error.

    # Optional.
    receipt_owner_address = input("Receipt owner address (optional): ") or None

    # Optional.
    shop_name: str = input(
        "Shop name: "
    )  # TODO: assert it does not have spaces, newlines or tabs.
    shop_address = input("Shop address: ")


    # Optional.
    subtotal = get_float_input(
        question="Subtotal (Optional, press enter to skip): ",
        allow_optional=True,
    )
    # Optional.
    total_tax = get_float_input(
        question="Total tax (Optional, press enter to skip): ",
        allow_optional=True,
    )



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

    payed_total_read: float = get_float_input(
        question="Payed total:", allow_optional=False
    )

    ]

    receipt_categorisation: str = "swag:something"
    bought_items = process_single_item(
        item_type="bought",
        parent_category=receipt_categorisation,
        parent_date=datetime.now(),
    )
    # TODO: check if you want to add another item.
    returned_items = process_single_item(
        item_type="returned",
        parent_category=receipt_categorisation,
        parent_date=datetime.now(),
    )
