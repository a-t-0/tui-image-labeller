from collections import Counter
from typing import Dict, List, Optional, Tuple

from hledger_preprocessor.TransactionObjects.Receipt import (
    Address,
    Receipt,
    ShopId,
)
from typeguard import typechecked


@typechecked
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

    # Group by category
    for category in {cat for cat, _ in category_shop_pairs}:
        # Get all shop IDs for this category
        shop_ids = [sid for cat, sid in category_shop_pairs if cat == category]
        # Convert ShopId to a hashable tuple for counting
        shop_id_tuples = [
            (
                sid["name"] if isinstance(sid, dict) else sid.name,
                (
                    Address(**sid["address"]).to_string()
                    if isinstance(sid, dict)
                    and isinstance(sid["address"], dict)
                    else sid.address.to_string()
                ),
                (
                    sid.get("shop_account_nr", "")
                    if isinstance(sid, dict)
                    else (sid.shop_account_nr or "")
                ),
            )
            for sid in shop_ids
        ]
        # Count occurrences of each shop ID
        shop_counts = Counter(shop_id_tuples)
        # Convert back to ShopId objects with counts, sorted by count descending
        category_shop_counts[category] = [
            (
                count,
                (
                    ShopId(
                        name=hashable_sid[0],
                        address=(
                            Address(**sid["address"])
                            if isinstance(sid, dict)
                            and isinstance(sid["address"], dict)
                            else sid.address
                        ),
                        shop_account_nr=(
                            hashable_sid[2] if hashable_sid[2] else None
                        ),
                    )
                    if isinstance(sid, dict)
                    else sid
                ),
            )
            for hashable_sid, count in shop_counts.most_common()
            for sid in shop_ids
            if (
                (sid["name"] if isinstance(sid, dict) else sid.name)
                == hashable_sid[0]
                and (
                    Address(**sid["address"]).to_string()
                    if isinstance(sid, dict)
                    and isinstance(sid["address"], dict)
                    else sid.address.to_string()
                )
                == hashable_sid[1]
                and (
                    sid.get("shop_account_nr", "")
                    if isinstance(sid, dict)
                    else (sid.shop_account_nr or "")
                )
                == hashable_sid[2]
            )
        ]

    # Step 1: If category_input is provided, filter to that category
    if category_input:
        return {category_input: category_shop_counts.get(category_input, [])}

    return category_shop_counts


@typechecked
def get_sorted_unique_shop_ids(
    *, previous_shop_ids: Dict[str, List[Tuple[int, ShopId]]]
) -> List[ShopId]:
    # Collect all unique shop IDs with their highest associated integer
    shop_max_scores: Dict[tuple, int] = {}

    for _, tuples in previous_shop_ids.items():
        for score, shop_id in tuples:
            shop_key = (
                shop_id.name,
                shop_id.address.to_string(),
                shop_id.shop_account_nr or "",
            )
            if (
                shop_key not in shop_max_scores
                or score > shop_max_scores[shop_key]
            ):
                shop_max_scores[shop_key] = score

    # Sort shop IDs by score (descending) and name (alphabetical for equal scores)
    sorted_shops = sorted(
        shop_max_scores.keys(),
        key=lambda shop_key: (-shop_max_scores[shop_key], shop_key[0]),
    )

    # Convert back to ShopId objects
    shop_id_map = {
        (sid.name, sid.address.to_string(), sid.shop_account_nr or ""): sid
        for category, tuples in previous_shop_ids.items()
        for _, sid in tuples
    }

    return [
        shop_id_map[shop_key]
        for shop_key in sorted_shops
        if shop_key in shop_id_map
    ]


@typechecked
def get_initial_complete_list(
    *, labelled_receipts: List[Receipt]
) -> List[ShopId]:
    previous_shop_ids: Dict[str, List[Tuple[int, ShopId]]] = (
        get_relevant_shop_ids(labelled_receipts=labelled_receipts)
    )
    return get_sorted_unique_shop_ids(previous_shop_ids=previous_shop_ids)
