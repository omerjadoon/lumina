"""
Evaluation scenarios for the Legal Investigation Agent.

Each scenario defines:
  - A natural language goal given to the agent
  - The document corpus available (subset of data/documents/)
  - What failure modes are expected to be triggered
  - The minimum passing score on required criteria

Scenarios are ordered from easiest (full corpus, clean) to hardest (partial corpus, conflicts).
"""

from dataclasses import dataclass, field


@dataclass
class Scenario:
    id: str
    name: str
    goal: str
    available_documents: list[str]  # filenames relative to data/documents/
    expected_gaps: list[str]        # rubric criterion IDs the agent should flag as gaps
    expected_conflicts: list[str]   # rubric criterion IDs where agent should detect contradiction
    description: str
    minimum_required_pass: int      # how many required criteria must pass for scenario to pass


# ---------------------------------------------------------------------------
# Scenario 1: Full corpus — happy path
# Agent has all documents. Should surface all findings cleanly.
# Tests: can the agent complete a full investigation without prompting?
# ---------------------------------------------------------------------------

SCENARIO_HAPPY_PATH = Scenario(
    id="S1",
    name="Full Corpus — Happy Path",
    goal="Can Orion Capital safely acquire Nexus Legal Technologies?",
    available_documents=[
        "nexus_ip_assignment.txt",
        "nexus_university_licence.txt",
        "nexus_client_contract_lawfirm_alpha.txt",
        "nexus_incorporation_certificate.txt",
        "nexus_shareholder_register.txt",
        "nexus_litigation_register.txt",
        "nexus_regulatory_filing.txt",
    ],
    expected_gaps=["CONTRACT-02"],       # No second client contract exists even in full corpus
    expected_conflicts=["LIT-02"],       # Anonymous IP threat conflicts with IP assignment representation
    description=(
        "Full document corpus available. Agent should complete all five investigation categories, "
        "surface the DataVault dispute, flag the anonymous IP threat as conflicting with the "
        "founder's sole-inventor representation, and note the non-transferable Imperial licence. "
        "Expected: high score on all required criteria."
    ),
    minimum_required_pass=5,  # All 5 required criteria (IP-01, IP-02, CONTRACT-01, LIT-01, LIT-02)
)


# ---------------------------------------------------------------------------
# Scenario 2: Missing litigation register
# Agent cannot find LIT-2023-007 or the DataVault claim directly.
# Tests: does the agent notice the gap and flag it rather than silently skip?
# ---------------------------------------------------------------------------

SCENARIO_MISSING_LITIGATION = Scenario(
    id="S2",
    name="Missing Litigation Register",
    goal="Can Orion Capital safely acquire Nexus Legal Technologies?",
    available_documents=[
        "nexus_ip_assignment.txt",
        "nexus_university_licence.txt",
        "nexus_client_contract_lawfirm_alpha.txt",
        "nexus_incorporation_certificate.txt",
        "nexus_shareholder_register.txt",
        # nexus_litigation_register.txt intentionally absent
        "nexus_regulatory_filing.txt",
    ],
    expected_gaps=["LIT-01", "LIT-02"],
    expected_conflicts=[],
    description=(
        "Litigation register is absent from the corpus. Agent should attempt to find litigation "
        "information, fail to locate the document, explicitly flag that litigation status cannot "
        "be confirmed, and recommend it as a blocker before proceeding with acquisition. "
        "Expected: LIT-01 and LIT-02 flagged as unresolvable gaps, not silently omitted."
    ),
    minimum_required_pass=3,  # IP-01, IP-02, CONTRACT-01 should still pass; LIT criteria will gap
)


# ---------------------------------------------------------------------------
# Scenario 3: Missing IP assignment — core document gap
# The most critical document is absent. Agent must identify this as a blocker.
# Tests: does the agent escalate the right gaps as blockers?
# ---------------------------------------------------------------------------

SCENARIO_MISSING_IP_ASSIGNMENT = Scenario(
    id="S3",
    name="Missing IP Assignment — Core Blocker",
    goal="Can Orion Capital safely acquire Nexus Legal Technologies?",
    available_documents=[
        # nexus_ip_assignment.txt intentionally absent
        "nexus_university_licence.txt",
        "nexus_client_contract_lawfirm_alpha.txt",
        "nexus_incorporation_certificate.txt",
        "nexus_shareholder_register.txt",
        "nexus_litigation_register.txt",
        "nexus_regulatory_filing.txt",
    ],
    expected_gaps=["IP-01"],
    expected_conflicts=["LIT-02"],  # Anonymous threat still surfaceable without IP assignment
    description=(
        "IP assignment document is absent. Agent cannot confirm Nexus owns LexScan v1. "
        "Combined with the anonymous IP training data threat (still findable in the litigation "
        "register), the agent should conclude IP ownership is unverified and flag this as a "
        "acquisition blocker. Expected: IP-01 flagged as gap, LIT-02 escalated as high risk."
    ),
    minimum_required_pass=3,  # CONTRACT-01, LIT-01, LIT-02 should still be reachable
)


# ---------------------------------------------------------------------------
# Scenario 4: Conflicting IP documents only
# Only IP-related documents available. Tests depth of conflict detection.
# Tests: does the agent surface the Imperial licence vs IP assignment conflict?
# ---------------------------------------------------------------------------

SCENARIO_IP_CONFLICT_ONLY = Scenario(
    id="S4",
    name="IP Conflict Detection — Narrow Corpus",
    goal="Does Nexus Legal Technologies have clean IP ownership of its core product?",
    available_documents=[
        "nexus_ip_assignment.txt",
        "nexus_university_licence.txt",
    ],
    expected_gaps=["CONTRACT-01", "CONTRACT-02", "LIT-01", "LIT-02", "CORP-01", "CORP-02", "REG-01", "REG-02"],
    expected_conflicts=["IP-02"],  # Imperial licence non-transferable; derivatives jointly owned
    description=(
        "Narrow corpus: only IP documents available. Agent must work with limited evidence. "
        "The IP assignment states Vasquez was 'sole inventor' with no third-party claims, but "
        "the Imperial licence establishes that derivatives of ImperialNLP are jointly owned — "
        "and LexScan v1 was built during Vasquez's tenure under that licence. "
        "Agent should detect this conflict explicitly, flag all other categories as out of scope "
        "for this narrow goal, and recommend further document review before proceeding. "
        "Expected: IP-02 flagged as conflict; agent acknowledges corpus limitations."
    ),
    minimum_required_pass=1,  # Only IP-02 is realistically reachable here
)


ALL_SCENARIOS = [
    SCENARIO_HAPPY_PATH,
    SCENARIO_MISSING_LITIGATION,
    SCENARIO_MISSING_IP_ASSIGNMENT,
    SCENARIO_IP_CONFLICT_ONLY,
]
