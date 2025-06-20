import urwid
from hledger_preprocessor.TransactionObjects.Receipt import Address, ShopId
from typeguard import typechecked
from urwid import AttrMap, Button, Edit, Filler, Pile, Text

from tui_labeller.tuis.urwid.question_data_classes import (
    AddressSelectorQuestionData,
)


class AddressSelectorWidget(urwid.WidgetWrap):
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
        self.mode = "select"
        self.manual_answers = []
        self.current_question_idx = 0
        self.selected_shop = None
        print(f"DEBUG: Number of shops = {len(self.question_data.shops)}")
        for i, shop in enumerate(self.question_data.shops):
            print(f"DEBUG: Shop {i}: {shop.to_string()}")
        self.widget = self.build_select_widget()
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
        instructions = Text(
            (
                "text",
                (
                    "\nUse 1-5 to select, Left/Right to scroll, Down for manual"
                    " entry"
                ),
            ),
            align="center",
        )
        widgets.append(instructions)
        pile = Pile(widgets)
        pile.focus_position = 1 if len(widgets) > 1 else 0
        return Filler(pile, valign="top")

    def select_shop(self, button, shop):
        """Callback for when a shop button is clicked."""
        self.selected_shop = shop
        print(f"DEBUG: Button selected shop: {self.selected_shop.to_string()}")
        self._w = AttrMap(self.build_select_widget(), "normal")

    def build_manual_widget(self):
        """Build the widget for manual shop address entry."""
        question = self.question_data.manual_questions[
            self.current_question_idx
        ]
        widgets = [
            Text(("text", question.question), align="left"),
            Edit(("input", "> "), multiline=False),
        ]
        return Filler(Pile(widgets), valign="top")

    def handle_input(self, key):
        """Handle user input for shop selection or manual entry."""
        print(f"DEBUG: Received key={key!r}, mode={self.mode}, shops_count={len(self.question_data.shops)}, focused={self._w.base_widget.focus_position}")
        
        if self.mode == "select":
            if not self.question_data.shops:
                print("DEBUG: No shops available to select")
                return False
            
            # Handle number keys (1–5) for direct selection
            if key in ("1", "2", "3", "4", "5"):
                selection = int(key) - 1
                start_idx = self.current_batch * self.batch_size
                if start_idx + selection < len(self.question_data.shops):
                    self.selected_shop = self.question_data.shops[start_idx + selection]
                    print(f"DEBUG: Selected shop: {self.selected_shop.to_string()}")
                    self._w = AttrMap(self.build_select_widget(), "normal")
                    return True
                else:
                    print(f"DEBUG: Invalid selection: {selection}, start_idx={start_idx}, max_idx={len(self.question_data.shops)-1}")
                    return False
            
            # Handle navigation keys
            elif key == "left" and self.current_batch > 0:
                self.current_batch -= 1
                print(f"DEBUG: Navigated left, current_batch={self.current_batch}")
                self._w = AttrMap(self.build_select_widget(), "normal")
                return False
            elif key == "right" and (self.current_batch + 1) * self.batch_size < len(self.question_data.shops):
                self.current_batch += 1
                print(f"DEBUG: Navigated right, current_batch={self.current_batch}")
                self._w = AttrMap(self.build_select_widget(), "normal")
                return False
            elif key == "down":
                self.mode = "manual"
                print("DEBUG: Switched to manual mode")
                self._w = AttrMap(self.build_manual_widget(), "normal")
                return False
            elif key == "enter":
                pile = self._w.base_widget.body
                if pile.focus_position > 0:
                    focused_widget = pile.contents[pile.focus_position][0]
                    if isinstance(focused_widget, AttrMap) and isinstance(focused_widget.base_widget, urwid.Button):
                        shop = focused_widget.base_widget.user_data
                        self.selected_shop = shop
                        print(f"DEBUG: Enter confirmed shop: {self.selected_shop.to_string()}")
                        self._w = AttrMap(self.build_select_widget(), "normal")
                        return True
                print("DEBUG: Enter pressed but no shop focused or selected")
                return False
            else:
                print(f"DEBUG: Unhandled key in select mode: {key!r}")
                return False
        
        elif self.mode == "manual":
            if key == "enter":
                edit_widget = self._w.base_widget.body.contents[1][0]
                answer = edit_widget.get_edit_text()
                self.manual_answers.append(answer)
                self.current_question_idx += 1
                if self.current_question_idx >= len(self.question_data.manual_questions):
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
                    self.mode = "select"
                    self.current_batch = 0
                    self.manual_answers = []
                    self.current_question_idx = 0
                    print(f"DEBUG: Manual input complete, selected shop: {self.selected_shop.to_string()}")
                    self._w = AttrMap(self.build_select_widget(), "normal")
                    return True
                else:
                    print(f"DEBUG: Next manual question: {self.current_question_idx}")
                    self._w = AttrMap(self.build_manual_widget(), "normal")
                    return False
            elif isinstance(key, str) and len(key) == 1:
                edit_widget = self._w.base_widget.body.contents[1][0]
                edit_widget.insert_text(key)
                print(f"DEBUG: Inserted text: {key}")
                return False
        
        print(f"DEBUG: Unhandled key outside modes: {key!r}")
        return False

    def get_edit_text(self):
        """Return the string representation of the selected shop."""
        return self.selected_shop.to_string() if self.selected_shop else ""

    def update_autocomplete(self):
        pass  # No autocomplete for address selector

    def initalise_autocomplete_suggestions(self):
        pass  # No autocomplete for address selector

    @typechecked
    def get_answer(self):
        """Return the selected shop ID."""
        return self.selected_shop if self.selected_shop else None
