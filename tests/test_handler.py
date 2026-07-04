# tests/test_handler.py
import json
import pytest
from unittest.mock import patch, MagicMock
from src.handler import handler, _handle_analyze, _handle_negotiate
from src.rules_engine import ValidationError
from src.qwen_client import QwenAPIError


# --- _handle_analyze tests ---

@pytest.mark.parametrize("body", [
    {"transactions": []},
    {},
], ids=["empty-list", "missing-key"])
def test_handle_analyze_rejects_bad_input(body):
    result = _handle_analyze(body)
    assert result["statusCode"] == 400
    assert "No transactions" in json.loads(result["body"])["error"]


def test_handle_analyze_success():
    transactions = [
        {"amount": 1200, "category": "rent", "description": "Rent"},
        {"amount": 300, "category": "food", "description": "Groceries"},
    ]
    mock_rec = {"original_spending": 1500, "proposed_spending": 1300, "savings": 200,
                "cuts": {"food": 200}, "explanation": "Cut food", "essential": {}, "discretionary": {}}

    with patch("src.handler.get_budget_recommendation", return_value=mock_rec):
        result = _handle_analyze({"transactions": transactions, "savings_goal": 200})

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert body["savings"] == 200
    assert body["proposed_spending"] == 1300


# --- _handle_negotiate tests ---

@pytest.mark.parametrize("body", [
    {"categorized": None, "previous_plan": None},
    {"previous_plan": {"cuts": {}}},
    {"categorized": {"total": 1000}},
], ids=["both-missing", "missing-categorized", "missing-previous-plan"])
def test_handle_negotiate_rejects_missing_context(body):
    result = _handle_negotiate(body)
    assert result["statusCode"] == 400
    assert "Missing negotiation" in json.loads(result["body"])["error"]


def test_handle_negotiate_success():
    categorized = {"essential": {"rent": 1200}, "discretionary": {}, "total": 1200}
    previous_plan = {"cuts": {}, "savings": 0, "explanation": "Initial"}
    mock_counter = {"cuts": {"food": 50}, "savings": 50, "proposed_spending": 1150,
                    "explanation": "Adjusted", "essential": {}, "discretionary": {},
                    "original_spending": 1200}

    with patch("src.handler.generate_counter_offer", return_value=mock_counter):
        result = _handle_negotiate({
            "categorized": categorized,
            "previous_plan": previous_plan,
            "user_objection": "Too aggressive"
        })

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert body["savings"] == 50


# --- handler() routing tests ---

def test_handler_routes_analyze():
    body = json.dumps({"action": "analyze", "transactions": [{"amount": 100, "category": "food"}]})
    event = {"body": body}
    mock_rec = {"savings": 50, "proposed_spending": 50, "original_spending": 100,
                "cuts": {}, "explanation": "Cut", "essential": {}, "discretionary": {}}

    with patch("src.handler.get_budget_recommendation", return_value=mock_rec):
        result = handler(event, {})

    assert result["statusCode"] == 200


def test_handler_routes_negotiate():
    body = json.dumps({
        "action": "negotiate",
        "categorized": {"essential": {}, "discretionary": {}, "total": 1000},
        "previous_plan": {"cuts": {}, "savings": 0},
        "user_objection": "test"
    })
    event = {"body": body}
    mock_counter = {"cuts": {}, "savings": 0, "proposed_spending": 1000,
                    "explanation": "OK", "essential": {}, "discretionary": {},
                    "original_spending": 1000}

    with patch("src.handler.generate_counter_offer", return_value=mock_counter):
        result = handler(event, {})

    assert result["statusCode"] == 200


def test_handler_unknown_action_returns_400():
    event = {"body": json.dumps({"action": "deploy"})}
    result = handler(event, {})
    assert result["statusCode"] == 400
    assert "Unknown action" in json.loads(result["body"])["error"]


def test_handler_default_action_is_analyze():
    """Missing action defaults to 'analyze'."""
    event = {"body": json.dumps({"transactions": []})}
    result = handler(event, {})
    assert result["statusCode"] == 400
    assert "No transactions" in json.loads(result["body"])["error"]


# --- Error handling tests ---

