# How We Tested the AI Agent (Evaluation Results)

To make sure our AI agent does a good job, we put it through four different test cases (called "scenarios"). Each test represents a real-world situation a legal reviewer might face when checking a company before buying it. 

To score the AI's reports fairly, we used another AI (a "grader" or "judge") to read the final reports and grade them from 0 to 10 based on 10 specific checklist items. 

---

## Quick Summary of Results

Here is a summary of how the AI performed in each test. All four tests passed our target requirements!

| Test Case | Description | Score | Grade % | Did it Pass? |
|:---|:---|:---:|:---:|:---:|
| **Test 1: All Documents Available** | We gave the AI all 7 documents. This is the ideal situation. | 9.5 / 10 | 95% | ✅ PASS |
| **Test 2: Missing Court records** | We hid the list of court cases/disputes to see if the AI noticed the gap. | 8.0 / 10 | 80% | ✅ PASS |
| **Test 3: Missing Ownership Contract** | We hid the main document showing who owns the software/technology. | 9.0 / 10 | 90% | ✅ PASS |
| **Test 4: Bare Minimum Info** | We hid almost everything and only gave the AI 2 documents. | 5.5 / 10 | 55% | ✅ PASS |

**What these results mean:** Even when we hid important papers, the AI did not get confused or make things up. Instead, it realized documents were missing, flagged the gaps, and still found correct clues in the remaining paperwork.

---

## Detailed Test Breakdown

### Test 1: All Documents Available (The "Happy Path")
* **What we tested:** We gave the AI the complete folder of 7 documents to see how well it could write a full legal review.
* **Score:** 9.5 / 10 (95%)
* **Verdict:** ✅ PASS
* **What went well:** The AI found almost everything. It correctly identified who owns the technology, flagged contract deadlines, found regulatory details, and noted active court cases.
* **The only small miss:** The AI missed one minor detail—a specific investor's right to force other shareholders to sell their shares (called a "drag-along right"). 

---

### Test 2: Missing Court Records
* **What we tested:** We hid the "litigation register" (the list of court cases and disputes). We wanted to see if the AI would make up court cases or correctly report that it didn't have enough information.
* **Score:** 8.0 / 10 (80%)
* **Verdict:** ✅ PASS
* **What went well:** The AI did not make up any fake lawsuits. It correctly flagged that it could not confirm the company's full court history because the register was missing.
* **Room for improvement:** Although the AI noticed the court history was missing, it should have explicitly warned us that a specific £150k dispute might exist, rather than just stating the file was missing.

---

### Test 3: Missing Ownership Contract (A Core Blocker)
* **What we tested:** We hid the "IP Assignment" document—the official contract that transfers technology ownership from the inventor to the company. This is a major blocker for any acquisition.
* **Score:** 9.0 / 10 (90%)
* **Verdict:** ✅ PASS
* **What went well:** The AI did an excellent job. Even though the main contract was missing, it read a *different* university license document, noticed a reference to the missing contract, and used that clue to prove the transfer happened. It also flagged the missing document as a high-risk gap.

---

### Test 4: Bare Minimum Info
* **What we tested:** We gave the AI only 2 documents (the technology assignment and the university license) and withheld everything else. This test was designed to see if the AI would fail gracefully when it had almost no information.
* **Score:** 5.5 / 10 (55%)
* **Verdict:** ✅ PASS
* **What went well:** The AI scored lower here, but that was expected since we hid 5 out of 7 files. It successfully answered the questions about technology ownership using the two files it had, and it didn't fabricate any information about the missing files.

---

## What We Learned (Patterns & Behaviors)

### Where the AI is Very Strong:
1. **Connecting the Dots:** The AI is great at finding clues. For example, when we hid the main ownership contract, it read other documents to piece together who owned the technology.
2. **Finding Ownership Risks:** It consistently warns us about joint-ownership risks (e.g., if a university has rights to the company's code).
3. **Knowing What is Missing:** It is good at listing which categories of information it couldn't review because files were absent.

### Where the AI Can Improve:
1. **Linking Clues Together:** Sometimes, the AI finds two separate clues (like an anonymous threat about code ownership and a separate contract signed by the founder) but fails to connect them and realize they are about the same issue.
2. **Digging Deeper into Shareholders' Rights:** It occasionally misses fine-print details about investor agreements (such as drag-along rights) because it doesn't search specifically for those legal terms.

---

## The Checklist We Used to Grade the AI
We graded the AI on ten criteria across five main business categories. Five of these are **required** (essential for a passing grade):

1. **Technology Ownership (Required):** Did the AI verify who owns the software/IP?
2. **Ownership Risks (Required):** Did it find conflicts or university claims on the technology?
3. **Contract Restrictions (Required):** Did it look for clauses that require client permission before selling the company?
4. **Contract Gaps:** Did it report when contracts were missing?
5. **Court Cases & Lawsuits (Required):** Did it identify active or threatened legal disputes?
6. **Key Legal Threats (Required):** Did it catch serious claims (like an ex-employee claiming they own the code)?
7. **Company Structure:** Did it verify how the company is set up and owned?
8. **Shareholder Rules:** Did it check for special shareholder agreements?
9. **Regulatory Approvals:** Did it check if the company is properly registered with regulators?
10. **Compliance History:** Did it look for regulatory fines or warnings?
