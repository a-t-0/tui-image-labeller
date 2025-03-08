from typeguard import typechecked

from tui_labeller.tuis.urwid.InputValidationQuestions import (
    InputValidationQuestions,
)


@typechecked
def ask_input_validated_question():

    app = InputValidationQuestions()
    app.run()
