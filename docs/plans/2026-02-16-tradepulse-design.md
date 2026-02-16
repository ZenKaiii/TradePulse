# TradePulse Design (MVP)

Date: 2026-02-16
Project: TradePulse (renamed from open-news)
Audience: US stock trader (Chinese output, source-attributed, incremental push)

## 1. Goals

- Build an AI-native news aggregation and analysis tool for US stock traders.
- Run hourly on GitHub Actions with incremental pushes.
- Deliver Chinese summaries with clear source attribution.
- Prioritize Alibaba Cloud Bailian as primary LLM and Gemini as fallback (secret-driven auto enablement).
- Keep configuration beginner-friendly while retaining power for advanced users.

## 2. Non-Goals (MVP)

- No mandatory web UI dashboard (CLI + config + push-first delivery).
- No default scraping of protected websites requiring anti-bot bypass.
- No intraday quantitative backtesting in MVP.

## 3. Core Product Decisions

### 3.1 Primary signal design

- Mainline output is importance-first, not keyword-first.
- Every hourly run selects Top 10 most important event clusters.
- Keyword/ticker/geopolitics are "topic overlays" appended to the digest, not hard filters.

### 3.2 NewsMinimalist integration strategy

- Do not default to direct scraping.
- Create an optional `NewsMinimalistAdapter` placeholder interface.
- Enable only if a compliant and stable feed/API/token is provided by user later.

### 3.3 Output requirements

Each key item must include:
- Chinese summary
- Market direction: Bullish / Bearish / Neutral
- Affected symbols: ticker + company name
- Trading impact explanation (short)
- Source list (publisher + original URL)

## 4. System Architecture (MVP)

Pipeline:
1. Ingest (RSS/API adapters)
2. Normalize (canonical article schema)
3. Deduplicate + cluster (event-level grouping)
4. Score (rule + LLM hybrid importance scoring)
5. Compose (Top10 mainline + overlay sections)
6. Deliver (DingTalk / Telegram / Feishu via plugin notifiers)
7. Persist (incremental state for idempotent pushes)

Core components:
- `sources/`: Source adapters and health checks
- `pipeline/`: Normalize, dedupe, cluster, score
- `llm/`: Unified LLM gateway with fallback
- `overlays/`: ticker/keyword/geopolitical matching
- `deliveries/`: channel notifiers
- `storage/`: SQLite incremental and run metadata
- `app/`: orchestration and CLI entry

## 5. Data Model (canonical)

Canonical article fields:
- `id`, `title`, `summary_raw`, `url`, `source_name`, `published_at`
- `language`, `content_hash`, `source_type`, `fetched_at`

Cluster fields:
- `cluster_id`, `article_ids`, `representative_title`, `coverage_count`
- `first_seen_at`, `last_seen_at`

Scoring fields:
- `rule_score`, `llm_score`, `importance_score`
- `impact_direction`, `affected_tickers[]`, `impact_reason`

Push ledger:
- `cluster_id`, `pushed_at`, `push_channels`, `run_id`

## 6. Scoring Strategy

Hybrid formula:
- `importance_score = 0.4 * rule_score + 0.6 * llm_score`

Rule score factors:
- source credibility weight
- independent coverage breadth
- recency decay
- market-relevance lexicon hit
- policy/regulation/earnings/geopolitics priors

LLM score factors:
- expected impact intensity for US equities (0-10)
- scope (index/sector/single-stock)
- confidence and expected time horizon

Fallback:
- If LLM unavailable, use rule-only ranking and template summary.

## 7. Topic Overlays (not filters)

Overlay types:
- Ticker overlays: ticker + aliases/company names (e.g., NVDA/NVIDIA/英伟达)
- Keyword overlays: user-defined topics
- Geopolitical overlays: predefined packages (Middle East, Russia-Ukraine, Taiwan Strait, shipping chokepoints)

Behavior:
- Mainline Top10 is always generated first.
- Overlay matches are appended in dedicated sections.

## 8. Configuration Design (beginner-first)

Primary file:
- `config/user.yaml` only for common settings.

Required user-facing knobs:
- `watchlists.stocks`
- `watchlists.keywords`
- `watchlists.geopolitics`
- `sources.profile` (`balanced` / `trader`)
- `delivery.channels`
- `digest.top_n` (default 10)

Advanced options:
- `config/advanced.yaml` (optional)

## 9. LLM & Secret-driven Provider Routing

Provider auto-detection:
- Use Bailian first when Bailian secrets are present.
- Fall back to Gemini when Bailian call fails or is unavailable.
- If neither configured, continue in non-LLM degrade mode.

No manual provider routing required for basic users.

## 10. Source Strategy

Source tiers:
- `core`: default enabled, high-signal low-noise
- `extended`: optional, broader coverage
- `experimental`: testing candidates

Candidate pools:
- awesome-tech-rss and awesome-rss-feeds are used as seed catalogs, not blindly enabled.
- Feed health gates before promotion to `core/extended`:
  - availability
  - update cadence
  - duplicate ratio
  - noise ratio

## 11. Delivery & Message Format

Digest structure:
1. Hourly Top10 key events
2. Overlay hits (stocks/keywords/geopolitics)
3. Trading implications (risk/opportunity/watch)
4. Source attribution (publisher + URL)

Channels:
- DingTalk default
- Telegram/Feishu optional by secrets
- Channel failures are isolated (best-effort fanout)

## 12. Reliability & Incremental Push

- SQLite push ledger guarantees no duplicate push for same cluster.
- Hourly GitHub Actions schedule.
- Retries with exponential backoff for transient failures.
- Run-level status summary appended to message when partial failures occur.

## 13. OpenSpec + SDD Alignment

- Use OpenSpec change/spec artifacts to define scope and acceptance before coding.
- Implement using TDD cycle task-by-task.
- Validate OpenSpec artifacts and run tests in CI.
- Keep traceability from requirement -> test -> module.

## 14. Test Strategy (MVP)

Unit tests:
- dedupe/cluster behavior
- scoring math and bounds
- direction classification (bullish/bearish/neutral)
- ticker alias resolution

Integration tests:
- ingest -> cluster -> score -> compose
- LLM fallback path (Bailian fail -> Gemini)
- notifier payload rendering with source attribution

E2E checks:
- GitHub Actions dry-run
- incremental no-duplicate guarantees across consecutive runs

## 15. MVP Deliverables

- Runnable Python project with hourly GitHub Action.
- Chinese digest with source links and impact direction.
- Secret-driven provider/channel auto-enable.
- Beginner-friendly configuration and docs.
- OpenSpec artifacts + tests + CI baseline.

