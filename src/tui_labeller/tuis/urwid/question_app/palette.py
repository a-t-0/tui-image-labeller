from typing import List

from typeguard import typechecked


@typechecked
def setup_palette() -> List[tuple]:
    """Setup color palette for the UI with format:
    <identifier>, <text colour>, <background colour>."""
    return [
        ("normal", "white", ""),
        ("highlight", "white", "dark red"),
        ("direction", "white", "yellow"),
        ("navigation", "dark green", ""),
        ("error", "dark red", ""),
        ("ai_suggestions", "yellow", ""),
        ("history_suggestions", "light cyan", ""),
        ("mc_question_palette", "white", ""),
    ]
