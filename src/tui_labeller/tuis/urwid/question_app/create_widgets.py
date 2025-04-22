from typing import Union

import urwid
from typeguard import typechecked
from urwid import AttrMap, Pile

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
from tui_labeller.tuis.urwid.question_data_classes import (
    DateQuestionData,
    HorizontalMultipleChoiceQuestionData,
    InputValidationQuestionData,
    VerticalMultipleChoiceQuestionData,
)


# Manual
@typechecked
def create_question_widget(
    *,
    pile: Pile,
    ai_suggestion_box: AttrMap,
    history_suggestion_box: AttrMap,
    error_display: AttrMap,
    question_data: Union[
        DateQuestionData,
        InputValidationQuestionData,
        VerticalMultipleChoiceQuestionData,
        HorizontalMultipleChoiceQuestionData,
    ],
) -> Union[
    VerticalMultipleChoiceWidget, HorizontalMultipleChoiceWidget, AttrMap
]:
    """Create appropriate widget based on question type."""
    if isinstance(question_data, DateQuestionData):
        widget = DateTimeQuestion(
            question=question_data.question,
            date_only=question_data.date_only,
            ai_suggestions=question_data.ai_suggestions,
            ai_suggestion_box=ai_suggestion_box,
            pile=pile,
        )
        widget.error_text = error_display
        attr_widget = urwid.AttrMap(widget, "normal")
        widget.owner = attr_widget
        return attr_widget

    elif isinstance(question_data, InputValidationQuestionData):
        widget = InputValidationQuestion(
            question=question_data.question,
            input_type=question_data.input_type,
            ans_required=question_data.ans_required,
            ai_suggestions=question_data.ai_suggestions,
            history_suggestions=question_data.history_suggestions,
            ai_suggestion_box=ai_suggestion_box,
            history_suggestion_box=history_suggestion_box,
            pile=pile,
        )
        if question_data.default is not None:
            widget.set_edit_text(question_data.default)
        attr_widget = urwid.AttrMap(widget, "normal")
        widget.owner = attr_widget
        return attr_widget

    elif isinstance(question_data, VerticalMultipleChoiceQuestionData):
        widget = VerticalMultipleChoiceWidget(
            mc_question=question_data,
            ans_required=True,
            ai_suggestions=question_data.ai_suggestions,
            ai_suggestion_box=ai_suggestion_box,
            history_suggestion_box=history_suggestion_box,
            pile=pile,
        )
        # if question_data.default is not None:
        #     widget.set_edit_text(question_data.default)
        attr_widget = urwid.AttrMap(widget, "normal")
        widget.owner = attr_widget
        return attr_widget
        # return VerticalMultipleChoiceWidget(
        #     mc_question=question_data, ans_required=True
        # )
    elif isinstance(question_data, HorizontalMultipleChoiceQuestionData):
        widget = HorizontalMultipleChoiceWidget(
            mc_question=question_data,
        )
        # if question_data.default is not None:
        #     widget.set_edit_text(question_data.default)
        # attr_widget = urwid.AttrMap(widget, "normal")
        # widget.owner = attr_widget
        return widget
    else:
        raise TypeError(f"Unexpected type:{type(question_data)}")
