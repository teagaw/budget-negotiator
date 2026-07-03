# Budget Negotiator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an AI budget negotiator agent that ingests spending data, reasons about cuts, and negotiates a savings plan with the user via conversation.

**Architecture:** Hybrid rules + LLM. Rules engine handles CSV parsing, categorization, and validation. Qwen API handles reasoning about cuts, negotiation, and natural language output. Streamlit provides the chat UI with file upload and spending charts. Deployed on Alibaba Cloud Function Compute.

**Tech Stack:** Python 3.10+, Alibaba Cloud Function Compute, Qwen API (dashscope SDK), Streamlit, pandas, plotly, pytest

---

## 30-Hour Budget Breakdown

| Hours | Phase | Deliverable |
|-------|-------|-------------|
| 1-3 | Setup | Repo, deps, FC deployment proof, verify Qwen API works |
| 4-8 | Rules Engine | CSV parsing, categorization, validation, error handling |
| 9-14 | Qwen Integration | API client, reasoning prompts, negotiation logic |
| 15-20 | Streamlit UI | Chat interface, file upload, charts, conversation flow |
| 21-25 | Integration | Wire everything together, error paths, edge cases |
| 26-28 | Demo Prep | Synthetic data, architecture diagram, demo script |
| 29-30 | Submission | Video recording, README, submission form |

---

## File Structure

```
budget-negotiator/
├── .env                    # API key (gitignored)
├── .gitignore              # Security: no secrets in repo
├── README.md
├── LICENSE
├── requirements.txt
├── docs/
│   ├── architecture.md
│   └── demo-data/
│       ├── middle-class.csv
│       └── young-professional.csv
├── src/
│   ├── handler.py          # FC entry point (DEPLOYMENT PROOF)
│   ├── rules_engine.py     # CSV parsing, categorization, validation
│   ├── qwen_client.py      # Qwen API integration + negotiation reasoning
│   ├── negotiation.py      # Thin wrapper calling Qwen for counter-offers
│   └── models.py           # Data models
├── tests/
│   ├── test_rules_engine.py
│   ├── test_qwen_client.py
│   └── test_negotiation.py
└── streamlit/
    └── app.py              # Streamlit UI
```

---

### Task 1: Project Setup + Deployment Proof (Hours 1-3)

**Files:**
- Create: `.gitignore`
- Create: `.env`
- Create: `requirements.txt`
- Create: `src/__init__.py`
- Create: `tests/__init__.py`
- Create: `src/handler.py`

- [ ] **Step 1: Initialize git repo**

```bash
cd "C:\Users\QQQ\Desktop\hackathon projects\budget-negotiator"
git init
```

- [ ] **Step 2: Create .gitignore FIRST (before anything else)**

```bash
# .gitignore
.env
*.key
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
dist/
build/
.venv/
```

- [ ] **Step 3: Create .env with API key**

```bash
# .env (never commit this file)
DASHSCOPE_API_KEY=sk-your-real-key-here
```

- [ ] **Step 4: Create requirements.txt**

```
dashscope>=1.14.0
pandas>=2.0.0
plotly>=5.15.0
streamlit>=1.28.0
pytest>=7.4.0
python-dotenv>=1.0.0
```

- [ ] **Step 5: Install dependencies**

```bash
pip install -r requirements.txt
```

- [ ] **Step 6: Create src/__init__.py**

```python
# budget-negotiator src package
```

- [ ] **Step 7: Create tests/__init__.py**

```python
# budget-negotiator tests package
```

- [ ] **Step 8: Create handler.py — FC entry point**

```python
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
```

- [ ] **Step 9: Verify Qwen API works — create test script**

```python
# test_qwen_connection.py
import os
from dotenv import load_dotenv
import dashscope
from dashscope import Generation

load_dotenv()
dashscope.api_key = os.environ["DASHSCOPE_API_KEY"]

response = Generation.call(
    model="qwen-turbo",
    messages=[{"role": "user", "content": "Say hello in 5 words"}]
)
print(response.output.text)
```

- [ ] **Step 10: Run connection test**

```bash
python test_qwen_connection.py
```
Expected: Prints a 5-word greeting from Qwen

- [ ] **Step 11: Commit (with security check)**

```bash
git status  # Verify .env is NOT staged
git add .gitignore requirements.txt src/ tests/ .env
git commit -m "feat: project setup with .gitignore, env vars, and Qwen API verification"
```

