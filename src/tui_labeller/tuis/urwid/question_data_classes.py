from typing import List


class AISuggestion:
    def __init__(self, caption: str, probability: float, model_name: str):
        self.caption: str = caption
        self.probability: float = probability
        self.ai_suggestions: str = model_name


class HistorySuggestion:
    def __init__(self, caption: str, frequency: int):
        self.caption: str = caption
        self.frequency: int = frequency


class DateQuestionData:
    def __init__(
        self, caption: str, date_only: bool, ai_suggestions: List[AISuggestion]
    ):
        self.caption = caption
        self.date_only = date_only
        self.ai_suggestions: AISuggestion = ai_suggestions


class InputValidationQuestionData:
    def __init__(
        self,
        caption: str,
        ai_suggestions: List[AISuggestion],
        history_suggestions: List[HistorySuggestion],
    ):
        self.caption = caption
        self.ai_suggestions = ai_suggestions
        self.history_suggestions = history_suggestions


class MultipleChoiceQuestionData:
    def __init__(
        self,
        question: str,
        choices: List[str],
        ai_suggestions: List[AISuggestion],
    ):
        self.question = question
        self.choices = choices
        self.ai_suggestions = ai_suggestions
