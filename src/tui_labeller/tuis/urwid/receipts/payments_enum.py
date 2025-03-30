from enum import Enum


class PaymentTypes(Enum):
    CASH = "cash"
    CARD = "card"
    BOTH = "both"
    OTHER = "other"
