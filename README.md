# Python Repository Template

[![Python 3.12][python_badge]](https://www.python.org/downloads/release/python-3120/)
[![License: AGPL v3][agpl3_badge]](https://www.gnu.org/licenses/agpl-3.0)
[![Code Style: Black][black_badge]](https://github.com/ambv/black)

Example Python repository to quickly fork into new clean environment.

- typechecking
- pre-commit

## Usage

First install this pip package with:

```bash
pip install tui-labeller
```

Then run:

```sh
python -m tui_labeller
```

## Tests

```sh
python -m pytest
```

## UI specification

The user interface (UI) supports 3 types of questions:

- multiple choice questions (mc).
- questions with input validation (iv).
- questions that ask for a date (date).

### Autocomplete

There are two boxes with autocomplete suggestions:

- AI suggestions
- Past input/history suggestions
  The remaining options are automatically filterd, and if only one option is left (in total accros the 2 suggestion types), it can be applied by pressing `tab`.
  If multiple options are left the first option can be applied with:
- `Alt+tab` for the first (if any remaining) AI suggestion
- `Ctrl+tab` for the first (if any remaining) past entries/history suggestion
  The autocomplete can be filtered using `a*d` to match on `avocad(o)`.

### Navigation

One can navigate within question answer boxes, and amongst question answer boxes.

- Going to the end of a question and beyond means going to the next question.

- Going to the start of a question and further back/left means going to the previous question.

- Going beyond the last question moves to the start of the first question.

- Going back from the first question means going to the end of the last question.

#### Navigation: Tab

To navigate between the types of questions the following keys can be used, which behave context dependent:
`tab`:

- for input validation questions: see autocomplete. (`Shift+tab` moves to the previous question.)
- for date questions: move to next segment in terms of `yyyy`-`mm`-`dd` or to the next question if at segment `dd`(shift+tab moves to the previous segment or to the previous question if at `yyyy`.)
- for multiple choice: selects the next option, or moves to the next question if the last option is selected. (`shift+tab` moves to previous question if first option is selected).

#### Navigation: enter

Enter is used to select the current answer and move to the next question.
shift enter

#### Navigation: Enter

`Enter` is used to select the current answer and move to the next question.
`Shift+Enter` is used to select the current answer and move to the previous question, maintaining the symmetry of navigation flow.

#### Navigation: Home, End

- `Home`: Moves the cursor to the start of the current question’s input field. If already at the start, moves to the first question in the form.
- `End`: Moves the cursor to the end of the current question’s input field. If already at the end, moves to the last question in the form.

#### Navigation: Up, Down

- For multiple choice: `Up` moves to the previous question, `Down` moves to the next question. If at the first question, `Up` wraps to the last question; if at the last question, `Down` wraps to the first question.
- For input validation: `Up` moves to the previous question, `Down` moves to the next question. If at the first question, `Up` wraps to the last question; if at the last question, `Down` wraps to the first question.
- For date questions: `Up` rolls the current digit/segment (e.g., `yyyy`, `mm`, `dd`) upward (increments), `Down` rolls it downward (decrements). Wrapping occurs at the segment’s valid range (e.g., 1-12 for `mm`). ((shift+)Enter moves to (previous/)next question).

#### Navigation: Left, Right

- For multiple choice: `Left` selects the previous answer option, `Right` selects the next answer option. If at the first option, `Left` means go to previous question; if at the last option, `Right` means go to next question.
- For input validation: `Left` moves the cursor one character left within the input field, `Right` moves one character right. If at the start, `Left` moves to the previous question; if at the end, `Right` moves to the next question.
- For date questions: `Left` moves the cursor to the previous cursor by one digit to the left, `Right` moves the cursor to next digitIf at `Y` of `Yyyy`, `Left` moves to the previous question; if at `D` of`dD`, `Right` moves to the next question.

#### Navigation: Ctrl+Left, Ctrl+Right, Alt+Left, Alt+Right

- `Ctrl+Left` and `Ctrl+Right`: Scroll through history suggestions for autocomplete. `Ctrl+Left` moves to the previous history suggestion, `Ctrl+Right` moves to the next history suggestion. If no more suggestions, it stops.
- `Alt+Left` and `Alt+Right`: Scroll through AI suggestions for autocomplete. `Alt+Left` moves to the previous AI suggestion, `Alt+Right` moves to the next AI suggestion. If no more suggestions, it stops.

## Developer

```bash
conda env create --file environment.yml
conda activate tui-labeller

pre-commit install
pre-commit autoupdate
pre-commit run --all
```

## Publish pip package

Install the pip package locally with:

```bash
rm -r build
python -m build
pip install -e .
```

Upload the pip package to the world with:

```bash
rm -r build
python -m build
python3 -m twine upload dist/\*
```

## Sphinx documentation

To generate the documentation ensure the pip package is installed locally, such
that the documentation is able to import its Python files.

```bash
rm -r build
python -m build
pip install -e .
```

Then build the documentation with::

```sh
cd docs
make html
```

You can now see all your auto-generated Sphinx documentation in:
[docs/build/html/index.html](docs/build/html/index.html). This repository
auto-generates the Sphinx documentation for all your Python files using the
[/docs/source/conf.py](/docs/source/conf.py) file.

### Additional manual documentation

- The [docs/source/index.rst](docs/source/index.rst) is autogenerated and
  contains the main page and documentation file-structure.
- You can also add additional manual documentation in Markdown format as files in:

```
docs/source/manual_documenation/your_manual_documentation_filename.md
docs/source/manual_documenation/another_manual_documentation_filename.md
```

and then adding those filepaths into the `docs/source/manual.rst` file like:

```rst
Handwritten Documentation
=========================
.. toctree::
   :maxdepth: 2

   manual_documenation/your_manual_documentation_filename.md
   another_manual_documentation_filename.md
```

<!-- Un-wrapped URL's below (Mostly for Badges) -->

[agpl3_badge]: https://img.shields.io/badge/License-AGPL_v3-blue.svg
[black_badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[python_badge]: https://img.shields.io/badge/python-3.6-blue.svg
