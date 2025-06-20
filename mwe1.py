from dataclasses import dataclass
from typing import Optional

import urwid


@dataclass
class Address:
    street: Optional[str] = None
    house_nr: Optional[str] = None
    zipcode: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

    def to_string(self) -> str:
        parts = [
            self.street or "",
            self.house_nr or "",
            self.zipcode or "",
            self.city or "",
            self.country or "",
        ]
        return ", ".join(part for part in parts if part)


@dataclass
class ShopId:
    name: str
    address: Address
    shop_account_nr: Optional[str] = None

    def to_string(self) -> str:
        return f"{self.name} - {self.address.to_string()}"


@dataclass
class InputValidationQuestionData:
    question: str
    input_type: str
    ai_suggestions: list
    history_suggestions: list
    ans_required: bool
    reconfigurer: bool
    terminator: bool


class InputType:
    LETTERS = "LETTERS"
    LETTERS_AND_SPACE = "LETTERS_AND_SPACE"
    LETTERS_AND_NRS = "LETTERS_AND_NRS"


class AddressSelector:
    def __init__(self):
        self.shops = [
            ShopId(
                "Shop A",
                Address("Main St", "123", "12345", "CityA", "CountryA"),
            ),
            ShopId(
                "Shop B",
                Address("Broadway", "45", "67890", "CityB", "CountryB"),
            ),
            ShopId(
                "Shop C", Address("Elm St", "67a", "11111", "CityC", "CountryC")
            ),
            ShopId(
                "Shop D", Address("Oak Ave", "89", "22222", "CityD", "CountryD")
            ),
            ShopId(
                "Shop E", Address("Pine Rd", "12", "33333", "CityE", "CountryE")
            ),
            ShopId(
                "Shop F",
                Address("Cedar Ln", "34", "44444", "CityF", "CountryF"),
            ),
            ShopId(
                "Shop G",
                Address("Maple Dr", "56", "55555", "CityG", "CountryG"),
            ),
        ]
        self.batch_size = 5
        self.current_batch = 0
        self.mode = "select"  # Modes: "select" or "manual"
        self.manual_answers = []
        self.current_question_idx = 0
        self.questions = self.create_base_questions()
        self.palette = [
            ("border", "white", "dark blue"),
            ("number", "yellow", "dark blue"),
            ("text", "white", "black"),
            ("input", "light cyan", "black"),
        ]
        self.main_widget = self.build_select_widget()
        self.loop = urwid.MainLoop(
            self.main_widget, self.palette, unhandled_input=self.handle_input
        )

    def create_base_questions(self):
        return [
            InputValidationQuestionData(
                question="\nShop name:\n",
                input_type=InputType.LETTERS,
                ai_suggestions=[],
                history_suggestions=[],
                ans_required=False,
                reconfigurer=False,
                terminator=False,
            ),
            InputValidationQuestionData(
                question="Shop street:",
                input_type=InputType.LETTERS_AND_SPACE,
                ai_suggestions=[],
                history_suggestions=[],
                ans_required=False,
                reconfigurer=False,
                terminator=False,
            ),
            InputValidationQuestionData(
                question="Shop house nr.:",
                input_type=InputType.LETTERS_AND_NRS,
                ai_suggestions=[],
                history_suggestions=[],
                ans_required=False,
                reconfigurer=False,
                terminator=False,
            ),
            InputValidationQuestionData(
                question="Shop zipcode:",
                input_type=InputType.LETTERS_AND_NRS,
                ai_suggestions=[],
                history_suggestions=[],
                ans_required=False,
                reconfigurer=False,
                terminator=False,
            ),
            InputValidationQuestionData(
                question="Shop City:",
                input_type=InputType.LETTERS,
                ai_suggestions=[],
                history_suggestions=[],
                ans_required=False,
                reconfigurer=False,
                terminator=False,
            ),
            InputValidationQuestionData(
                question="Shop country:",
                input_type=InputType.LETTERS,
                ai_suggestions=[],
                history_suggestions=[],
                ans_required=False,
                reconfigurer=False,
                terminator=False,
            ),
        ]

    def build_select_widget(self):
        widgets = []
        start_idx = self.current_batch * self.batch_size
        end_idx = min(start_idx + self.batch_size, len(self.shops))
        for idx, shop in enumerate(self.shops[start_idx:end_idx], 1):
            address_text = shop.to_string()
            border = urwid.LineBox(
                urwid.Text(("text", address_text), align="left"),
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
            attr_border = urwid.AttrMap(border, "border")
            widgets.append(attr_border)
        instructions = urwid.Text(
            (
                "text",
                (
                    "\nUse 1-5 to select, Left/Right to scroll, Down for manual"
                    " entry, 'q' to quit"
                ),
            ),
            align="center",
        )
        pile = urwid.Pile(widgets + [instructions])
        return urwid.Filler(pile, valign="top")

    def build_manual_widget(self):
        question = self.questions[self.current_question_idx]
        widgets = [
            urwid.Text(("text", question.question), align="left"),
            urwid.Edit(("input", "> "), multiline=False),
        ]
        pile = urwid.Pile(widgets)
        return urwid.Filler(pile, valign="top")

    def handle_input(self, key):
        if key == "q":
            raise urwid.ExitMainLoop()
        if self.mode == "select":
            if key in ("1", "2", "3", "4", "5"):
                selection = int(key) - 1
                start_idx = self.current_batch * self.batch_size
                if start_idx + selection < len(self.shops):
                    selected_shop = self.shops[start_idx + selection]
                    print(f"Selected: {selected_shop.to_string()}")
                    raise urwid.ExitMainLoop()
            elif key == "left" and self.current_batch > 0:
                self.current_batch -= 1
                self.main_widget = self.build_select_widget()
                self.loop.widget = self.main_widget
            elif key == "right" and (
                self.current_batch + 1
            ) * self.batch_size < len(self.shops):
                self.current_batch += 1
                self.main_widget = self.build_select_widget()
                self.loop.widget = self.main_widget
            elif key == "down":
                self.mode = "manual"
                self.main_widget = self.build_manual_widget()
                self.loop.widget = self.main_widget
        elif self.mode == "manual":
            if key == "enter":
                edit_widget = self.main_widget.body.contents[1][0]
                answer = edit_widget.get_edit_text()
                self.manual_answers.append(answer)
                self.current_question_idx += 1
                if self.current_question_idx >= len(self.questions):
                    shop = ShopId(
                        name=self.manual_answers[0] or "Unknown",
                        address=Address(
                            street=self.manual_answers[1] or None,
                            house_nr=self.manual_answers[2] or None,
                            zipcode=self.manual_answers[3] or None,
                            city=self.manual_answers[4] or None,
                            country=self.manual_answers[5] or None,
                        ),
                    )
                    print(f"Manual entry: {shop.to_string()}")
                    raise urwid.ExitMainLoop()
                else:
                    self.main_widget = self.build_manual_widget()
                    self.loop.widget = self.main_widget
            elif isinstance(key, str) and len(key) == 1:
                edit_widget = self.main_widget.body.contents[1][0]
                edit_widget.insert_text(key)

    def run(self):
        self.loop.run()


if __name__ == "__main__":
    selector = AddressSelector()
    selector.run()
