# tests/test_negotiation.py
from unittest.mock import patch, MagicMock
from src.negotiation import generate_counter_offer, format_budget_breakdown
from src.qwen_client import QwenAPIError


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

    with patch("src.qwen_client.Generation.call", return_value=mock_response) as mock_call:
        result = generate_counter_offer(categorized, previous_plan, user_objection)

        # Verify Qwen was called with the user's objection
        mock_call.assert_called_once()
        call_args = mock_call.call_args
        messages = call_args.kwargs["messages"]
        assert messages[0]["role"] == "user"
        assert len(messages[0]["content"]) > 0

        # Verify result came from Qwen response
        assert result["savings"] == 60
        assert result["cuts"]["dining"] == 10
        assert "family visit" in result["explanation"]


def test_generate_counter_offer_qwen_error_returns_fallback():
    """QwenAPIError returns fallback plan, not crash."""
    categorized = {"essential": {"rent": 1200}, "discretionary": {}, "total": 1200}
    previous_plan = {"cuts": {"food": 50}, "savings": 50, "explanation": "Initial"}

    with patch("src.qwen_client.Generation.call", side_effect=QwenAPIError("API down")):
        result = generate_counter_offer(categorized, previous_plan, "test")

    assert result.get("fallback") is True
    assert "error" in result
    assert result["cuts"] == {"food": 50}


def test_generate_counter_offer_api_status_error_returns_fallback():
    """Non-200 status code raises QwenAPIError, caught by except."""
    categorized = {"essential": {}, "discretionary": {}, "total": 500}
    previous_plan = {"cuts": {}, "savings": 0}

    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.output.text = ""

    with patch("src.qwen_client.Generation.call", return_value=mock_response):
        result = generate_counter_offer(categorized, previous_plan, "hello")

    assert result.get("fallback") is True


def test_generate_counter_offer_invalid_json_returns_fallback():
    """Malformed JSON in Qwen response triggers JSONDecodeError → fallback."""
    categorized = {"essential": {}, "discretionary": {}, "total": 500}
    previous_plan = {"cuts": {}, "savings": 0}

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.output.text = "not json at all"

    with patch("src.qwen_client.Generation.call", return_value=mock_response):
        result = generate_counter_offer(categorized, previous_plan, "test")

    assert result.get("fallback") is True


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