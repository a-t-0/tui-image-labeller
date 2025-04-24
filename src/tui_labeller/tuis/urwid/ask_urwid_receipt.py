from typing import List

from hledger_preprocessor.receipt_transaction_matching.get_bank_data_from_transactions import (
    HledgerFlowAccountInfo,
)
from hledger_preprocessor.TransactionObjects.Receipt import (  # For image handling
    ExchangedItem,
    Receipt,
)
from typeguard import typechecked

from tui_labeller.tuis.urwid.question_app.generator import create_questionnaire
from tui_labeller.tuis.urwid.question_app.get_answers import (
    get_answers,
    is_terminated,
)
from tui_labeller.tuis.urwid.question_app.reconfiguration import (
    get_configuration,
)
from tui_labeller.tuis.urwid.QuestionnaireApp import (
    QuestionnaireApp,
)
from tui_labeller.tuis.urwid.receipts.AccountQuestions import AccountQuestions
from tui_labeller.tuis.urwid.receipts.BaseQuestions import (
    BaseQuestions,
)
from tui_labeller.tuis.urwid.receipts.create_receipt import (
    build_receipt_from_answers,
)
from tui_labeller.tuis.urwid.receipts.OptionalQuestions import OptionalQuestions


@typechecked
def build_receipt_from_urwid(
    *,
    receipt_owner_account_holder: str,
    receipt_owner_bank: str,
    receipt_owner_account_holder_type: str,
    account_infos: List[HledgerFlowAccountInfo],
    categories: List[str],
) -> Receipt:
    choices = categories + [
        "a",
        "b",
        "a",
        "b",
        "a",
        "b",
        "a",
        "b",
        "a",
        "b",
    ]
    account_questions: AccountQuestions = AccountQuestions(
        account_infos=list(
            {x.to_colon_separated_string() for x in account_infos}
        ),
        categories=choices,
    )
    base_questions: BaseQuestions = BaseQuestions()
    optional_questions: OptionalQuestions = OptionalQuestions()

    # Initialize questionnaire with all questions
    tui: QuestionnaireApp = create_questionnaire(
        questions=base_questions.base_questions
        + account_questions.account_questions
        + optional_questions.optional_questions,
        header="Answer the receipt questions.",
    )

    while True:
        tui.run()
        if is_terminated(inputs=tui.inputs):
            input("FOUND TERMINATOR")
            final_answers = get_answers(inputs=tui.inputs)
            # Build and return the receipt with final answers
            return build_receipt_from_answers(final_answers=final_answers)

        else:
            # Must be reconfiguration.
            some_tui = get_configuration(
                tui=tui,
                account_questions=account_questions,
                optional_questions=optional_questions,
            )
            input("REconfiguration.")
            some_tui.run()
            input("WAS ANOTHER ACCOUNT ADDED?.")
