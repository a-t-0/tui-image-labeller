from typing import List, Union

import urwid
from typeguard import typechecked
from urwid import AttrMap, Pile

from src.tui_labeller.tuis.urwid.mc_question.VerticalMultipleChoiceWidget import (
    VerticalMultipleChoiceWidget,
)
from tui_labeller.tuis.urwid.mc_question.HorizontalMultipleChoiceWidget import (
    HorizontalMultipleChoiceWidget,
)
from tui_labeller.tuis.urwid.question_app.create_widgets import (
    create_question_widget,
)
from tui_labeller.tuis.urwid.question_data_classes import (
    DateQuestionData,
    HorizontalMultipleChoiceQuestionData,
    InputValidationQuestionData,
    VerticalMultipleChoiceQuestionData,
)


# Manual
@typechecked
def build_questionnaire(
    *,
    header: str,
    inputs: List[
        Union[
            VerticalMultipleChoiceWidget,
            HorizontalMultipleChoiceWidget,
            AttrMap,
        ]
    ],
    questions: List[
        Union[
            DateQuestionData,
            InputValidationQuestionData,
            VerticalMultipleChoiceQuestionData,
            HorizontalMultipleChoiceQuestionData,
        ]
    ],
    descriptor_col_width: int,
    pile: Pile,
    ai_suggestion_box: AttrMap,
    history_suggestion_box: AttrMap,
    error_display: AttrMap,
) -> None:
    # Manual
    """Build the complete questionnaire UI."""
    pile_contents = [(urwid.Text(header), ("pack", None))]

    for i, question_data in enumerate(questions):
        widget: Union[
            VerticalMultipleChoiceWidget,
            HorizontalMultipleChoiceWidget,
            AttrMap,
        ] = create_question_widget(
            pile=pile,
            ai_suggestion_box=ai_suggestion_box,
            history_suggestion_box=history_suggestion_box,
            error_display=error_display,
            question_data=question_data,
        )
        inputs.append(widget)  # Add all widgets to inputs
        pile_contents.append((widget, ("pack", None)))

    pile.contents = pile_contents
