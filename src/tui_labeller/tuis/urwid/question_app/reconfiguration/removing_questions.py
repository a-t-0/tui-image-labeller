from typing import Any, List, Tuple, Union

from typeguard import typechecked

from tui_labeller.tuis.urwid.QuestionnaireApp import (
    QuestionnaireApp,
)
from tui_labeller.tuis.urwid.receipts.AccountQuestions import AccountQuestions


@typechecked
def remove_later_account_questions(
    *,
    tui: "QuestionnaireApp",
    account_questions: "AccountQuestions",
    start_question_nr: int,
    preserved_answers: List[Union[None, Tuple[str, Any]]],
) -> List[Tuple[str, Any]]:
    """Remove account questions after the given question number, validate
    preserved answers, and update accordingly."""
    # Identify account question identifiers
    account_question_identifiers = {
        q.question for q in account_questions.account_questions
    }

    current_questions = tui.questions  # TODO: switch to tui.inputs?
    # Validate preserved answers against current questions

    for idx, preserved_q_and_a in enumerate(preserved_answers):
        if preserved_q_and_a is not None:
            preserved_question: str = preserved_q_and_a[0]
            preserved_answer: Any = preserved_q_and_a[1]
            if (
                idx < len(current_questions)
                and preserved_question != current_questions[idx].question
            ):
                raise ValueError(
                    f"Preserved answer at index {idx} has question"
                    f" '{preserved_question}' but expected"
                    f" '{current_questions[idx].question}'"
                )

    updated_preserved: List[Tuple[str, Any]] = (
        preserved_answers.copy()
    )  # Create a copy to modify
    non_account_question_found = False

    # Process questions to build remaining_questions.
    offset: int = 0
    original_inputs = tui.inputs.copy()
    for i, input_widget in enumerate(original_inputs):
        widget = input_widget.base_widget
        question_text = widget.question.question

        if i > start_question_nr:
            if question_text not in account_question_identifiers:
                # Non-account question found after start_question_nr
                non_account_question_found = True
            else:
                # Account question after start_question_nr, remove it
                if non_account_question_found:
                    raise ValueError(
                        f"Account question '{question_text}' found "
                        f"after a non-account question at index {i}"
                    )

                if (
                    updated_preserved[i - offset] is not None
                ):  # If the questions are not yet answered, their answers are not stored.

                    if question_text != updated_preserved[i - offset][1]:
                        raise ValueError(
                            f"updated_preserved[i][1] answer at i={i},"
                            f" offset={offset} has question"
                            f" '{updated_preserved[i][1]}' but expected"
                            f" '{question_text}'"
                        )
                print(
                    f"i={i}, offset={offset}, removing"
                    f" question:{question_text} and"
                    f" answer={updated_preserved[i]}"
                )
                updated_preserved.pop(i - offset)
                tui.inputs.pop(i - offset)
                offset += 1

    # tui.inputs = remaining_questions
    if len(tui.inputs) != len(updated_preserved):
        raise ValueError(
            f"Length mismatch: {len(tui.inputs)} remaining questions"
            f" vs {len(updated_preserved)} preserved items"
        )

    # Update answers for remaining questions
    for i, preserved_q_and_a in enumerate(updated_preserved):
        if preserved_q_and_a is not None:
            preserved_question: str = preserved_q_and_a[0]
            preserved_answer: Any = preserved_q_and_a[1]
            if (
                tui.inputs[i].base_widget.question.question
                != preserved_question
            ):
                raise ValueError(
                    "Mismatch in input questions and preserved answers."
                )
            else:
                tui.inputs[i].base_widget.set_answer(preserved_answer)
    return preserved_answers
