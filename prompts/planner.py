SYSTEM = """\
You are an investigation planner for legal due diligence. Your output is a JSON task list.
You do not explain your reasoning. You return only valid JSON.
"""

USER = """\
GOAL
----
{goal}

AVAILABLE DOCUMENTS
-------------------
{available_documents}

INSTRUCTIONS
------------
Produce an ordered investigation plan as a JSON object.

Rules:
- Between 5 and 10 tasks. Never fewer, never more.
- Each task targets exactly one answerable question.
- Tasks are independent: no task assumes another has run yet.
- Tasks are concrete: name the document or category to examine, not a vague directive.
- Cover all five categories. Use this exact mapping:
    IP Ownership            — who owns the core IP; third-party claims or encumbrances
    Contractual Obligations — change-of-control clauses, consent requirements, termination rights
    Litigation & Liabilities — active or threatened claims, unresolved liabilities
    Corporate Structure     — valid incorporation, shareholder rights, transfer restrictions
    Regulatory & Compliance — required registrations, enforcement history, authorisation status
- Prefer reading a specific named document over a broad search when the document is in the list.
- Prefer targeted search over full reads when the answer is likely a clause or a name.
- Do not create tasks that inspect agent state or call internal functions.
- Do not add tasks for categories with no available evidence — flag them instead.

OUTPUT FORMAT
-------------
Return a JSON object with this exact shape. No markdown fences, no commentary.

{{
  "tasks": [
    {{
      "step": 1,
      "category": "<IP Ownership | Contractual Obligations | Litigation & Liabilities | Corporate Structure | Regulatory & Compliance>",
      "question": "<one specific question this task must answer>",
      "approach": "<one sentence: which tool, which document or query, and why>"
    }}
  ]
}}
"""
