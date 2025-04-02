from typing import List, Optional, Dict
from datetime import datetime
from dataclasses import dataclass

from hledger_preprocessor.TransactionObjects.Receipt import (  # For image handling
    ExchangedItem,
    Receipt,
)
from typeguard import typechecked



@typechecked
def build_receipt_from_answers(*,final_answers: dict) -> Receipt:
    """
    Builds a Receipt object from the dictionary of answers returned by tui.get_answers()
    
    Args:
        final_answers: Dictionary containing question widgets as keys and their answers as values
    
    Returns:
        Receipt object with mapped values
    """
    # Helper function to extract value from widget key
    def get_value(caption: str) -> any:
        for widget, value in final_answers.items():
            if hasattr(widget, 'caption') and caption in widget.caption:
                # Convert empty strings to None for optional fields
                return value if value != '' else None
        return None

    # Since bought_items and returned_items aren't in the provided questions,
    # we'll initialize them as empty lists
    bought_items = []
    returned_items = []

    

    # Map the answers to Receipt parameters
    receipt_params = {
        'currency': get_value('Currency:\n') or '',  # Required, default to empty string
        'shop_name': get_value('\nShop name:\n') or '',  # Required, default to empty string
        'receipt_owner_account_holder': get_value('\nAccount holder name:\n') or '',  # Required
        'receipt_owner_bank': get_value('\nBank name (e.g., triodos, bitfavo):\n') or '',  # Required
        'receipt_owner_account_holder_type': get_value('\nAccount type (e.g., checking, credit):\n') or '',  # Required
        'bought_items': bought_items,
        'returned_items': returned_items,
        'the_date': get_value('Receipt date and time:\n') or datetime.now(),  # Use current time if missing
        'payed_total_read': float(get_value('\nAmount paid in cash:\n') or 
                                get_value('\nAmount paid by card:\n') or 0.0),  # Required, default to 0.0
        'shop_address': get_value('\nShop address:\n'),
        'shop_account_nr': get_value('\nShop account nr:\n'),
        'subtotal': float(get_value('\nSubtotal (Optional, press enter to skip):\n')) if get_value('\nSubtotal (Optional, press enter to skip):\n') else None,
        'total_tax': float(get_value('\nTotal tax (Optional, press enter to skip):\n')) if get_value('\nTotal tax (Optional, press enter to skip):\n') else None,
        'cash_payed': float(get_value('\nAmount paid in cash:\n')) if get_value('\nAmount paid in cash:\n') else None,
        'cash_returned': float(get_value('\nChange returned (cash):\n')) if get_value('\nChange returned (cash):\n') else None,
        'receipt_owner_address': get_value('\nReceipt owner address (optional):\n'),
        'receipt_categorisation': {'category': get_value('\nBookkeeping category:\n')} if get_value('\nBookkeeping category:\n') else None
    }

    # Handle card payments if present
    card_payed = get_value('\nAmount paid by card:\n')
    if card_payed is not None:
        receipt_params['payed_total_read'] = float(card_payed)
    
    card_returned = get_value('\nChange returned (card):\n')
    if card_returned is not None and receipt_params['cash_returned'] is None:
        receipt_params['cash_returned'] = float(card_returned)

    if bought_items == [] and returned_items == []:
        filler_item:ExchangedItem=ExchangedItem(
            quantity=1,
            description=receipt_params['receipt_categorisation'],
            the_date= receipt_params['the_date'],
            payed_unit_price=compute_total(receipt_params=receipt_params),
            currency= receipt_params['currency'],
            tax_per_unit=0,
            group_discount=0,
            # category=None
            # round_amount: Optional[str]

    )   
        receipt_params['bought_items']=bought_items
        bought_items

    return Receipt(**receipt_params)


def compute_total(*, receipt_params: Dict) -> float:
    """
    Computes the total amount for the receipt based on payment and return values.
    
    Args:
        receipt_params: Dictionary containing receipt parameters
        
    Returns:
        float: The computed total amount (positive for money paid, negative for money received)
        
    Notes:
        - Cash paid and card paid are positive contributions
        - Cash returned and card returned are negative contributions
        - If subtotal and total_tax are provided, they can be used to verify the calculation
        - Uses 0 as default when values are missing or None
    """
    # Initialize total
    total = 0.0
    
    # Get payment and return values, defaulting to 0 if None or missing
    cash_payed = float(receipt_params.get('cash_payed', 0) or 0)
    cash_returned = float(receipt_params.get('cash_returned', 0) or 0)
    card_payed = float(receipt_params.get('payed_total_read', 0) or 0)
    
    # Handle case where payed_total_read might be from cash payment
    if cash_payed != 0 and card_payed == cash_payed:
        # If payed_total_read matches cash_payed, assume it's not a separate card payment
        card_payed = 0.0
    
    # Add explicit card payment if present (assuming it might be in the dict with a different key)
    explicit_card_payed = float(receipt_params.get('card_payed', 0) or 0)
    if explicit_card_payed != 0:
        card_payed = explicit_card_payed
    
    # Add explicit card returned if present
    card_returned = float(receipt_params.get('card_returned', 0) or 0)
    
    # Calculate total
    total += cash_payed  # Positive: money paid in cash
    total -= cash_returned  # Negative: money returned in cash
    total += card_payed  # Positive: money paid by card
    total -= card_returned  # Negative: money returned by card
    
    # Verification with subtotal and tax if available
    subtotal = receipt_params.get('subtotal')
    total_tax = receipt_params.get('total_tax')
    if subtotal is not None and total_tax is not None:
        expected_total = float(subtotal) + float(total_tax)
        if abs(expected_total - total) > 0.01:  # Allow for small floating-point differences
            print(f"Warning: Computed total ({total:.2f}) differs from subtotal ({subtotal:.2f}) + tax ({total_tax:.2f}) = {expected_total:.2f}")

    return total