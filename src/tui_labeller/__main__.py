"""Entry point for the project."""

from argparse import ArgumentParser, Namespace

from tui_labeller.arg_parser.arg_parser import create_arg_parser, verify_args
from tui_labeller.interface_enum import InterfaceMode
from tui_labeller.tuis.cli.questions.ask_receipt import (
    build_receipt_from_cli,
)
from tui_labeller.tuis.urwid.ask_mc_questions import (
    built_receipt_from_urwid,
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
        built_receipt_from_urwid(
            receipt_owner_account_holder="account_placeholder",
            receipt_owner_bank="bank_placeholder",
            receipt_owner_account_holder_type="account_type_placeholder",
        )

    else:
        print(f"Please select a CLI/TUI. You choose:{args.tui.lower()}")
