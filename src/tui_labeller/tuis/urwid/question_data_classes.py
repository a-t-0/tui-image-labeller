from typing import List, Optional

from tui_labeller.tuis.urwid.input_validation.InputType import InputType


class AISuggestion:
    def __init__(self, question: str, probability: float, model_name: str):
        self.question: str = question
        self.probability: float = probability
        self.ai_suggestions: str = model_name


class HistorySuggestion:
    def __init__(self, question: str, frequency: int):
        self.question: str = question
        self.frequency: int = frequency


class DateQuestionData:
    def __init__(
        self, question: str, date_only: bool, ai_suggestions: List[AISuggestion]
    ):
        self.question = question
        self.date_only = date_only
        self.ai_suggestions: AISuggestion = ai_suggestions


class InputValidationQuestionData:
    def __init__(
        self,
        question: str,
        input_type: InputType,
        ans_required: bool,
        ai_suggestions: List[AISuggestion],
        history_suggestions: List[HistorySuggestion],
        default: Optional[str] = None,
    ):
        self.question: str = question
        self.input_type = input_type
        self.ans_required: bool = ans_required
        self.ai_suggestions = ai_suggestions
        self.history_suggestions = history_suggestions
        self.default: str = default


class MultipleChoiceQuestionData:
    def __init__(
        self,
        question: str,
        choices: List[str],
        ai_suggestions: List[AISuggestion],
        terminator: Optional[bool] = False,
    ):
        self.question = question
        self.choices = choices
        self.ai_suggestions = ai_suggestions
        self.terminator = terminator


class HorizontalMultipleChoiceQuestionData:
    def __init__(
        self,
        question: str,
        choices: List[str],
        ai_suggestions: List[AISuggestion],
        terminator: Optional[bool] = False,
    ):
        self.question = question
        self.choices = choices
        self.ai_suggestions = ai_suggestions
        self.terminator = terminator
