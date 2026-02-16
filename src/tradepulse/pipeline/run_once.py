from pathlib import Path
from typing import Dict, List
import os
import hashlib
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from tradepulse.compose import compose_digest
from tradepulse.config import apply_env_overrides, load_user_config
from tradepulse.llm import enrich_top_events_with_llm
from tradepulse.market import MarketRegimeOptions, build_market_regime_snapshot
from tradepulse.models import CanonicalArticle
from tradepulse.notifiers import send_best_effort
from tradepulse.notifiers.dingtalk import send as send_dingtalk
from tradepulse.notifiers.feishu import send as send_feishu
from tradepulse.notifiers.telegram import send as send_telegram
from tradepulse.overlays import match_overlays
from tradepulse.pipeline.cluster import cluster_articles
from tradepulse.pipeline.rule_score import score_cluster
from tradepulse.sources import fetch_articles_with_health
from tradepulse.storage import PushLedger


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _sample_articles() -> List[CanonicalArticle]:
    samples = [
        (
            "NVIDIA raises guidance as AI demand surges",
            "https://news.example.com/nvda-guidance",
            "Reuters",
        ),
        (
            "US proposes tighter export controls on advanced chips",
            "https://news.example.com/export-controls",
            "Bloomberg",
        ),
        (
            "Fed officials signal potential rate cut path",
            "https://news.example.com/fed-rates",
            "WSJ",
        ),
    ]
    out = []
    for title, url, source in samples:
        aid = hashlib.sha1(f"{title}|{url}|{source}".encode("utf-8")).hexdigest()
        out.append(
            CanonicalArticle(
                id=aid,
                title=title,
                url=url,
                source_name=source,
                published_at="",
                summary_raw=title,
            )
        )
    return out


def _collect_senders(text: str, channels: List[str]):
    senders = []
    enabled = {channel.lower() for channel in channels}

    dingtalk_webhook = os.getenv("DINGTALK_WEBHOOK_URL", "")
    if "dingtalk" in enabled and dingtalk_webhook:
        senders.append(lambda: send_dingtalk(dingtalk_webhook, text))

    telegram_bot = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat = os.getenv("TELEGRAM_CHAT_ID", "")
    if "telegram" in enabled and telegram_bot and telegram_chat:
        senders.append(lambda: send_telegram(telegram_bot, telegram_chat, text))

    feishu_webhook = os.getenv("FEISHU_WEBHOOK_URL", "")
    if "feishu" in enabled and feishu_webhook:
        senders.append(lambda: send_feishu(feishu_webhook, text))

    return senders


