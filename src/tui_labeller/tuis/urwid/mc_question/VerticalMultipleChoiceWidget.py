from typing import List, Union

import urwid
from typeguard import typechecked

from src.tui_labeller.tuis.urwid.mc_question.helper import (
    get_mc_question,
    get_selected_caption,
    input_is_in_int_range,
)
from tui_labeller.tuis.urwid.helper import get_matching_unique_suggestions
from tui_labeller.tuis.urwid.input_validation.InputType import InputType
from tui_labeller.tuis.urwid.question_data_classes import (
    MultipleChoiceQuestionData,
)


class VerticalMultipleChoiceWidget(urwid.Edit):
    @typechecked
    def __init__(
        self,
        mc_question: MultipleChoiceQuestionData,
        ans_required: bool,
        ai_suggestions=None,
        history_suggestions=None,
        ai_suggestion_box=None,
        history_suggestion_box=None,
        pile=None,
    ):
        self.indentation: int = 1
        super().__init__(
            caption=get_mc_question(
                mc_question=mc_question, indentation=self.indentation
            )
        )
        self.mc_question: MultipleChoiceQuestionData = mc_question
        self.input_type: InputType = InputType.INTEGER
        self.ans_required: bool = ans_required
        self.ai_suggestions = ai_suggestions or []
        self.history_suggestions = history_suggestions or []
        self.ai_suggestion_box = ai_suggestion_box
        self.history_suggestion_box = history_suggestion_box
        self.pile = pile
        self._in_autocomplete: bool = False

    @typechecked
    def valid_char(self, ch: str):
        """Check if a character is valid based on specified mode.

        Args:
            ch: Character to check (string of length 1)
            mode: InputType enum - LETTERS for a-Z/:/* or NUMBERS for digits and .

        Returns:
            bool: True if character is valid for the specified mode
        """
        if len(ch) != 1:
            return False
        if ch.isdigit():
            return True
        return False

    @typechecked
    def is_valid_answer(self):
        if self.inputs is None:
            return False
        return self.inputs != ""

    @typechecked
    def safely_go_to_next_question(self) -> Union[str, None]:
        if self.edit_text.strip():  # Check if current input has text
            self.owner.set_attr_map({None: "normal"})
            self.set_caption(
                get_selected_caption(
                    mc_question=self.mc_question,
                    selected_index=int(self.get_edit_text()),
                    indentation=self.indentation,
                )
            )
            self.set_edit_text("")
            return "next_question"
        # Set highlighting to error if required and empty
        if self.ans_required:
            self.owner.set_attr_map({None: "error"})
            return None
        else:
            self.set_caption(
                get_selected_caption(
                    mc_question=self.mc_question,
                    selected_index=int(self.get_edit_text()),
                    indentation=self.indentation,
                )
            )
            self.set_edit_text("")
            return "next_question"

    @typechecked
    def handle_attempt_to_navigate_to_previous_question(
        self,
    ) -> Union[str, None]:
        if self.pile.focus_position > 1:  # TODO: parameterise header
            return "previous_question"
        else:
            self.owner.set_attr_map({None: "direction"})
            return None

    @typechecked
    def safely_go_to_previous_question(self) -> Union[str, None]:
        """Allow the user to go up and change an answer unless at the first
        question.

        If the user is not at the first question, they can move to the previous question
        even if the current answer is invalid. However, if the user is at the first question,
        they are not allowed to go back to prevent looping to the last question.

        Returns:
            str: "previous_question" if allowed to proceed to the previous question.
            None: If the answer is required and empty, highlighting is set to error.
        """
        if self.edit_text.strip():  # Check if current input has text.
            self.owner.set_attr_map({None: "normal"})
            return self.handle_attempt_to_navigate_to_previous_question()
        # Set highlighting to error if required and empty.
        if self.ans_required:
            self.owner.set_attr_map({None: "error"})
            return self.handle_attempt_to_navigate_to_previous_question()
        else:
            return self.handle_attempt_to_navigate_to_previous_question()

    @typechecked
    def keypress(self, size, key):
        """Overrides the internal/urwid pip package method "keypress" to map
        incoming keys into separate behaviour."""
        if key == "tab":
            matching_suggestions: List[str] = get_matching_unique_suggestions(
                suggestions=self.ai_suggestions + self.history_suggestions,
                current_text=self.get_edit_text(),
                cursor_pos=self.edit_pos,
            )
            if len(matching_suggestions) == 1:

                self.apply_suggestion(matching_suggestions=matching_suggestions)
                return self.safely_go_to_next_question()
        if key == "home":
            if self.edit_pos == 0:
                # Home at start of question moves to previous question.
                return self.safely_go_to_previous_question()
            self.set_edit_pos(0)  # Move back to start.
            return None
        if key == "end":
            if self.edit_pos == len(self.edit_text):
                # End at end of question moves to next question.
                return self.safely_go_to_next_question()
            self.set_edit_pos(len(self.edit_text))  # Move to end of input box.
            return None
        if key == "shift tab":
            return self.safely_go_to_previous_question()

        if key == "enter":
            # self._caption="HELLO"
            self.set_caption(
                get_selected_caption(
                    mc_question=self.mc_question,
                    selected_index=int(self.get_edit_text()),
                    indentation=self.indentation,
                )
            )
            return self.safely_go_to_next_question()
        if key == "up":
            return self.safely_go_to_previous_question()
        if key == "down":
            return self.safely_go_to_next_question()
        elif key in ("delete", "backspace", "left", "right"):
            self.set_caption(
                get_mc_question(
                    mc_question=self.mc_question, indentation=self.indentation
                )
            )
            result = super().keypress(size, key)
            return result
        elif self.valid_char(ch=key):
            if input_is_in_int_range(
                char=key,
                start=0,
                ceiling=len(self.mc_question.choices),
                current=self.edit_text,
            ):
                new_text = self.edit_text + key
                self.set_edit_text(new_text)
                self.set_caption(
                    get_selected_caption(
                        mc_question=self.mc_question,
                        selected_index=int(self.get_edit_text()),
                        indentation=self.indentation,
                    )
                )
                return new_text
            else:
                return None
        return None

    @typechecked
    def get_answer(self) -> str:
        """Returns the current input value converted to the appropriate type
        based on input_type.

        Returns:
            Union[str, float, int]: The current input value as:
                - str for InputType.LETTERS
                - float for InputType.FLOAT
                - int for InputType.INTEGER

        Raises:
            ValueError: If the input cannot be converted to the specified type or is empty when required
        """
        current_text = self.get_edit_text().strip()

        # Check if answer is required but empty
        if self.ans_required and not current_text:
            raise ValueError(
                f"Answer is required but input is empty for '{self.question}'"
            )

        # Return empty string if no input and not required
        if not current_text:
            return ""

        # Convert based on input type

        if self.input_type == InputType.LETTERS:
            return current_text
        if self.input_type == InputType.LETTERS_SEMICOLON:
            return current_text
        elif self.input_type == InputType.FLOAT:
            return float(current_text)
        elif self.input_type == InputType.INTEGER:
            return int(current_text)
        else:
            raise ValueError(f"Unknown input type: {self.input_type}")
