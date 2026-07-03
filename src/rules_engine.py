# src/rules_engine.py
from typing import List, Dict, Any
from src.models import Transaction, CategorizedTransactions


def validate_transactions(transactions: list) -> list:
    """Validate and clean transaction data."""
    valid = []
    for t in transactions:
        if not isinstance(t, dict):
            continue
        amount = t.get("amount")
        if amount is None or not isinstance(amount, (int, float)):
            continue
        if float(amount) < 0:
            continue
        valid.append(t)
    return valid


def parse_transactions(raw_data: List[Dict[str, Any]]) -> List[Transaction]:
    """Parse and validate raw transaction data."""
    validated = validate_transactions(raw_data)
    transactions = []
    for item in validated:
        transactions.append(Transaction(
            amount=float(item.get("amount", 0)),
            category=item.get("category", "uncategorized"),
            description=item.get("description", "")
        ))
    return transactions


ESSENTIAL_CATEGORIES = {"rent", "utilities", "insurance", "healthcare", "transport"}
DISCRETIONARY_CATEGORIES = {"food", "entertainment", "dining", "shopping", "personal"}


def categorize_transactions(transactions: List[Transaction]) -> CategorizedTransactions:
    """Categorize transactions into essential vs discretionary."""
    essential = {}
    discretionary = {}
    total = 0.0

    for t in transactions:
        total += t.amount
        cat_lower = t.category.lower()

        if cat_lower in ESSENTIAL_CATEGORIES:
            essential[cat_lower] = essential.get(cat_lower, 0) + t.amount
        else:
            discretionary[cat_lower] = discretionary.get(cat_lower, 0) + t.amount

    return CategorizedTransactions(
        essential=essential,
        discretionary=discretionary,
        total=total
    )