# System Architecture: How the Legal AI is Built

This document explains how our Legal Investigation AI Agent is designed under the hood. We built this system to be as simple and transparent as possible—using only **four main files** and **one central loop**, without any complex external agent frameworks.

---

## 📂 The File Structure & Roles

We divided the project into four main code files. Each file has one specific job:

| File | Role | Plain English Description |
|:---|:---|:---|
| **`agent/runner.py`** | The Boss / Coordinator | Runs the main loop, coordinates the tools and AI, prints progress to the screen, and writes log files. |
| **`agent/planner.py`** | The Brain / Decision Maker | Handles all the logic that talks to OpenAI. It designs the plan, decides which tool to use, analyzes search results, and writes the final report. |
| **`agent/tools.py`** | The Hands / Workers | Performs the actual filesystem work: listing files in folders, reading files, and searching for keywords. |
| **`agent/state.py`** | The Notepad / Memory | A simple structure that holds the current state of the investigation (what questions remain, what notes have been taken). |

---

## 📝 How the Agent Remembers Things (The State Model)

Instead of sending the entire history of everything the AI did back and forth (which wastes computer power and money), we use a structured notepad called `InvestigationState`. 

It stores two main things:
1. **The Plan:** An ordered list of questions the AI needs to answer.
2. **Notes:** A list of key facts found during the search. Each note is saved as a simple format containing:
   * **Kind:** Is it a `finding` (a fact), a `gap` (something missing), or a `conflict` (two documents saying different things)?
   * **Category:** Which legal topic does this belong to (e.g., Intellectual Property, Contracts, Court Cases)?
   * **Description:** A short, plain-English summary of what was found.
   * **Sources:** Which documents this information came from.

This simple memory structure means that whether the AI runs 5 steps or 20 steps, it only has to read a small list of clean notes, keeping it fast and accurate.

---

## 🔄 The Step-by-Step Investigation Loop

Here is exactly what happens when you start an investigation:

1. **Step 1: Discover Files** — The coordinator (`runner.py`) lists all files in the folder.
2. **Step 2: Make a Plan** — The brain (`planner.py`) looks at the list of files and the user's goal, then writes a list of 5 to 8 questions covering all key legal areas.
3. **Step 3: The Search Loop** (Repeats until finished):
   * **Pick a Question:** Look at the next unanswered question on the list.
   * **Select a Tool:** The brain decides whether to read a whole file or search for specific keywords.
   * **Run the Tool:** The coordinator executes the search and gets the raw text.
   * **Observe & Take Notes:** The brain reads the raw text, extracts any useful facts (saving them as notes), and decides whether to *continue*, *re-plan* (if a document was missing), or *conclude*.
4. **Step 4: Write the Report** — The brain reads all the accumulated notes and summarizes them into a clean final report.

---

## 🛠 The Tools the AI Can Use

The AI can only interact with files using three simple functions:
1. `list_files` — Lists the names of all files in the document folder.
2. `read_file` — Reads the text inside a specific document (truncated to a maximum size so the AI isn't overwhelmed by long documents).
3. `search_in_file` — Scans a document and returns only the lines that match a specific keyword query.

Using simple keyword searches instead of fancy search algorithms makes it very clear to the AI when a document is missing or empty, allowing it to quickly flag problems.

---

## 🔄 Handling Gaps and Re-planning

If the AI tries to read a document and finds nothing, or if it finds two documents that contradict each other:
1. It records a **Gap** or **Conflict** note.
2. It triggers a **Re-plan** step.
3. The AI rewrites its remaining questions to address the problem. For example, if the court register file is missing, it will add a new task: *"Search all other files to see if any other document mentions active lawsuits."*

This allows the AI to adapt dynamically when things don't go according to plan.

---

## 📝 Logging (Stdout & JSONL Files)

The coordinator writes logs to two places at the same time:
* **Your Screen (Stdout):** Beautiful, color-coded text showing what the AI is doing in real-time (e.g., `[PLAN]`, `[TOOL]`, `[OBSERVE]`, `[REPLAN]`).
* **Log Files (JSONL):** Detailed, machine-readable files saved in the `logs/` folder. These files can be loaded by testing scripts to see exactly what happened step-by-step.
