from collections import Counter
from typing import Dict, List, Optional, Tuple

from hledger_preprocessor.TransactionObjects.Receipt import (
    Receipt,
    ShopId,
)
from typeguard import typechecked


def get_relevant_shop_ids(
    *, labelled_receipts: List[Receipt], category_input: Optional[str] = None
) -> Dict[str, List[Tuple[int, ShopId]]]:
    """Load labelled_receipts and create a category-to-shop-id mapping with
    counts.

    Args:
        labelled_receipts: List of Receipt objects
        category_input: User-provided category to filter shop IDs

    Returns:
        Dict mapping categories to lists of (count, ShopId) tuples

    Raises:
        ValueError: If labelled_receipts list is empty
    """
    if not labelled_receipts:
        raise ValueError("Receipts list cannot be empty")

    # Step 0: Create category-to-shop-id mapping with counts
    category_shop_counts: Dict[str, List[Tuple[int, ShopId]]] = {}

    # Extract category and shop ID pairs
    category_shop_pairs = [
        (r.receipt_category, r.shop_identifier)
        for r in labelled_receipts
        if r.receipt_category is not None and r.shop_identifier is not None
    ]

    # Group shop IDs by category and count occurrences
    for category, shop_id in category_shop_pairs:
        if category not in category_shop_counts:
            category_shop_counts[category] = []
        # Count occurrences of each shop ID within the category
        shop_counts = Counter(
            sid for cat, sid in category_shop_pairs if cat == category
        )
        # Convert to list of (count, ShopId) tuples, sorted by count descending
        category_shop_counts[category] = [
            (count, shop_id) for shop_id, count in shop_counts.most_common()
        ]

    # Step 1: If category_input is provided, check for match
    if category_input:
        if category_input in category_shop_counts:
            return {category_input: category_shop_counts[category_input]}
        return {}

    return category_shop_counts


@typechecked
def get_sorted_unique_shop_ids(
    *, previous_shop_ids: Dict[str, List[Tuple[int, ShopId]]]
) -> List[ShopId]:
    # Collect all unique shop IDs with their highest associated integer
    shop_max_scores: Dict[ShopId, int] = {}

    for _, tuples in previous_shop_ids.items():
        for score, shop_id in tuples:
            if (
                shop_id not in shop_max_scores
                or score > shop_max_scores[shop_id]
            ):
                shop_max_scores[shop_id] = score

    # Sort shop IDs by score (descending) and name (alphabetical for equal scores)
    sorted_shops = sorted(
        shop_max_scores.keys(),
        key=lambda shop: (-shop_max_scores[shop], shop.name),
    )

    return sorted_shops


@typechecked
def get_initial_complete_list(
    *, labelled_receipts: List[Receipt]
) -> List[ShopId]:
    previous_shop_ids: Dict[str, List[Tuple[int, ShopId]]] = (
        get_relevant_shop_ids(labelled_receipts=labelled_receipts)
    )
    return get_sorted_unique_shop_ids(previous_shop_ids=previous_shop_ids)
