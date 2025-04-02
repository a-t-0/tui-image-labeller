from datetime import datetime

from hledger_preprocessor.TransactionObjects.Receipt import (  # For image handling
    ExchangedItem,
    Receipt,
)
from typeguard import typechecked


@typechecked
def build_receipt_from_answers(*, final_answers: dict) -> Receipt:
    """Builds a Receipt object from the dictionary of answers returned by
    tui.get_answers()

    Args:
        final_answers: Dictionary containing question widgets as keys and their answers as values

    Returns:
        Receipt object with mapped values
    """

    # Helper function to extract value from widget key
    def get_value(caption: str) -> any:
        for widget, value in final_answers.items():
            if hasattr(widget, "caption") and caption in widget.caption:
                # Convert empty strings to None for optional fields
                return value if value != "" else None
        return None

    @typechecked
    def get_float(*, caption) -> float:
        for widget, value in final_answers.items():
            if hasattr(widget, "caption") and caption in widget.caption:
                # Convert empty strings to None for optional fields
                return float(value) if value != "" else 0
        return 0

    # Since bought_items and returned_items aren't in the provided questions,
    # we'll initialize them as empty lists
    bought_items = []
    returned_items = []

    cash_payed: float = get_float(caption="\nAmount paid in cash:\n")
    cash_returned: float = get_float(caption="\nChange returned (cash):\n")
    card_payed: float = get_float(caption="\nAmount paid by card:\n")
    card_returned: float = get_float(
        caption="\nChange returned (card):\n",
    )
    # Map the answers to Receipt parameters
    receipt_params = {
        "currency": (
            get_value("Currency:\n") or ""
        ),  # Required, default to empty string
        "shop_name": (
            get_value("\nShop name:\n") or ""
        ),  # Required, default to empty string
        "receipt_owner_account_holder": (
            get_value("\nAccount holder name:\n") or ""
        ),  # Required
        "receipt_owner_bank": (
            get_value("\nBank name (e.g., triodos, bitfavo):\n") or ""
        ),  # Required
        "receipt_owner_account_holder_type": (
            get_value("\nAccount type (e.g., checking, credit):\n") or ""
        ),  # Required
        "bought_items": bought_items,
        "returned_items": returned_items,
        "the_date": (
            get_value("Receipt date and time:\n") or datetime.now()
        ),  # Use current time if missing
        "payed_total_read": (
            cash_payed - cash_returned + card_payed - card_returned
        ),
        "shop_address": get_value("\nShop address:\n"),
        "shop_account_nr": get_value("\nShop account nr:\n"),
        "subtotal": (
            float(get_value("\nSubtotal (Optional, press enter to skip):\n"))
            if get_value("\nSubtotal (Optional, press enter to skip):\n")
            else None
        ),
        "total_tax": (
            float(get_value("\nTotal tax (Optional, press enter to skip):\n"))
            if get_value("\nTotal tax (Optional, press enter to skip):\n")
            else None
        ),
        "cash_payed": cash_payed,
        "cash_returned": cash_returned,
        "card_payed": card_payed,
        "card_returned": card_returned,
        "receipt_owner_address": get_value(
            "\nReceipt owner address (optional):\n"
        ),
        "receipt_categorisation": (
            {"category": get_value("\nBookkeeping category:\n")}
            if get_value("\nBookkeeping category:\n")
            else None
        ),
    }

    card_returned = get_value("\nChange returned (card):\n")
    if card_returned is not None and receipt_params["cash_returned"] is None:
        receipt_params["cash_returned"] = float(card_returned)

    if bought_items == [] and returned_items == []:
        filler_bought_item: ExchangedItem = ExchangedItem(
            quantity=1,
            description=receipt_params["receipt_categorisation"],
            the_date=receipt_params["the_date"],
            payed_unit_price=float(receipt_params.get("cash_payed", 0) or 0)
            + float(receipt_params.get("card_payed", 0) or 0),
            currency=receipt_params["currency"],
            tax_per_unit=0,
            group_discount=0,
            category=None,
            round_amount=None,
        )
        receipt_params["bought_items"] = [filler_bought_item]

        filler_returned_item: ExchangedItem = ExchangedItem(
            quantity=1,
            description=receipt_params["receipt_categorisation"],
            the_date=receipt_params["the_date"],
            payed_unit_price=float(receipt_params.get("cash_returned", 0) or 0)
            + float(receipt_params.get("card_returned", 0) or 0),
            currency=receipt_params["currency"],
            tax_per_unit=0,
            group_discount=0,
            category=None,
            round_amount=None,
        )
        receipt_params["returned_items"] = [filler_returned_item]
    return Receipt(**receipt_params)
