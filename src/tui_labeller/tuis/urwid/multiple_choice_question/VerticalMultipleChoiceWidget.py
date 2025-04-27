from typing import List, Union

import urwid
from typeguard import typechecked

from tui_labeller.tuis.urwid.helper import get_matching_unique_suggestions
from tui_labeller.tuis.urwid.input_validation.InputType import InputType
from tui_labeller.tuis.urwid.multiple_choice_question.helper import (
    get_selected_caption,
    get_vc_question,
    input_is_in_int_range,
)
from tui_labeller.tuis.urwid.question_data_classes import (
    VerticalMultipleChoiceQuestionData,
)


class VerticalMultipleChoiceWidget(urwid.Edit):
    @typechecked
    def __init__(
        self,
        question: VerticalMultipleChoiceQuestionData,
        ai_suggestions=None,
        history_suggestions=None,
        ai_suggestion_box=None,
        history_suggestion_box=None,
        pile=None,
    ):
        self.indentation: int = 1
        super().__init__(
            caption=get_vc_question(
                vc_question=question, indentation=self.indentation
            )
        )
        self.question: VerticalMultipleChoiceQuestionData = question
        self.input_type: InputType = InputType.INTEGER
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
                    vc_question=self.question,
                    selected_index=int(self.get_edit_text()),
                    indentation=self.indentation,
                )
            )
            return "next_question"
        # Set highlighting to error if required and empty
        if self.question.ans_required:
            self.owner.set_attr_map({None: "error"})
            return None
        else:
            self.set_caption(
                get_selected_caption(
                    vc_question=self.question,
                    selected_index=int(self.get_edit_text()),
                    indentation=self.indentation,
                )
            )
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
        if self.question.ans_required:
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
            if len(self.edit_text) != 0:
                self.set_caption(
                    get_selected_caption(
                        vc_question=self.question,
                        selected_index=int(self.get_edit_text()),
                        indentation=self.indentation,
                    )
                )
                return self.safely_go_to_next_question()
            return None

        if key == "up":
            return self.safely_go_to_previous_question()

        if key == "down":
            return self.safely_go_to_next_question()

        elif key in ("delete", "backspace", "left", "right"):
            # Handle backspace/delete by calling super() first to update the text
            result = super().keypress(size, key)
            # Update caption to show the full question
            self.set_caption(
                get_vc_question(
                    vc_question=self.question, indentation=self.indentation
                )
            )
            return result

        elif self.valid_char(ch=key):
            if input_is_in_int_range(
                char=key,
                start=0,
                ceiling=len(self.question.choices),
                current=self.edit_text,
            ):
                # Append the new digit
                new_text = self.edit_text + key
                self.set_edit_text(new_text)
                self.set_edit_pos(len(new_text))  # Ensure cursor is at the end

                # Keep the full question visible in the caption
                self.set_caption(
                    get_vc_question(
                        vc_question=self.question, indentation=self.indentation
                    )
                )

                # Check if the current input is a valid, non-extendable choice
                try:
                    current_index = int(new_text)
                    max_choice = len(self.question.choices) - 1
                    if 0 <= current_index <= max_choice:
                        # Check if appending any digit (0-9) would result in a valid index
                        can_extend = False
                        for digit in range(10):
                            extended_text = new_text + str(digit)
                            try:
                                extended_index = int(extended_text)
                                # Allow extension only if the extended index is within range
                                # and the extended text doesn't exceed the maximum choice length
                                if 0 <= extended_index <= max_choice and len(
                                    extended_text
                                ) <= len(str(max_choice)):
                                    can_extend = True
                                    break
                            except ValueError:
                                continue
                        if not can_extend:
                            # Valid choice that cannot be extended, move to next question
                            self.set_caption(
                                get_selected_caption(
                                    vc_question=self.question,
                                    selected_index=current_index,
                                    indentation=self.indentation,
                                )
                            )
                            return self.safely_go_to_next_question()
                except ValueError:
                    pass

                return new_text
            else:
                return None

        return None

    @typechecked
    def get_answer(self) -> str:
        return self.question.choices[int(self.get_edit_text())]

    @typechecked
    def has_answer(self) -> bool:
        """Checks if a valid answer can be obtained without errors and edit
        text is not empty.

        Returns:
            bool: True if get_answer() would return a valid result without raising an error
                and edit text is not empty, False otherwise.
        """
        if not self.get_edit_text():  # Check if edit text is empty
            return False
        try:
            self.get_answer()
            return True
        except (
            ValueError,
            IndexError,
        ):  # Handle invalid index or non-integer input
            return False

    @typechecked
    def set_answer(self, value: Union[str, int]) -> None:
        """Sets the answer for the multiple choice question based on the
        provided value.

        Args:
            value: The value to set. Can be either:
                - str: The exact choice text from question.choices.
                - int: The index of the choice in question.choices.

        Raises:
            ValueError: If the value is not a valid choice or index, or if the type is incorrect.
        """
        if isinstance(value, str):
            # Check if the string is a valid choice
            if value not in self.question.choices:
                raise ValueError(
                    f"Value '{value}' is not a valid choice in"
                    f" {self.question.choices}"
                )
            # Find the index of the choice.
            index = self.question.choices.index(value)
            self.set_edit_text(str(index))
        elif isinstance(value, int):
            # Check if the index is valid
            if not (0 <= value < len(self.question.choices)):
                raise ValueError(
                    f"Index {value} is out of range for choices"
                    f" {self.question.choices}"
                )
            self.set_edit_text(str(value))
        else:
            raise ValueError(f"Expected str or int, got {type(value)}")

        # Update the caption to reflect the selected choice
        self.set_caption(
            get_selected_caption(
                vc_question=self.question,
                selected_index=int(self.get_edit_text()),
                indentation=self.indentation,
            )
        )
