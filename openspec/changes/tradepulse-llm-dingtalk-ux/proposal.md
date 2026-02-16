## Why

Current digest delivery has two user-facing issues: DingTalk displays raw markdown text as plain text, and event analysis is still rule-template based instead of actual LLM reasoning. This makes the output less readable and less trustworthy for trading decisions.

## What Changes

- Switch DingTalk notifier from plain text payload to markdown payload with mobile-friendly formatting.
- Add real LLM analysis pipeline with Bailian primary and Gemini fallback.
- Support model/provider/base URL configuration via GitHub Actions variables.
- Implement mixed detail strategy: Top5 detailed analysis + Top5 brief analysis.
- Add beginner-friendly Chinese explanations for Section A/B/C and add light emoji markers for readability.

## Capabilities

### New Capabilities
- `llm-event-analysis`: Use LLM to generate Chinese summary, direction rationale, and affected ticker hints per event.
- `dingtalk-markdown-delivery`: Deliver digest in DingTalk markdown message type with readable structure.

### Modified Capabilities
- `market-regime-section`: Expand Section C text to explain metrics and representative stocks for novice users.

## Impact

- `src/tradepulse/notifiers/dingtalk.py`: markdown payload support.
- `src/tradepulse/llm/*`: provider clients, fallback routing, and structured analysis parser.
- `src/tradepulse/pipeline/run_once.py`: LLM enrichment in event pipeline.
- `src/tradepulse/compose.py`: detailed/brief rendering and novice-friendly explanations.
- `src/tradepulse/config.py` + workflow/docs: new `TRADEPULSE_LLM_*` variables and docs.
- `tests/*`: new tests for LLM config, analysis pipeline, and DingTalk payload.
