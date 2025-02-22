"""Entry point for the project."""

from argparse import ArgumentParser, Namespace

from src.tui_labeller.tuis.cli.questions.ask_receipt import (
    build_receipt_from_cli,
)
from tui_labeller.arg_parser.arg_parser import create_arg_parser, verify_args

parser: ArgumentParser = create_arg_parser()
args: Namespace = verify_args(parser=parser)


if __name__ == "__main__":
    input("hi")
    if args.tui == "CLI":

        build_receipt_from_cli(
            receipt_owner_account_holder="account_placeholder",
            receipt_owner_bank="bank_placeholder",
            receipt_owner_account_holder_type="account_type_placeholder",
        )
