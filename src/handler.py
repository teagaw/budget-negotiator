"""
Alibaba Cloud Function Compute entry point.
Demonstrates real Qwen Cloud API usage for budget negotiation.
"""
import os
import json
import dashscope
from dashscope import Generation
from src.rules_engine import parse_transactions, categorize_transactions
from src.qwen_client import get_budget_recommendation, get_counter_offer

# Load API key from environment (set in FC console or .env for local)
dashscope.api_key = os.environ.get("DASHSCOPE_API_KEY", "")


def handler(event, context):
    """
    FC HTTP trigger handler.
    Receives spending data + chat history, returns budget negotiation response.
    """
    try:
        body = json.loads(event.get("body", "{}"))
        action = body.get("action", "analyze")

        if action == "analyze":
            transactions = body.get("transactions", [])
            savings_goal = body.get("savings_goal", "auto")

            if not transactions:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "No transactions provided"})
                }

            # Step 1: Rules engine — parse and categorize
            parsed = parse_transactions(transactions)
            categorized = categorize_transactions(parsed)

            # Step 2: Qwen API — reason about cuts
            recommendation = get_budget_recommendation(
                categorized_transactions=categorized,
                savings_goal=savings_goal
            )

            return {
                "statusCode": 200,
                "body": json.dumps(recommendation)
            }

        elif action == "negotiate":
            # New: Qwen-powered negotiation on every turn
            categorized = body.get("categorized")
            previous_plan = body.get("previous_plan")
            user_objection = body.get("user_objection", "")

            if not categorized or not previous_plan:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Missing negotiation context"})
                }

            counter = get_counter_offer(categorized, previous_plan, user_objection)

            return {
                "statusCode": 200,
                "body": json.dumps(counter)
            }

        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Unknown action: {action}"})
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
