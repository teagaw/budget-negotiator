"""
Alibaba Cloud Function Compute entry point.
Demonstrates real Qwen Cloud API usage for budget negotiation.
"""
import os
import json
import hmac
import logging
import dashscope
from src.rules_engine import parse_transactions, categorize_transactions, ValidationError
from src.qwen_client import get_budget_recommendation, QwenAPIError
from src.negotiation import generate_counter_offer

# Load API key from environment (set in FC console or .env for local)
dashscope.api_key = os.environ.get("DASHSCOPE_API_KEY", "")

def _get_function_api_key():
    """Shared-secret auth key (set in FC console env, never hardcoded)."""
    return os.environ.get("FUNCTION_API_KEY", "")


def _handle_analyze(body: dict) -> dict:
    """Process initial budget analysis request."""
    transactions = body.get("transactions", [])
    savings_goal = body.get("savings_goal", "auto")

    if not transactions:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "No transactions provided"})
        }

    parsed = parse_transactions(transactions)
    categorized = categorize_transactions(parsed)

    recommendation = get_budget_recommendation(
        categorized_transactions=categorized,
        savings_goal=savings_goal
    )

    return {
        "statusCode": 200,
        "body": json.dumps(recommendation)
    }


def _handle_negotiate(body: dict) -> dict:
    """Process negotiation request with Qwen-powered counter-offer."""
    categorized = body.get("categorized")
    previous_plan = body.get("previous_plan")
    user_objection = body.get("user_objection", "")

    if not categorized or not previous_plan:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing negotiation context"})
        }

    counter = generate_counter_offer(categorized, previous_plan, user_objection)

    return {
        "statusCode": 200,
        "body": json.dumps(counter)
    }


def handler(event, context):
    """
    FC HTTP trigger handler.
    Receives spending data + chat history, returns budget negotiation response.
    """
    # Shared-secret auth — reject before any parsing or Qwen calls
    headers = event.get("headers", {}) or {}
    provided_key = headers.get("x-api-key", "") or headers.get("X-API-Key", "")
    api_key = _get_function_api_key()
    if api_key and not hmac.compare_digest(provided_key, api_key):
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Unauthorized"})
        }

    try:
        body = json.loads(event.get("body", "{}"))
        action = body.get("action", "analyze")

        if action == "analyze":
            return _handle_analyze(body)
        elif action == "negotiate":
            return _handle_negotiate(body)
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Unknown action: {action}"})
            }

    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON in request body"})
        }
    except ValidationError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)})
        }
    except QwenAPIError:
        return {
            "statusCode": 502,
            "body": json.dumps({"error": "Qwen API is currently unavailable, please try again"})
        }
    except Exception:
        logging.exception("Unhandled error in handler")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }
