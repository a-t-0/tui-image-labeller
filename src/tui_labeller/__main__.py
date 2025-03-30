"""Entry point for the project."""

from argparse import ArgumentParser, Namespace

from tui_labeller.arg_parser.arg_parser import create_arg_parser, verify_args
from tui_labeller.interface_enum import InterfaceMode
from tui_labeller.tuis.cli.questions.ask_receipt import (
    build_receipt_from_cli,
)
from tui_labeller.tuis.urwid.ask_urwid_receipt import build_receipt_from_urwid
from tui_labeller.tuis.urwid.input_validation.InputType import InputType
from tui_labeller.tuis.urwid.merged_questions import (
    create_and_run_questionnaire,
)
from tui_labeller.tuis.urwid.question_data_classes import (
    AISuggestion,
    DateQuestionData,
    HistorySuggestion,
    InputValidationQuestionData,
    MultipleChoiceQuestionData,
)

parser: ArgumentParser = create_arg_parser()
args: Namespace = verify_args(parser=parser)


if __name__ == "__main__":

    if args.tui.lower() == InterfaceMode.CLI.value:

        build_receipt_from_cli(
            receipt_owner_account_holder="account_placeholder",
            receipt_owner_bank="bank_placeholder",
            receipt_owner_account_holder_type="account_type_placeholder",
        )
    elif args.tui.lower() == InterfaceMode.URWID.value:
        build_receipt_from_urwid(
            receipt_owner_account_holder="account_placeholder",
            receipt_owner_bank="bank_placeholder",
            receipt_owner_account_holder_type="account_type_placeholder",
        )

        questions = [
            DateQuestionData(
                "Date: ",
                True,
                [
                    AISuggestion("2025-03-17", 0.95, "DatePredictorV1"),
                    AISuggestion("5025-03-18", 0.85, "DatePredictorV1"),
                    AISuggestion("6025-03-16", 0.75, "DatePredictorV2"),
                ],
            ),
            InputValidationQuestionData(
                question="Fruit: ",
                input_type=InputType.LETTERS,
                ans_required=True,
                ai_suggestions=[
                    AISuggestion("apple", 0.9, "FruitNet"),
                    AISuggestion("banana", 0.85, "FruitNet"),
                    AISuggestion("forest", 0.6, "TypoCorrector"),
                ],
                history_suggestions=[
                    HistorySuggestion("pear", 5),
                    HistorySuggestion("peach", 3),
                    HistorySuggestion("apple", 2),
                ],
            ),
            MultipleChoiceQuestionData(
                question="Capital of France?",
                choices=["Paris", "London", "Lutjebroek"],
                ai_suggestions=[
                    AISuggestion("Paris", 0.99, "GeoAI"),
                    AISuggestion("London", 0.1, "GeoAI"),
                    AISuggestion("Paris", 0.97, "HistoryBot"),
                ],
            ),
            DateQuestionData(
                "DateTime: ",
                False,
                [
                    AISuggestion("2025-03-17 14:30", 0.92, "TimeMaster"),
                    AISuggestion("2025-03-17 09:00", 0.88, "TimeMaster"),
                    AISuggestion("2025-03-18 12:00", 0.80, "ChronoAI"),
                ],
            ),
        ]
        create_and_run_questionnaire(
            questions=questions, header="Example diverse questions."
        )

    else:
        print(f"Please select a CLI/TUI. You choose:{args.tui.lower()}")
