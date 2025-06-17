from datetime import datetime
from typing import List, Tuple, Union

import urwid
from hledger_preprocessor.receipt_transaction_matching.get_bank_data_from_transactions import (
    HledgerFlowAccountInfo,
)
from hledger_preprocessor.TransactionObjects.Receipt import (  # For image handling
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
from tui_labeller.tuis.urwid.question_app.generator import create_questionnaire
from tui_labeller.tuis.urwid.question_app.get_answers import (
    get_answers,
    is_terminated,
)
from tui_labeller.tuis.urwid.question_app.reconfiguration.reconfiguration import (
    get_configuration,
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
    account_infos: set[HledgerFlowAccountInfo],
    asset_accounts: set[str],
    labelled_receipts: List[Receipt],
) -> Receipt:

    account_questions = AccountQuestions(
        account_infos=list(
            {x.to_colon_separated_string() for x in account_infos}
        ),
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

    tui.run()  # Start the first run.
    while True:

        if is_terminated(inputs=tui.inputs):
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
            ] = get_answers(inputs=tui.inputs)

            return build_receipt_from_answers(
                final_answers=final_answers,
                verbose=True,
                account_infos=account_infos,
                asset_accounts=asset_accounts,
            )
        else:
            current_position: int = tui.get_focus()
            tui = get_configuration(
                tui=tui,
                account_questions=account_questions,
                optional_questions=optional_questions,
            )

            # Update the pile based on the reconfiguration.
            pile_contents = [(urwid.Text(tui.header), ("pack", None))]
            for some_widget in tui.inputs:
                pile_contents.append((some_widget, ("pack", None)))
            tui.pile.contents = pile_contents

            tui.run(
                alternative_start_pos=current_position + tui.nr_of_headers + 1
            )
