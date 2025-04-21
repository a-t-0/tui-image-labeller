from typing import List, Union

from typeguard import typechecked

from tui_labeller.tuis.urwid.question_data_classes import (
    DateQuestionData,
    HorizontalMultipleChoiceQuestionData,
    InputValidationQuestionData,
    MultipleChoiceQuestionData,
)
from tui_labeller.tuis.urwid.QuestionnaireApp import QuestionnaireApp


# Manual generator
@typechecked
def create_questionnaire(
    header: str,
    questions: List[
        Union[
            DateQuestionData,
            InputValidationQuestionData,
            MultipleChoiceQuestionData,
            HorizontalMultipleChoiceQuestionData,
        ]
    ],
) -> QuestionnaireApp:
    """Create and run a questionnaire with the given questions."""
    app = QuestionnaireApp(header=header, questions=questions)
    # write_to_file(filename="eg.txt", content="STARTED", append=False)
    return app
