from pprint import pprint
from typing import List

import pytest
import urwid

from tui_labeller.tuis.urwid.InputValidationQuestions import (
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
    actual_widget = (
        the_question._original_widget.autocomplete_box.original_widget
    )
    actual_text = actual_widget.text
    actual_options = [opt.strip() for opt in actual_text.split(",")]
    actual_options.sort()
    expected_options_sorted = sorted(expected_options)
    assert actual_options == expected_options_sorted, (
        f"After '{step}', expected {expected_options_sorted}, got"
        f" '{actual_options}'"
    )
    pprint(f"Autocomplete text after '{step}': {actual_text}")


# Original test
def test_avocado_selection(app):
    the_question = app.inputs[0]
    the_question.keypress(1, "a")
    assert_autocomplete_options(
        the_question, ["avocado", "apple", "apricot"], "a"
    )
    the_question.keypress(1, "*")
    assert_autocomplete_options(
        the_question, ["avocado", "apple", "apricot"], "*"
    )
    the_question.keypress(1, "t")
    assert_autocomplete_options(the_question, ["apricot"], "t")


# New test cases
def test_case_sensitivity(app):
    the_question = app.inputs[0]
    the_question.keypress(1, "A")
    the_question.keypress(1, "*")
    the_question.keypress(1, "t")
    assert_autocomplete_options(the_question, ["apricot"], "A*t")


def test_multiple_matches_with_wildcard(app):
    the_question = app.inputs[0]
    the_question.keypress(1, "a")
    the_question.keypress(1, "*")
    the_question.keypress(1, "c")
    # Assuming the options list contains these test cases
    assert_autocomplete_options(the_question, ["avocado", "apricot"], "a*c")


def test_wildcard_at_start(app):
    the_question = app.inputs[0]
    the_question.keypress(1, "*")
    the_question.keypress(1, "c")
    the_question.keypress(1, "o")
    the_question.keypress(1, "t")
    assert_autocomplete_options(the_question, ["apricot"], "*cot")


def test_multiple_wildcards_complex(app):
    the_question = app.inputs[0]
    the_question.keypress(1, "a")
    the_question.keypress(1, "*")
    the_question.keypress(1, "d")
    the_question.keypress(1, "*")
    the_question.keypress(1, "o")
    assert_autocomplete_options(the_question, ["avocado", "ado"], "a*d*o")


def test_empty_pattern(app):
    the_question = app.inputs[0]
    # No keypress, just initial state
    assert_autocomplete_options(
        the_question, ["apple", "apricot", "avocado"], "empty"
    )


def test_only_wildcard(app):
    the_question = app.inputs[0]
    the_question.keypress(1, "*")
    assert_autocomplete_options(
        the_question, ["apple", "apricot", "avocado"], "*"
    )


def test_consecutive_wildcards(app):
    the_question = app.inputs[0]
    the_question.keypress(1, "a")
    the_question.keypress(1, "*")
    the_question.keypress(1, "*")
    the_question.keypress(1, "e")
    assert_autocomplete_options(the_question, ["apple"], "a**e")


def test_non_alphanumeric(app):
    the_question = app.inputs[0]
    the_question.keypress(1, "a")
    the_question.keypress(1, "*")
    the_question.keypress(1, "t")
    assert_autocomplete_options(the_question, ["apricot"], "a*t")
    the_question.keypress(1, "!")
    # ! is not a valid character, so one would nto expect it to be added.
    assert_autocomplete_options(the_question, ["apricot"], "a*t!")


def test_wildcard_at_end(app):
    the_question = app.inputs[0]
    the_question.keypress(1, "a")
    the_question.keypress(1, "p")
    the_question.keypress(1, "*")
    assert_autocomplete_options(the_question, ["apple", "apricot"], "ap*")
