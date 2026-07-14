# AI Engineering Take-Home

*(Example inspiration: long-running agent tools such as Cursor — plan → act → observe → adapt, with visibility into each step. You are free to design your own approach.)*

## The Challenge

Build a small AI agent that carries out long-running, multi-step tasks on a user's behalf.

The user describes a high-level goal, your agent breaks it into work, executes it using tools, and returns a result.

You pick the domain (research assistant, coding helper, ops assistant, document analyst, project planner, or anything else you can demonstrate well) and the interaction model (CLI, chat, or a minimal UI).

The interesting part is **not** the happy path. Long-running tasks rarely go exactly to plan, and a fixed sequence of prompts will not get you far. We're interested in how your agent decides what to do next, keeps track of where it is, and copes when things don't go smoothly. How you approach that is entirely up to you, and it's a large part of what we're looking at.

> **Important:** Please **do not** use agent frameworks (LangChain, LangGraph, AutoGen, CrewAI, etc.). We want to see **your own** agent loop, prompts, and context handling. Thin, non-agent libraries (such as an HTTP client, a vector store, or the provider SDK) are perfectly fine.

---

## Keep It Simple

We are **not** looking for a reusable agent framework or a platform.

We want the **simplest harness that does the job well**.

Developing a solution that's unnecessarily complex will count against you. A narrow, polished, well-understood agent is better than an ambitious but half-finished one.

---

## Evaluation

How do you know your agent is any good?

Build a **runnable evaluation harness**, use it to evaluate your own agent, and tell us what you learned and what you'd improve.

We care more about sound thinking than breadth.

---

## Deliverables

### 1. Source Code
- Public Git repository
- Clear project structure
- Run instructions

### 2. README
In your own words:
- How your agent works
- Key design decisions and why you made them
- What you would do with more time

### 3. Evaluation Harness
- A runnable evaluation harness
- Results from running it against your agent

### 4. Example Run
A real task executed from start to finish.

### 5. Short Video (3–5 minutes)
Explain:
- How your agent works
- How information and tools flow through the system
- How you would extend it

### 6. Build Session Logs
Assuming you used AI tools to help build your solution (e.g., Claude Code, Codex, Copilot, etc.), export **all raw session logs** into a `build_sessions/` directory.

Do **not** edit these logs—we want to see how you work.

---

## Time

Aim for roughly **4–6 hours**, although it's ultimately up to you.

Spend your time where you think it best demonstrates your judgment, and explain in the README:
- How you allocated your time
- What trade-offs you made

---

# How We Evaluate

| Area | Weight |
|------|-------:|
| Harness engineering (agent loop, decision making, adaptation, context/state handling, robustness, observability/tracing) | **40%** |
| Evaluation (quality of the evaluation harness and insights from the results) | **30%** |
| Prompt and context engineering | **15%** |
| Code quality, simplicity, and engineering judgment | **15%** |