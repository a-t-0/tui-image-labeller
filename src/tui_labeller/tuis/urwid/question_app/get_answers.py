from datetime import datetime
from typing import Dict, List, Type, Union

from typeguard import typechecked
from urwid import AttrMap

from src.tui_labeller.tuis.urwid.mc_question.VerticalMultipleChoiceWidget import (
    VerticalMultipleChoiceWidget,
)
from tui_labeller.tuis.urwid.date_question.DateTimeQuestion import (
    DateTimeQuestion,
)
from tui_labeller.tuis.urwid.input_validation.InputValidationQuestion import (
    InputValidationQuestion,
)


# Manual
@typechecked
def get_answers(
    *,
    inputs: List[Union[VerticalMultipleChoiceWidget, AttrMap]],
) -> Dict[
    Union[
        DateTimeQuestion, InputValidationQuestion, VerticalMultipleChoiceWidget
    ],
    Union[str, float, int, datetime],
]:
    """Collects answers from all questions in the questionnaire.

    Returns:
        Dict[str, Union[str, float, int, datetime]]: A dictionary mapping question captions
            to their answers. Answer types depend on question type:
            - DateTimeQuestion: datetime
            - InputValidationQuestion: str, float, or int
            - VerticalMultipleChoiceWidget: str

    Raises:
        ValueError: If any question's answer cannot be retrieved or validated
    """
    # results: Dict[str, Union[str, float, int, datetime]] = {}
    results: Dict[
        Union[
            DateTimeQuestion,
            InputValidationQuestion,
            VerticalMultipleChoiceWidget,
        ],
        Union[str, float, int, datetime],
    ] = {}

    for i, input_widget in enumerate(inputs):
        widget = input_widget.base_widget
        # try:
        if isinstance(widget, DateTimeQuestion):
            answer = widget.get_answer()
            results[widget] = answer

        elif isinstance(widget, InputValidationQuestion):
            answer = widget.get_answer()
            results[widget] = answer

        elif isinstance(widget, VerticalMultipleChoiceWidget):
            answer = widget.get_answer()
            results[widget] = answer

        else:
            raise ValueError(
                f"Unknown widget type at index {i}: {type(widget)}"
            )
    return results


@typechecked
def get_question_ans_by_text_and_type(
    *,
    inputs: List[Union[VerticalMultipleChoiceWidget, AttrMap]],
    question_text: str,
    question_type: Type[
        Union[
            DateTimeQuestion,
            InputValidationQuestion,
            VerticalMultipleChoiceWidget,
        ]
    ],
) -> str:
    """Retrieve the first question matching the specified text and type from
    the app's questions.

    Args:
        self: The QuestionnaireApp instance (implicit).
        question_text: The exact text (question or caption) to search for.
        question_type: The type of question to match (e.g., VerticalMultipleChoiceWidget).

    Returns:
        PaymentTypes: The first question
            object matching the specified text and type.

    Raises:
        ValueError: If no question with the specified text and type is found.
    """

    for i, input_widget in enumerate(inputs):
        widget = input_widget.base_widget
        if isinstance(widget, VerticalMultipleChoiceWidget):
            if widget.question == question_text:
                answer = widget.get_answer()
                return answer

    # Raise ValueError if no matching question is found
    raise ValueError(
        f"No '{question_text}' question of type"
        f" {question_type.__name__} found in the questionnaire"
    )


@typechecked
def question_has_answer(
    *,
    inputs: List[Union[VerticalMultipleChoiceWidget, AttrMap]],
    question_text: str,
    question_type: Type[
        Union[
            DateTimeQuestion,
            InputValidationQuestion,
            VerticalMultipleChoiceWidget,
        ]
    ],
) -> bool:
    """Checks if a question with the specified text and type has an answer.

    Args:
        question_text: The exact text (question or caption) to search for.
        question_type: The type of question to match (e.g., VerticalMultipleChoiceWidget).

    Returns:
        bool: True if the question has an answer, False otherwise.

    Raises:
        ValueError: If no question with the specified text and type is found.
    """
    for input_widget in inputs:
        widget = input_widget.base_widget
        if isinstance(widget, question_type):
            if (
                isinstance(widget, VerticalMultipleChoiceWidget)
                and widget.question == question_text
            ):
                return widget.has_answer()
            elif hasattr(widget, "caption") and question_text in widget.caption:
                answer = widget.get_answer()
                if isinstance(answer, str):
                    return bool(answer.strip())
                return True
    raise ValueError(
        f"No '{question_text}' question of type"
        f" {question_type.__name__} found in the questionnaire"
    )
