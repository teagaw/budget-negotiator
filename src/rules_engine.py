# src/rules_engine.py
from typing import List, Dict, Any
from src.models import Transaction, CategorizedTransactions


class ValidationError(Exception):
    """Raised when transaction data is invalid."""
    pass


def validate_transactions(transactions: list) -> list:
    """Validate transaction data. Raises ValidationError with details on bad rows."""
    valid = []
    dropped = []

    for i, t in enumerate(transactions):
        if not isinstance(t, dict):
            dropped.append({"row": i + 1, "reason": "not a dict"})
            continue
        amount = t.get("amount")
        if amount is None:
            dropped.append({"row": i + 1, "reason": "missing amount"})
            continue
        if not isinstance(amount, (int, float)):
            dropped.append({"row": i + 1, "reason": f"non-numeric amount: {amount}"})
            continue
        if float(amount) < 0:
            dropped.append({"row": i + 1, "reason": f"negative amount: {amount}"})
            continue
        valid.append(t)

    if dropped:
        raise ValidationError(
            f"{len(dropped)} invalid row(s) dropped: "
            + "; ".join(f"row {d['row']}: {d['reason']}" for d in dropped[:5])
            + ("..." if len(dropped) > 5 else "")
        )

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


def categorize_transactions(transactions: List[Transaction]) -> CategorizedTransactions:
    """Categorize transactions into essential vs discretionary."""
    essential = {}
    discretionary = {}
    total = 0.0

    for txn in transactions:
        total += txn.amount
        cat_lower = txn.category.lower()

        if cat_lower in ESSENTIAL_CATEGORIES:
            essential[cat_lower] = essential.get(cat_lower, 0) + txn.amount
        else:
            discretionary[cat_lower] = discretionary.get(cat_lower, 0) + txn.amount

    return CategorizedTransactions(
        essential=essential,
        discretionary=discretionary,
        total=total
    )