**SECURITY CHECK:** Run `git status` and confirm `.env` is in `.gitignore` and NOT listed in staged files.

- [ ] **Step 12: Deploy to Alibaba Cloud Function Compute**

```bash
# Install Alibaba Cloud Serverless Devs CLI
npm install -g @serverless-devs/s

# Configure credentials (get from Alibaba Cloud console)
s config add --accessKeyID YOUR_AK --accessKeySecret YOUR_SK --region cn-hangzhou

# Create s.yaml for FC deployment
cat > s.yaml << 'EOF'
edition: 3.0.0
name: budget-negotiator
access: default
vars:
  region: cn-hangzhou
resources:
  budget-negotiator:
    component: fc3
    props:
      region: cn-hangzhou
      functionName: budget-negotiator
      runtime: python3.10
      handler: src/handler.handler
      memorySize: 128
      timeout: 60
      environmentVariables:
        DASHSCOPE_API_KEY: ${env:DASHSCOPE_API_KEY}
      triggers:
        - triggerName: http-trigger
          triggerType: http
          triggerConfig:
            authType: anonymous
            methods:
              - POST
EOF

# Deploy
s deploy
```

- [ ] **Step 13: Verify live endpoint**

```bash
# Get the endpoint URL from deploy output
# Test with a real request
curl -X POST https://your-fc-endpoint.cn-hangzhou.fc.aliyuncs.com \
  -H "Content-Type: application/json" \
  -d '{"action":"analyze","transactions":[{"amount":100,"category":"food","description":"test"}]}'
```
Expected: HTTP 200 with JSON response

- [ ] **Step 14: Save endpoint URL**

```bash
# Save this for submission and Streamlit config
echo "FC_ENDPOINT=https://your-fc-endpoint.cn-hangzhou.fc.aliyuncs.com" >> .env
```

---

### Task 2: Data Models (Hours 4-5)

**Files:**
- Create: `src/models.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write failing test for Transaction model**

```python
# tests/test_models.py
from src.models import Transaction, CategorizedTransactions, BudgetPlan


def test_transaction_creation():
    t = Transaction(amount=45.50, category="food", description="Grocery store")
    assert t.amount == 45.50
    assert t.category == "food"
    assert t.description == "Grocery store"


def test_categorized_transactions_creation():
    cats = CategorizedTransactions(
        essential={"rent": 1200, "utilities": 150},
        discretionary={"entertainment": 80, "dining": 120},
        total=1550
    )
    assert cats.essential["rent"] == 1200
    assert cats.total == 1550


def test_budget_plan_creation():
    plan = BudgetPlan(
        original_spending=1550,
        proposed_spending=1300,
        savings=250,
        cuts={"entertainment": 60, "dining": 40},
        explanation="Cut discretionary spending by 50%"
    )
    assert plan.savings == 250
    assert plan.cuts["entertainment"] == 60
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_models.py -v
```
Expected: FAIL with "ModuleNotFoundError: No module named 'src.models'"

- [ ] **Step 3: Implement models.py**

```python
# src/models.py
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Transaction:
    amount: float
    category: str
    description: str


@dataclass
class CategorizedTransactions:
    essential: Dict[str, float] = field(default_factory=dict)
    discretionary: Dict[str, float] = field(default_factory=dict)
    total: float = 0.0


@dataclass
class BudgetPlan:
    original_spending: float
    proposed_spending: float
    savings: float
    cuts: Dict[str, float] = field(default_factory=dict)
    explanation: str = ""
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_models.py -v
```
Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/models.py tests/test_models.py
git commit -m "feat: add Transaction, CategorizedTransactions, BudgetPlan models"
```

---

### Task 3: Rules Engine — CSV Parsing (Hours 5-6)

**Files:**
- Create: `src/rules_engine.py`
- Create: `tests/test_rules_engine.py`

- [ ] **Step 1: Write failing test for parse_transactions**

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_rules_engine.py -v
```
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement parse_transactions**

```python
# src/rules_engine.py
from typing import List, Dict, Any
from src.models import Transaction, CategorizedTransactions


def parse_transactions(raw_data: List[Dict[str, Any]]) -> List[Transaction]:
    """Parse raw transaction dicts into Transaction objects."""
    transactions = []
    for item in raw_data:
        transactions.append(Transaction(
            amount=float(item.get("amount", 0)),
            category=item.get("category", "uncategorized"),
            description=item.get("description", "")
        ))
    return transactions
