from hledger_preprocessor.receipt_transaction_matching.get_bank_data_from_transactions import (
    HledgerFlowAccountInfo,
)
from hledger_preprocessor.TransactionObjects.Receipt import (  # For image handling
    ExchangedItem,
    Receipt,
)
from typeguard import typechecked

from tui_labeller.tuis.urwid.question_app.generator import create_questionnaire
from tui_labeller.tuis.urwid.QuestionnaireApp import QuestionnaireApp
from tui_labeller.tuis.urwid.receipts.AccountQuestions import AccountQuestions
from tui_labeller.tuis.urwid.receipts.BaseQuestions import (
    BaseQuestions,
)
from tui_labeller.tuis.urwid.receipts.OptionalQuestions import OptionalQuestions


@typechecked
def generate_test_tui(
    *,
    account_info: HledgerFlowAccountInfo,
    asset_accounts: set[str],
) -> QuestionnaireApp:

    account_questions = AccountQuestions(
        account_infos=[account_info.to_colon_separated_string()],
        asset_accounts=asset_accounts,
    )
    base_questions = BaseQuestions()
    optional_questions = OptionalQuestions()

    tui = create_questionnaire(
        questions=base_questions.base_questions
        + account_questions.account_questions
        + optional_questions.optional_questions,
        header="Answer the receipt questions.",
    )

    return tui
