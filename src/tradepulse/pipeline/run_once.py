from pathlib import Path
from typing import Dict, List
import os
import hashlib

from tradepulse.compose import compose_digest
from tradepulse.config import load_user_config
from tradepulse.models import CanonicalArticle
from tradepulse.notifiers import send_best_effort
from tradepulse.notifiers.dingtalk import send as send_dingtalk
from tradepulse.notifiers.feishu import send as send_feishu
from tradepulse.notifiers.telegram import send as send_telegram
from tradepulse.overlays import match_overlays
from tradepulse.pipeline.cluster import cluster_articles
from tradepulse.pipeline.rule_score import score_cluster
from tradepulse.sources import fetch_articles_from_feeds
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


def _collect_senders(text: str):
    senders = []
    dingtalk_webhook = os.getenv("DINGTALK_WEBHOOK_URL", "")
    if dingtalk_webhook:
        senders.append(lambda: send_dingtalk(dingtalk_webhook, text))

    telegram_bot = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat = os.getenv("TELEGRAM_CHAT_ID", "")
    if telegram_bot and telegram_chat:
        senders.append(lambda: send_telegram(telegram_bot, telegram_chat, text))

    feishu_webhook = os.getenv("FEISHU_WEBHOOK_URL", "")
    if feishu_webhook:
        senders.append(lambda: send_feishu(feishu_webhook, text))

    return senders


def run_once(dry_run: bool = False) -> Dict:
    root = _project_root()
    user_cfg_path = root / "config" / "user.yaml"
    if not user_cfg_path.exists():
        user_cfg_path = root / "config" / "user.example.yaml"

    config = load_user_config(user_cfg_path)
    fetched_articles = fetch_articles_from_feeds(config.sources.profile)
    articles = fetched_articles or _sample_articles()
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

    overlay_hits = match_overlays(
        [event["title"] for event in top_events],
        stocks=config.watchlists.stocks,
        keywords=config.watchlists.keywords,
        geopolitics=config.watchlists.geopolitics,
    )

    digest = compose_digest(top_events=top_events, overlays=overlay_hits)

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
        errors = send_best_effort(_collect_senders(digest))

    return {
        "digest": digest,
        "stats": {
            "total_clusters": len(clusters),
            "top_events": len(top_events),
            "new_events": pushed_count,
            "delivery_errors": len(errors),
        },
    }
