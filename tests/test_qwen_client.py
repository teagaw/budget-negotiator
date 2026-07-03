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