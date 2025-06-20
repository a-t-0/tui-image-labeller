from hledger_preprocessor.TransactionObjects.Receipt import (
    Address,
    ShopId,
)

from tui_labeller.tuis.urwid.input_validation.InputType import InputType
from tui_labeller.tuis.urwid.question_data_classes import (
    AddressSelectorQuestionData,
    HorizontalMultipleChoiceQuestionData,
    InputValidationQuestionData,
)


class OptionalQuestions:
    def __init__(
        self,
    ):
        self.optional_questions = self.create_base_questions()
        self.verify_unique_questions(self.optional_questions)

    def create_base_questions(self):
        return [
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
                input_type=InputType.LETTERS_AND_NRS,  # TODO: allow 37a
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
            InputValidationQuestionData(
                question="\nSubtotal (Optional, press enter to skip):\n",
                input_type=InputType.FLOAT,
                ai_suggestions=[],
                history_suggestions=[],
                ans_required=False,
                reconfigurer=False,
                terminator=False,
            ),
            InputValidationQuestionData(
                question="\nTotal tax (Optional, press enter to skip):\n",
                input_type=InputType.FLOAT,
                ai_suggestions=[],
                history_suggestions=[],
                ans_required=False,
                reconfigurer=False,
                terminator=False,
            ),
            HorizontalMultipleChoiceQuestionData(
                question="\nDone with this receipt?",
                choices=["yes"],
                ai_suggestions=[],
                ans_required=True,
                reconfigurer=False,
                terminator=True,
            ),
        ]

    def verify_unique_questions(self, questions):
        seen = set()
        for q in questions:
            question = getattr(q, "question", getattr(q, "question", None))
            if question is None:
                raise ValueError("Question object missing question/question")
            if question in seen:
                raise ValueError(f"Duplicate question question: '{question}'")
            seen.add(question)

    def get_is_done_question_identifier(self) -> str:
        return self.optional_questions[-1].question
