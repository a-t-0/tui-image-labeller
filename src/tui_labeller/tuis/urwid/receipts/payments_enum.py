from enum import Enum


class PaymentTypes(Enum):
    CASH = "cash"
    CARD = "card"
    BOTH = "both"
    OTHER = "other"


from enum import Enum

from typeguard import typechecked


class PaymentTypes(Enum):
    CASH = "cash"
    CARD = "card"
    BOTH = "both"
    OTHER = "other"


@typechecked
def str_to_payment_type(*, value: str) -> PaymentTypes:
    """Convert a string to a PaymentTypes enum member.

    Args:
        value: The string to cast (e.g., "cash", "card").

    Returns:
        PaymentTypes: The corresponding PaymentTypes enum member.

    Raises:
        ValueError: If the string does not match any PaymentTypes value.
    """
    try:
        # Directly use the Enum class to look up the value
        return PaymentTypes(value)
    except ValueError:
        raise ValueError(
            f"'{value}' is not a valid PaymentTypes value. Expected one of:"
            f" {', '.join(pt.value for pt in PaymentTypes)}"
        )