```

- [ ] **Step 4: Run parse tests to verify they pass**

```bash
pytest tests/test_rules_engine.py::test_parse_transactions_from_dicts tests/test_rules_engine.py::test_parse_handles_missing_fields -v
```
Expected: PASS

- [ ] **Step 5: Implement categorize_transactions**

```python
# Add to src/rules_engine.py

ESSENTIAL_CATEGORIES = {"rent", "utilities", "insurance", "healthcare", "transport"}
DISCRETIONARY_CATEGORIES = {"food", "entertainment", "dining", "shopping", "personal"}


def categorize_transactions(transactions: List[Transaction]) -> CategorizedTransactions:
    """Categorize transactions into essential vs discretionary."""
    essential = {}
    discretionary = {}
    total = 0.0

    for t in transactions:
        total += t.amount
        cat_lower = t.category.lower()

        if cat_lower in ESSENTIAL_CATEGORIES:
            essential[cat_lower] = essential.get(cat_lower, 0) + t.amount
        else:
            discretionary[cat_lower] = discretionary.get(cat_lower, 0) + t.amount

    return CategorizedTransactions(
        essential=essential,
        discretionary=discretionary,
        total=total
    )
```

- [ ] **Step 6: Run all rules engine tests**

```bash
pytest tests/test_rules_engine.py -v
```
Expected: All 4 tests PASS

- [ ] **Step 7: Commit**

```bash
git add src/rules_engine.py tests/test_rules_engine.py
git commit -m "feat: rules engine with CSV parsing and transaction categorization"
```

---

### Task 4: Qwen API Client (Hours 7-9)

**Files:**
- Create: `src/qwen_client.py`
- Create: `tests/test_qwen_client.py`

- [ ] **Step 1: Write failing test for build_prompt**

```python
# tests/test_qwen_client.py
from src.qwen_client import build_prompt, parse_recommendation
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_qwen_client.py -v
```
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement build_prompt**

```python
# src/qwen_client.py
import os
import json
import dashscope
from dashscope import Generation
from src.models import CategorizedTransactions, BudgetPlan

# Load API key from environment
dashscope.api_key = os.environ.get("DASHSCOPE_API_KEY", "")


def build_prompt(categorized: CategorizedTransactions, savings_goal) -> str:
    """Build the initial negotiation prompt for Qwen."""
    goal_text = (
        f"The user wants to save ${savings_goal} per month."
        if savings_goal != "auto"
        else "The user wants to save as much as possible without hurting essentials."
    )

    prompt = f"""You are a budget negotiator. Analyze this spending and propose cuts.

MONTHLY SPENDING:
Essential: {json.dumps(categorized.essential, indent=2)}
Discretionary: {json.dumps(categorized.discretionary, indent=2)}
Total: ${categorized.total:.2f}

GOAL: {goal_text}

RULES:
1. Never cut essentials below survival level
2. Cut discretionary spending first (entertainment, dining, shopping)
3. Propose specific dollar amounts per category
4. Explain your reasoning clearly

Respond in this exact JSON format:
{{
    "cuts": {{"category": dollar_amount}},
    "savings": total_monthly_savings,
    "explanation": "Your explanation here"
}}"""

    return prompt
```

- [ ] **Step 4: Run prompt tests**

```bash
pytest tests/test_qwen_client.py::test_build_prompt_includes_categories tests/test_qwen_client.py::test_build_prompt_with_goal -v
```
Expected: PASS

- [ ] **Step 5: Implement parse_recommendation**

```python
# Add to src/qwen_client.py

def parse_recommendation(raw_response: str, original_total: float) -> BudgetPlan:
    """Parse Qwen's response into a BudgetPlan."""
    try:
        # Extract JSON from response
        start = raw_response.find("{")
        end = raw_response.rfind("}") + 1
        data = json.loads(raw_response[start:end])

        cuts = data.get("cuts", {})
        savings = data.get("savings", 0)
        explanation = data.get("explanation", "")

        return BudgetPlan(
            original_spending=original_total,
            proposed_spending=original_total - savings,
            savings=savings,
            cuts=cuts,
            explanation=explanation
        )
    except (json.JSONDecodeError, ValueError):
        return BudgetPlan(
            original_spending=original_total,
            proposed_spending=original_total,
            savings=0,
            cuts={},
            explanation="Failed to parse recommendation. Please try again."
        )
```

- [ ] **Step 6: Run parse tests**

```bash
pytest tests/test_qwen_client.py::test_parse_recommendation -v
```
Expected: PASS

- [ ] **Step 7: Implement get_budget_recommendation (initial API call)**

```python
# Add to src/qwen_client.py

