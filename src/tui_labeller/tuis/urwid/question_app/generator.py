from typing import List, Union

from typeguard import typechecked

from tui_labeller.tuis.urwid.question_data_classes import (
    AddressSelectorQuestionData,
    DateQuestionData,
    HorizontalMultipleChoiceQuestionData,
    InputValidationQuestionData,
    VerticalMultipleChoiceQuestionData,
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
            VerticalMultipleChoiceQuestionData,
            HorizontalMultipleChoiceQuestionData,
            AddressSelectorQuestionData,
        ]
    ],
) -> QuestionnaireApp:
    """Create and run a questionnaire with the given questions."""
    app = QuestionnaireApp(header=header, questions=questions)
    # write_to_file(filename="eg.txt", content="STARTED", append=False)
    return app
