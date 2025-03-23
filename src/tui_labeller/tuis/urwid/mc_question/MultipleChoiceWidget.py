from typing import List

import urwid
from typeguard import typechecked

from tui_labeller.file_read_write_helper import write_to_file
from tui_labeller.tuis.urwid.question_data_classes import (
    AISuggestion,
    MultipleChoiceQuestionData,
)


@typechecked
class MultipleChoiceWidget(urwid.WidgetWrap):
    def __init__(self, mc_question: MultipleChoiceQuestionData):
        self.mc_question: MultipleChoiceQuestionData = mc_question
        self.ai_suggestions: List[AISuggestion] = mc_question.ai_suggestions
        self.selected = None
        self.choice_widgets = []
        self.radio_group = []
        self.setup_widgets()

    def get_answer_in_focus(self) -> int:
        """Returns the column index of the answer you just selected."""
        monitored_nr: int = self._wrapped_widget._contents.focus
        the_obj = self._wrapped_widget._contents[monitored_nr]
        for i, elem in enumerate(the_obj):
            if isinstance(elem, urwid.Columns):
                focus_column: int = elem.get_focus_column()
        if focus_column is not None:
            return focus_column
        raise ValueError("Did not find which column was in focus.")

    def setup_widgets(self):
        # Find the choice with the highest probability for auto-selection
        max_prob = -1
        auto_select_label = None
        if self.ai_suggestions:
            for suggestion in self.ai_suggestions:
                if suggestion.probability > max_prob:
                    max_prob = suggestion.probability
                    auto_select_label = suggestion.caption

        # Create radio buttons and AI suggestion text for each choice in mc_question.choices
        for i, choice in enumerate(
            self.mc_question.choices
        ):  # Ensures all choices are included
            radio_button = urwid.RadioButton(
                self.radio_group,
                choice,
                state=(
                    choice == auto_select_label
                ),  # Auto-select highest probability
                on_state_change=self.on_select,
            )
            write_to_file(
                filename="hello.txt",
                content=f"choice={choice}",
                append=True,
            )
            # Collect all AI suggestions for this choice
            suggestion_texts = []
            if self.ai_suggestions:  # Check if there are any suggestions at all
                for suggestion in self.ai_suggestions:
                    if suggestion.caption == choice:
                        suggestion_texts.append(
                            urwid.Text(
                                (
                                    "ai_suggestion",
                                    (
                                        f"{suggestion.probability:.2f} {suggestion.ai_suggestions}"
                                    ),
                                ),
                                align="left",
                            )
                        )
            # If no suggestions exist for this choice, add an empty placeholder
            if not suggestion_texts:
                suggestion_texts.append(
                    urwid.Text(("ai_suggestion", ""), align="left")
                )

            # Stack the radio button and all suggestions in a Pile
            choice_column = urwid.Pile(
                [
                    urwid.AttrMap(radio_button, "normal", "selected"),
                    *suggestion_texts,  # Unpack all suggestion widgets
                ]
            )
            self.choice_widgets.append(choice_column)

        # Display choices horizontally
        choices_row = urwid.Columns(self.choice_widgets, dividechars=2)
        question_text = urwid.Text(
            ("mc_question_palette", self.mc_question.question)
        )
        pile = urwid.Pile(
            [question_text, choices_row]
        )  # No divider for tighter layout
        super().__init__(pile)

    def on_select(self, radio_button, new_state):
        if new_state:
            self.selected = radio_button.label
            self.confirm_selection()
            write_to_file(
                filename="eg.txt",
                content=(
                    f"new_state={new_state}, radio_button={radio_button},"
                    f" self.selected={self.selected}"
                ),
                append=True,
            )
        else:
            write_to_file(
                filename="eg.txt",
                content=(
                    f"new_state={new_state}, radio_button={radio_button},"
                    f" self.selected={self.selected}"
                ),
                append=True,
            )

    def confirm_selection(self):
        for widget in self.choice_widgets:
            radio = widget.contents[0][
                0
            ].base_widget  # Access radio button from Pile
            if radio.label == self.selected:
                widget.contents[0][0].set_attr_map({None: "selected"})
            else:
                radio.set_state(False, do_callback=False)
                widget.contents[0][0].set_attr_map({None: "normal"})

    def keypress(self, size, key):
        if key in ["enter", "tab"]:
            # Handle both Enter and Tab key presses
            if self.selected is not None or key == "tab":
                # Process selection if something is selected (Enter) or always for Tab
                selected_ans_col = self.get_answer_in_focus()
                # Get the index of the currently focused answer column

                # Tab key handling
                if key == "tab":
                    # Move to next answer and select it
                    selected_ans_col = (selected_ans_col + 1) % len(
                        self.choice_widgets
                    )
                    self._update_selection(selected_ans_col)
                    # Set focus to the newly selected column
                    choices_row = self._wrapped_widget.contents[1][
                        0
                    ]  # Access the Columns widget
                    if isinstance(choices_row, urwid.Columns):
                        choices_row.focus_position = selected_ans_col
                    return None

                # Enter key handling
                if key == "enter":
                    self._update_selection(selected_ans_col)
                    self.confirm_selection()
                    return None
                    # Return None to indicate keypress handled

            else:
                # Enter pressed with nothing selected
                write_to_file(
                    filename="eg.txt", content=f"self={self}", append=True
                )
                return None

        # Handle other keys
        return super().keypress(size, key)

    def _update_selection(self, selected_ans_col):
        """Helper method to update radio button states and selection."""
        for i, widget in enumerate(self.choice_widgets):
            # Iterate over each choice widget (e.g., radio button options) with its index
            radio = widget.contents[0][0].base_widget
            # Extract the actual RadioButton widget from the nested structure

            write_to_file(
                filename="eg.txt",
                content=f"widget={widget},selected_ans_col={selected_ans_col}",
                append=True,
            )
            # Log the current widget and selected answer column for debugging

            if i == selected_ans_col:
                # If this widget corresponds to the selected answer
                radio.set_state(True, do_callback=False)
                # Select it by setting its state to True, without triggering callbacks
                self.selected = radio.label
                # Store the label of the selected radio button as the current selection
            else:
                # For all other radio buttons
                radio.set_state(False, do_callback=False)
                # Ensure they are deselected, without triggering callbacks
