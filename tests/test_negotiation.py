# tests/test_negotiation.py
from unittest.mock import patch, MagicMock
from src.negotiation import generate_counter_offer, format_budget_breakdown


def test_generate_counter_offer_calls_qwen():
    """Verify counter-offer goes through Qwen, not local arithmetic."""
    categorized = {
        "essential": {"rent": 1200},
        "discretionary": {"food": 300, "entertainment": 80, "dining": 120},
        "total": 1700
    }
    previous_plan = {
        "cuts": {"entertainment": 40, "dining": 30},
        "savings": 70,
        "explanation": "Cut discretionary"
    }
    user_objection = "I can't cut dining that much, parents are visiting next month"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.output.text = '{"cuts": {"entertainment": 50, "dining": 10}, "savings": 60, "explanation": "Reduced dining cut due to family visit"}'

    with patch("src.negotiation.Generation.call", return_value=mock_response) as mock_call:
        result = generate_counter_offer(categorized, previous_plan, user_objection)

        # Verify Qwen was called with the user's objection
        mock_call.assert_called_once()
        call_args = mock_call.call_args
        assert "parents are visiting" in call_args.kwargs["messages"][0]["content"]

        # Verify result came from Qwen response
        assert result["savings"] == 60
        assert result["cuts"]["dining"] == 10
        assert "family visit" in result["explanation"]


def test_format_budget_breakdown():
    plan = {
        "original_spending": 1500,
        "proposed_spending": 1300,
        "savings": 200,
        "cuts": {"entertainment": 100, "dining": 100},
        "explanation": "Cut discretionary"
    }
    breakdown = format_budget_breakdown(plan)
    assert "$1,500" in breakdown
    assert "$1,300" in breakdown
    assert "$200" in breakdown
    assert "entertainment" in breakdown