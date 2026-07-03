# tests/test_qwen_client.py
import json
import pytest
from unittest.mock import patch, MagicMock
from src.qwen_client import (
    build_prompt, parse_recommendation, extract_json_from_response,
    get_budget_recommendation, QwenAPIError
)
from src.models import CategorizedTransactions


def test_build_prompt_includes_categories():
    cats = CategorizedTransactions(
        essential={"rent": 1200},
        discretionary={"food": 300, "entertainment": 80},
        total=1580
    )
    prompt = build_prompt(cats, "auto")
    assert "rent" in prompt
    assert "1200" in prompt
    assert "food" in prompt
    assert "300" in prompt


def test_build_prompt_with_goal():
    cats = CategorizedTransactions(
        essential={"rent": 1200},
        discretionary={"food": 300},
        total=1500
    )
    prompt = build_prompt(cats, 200)
    assert "200" in prompt


def test_parse_recommendation():
    raw_response = """
    {"cuts": {"entertainment": 40, "dining": 30}, "savings": 70, "explanation": "Reduce discretionary spending"}
    """
    result = parse_recommendation(raw_response, 1500)
    assert result.savings == 70
    assert result.cuts["entertainment"] == 40
    assert result.explanation == "Reduce discretionary spending"


# --- extract_json_from_response ---

def test_extract_json_from_text_wrapping():
    raw = 'Here is the plan: {"cuts": {"food": 50}, "savings": 50, "explanation": "Cut food"} hope that helps'
    result = extract_json_from_response(raw)
    assert result["savings"] == 50


def test_extract_json_no_json_raises():
    import pytest
    with pytest.raises(json.JSONDecodeError):
        extract_json_from_response("no json here at all")


def test_extract_json_empty_string_raises():
    import pytest
    with pytest.raises(json.JSONDecodeError):
        extract_json_from_response("")


# --- parse_recommendation edge cases ---

def test_parse_recommendation_invalid_json_returns_fallback_plan():
    result = parse_recommendation("garbage response", 1000)
    assert result.savings == 0
    assert result.proposed_spending == 1000
    assert "Failed to parse" in result.explanation


def test_parse_recommendation_missing_fields_uses_defaults():
    raw = '{"cuts": {}}'
    result = parse_recommendation(raw, 1500)
    assert result.savings == 0
    assert result.cuts == {}
    assert result.explanation == ""


# --- get_budget_recommendation ---

@pytest.mark.parametrize("goal", ["auto", 200], ids=["auto-goal", "numeric-goal"])
def test_get_budget_recommendation_success(goal):
    cats = CategorizedTransactions(
        essential={"rent": 1200}, discretionary={"food": 300}, total=1500
    )
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.output.text = '{"cuts": {"food": 100}, "savings": 100, "explanation": "Cut food"}'

    with patch("src.qwen_client.Generation.call", return_value=mock_response):
        result = get_budget_recommendation(cats, goal)

    assert result["savings"] == 100
    assert result["original_spending"] == 1500
    assert result["proposed_spending"] == 1400
    assert "essential" in result
    assert "discretionary" in result


def test_get_budget_recommendation_api_error():
    cats = CategorizedTransactions(
        essential={"rent": 1200}, discretionary={}, total=1200
    )

    mock_response = MagicMock()
    mock_response.status_code = 500

    with patch("src.qwen_client.Generation.call", return_value=mock_response):
        with pytest.raises(QwenAPIError):
            get_budget_recommendation(cats, "auto")


def test_retry_on_transient_503_then_success():
    """First call returns 503, second returns 200 — retry succeeds."""
    cats = CategorizedTransactions(
        essential={"rent": 1200}, discretionary={"food": 300}, total=1500
    )

    error_response = MagicMock()
    error_response.status_code = 503

    ok_response = MagicMock()
    ok_response.status_code = 200
    ok_response.output.text = '{"cuts": {"food": 50}, "savings": 50, "explanation": "Cut food"}'

    with patch("src.qwen_client.Generation.call", side_effect=[error_response, ok_response]):
        with patch("src.qwen_client.time.sleep") as mock_sleep:
            result = get_budget_recommendation(cats, "auto")

    mock_sleep.assert_called_once_with(1)
    assert result["savings"] == 50
    assert result["original_spending"] == 1500
    assert result["proposed_spending"] == 1450


@pytest.mark.parametrize("goal,expected_str", [
    ("auto", "save as much as possible"),
    (250, "$250"),
], ids=["auto-goal", "numeric-goal"])
def test_build_prompt_includes_goal_text(goal, expected_str):
    cats = CategorizedTransactions(
        essential={"rent": 1200}, discretionary={"food": 300}, total=1500
    )
    prompt = build_prompt(cats, goal)
    assert expected_str in prompt.lower() if isinstance(expected_str, str) else expected_str in prompt