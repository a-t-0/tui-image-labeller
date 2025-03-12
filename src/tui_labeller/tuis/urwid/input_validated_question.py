from typeguard import typechecked

from tui_labeller.tuis.urwid.input_validation.InputValidationQuestions import (
    InputValidationQuestions,
)


@typechecked
def ask_input_validated_question():

    app = InputValidationQuestions()
    app.run()
