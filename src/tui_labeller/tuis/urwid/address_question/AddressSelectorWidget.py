import urwid
from hledger_preprocessor.TransactionObjects.Receipt import (
    Address,
    ShopId,
)
from urwid import AttrMap, Edit, Filler, LineBox, Pile, Text

from tui_labeller.tuis.urwid.question_data_classes import (
    AddressSelectorQuestionData,
)


class AddressSelectorWidget(urwid.WidgetWrap):
    def __init__(
        self,
        question_data: AddressSelectorQuestionData,
        descriptor_col_width: int,
    ):
        self.question_data = question_data
        self.descriptor_col_width = descriptor_col_width
        self.batch_size = 5
        self.current_batch = 0
        self.mode = "select"  # Modes: "select" or "manual"
        self.manual_answers = []
        self.current_question_idx = 0
        self.selected_shop = None
        self.widget = self.build_select_widget()
        super().__init__(AttrMap(self.widget, "normal"))

    def build_select_widget(self):
        widgets = [Text(("text", self.question_data.question), align="left")]
        start_idx = self.current_batch * self.batch_size
        end_idx = min(
            start_idx + self.batch_size, len(self.question_data.shops)
        )
        for idx, shop in enumerate(
            self.question_data.shops[start_idx:end_idx], 1
        ):
            address_text = shop.to_string()
            border = LineBox(
                Text(("text", address_text), align="left"),
                title=f"{idx}",
                title_attr="number",
                bline="─",
                tline="─",
                lline="│",
                rline="│",
                tlcorner="┌",
                trcorner="┐",
                blcorner="└",
                brcorner="┘",
            )
            widgets.append(AttrMap(border, "border"))
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
        return Filler(Pile(widgets), valign="top")

    def build_manual_widget(self):
        question = self.question_data.manual_questions[
            self.current_question_idx
        ]
        widgets = [
            Text(("text", question.question), align="left"),
            Edit(("input", "> "), multiline=False),
        ]
        return Filler(Pile(widgets), valign="top")

    def handle_input(self, key):
        if self.mode == "select":
            if key in ("1", "2", "3", "4", "5"):
                selection = int(key) - 1
                start_idx = self.current_batch * self.batch_size
                if start_idx + selection < len(self.question_data.shops):
                    self.selected_shop = self.question_data.shops[
                        start_idx + selection
                    ]
                    self._w = AttrMap(self.build_select_widget(), "normal")
                    return True
            elif key == "left" and self.current_batch > 0:
                self.current_batch -= 1
                self._w = AttrMap(self.build_select_widget(), "normal")
            elif key == "right" and (
                self.current_batch + 1
            ) * self.batch_size < len(self.question_data.shops):
                self.current_batch += 1
                self._w = AttrMap(self.build_select_widget(), "normal")
            elif key == "down":
                self.mode = "manual"
                self._w = AttrMap(self.build_manual_widget(), "normal")
        elif self.mode == "manual":
            if key == "enter":
                edit_widget = self._w.base_widget.body.contents[1][0]
                answer = edit_widget.get_edit_text()
                self.manual_answers.append(answer)
                self.current_question_idx += 1
                if self.current_question_idx >= len(
                    self.question_data.manual_questions
                ):
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
                    self._w = AttrMap(self.build_select_widget(), "normal")
                    return True
                else:
                    self._w = AttrMap(self.build_manual_widget(), "normal")
            elif isinstance(key, str) and len(key) == 1:
                edit_widget = self._w.base_widget.body.contents[1][0]
                edit_widget.insert_text(key)
        return False

    def get_edit_text(self):
        return self.selected_shop.to_string() if self.selected_shop else ""

    def update_autocomplete(self):
        pass  # No autocomplete for address selector

    def initalise_autocomplete_suggestions(self):
        pass  # No autocomplete for address selector
