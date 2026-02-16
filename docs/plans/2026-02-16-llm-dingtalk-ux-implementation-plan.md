# LLM + DingTalk UX Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix DingTalk markdown rendering and enable configurable LLM event analysis with beginner-friendly digest output.

**Architecture:** Add LLM config + analyzer module, enrich top events in pipeline, switch DingTalk payload to markdown, and update docs/workflow variables.

**Tech Stack:** Python 3.8+, httpx, pytest, OpenSpec

---

### Task 1: Add failing tests
- Update notifier/config/compose tests.
- Add analyzer tests for provider selection and detail split.

### Task 2: Add LLM config surface
- Extend `UserConfig` with `LLMConfig`.
- Add env override support for `TRADEPULSE_LLM_*` and model/base URL variables.

### Task 3: Implement LLM analyzer
- Add provider selection logic.
- Add Bailian and Gemini API calls.
- Add JSON parsing and fallback behavior.

### Task 4: Integrate pipeline
- Enrich top events before composing digest.
- Carry provider/model metadata to output stats.

### Task 5: Improve digest UX and DingTalk payload
- Add novice-friendly sections and emoji markers.
- Add section explanations and representative stocks.
- Send DingTalk as markdown payload.

### Task 6: Docs + workflow
- Add new variables to workflow.
- Update README (EN/CN) and setup docs.

### Task 7: Verify and close
- Run full pytest.
- Validate OpenSpec change.
- Mark tasks complete.
