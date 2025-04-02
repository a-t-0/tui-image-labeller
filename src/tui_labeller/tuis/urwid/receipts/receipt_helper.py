from typing import Any, List, Union

from hledger_preprocessor.TransactionObjects.Receipt import (  # For image handling
    ExchangedItem,
    Receipt,
)
from typeguard import typechecked

from tui_labeller.tuis.urwid.appending_questions import append_questions_to_list
from tui_labeller.tuis.urwid.merged_questions import (
    QuestionnaireApp,
)
from tui_labeller.tuis.urwid.move_optionals_to_end import move_questions_to_end
from tui_labeller.tuis.urwid.question_data_classes import (
    AISuggestion,
    HistorySuggestion,
    InputValidationQuestionData,
)
from tui_labeller.tuis.urwid.receipts.payments_enum import PaymentTypes
from tui_labeller.tuis.urwid.removing_questions import (
    remove_specific_questions_from_list,
)


@typechecked
def get_matching_unique_suggestions(
    suggestions: List[Union[AISuggestion, HistorySuggestion]],
    current_text: str,
    cursor_pos: int,
) -> List[str]:
    # Get the portion of text up to cursor position
    text_to_match = current_text[: cursor_pos + 1]

    # Filter suggestions that match up to the cursor position
    matching_suggestions = [
        suggestion.question
        for suggestion in suggestions
        if suggestion.question.startswith(text_to_match)
    ]
    # Preserve order, remove dupes.
    return list(dict.fromkeys(matching_suggestions))


@typechecked
def has_questions(
    *,
    expected_questions: List[InputValidationQuestionData],
    actual_questions: List[Any],
) -> bool:
    """Determine if questions of a specific payment type are present."""

    nr_of_matching_questions: int = nr_of_questions(
        expected_questions=expected_questions, actual_questions=actual_questions
    )

    if nr_of_matching_questions > 0:
        if nr_of_matching_questions != len(expected_questions):
            raise ValueError(
                "Either all or none of the questions must be present. Found"
                f" {nr_of_matching_questions} out of"
                f" {len(expected_questions)} questions."
            )
        return True
    return False


@typechecked
def nr_of_questions(
    expected_questions: List[InputValidationQuestionData],
    actual_questions: List[Any],
) -> int:
    """Count the number of questions of a specific payment type."""
    question_strings = [q.question for q in expected_questions]
    question_count = 0

    for tui_question in actual_questions:
        tui_text = getattr(
            tui_question, "question", getattr(tui_question, "caption", None)
        )
        if tui_text in question_strings:
            question_count += 1

    return question_count


@typechecked
def update_questionnaire(
    *,
    app: QuestionnaireApp,
    new_transaction_type: PaymentTypes,
    cash_questions: List[Any],
    card_questions: List[Any],
    has_cash_questions: bool,
    has_card_questions: bool,
    optional_questions: List[Any],
) -> None:
    """Update the questionnaire based on the transaction type."""

    # First handle removal of cash questions if switching away from cash
    if new_transaction_type not in [PaymentTypes.CASH, PaymentTypes.BOTH]:
        if has_cash_questions:
            remove_specific_questions_from_list(
                app=app, expected_questions=cash_questions
            )
            assert (
                nr_of_questions(
                    expected_questions=cash_questions,
                    actual_questions=app.questions,
                )
                == 0
            ), (
                "Expected 0 cash questions remaining, but found"
                f" {nr_of_questions(expected_questions=cash_questions, actual_questions=app.questions)}"
            )

    # Then handle removal of card questions if switching away from card
    if new_transaction_type not in [PaymentTypes.CARD, PaymentTypes.BOTH]:
        if has_card_questions:
            remove_specific_questions_from_list(
                app=app, expected_questions=card_questions
            )
            assert (
                nr_of_questions(
                    expected_questions=card_questions,
                    actual_questions=app.questions,
                )
                == 0
            ), (
                "Expected 0 card questions remaining, but found"
                f" {nr_of_questions(expected_questions=card_questions, actual_questions=app.questions)}"
            )

    # Now handle adding cash questions if needed
    if new_transaction_type in [PaymentTypes.CASH, PaymentTypes.BOTH]:
        if not has_cash_questions:
            append_questions_to_list(app=app, new_questions=cash_questions)
            assert nr_of_questions(
                expected_questions=cash_questions,
                actual_questions=app.questions,
            ) == len(cash_questions), (
                f"Expected {len(cash_questions)} cash questions, but found"
                f" {nr_of_questions(expected_questions=cash_questions, actual_questions=app.questions)}"
            )

    # Finally handle adding card questions if needed
    if new_transaction_type in [PaymentTypes.CARD, PaymentTypes.BOTH]:
        if not has_card_questions:
            append_questions_to_list(app=app, new_questions=card_questions)
            assert nr_of_questions(
                expected_questions=card_questions,
                actual_questions=app.questions,
            ) == len(card_questions), (
                f"Expected {len(card_questions)} card questions, but found"
                f" {nr_of_questions(expected_questions=card_questions, actual_questions=app.questions)}"
            )

    move_questions_to_end(app=app, questions_to_move=optional_questions)

    if new_transaction_type == PaymentTypes.OTHER.value:
        raise NotImplementedError("Other transaction types not implemented")
