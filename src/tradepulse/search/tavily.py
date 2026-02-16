import os
from typing import Any, Dict, List, Mapping, Optional, Tuple

import httpx

from tradepulse.config import SearchEnhanceConfig


def _build_context(payload: Dict[str, Any]) -> str:
    answer = str(payload.get("answer", "")).strip()
    results = payload.get("results", [])
    if answer:
        return answer
    if isinstance(results, list) and results:
        first = results[0] if isinstance(results[0], dict) else {}
        title = str(first.get("title", "")).strip()
        url = str(first.get("url", "")).strip()
        if title and url:
            return f"{title} ({url})"
        if title:
            return title
    return ""


def _search_tavily(
    query: str,
    cfg: SearchEnhanceConfig,
    api_key: str,
) -> Dict[str, Any]:
    response = httpx.post(
        "https://api.tavily.com/search",
        json={
            "api_key": api_key,
            "query": query,
            "topic": "news",
            "search_depth": "basic",
            "max_results": cfg.max_results,
            "include_answer": True,
        },
        timeout=cfg.timeout_sec,
    )
    response.raise_for_status()
    return response.json()


def enrich_events_with_tavily(
    events: List[Dict[str, Any]],
    cfg: SearchEnhanceConfig,
    environ: Optional[Mapping[str, str]] = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    if not events or not cfg.enabled:
        return events, {"provider": "none", "hits": 0, "failures": 0}

    env = dict(environ or os.environ)
    api_key = env.get("TAVILY_API_KEY", "").strip()
    if not api_key:
        return events, {"provider": "tavily", "hits": 0, "failures": 0, "reason": "missing_api_key"}

    hits = 0
    failures = 0
    enriched: List[Dict[str, Any]] = []
    for index, event in enumerate(events):
        updated = dict(event)
        if index < cfg.top_n and str(event.get("analysis_level", "")).lower() == "detailed":
            try:
                payload = _search_tavily(str(event.get("title", "")), cfg, api_key)
                context = _build_context(payload)
                if context:
                    updated["search_context"] = context
                    hits += 1
            except Exception as exc:
                failures += 1
                print(f"[tradepulse][search] tavily failed: {str(exc)}")
        enriched.append(updated)

    return enriched, {"provider": "tavily", "hits": hits, "failures": failures}
