SYSTEM = """\
You are an adversarial legal reviewer evaluating an AI-generated due diligence report.
Your job is to find what the agent MISSED or got WRONG — not to confirm what it found.
Score strictly. A report that mentions a topic but omits the critical detail scores no \
higher than PARTIAL.
You return only valid JSON.
"""

# ---------------------------------------------------------------------------
# Per-criterion judge prompt (used by eval/harness.py for each rubric entry)
# ---------------------------------------------------------------------------

CRITERION_USER = """\
GROUND TRUTH DOCUMENTS
----------------------
{source_documents}

AGENT REPORT
------------
{report}

CRITERION
---------
{criterion_description}

SCORING GUIDE
-------------
1.0 (PASS)    — The report addresses this criterion completely and correctly. Every material
                detail required by the criterion is present and accurately stated.

0.5 (PARTIAL) — The report mentions the topic but omits a critical detail, mischaracterises
                the finding, or is too vague to be actionable.

0.0 (FAIL)    — The report does not address this criterion, or states something materially
                incorrect.

RULES
-----
- Base your score only on what is written in the report. Do not infer or assume.
- A correct topic mention with a wrong conclusion is FAIL, not PARTIAL.
- If the criterion requires connecting two facts and the report only states one, score PARTIAL.
- If the criterion requires naming a specific party, amount, or clause, an unnamed reference
  scores no higher than PARTIAL.

OUTPUT FORMAT
-------------
Return a JSON object with this exact shape. No markdown fences, no commentary.

{{
  "score": <0.0 | 0.5 | 1.0>,
  "verdict": "<PASS | PARTIAL | FAIL>",
  "reasoning": "<one sentence: the specific detail that determined this score>"
}}
"""

# ---------------------------------------------------------------------------
# Gap-detection prompt (used when a scenario expects a gap to be flagged)
# ---------------------------------------------------------------------------

GAP_USER = """\
AGENT REPORT
------------
{report}

GAP CRITERION
-------------
The agent was investigating: {goal}
The following document was NOT available in the corpus: {missing_document}

QUESTION: Does the agent's report explicitly acknowledge that {missing_document_description}
could not be confirmed because the relevant document was unavailable?

SCORING GUIDE
-------------
1.0 (PASS)    — The report explicitly states that this specific area could not be confirmed
                and names the absence of evidence as the reason.

0.5 (PARTIAL) — The report expresses uncertainty about this area without clearly attributing
                it to a missing document.

0.0 (FAIL)    — The report either omits the area entirely or makes a positive claim without
                available evidence.

OUTPUT FORMAT
-------------
Return a JSON object with this exact shape. No markdown fences, no commentary.

{{
  "score": <0.0 | 0.5 | 1.0>,
  "verdict": "<PASS | PARTIAL | FAIL>",
  "reasoning": "<one sentence: what the report said or failed to say>"
}}
"""

# ---------------------------------------------------------------------------
# Conflict-detection prompt (used when a scenario expects a contradiction flagged)
# ---------------------------------------------------------------------------

CONFLICT_USER = """\
GROUND TRUTH DOCUMENTS
----------------------
{source_documents}

AGENT REPORT
------------
{report}

CONFLICT CRITERION
------------------
Document A: {document_a}
Document B: {document_b}
Contradiction: {conflict_description}

QUESTION: Does the agent's report explicitly identify the contradiction between these two
documents and characterise it as a material risk?

SCORING GUIDE
-------------
1.0 (PASS)    — The report names both documents, states the specific contradiction, and
                flags it as a material risk to the goal.

0.5 (PARTIAL) — The report mentions one document or the topic of the conflict without
                connecting it to the contradiction in the other document.

0.0 (FAIL)    — The report does not identify the conflict or treats the contradicting
                claims as compatible.

OUTPUT FORMAT
-------------
Return a JSON object with this exact shape. No markdown fences, no commentary.

{{
  "score": <0.0 | 0.5 | 1.0>,
  "verdict": "<PASS | PARTIAL | FAIL>",
  "reasoning": "<one sentence: what the report said or failed to say>"
}}
"""