def get_budget_recommendation(
    categorized_transactions: CategorizedTransactions,
    savings_goal
) -> dict:
    """Call Qwen API and return structured recommendation."""
    prompt = build_prompt(categorized_transactions, savings_goal)

    try:
        response = Generation.call(
            model="qwen-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
            timeout=30
        )

        if response.status_code != 200:
            return {
                "error": "Qwen API timeout or error",
                "fallback": True,
                "original_total": categorized_transactions.total,
                "essential": categorized_transactions.essential,
                "discretionary": categorized_transactions.discretionary
            }

        plan = parse_recommendation(response.output.text, categorized_transactions.total)

        return {
            "original_spending": plan.original_spending,
            "proposed_spending": plan.proposed_spending,
            "savings": plan.savings,
            "cuts": plan.cuts,
            "explanation": plan.explanation,
            "essential": categorized_transactions.essential,
            "discretionary": categorized_transactions.discretionary
        }

    except Exception as e:
        return {
            "error": f"Qwen API timeout: {str(e)}",
            "fallback": True,
            "original_total": categorized_transactions.total,
            "essential": categorized_transactions.essential,
            "discretionary": categorized_transactions.discretionary
        }
```

- [ ] **Step 8: Commit**

```bash
git add src/qwen_client.py tests/test_qwen_client.py
git commit -m "feat: Qwen API client with prompt building and response parsing"
```

---

### Task 5: Negotiation Logic — Qwen-Powered (Hours 10-11)

**Files:**
- Create: `src/negotiation.py`
- Create: `tests/test_negotiation.py`

**CRITICAL:** This task makes Qwen reason on EVERY negotiation turn, not just the first one.

- [ ] **Step 1: Write failing test for generate_counter_offer (mocks Qwen)**

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_negotiation.py -v
```
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement generate_counter_offer (Qwen-powered)**

```python
# src/negotiation.py
import os
import json
import dashscope
from dashscope import Generation

dashscope.api_key = os.environ.get("DASHSCOPE_API_KEY", "")


def generate_counter_offer(
    categorized: dict,
    previous_plan: dict,
    user_objection: str
) -> dict:
    """
    Generate counter-offer using Qwen API on EVERY turn.
    No local arithmetic — the LLM reasons about the tradeoff.
    """
    prompt = f"""You are a budget negotiator in a conversation with a user.

ORIGINAL SPENDING DATA:
Essential: {json.dumps(categorized.get("essential", {}), indent=2)}
Discretionary: {json.dumps(categorized.get("discretionary", {}), indent=2)}
Total: ${categorized.get("total", 0):.2f}

PREVIOUS PLAN YOU PROPOSED:
{json.dumps(previous_plan, indent=2)}

USER'S OBJECTION:
"{user_objection}"

TASK:
The user rejected part of your previous plan. Read their objection carefully.
They may reject a specific category, explain why, or propose an alternative.

Adjust the plan based on their feedback:
- If they reject a cut, reduce it or find savings elsewhere
- If they propose an alternative, incorporate it
- Always maintain the total savings target if possible
- Never cut essentials

Respond in this exact JSON format:
{{
    "cuts": {{"category": dollar_amount}},
    "savings": total_monthly_savings,
    "explanation": "Your explanation acknowledging their feedback and your adjustment"
}}"""

    try:
        response = Generation.call(
            model="qwen-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
            timeout=30
        )

        if response.status_code != 200:
            # Fallback: return previous plan unchanged
            return previous_plan

        # Parse Qwen's response
        raw = response.output.text
        start = raw.find("{")
        end = raw.rfind("}") + 1
        data = json.loads(raw[start:end])

        return {
            "cuts": data.get("cuts", {}),
            "savings": data.get("savings", 0),
            "explanation": data.get("explanation", ""),
            "essential": categorized.get("essential", {}),
            "discretionary": categorized.get("discretionary", {}),
            "original_spending": categorized.get("total", 0)
        }

    except Exception:
        # On any error, return previous plan unchanged
        return previous_plan
```

- [ ] **Step 4: Run counter offer test (with mocked Qwen)**

```bash
pytest tests/test_negotiation.py::test_generate_counter_offer_calls_qwen -v
```
Expected: PASS

- [ ] **Step 5: Implement format_budget_breakdown**

