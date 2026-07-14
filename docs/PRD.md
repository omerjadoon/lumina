# Product Requirements: What the AI Agent Needs to Do

This document explains the requirements and goals for the Legal Investigation AI Agent. It outlines what the tool does, what is out of bounds, and how we measure success.

---

## 🔍 The Problem We Are Solving

When lawyers or business professionals want to buy a company, they have to read hundreds of pages of documents (contracts, corporate filings, court records, etc.) to make sure there are no hidden risks. This manual review is:
* **Slow:** Reading takes days or weeks.
* **Error-prone:** It is easy to miss a small sentence in a long document.
* **Rigid:** Existing tools can't adapt when a file is missing or contains conflicting statements. They don't know what to look for next.

---

## 🎯 Our Goal

Build a simple AI assistant that can:
1. Accept a high-level goal (like *"Is it safe to buy this company?"*).
2. Create its own investigation plan.
3. Search and read local document files.
4. Adapt when information is missing or contradictory (e.g., re-planning its next steps).
5. Generate a clear final report summarizing the findings, gaps, and conflicts.

---

## 👥 Who This Is For

1. **AI Engineers:** Who want to evaluate if the agent is built cleanly, handles errors robustly, and makes smart decisions under the hood.
2. **Business Professionals:** Who need quick answers about buying a company from a folder of documents without having to read every single page themselves.

---

## 🔎 What the AI Can & Cannot Do

### Inside the Scope (What it Can Do):
* Runs as a simple command-line tool.
* Investigates one goal at a time (e.g., checking if an acquisition is safe).
* Reads local text and markdown files in a folder.
* Generates its own step-by-step checklist.
* Automatically updates its checklist when it finds missing or conflicting information.
* Writes a final summary report.
* Runs against a testing suite to score its performance.

### Outside the Scope (What it Cannot Do):
* Search the internet or make external API calls (other than talking to the OpenAI language model).
* Remember information between different runs (each run starts fresh).
* Require a web browser or graphical user interface (it runs purely in the terminal).
* Read PDFs, Word documents, or image files (only plain text/markdown files are supported).
* Provide actual, official legal advice (this is a demo tool, not a lawyer!).

---

## 🛠 Features the AI Must Have (Functional Requirements)

1. **Goal Input:** The user can type their goal in plain English when starting the tool.
2. **Plan Generation:** The AI creates a checklist of questions covering all key business areas (ownership, contracts, lawsuits, corporate structure, and compliance).
3. **Tool Execution:** The AI uses tools to read folders, open documents, and search for keywords.
4. **Smart Adapting (Re-planning):** If a document is missing or information doesn't match up, the AI explicitly decides to change its plan, search for alternative documents, or flag the gap.
5. **State Tracking:** The AI keeps a neat list of notes so it always knows what has been answered, what is still open, and what is missing.
6. **Final Report:** The AI writes a clear, organized report summarizing its findings.
7. **Testing System:** A separate script runs the AI through different scenarios to grade its accuracy.

---

## 📏 Rules the Code Must Follow (Non-Functional Requirements)

1. **Easy to Follow:** Every decision the AI makes must be printed clearly on the screen so a human can follow its thoughts without reading the code.
2. **Simple and Clean:** The code must be easy to read and understand in one sitting (under 500 lines of core Python code).
3. **Robust:** The AI must not crash if a file is missing or a tool fails. It must log the error and keep going.
4. **Reproducible:** Anyone should be able to download the code, run one setup command, and get it working exactly the same way.

---

## ⚠️ What Could Go Wrong & How We Prevent It

| Risk | What Happens | How We Prevent It |
|:---|:---|:---|
| **Infinite Loop** | The AI gets stuck in a loop searching forever. | We set a strict maximum limit of 20 steps. If the AI isn't done by then, it is forced to write the report with what it has. |
| **Too Much Text** | The files are too long, causing the AI to lose track. | The AI only keeps a list of short *notes* instead of saving the full text of every document it reads. |
| **Vague Plans** | The AI creates useless or random checklists. | We force the AI to return its checklist in a structured format, not free-text prose. |
| **No Real Challenges** | The test files are too easy or clean. | We deliberately planted missing files and conflicting claims in the test folders to challenge the AI. |
