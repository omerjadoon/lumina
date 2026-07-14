# AI Engineering Take-Home Challenge

This document outlines the challenge requirements for building the Legal Investigation AI Agent.

---

## 🎯 The Challenge: What to Build

Build a small AI assistant that can execute long, multi-step tasks on a user's behalf. 

The user describes a high-level goal, and your assistant:
1. Breaks it down into smaller steps.
2. Executes those steps using tools.
3. Adapts when things go wrong (e.g., if a file is missing or information conflicts).
4. Returns a final report.

> **CRITICAL RULE:** Do **not** use agent frameworks like LangChain, LangGraph, AutoGen, or CrewAI. We want to see your own custom loops, prompts, and memory handling. You can use standard libraries (like the OpenAI SDK or a simple search library).

---

## 💡 Keep It Simple

We are **not** looking for a complex, general-purpose platform. 

We want the **simplest code that does the job well**. 
Building something unnecessarily complex will count against you. A narrow, highly polished, and well-understood assistant is much better than an ambitious but half-finished one.

---

## 📊 How It Is Graded

To verify how good your assistant is, you must build a **runnable testing script (evaluation harness)**. Use this script to grade your own assistant, and document what you learned and what you would improve.

We score the project based on four areas:

| Area | Weight | What We Look For |
|:---|:---:|:---|
| **System Design & Loop** | **40%** | How the assistant makes decisions, adapts to missing information, and tracks its state. |
| **Testing & Evaluation** | **30%** | The quality of your test script and the honesty of your insights. |
| **Prompts & Instructions** | **15%** | How clear and effective your instructions to the AI are. |
| **Code Quality & Simplicity** | **15%** | How readable, clean, and simple your code is. |

---

## 📦 What You Need to Hand In (Deliverables)

1. **Source Code:** A clean, organized, public Git repository with clear instructions on how to run it.
2. **README:** A document explaining in plain English:
   * How your assistant works.
   * Why you made key design decisions.
   * What you would do if you had more time.
3. **Testing Script:** A runnable script that tests the assistant, along with a file containing the test results.
4. **Example Run:** A saved log showing a full run from start to finish.
5. **Short Video (3–5 minutes):** A quick walkthrough explaining:
   * How the assistant works.
   * How information flows through the system.
   * How you would expand it in the future.
6. **Build Logs:** Exported chat logs showing how you used AI coding assistants (like Claude, Copilot, etc.) to help build the project. Do not edit these logs.

---

## ⏱ Time Allocation

Aim to spend roughly **4 to 6 hours** on this challenge. 

Use your time wisely to demonstrate good engineering judgment. In your README, explain:
* How you spent your time.
* What shortcuts or trade-offs you had to make.