```python
# Add to src/negotiation.py


def format_budget_breakdown(plan: dict) -> str:
    """Format budget plan as readable text."""
    lines = [
        "=== BUDGET NEGOTIATION PLAN ===",
        f"\nOriginal Spending: ${plan.get('original_spending', 0):,.2f}",
        f"Proposed Spending: ${plan.get('proposed_spending', 0):,.2f}",
        f"Monthly Savings:   ${plan.get('savings', 0):,.2f}",
        "\n--- PROPOSED CUTS ---"
    ]

    for category, amount in plan.get("cuts", {}).items():
        lines.append(f"  {category}: -${amount:.2f}")

    lines.append(f"\n--- REASONING ---")
    lines.append(plan.get("explanation", ""))

    return "\n".join(lines)
```

- [ ] **Step 6: Run format test**

```bash
pytest tests/test_negotiation.py::test_format_budget_breakdown -v
```
Expected: PASS

- [ ] **Step 7: Run all negotiation tests**

```bash
pytest tests/test_negotiation.py -v
```
Expected: All tests PASS

- [ ] **Step 8: Commit**

```bash
git add src/negotiation.py tests/test_negotiation.py
git commit -m "feat: Qwen-powered negotiation with real reasoning on every turn"
```

---

### Task 6: Synthetic Demo Data (Hours 12-13)

**Files:**
- Create: `docs/demo-data/middle-class.csv`
- Create: `docs/demo-data/young-professional.csv`

- [ ] **Step 1: Create middle-class profile**

```csv
amount,category,description
1200,rent,Monthly apartment rent
150,utilities,Electric and water
80,insurance,Renter's insurance
300,food,Groceries
120,dining,Restaurants and takeout
80,entertainment,Netflix Spotify movies
60,shopping,Clothes and misc
100,transport,Gas and parking
50,healthcare,Pharmacy and copays
40,personal,Haircuts and grooming
```

- [ ] **Step 2: Create young-professional profile**

```csv
amount,category,description
900,rent,Studio apartment
100,utilities,Electric and internet
45,insurance,Health insurance supplement
200,food,Groceries and meal prep
180,dining,Restaurants and bars
60,entertainment,Streaming subscriptions
120,shopping,Clothes tech gadgets
80,transport,Uber and gas
30,healthcare,Pharmacy
25,personal,Gym membership
```

- [ ] **Step 3: Commit**

```bash
git add docs/demo-data/
git commit -m "feat: add synthetic demo data for middle-class and young-professional profiles"
```

---

### Task 7: Streamlit UI — Chat Interface (Hours 14-17)

**Files:**
- Create: `streamlit/app.py`

- [ ] **Step 1: Create basic Streamlit app skeleton**

```python
# streamlit/app.py
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Budget Negotiator", layout="wide")
st.title("Budget Negotiator")
st.caption("AI-powered budget analysis and negotiation")

# Session state for conversation
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_plan" not in st.session_state:
    st.session_state.current_plan = None
if "categorized" not in st.session_state:
    st.session_state.categorized = None
```

- [ ] **Step 2: Add sidebar with data input options**

```python
# Add to app.py after page config

with st.sidebar:
    st.header("Data Input")

    input_method = st.radio(
        "How would you like to input spending?",
        ["Upload CSV", "Use Demo Data"]
    )

    if input_method == "Upload CSV":
        uploaded_file = st.file_uploader("Upload your spending CSV", type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df)
    else:
        demo_profile = st.selectbox(
            "Choose a demo profile",
            ["Middle Class ($1,580/mo)", "Young Professional ($1,740/mo)"]
        )

    FC_ENDPOINT = st.text_input(
        "Function Compute Endpoint",
        value=os.environ.get("FC_ENDPOINT", "https://your-fc-endpoint.cn-hangzhou.fc.aliyuncs.com")
    )
```

- [ ] **Step 3: Add main chat area**

```python
# Add to app.py

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Ask about your budget or reject a suggestion...")
```

- [ ] **Step 4: Add chart display function**

```python
# Add to app.py

def display_spending_chart(plan: dict):
    """Display spending breakdown as pie chart."""
    all_categories = {}
    all_categories.update(plan.get("essential", {}))
    all_categories.update(plan.get("discretionary", {}))

    if all_categories:
        fig = px.pie(
            values=list(all_categories.values()),
            names=list(all_categories.keys()),
            title="Spending Breakdown"
        )
        st.plotly_chart(fig, use_container_width=True)
```

- [ ] **Step 5: Commit**

