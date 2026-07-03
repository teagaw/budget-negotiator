# tests/test_rules_engine.py
import pytest
from src.rules_engine import parse_transactions, categorize_transactions, validate_transactions, ValidationError


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


# --- validate_transactions edge cases ---

@pytest.mark.parametrize("data,match", [
    (["not a dict", 42], "not a dict"),
    ([{"category": "food"}], "missing amount"),
    ([{"amount": "abc", "category": "food"}], "non-numeric"),
    ([{"amount": -50, "category": "food"}], "negative"),
], ids=["non-dict", "missing-amount", "non-numeric", "negative"])
def test_validate_rejects_bad_rows(data, match):
    with pytest.raises(ValidationError, match=match):
        validate_transactions(data)


def test_validate_mixed_errors_truncates_to_5():
    bad_rows = [{"amount": "x"} for _ in range(10)]
    with pytest.raises(ValidationError, match=r"\.\.\.$"):
        validate_transactions(bad_rows)


@pytest.mark.parametrize("data,expected_amount", [
    ([{"amount": 0, "category": "free"}], 0),
    ([{"amount": 19.99, "category": "food"}], 19.99),
], ids=["zero-amount", "float-amount"])
def test_validate_accepts_valid_edge_cases(data, expected_amount):
    result = validate_transactions(data)
    assert len(result) == 1
    assert result[0]["amount"] == expected_amount


def test_parse_transactions_uses_validated_data():
    raw = [
        {"amount": 100, "category": "rent", "description": "Rent"},
        {"amount": "bad"},  # will be rejected by validate
    ]
    with pytest.raises(ValidationError):
        parse_transactions(raw)


def test_categorize_empty_transactions():
    result = categorize_transactions([])
    assert result.total == 0.0
    assert result.essential == {}
    assert result.discretionary == {}


def test_categorize_case_insensitive():
    from src.models import Transaction
    transactions = [
        Transaction(100, "RENT", "Rent"),
        Transaction(50, "Food", "Groceries"),
    ]
    result = categorize_transactions(transactions)
    assert "rent" in result.essential
    assert "food" in result.discretionary


def test_categorize_unknown_category_goes_to_discretionary():
    from src.models import Transaction
    transactions = [Transaction(30, "crypto", "Bitcoin")]
    result = categorize_transactions(transactions)
    assert "crypto" in result.discretionary


def test_categorize_sum_multiple_same_category():
    from src.models import Transaction
    transactions = [
        Transaction(100, "food", "Groceries"),
        Transaction(50, "food", "Snacks"),
    ]
    result = categorize_transactions(transactions)
    assert result.discretionary["food"] == 150
    assert result.total == 150