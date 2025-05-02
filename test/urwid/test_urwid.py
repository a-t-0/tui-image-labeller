from datetime import datetime
from typing import List

import pytest
import urwid
from hledger_preprocessor.receipt_transaction_matching.get_bank_data_from_transactions import (
    HledgerFlowAccountInfo,
)
from hledger_preprocessor.TransactionObjects.Receipt import (  # For image handling
    ExchangedItem,
    Receipt,
)

from tui_labeller.tuis.urwid.question_app.generator import create_questionnaire
from tui_labeller.tuis.urwid.QuestionnaireApp import QuestionnaireApp
from tui_labeller.tuis.urwid.receipts.AccountQuestions import AccountQuestions
from tui_labeller.tuis.urwid.receipts.BaseQuestions import (
    BaseQuestions,
)
from tui_labeller.tuis.urwid.receipts.OptionalQuestions import OptionalQuestions


@pytest.fixture
def app():
    app: QuestionnaireApp = generate_test_tui()
    app.loop.screen = urwid.raw_display.Screen()
    return app


def test_avocado_selection(app):
    the_question = app.inputs[0]

    # Step 1: Press "3" and then Enter
    the_question.keypress(1, "3")
    the_question.keypress(1, "enter")

    # Get current date and time with transformed year
    now = datetime.now()
    expected_datetime = now.replace(year=3000 + now.year % 1000)
    expected_formatted = expected_datetime.strftime("%Y-%m-%d %H")

    answer = app.inputs[0].base_widget.get_answer()
    if isinstance(answer, datetime):
        answer_formatted = answer.strftime("%Y-%m-%d %H")
    else:
        answer_parsed = datetime.strptime(str(answer), "%Y-%m-%d %H:%M:%S")
        answer_formatted = answer_parsed.strftime("%Y-%m-%d %H")

    assert (
        answer_formatted == expected_formatted
    ), f"After '3', expected {expected_formatted}, got '{answer_formatted}'"


def generate_test_tui() -> QuestionnaireApp:

    account_info: HledgerFlowAccountInfo = HledgerFlowAccountInfo(
        account_holder="account_placeholder",
        bank="bank_placeholder",
        account_type="account_type_placeholder",
    )

    asset_accounts: List[str] = ["assets:gold", "assets:btc:2342323"]

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
