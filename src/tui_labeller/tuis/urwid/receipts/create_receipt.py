from datetime import datetime
from pprint import pprint
from typing import List, Optional, Tuple, Union

from hledger_preprocessor.receipt_transaction_matching.get_bank_data_from_transactions import (
    HledgerFlowAccountInfo,
)
from hledger_preprocessor.TransactionObjects.Receipt import (  # For image handling
    AccountTransaction,
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
from tui_labeller.tuis.urwid.receipts.account_parser import (
    get_bought_and_returned_items,
)


@typechecked
def build_receipt_from_answers(
    *,
    final_answers: List[
        Tuple[
            Union[
                DateTimeQuestion,
                InputValidationQuestion,
                VerticalMultipleChoiceWidget,
                HorizontalMultipleChoiceWidget,
            ],
            Union[str, float, int, datetime],
        ]
    ],
    verbose: bool,
    account_infos: set[HledgerFlowAccountInfo],
    asset_accounts: set[str],
) -> Receipt:
    """Builds a Receipt object from the dictionary of answers returned by
    tui.get_answers()

    Args:
        final_answers: Dictionary containing question widgets as keys and their answers as values

    Returns:
        Receipt object with mapped values
    """

    # Helper function to extract value from widget key
    @typechecked
    def get_value(*, caption: str, required: Optional[bool] = False) -> any:
        for index, answer in enumerate(final_answers):
            widget, value = answer
            # for widget, value in final_answers.items():
            if hasattr(widget, "caption"):
                if caption in widget.caption:
                    # Convert empty strings to None for optional fields
                    return value if value != "" else None
            elif isinstance(widget, VerticalMultipleChoiceWidget):
                if caption in widget.question.question:
                    return value
            elif isinstance(widget, HorizontalMultipleChoiceWidget):
                if caption in widget.question.question:
                    return value
            else:
                raise TypeError(f"Did not expect question widget type:{widget}")
        if required:
            pprint(final_answers)
            raise ValueError(
                f"Did not find the answer to:{caption}\n in the answers above."
            )
        return None

    @typechecked
    def get_float(*, caption) -> float:
        found_caption: bool = False
        for index, answer in enumerate(final_answers):
            widget, value = answer
            if hasattr(widget, "caption") and caption in widget.caption:
                found_caption = True
                # Convert empty strings to None for optional fields
                return float(value) if value != "" else 0.0
        if not found_caption:
            print("\n")
            pprint(final_answers)
            raise ValueError(
                f"Did not find caption:{caption} in above answers."
            )
        return 0.0

    average_receipt_category: str = get_value(
        caption="\nBookkeeping expense category:", required=True
    )
    the_date: datetime = get_value(
        caption="Receipt date and time:\n", required=True
    )
    net_bought_items: Union[None, ExchangedItem]
    net_returned_items: Union[None, ExchangedItem]
    net_bought_items, net_returned_items = get_bought_and_returned_items(
        final_answers=final_answers,
        account_infos=account_infos,
        asset_accounts=asset_accounts,
        average_receipt_category=average_receipt_category,
        the_date=the_date,
    )

    # Map the answers to Receipt parameters
    receipt_params = {
        "shop_name": (
            get_value(caption="\nShop name:\n") or ""
        ),  # Required, default to empty string
        "net_bought_items": net_bought_items,
        "net_returned_items": net_returned_items,
        "the_date": the_date,
        "shop_address": get_value(caption="\nShop address:\n"),
        "shop_account_nr": get_value(caption="\nShop account nr:\n"),
        "subtotal": (
            float(
                get_value(
                    caption="\nSubtotal (Optional, press enter to skip):\n"
                )
            )
            if get_value(
                caption="\nSubtotal (Optional, press enter to skip):\n"
            )
            else None
        ),
        "total_tax": (
            float(
                get_value(
                    caption="\nTotal tax (Optional, press enter to skip):\n"
                )
            )
            if get_value(
                caption="\nTotal tax (Optional, press enter to skip):\n"
            )
            else None
        ),
        # TODO: store amount payed and returned per account.
        "receipt_owner_address": get_value(
            caption="\nReceipt owner address (optional):\n"
        ),
        "receipt_categorisation": average_receipt_category,
    }

    if verbose:
        pprint(receipt_params)
        print("OK?")
    return Receipt(**receipt_params)
