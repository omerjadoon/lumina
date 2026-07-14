"""
Hidden evaluation rubric for the Legal Investigation Agent.

Written BEFORE agent implementation. Each criterion is scored by an
adversarial LLM judge (temperature=0) that receives:
  - The criterion's ground-truth source documents (from master corpus)
  - The agent's final report
  - A skeptical judge prompt that demands specific evidence of reasoning

Scores: PASS=1.0, PARTIAL=0.5, FAIL=0.0
"""

from dataclasses import dataclass


@dataclass
class Criterion:
    id: str
    category: str
    description: str
    required: bool
    relevant_documents: list[str]  # filenames from master corpus (ground truth for judge)
    judge_prompt: str              # adversarial prompt sent to the LLM judge


RUBRIC: list["Criterion"] = [

    Criterion(
        id="IP-01",
        category="IP Ownership",
        description="Confirms LexScan v1 IP was assigned from founder to Nexus",
        required=True,
        relevant_documents=["nexus_ip_assignment.txt"],
        judge_prompt="""
You are an adversarial legal reviewer evaluating an AI agent's due diligence report.
Your job is to find what the agent MISSED or got WRONG, not to confirm what it found.

GROUND TRUTH DOCUMENT:
{source_documents}

AGENT REPORT:
{report}

CRITERION: The agent must confirm that LexScan v1 intellectual property was formally
assigned from Dr. Elena Vasquez (the founder) to Nexus Legal Technologies, and that
this assignment is documented.

Score the agent's report:
- 1.0 (PASS): The report explicitly confirms the IP assignment from Vasquez to Nexus,
  references the assignment agreement, and notes it covers LexScan v1 and the patent application.
- 0.5 (PARTIAL): The report mentions IP ownership or the founder's role but is vague
  about the formal assignment document or its scope.
- 0.0 (FAIL): The report does not address IP assignment, or incorrectly states ownership.

Respond in JSON: {"score": <0.0|0.5|1.0>, "verdict": "<PASS|PARTIAL|FAIL>", "reasoning": "<one sentence>"}
""",
    ),

    Criterion(
        id="IP-02",
        category="IP Ownership",
        description="Flags Imperial College licence as non-transferable with joint-ownership risk on derivatives",
        required=True,
        relevant_documents=["nexus_ip_assignment.txt", "nexus_university_licence.txt"],
        judge_prompt="""
You are an adversarial legal reviewer evaluating an AI agent's due diligence report.
Your job is to find what the agent MISSED or got WRONG, not to confirm what it found.

GROUND TRUTH DOCUMENTS:
{source_documents}

AGENT REPORT:
{report}

CRITERION: The agent must identify a specific conflict between two documents:
1. The IP Assignment states Vasquez is "sole inventor" with no third-party claims.
2. The Imperial College licence (predating the assignment) grants Vasquez use of ImperialNLP
   under terms that: (a) are non-transferable without Imperial's written consent, and
   (b) make any derivatives of ImperialNLP jointly owned by Imperial and Vasquez.

If LexScan v1 is a derivative of ImperialNLP (which the licence does not exclude), then:
- Nexus may not own LexScan v1 outright
- The licence cannot be transferred to an acquirer without Imperial's consent
- The founder's "sole inventor" representation may be materially misleading

A passing report must surface this conflict explicitly — not merely mention Imperial College.

Score the agent's report:
- 1.0 (PASS): The report explicitly identifies the conflict between the IP assignment's
  sole-inventor claim and the Imperial licence's joint-ownership and non-transferability
  terms, and flags this as a material acquisition risk.
- 0.5 (PARTIAL): The report mentions the Imperial licence or the non-transferability
  but does not connect it to the conflict with the IP assignment.
- 0.0 (FAIL): The report does not mention the Imperial licence or misses the conflict entirely.

Respond in JSON: {"score": <0.0|0.5|1.0>, "verdict": "<PASS|PARTIAL|FAIL>", "reasoning": "<one sentence>"}
""",
    ),

    Criterion(
        id="CONTRACT-01",
        category="Contractual Obligations",
        description="Identifies change-of-control termination right in the Alpha & Partners contract",
        required=True,
        relevant_documents=["nexus_client_contract_lawfirm_alpha.txt"],
        judge_prompt="""
You are an adversarial legal reviewer evaluating an AI agent's due diligence report.
Your job is to find what the agent MISSED or got WRONG, not to confirm what it found.

GROUND TRUTH DOCUMENT:
{source_documents}

AGENT REPORT:
{report}

CRITERION: The agent must identify that the Master Services Agreement with Alpha & Partners LLP
contains a change-of-control clause (Clause 4) giving the client the right to terminate with
30 days' notice if Nexus undergoes a change of control (defined as >50% voting share acquisition).
A Orion Capital acquisition would trigger this clause directly.

Score the agent's report:
- 1.0 (PASS): The report explicitly identifies the change-of-control termination right,
  names Alpha & Partners, and notes that the proposed acquisition would trigger it.
- 0.5 (PARTIAL): The report mentions the change-of-control clause or client contracts
  but does not clearly connect it to the acquisition trigger.
- 0.0 (FAIL): The report does not identify the clause or incorrectly characterises it.

Respond in JSON: {"score": <0.0|0.5|1.0>, "verdict": "<PASS|PARTIAL|FAIL>", "reasoning": "<one sentence>"}
""",
    ),

    Criterion(
        id="CONTRACT-02",
        category="Contractual Obligations",
        description="Flags that only one client contract was reviewed — gap in contractual coverage",
        required=False,
        relevant_documents=["nexus_client_contract_lawfirm_alpha.txt"],
        judge_prompt="""
You are an adversarial legal reviewer evaluating an AI agent's due diligence report.
Your job is to find what the agent MISSED or got WRONG, not to confirm what it found.

GROUND TRUTH DOCUMENT:
{source_documents}

AGENT REPORT:
{report}

CRITERION: The document corpus contains only one client contract (Alpha & Partners). A thorough
agent should notice this limitation and explicitly flag that it cannot confirm whether other
client agreements contain similar change-of-control clauses. Silently concluding that
"the contract" has been reviewed without noting this gap is a failure of due diligence.

Score the agent's report:
- 1.0 (PASS): The report explicitly notes that only one client contract was available
  and that the change-of-control risk may extend to other undisclosed contracts.
- 0.5 (PARTIAL): The report implies uncertainty about contract coverage without
  explicitly naming the gap.
- 0.0 (FAIL): The report treats the single contract review as complete without caveat.

Respond in JSON: {"score": <0.0|0.5|1.0>, "verdict": "<PASS|PARTIAL|FAIL>", "reasoning": "<one sentence>"}
""",
    ),

    Criterion(
        id="LIT-01",
        category="Litigation & Liabilities",
        description="Identifies the active DataVault dispute (£150k, pre-action)",
        required=True,
        relevant_documents=["nexus_litigation_register.txt"],
        judge_prompt="""
You are an adversarial legal reviewer evaluating an AI agent's due diligence report.
Your job is to find what the agent MISSED or got WRONG, not to confirm what it found.

GROUND TRUTH DOCUMENT:
{source_documents}

AGENT REPORT:
{report}

CRITERION: The litigation register records an active pre-action dispute with DataVault Ltd
(LIT-2023-004): breach of contract claim for £150,000, with external counsel estimating
40% probability of proceedings. The agent must surface this as an unresolved contingent liability.

Score the agent's report:
- 1.0 (PASS): The report identifies DataVault, the £150k claim amount, the pre-action
  status, and characterises it as a contingent liability requiring attention.
- 0.5 (PARTIAL): The report mentions active litigation or the DataVault matter
  without the full financial and procedural context.
- 0.0 (FAIL): The report misses the DataVault dispute or states there is no active litigation.

Respond in JSON: {"score": <0.0|0.5|1.0>, "verdict": "<PASS|PARTIAL|FAIL>", "reasoning": "<one sentence>"}
""",
    ),

    Criterion(
        id="LIT-02",
        category="Litigation & Liabilities",
        description="Flags anonymous IP training data threat and its conflict with the founder's sole-inventor representation",
        required=True,
        relevant_documents=["nexus_litigation_register.txt", "nexus_ip_assignment.txt"],
        judge_prompt="""
You are an adversarial legal reviewer evaluating an AI agent's due diligence report.
Your job is to find what the agent MISSED or got WRONG, not to confirm what it found.

GROUND TRUTH DOCUMENTS:
{source_documents}

AGENT REPORT:
{report}

CRITERION: The litigation register records a threatened claim (LIT-2023-007) from an
anonymous party alleging unauthorised use of proprietary training data in LexScan v1.
No proceedings have been issued, but the risk is rated "High" in the register.

Critically, this conflicts with the IP Assignment Agreement in which Vasquez represented
she was the "sole inventor" and that "no third party has any claim" over the assigned IP.
If the anonymous claim proceeds and succeeds, the IP assignment representation is materially false.

The agent must identify this threat AND explicitly connect it to the conflict with
the IP assignment representation. Finding one without the other is only a partial pass.

Score the agent's report:
- 1.0 (PASS): The report identifies the anonymous IP threat, rates it as high risk,
  and explicitly notes the conflict with Vasquez's sole-inventor representation in the
  IP assignment.
- 0.5 (PARTIAL): The report flags the anonymous threat or the IP representation conflict
  but does not connect both together.
- 0.0 (FAIL): The report misses the anonymous threat or treats it as low risk.

Respond in JSON: {"score": <0.0|0.5|1.0>, "verdict": "<PASS|PARTIAL|FAIL>", "reasoning": "<one sentence>"}
""",
    ),

    Criterion(
        id="CORP-01",
        category="Corporate Structure",
        description="Confirms valid UK incorporation under Companies Act 2006",
        required=False,
        relevant_documents=["nexus_incorporation_certificate.txt"],
        judge_prompt="""
You are an adversarial legal reviewer evaluating an AI agent's due diligence report.
Your job is to find what the agent MISSED or got WRONG, not to confirm what it found.

GROUND TRUTH DOCUMENT:
{source_documents}

AGENT REPORT:
{report}

CRITERION: The agent must confirm that Nexus Legal Technologies Ltd is validly incorporated
as a private limited company in England and Wales under the Companies Act 2006, with
company number 12345678. This is a baseline structural check.

Score the agent's report:
- 1.0 (PASS): The report confirms valid incorporation, references the Companies Act 2006
  or the company number, and notes no structural concerns at incorporation level.
- 0.5 (PARTIAL): The report confirms Nexus is a registered company but without
  specific detail.
- 0.0 (FAIL): The report does not address corporate structure or incorporation status.

Respond in JSON: {"score": <0.0|0.5|1.0>, "verdict": "<PASS|PARTIAL|FAIL>", "reasoning": "<one sentence>"}
""",
    ),

    Criterion(
        id="CORP-02",
        category="Corporate Structure",
        description="Flags Meridian Ventures drag-along rights and absence of the full investment agreement",
        required=False,
        relevant_documents=["nexus_shareholder_register.txt"],
        judge_prompt="""
You are an adversarial legal reviewer evaluating an AI agent's due diligence report.
Your job is to find what the agent MISSED or got WRONG, not to confirm what it found.

GROUND TRUTH DOCUMENT:
{source_documents}

AGENT REPORT:
{report}

CRITERION: The shareholder register shows Meridian Ventures holds 20% (Preferred B shares)
with drag-along rights and standard protective provisions under a shareholders' agreement
dated 15 April 2022. The full shareholders' agreement is not in the corpus — only a summary
in the register. The agent must flag Meridian's drag-along rights and note that the full
agreement was not independently reviewed.

Score the agent's report:
- 1.0 (PASS): The report identifies Meridian Ventures, their drag-along rights, and
  explicitly notes that the full shareholders' agreement was not available for review.
- 0.5 (PARTIAL): The report mentions Meridian or the drag-along rights without flagging
  the missing agreement.
- 0.0 (FAIL): The report does not address the shareholder structure or Meridian's position.

Respond in JSON: {"score": <0.0|0.5|1.0>, "verdict": "<PASS|PARTIAL|FAIL>", "reasoning": "<one sentence>"}
""",
    ),

    Criterion(
        id="REG-01",
        category="Regulatory & Compliance",
        description="Confirms active ICO registration and absence of enforcement actions",
        required=False,
        relevant_documents=["nexus_regulatory_filing.txt"],
        judge_prompt="""
You are an adversarial legal reviewer evaluating an AI agent's due diligence report.
Your job is to find what the agent MISSED or got WRONG, not to confirm what it found.

GROUND TRUTH DOCUMENT:
{source_documents}

AGENT REPORT:
{report}

CRITERION: The agent must confirm that Nexus holds an active ICO registration (ZA987654)
covering its AI document processing activities, and that no ICO enforcement notices or
fines have been issued. A completed DPIA and external DPO review with no material issues
are also on record.

Score the agent's report:
- 1.0 (PASS): The report confirms active ICO registration, notes no enforcement actions,
  and references the DPIA or DPO review.
- 0.5 (PARTIAL): The report confirms ICO registration without the enforcement or
  compliance review detail.
- 0.0 (FAIL): The report does not address data protection or ICO registration.

Respond in JSON: {"score": <0.0|0.5|1.0>, "verdict": "<PASS|PARTIAL|FAIL>", "reasoning": "<one sentence>"}
""",
    ),

    Criterion(
        id="REG-02",
        category="Regulatory & Compliance",
        description="Confirms Nexus does not require SRA authorisation",
        required=False,
        relevant_documents=["nexus_regulatory_filing.txt"],
        judge_prompt="""
You are an adversarial legal reviewer evaluating an AI agent's due diligence report.
Your job is to find what the agent MISSED or got WRONG, not to confirm what it found.

GROUND TRUTH DOCUMENT:
{source_documents}

AGENT REPORT:
{report}

CRITERION: The agent must confirm that Nexus is not required to hold SRA (Solicitors
Regulation Authority) authorisation because it provides software tools to authorised firms
rather than legal services directly. This was confirmed by SRA correspondence in April 2023.

Score the agent's report:
- 1.0 (PASS): The report addresses SRA authorisation status, confirms it is not required,
  and correctly characterises Nexus as a software provider rather than a legal services provider.
- 0.5 (PARTIAL): The report mentions regulatory status or SRA without clear confirmation.
- 0.0 (FAIL): The report does not address SRA authorisation or incorrectly states
  authorisation is required.

Respond in JSON: {"score": <0.0|0.5|1.0>, "verdict": "<PASS|PARTIAL|FAIL>", "reasoning": "<one sentence>"}
""",
    ),
]

MAX_SCORE = sum(1.0 for _ in RUBRIC)
REQUIRED_CRITERIA = [c for c in RUBRIC if c.required]
