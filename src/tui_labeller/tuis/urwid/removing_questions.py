import urwid
from typeguard import typechecked

from tui_labeller.tuis.urwid.merged_questions import QuestionnaireApp


@typechecked
def remove_last_n_questions_from_list(
    *,
    app: QuestionnaireApp,
    n: int,
) -> None:
    """Remove the last n questions from the QuestionnaireApp's question list
    and update the UI.

    Args:
        app: The running QuestionnaireApp instance to modify.
        n: Number of questions to remove from the end of the list.

    Raises:
        ValueError: If n is negative or greater than the number of questions.
    """
    if n < 0:
        raise ValueError("Number of questions to remove (n) cannot be negative")
    if n > len(app.questions):
        raise ValueError(
            f"Cannot remove {n} questions; only {len(app.questions)} exist"
        )
    if n == 0:
        return  # No changes needed

    # Remove the last n questions from the questions list
    del app.questions[-n:]

    # Remove the last n widgets from the inputs list
    del app.inputs[-n:]

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
