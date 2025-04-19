from datetime import datetime
from pprint import pprint
from typing import Dict, List, Union

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
from tui_labeller.tuis.urwid.mc_question.MultipleChoiceWidget import (
    MultipleChoiceWidget,
)
from tui_labeller.tuis.urwid.merged_questions import (
    QuestionnaireApp,
    create_questionnaire,
)
from tui_labeller.tuis.urwid.receipts.AccountQuestions import AccountQuestions
from tui_labeller.tuis.urwid.receipts.BaseQuestions import (
    BaseQuestions,
)
from tui_labeller.tuis.urwid.receipts.create_receipt import (
    build_receipt_from_answers,
)
from tui_labeller.tuis.urwid.receipts.ItemQuestionnaire import (
    ItemQuestionnaire,
    get_exchanged_item,
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
    account_questions = AccountQuestions(
        account_infos=list(
            {x.to_colon_separated_string() for x in account_infos}
        ),
        categories=categories,
    )

    # Step 1: Run base questionnaire
    base_questions = BaseQuestions()
    OptionalQuestions()
    tui: QuestionnaireApp = create_questionnaire(
        questions=base_questions.base_questions,
        header="",
    )

    tui.run()
    print("before")

    # update_questions_based_on_transaction_type(
    #     app=tui,
    #     current_transaction_type=new_transaction_type,  # TODO: improve logic.
    #     optional_questions=optional_questions,
    #     base_questions=base_questions,
    #     nr_of_base_questions=len(base_questions.base_questions),
    #     receipt_owner_account_holder=receipt_owner_account_holder,
    #     receipt_owner_bank=receipt_owner_bank,
    #     receipt_owner_account_holder_type=receipt_owner_account_holder_type,
    #     is_first_run=True,
    # )

    # Step 4: Build and return the receipt with final answers
    final_answers = tui.get_answers()
    pprint(final_answers)

    return build_receipt_from_answers(final_answers=final_answers)


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
    questionnaire_tui: QuestionnaireApp = create_questionnaire(
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
