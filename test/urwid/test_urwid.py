from pprint import pprint
from typing import List

import pytest
import urwid

from tui_labeller.tuis.urwid.input_validation.InputValidationQuestions import (
    InputValidationQuestions,
)


@pytest.fixture
def app():
    app = InputValidationQuestions()
    app.loop.screen = urwid.raw_display.Screen()
    return app


def assert_autocomplete_options(
    the_question, expected_options: List[str], step: str
):
    """Helper function to compare autocomplete options with expected list."""
    # Extract the text from the autocomplete_box widget
    actual_widget = (
        the_question._original_widget.autocomplete_box.original_widget
    )
    actual_text = actual_widget.text  # Get the Text widget’s content
    # Split the comma-separated string into a list, stripping whitespace
    actual_options = [opt.strip() for opt in actual_text.split(",")]
    # Sort both lists to ignore order differences
    actual_options.sort()
    expected_options_sorted = sorted(expected_options)
    assert actual_options == expected_options_sorted, (
        f"After '{step}', expected {expected_options_sorted}, got"
        f" '{actual_options}'"
    )
    # Debug output
    pprint(f"Autocomplete text after '{step}': {actual_text}")


def test_avocado_selection(app):
    the_question = app.inputs[
        0
    ]  # Assuming inputs[0] is the widget we’re testing

    # Step 1: Press "a"
    the_question.keypress(1, "a")
    expected_after_a = ["avocado", "apple", "apricot"]
    assert_autocomplete_options(the_question, expected_after_a, "a")

    # Step 2: Press "*"
    the_question.keypress(1, "*")
    expected_after_star = ["avocado", "apple", "apricot"]
    assert_autocomplete_options(the_question, expected_after_star, "*")

    # Step 3: Press "t"
    the_question.keypress(1, "t")
    expected_after_t = ["apricot"]
    assert_autocomplete_options(the_question, expected_after_t, "t")
