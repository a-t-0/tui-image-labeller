from datetime import datetime
from typing import List, Tuple, Union

from hledger_preprocessor.Currency import Currency
from hledger_preprocessor.receipt_transaction_matching.get_bank_data_from_transactions import (
    HledgerFlowAccountInfo,
)
from hledger_preprocessor.TransactionObjects.Receipt import (  # For image handling
    Account,
    AccountTransaction,
    AccountType,
    ExchangedItem,
    Receipt,
)
from typeguard import typechecked
from typing_extensions import TypeGuard

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


@typechecked
def is_asset_account(*, s: str) -> TypeGuard[str]:
    """Check if string matches asset account format (e.g., 'assets:gold' or
    'assets:BTC:address')."""
    parts = s.split(":")
    return len(parts) >= 2 and parts[0].lower() == "assets"


@typechecked
def parse_account_string(
    *,
    input_string: str,
    account_infos: List[HledgerFlowAccountInfo],
    asset_accounts: List[str],
) -> Account:
    """Parse input string and match to exactly one bank or asset account.

    Returns an Account object or raises ValueError for no matches or
    multiple matches.
    """
    matches: List[Account] = []

    # Check bank accounts (HledgerFlowAccountInfo)
    for account_info in account_infos:
        bank_str = account_info.to_colon_separated_string()
        if input_string == bank_str:
            matches.append(
                Account(
                    account_type=AccountType.BANK,
                    account_holder=account_info.account_holder,
                    bank=account_info.bank,
                    bank_account_type=account_info.account_type,
                )
            )

    # Check asset accounts
    if is_asset_account(s=input_string):
        for asset in asset_accounts:
            print(f"left={input_string.lower()}, right={asset.lower()}")
            if input_string.lower() == asset.lower():
                matches.append(
                    Account(
                        account_type=AccountType.ASSET,
                        asset_category=input_string,
                    )
                )

    # Handle match results
    if not matches:
        raise ValueError(f"No account found matching: {input_string}")
    if len(matches) > 1:
        raise ValueError(f"Multiple accounts found matching: {input_string}")
    return matches[0]


@typechecked
def get_accounts_from_answers(
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
    account_infos: List[HledgerFlowAccountInfo],
    asset_accounts: List[str],
) -> List[AccountTransaction]:
    account_transactions: List[AccountTransaction] = []
    i = 0
    while i < len(final_answers):

        widget, _ = final_answers[i]
        caption = (
            widget.question.question
            if isinstance(widget, HorizontalMultipleChoiceWidget)
            else widget.caption
        )
        print(f"caption={caption}")
        first_account_question_id: str = "Belongs to bank/asset_accounts:"
        if (
            caption[: len(first_account_question_id)]
            == first_account_question_id
        ):
            if not isinstance(widget, VerticalMultipleChoiceWidget):
                raise ValueError(
                    f"Expected VerticalMultipleChoiceWidget at index {i}"
                )
            if i + 4 >= len(final_answers):
                raise ValueError("Incomplete account transaction questions")

            # Account
            account_str = str(final_answers[i][1])
            print(f"account_str={account_str}END")
            print(f"asset_accounts={asset_accounts}END")
            account = parse_account_string(
                input_string=account_str,
                account_infos=account_infos,
                asset_accounts=asset_accounts,
            )

            # Currency
            currency_widget, currency_answer = final_answers[i + 1]
            # currency_caption = currency_widget.question.question if isinstance(currency_widget, HorizontalMultipleChoiceWidget) else currency_widget.caption
            if not isinstance(currency_widget, VerticalMultipleChoiceWidget):
                raise ValueError(
                    f"Expected VerticalMultipleChoiceWidget at index {i + 1}"
                )
            currency = Currency(currency_answer)

            # Amount paid
            amount_widget, amount_answer = final_answers[i + 2]
            amount_caption = (
                amount_widget.question.question
                if isinstance(amount_widget, HorizontalMultipleChoiceWidget)
                else amount_widget.caption
            )
            if not isinstance(amount_widget, InputValidationQuestion):
                raise ValueError(
                    f"Expected InputValidationQuestion at index {i + 2}"
                )
            amount_paid = float(amount_answer)

            # Change returned
            change_widget, change_answer = final_answers[i + 3]
            change_caption = (
                change_widget.question.question
                if isinstance(change_widget, HorizontalMultipleChoiceWidget)
                else change_widget.caption
            )
            if not isinstance(change_widget, InputValidationQuestion):
                raise ValueError(
                    f"Expected InputValidationQuestion at index {i + 3}"
                )
            change_returned = float(change_answer)

            account_transactions.append(
                AccountTransaction(
                    account=account,
                    currency=currency,
                    amount_paid=amount_paid,
                    change_returned=change_returned,
                )
            )

            # Check for additional account
            if i + 4 < len(final_answers):
                add_widget, add_answer = final_answers[i + 4]
                add_caption = (
                    add_widget.question.question
                    if isinstance(add_widget, HorizontalMultipleChoiceWidget)
                    else add_widget.caption
                )
                if add_caption == "Add another account (y/n)?:":
                    if not isinstance(
                        add_widget, HorizontalMultipleChoiceWidget
                    ):
                        raise ValueError(
                            "Expected HorizontalMultipleChoiceWidget at index"
                            f" {i + 4}"
                        )
                    if str(add_answer).lower() == "y":
                        i += 5
                        continue
                    else:
                        break
            break
        else:
            i += 1
    return account_transactions


@typechecked
def has_purchase_account_transactions(
    *, account_transactions: List[AccountTransaction]
) -> bool:
    for account_transaction in account_transactions:
        if account_transaction.is_purchase():
            return True
    return False


@typechecked
def separate_account_transactions(
    *, account_transactions: List[AccountTransaction]
) -> Tuple[List[AccountTransaction], List[AccountTransaction]]:
    purchase_account_transactions: List[AccountTransaction] = []
    non_purchase_account_transactions: List[AccountTransaction] = []
    for account_transaction in account_transactions:
        if account_transaction.is_purchase():
            purchase_account_transactions.append(account_transaction)
        else:
            non_purchase_account_transactions.append(account_transaction)
    return non_purchase_account_transactions, purchase_account_transactions
