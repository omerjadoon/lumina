# Example Run: What the AI Agent Looks Like in Action

This document shows an example of what happens step-by-step when a user runs the AI agent to investigate a company. 

In this example, the user wants to answer this goal:
> **Goal:** "Can Orion Capital safely acquire Nexus Legal Technologies?"

Here is how the AI agent works through the task, step-by-step.

---

## Step 1: Making the Checklist (The Plan)

At the very beginning, the agent looks at the files in the folder and writes a plan. It decides to check five main legal areas:

```
[PLAN] Step 1: Check who officially owns the technology (IP ownership).
[PLAN] Step 2: Look for contracts that require client permission to buy the company.
[PLAN] Step 3: Search for active lawsuits or legal claims against the company.
[PLAN] Step 4: Verify how many shares exist and who owns them.
[PLAN] Step 5: Check if the company has all its government permits and registrations.
```

---

## Step 2: Searching the Documents (The Loop)

The agent now starts going through its checklist. It chooses the best search tool for each step.

### Check 1: Technology Ownership
* **Action:** The agent decides to search for the word "Nexus" inside the file `nexus_ip_assignment.txt`.
* **Tool Used:** `search_in_file`
* **Result:** It finds text showing that the founder, Dr. Vasquez, transferred all ownership rights to the company (Nexus).
* **AI Note:** *Finding (IP Ownership) — Technology fully transferred to Nexus.*

### Check 2: Contracts & Restrictions
* **Action:** The agent decides to read `nexus_client_contract.txt`.
* **Tool Used:** `read_file`
* **Result:** It reads the contract and finds a clause stating that if Nexus is sold to another company, they must get written consent from their top client, Alpha Partners.
* **AI Note:** *Finding (Contracts) — Consent required from Alpha Partners before purchase.*

### Check 3: Lawsuits & Disputes
* **Action:** The agent attempts to open `nexus_litigation_register.txt` to check for lawsuits.
* **Result:** **File is missing!** The tool returns nothing.
* **AI Adaptability (Re-plan):** Instead of giving up, the agent notices the missing file, flags a gap, and updates its plan to search all other documents for any mention of disputes.
* **AI Note:** *Gap (Lawsuits) — Court register file is missing. Searching other files for mentions.*
* **New Action:** Scans all other documents for keywords like "lawsuit", "court", or "dispute".
* **Result:** Finds a letter mentioning an ongoing £150,000 billing dispute with a vendor called DataVault.
* **AI Note:** *Finding (Lawsuits) — Found a hidden £150k dispute with DataVault.*

---

## Step 3: Writing the Final Report

Once all checklist items are addressed, the agent compiles its notes into a simple, easy-to-read report for the buyer:

### 📄 Final Investigation Report Summary

* **Technology Ownership:** Dr. Vasquez successfully transferred all software rights to Nexus. However, there is a risk: Imperial College London may have joint rights to a portion of the software.
* **Contracts:** You must get written permission from Alpha Partners before buying Nexus, or their contract might be terminated.
* **Lawsuits (Risk Flagged):** The official court register file was missing, but we uncovered a hidden £150,000 dispute with a supplier named DataVault.
* **Verdict:** Acquisition is possible, but you must resolve the DataVault dispute and obtain consent from Alpha Partners before signing.



you can see the real example run logs at `logs/` folder.