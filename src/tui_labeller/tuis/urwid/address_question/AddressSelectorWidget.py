import logging
import os

import urwid
from hledger_preprocessor.TransactionObjects.Receipt import Address, ShopId
from typeguard import typechecked
from urwid import AttrMap, Button, Columns, Edit, Filler, Pile, Text, WidgetWrap

from tui_labeller.tuis.urwid.question_data_classes import (
    AddressSelectorQuestionData,
)

log_file = os.path.join(os.path.dirname(__file__), "../../../../../log.txt")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    force=True,
)
log = logging.info


class AddressSelectorWidget(WidgetWrap):
    def __init__(
        self,
        question_data: AddressSelectorQuestionData,
        descriptor_col_width: int,
    ):
        """Initialize the AddressSelectorWidget with question data and UI
        settings."""
        self.question_data = question_data
        self.descriptor_col_width = descriptor_col_width
        self.batch_size = 5
        self.current_batch = 0
        self.mode = "select"  # select, manual
        self.manual_answers = [""] * len(self.question_data.manual_questions)
        self.current_question_idx = 0
        self.selected_shop = None
        self.answer_valid = False
        log(f"DEBUG: Number of shops = {len(self.question_data.shops)}")
        for i, shop in enumerate(self.question_data.shops):
            log(f"DEBUG: Shop {i}: {shop.to_string()}")
        self.widget = self.build_widget()
        super().__init__(AttrMap(self.widget, "normal"))

    def build_select_widget(self):
        """Build the widget for selecting a shop from a batch of options."""
        widgets = [Text(("text", self.question_data.question), align="left")]
        start_idx = self.current_batch * self.batch_size
        end_idx = min(
            start_idx + self.batch_size, len(self.question_data.shops)
        )
        for idx, shop in enumerate(
            self.question_data.shops[start_idx:end_idx], 1
        ):
            address_text = shop.to_string()
            button = Button(
                f"{idx}: {address_text}",
                on_press=self.select_shop,
                user_data=shop,
            )
            if self.selected_shop and self.selected_shop == shop:
                widgets.append(
                    AttrMap(
                        button, ("history_suggestions", "light green", "black")
                    )
                )
            else:
                widgets.append(AttrMap(button, "border"))
        return Filler(Pile(widgets), valign="top")

    def build_manual_widget(self):
        """Build the widget for manual shop address entry, displaying all
        questions."""
        widgets = []
        for idx, question in enumerate(self.question_data.manual_questions):
            # Remove extra newlines from question text
            question_text = question.question.strip()
            widgets.append(Text(("text", question_text), align="left"))
            # Use stored answer if available, otherwise empty string
            edit_text = (
                self.manual_answers[idx]
                if idx < len(self.manual_answers)
                else ""
            )
            widgets.append(Edit(("input", "> "), edit_text, multiline=False))
        return Filler(Pile(widgets), valign="top")

    def build_widget(self):
        """Build the main widget with address list on left and manual entry on
        right."""
        select_widget = self.build_select_widget()
        manual_widget = self.build_manual_widget()
        return Columns(
            [("weight", 1, select_widget), ("weight", 1, manual_widget)]
        )

    def select_shop(self, button, shop):
        """Callback for when a shop button is clicked."""
        self.selected_shop = shop
        self.answer_valid = True
        log(f"DEBUG: Button selected shop: {self.selected_shop.to_string()}")
        self._w = AttrMap(self.build_widget(), "normal")

    def handle_input(self, key):
        """Handle user input for shop selection or manual entry."""
        log(
            f"DEBUG: Received key={key!r}, mode={self.mode},"
            f" shops_count={len(self.question_data.shops)},"
            f" focused={self._w.base_widget.focus_position}"
        )

        # Initialize focus on first address entry when coming from previous question
        if self.mode == "select" and self._w.base_widget.focus_position != 0:
            self._w.base_widget.focus_position = 0
            self._w.base_widget.contents[0][0].base_widget.focus_position = (
                1 if len(self.question_data.shops) > 0 else 0
            )

        if self.mode == "select":
            if not self.question_data.shops:
                log("DEBUG: No shops available to select")
                return False
            if key in ("1", "2", "3", "4", "5"):
                selection = int(key) - 1
                start_idx = self.current_batch * self.batch_size
                if start_idx + selection < len(self.question_data.shops):
                    self.selected_shop = self.question_data.shops[
                        start_idx + selection
                    ]
                    self.answer_valid = True
                    log(
                        "DEBUG: Selected shop:"
                        f" {self.selected_shop.to_string()}"
                    )
                    self._w = AttrMap(self.build_widget(), "normal")
                    return True
                else:
                    log(
                        f"DEBUG: Invalid selection: {selection},"
                        f" start_idx={start_idx},"
                        f" max_idx={len(self.question_data.shops)-1}"
                    )
            elif key == "ctrl down":
                if (self.current_batch + 1) * self.batch_size < len(
                    self.question_data.shops
                ):
                    self.current_batch += 1
                    log(
                        "DEBUG: Navigated to next batch,"
                        f" current_batch={self.current_batch}"
                    )
                    self._w = AttrMap(self.build_widget(), "normal")
            elif key in ("n", "right"):
                self.mode = "manual"
                self._w.base_widget.focus_position = 1
                self._w.base_widget.contents[1][
                    0
                ].base_widget.focus_position = 1
                log("DEBUG: Switched to manual mode")
                self._w = AttrMap(self.build_widget(), "normal")
            elif key == "enter":
                if self.answer_valid:
                    pile = self._w.base_widget.contents[0][0].base_widget.body
                    if pile.focus_position > 0:  # Skip question text
                        focused_widget = pile.contents[pile.focus_position][0]
                        if isinstance(focused_widget, AttrMap) and isinstance(
                            focused_widget.base_widget, urwid.Button
                        ):
                            shop = focused_widget.base_widget.user_data
                            self.selected_shop = shop
                            self.answer_valid = True
                            log(
                                "DEBUG: Enter confirmed shop:"
                                f" {self.selected_shop.to_string()}"
                            )
                            self._w = AttrMap(self.build_widget(), "normal")
                            return True
                log("DEBUG: Enter pressed but no valid answer selected")
                return False
            else:
                log(f"DEBUG: Unhandled key in select mode: {key!r}")
        elif self.mode == "manual":
            if key == "enter":
                # Collect all answers
                pile = self._w.base_widget.contents[1][0].base_widget
                answers = []
                all_valid = True
                for idx in range(
                    0, len(pile.contents), 2
                ):  # Step by 2 to skip Text widgets
                    edit_widget = pile.contents[idx + 1][0]
                    answer = edit_widget.get_edit_text().strip()
                    answers.append(answer)
                    if (
                        not answer
                        and self.question_data.manual_questions[
                            idx // 2
                        ].ans_required
                    ):
                        all_valid = False
                if all_valid:
                    self.manual_answers = answers
                    self.selected_shop = ShopId(
                        name=self.manual_answers[0] or "Unknown",
                        address=Address(
                            street=self.manual_answers[1] or None,
                            house_nr=self.manual_answers[2] or None,
                            zipcode=self.manual_answers[3] or None,
                            city=self.manual_answers[4] or None,
                            country=self.manual_answers[5] or None,
                        ),
                    )
                    self.answer_valid = True
                    self.mode = "select"
                    self.current_batch = 0
                    self.manual_answers = [""] * len(
                        self.question_data.manual_questions
                    )
                    self.current_question_idx = 0
                    self._w.base_widget.focus_position = 0
                    log(
                        "DEBUG: Manual input complete, selected shop:"
                        f" {self.selected_shop.to_string()}"
                    )
                    self._w = AttrMap(self.build_widget(), "normal")
                    return True
                else:
                    log("DEBUG: Not all required fields filled")
            elif isinstance(key, str) and len(key) == 1:
                pile = self._w.base_widget.contents[1][0].base_widget
                edit_widget = pile.contents[pile.focus_position][0]
                if isinstance(edit_widget, Edit):
                    edit_widget.insert_text(key)
                    log(f"DEBUG: Inserted text: {key}")
        return False if not self.answer_valid else True

    def get_edit_text(self):
        """Return the string representation of the selected shop."""
        return self.selected_shop.to_string() if self.selected_shop else ""

    def update_autocomplete(self):
        pass  # No autocomplete for address selector

    def initalise_autocomplete_suggestions(self):
        pass  # No autocomplete for address selector

    @typechecked
    def get_answer(self):
        """Return the selected shop ID if valid."""
        return self.selected_shop if self.answer_valid else None
