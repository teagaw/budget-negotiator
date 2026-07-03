# tests/test_regression.py
"""
Regression tests for bugs found during development.
Each test is named after the bug it prevents.
"""
import json
import pytest
from unittest.mock import patch, MagicMock
from src.handler import handler
from src.negotiation import generate_counter_offer, format_budget_breakdown
from src.qwen_client import QwenAPIError
from src.rules_engine import ValidationError


# ============================================================
# BUG-R1: handler returns flat proposed_spending (not nested)
# Bug: negotiate response used {"savings": {"plan": {"proposed_spending": ...}}}
# but handler looked for flat keys. Fixed by aligning response shape.
# ============================================================

def test_negotiate_response_shape_matches_handler():
    """BUG-R1: negotiate response must have flat proposed_spending key."""
    categorized = {"essential": {"rent": 1200}, "discretionary": {}, "total": 1200}
    previous_plan = {"cuts": {}, "savings": 0, "explanation": "Initial"}
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.output.text = '{"cuts": {"food": 50}, "savings": 50, "explanation": "Adjusted"}'

    with patch("src.negotiation.Generation.call", return_value=mock_response):
        result = generate_counter_offer(categorized, previous_plan, "test")

    # These keys MUST exist at top level (not nested under "savings.plan")
    assert "proposed_spending" in result, "proposed_spending must be a top-level key"
    assert "savings" in result
    assert "cuts" in result
    assert "explanation" in result
    assert result["proposed_spending"] == 1150  # 1200 - 50


# ============================================================
# BUG-R2: handler leaks raw exception messages to client
# Bug: handler returned str(e) which exposed internal paths/API keys.
# Fixed by returning generic "Internal server error" for all cases.
# ============================================================

@pytest.mark.parametrize("error_cls,args", [
    (ValidationError, ["bad data"]),
    (QwenAPIError, ["API down"]),
    (RuntimeError, ["unexpected crash"]),
    (ValueError, ["something weird"]),
], ids=["validation", "qwen-api", "runtime", "value"])
def test_error_messages_never_leak_to_client(error_cls, args):
    """BUG-R2: all errors return identical generic message, no internals."""
    event = {"body": json.dumps({"transactions": [{"amount": 100, "category": "food"}]})}

    with patch("src.handler.get_budget_recommendation", side_effect=error_cls(*args)):
        result = handler(event, {})

    body = json.loads(result["body"])
    assert body["error"] == "Internal server error"
    # Must NOT contain exception text, file paths, or API details
    assert args[0] not in body["error"]


# ============================================================
# BUG-R3: handler returns wrong status for unknown actions
# Bug: unknown action returned 500 instead of 400.
# ============================================================

@pytest.mark.parametrize("action", ["deploy", "delete", "export", "unknown"])
def test_unknown_action_returns_400_not_500(action):
    """BUG-R3: unknown action is client error (400), not server error (500)."""
    event = {"body": json.dumps({"action": action})}
    result = handler(event, {})
    assert result["statusCode"] == 400
    assert "Unknown action" in json.loads(result["body"])["error"]


# ============================================================
# BUG-R4: negotiate crashes on missing context instead of 400
# Bug: handler tried to call generate_counter_offer with None args.
# ============================================================

@pytest.mark.parametrize("body", [
    {},
    {"categorized": None},
    {"previous_plan": None},
    {"categorized": None, "previous_plan": None},
], ids=["empty", "null-categorized", "null-plan", "both-null"])
def test_negotiate_rejects_missing_context_as_400(body):
    """BUG-R4: missing negotiate context returns 400, not 500."""
    event = {"body": json.dumps({"action": "negotiate", **body})}
    result = handler(event, {})
    assert result["statusCode"] == 400
    assert "Missing negotiation" in json.loads(result["body"])["error"]


# ============================================================
# BUG-R5: negotiation API error crashes instead of fallback
# Bug: generate_counter_offer raised QwenAPIError to caller
# instead of returning fallback plan.
# ============================================================

def test_negotiation_api_error_returns_fallback():
    """BUG-R5: Qwen failure returns previous_plan, not exception."""
    categorized = {"essential": {"rent": 1200}, "discretionary": {}, "total": 1200}
    previous_plan = {"cuts": {"food": 50}, "savings": 50, "explanation": "Initial"}

    with patch("src.negotiation._call_qwen_negotiation", side_effect=QwenAPIError("timeout")):
        result = generate_counter_offer(categorized, previous_plan, "test")

    assert result.get("fallback") is True
    assert result["cuts"] == {"food": 50}  # Previous plan preserved
    assert result["savings"] == 50


# ============================================================
# BUG-R6: ambiguous input sanity check
# Bug: user could input "save $2000" on $1500 spending, producing
# nonsensical plan. Fixed by validating savings < original.
# ============================================================

def test_ambiguous_input_validates_savings_lt_original():
    """BUG-R6: savings cannot exceed original spending."""
    from src.negotiation import validate_ambiguity

    categorized = {"total": 1500}
    plan = {"savings": 2000, "proposed_spending": -500}

    result = validate_ambiguity(categorized, plan)
    assert result is False  # Should reject impossible plan


def test_ambiguous_input_rejects_zero_proposed_spending():
    """BUG-R6: proposed spending must be > 0."""
    from src.negotiation import validate_ambiguity

    categorized = {"total": 1500}
    plan = {"savings": 1500, "proposed_spending": 0}

    result = validate_ambiguity(categorized, plan)
    assert result is False


def test_ambiguous_input_accepts_valid_plan():
    """BUG-R6: normal plans pass validation."""
    from src.negotiation import validate_ambiguity

    categorized = {"total": 1500}
    plan = {"savings": 200, "proposed_spending": 1300}

    result = validate_ambiguity(categorized, plan)
    assert result is True
