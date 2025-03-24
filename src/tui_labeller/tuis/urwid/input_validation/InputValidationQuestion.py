import re
from typing import List

import urwid

from tui_labeller.file_read_write_helper import write_to_file
from tui_labeller.tuis.urwid.helper import get_matching_unique_suggestions
from tui_labeller.tuis.urwid.input_validation.autocomplete_filtering import (
    get_filtered_suggestions,
)


class InputValidationQuestion(urwid.Edit):
    def __init__(
        self,
        caption,
        ai_suggestions=None,
        history_suggestions=None,
        ai_suggestion_box=None,
        history_suggestion_box=None,
        pile=None,
    ):
        super().__init__(caption=caption)
        self.ai_suggestions = ai_suggestions or []
        self.history_suggestions = history_suggestions or []
        self.ai_suggestion_box = ai_suggestion_box
        self.history_suggestion_box = history_suggestion_box
        self.pile = pile
        self._in_autocomplete: bool = False

    def valid_char(self, ch):
        return len(ch) == 1 and (ch.isalpha() or ch in [":", "*"])

    def keypress(self, size, key):
        """Overrides the internal/urwid pip package method "keypress" to map
        incoming keys into separate behaviour."""
        if key == "meta u":
            matching_suggestions: List[str] = get_matching_unique_suggestions(
                suggestions=self.ai_suggestions,
                current_text=self.get_edit_text(),
                cursor_pos=self.edit_pos,
            )
            if len(matching_suggestions) >= 1:
                self.apply_suggestion(matching_suggestions=matching_suggestions)
                return "next_question"
        if key == "ctrl u":
            matching_suggestions: List[str] = get_matching_unique_suggestions(
                suggestions=self.history_suggestions,
                current_text=self.get_edit_text(),
                cursor_pos=self.edit_pos,
            )
            if len(matching_suggestions) >= 1:
                self.apply_suggestion(matching_suggestions=matching_suggestions)
                return "next_question"

        if key == "tab":
            matching_suggestions: List[str] = get_matching_unique_suggestions(
                suggestions=self.ai_suggestions + self.history_suggestions,
                current_text=self.get_edit_text(),
                cursor_pos=self.edit_pos,
            )
            if len(matching_suggestions) == 1:

                self.apply_suggestion(matching_suggestions=matching_suggestions)
                return "next_question"
        if key == "home":
            if self.edit_pos == 0:
                # Home at start of question moves to previous question.
                return "previous_question"
            self.set_edit_pos(0)  # Move back to start.
            return None
        if key == "end":
            if self.edit_pos == len(self.edit_text):
                # End at end of question moves to next question.
                return "next_question"
            self.set_edit_pos(len(self.edit_text))  # Move to end of input box.
            return None
        if key == "shift tab":
            self._log_suggestions("previous_question", "previous_questiona")
            return "previous_question"

        if key == "enter":
            return "enter"
        if key == "up":
            return "previous_question"
        if key == "down":
            return "next_question"
        elif key in ("delete", "backspace", "left", "right"):
            result = super().keypress(size, key)
            self.update_autocomplete()
            return result
        elif self.valid_char(key):
            result = super().keypress(size, key)
            self.update_autocomplete()
            return result
        return None

    def _match_pattern(self, suggestion):
        pattern = self.edit_text.lower().replace("*", ".*")
        return bool(re.match(f"^{pattern}$", suggestion.lower()))

    def update_autocomplete(self):
        write_to_file(filename="eg.txt", content=f"CALLED ", append=True)
        if self._in_autocomplete:  # Prevent recursion
            return

        self._in_autocomplete = True  # Set flag
        self._update_ai_suggestions()
        self._update_history_suggestions()

        try:
            self._handle_autocomplete()
        finally:
            self._in_autocomplete = False  # Reset flag

    def _update_ai_suggestions(self):
        """Update the AI suggestion box with filtered suggestions."""
        if not self.ai_suggestion_box or not self.ai_suggestions:
            return

        ai_remaining_suggestions = get_filtered_suggestions(
            input_text=self.edit_text,
            available_suggestions=list(
                map(lambda x: x.caption, self.ai_suggestions)
            ),
        )
        ai_suggestions_text = ", ".join(ai_remaining_suggestions)
        self._log_suggestions(
            "SETTING ai_suggestions_text", ai_suggestions_text
        )
        self._set_suggestion_text(self.ai_suggestion_box, ai_suggestions_text)
        return ai_remaining_suggestions

    def _update_history_suggestions(self):
        """Update the history suggestion box with filtered suggestions."""
        if not self.history_suggestion_box or not self.history_suggestions:
            return

        history_remaining_suggestions = get_filtered_suggestions(
            input_text=self.edit_text,
            available_suggestions=list(
                map(lambda x: x.caption, self.history_suggestions)
            ),
        )
        history_suggestions_text = ", ".join(history_remaining_suggestions)
        self._log_suggestions(
            "history_suggestions_text", history_suggestions_text
        )
        self._set_suggestion_text(
            self.history_suggestion_box, history_suggestions_text
        )
        return history_remaining_suggestions

    def _log_suggestions(self, label, suggestions_text):
        """Write suggestions to a log file."""
        write_to_file(
            filename="eg.txt",
            content=f"{label}={suggestions_text}",
            append=True,
        )

    def _set_suggestion_text(self, suggestion_box, text):
        """Set text in a suggestion box and invalidate it."""
        suggestion_box.base_widget.set_text(text)
        suggestion_box.base_widget._invalidate()

    def _handle_autocomplete(self):
        """Handle wildcard-based autocompletion."""
        if "*" not in self.edit_text:
            self.owner.set_attr_map({None: "normal"})
            return
        ai_suggestions = self._update_ai_suggestions() or []
        history_suggestions = self._update_history_suggestions() or []

        if len(ai_suggestions) == 1:
            self._apply_autocomplete(ai_suggestions[0])
        elif len(history_suggestions) == 1:
            self._apply_autocomplete(history_suggestions[0])

    def _apply_autocomplete(self, new_text):
        """Apply the autocompleted text and move cursor to the end."""
        self.set_edit_text(new_text)
        self.set_edit_pos(len(new_text))

    def apply_suggestion(self, matching_suggestions: List[str]) -> None:
        self.set_edit_text(matching_suggestions[0])
        self.set_edit_pos(len(matching_suggestions[0]))
        return None
