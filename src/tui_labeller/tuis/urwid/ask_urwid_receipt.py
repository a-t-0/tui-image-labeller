from datetime import datetime
from pprint import pprint
from typing import Dict, Union

from hledger_preprocessor.TransactionObjects.Receipt import (  # For image handling
    ExchangedItem,
    Receipt,
)
from typeguard import typechecked

from tui_labeller.tuis.urwid.appending_questions import append_questions_to_list
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
    create_and_run_questionnaire,
)
from tui_labeller.tuis.urwid.receipts.BaseQuestions import (
    BaseQuestions,
)
from tui_labeller.tuis.urwid.receipts.CardPaymentQuestions import (
    CardPaymentQuestions,
)
from tui_labeller.tuis.urwid.receipts.CashPaymentQuestions import (
    CashPaymentQuestions,
)
from tui_labeller.tuis.urwid.receipts.create_receipt import (
    build_receipt_from_answers,
)
from tui_labeller.tuis.urwid.receipts.ItemQuestionnaire import (
    ItemQuestionnaire,
    get_exchanged_item,
)
from tui_labeller.tuis.urwid.receipts.OptionalQuestions import OptionalQuestions
from tui_labeller.tuis.urwid.receipts.payments_enum import PaymentTypes
from tui_labeller.tuis.urwid.receipts.receipt_helper import (
    has_questions,
    update_questionnaire,
)


@typechecked
def build_receipt_from_urwid(
    *,
    receipt_owner_account_holder: str,
    receipt_owner_bank: str,
    receipt_owner_account_holder_type: str,
) -> Receipt:
    # Step 1: Run base questionnaire
    base_questions = BaseQuestions()
    optional_questions = OptionalQuestions()
    tui: QuestionnaireApp = create_and_run_questionnaire(
        questions=base_questions.base_questions,
        header="",
    )

    new_transaction_type: PaymentTypes = tui.get_question_by_text_and_type(
        question_text="Transaction type",
        question_type=MultipleChoiceWidget,
    )

    update_questions_based_on_transaction_type(
        app=tui,
        current_transaction_type=new_transaction_type,  # TODO: improve logic.
        optional_questions=optional_questions,
        nr_of_base_questions=len(base_questions.base_questions),
        receipt_owner_account_holder=receipt_owner_account_holder,
        receipt_owner_bank=receipt_owner_bank,
        receipt_owner_account_holder_type=receipt_owner_account_holder_type,
        is_first_run=True,
    )

    # Step 4: Build and return the receipt with final answers
    final_answers = tui.get_answers()
    pprint(final_answers)

    return build_receipt_from_answers(final_answers=final_answers)
    # Assuming Receipt class takes these parameters and answers
    # return Receipt(
    #     **final_answers
    #     # receipt_owner_account_holder=receipt_owner_account_holder,
    #     # receipt_owner_bank=receipt_owner_bank,
    #     # receipt_owner_account_holder_type=receipt_owner_account_holder_type,
    #     # answers=final_answers,
    # )


@typechecked
def update_questions_based_on_transaction_type(
    *,
    app: QuestionnaireApp,
    current_transaction_type: PaymentTypes,
    optional_questions: OptionalQuestions,
    nr_of_base_questions: int,
    receipt_owner_account_holder: str,
    receipt_owner_bank: str,
    receipt_owner_account_holder_type: str,
    is_first_run: bool,
) -> PaymentTypes:
    """Main function to update questions based on transaction type."""

    new_transaction_type: PaymentTypes = app.get_question_by_text_and_type(
        question_text="Transaction type",
        question_type=MultipleChoiceWidget,
    )

    if new_transaction_type == current_transaction_type and not is_first_run:
        return new_transaction_type

    cash_questions = CashPaymentQuestions().questions
    card_questions = CardPaymentQuestions(
        receipt_owner_account_holder=receipt_owner_account_holder,
        receipt_owner_bank=receipt_owner_bank,
        receipt_owner_account_holder_type=receipt_owner_account_holder_type,
    ).questions
    actual_questions = app.questions

    has_cash_questions = has_questions(
        expected_questions=cash_questions, actual_questions=actual_questions
    )
    has_card_questions = has_questions(
        expected_questions=card_questions, actual_questions=actual_questions
    )

    update_questionnaire(
        app=app,
        new_transaction_type=new_transaction_type,
        cash_questions=cash_questions,
        card_questions=card_questions,
        has_cash_questions=has_cash_questions,
        has_card_questions=has_card_questions,
        optional_questions=optional_questions.optional_questions,
    )
    if not has_questions(
        expected_questions=optional_questions.optional_questions,
        actual_questions=actual_questions,
    ):
        append_questions_to_list(
            app=app, new_questions=optional_questions.optional_questions
        )

    if not is_first_run:
        app.run(
            alternative_start_pos=nr_of_base_questions + 1
        )  # TODO: parameterise header.
    else:
        app.run()

    final_transaction_type: PaymentTypes = (
        update_questions_based_on_transaction_type(
            app=app,
            current_transaction_type=new_transaction_type,
            optional_questions=optional_questions,
            nr_of_base_questions=nr_of_base_questions,
            receipt_owner_account_holder=receipt_owner_account_holder,
            receipt_owner_bank=receipt_owner_bank,
            receipt_owner_account_holder_type=receipt_owner_account_holder_type,
            is_first_run=False,
        )
    )
    return final_transaction_type


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
    questionnaire_tui: QuestionnaireApp = create_and_run_questionnaire(
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
