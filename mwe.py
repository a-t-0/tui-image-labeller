from dataclasses import dataclass
from typing import List, Optional, Union

import urwid
from typeguard import typechecked
from urwid import AttrMap, Edit, Filler, LineBox, Pile, Text

from src.tui_labeller.tuis.urwid.multiple_choice_question.HorizontalMultipleChoiceWidget import (
    HorizontalMultipleChoiceWidget,
)
from src.tui_labeller.tuis.urwid.multiple_choice_question.VerticalMultipleChoiceWidget import (
    VerticalMultipleChoiceWidget,
)


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
    question_id: Optional[str] = None


@dataclass
class DateQuestionData:
    question: str
    question_id: Optional[str] = None


@dataclass
class VerticalMultipleChoiceQuestionData:
    question: str
    options: list
    question_id: Optional[str] = None


@dataclass
class AddressSelectorQuestionData:
    question: str
    shops: List[ShopId]
    manual_questions: List[InputValidationQuestionData]
    question_id: Optional[str] = None


class InputType:
    LETTERS = "LETTERS"
    LETTERS_AND_SPACE = "LETTERS_AND_SPACE"
    LETTERS_AND_NRS = "LETTERS_AND_NRS"


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


class QuestionnaireApp:
    def __init__(
        self,
        header: str,
        questions: List[
            Union[
                DateQuestionData,
                InputValidationQuestionData,
                VerticalMultipleChoiceQuestionData,
                AddressSelectorQuestionData,
            ]
        ],
    ):
        self.indentation_spaces: int = 1
        self.descriptor_col_width: int = 20
        self.header = header
        self.nr_of_headers: int = len(self.header.splitlines())
        self.palette = [
            ("normal", "white", "black"),
            ("ai_suggestions", "light cyan", "black"),
            ("history_suggestions", "light green", "black"),
            ("error", "light red", "black"),
            ("navigation", "yellow", "black"),
            ("border", "white", "dark blue"),
            ("number", "yellow", "dark blue"),
            ("text", "white", "black"),
            ("input", "light cyan", "black"),
        ]
        self.questions = questions
        self.inputs: List[
            Union[
                urwid.WidgetWrap,
                AttrMap,
            ]
        ] = []  # Added both.
        self.pile = Pile([])
        self.history_store = {}
        self.ai_suggestion_box = AttrMap(
            Text(
                [
                    ("ai_suggestions", "AI Suggestions:\n"),
                    (
                        "normal",
                        f"{self.indentation_spaces*' '}AI Suggestion 1\n",
                    ),
                    (
                        "normal",
                        f"{self.indentation_spaces*' '}AI Suggestion 2\n",
                    ),
                    ("normal", f"{self.indentation_spaces*' '}AI Suggestion 3"),
                ]
            ),
            "ai_suggestions",
        )
        self.history_suggestion_box = AttrMap(
            Text(
                [
                    ("history_suggestions", "History Suggestions:\n"),
                    (
                        "normal",
                        f"{self.indentation_spaces*' '}History Option 1\n",
                    ),
                    (
                        "normal",
                        f"{self.indentation_spaces*' '}History Option 2\n",
                    ),
                    (
                        "normal",
                        f"{self.indentation_spaces*' '}History Option 3",
                    ),
                ]
            ),
            "history_suggestions",
        )
        self.error_display = AttrMap(
            Pile(
                [
                    Text(("normal", "Input Error(s)")),
                    Text(("error", f"{self.indentation_spaces*' '}None")),
                ]
            ),
            "",
        )
        self.navigation_display = AttrMap(
            Pile(
                [
                    Text(("navigation", "Navigation")),
                    Text(f"{self.indentation_spaces*' '}Q          - quit"),
                    Text(
                        f"{self.indentation_spaces*' '}Shift+tab  - previous"
                        " question"
                    ),
                    Text(
                        f"{self.indentation_spaces*' '}Enter      - next"
                        " question"
                    ),
                ]
            ),
            "normal",
        )
        build_questionnaire(
            header=header,
            inputs=self.inputs,
            questions=self.questions,
            descriptor_col_width=self.descriptor_col_width,
            pile=self.pile,
            ai_suggestion_box=self.ai_suggestion_box,
            history_suggestion_box=self.history_suggestion_box,
            error_display=self.error_display,
            history_store=self.history_store,
        )

        screen = urwid.raw_display.Screen()
        term_width, term_height = screen.get_cols_rows()
        section_height = max(3, term_height // 8)
        sidebar_pile = Pile(
            [
                (
                    section_height * 3,
                    Filler(self.navigation_display, valign="top"),
                ),
                (urwid.Divider("─")),
                (section_height, Filler(self.error_display, valign="top")),
                (urwid.Divider("─")),
                (
                    section_height * 2,
                    Filler(self.ai_suggestion_box, valign="top"),
                ),
                (urwid.Divider("─")),
                (
                    section_height * 2,
                    Filler(self.history_suggestion_box, valign="top"),
                ),
            ]
        )
        self.fill = Filler(self.pile, valign="top")
        self.columns = urwid.Columns(
            [
                ("weight", 7, self.fill),
                ("weight", 3, Filler(sidebar_pile, valign="top")),
            ]
        )
        self.loop = urwid.MainLoop(
            self.columns, self.palette, unhandled_input=self._handle_input
        )

    def _move_focus(self, current_pos: int, key: str) -> None:
        nr_of_questions = len(self.questions)
        if not nr_of_questions:
            raise ValueError("Should have questions.")
        if key in ["enter", "down", "tab"]:
            next_pos = (
                0 if current_pos == nr_of_questions - 1 else current_pos + 1
            )
            self.pile.focus_position = next_pos + self.nr_of_headers
        elif key == "up":
            next_pos = (
                nr_of_questions - 1 if current_pos == 0 else current_pos - 1
            )
            self.pile.focus_position = next_pos + self.nr_of_headers
        else:
            raise ValueError(
                f"Unexpected key={key}, current_pos={current_pos}."
            )

    # Till here
    def _handle_input(self, key: str):
        current_pos = self.pile.focus_position - self.nr_of_headers
        if key in ("enter", "down", "tab", "up"):
            if current_pos >= 0:
                focused_widget = self.inputs[current_pos].base_widget
                if isinstance(focused_widget, AddressSelectorWidget):
                    if focused_widget.handle_input(key):
                        self._move_focus(current_pos, key)
                else:
                    self._move_focus(current_pos, key)
        elif key == "q":
            self._save_results()
            raise urwid.ExitMainLoop()
        elif key == "next_question":
            if (
                self.pile.focus_position
                < len(self.questions) + self.nr_of_headers - 1
            ):
                self.pile.focus_position += 1
            else:
                self.pile.focus_position = self.nr_of_headers
        elif key == "previous_question":
            if self.pile.focus_position > self.nr_of_headers:
                self.pile.focus_position -= 1
            else:
                self._move_focus(current_pos=current_pos, key="up")
        if current_pos >= 0:
            focused_widget = self.inputs[current_pos].base_widget
            if not isinstance(
                focused_widget,
                (
                    VerticalMultipleChoiceWidget,
                    HorizontalMultipleChoiceWidget,
                    AddressSelectorWidget,
                ),
            ):
                focused_widget.update_autocomplete()

    def _save_results(self):
        results = {}
        for i, input_widget in enumerate(self.inputs):
            question_id = self.questions[i].question_id
            results[question_id] = input_widget.base_widget.get_edit_text()
        write_to_file("results.txt", str(results), append=True)

    @typechecked
    def run(self, alternative_start_pos: Optional[int] = None) -> None:
        if self.inputs:
            if alternative_start_pos is None:
                self.pile.focus_position = self.nr_of_headers
            else:
                self.pile.focus_position = (
                    alternative_start_pos + self.nr_of_headers
                )
            if not isinstance(
                self.inputs[0].base_widget,
                (VerticalMultipleChoiceWidget, HorizontalMultipleChoiceWidget),
            ):
                self.inputs[0].base_widget.initalise_autocomplete_suggestions()
        self.loop.run()

    @typechecked
    def set_focus(self, target_position: int) -> None:
        if 0 <= target_position < len(self.questions):
            self.pile.focus_position = target_position + self.nr_of_headers
        else:
            raise ValueError(f"Invalid focus position: {target_position}")

    @typechecked
    def get_focus(self) -> int:
        return self.pile.focus_position - self.nr_of_headers


# TIll here
def build_questionnaire(
    header: str,
    inputs: List,
    questions: List,
    descriptor_col_width: int,
    pile: Pile,
    ai_suggestion_box: AttrMap,
    history_suggestion_box: AttrMap,
    error_display: AttrMap,
    history_store: dict,
):
    pile.contents = [(Text(header), ("pack", None))]
    for i, question in enumerate(questions):
        if isinstance(question, InputValidationQuestionData):
            widget = AttrMap(Edit(question.question), "normal")
            inputs.append(widget)
            pile.contents.append((widget, ("pack", None)))
        elif isinstance(question, AddressSelectorQuestionData):
            widget = AddressSelectorWidget(question, descriptor_col_width)
            inputs.append(AttrMap(widget, "normal"))
            pile.contents.append((inputs[-1], ("pack", None)))
        else:
            raise NotImplementedError(
                f"Question type {type(question)} not supported"
            )


if __name__ == "__main__":
    questions = [
        AddressSelectorQuestionData(
            question="Select Shop Address:\n",
            shops=[
                ShopId(
                    "Shop A",
                    Address("Main St", "123", "12345", "CityA", "CountryA"),
                ),
                ShopId(
                    "Shop B",
                    Address("Broadway", "45", "67890", "CityB", "CountryB"),
                ),
                ShopId(
                    "Shop C",
                    Address("Elm St", "67a", "11111", "CityC", "CountryC"),
                ),
                ShopId(
                    "Shop D",
                    Address("Oak Ave", "89", "22222", "CityD", "CountryD"),
                ),
                ShopId(
                    "Shop E",
                    Address("Pine Rd", "12", "33333", "CityE", "CountryE"),
                ),
                ShopId(
                    "Shop F",
                    Address("Cedar Ln", "34", "44444", "CityF", "CountryF"),
                ),
                ShopId(
                    "Shop G",
                    Address("Maple Dr", "56", "55555", "CityG", "CountryG"),
                ),
            ],
            manual_questions=[
                InputValidationQuestionData(
                    question="\nShop name:\n",
                    input_type=InputType.LETTERS,
                    ai_suggestions=[],
                    history_suggestions=[],
                    ans_required=False,
                    reconfigurer=False,
                    terminator=False,
                    question_id="shop_name",
                ),
                InputValidationQuestionData(
                    question="Shop street:",
                    input_type=InputType.LETTERS_AND_SPACE,
                    ai_suggestions=[],
                    history_suggestions=[],
                    ans_required=False,
                    reconfigurer=False,
                    terminator=False,
                    question_id="shop_street",
                ),
                InputValidationQuestionData(
                    question="Shop house nr.:",
                    input_type=InputType.LETTERS_AND_NRS,
                    ai_suggestions=[],
                    history_suggestions=[],
                    ans_required=False,
                    reconfigurer=False,
                    terminator=False,
                    question_id="shop_house_nr",
                ),
                InputValidationQuestionData(
                    question="Shop zipcode:",
                    input_type=InputType.LETTERS_AND_NRS,
                    ai_suggestions=[],
                    history_suggestions=[],
                    ans_required=False,
                    reconfigurer=False,
                    terminator=False,
                    question_id="shop_zipcode",
                ),
                InputValidationQuestionData(
                    question="Shop City:",
                    input_type=InputType.LETTERS,
                    ai_suggestions=[],
                    history_suggestions=[],
                    ans_required=False,
                    reconfigurer=False,
                    terminator=False,
                    question_id="shop_city",
                ),
                InputValidationQuestionData(
                    question="Shop country:",
                    input_type=InputType.LETTERS,
                    ai_suggestions=[],
                    history_suggestions=[],
                    ans_required=False,
                    reconfigurer=False,
                    terminator=False,
                    question_id="shop_country",
                ),
            ],
            question_id="address_selector",
        ),
    ]
    app = QuestionnaireApp(header="Receipt Labeller", questions=questions)
    app.run()
