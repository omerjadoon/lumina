# Step-by-Step Build Plan (Tasks)

This document shows the checklist used to build the Legal Investigation AI Agent from start to finish.

## Status Legend
* `[ ]` Not started
* `[x]` Complete

---

## 📝 Step 1: Create the Notebook (Memory Structure)
* **Goal:** Create the basic structure that the AI uses to take notes and track its progress.
* **Status:** `[x]` Complete
* **Tasks:**
  * [x] Create the initial folder structures.
  * [x] Create `agent/state.py` to hold the list of notes, files read, and questions.

---

## 🛠 Step 2: Build the Hands (File Tools)
* **Goal:** Write the functions that allow the AI to look at the folders, read files, and search for keywords on the local computer.
* **Status:** `[x]` Complete
* **Tasks:**
  * [x] Create `agent/tools.py`.
  * [x] Write `list_files` to let the AI see all document names.
  * [x] Write `read_file` to let the AI read a file (up to a safe size limit).
  * [x] Write `search_in_file` to let the AI look for specific keywords in a document.

---

## 🧠 Step 3: Build the Brain (AI Instructions)
* **Goal:** Write the prompts and logic that talk to OpenAI to plan, choose tools, take notes, and write reports.
* **Status:** `[x]` Complete
* **Tasks:**
  * [x] Create `agent/planner.py`.
  * [x] Implement the planning function (creates a checklist of 5–8 questions).
  * [x] Implement tool selection (decides whether to read or search).
  * [x] Implement observation logic (reads search results and decides if they show a fact, a missing file, or a contradiction).
  * [x] Implement re-planning (rewrites questions if the AI gets stuck).
  * [x] Implement report writing (writes the final prose summary).

---

## 🔄 Step 4: Build the Coordinator (The Main Loop)
* **Goal:** Tie everything together so the AI can automatically plan, execute tools, observe, and repeat until done.
* **Status:** `[x]` Complete
* **Tasks:**
  * [x] Create `agent/runner.py`.
  * [x] Implement the logging system so progress prints nicely to the screen and saves to files in `logs/`.
  * [x] Implement the main loop that coordinates steps 1 to 3.
  * [x] Set a safety guard (maximum of 20 steps) so the AI never gets stuck looping forever.

---

## 🧪 Step 5: Run a Manual Test
* **Goal:** Run the AI once by hand to make sure it runs smoothly without crashing.
* **Status:** `[x]` Complete
* **Tasks:**
  * [x] Run the agent on the sample documents folder.
  * [x] Verify that the logs print correctly and the final report contains details about technology ownership, contracts, and court cases.
  * [x] Hide one file and verify that the AI notices and flags the gap.

---

## 📊 Step 6: Run the Full Test Suite
* **Goal:** Run the evaluation script against all 4 test cases to grade the AI.
* **Status:** `[x]` Complete
* **Tasks:**
  * [x] Run the grading script for Test 1 (Happy Path).
  * [x] Run all tests together and save the scores to `results/eval_results.json`.
  * [x] Check the grading details and tweak the AI's instructions to improve the scores.

---

## 📖 Step 7: Document Everything
* **Goal:** Write the main guides so anyone can install and run the project.
* **Status:** `[x]` Complete
* **Tasks:**
  * [x] Write the `README.md` with simple setup instructions.
  * [x] Document the system design in `docs/architecture.md`.
