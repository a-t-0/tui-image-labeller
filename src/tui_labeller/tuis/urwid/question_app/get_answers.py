from datetime import datetime
from typing import Dict, List, Union

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
from tui_labeller.tuis.urwid.mc_question.HorizontalMultipleChoiceWidget import (
    HorizontalMultipleChoiceWidget,
)


# Manual
@typechecked
def get_answers(
    *,
    inputs: List[
        Union[
            VerticalMultipleChoiceWidget,
            HorizontalMultipleChoiceWidget,
            AttrMap,
        ]
    ],
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
            HorizontalMultipleChoiceWidget,
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

        elif isinstance(widget, HorizontalMultipleChoiceWidget):
            answer = widget.get_answer()
            results[widget] = answer

        else:
            raise ValueError(
                f"Unknown widget type at index {i}: {type(widget)}"
            )
    return results
