from pathlib import Path
from typing import Dict, List
import os
import hashlib

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
    for cluster in clusters:
        representative = cluster.articles[0]
        score = score_cluster(representative.title, coverage_count=cluster.coverage_count)
        scored_events.append(
            {
                "cluster_id": cluster.cluster_id,
                "title": representative.title,
                "direction": score.direction,
                "affected_tickers": score.affected_tickers,
                "impact_reason_zh": "基于事件重要性与市场语义规则推断",
                "sources": [
                    {"name": item.source_name, "url": item.url} for item in cluster.articles
                ],
                "importance_score": score.rule_score,
            }
        )

    scored_events.sort(key=lambda item: item["importance_score"], reverse=True)
    top_events = scored_events[: config.digest.top_n]
    top_events, analysis_meta = enrich_top_events_with_llm(top_events, config.llm)

    overlay_hits = match_overlays(
        [event["title"] for event in top_events],
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

    ledger_dir = root / "data"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    ledger = PushLedger(ledger_dir / "state.db")

    pushed_count = 0
    for event in top_events:
        if ledger.should_push(event["cluster_id"]):
            if not dry_run:
                ledger.mark_pushed(event["cluster_id"], "run-once")
            pushed_count += 1

    errors = []
    if not dry_run:
        errors = send_best_effort(_collect_senders(digest, config.delivery.channels))

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
