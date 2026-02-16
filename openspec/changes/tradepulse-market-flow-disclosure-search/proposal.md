## Why

Users need richer Section 4 insights and configurable research augmentation:
- default model choices should align with requested provider defaults;
- Telegram should render formatted output instead of plain text wall;
- US market flow should include daily capital-flow proxy for sectors and stocks;
- users want institution/insider tracking via 13F + Form4;
- Tavily should be optional enhancement, not hard dependency.

## What Changes

- Update LLM default models (`qwen3.5-plus`, `gemini-3-pro-preview`).
- Add Telegram markdown-mode rendering with fallback behavior.
- Extend Section 4 with US sector/stock flow proxy metrics.
- Add SEC disclosure tracking (institution 13F + insider Form4).
- Add optional Tavily search enhancement for top events.
- Add Google News RSS feeds as extended source tier supplements.

## Impact

- config/runtime/env model updated for search and market options
- market snapshot and digest composer gain new sections
- notifier behavior changes for Telegram formatting
- workflow/docs add new secrets/variables