```bash
git add streamlit/app.py
git commit -m "feat: Streamlit UI skeleton with chat and data input"
```

---

### Task 8: Streamlit — API Integration + Negotiation Flow (Hours 18-20)

**Files:**
- Modify: `streamlit/app.py`

**CRITICAL:** Every negotiation turn goes to Qwen via the FC endpoint, not local Python.

- [ ] **Step 1: Add budget analysis function**

```python
# Add to app.py

def analyze_budget(transactions: list, goal: str = "auto"):
    """Call FC endpoint for initial budget analysis."""
    try:
        response = requests.post(
            FC_ENDPOINT,
            json={"action": "analyze", "transactions": transactions, "savings_goal": goal},
            timeout=70
        )
        return response.json()
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except Exception as e:
        return {"error": str(e)}
```

- [ ] **Step 2: Add Qwen-powered negotiation function**

```python
# Add to app.py

def negotiate_budget(categorized: dict, previous_plan: dict, user_objection: str):
    """Call FC endpoint for negotiation — Qwen reasons on every turn."""
    try:
        response = requests.post(
            FC_ENDPOINT,
            json={
                "action": "negotiate",
                "categorized": categorized,
                "previous_plan": previous_plan,
                "user_objection": user_objection
            },
            timeout=70
        )
        return response.json()
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except Exception as e:
        return {"error": str(e)}
```

- [ ] **Step 3: Add format_response helper**

```python
# Add to app.py

def format_response(plan: dict) -> str:
    """Format plan as readable response."""
    if "error" in plan:
        return f"Error: {plan['error']}"

    lines = [
        f"## Budget Analysis",
        f"**Original:** ${plan.get('original_spending', 0):,.2f}/mo",
        f"**Proposed:** ${plan.get('proposed_spending', 0):,.2f}/mo",
        f"**Savings:** ${plan.get('savings', 0):,.2f}/mo",
        "",
        "### Proposed Cuts:"
    ]

    for cat, amount in plan.get("cuts", {}).items():
        lines.append(f"- **{cat}:** -${amount:.2f}")

    lines.append(f"\n*{plan.get('explanation', '')}*")
    lines.append("\n> Tell me what you'd like to change, or explain why a cut doesn't work for you.")

    return "\n".join(lines)
```

- [ ] **Step 4: Add message handling logic (Qwen on every turn)**

```python
# Add to app.py

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    if user_input.lower() in ["analyze", "start", "begin"]:
        # Trigger initial analysis
        if input_method == "Upload CSV" and uploaded_file:
            transactions = df.to_dict("records")
        else:
            profile_file = "middle-class.csv" if "Middle" in demo_profile else "young-professional.csv"
            transactions = pd.read_csv(f"docs/demo-data/{profile_file}").to_dict("records")

        result = analyze_budget(transactions)

        if "error" in result:
            response = f"Error: {result['error']}"
        else:
            st.session_state.current_plan = result
            st.session_state.categorized = {
                "essential": result.get("essential", {}),
                "discretionary": result.get("discretionary", {}),
                "total": result.get("original_spending", 0)
            }
            response = format_response(result)

    elif st.session_state.current_plan:
        # NEW: Every non-analyze message goes to Qwen for negotiation
        result = negotiate_budget(
            categorized=st.session_state.categorized,
            previous_plan=st.session_state.current_plan,
            user_objection=user_input  # Full user text, no string matching
        )

        if "error" in result:
            response = f"Error: {result['error']}"
        else:
            st.session_state.current_plan = result
            response = format_response(result)
    else:
        response = "Type 'analyze' to start your budget analysis."

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
```

- [ ] **Step 5: Add chart display to main flow**

```python
# Add AFTER the chat message loop, at root level of the script (NOT inside if user_input:)
# This ensures the chart persists across reruns — not just the frame where user_input fires

if st.session_state.current_plan:
    display_spending_chart(st.session_state.current_plan)
```

- [ ] **Step 6: Commit**

```bash
git add streamlit/app.py
git commit -m "feat: Streamlit with Qwen-powered negotiation on every turn"
```

---

### Task 9: Error Handling (Hours 21-22)

**Files:**
- Modify: `src/rules_engine.py`
- Modify: `src/qwen_client.py`

- [ ] **Step 1: Add validation to rules_engine.py**

