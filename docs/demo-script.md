# Demo Video Script (3 minutes)

## 0:00-0:15 — Problem
"If you've ever wondered where your paycheck went by the end of the month, you're not alone. Most budgeting tools just show you what you spent. They don't help you figure out what to cut."

## 0:15-0:45 — What the agent does
"Budget Negotiator is an AI agent that analyzes your spending and negotiates a savings plan with you. Upload your transaction CSV, and the agent categorizes your spending, identifies where you can cut, and proposes a realistic budget."

## 0:45-1:30 — Live demo (initial analysis)
[Show CSV upload → analysis → budget proposal]
"Here's a middle-class profile spending $1,580 a month. The agent proposes cutting entertainment by $40 and dining by $30."
[Show the budget breakdown with savings highlighted]

## 1:30-1:50 — Accept checkpoint
"Once the agent proposes a plan, you can accept it or keep negotiating. Let's say I want to push back."
[Click ✓ Accept — show success state]
"Or I can accept the plan and start fresh with a new analysis."
[Click "Start New Analysis" — reset flow]

## 1:50-2:30 — Live demo (negotiation)
[Show rejection → Qwen reasoning → counter-offer]
"But what if I push back? 'I can't cut dining that much, parents are visiting next month.' Watch — the agent reads my objection, understands the context, and adjusts. It reduces the dining cut and finds savings elsewhere."
[Type vague objection: "just save me more somehow"]
"Even when I type something vague — 'just save me more somehow' — the agent doesn't crash. It reasons about what that means given the current plan, and proposes a revised breakdown. Every turn, it's reasoning about tradeoffs."

## 2:30-2:50 — Why it's not just a spreadsheet
"A spreadsheet can subtract numbers. This agent reasons about tradeoffs on every turn. It knows essentials come first. It adapts when you push back. It learns your priorities through conversation."

## 2:50-2:55 — Tech
"Built with Qwen API on Alibaba Cloud Function Compute. Rules engine handles data parsing. Qwen handles the intelligence on every negotiation turn."

## 2:55-3:00 — Closing
"Budget Negotiator — because saving money shouldn't feel like homework."
