from typing import List

import urwid
from typeguard import typechecked
from urwid import AttrMap


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
        ("history_suggestions", "yellow", ""),
        ("mc_question_palette", "light cyan", ""),
    ]


@typechecked
def create_suggestion_box(*, palette_name: str) -> AttrMap:
    """Create a suggestion box widget with specified palette."""
    return AttrMap(urwid.Text("", align="left"), palette_name)
