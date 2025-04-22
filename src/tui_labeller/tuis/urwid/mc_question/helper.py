from typeguard import typechecked

from tui_labeller.tuis.urwid.question_data_classes import (
    VerticalMultipleChoiceQuestionData,
)


def input_is_in_int_range(
    *, char: str, start: int, ceiling: int, current: str = ""
) -> bool:
    # Validate that the input is a single digit
    if not char.isdigit():
        return False

    # Combine the current input with the new digit
    new_input = current + char

    # If the new input is empty, reject it
    if not new_input:
        return False

    try:
        # Convert the combined input to an integer
        num = int(new_input)
        # Check if the number is within the range [start, ceiling]
        return start <= num < ceiling

    except ValueError:
        return False


@typechecked
def get_selected_caption(
    *,
    mc_question: VerticalMultipleChoiceQuestionData,
    selected_index: int,
    indentation: int,
) -> str:

    @typechecked
    def get_selected_answer(
        *,
        mc_question: VerticalMultipleChoiceQuestionData,
        selected_index: int,
        indentation: int,
    ) -> str:
        max_choice_length = max(len(choice) for choice in mc_question.choices)
        suggestion_text = ""
        for suggestion in mc_question.ai_suggestions:
            if suggestion.question == mc_question.choices[selected_index]:
                # Use fixed-width spacing instead of tabs for consistent rendering
                suggestion_text = (
                    f"{suggestion.probability:.2f} {suggestion.ai_suggestions}"
                )
        # Replace tabs with spaces and ensure consistent indentation
        return (
            f"{' ' * indentation}{selected_index} {mc_question.choices[selected_index]:<{max_choice_length}} "
            f" {suggestion_text}"
        )

    new_caption: str = mc_question.question
    new_caption += (
        f"\n{
        get_selected_answer(
            mc_question=mc_question,
            selected_index=selected_index,
            indentation=indentation,
        )}"
    )

    return f"{new_caption}\n"


def get_mc_question(
    *, mc_question: VerticalMultipleChoiceQuestionData, indentation: int
) -> str:
    result = [mc_question.question]
    max_choice_length = max(len(choice) for choice in mc_question.choices)

    for i, choice in enumerate(mc_question.choices):
        suggestion_text = ""
        for suggestion in mc_question.ai_suggestions:
            if suggestion.question == choice:
                # Use fixed-width spacing instead of tabs for consistent rendering
                suggestion_text = (
                    f"{suggestion.probability:.2f} {suggestion.ai_suggestions}"
                )
        # Replace tabs with spaces and ensure consistent indentation
        line = (
            f"{' ' * indentation}{i} {choice:<{max_choice_length}} "
            f" {suggestion_text}"
        )
        result.append(line)

    options_text: str = "\n".join(result)
    # Ensure the output is clean ASCII to avoid encoding issues
    options_text = options_text.encode("ascii", errors="ignore").decode("ascii")
    return f"\n{options_text}\n"
