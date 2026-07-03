# streamlit/app.py
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

# FC endpoint
FC_ENDPOINT = os.environ.get("FC_ENDPOINT", "https://your-fc-endpoint.cn-hangzhou.fc.aliyuncs.com")

# Sidebar — data input
with st.sidebar:
    st.header("Data Input")

    input_method = st.radio(
        "How would you like to input spending?",
        ["Upload CSV", "Use Demo Data"]
    )

    uploaded_file = None
    df = None
    demo_profile = None

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
        value=FC_ENDPOINT
    )


# Chart display function — ROOT LEVEL, not inside if user_input:
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


# API functions
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


# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Ask about your budget or reject a suggestion...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    if user_input.lower() in ["analyze", "start", "begin"]:
        # Trigger initial analysis
        if input_method == "Upload CSV" and uploaded_file:
            transactions = df.to_dict("records")
        else:
            profile_file = "middle-class.csv" if "Middle" in demo_profile else "young-professional.csv"
            transactions = pd.read_csv(os.path.join(BASE_DIR, "docs", "demo-data", profile_file)).to_dict("records")

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
        # Every non-analyze message goes to Qwen for negotiation
        result = negotiate_budget(
            categorized=st.session_state.categorized,
            previous_plan=st.session_state.current_plan,
            user_objection=user_input
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

# Chart at root level — persists across reruns
if st.session_state.current_plan:
    display_spending_chart(st.session_state.current_plan)
