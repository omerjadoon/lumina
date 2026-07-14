# List of Planned Improvements

This document lists the improvements planned (and completed) for the Legal Investigation AI Agent. These tasks are organized by how much they improve the agent's accuracy, speed, and code quality.

## Status Legend
* `[ ]` Not started
* `[~]` In progress
* `[x]` Complete

---

## 🛠 High-Priority Improvements (Essential Fixes)

### 1. Fixing the Test Documents (Making sure the tests are fair)
* **Status:** `[x]` Complete
* **The issue:** The folder of documents contained an index file (`CORPUS_INDEX.txt`) that explicitly listed all the missing files and gaps. If the AI read this file, it would automatically know what was missing without having to discover it.
* **The fix:** Moved the index file out of the folder where the AI searches so the AI has to find the gaps itself, making the test results honest and accurate.

### 2. Organizing the AI Prompts (Single source of truth)
* **Status:** `[x]` Complete
* **The issue:** Prompts (the instructions sent to the AI) were scattered inside the code and in a separate folder, making it confusing to know which prompt was actually being used.
* **The fix:** Updated the code to import all prompts from a single, dedicated `prompts/` folder. This makes it easy to update prompts in one place.

### 3. Giving Clearer Roles to the AI (Improving instructions)
* **Status:** `[x]` Complete
* **The issue:** The AI was given simple user messages without a "system role" (like telling it: *"You are a professional legal investigator"*).
* **The fix:** Added explicit system roles to all 5 AI functions (planning, tool selection, observation, re-planning, and report writing) to improve how well the AI follows instructions.

### 4. Letting the AI Read More Text (Preventing missed details)
* **Status:** `[x]` Complete
* **The issue:** The AI was only allowed to look at the first 2,000 characters of a document when analyzing search results. If an important detail or conflict was in the middle of a long document, the AI would miss it.
* **The fix:** Increased the limit to 6,000 characters so the AI can read more of the document at once without missing key facts.

---

## 📈 Medium-Priority Improvements (Robustness & Reliability)

### 5. Fixing Log File Errors (Ensuring logs save properly)
* **Status:** `[x]` Complete
* **The issue:** If the AI crashed or ran into an error at the very end of its run, the log file would remain open and lock up, causing future runs to fail to save logs.
* **The fix:** Wrapped the logging code in a safety block (a `try/finally` block) that ensures log files are always closed properly, even if an error occurs.

### 6. Locking Package Versions (Ensuring the app runs on any computer)
* **Status:** `[x]` Complete
* **The issue:** The project didn't specify exactly which version of the OpenAI library it needed. If a user installed a newer, incompatible version, the project would crash.
* **The fix:** Created a `requirements.txt` file that locks in the safe version range, making sure the project works for everyone.

### 7. Letting the AI Try Searching Again (Avoiding giving up too early)
* **Status:** `[x]` Complete
* **The issue:** If the AI searched for a keyword and found nothing on its first try, it would immediately declare a "gap" and give up, even if the information was in the document under a different name.
* **The fix:** Added retry logic. The AI is now allowed to try up to 2 different keywords (like "IP assignment" then "software license") before it is allowed to declare that the information is missing.

### 8. Improving Contradiction Detection
* **Status:** `[x]` Complete
* **The issue:** The AI was sometimes reading two contradictory statements (e.g., one saying the founder owns the code, another saying a university owns it) but recording them as normal findings instead of flagging a conflict.
* **The fix:** Added explicit instructions to the AI to look for contradictions and show it a list of recent findings so it can easily notice if a new document contradicts an old one.

---

## 🧼 Low-Priority Improvements (Cleanup & Polish)

### 9. Cleaning Up Unused Code Statuses
* **Status:** `[x]` Complete
* **The fix:** Removed unused status variables in the code to keep the code clean and easy to read.

### 10. Making AI Grading More Reliable
* **Status:** `[ ]` Not started
* **The goal:** When scoring the AI, a single grader AI run can sometimes give slightly different scores. We want to run the grader 3 times and take the average (median) score to make sure the grades are completely fair and consistent.

### 11. Running the Entire System to Double-Check
* **Status:** `[ ]` Not started
* **The goal:** Run all tests end-to-end and update the README with the final honest scores once we confirm everything is working.
