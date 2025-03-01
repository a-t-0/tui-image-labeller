"""Parses the CLI args."""

import argparse
import os
from argparse import ArgumentParser, Namespace

from hledger_preprocessor.dir_reading_and_writing import assert_dir_exists
from typeguard import typechecked

from tui_labeller.interface_enum import InterfaceMode


@typechecked
def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate labels for images using CLI/TUI."
    )

    # Required args.
    parser.add_argument(
        "-i",
        "--image-path",
        type=str,
        required=True,
        help="Path to an image.",
    )
    parser.add_argument(
        "-t",
        "--tui",
        type=str,
        required=True,
        help="Which TUI you would like to use for labelling.",
    )
    parser.add_argument(
        "-o",
        "--output-json-dir",
        type=str,
        required=True,
        help="Where your output json will be stored.",
    )

    return parser


@typechecked
def assert_file_exists(*, filepath: str) -> None:
    """Asserts that the given file exists.

    Args:
      filepath: The path to the file.

    Raises:
      FileNotFoundError: If the file does not exist.
    """

    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File '{filepath}' does not exist.")


@typechecked
def assert_dir_exists(*, dirpath: str) -> None:
    """Asserts that the given directory exists.

    Args:
      dirpath: The path to the directory.

    Raises:
      FileNotFoundError: If the directory does not exist.
    """

    if not os.path.isdir(dirpath):
        raise FileNotFoundError(f"Directory '{dirpath}' does not exist.")


@typechecked
def validate_tui(*, tui_arg: str) -> None:
    try:
        InterfaceMode(tui_arg.lower())  # Try to create an Enum member
    except ValueError:
        raise NotImplementedError(f"That TUI '{tui_arg}' is not supported.")


@typechecked
def verify_args(*, parser: ArgumentParser) -> Namespace:
    args: Namespace = parser.parse_args()

    # Verify output directory for jsons exist.
    assert_dir_exists(dirpath=args.output_json_dir)

    # Verify the input image exists.
    assert_file_exists(filepath=args.image_path)

    # Verify the chosen TUI method is supported.
    validate_tui(tui_arg=args.tui)

    return args
