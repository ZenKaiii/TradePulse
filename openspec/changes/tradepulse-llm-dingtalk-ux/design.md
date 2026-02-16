## Context

TradePulse currently computes direction and impact text purely by rule heuristics. Even with valid API keys configured in GitHub Actions, no LLM call happens in the pipeline. DingTalk output uses `msgtype=text`, so markdown headers and lists are not rendered.

## Goals / Non-Goals

**Goals:**
- Ensure DingTalk renders structured digest correctly.
- Ensure Top10 event commentary is truly model-generated in Chinese.
- Keep runtime robust with Bailian -> Gemini fallback.
- Make model/provider selectable via config variables.
- Improve readability for non-expert users.

**Non-Goals:**
- No full article crawling/parsing in this iteration.
- No speculative trading recommendation engine.
- No per-source deep due-diligence scoring redesign.

## Decisions

1. **DingTalk markdown payload**
   - Use `msgtype=markdown` and `markdown.title/text` for bot messages.
   - Keep text length bounded by concise section formatting.

2. **Structured JSON LLM output**
   - Prompt model to return strict JSON fields for deterministic parsing.
   - If parse fails, fallback to rule-based fields to avoid job failure.

3. **Provider abstraction + config**
   - Add `LLMConfig` with provider/model/base_url/timeout/detail split.
   - Prefer Bailian using OpenAI-compatible endpoint; fallback to Gemini REST.

4. **Detail strategy**
   - Top5 events: detailed summary + rationale + beginner note.
   - Remaining events: short summary + short rationale.

## Risks / Trade-offs

- **[Model JSON non-compliance]** -> regex-json extraction + fallback.
- **[Provider latency]** -> timeout and per-event graceful degradation.
- **[Cost increase]** -> brief mode for lower-ranked events and tunable detail count.
- **[DingTalk markdown subset limits]** -> conservative markdown syntax and short lines.

## Migration Plan

1. Add config + env vars for LLM behavior.
2. Implement LLM client and enrichment function.
3. Integrate into pipeline and composer.
4. Switch DingTalk payload format.
5. Update workflow and README docs.
6. Rollback: set `TRADEPULSE_LLM_ENABLED=false` and keep rule-only mode.

## Open Questions

- None for this scope; user confirmed strategy and direction.
