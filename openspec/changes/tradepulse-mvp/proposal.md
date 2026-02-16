# Proposal: TradePulse MVP

## Summary

Implement TradePulse MVP as an importance-first, hourly digest for US stock traders, with Chinese output, source attribution, and multi-channel push.

## Motivation

- Reduce signal-to-noise ratio for trading workflows.
- Provide actionable event direction (`利好/利空/中性`) with ticker mapping.
- Keep onboarding simple through single-file config and secret-driven provider/channel activation.

## Scope

- Canonical ingestion + clustering + rule scoring
- Overlay topics (stocks/keywords/geopolitics) as append-only sections
- LLM provider routing (Bailian primary, Gemini fallback)
- Incremental push ledger (SQLite) and hourly GitHub workflow

## Out of Scope (MVP)

- Browser dashboard UI
- Mandatory scraping of anti-bot protected sites
- Quant backtesting and historical alpha metrics
