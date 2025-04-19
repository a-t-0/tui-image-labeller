from typing import List

import urwid
from typeguard import typechecked

from tui_labeller.tuis.urwid.question_data_classes import (
    InputValidationQuestionData,
)
from tui_labeller.tuis.urwid.QuestionnaireApp import QuestionnaireApp


@typechecked
def remove_specific_questions_from_list(
    *,
    app: QuestionnaireApp,
    expected_questions: List[InputValidationQuestionData],
) -> None:
    """Remove specific questions from the QuestionnaireApp's question list that
    match the expected_questions, and update the UI accordingly.

    Args:
        app: The running QuestionnaireApp instance to modify.
        expected_questions: List of questions to remove if found in app.questions.

    Raises:
        ValueError: If expected_questions is empty.
    """
    if not expected_questions:
        raise ValueError("expected_questions list cannot be empty")

    # Get the question strings to match against
    question_strings = [q.question for q in expected_questions]
    if not question_strings:
        return  # No questions to remove

    # Create new lists excluding the matching questions
    new_questions = []
    new_inputs = []
    indices_to_remove = set()

    # Identify indices of questions to remove
    for i, (question, widget) in enumerate(zip(app.questions, app.inputs)):
        question_text = getattr(
            question, "question", getattr(question, "caption", None)
        )
        if question_text in question_strings:
            indices_to_remove.add(i)
        else:
            new_questions.append(question)
            new_inputs.append(widget)

    if not indices_to_remove:
        return  # No matching questions found to remove

    # Update the app's lists
    app.questions = new_questions
    app.inputs = new_inputs

    # Update pile contents: preserve header, use updated inputs list
    current_contents = app.pile.contents[: app.nr_of_headers]  # Keep header
    current_contents.extend((widget, ("pack", None)) for widget in app.inputs)

    # Re-append suggestion boxes
    current_contents.extend(
        [
            (urwid.Divider(), ("pack", None)),
            (
                urwid.Columns(
                    [
                        (
                            app.descriptor_col_width,
                            urwid.Text("AI suggestions: "),
                        ),
                        app.ai_suggestion_box,
                    ]
                ),
                ("pack", None),
            ),
            (
                urwid.Columns(
                    [
                        (
                            app.descriptor_col_width,
                            urwid.Text("History suggestions: "),
                        ),
                        app.history_suggestion_box,
                    ]
                ),
                ("pack", None),
            ),
        ]
    )
    app.pile.contents = current_contents

    # Adjust focus position if necessary
    if app.inputs:
        app.pile.focus_position = min(
            app.pile.focus_position,
            len(current_contents) - 1,  # Account for suggestion boxes
        )
    elif current_contents:
        app.pile.focus_position = 0  # Focus on header if no inputs remain
