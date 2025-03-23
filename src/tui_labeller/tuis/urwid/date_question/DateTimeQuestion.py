import datetime
from typing import List

import urwid
from typeguard import typechecked
from urwid.widget.pile import Pile

from tui_labeller.file_read_write_helper import write_to_file
from tui_labeller.tuis.urwid.date_question.helper import (
    update_values,
)
from tui_labeller.tuis.urwid.date_question.update_digit_value import (
    update_digit_value,
)
from tui_labeller.tuis.urwid.helper import get_matching_unique_suggestions
from tui_labeller.tuis.urwid.question_data_classes import (
    AISuggestion,
)


@typechecked
class DateTimeQuestion(urwid.Edit):
    def __init__(
        self,
        caption: str,
        ai_suggestions: List[AISuggestion],
        ai_suggestion_box: urwid.AttrMap,
        pile: Pile = None,
        date_only: bool = False,
        **kwargs,
    ):
        super().__init__(caption, **kwargs)
        self.ai_suggestions: List[AISuggestion] = ai_suggestions
        write_to_file(
            filename="eg.txt",
            content=f"DATE OBJ self.ai_suggestions={self.ai_suggestions}",
            append=True,
        )
        self.ai_suggestion_box = ai_suggestion_box
        self.pile = pile
        self.date_only = date_only
        self._in_autocomplete: bool = False
        self.error_text = urwid.Text("")
        self.help_text = urwid.Text("")
        self.date_parts = [4, 2, 2]  # year, month, day
        self.time_parts = [2, 2]  # hour, minute
        self.current_part = 0
        self.date_values = [None, None, None]  # year, month, day
        self.time_values = [None, None]  # hour, minute
        self.date_separator = "-"
        self.time_separator = ":"
        # Start with today as default value.
        today = datetime.datetime.now()
        self.date_values = [today.year, today.month, today.day]
        if not self.date_only:
            self.time_values = [today.hour, today.minute]
        self.update_text()  # Set initial text based on today's date/time
        self.initalise_autocomplete_suggestions()

    def keypress(self, size, key):
        current_pos: int = self.edit_pos
        write_to_file(
            filename="eg.txt",
            content=f"size={size}, key={key}",
            append=True,
        )
        if key == "ctrl h":
            self.show_help()
            return None

        if key == "meta u":
            if (
                self.ai_suggestions
            ):  # If there's at least 1 suggestion, accept it.
                self.apply_first_ai_suggestion()
                return "next_question"

        if key == "enter":
            return (  # Signal to move to the next box (already implemented)
                "next_question"
            )
        if key in ["delete", "backspace"]:
            return None
        # TODO 3: Ensure that pressing "Tab" moves it to the next segment
        if key == "tab":
            matching_suggestions: List[str] = get_matching_unique_suggestions(
                suggestions=self.ai_suggestions,
                current_text=self.get_edit_text(),
                cursor_pos=self.edit_pos,
            )
            if len(matching_suggestions) == 1:
                self.apply_first_ai_suggestion()
                return "next_question"
            else:
                return self.move_to_next_part()
        if key == "shift tab":
            pass
        if key == "left":
            return self.move_cursor_to_left(current_pos=current_pos)

        if key == "right":
            return self.move_cursor_to_right(current_pos=current_pos)

        if key == "up" or key == "down":
            self.date_values, self.time_values = update_values(
                direction=key,
                edit_text=self.get_edit_text(),
                current_pos=current_pos,
                date_only=self.date_only,
                date_values=self.date_values,
                time_values=self.time_values,
            )
            self.update_text()
            self.update_autocomplete()
            return None

        if key.isdigit():
            # self.update_digit_value(new_digit=key)
            self.date_values, self.time_values = update_digit_value(
                edit_text=self.get_edit_text(),
                current_pos=current_pos,
                new_digit=int(key),
                date_only=self.date_only,
                date_values=self.date_values,
                time_values=self.time_values,
            )
            self.update_text()
            return self.move_cursor_to_right(current_pos=current_pos)

        result = super().keypress(size, key)
        if result:

            self.error_text.original_widget.set_text(
                ""
            )  # Clear error on valid input
        return result

    def move_to_next_part(self):
        if self.date_only:
            # For date only (yyyy-mm-dd), part starts are 0 (year), 5 (month), 8 (day)
            part_starts = [0, 5, 8]
            # Find which part we're in based on edit_pos
            current_part = 0
            for i, pos in enumerate(part_starts):
                if self.edit_pos >= pos:
                    current_part = i
                else:
                    break
            # Move to next part or reset
            if current_part < len(part_starts) - 1:
                self.current_part = current_part + 1
                self.set_edit_pos(part_starts[self.current_part])
            else:
                self.current_part = 0
                self.set_edit_pos(0)
                return "next_question"
        else:

            # For full format (yyyy-mm-dd hh:ss), part starts are 0 (year), 5 (month), 8 (day), 11 (hour), 14 (seconds)
            part_starts = [0, 5, 8, 11, 14]
            # Find which part we're in based on edit_pos
            current_part = 0
            for i, pos in enumerate(part_starts):
                if self.edit_pos >= pos:
                    current_part = i
                else:
                    break
            # Move to next part or reset
            if current_part < len(part_starts) - 1:
                self.current_part = current_part + 1
                self.set_edit_pos(part_starts[self.current_part])
            else:
                self.current_part = 0
                self.set_edit_pos(0)
                write_to_file(
                    filename="eg.txt",
                    content=(
                        f"self.current_part={self.current_part},"
                        f" self.date_parts={self.date_parts},"
                        f" self.time_parts={self.time_parts}"
                    ),
                    append=True,
                )
                return "next_question"

    def update_text(
        self,
    ):
        date_str = self.date_separator.join(
            map(
                lambda x: str(x).zfill(2) if x is not None else "00",
                self.date_values,
            )
        )
        if self.date_only:
            self.set_edit_text(date_str)
        else:
            time_str = self.time_separator.join(
                map(
                    lambda x: str(x).zfill(2) if x is not None else "00",
                    self.time_values,
                )
            )
            self.set_edit_text(date_str + " " + time_str)

    def show_help(self):
        self.help_text.set_text(
            "Use arrows to adjust, Tab to move parts, Enter to next field"
        )

    def move_cursor_to_right(self, current_pos):
        if current_pos < len(self.get_edit_text()):
            if self.date_only:
                if current_pos in [3, 6]:  # Skip date separators: yyyy-mm-dd
                    self.set_edit_pos(current_pos + 2)
                else:
                    self.set_edit_pos(current_pos + 1)
            else:
                if current_pos in [
                    3,
                    6,
                    9,
                    12,
                ]:  # Skip separators: yyyy-mm-dd hh:mm
                    self.set_edit_pos(current_pos + 2)
                else:
                    self.set_edit_pos(current_pos + 1)
            return None
        else:
            return "next_question"

    def move_cursor_to_left(self, current_pos):
        if current_pos > 0:
            if self.date_only:
                if current_pos in [5, 8]:  # Skip date separators: yyyy-mm-dd
                    self.set_edit_pos(current_pos - 2)
                else:
                    self.set_edit_pos(current_pos - 1)
            else:
                if current_pos in [
                    5,
                    8,
                    11,
                    14,
                ]:  # Skip separators: yyyy-mm-dd hh:mm
                    self.set_edit_pos(current_pos - 2)
                else:
                    self.set_edit_pos(current_pos - 1)
            return None
        else:
            return "previous_question"

    def update_autocomplete(self):
        if self._in_autocomplete:  # Prevent recursion
            return

        if not self.ai_suggestion_box:
            return

        matching_suggestions: List[str] = get_matching_unique_suggestions(
            suggestions=self.ai_suggestions,
            current_text=self.get_edit_text(),
            cursor_pos=self.edit_pos,
        )
        suggestions_text = ", ".join(matching_suggestions)

        self._in_autocomplete = True  # Set flag

        self.ai_suggestion_box.base_widget.set_text(suggestions_text)
        self.ai_suggestion_box.base_widget._invalidate()

        if "*" in self.edit_text and len(matching_suggestions) == 1:
            new_text = matching_suggestions[0]
            self.set_edit_text(new_text)
            self.set_edit_pos(len(new_text))

        self._in_autocomplete = False  # Reset flag

    def apply_first_ai_suggestion(self) -> None:
        matching_suggestions: List[str] = get_matching_unique_suggestions(
            suggestions=self.ai_suggestions,
            current_text=self.get_edit_text(),
            cursor_pos=self.edit_pos,
        )
        self.set_edit_text(matching_suggestions[0])
        self.set_edit_pos(len(matching_suggestions[0]))
        return None

    def initalise_autocomplete_suggestions(self):
        write_to_file(
            filename="eg.txt",
            content=f"initialising ai_suggestions={self.ai_suggestions}",
            append=True,
        )
        self.ai_suggestion_box.base_widget.set_text(
            ",".join(map(lambda x: x.caption, self.ai_suggestions))
        )
        self.ai_suggestion_box.base_widget._invalidate()
