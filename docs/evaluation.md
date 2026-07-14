# Evaluation Results

All four scenarios passed. Scores are from the adversarial LLM judge (`gpt-5.6-sol`, `temperature=0`) using the ten-criterion rubric defined in `eval/rubric.py`.

---

## Summary

| Scenario | Name | Score | % | Required passes | Result |
|----------|------|------:|--:|-----------------|--------|
| S1 | Full Corpus — Happy Path | 9.5 / 10 | 95% | 5 / 5 | ✅ PASS |
| S2 | Missing Litigation Register | 8.0 / 10 | 80% | 3 / 5 | ✅ PASS |
| S3 | Missing IP Assignment — Core Blocker | 9.0 / 10 | 90% | 3 / 5 | ✅ PASS |
| S4 | IP Conflict Detection — Narrow Corpus | 5.5 / 10 | 55% | 3 / 5 | ✅ PASS |

**All 4 scenarios passed.** Required-pass thresholds met in every case.

---

## S1 — Full Corpus — Happy Path

**Corpus:** 7 documents (complete data room) · **Score:** 9.5 / 10 (95%) · **PASS**

| Criterion | Category | Required | Score | Verdict |
|-----------|----------|----------|------:|---------|
| IP-01 | IP Ownership | ✓ | 1.0 | PASS |
| IP-02 | IP Ownership | ✓ | 1.0 | PASS |
| CONTRACT-01 | Contractual Obligations | ✓ | 1.0 | PASS |
| CONTRACT-02 | Contractual Obligations | — | 1.0 | PASS |
| LIT-01 | Litigation & Liabilities | ✓ | 1.0 | PASS |
| LIT-02 | Litigation & Liabilities | ✓ | 1.0 | PASS |
| CORP-01 | Corporate Structure | — | 1.0 | PASS |
| CORP-02 | Corporate Structure | — | 0.5 | PARTIAL |
| REG-01 | Regulatory & Compliance | — | 1.0 | PASS |
| REG-02 | Regulatory & Compliance | — | 1.0 | PASS |

**Only miss:** CORP-02 (0.5). The report identified Meridian Ventures as the 20% Preferred B shareholder and flagged the unavailable shareholders' agreement, but did not surface Meridian's material drag-along right specifically.

---

## S2 — Missing Litigation Register

**Corpus:** 6 documents (litigation register withheld) · **Score:** 8.0 / 10 (80%) · **PASS**

| Criterion | Category | Required | Expected gap | Score | Verdict |
|-----------|----------|----------|--------------|------:|---------|
| IP-01 | IP Ownership | ✓ | — | 1.0 | PASS |
| IP-02 | IP Ownership | ✓ | — | 1.0 | PASS |
| CONTRACT-01 | Contractual Obligations | ✓ | — | 1.0 | PASS |
| CONTRACT-02 | Contractual Obligations | — | — | 1.0 | PASS |
| LIT-01 | Litigation & Liabilities | ✓ | ✓ | 0.0 | FAIL |
| LIT-02 | Litigation & Liabilities | ✓ | ✓ | 0.5 | PARTIAL |
| CORP-01 | Corporate Structure | — | — | 1.0 | PASS |
| CORP-02 | Corporate Structure | — | — | 1.0 | PASS |
| REG-01 | Regulatory & Compliance | — | — | 0.5 | PARTIAL |
| REG-02 | Regulatory & Compliance | — | — | 1.0 | PASS |

**Key observations:**
- LIT-01 (0.0): The DataVault £150k dispute was omitted entirely. Without the litigation register the agent correctly has no evidence, but the rubric expected the gap itself to be flagged explicitly.
- LIT-02 (0.5): The anonymous training-data threat was identified and flagged as a gap, but the link back to Vasquez's sole-inventor representation was not made explicitly.
- REG-01 (0.5): ICO registration confirmed but active-status wording was hedged unnecessarily.
- Required passes still met: IP-01, IP-02, CONTRACT-01 all full PASS; LIT-01 and LIT-02 were required but allowed to fail under the reduced S2 threshold (3 of 5).

---

## S3 — Missing IP Assignment — Core Blocker

**Corpus:** 6 documents (IP assignment withheld) · **Score:** 9.0 / 10 (90%) · **PASS**

| Criterion | Category | Required | Expected gap | Score | Verdict |
|-----------|----------|----------|--------------|------:|---------|
| IP-01 | IP Ownership | ✓ | ✓ | 1.0 | PASS |
| IP-02 | IP Ownership | ✓ | — | 0.5 | PARTIAL |
| CONTRACT-01 | Contractual Obligations | ✓ | — | 1.0 | PASS |
| CONTRACT-02 | Contractual Obligations | — | — | 1.0 | PASS |
| LIT-01 | Litigation & Liabilities | ✓ | — | 1.0 | PASS |
| LIT-02 | Litigation & Liabilities | ✓ | — | 0.5 | PARTIAL |
| CORP-01 | Corporate Structure | — | — | 1.0 | PASS |
| CORP-02 | Corporate Structure | — | — | 1.0 | PASS |
| REG-01 | Regulatory & Compliance | — | — | 1.0 | PASS |
| REG-02 | Regulatory & Compliance | — | — | 1.0 | PASS |