```python
# Add to src/rules_engine.py

def validate_transactions(transactions: list) -> list:
    """Validate and clean transaction data."""
    valid = []
    for t in transactions:
        if not isinstance(t, dict):
            continue
        amount = t.get("amount")
        if amount is None or not isinstance(amount, (int, float)):
            continue
        if float(amount) < 0:
            continue
        valid.append(t)
    return valid
```

- [ ] **Step 2: Update parse_transactions to use validation**

```python
# Update parse_transactions in src/rules_engine.py

def parse_transactions(raw_data: list) -> list:
    """Parse and validate raw transaction data."""
    validated = validate_transactions(raw_data)
    transactions = []
    for item in validated:
        transactions.append(Transaction(
            amount=float(item.get("amount", 0)),
            category=item.get("category", "uncategorized"),
            description=item.get("description", "")
        ))
    return transactions
```

- [ ] **Step 3: Run all tests**

```bash
pytest tests/ -v
```
Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
git add src/rules_engine.py
git commit -m "feat: add input validation for transaction data"
```

---

### Task 10: Integration Testing (Hours 23-24)

**Files:**
- Create: `tests/test_integration.py`

- [ ] **Step 1: Write integration test**

```python
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
```

- [ ] **Step 2: Run integration tests**

```bash
pytest tests/test_integration.py -v
```
Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "feat: integration tests for full pipeline and negotiation flow"
```

---

### Task 11: Demo Preparation (Hours 25-27)

**Files:**
- Create: `docs/architecture.md`
- Create: `README.md`
- Create: `LICENSE`

- [ ] **Step 1: Create architecture.md**

```markdown
# Architecture

## Overview

Budget Negotiator is a hybrid AI agent that analyzes spending data and negotiates budget cuts through conversation. Unlike a spreadsheet, it reasons about tradeoffs on every turn using Qwen API.

## Components

### Streamlit UI
- Chat interface for user interaction
- File upload for CSV spending data
- Plotly charts for spending visualization

### Alibaba Cloud Function Compute
- Serverless backend for agent logic
- Python runtime with Qwen API integration
- Entry point: handler.py
- **Live endpoint:** (insert URL after deployment)

### Rules Engine
- CSV parsing and validation
- Transaction categorization (essential vs discretionary)
- Deterministic, no API cost

### Qwen API (dashscope)
- Budget reasoning and cut proposals (initial analysis)
- Conversational negotiation (every turn)
- Natural language explanations

## Data Flow

### Initial Analysis
1. User uploads CSV or selects demo data
2. Streamlit sends transactions to FC endpoint
3. Rules Engine parses and categorizes
4. Qwen API reasons about cuts
5. Response returned to Streamlit

### Negotiation (Every Turn)
1. User types objection in natural language
2. Streamlit sends: categorized data + previous plan + user text to FC
3. FC calls Qwen with full context
4. Qwen reasons about the tradeoff and adjusts plan
5. Updated plan returned to Streamlit

## Error Handling

- Malformed CSV → structured error response
- Qwen API timeout → fallback to previous plan
- Invalid input → validation before processing
```

- [ ] **Step 2: Create README.md**

```markdown
# Budget Negotiator

AI-powered budget analysis and negotiation agent. Upload your spending data, and the agent will analyze it, propose cuts, and negotiate a savings plan with you through natural conversation.

## Features

- CSV upload for spending data
- AI-powered budget analysis
- Conversational negotiation — push back on any cut and the agent reasons about tradeoffs
- Spending visualization charts
- Two demo profiles included

## How It Works

1. Upload your spending CSV or use a demo profile
2. The agent categorizes your spending and proposes cuts
3. Push back on any suggestion — "I can't cut dining, parents are visiting"
4. The agent adjusts and finds alternatives

## Tech Stack

- Python 3.10+
- Alibaba Cloud Function Compute (serverless)
- Qwen API (dashscope) — reasons on every negotiation turn
- Streamlit — chat UI
- Plotly — spending charts

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Set up `.env` with your `DASHSCOPE_API_KEY`
3. Run Streamlit: `cd streamlit && streamlit run app.py`
4. Upload your spending CSV or use demo data
5. Type "analyze" to start

## Deployment

Deployed on Alibaba Cloud Function Compute.
See `src/handler.py` for the FC entry point.

## Demo Data

Two synthetic profiles included:
- Middle Class ($1,580/mo) — rent, utilities, groceries, subscriptions
- Young Professional ($1,740/mo) — studio apartment, meal prep, streaming

## License

MIT
```

- [ ] **Step 3: Create LICENSE**

