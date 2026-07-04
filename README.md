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

## Tests

77 tests · 100% coverage — `pytest tests/`

## Deployment

Deployed on Alibaba Cloud Function Compute.
See `src/handler.py` for the FC entry point.

**Authentication**: The FC endpoint uses shared-secret auth via the `X-API-Key` header.
Set `FUNCTION_API_KEY` in your FC console environment (or `.env` for local dev).
When `FUNCTION_API_KEY` is empty, auth is skipped (local dev mode).

## Demo Data

Two synthetic profiles included:
- Middle Class ($2,180/mo) — rent, utilities, groceries, subscriptions
- Young Professional ($1,740/mo) — studio apartment, meal prep, streaming

## License

MIT
