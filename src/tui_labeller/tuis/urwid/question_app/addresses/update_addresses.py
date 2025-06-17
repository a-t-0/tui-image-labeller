from collections import Counter
from typing import Dict, List, Optional, Tuple

from hledger_preprocessor.TransactionObjects.Receipt import (
    Receipt,
    ShopId,
)


def get_relevant_shop_ids(
    *, receipts: List[Receipt], category_input: Optional[str] = None
) -> Dict[str, List[Tuple[int, ShopId]]]:
    """Load receipts and create a category-to-shop-id mapping with counts.

    Args:
        receipts: List of Receipt objects
        category_input: User-provided category to filter shop IDs

    Returns:
        Dict mapping categories to lists of (count, ShopId) tuples

    Raises:
        ValueError: If receipts list is empty
    """
    if not receipts:
        raise ValueError("Receipts list cannot be empty")

    # Step 0: Create category-to-shop-id mapping with counts
    category_shop_counts: Dict[str, List[Tuple[int, ShopId]]] = {}

    # Extract category and shop ID pairs
    category_shop_pairs = [
        (r.receipt_category, r.shop_identifier)
        for r in receipts
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
