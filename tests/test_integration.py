# tests/test_integration.py
from unittest.mock import patch, MagicMock
from src.rules_engine import parse_transactions, categorize_transactions
from src.qwen_client import build_prompt, parse_recommendation
from src.negotiation import generate_counter_offer, format_budget_breakdown


def test_full_pipeline():
    """Test the complete flow from CSV to budget plan."""
    raw_data = [
        {"amount": 1200, "category": "rent", "description": "Monthly rent"},
        {"amount": 300, "category": "food", "description": "Groceries"},
        {"amount": 80, "category": "entertainment", "description": "Netflix"},
        {"amount": 120, "category": "dining", "description": "Restaurants"},
    ]

    parsed = parse_transactions(raw_data)
    assert len(parsed) == 4

    categorized = categorize_transactions(parsed)
    assert categorized.total == 1700
    assert "rent" in categorized.essential

    prompt = build_prompt(categorized, 200)
    assert "rent" in prompt
    assert "200" in prompt

    mock_response = '{"cuts": {"entertainment": 40, "dining": 30}, "savings": 70, "explanation": "Cut discretionary"}'
    plan = parse_recommendation(mock_response, 1700)
    assert plan.savings == 70

    formatted = format_budget_breakdown({
        "original_spending": 1700,
        "proposed_spending": 1630,
        "savings": 70,
        "cuts": {"entertainment": 40, "dining": 30},
        "explanation": "Cut discretionary"
    })
    assert "$1,700" in formatted
    assert "$70" in formatted


def test_negotiation_flow():
    """Test the negotiation flow with mocked Qwen."""
    categorized = {
        "essential": {"rent": 1200},
        "discretionary": {"food": 300, "entertainment": 80},
        "total": 1580
    }
    previous_plan = {"cuts": {"entertainment": 40}, "savings": 40}

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.output.text = '{"cuts": {"entertainment": 20}, "savings": 20, "explanation": "Reduced as requested"}'

    with patch("src.negotiation.Generation.call", return_value=mock_response):
        result = generate_counter_offer(categorized, previous_plan, "I need entertainment for work")
        assert result["cuts"]["entertainment"] == 20
        assert "Reduced" in result["explanation"]