def test_handler_invalid_json_returns_400():
    event = {"body": "not valid json {{{"}
    result = handler(event, {})
    assert result["statusCode"] == 400
    assert "Invalid JSON" in json.loads(result["body"])["error"]


def test_handler_validation_error_returns_400():
    event = {"body": json.dumps({"transactions": [{"amount": -5}]})}
    result = handler(event, {})
    assert result["statusCode"] == 400
    body = json.loads(result["body"])
    assert "error" in body
    assert "Internal server error" not in body["error"]


def test_handler_qwen_api_error_returns_502():
    event = {"body": json.dumps({"transactions": [{"amount": 100, "category": "food"}]})}
    with patch("src.handler.get_budget_recommendation", side_effect=QwenAPIError("API down")):
        result = handler(event, {})
    assert result["statusCode"] == 502
    body = json.loads(result["body"])
    assert "Qwen API" in body["error"] or "unavailable" in body["error"]


def test_handler_unknown_exception_returns_500():
    event = {"body": json.dumps({"transactions": [{"amount": 100, "category": "food"}]})}
    with patch("src.handler.get_budget_recommendation", side_effect=RuntimeError("crash")):
        result = handler(event, {})
    assert result["statusCode"] == 500
    assert "Internal server error" in json.loads(result["body"])["error"]


def test_handler_empty_body_defaults_to_analyze():
    event = {"body": ""}
    result = handler(event, {})
    assert result["statusCode"] == 400
    assert "Invalid JSON" in json.loads(result["body"])["error"]


def test_handler_missing_body_key():
    event = {}
    result = handler(event, {})
    assert result["statusCode"] == 400


# --- Auth tests ---

@pytest.mark.parametrize("headers,description", [
    (None, "missing headers entirely"),
    ({}, "empty headers"),
    ({"X-API-Key": ""}, "empty key"),
    ({"X-API-Key": "wrong-key"}, "wrong key"),
    ({"x-api-key": "wrong-key"}, "lowercase header, wrong key"),
], ids=["no-headers", "empty-headers", "empty-key", "wrong-key", "lowercase-wrong"])
@patch("src.handler.FUNCTION_API_KEY", "test-secret-key")
def test_handler_unauthorized_returns_401(headers, description):
    """Auth: missing or wrong X-API-Key is rejected before any business logic runs."""
    event = {
        "body": json.dumps({"action": "analyze", "transactions": [{"amount": 100, "category": "food"}]}),
        "headers": headers
    }
    # If business logic runs, this mock will fail the test
    with patch("src.handler.get_budget_recommendation", side_effect=AssertionError("business logic should not run")):
        result = handler(event, {})
    assert result["statusCode"] == 401
    assert "Unauthorized" in json.loads(result["body"])["error"]


@patch("src.handler.FUNCTION_API_KEY", "test-secret-key")
def test_handler_authorized_request_passes_through():
    """Auth: correct X-API-Key reaches business logic."""
    event = {
        "body": json.dumps({"action": "analyze", "transactions": [{"amount": 100, "category": "food"}]}),
        "headers": {"X-API-Key": "test-secret-key"}
    }
    mock_rec = {"savings": 50, "proposed_spending": 50, "original_spending": 100,
                "cuts": {}, "explanation": "Cut", "essential": {}, "discretionary": {}}
    with patch("src.handler.get_budget_recommendation", return_value=mock_rec):
        result = handler(event, {})
    assert result["statusCode"] == 200


@patch("src.handler.FUNCTION_API_KEY", "")
def test_handler_no_auth_config_skips_check():
    """Auth: when FUNCTION_API_KEY is empty, auth check is skipped (local dev)."""
    event = {
        "body": json.dumps({"action": "analyze", "transactions": [{"amount": 100, "category": "food"}]}),
        "headers": {}
    }
    mock_rec = {"savings": 50, "proposed_spending": 50, "original_spending": 100,
                "cuts": {}, "explanation": "Cut", "essential": {}, "discretionary": {}}
    with patch("src.handler.get_budget_recommendation", return_value=mock_rec):
        result = handler(event, {})
    assert result["statusCode"] == 200
