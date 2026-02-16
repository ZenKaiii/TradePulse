## Context

Current pipeline already has a push ledger but only uses it for stats. Digest composition still uses full `top_events`, so users receive repeated events. Overlay matching currently scans concatenated top titles with naive substring checks, leading to low relevance and false positives.

## Goals / Non-Goals

**Goals:**
- True incremental digest behavior.
- Better relevance in A section via freshness/source constraints.
- Accurate B section overlays with evidence lines.
- Telegram delivery works out-of-box when credentials are configured.
- C section gives novice-friendly sector rotation watchlist checklist.

**Non-Goals:**
- No automatic order execution.
- No deep valuation model or portfolio optimization.
- No external DB service migration.

## Decisions

1. **Incremental first**
   - Filter selected events by `ledger.should_push` before composing digest.
   - If no new event, render a dedicated no-new message.

2. **Freshness + source cap**
   - Add `digest.max_age_hours` (default 72).
   - Add `digest.max_per_source` (default 3).

3. **Structured overlays**
   - Stock matching: regex word boundaries with ticker syntax support.
   - Geopolitics matching: require >=2 token hits for multi-token topics.
   - Return matched event snippets for traceability.

4. **Auto channel detection**
   - Explicit channels (env/user config) have priority.
   - If empty, detect available channels from credentials.

5. **Section C watchlist ideas**
   - Build observation list from leading sectors and representative stocks.
   - Include entry checklist and risk reminder.

## Risks / Trade-offs

- Stricter matching may reduce hit count; this is acceptable for precision.
- Incremental behavior may produce no-new runs; user clarity is handled via explicit message.
- Additional digest text length is constrained with item limits.

## Migration Plan

1. Add config fields and defaults.
2. Add failing tests.
3. Implement incremental/event selection and overlays.
4. Implement auto channel detection.
5. Extend C section rendering.
6. Update docs and validate OpenSpec.