def _unique(items: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in items:
        key = item.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def resolve_channels(configured_channels: List[str], environ: Dict[str, str] | None = None) -> List[str]:
    env = dict(environ or os.environ)
    explicit = str(env.get("TRADEPULSE_CHANNELS", "")).strip()
    base_channels = _unique(configured_channels)

    # Explicit channel config has highest priority.
    if explicit:
        return base_channels

    auto = list(base_channels)
    if env.get("DINGTALK_WEBHOOK_URL"):
        auto.append("dingtalk")
    if env.get("TELEGRAM_BOT_TOKEN") and env.get("TELEGRAM_CHAT_ID"):
        auto.append("telegram")
    if env.get("FEISHU_WEBHOOK_URL"):
        auto.append("feishu")
    return _unique(auto)


def _age_hours(published_at: str, now: datetime) -> float | None:
    if not published_at:
        return None
    try:
        parsed = parsedate_to_datetime(published_at)
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    delta = now - parsed.astimezone(timezone.utc)
    return max(delta.total_seconds() / 3600.0, 0.0)


def _apply_source_cap(events: List[Dict], max_per_source: int) -> List[Dict]:
    selected: List[Dict] = []
    source_counts: Dict[str, int] = {}
    for event in events:
        source_name = str(event.get("primary_source", "Unknown"))
        if source_counts.get(source_name, 0) >= max_per_source:
            continue
        source_counts[source_name] = source_counts.get(source_name, 0) + 1
        selected.append(event)
    return selected


def run_once(dry_run: bool = False) -> Dict:
    root = _project_root()
    config_path_env = os.getenv("TRADEPULSE_CONFIG_PATH", "").strip()
    if config_path_env:
        candidate = Path(config_path_env)
        user_cfg_path = candidate if candidate.is_absolute() else root / candidate
    else:
        user_cfg_path = root / "config" / "user.yaml"

    if not user_cfg_path.exists():
        user_cfg_path = root / "config" / "user.example.yaml"

    config = apply_env_overrides(load_user_config(user_cfg_path), os.environ)
    fetched_articles, feed_health = fetch_articles_with_health(
        profile=config.sources.profile,
        tier=config.sources.tier,
    )
    healthy_sources = {
        record.name
        for record in feed_health
        if record.health_score >= config.sources.min_health_score
    }
    filtered_articles = [item for item in fetched_articles if item.source_name in healthy_sources]
    articles = filtered_articles or fetched_articles or _sample_articles()
    clusters = cluster_articles(articles)

    scored_events = []
    now = datetime.now(timezone.utc)
    for cluster in clusters:
        representative = cluster.articles[0]
        score = score_cluster(representative.title, coverage_count=cluster.coverage_count)
        age_hours = _age_hours(representative.published_at, now)
        is_fresh = age_hours is None or age_hours <= float(config.digest.max_age_hours)
        freshness_bonus = 0.0
        if age_hours is not None:
            freshness_bonus = max(
                0.0,
                2.5 * (1.0 - min(age_hours / float(config.digest.max_age_hours), 1.0)),
            )
        scored_events.append(
            {
                "cluster_id": cluster.cluster_id,
                "title": representative.title,
                "primary_source": representative.source_name,
                "published_at": representative.published_at,
                "direction": score.direction,
                "affected_tickers": score.affected_tickers,
                "impact_reason_zh": "基于事件重要性与市场语义规则推断",
                "sources": [
                    {"name": item.source_name, "url": item.url} for item in cluster.articles
                ],
                "importance_score": score.rule_score,
                "freshness_bonus": round(freshness_bonus, 2),
                "event_score": round(score.rule_score + freshness_bonus, 2),
                "is_fresh": is_fresh,
            }
        )

    scored_events.sort(key=lambda item: item["event_score"], reverse=True)
    fresh_candidates = [item for item in scored_events if item.get("is_fresh")]
    candidate_pool = fresh_candidates
    candidate_pool = _apply_source_cap(candidate_pool, config.digest.max_per_source)

    ledger_dir = root / "data"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    ledger = PushLedger(ledger_dir / "state.db")

    top_events = []
    for event in candidate_pool:
        if ledger.should_push(event["cluster_id"]):
            top_events.append(event)
        if len(top_events) >= config.digest.top_n:
            break

    top_events, analysis_meta = enrich_top_events_with_llm(top_events, config.llm)

    overlay_hits = match_overlays(
        candidate_pool,
        stocks=config.watchlists.stocks,
        keywords=config.watchlists.keywords,
        geopolitics=config.watchlists.geopolitics,
    )

    market_snapshot = build_market_regime_snapshot(
        options=MarketRegimeOptions(
            enabled=config.market_regime.enabled,
            us_enabled=config.market_regime.us_enabled,
            a_share_enabled=config.market_regime.a_share_enabled,
            us_top_n=config.market_regime.us_top_n,
            a_share_top_n=config.market_regime.a_share_top_n,
            request_timeout_sec=config.market_regime.request_timeout_sec,
        )
    )

    digest = compose_digest(
        top_events=top_events,
        overlays=overlay_hits,
        analysis_meta=analysis_meta,
        market_regime=market_snapshot,
    )

    pushed_count = len(top_events)
    if not dry_run:
        for event in top_events:
            ledger.mark_pushed(event["cluster_id"], "run-once")

    errors = []
    channels = resolve_channels(config.delivery.channels)
    if not dry_run:
        errors = send_best_effort(_collect_senders(digest, channels))
        for err in errors:
            print(f"[tradepulse][delivery] {err}")

    return {
        "digest": digest,
        "stats": {
            "feed_count": len(feed_health),
            "healthy_feed_count": len(healthy_sources),
            "total_clusters": len(clusters),
            "top_events": len(top_events),
            "new_events": pushed_count,
            "delivery_errors": len(errors),
            "analysis_provider": analysis_meta.get("provider", "rule"),
            "analysis_model": analysis_meta.get("model", "rule-engine"),
            "analysis_attempted_provider": analysis_meta.get("attempted_provider", "none"),
            "analysis_failures": int(analysis_meta.get("failures", 0)),
        },
    }
