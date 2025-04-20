from typing import List, Optional, Union

import urwid
from urwid import AttrMap

from src.tui_labeller.tuis.urwid.mc_question.VerticalMultipleChoiceWidget import (
    VerticalMultipleChoiceWidget,
)
from tui_labeller.file_read_write_helper import write_to_file
from tui_labeller.tuis.urwid.question_app.build_questionnaire import (
    build_questionnaire,
)
from tui_labeller.tuis.urwid.question_app.offload import (
    create_suggestion_box,
    setup_palette,
)
from tui_labeller.tuis.urwid.question_data_classes import (
    DateQuestionData,
    InputValidationQuestionData,
    MultipleChoiceQuestionData,
)


class QuestionnaireApp:
    def __init__(
        self,
        header: str,
        questions: List[
            Union[
                DateQuestionData,
                InputValidationQuestionData,
                MultipleChoiceQuestionData,
            ]
        ],
    ):
        """Initialize the questionnaire application with a list of
        questions."""
        self.descriptor_col_width: int = 20
        self.header = header

        self.nr_of_headers: int = len(self.header)
        input(f"header={header}END")
        input(f"self.nr_of_headers={self.nr_of_headers}END")
        self.palette = setup_palette()
        self.questions = questions
        self.inputs: List[Union[VerticalMultipleChoiceWidget, AttrMap]] = []
        self.pile = urwid.Pile([])

        # Setup UI elements
        self.ai_suggestion_box: AttrMap = create_suggestion_box(
            palette_name="ai_suggestions"
        )
        self.history_suggestion_box = create_suggestion_box(
            palette_name="history_suggestions"
        )
        self.error_display: AttrMap = urwid.AttrMap(urwid.Text(""), "error")

        # Build questionnaire
        build_questionnaire(
            header=header,
            inputs=self.inputs,
            questions=self.questions,
            descriptor_col_width=self.descriptor_col_width,
            pile=self.pile,
            ai_suggestion_box=self.ai_suggestion_box,
            history_suggestion_box=self.history_suggestion_box,
            error_display=self.error_display,
        )

        self.fill = urwid.Filler(self.pile, valign="top")
        self.loop = urwid.MainLoop(
            self.fill, self.palette, unhandled_input=self._handle_input
        )

    # Override
    def _move_focus(self, current_pos: int, key: str) -> None:
        """Move focus to next/previous question with wrap-around."""

        nr_of_questions = len(self.questions)
        if not nr_of_questions:
            raise ValueError("Should have questions.")

        if key in ["enter", "down", "tab"]:
            next_pos = (
                0 if current_pos == nr_of_questions - 1 else current_pos + 1
            )
            self.pile.focus_position = next_pos = next_pos
        elif key == "up":
            next_pos = (
                nr_of_questions - 1 if current_pos == 0 else current_pos - 1
            )
            self.pile.focus_position = next_pos
        else:
            raise ValueError(
                f"Unexpected key={key}, current_pos={current_pos}."
            )

    # Override
    def _handle_input(self, key: str):
        """Handle user keyboard input."""
        current_pos = self.pile.focus_position - 1

        if key in ("enter", "down", "tab", "up"):
            if current_pos >= 0:
                self._move_focus(current_pos=current_pos, key=key)
        elif key == "terminator":
            # raise ValueError("STOOPPPED")
            raise urwid.ExitMainLoop()  # Exit the main loop

        elif key == "q":
            self._save_results()
            raise urwid.ExitMainLoop()

        elif key == "next_question":
            if (
                self.pile.focus_position
                < len(self.questions) - 1 + self.nr_of_headers
            ):
                self.pile.focus_position += 1
            else:
                # TODO: parameterise start question position wrt header at 0.
                self.pile.focus_position = self.nr_of_headers
                # TODO: reset edit position of current question to start of edit text.
            focused_widget = self.inputs[
                self.pile.focus_position - self.nr_of_headers
            ].base_widget

        elif key == "previous_question":
            if self.pile.focus_position > 1:
                self.pile.focus_position -= 1
            else:
                self._move_focus(current_pos=current_pos, key="up")

        # Update the autocomplete suggestions.
        focused_widget = self.inputs[
            self.pile.focus_position - self.nr_of_headers
        ].base_widget
        if not isinstance(focused_widget, VerticalMultipleChoiceWidget):
            focused_widget.update_autocomplete()

    # Manual
    def _save_results(self):
        """Save questionnaire results before exit."""
        results = {}
        for i, input_widget in enumerate(self.inputs):
            results[f"question_{i}"] = input_widget.base_widget.edit_text
        # Add saving logic here if needed
        write_to_file("results.txt", str(results), append=True)

    # Override
    def run(self, alternative_start_pos: Optional[int] = None):
        """Start the questionnaire application."""
        if self.inputs:
            if alternative_start_pos is None:
                self.pile.focus_position = 1  # TODO: parameterise Header.
            else:
                self.pile.focus_position = alternative_start_pos
            self.inputs[1].base_widget.initalise_autocomplete_suggestions()
        self.loop.run()
