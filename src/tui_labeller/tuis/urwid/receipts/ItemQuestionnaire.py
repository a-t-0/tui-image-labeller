from datetime import datetime
from typing import Dict, Union

from hledger_preprocessor.TransactionObjects.Receipt import (  # For image handling
    ExchangedItem,
    Receipt,
)
from typeguard import typechecked

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
from tui_labeller.tuis.urwid.question_data_classes import (
    AISuggestion,
    InputValidationQuestionData,
    MultipleChoiceQuestionData,
)


class ItemQuestionnaire:
    def __init__(
        self, item_type: str, parent_category: str, parent_date: datetime
    ):
        self.item_type = item_type
        self.parent_category = parent_category
        self.parent_date = parent_date
        self.questions = self.create_item_questions(
            item_type=item_type,
            parent_category=parent_category,
            parent_date=parent_date,
        )
        self.verify_unique_questions()

    def create_item_questions(
        self, item_type: str, parent_category: str, parent_date: datetime
    ):
        return [
            InputValidationQuestionData(
                caption=f"Name/description (a-Z only): ",
                input_type=InputType.LETTERS,
                ans_required=True,
                ai_suggestions=[
                    AISuggestion("widget", 0.9, "ItemPredictor"),
                    AISuggestion("gadget", 0.85, "ItemPredictor"),
                ],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                caption="Currency (e.g. EUR,BTC,$,YEN): ",
                input_type=InputType.LETTERS,
                ans_required=False,
                ai_suggestions=[
                    AISuggestion("USD", 0.90, "CurrencyNet"),
                    AISuggestion("EUR", 0.95, "CurrencyNet"),
                    AISuggestion("BTC", 0.85, "CurrencyNet"),
                ],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                caption=f"Amount: ",
                input_type=InputType.FLOAT,
                ans_required=True,
                ai_suggestions=[
                    AISuggestion("1", 0.9, "QuantityAI"),
                    AISuggestion("2", 0.85, "QuantityAI"),
                    AISuggestion("1.83", 0.85, "QuantityAI"),
                ],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                caption=f"Price for selected amount:",
                input_type=InputType.FLOAT,
                ans_required=True,
                ai_suggestions=[
                    AISuggestion("9.99", 0.9, "PricePredictor"),
                    AISuggestion("19.99", 0.85, "PricePredictor"),
                ],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                caption=f"Category (empty is: {parent_category}): ",
                input_type=InputType.LETTERS,
                ans_required=True,
                ai_suggestions=[
                    AISuggestion("general", 0.8, "CategoryAI"),
                ],
                history_suggestions=[
                    AISuggestion(parent_category, 0.95, "CategoryAI"),
                ],
            ),
            InputValidationQuestionData(
                caption="Tax for selected items (Optional):",
                input_type=InputType.FLOAT,
                ans_required=False,
                ai_suggestions=[
                    AISuggestion("0", 0.9, "TaxAI"),
                    AISuggestion("1.99", 0.7, "TaxAI"),
                ],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                caption="Discount for selected items (Optional):",
                input_type=InputType.FLOAT,
                ans_required=False,
                ai_suggestions=[
                    AISuggestion("0", 0.9, "DiscountAI"),
                    AISuggestion("5.00", 0.7, "DiscountAI"),
                ],
                history_suggestions=[],
            ),
            MultipleChoiceQuestionData(
                question=f"Add another {item_type} item? (y/n): ",
                choices=["yes", "no"],
                ai_suggestions=[],
                terminator=True,
            ),
        ]

    def verify_unique_questions(self) -> None:
        """Verifies all question captions/questions are unique, raises error if
        not."""
        seen = set()
        for q in self.questions:
            # Use caption for InputValidationQuestionData, question for MultipleChoiceQuestionData
            caption = getattr(q, "caption", getattr(q, "question", None))
            if caption is None:
                raise ValueError(
                    "Question object missing caption or question attribute"
                )
            if caption in seen:
                raise ValueError(
                    f"Duplicate question caption found: '{caption}'"
                )
            seen.add(caption)


@typechecked
def get_exchanged_item(
    *,
    answers: Dict[
        Union[DateTimeQuestion, InputValidationQuestion, MultipleChoiceWidget],
        Union[str, float, int, datetime],
    ],
) -> ExchangedItem:
    """Constructs an ExchangedItem from questionnaire answers.

    Args:
        answers: Dictionary of answers from the questionnaire

    Returns:
        ExchangedItem: Constructed item based on the answers
    """
    # Find questions by caption and extract answers
    description_q = next(
        q
        for q in answers.keys()
        if q.caption == "Name/description (a-Z only): "
    )
    currency_q = next(
        q
        for q in answers.keys()
        if q.caption == "Currency (e.g. EUR,BTC,$,YEN): "
    )
    amount_q = next(q for q in answers.keys() if q.caption == "Amount: ")
    price_q = next(
        q for q in answers.keys() if q.caption == "Price for selected amount:"
    )
    category_q = next(
        q for q in answers.keys() if "Category (empty is:" in q.caption
    )
    tax_q = next(
        q
        for q in answers.keys()
        if q.caption == "Tax for selected items (Optional):"
    )
    discount_q = next(
        q
        for q in answers.keys()
        if q.caption == "Discount for selected items (Optional):"
    )

    description = answers[description_q]
    currency = answers[currency_q] if answers[currency_q] else None
    quantity = float(answers[amount_q])
    payed_unit_price = float(answers[price_q])
    category = (
        answers[category_q]
        if answers[category_q]
        else category_q.caption.split("empty is: ")[1].rstrip("): ")
    )
    tax_per_unit = float(answers[tax_q]) if answers[tax_q] else 0
    group_discount = float(answers[discount_q]) if answers[discount_q] else 0

    return ExchangedItem(
        quantity=quantity,
        description=description,
        the_date=(
            answers[description_q].parent_date
            if hasattr(answers[description_q], "parent_date")
            else datetime.now()
        ),
        payed_unit_price=payed_unit_price,
        currency=currency,
        tax_per_unit=tax_per_unit,
        group_discount=group_discount,
        category=category,
        round_amount=None,
    )