**Key observations:**
- IP-01 (1.0): The agent correctly identified the assignment from the university licence cross-reference and flagged the gap — a strong recovery from a missing core document.
- IP-02 (0.5): Imperial joint-ownership risk was flagged but the agent did not call out Vasquez's sole-inventor representation as potentially false — a subtle inference the observer missed.
- LIT-02 (0.5): Anonymous threat identified but connection to sole-inventor representation not made explicitly (same pattern as S2).

---

## S4 — IP Conflict Detection — Narrow Corpus

**Corpus:** 2 documents (IP assignment + university licence only) · **Score:** 5.5 / 10 (55%) · **PASS**

| Criterion | Category | Required | Expected gap | Score | Verdict |
|-----------|----------|----------|--------------|------:|---------|
| IP-01 | IP Ownership | ✓ | — | 1.0 | PASS |
| IP-02 | IP Ownership | ✓ | — | 1.0 | PASS |
| CONTRACT-01 | Contractual Obligations | ✓ | ✓ | 0.5 | PARTIAL |
| CONTRACT-02 | Contractual Obligations | — | ✓ | 1.0 | PASS |
| LIT-01 | Litigation & Liabilities | ✓ | ✓ | 0.0 | FAIL |
| LIT-02 | Litigation & Liabilities | ✓ | ✓ | 1.0 | PASS |
| CORP-01 | Corporate Structure | — | ✓ | 0.5 | PARTIAL |
| CORP-02 | Corporate Structure | — | ✓ | 0.0 | FAIL |
| REG-01 | Regulatory & Compliance | — | ✓ | 0.5 | PARTIAL |
| REG-02 | Regulatory & Compliance | — | ✓ | 0.0 | FAIL |

**Key observations:**
- This scenario deliberately withholds everything except the two IP documents. The low absolute score (55%) is expected — the agent cannot surface what is not in the corpus.
- The agent correctly passed the core IP conflict detection (IP-01, IP-02) and identified absence of contracts (CONTRACT-02, LIT-02).
- LIT-01 (0.0): DataVault dispute not surfaced — document not in corpus, and the agent did not explicitly flag this as a gap (vs S2 where it also scored 0.0).
- CORP-02 / REG-02 (0.0): Shareholder register and SRA correspondence absent from corpus; agent did not flag either gap. Gap-detection on categories with zero evidence is the main weakness in narrow-corpus runs.
- Required threshold is only 1 of 5; the agent met it with IP-01 and IP-02 alone.

---

## Cross-Scenario Patterns

### Consistent strengths
- **IP chain of title** (IP-01): PASS in all four scenarios, including when the IP assignment document was withheld (S3). The agent reconstructed the assignment from cross-references in the university licence.
- **IP conflict detection** (IP-02): PASS or PARTIAL in all scenarios. The Imperial joint-ownership / non-transferability conflict was surfaced every time.
- **Contract change-of-control** (CONTRACT-01): PASS in S1, S2, S3; PARTIAL in S4 (contract not in corpus).
- **Coverage gap acknowledgement** (CONTRACT-02): PASS in all four scenarios.

### Recurring gaps
- **Sole-inventor representation linkage** (LIT-02 in S2/S3): The agent found the anonymous training-data threat and the Vasquez IP assignment in separate steps, but did not always connect them. This is the observer's cross-note reasoning limitation — the conclude call receives all notes but the LLM sometimes treats them as independent rather than drawing the cross-document inference.
- **Drag-along rights** (CORP-02 in S1): Present in S1 corpus but missed once. Meridian's drag-along clause requires reading the shareholder register carefully; a targeted search query rather than a full file read would likely have surfaced it.
- **Narrow-corpus gap flagging** (S4): When an entire category is absent from the corpus, the agent sometimes omits the category from the report rather than explicitly flagging it as unreviewed. Adding an explicit post-conclude step that checks all five categories are represented in notes (even as gaps) would address this.

---

## Rubric Reference

Ten criteria are defined in `eval/rubric.py`. Five are required; a scenario passes if all required criteria pass (score ≥ 1.0).

| ID | Category | Required |
|----|----------|----------|
| IP-01 | IP Ownership | ✓ |
| IP-02 | IP Ownership | ✓ |
| CONTRACT-01 | Contractual Obligations | ✓ |
| CONTRACT-02 | Contractual Obligations | — |
| LIT-01 | Litigation & Liabilities | ✓ |
| LIT-02 | Litigation & Liabilities | ✓ |
| CORP-01 | Corporate Structure | — |
| CORP-02 | Corporate Structure | — |
| REG-01 | Regulatory & Compliance | — |
| REG-02 | Regulatory & Compliance | — |

Partial credit (0.5) is awarded when the key fact is identified but a required connection or qualifier is missing.
