# tests/test_rules_engine.py
from src.rules_engine import parse_transactions, categorize_transactions


def test_parse_transactions_from_dicts():
    raw = [
        {"amount": 45.50, "category": "food", "description": "Grocery store"},
        {"amount": 1200, "category": "rent", "description": "Monthly rent"}
    ]
    result = parse_transactions(raw)
    assert len(result) == 2
    assert result[0].amount == 45.50


def test_parse_handles_missing_fields():
    raw = [{"amount": 10.00}]
    result = parse_transactions(raw)
    assert len(result) == 1
    assert result[0].category == "uncategorized"
    assert result[0].description == ""


def test_categorize_transactions():
    from src.models import Transaction
    transactions = [
        Transaction(1200, "rent", "Monthly rent"),
        Transaction(45.50, "food", "Groceries"),
        Transaction(80, "entertainment", "Netflix"),
        Transaction(150, "utilities", "Electric bill"),
    ]
    result = categorize_transactions(transactions)
    assert "rent" in result.essential
    assert "utilities" in result.essential
    assert "food" in result.discretionary
    assert "entertainment" in result.discretionary
    assert result.total == 1475.50