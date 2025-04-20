from typing import Optional, Union

from hledger_preprocessor.TransactionObjects.Receipt import (  # For image handling
    ExchangedItem,
    Receipt,
)

from src.tui_labeller.tuis.urwid.mc_question.VerticalMultipleChoiceWidget import (
    VerticalMultipleChoiceWidget,
)
from tui_labeller.tuis.urwid.date_question.DateTimeQuestion import (
    DateTimeQuestion,
)
from tui_labeller.tuis.urwid.input_validation.InputValidationQuestion import (
    InputValidationQuestion,
)


# Wrapper class
class AnsweredQuestion:
    def __init__(
        self,
        question: Union[
            DateTimeQuestion,
            InputValidationQuestion,
            VerticalMultipleChoiceWidget,
        ],
    ):
        self.question = question
        self.answer: Optional[str] = None

    def set_answer(self, answer: str) -> None:
        """Set the answer and update the underlying question UI."""
        self.answer = answer
        if isinstance(
            self.question, (DateTimeQuestion, InputValidationQuestion)
        ):
            self.question.set_edit_text(answer if answer is not None else "")
        elif isinstance(self.question, VerticalMultipleChoiceWidget):
            self.question.selected = answer  # Assuming selection logic exists

    def get_question(self) -> str:
        """Get the question's question or equivalent."""
        if isinstance(
            self.question, (DateTimeQuestion, InputValidationQuestion)
        ):
            return self.question.question
        elif isinstance(self.question, VerticalMultipleChoiceWidget):
            return self.question.mc_question.question
        return ""
