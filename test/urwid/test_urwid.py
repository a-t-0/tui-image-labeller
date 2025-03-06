"""Tests whether the script correctly handles multiline arguments and verifies
directory structure."""

import os
import tempfile
import unittest
import uuid
from io import StringIO
from unittest.mock import patch

from typeguard import typechecked

from tui_labeller.tuis.urwid.input_validated_question import (
    ask_input_validated_question,
)


class Test_script_with_multiline_args(unittest.TestCase):
    """Object used to test a script handling multiline arguments and directory
    verification."""

    # Initialize test object
    @typechecked
    def __init__(self, *args, **kwargs):  # type:ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self.existent_tmp_dir: str = tempfile.mkdtemp()
        self.nonexistant_tmp_dir: str = self.get_random_nonexistent_dir()

    @typechecked
    def get_random_nonexistent_dir(
        self,
    ) -> str:
        """Generates and returns a random directory path that does not
        exist."""
        random_dir = f"/tmp/{uuid.uuid4()}"
        while os.path.exists(random_dir):
            random_dir = f"/tmp/{uuid.uuid4()}"
        return random_dir

    def test_multiline_args_and_dirs(self):

        cli_args = [
            "tui_labeller_filler_name_to_skip_script_at_arg[0]",  # Dummy program name
            "--image-path",
            "images/receipts/0.jpg",
            f"{self.existent_tmp_dir}",
            "--output-json-dir",
            "test/test_jsons/--tui",
            "urwid",
        ]

        # python -m src.tui_labeller -i /home/a/finance/a-t-0/receipt/20250112_114733.jpg -o $PWD/.. -t urwid
        print(f"self.existent_tmp_dir={self.existent_tmp_dir}")

        first_char: str = "a"
        second_char: str = "*"
        third_char: str = "t"

        # Simulate user input for `ask_user_for_starting_info(..)`
        user_input = StringIO(
            f"{first_char}\n" + f"{second_char}\n" + f"{third_char}\n"
        )

        with patch("sys.argv", cli_args), patch("sys.stdin", user_input):
            # main()
            ask_input_validated_question()