```
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 4: Commit**

```bash
git add docs/architecture.md README.md LICENSE
git commit -m "docs: add architecture, README, and MIT license"
```

---

### Task 12: Demo Video Script (Hours 28-29)

**Files:**
- Create: `docs/demo-script.md`

- [ ] **Step 1: Write demo script**

```markdown
# Demo Video Script (3 minutes)

## 0:00-0:15 — Problem
"If you've ever wondered where your paycheck went by the end of the month, you're not alone. Most budgeting tools just show you what you spent. They don't help you figure out what to cut."

## 0:15-0:45 — What the agent does
"Budget Negotiator is an AI agent that analyzes your spending and negotiates a savings plan with you. Upload your transaction CSV, and the agent categorizes your spending, identifies where you can cut, and proposes a realistic budget."

## 0:45-1:30 — Live demo (initial analysis)
[Show CSV upload → analysis → budget proposal]
"Here's a middle-class profile spending $1,580 a month. The agent proposes cutting entertainment by $40 and dining by $30."

## 1:30-2:15 — Live demo (negotiation)
[Show rejection → Qwen reasoning → counter-offer]
"But what if I push back? 'I can't cut dining that much, parents are visiting next month.' Watch — the agent reads my objection, understands the context, and adjusts. It reduces the dining cut and finds savings elsewhere. Every turn, it's reasoning about tradeoffs."

## 2:15-2:45 — Why it's not just a spreadsheet
"A spreadsheet can subtract numbers. This agent reasons about tradeoffs on every turn. It knows essentials come first. It adapts when you push back. It learns your priorities through conversation."

## 2:45-2:50 — Tech
"Built with Qwen API on Alibaba Cloud Function Compute. Rules engine handles data parsing. Qwen handles the intelligence on every negotiation turn."

## 2:50-3:00 — Closing
"Budget Negotiator — because saving money shouldn't feel like homework."
```

- [ ] **Step 2: Commit**

```bash
git add docs/demo-script.md
git commit -m "docs: add demo video script"
```

---

### Task 13: Final Polish + Submission Prep (Hour 30)

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Verify all tests pass**

```bash
pytest tests/ -v
```
Expected: All tests PASS

- [ ] **Step 2: Verify Streamlit runs**

```bash
cd streamlit && streamlit run app.py
```
Expected: App opens in browser

- [ ] **Step 3: Streamlit smoke test — negotiation path end-to-end**

Manually exercise the reject/counter-offer path in the running Streamlit app:
1. Select "Use Demo Data" → "Middle Class" profile
2. Type "analyze" — confirm budget analysis appears with cuts
3. Type "I can't cut dining that much, parents are visiting next month"
4. Confirm you get a **reasoned counter-offer from Qwen** (not a `NameError` stack trace)
5. Verify the chart updates with revised spending

This catches UI-scope variable wiring bugs that pytest mocks will not surface.

- [ ] **Step 4: Verify .env is gitignored**

```bash
git status
```
Expected: `.env` NOT listed in untracked files

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "feat: final polish and submission prep"
```

- [ ] **Step 6: Record deployment proof video (~30–60 sec)**

Record a **separate, short screen recording** showing the backend is actually running on Alibaba Cloud:
1. Show the live FC endpoint URL in the FC console (or terminal output from `s deploy`)
2. Run a `curl` (or Postman) call hitting that endpoint
3. Show the real JSON response coming back

Save this as a **separate file** from the 3-minute demo video — do not combine them.

- [ ] **Step 7: Record 3-minute demo video**

Follow `docs/demo-script.md`, keep under 3 minutes. Show real negotiation with natural language objection.

- [ ] **Step 8: Submit to hackathon**

Upload to YouTube or Vimeo, fill submission form with:
- Track: Autopilot Agent
- Deployment proof: live FC endpoint URL + link to `src/handler.py`
- Deployment proof recording: [separate link from Step 6]
- Architecture diagram
- Demo video: [YouTube or Vimeo link]

---

## Self-Review Checklist

- [ ] All 13 tasks have actual code, no placeholders
- [ ] Error paths drawn in architecture and implemented in code
- [ ] Alibaba Cloud FC deployment proof is REAL — endpoint verified with curl
- [ ] .gitignore in place before first commit — no API keys in repo
- [ ] Negotiation uses Qwen on EVERY turn — no local arithmetic fallback
- [ ] Synthetic data ready for demo
- [ ] Demo script under 3 minutes, shows natural language objection
- [ ] All tests pass
- [ ] README and LICENSE in place
