import json
import os
import re
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

import httpx

from tradepulse.config import LLMConfig


def select_provider(llm_config: LLMConfig, environ: Optional[Mapping[str, str]] = None) -> str:
    env = dict(environ or os.environ)
    forced = (llm_config.provider or "auto").strip().lower()
    has_bailian = bool(env.get("BAILIAN_API_KEY"))
    has_gemini = bool(env.get("GEMINI_API_KEY"))

    if forced == "bailian":
        return "bailian" if has_bailian else "none"
    if forced == "gemini":
        return "gemini" if has_gemini else "none"
    if has_bailian:
        return "bailian"
    if has_gemini:
        return "gemini"
    return "none"


def _fallback_analysis(event: Dict[str, Any], detail_mode: str) -> Dict[str, Any]:
    title = str(event.get("title", ""))
    if detail_mode == "brief":
        summary = f"【规则回退】{title[:60]}..." if len(title) > 60 else f"【规则回退】{title}"
    else:
        summary = f"【规则回退】{title[:80]}..." if len(title) > 80 else f"【规则回退】{title}"

    return {
        "summary_zh": summary or "暂无有效摘要",
        "impact_reason_zh": "规则引擎推断：需结合板块与成交量判断",
        "direction": str(event.get("direction", "neutral")),
        "affected_tickers": list(event.get("affected_tickers", [])),
        "beginner_note_zh": "该信息需结合行业趋势与成交量综合判断",
        "provider": "rule",
        "model": "rule-engine",
    }


def _build_prompt(event: Dict[str, Any], detail_mode: str) -> str:
    title = event.get("title", "")
    sources = ", ".join(item.get("name", "Unknown") for item in event.get("sources", []))
    detail_requirement = (
        "请输出较详细解释，summary_zh 40-80字，impact_reason_zh 40-80字，beginner_note_zh 30-60字。"
        if detail_mode == "detailed"
        else "请输出简版解释，summary_zh 15-35字，impact_reason_zh 15-35字，beginner_note_zh 15-35字。"
    )
    return (
        "你是面向美股交易新手的新闻分析助手。请基于事件标题做中文解释。"
        "必须只返回JSON对象，不要markdown。\n"
        "字段要求：summary_zh, impact_reason_zh, direction, affected_tickers, beginner_note_zh。\n"
        "direction仅能是: bullish, bearish, neutral。\n"
        "affected_tickers为数组，每项含symbol和name。若无则返回空数组。\n"
        f"{detail_requirement}\n"
        f"标题: {title}\n"
        f"来源: {sources}\n"
    )


def _extract_json(text: str) -> Dict[str, Any]:
    cleaned = text.strip()
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if not match:
        raise ValueError("no json object found")
    return json.loads(match.group(0))


def _normalize_direction(value: Any, fallback: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"bullish", "bearish", "neutral"}:
        return normalized
    return fallback


def _normalize_tickers(value: Any) -> List[Dict[str, str]]:
    if not isinstance(value, list):
        return []
    result: List[Dict[str, str]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        symbol = str(item.get("symbol", "")).strip().upper()
        name = str(item.get("name", symbol)).strip()
        if symbol:
            result.append({"symbol": symbol, "name": name or symbol})
    return result


def _call_bailian_with_retry(prompt: str, llm_config: LLMConfig, api_key: str) -> str:
    last_exception = None
    for attempt in range(llm_config.max_retries + 1):
        try:
            return _call_bailian(prompt, llm_config, api_key)
        except Exception as exc:
            last_exception = exc
            if attempt < llm_config.max_retries:
                import time
                backoff = llm_config.retry_backoff_sec * (attempt + 1)
                print(f"[tradepulse][llm] bailian attempt {attempt + 1} failed: {str(exc)}, retrying in {backoff}s...")
                time.sleep(backoff)
    if last_exception:
        raise last_exception
    raise RuntimeError("bailian call failed with no exception")


def _call_gemini_with_retry(prompt: str, llm_config: LLMConfig, api_key: str) -> str:
    last_exception = None
    for attempt in range(llm_config.max_retries + 1):
        try:
            return _call_gemini(prompt, llm_config, api_key)
        except Exception as exc:
            last_exception = exc
            if attempt < llm_config.max_retries:
                import time
                backoff = llm_config.retry_backoff_sec * (attempt + 1)
                print(f"[tradepulse][llm] gemini attempt {attempt + 1} failed: {str(exc)}, retrying in {backoff}s...")
                time.sleep(backoff)
    if last_exception:
        raise last_exception
    raise RuntimeError("gemini call failed with no exception")


def _call_bailian(prompt: str, llm_config: LLMConfig, api_key: str) -> str:
    url = f"{llm_config.bailian_base_url.rstrip('/')}/chat/completions"
    response = httpx.post(
        url,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": llm_config.bailian_model,
            "messages": [
                {"role": "system", "content": "你是金融新闻分析助手，只输出JSON。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": llm_config.temperature,
            "response_format": {"type": "json_object"},
        },
        timeout=llm_config.timeout_sec,
    )
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                text_parts.append(str(item.get("text", "")))
            else:
                text_parts.append(str(item))
        return "\n".join(part for part in text_parts if part)
    return str(content)


def _call_bailian_fallback(prompt: str, llm_config: LLMConfig, api_key: str) -> str:
    url = f"{llm_config.bailian_base_url.rstrip('/')}/chat/completions"
    response = httpx.post(
        url,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": llm_config.bailian_fallback_model,
            "messages": [
                {"role": "system", "content": "你是金融新闻分析助手，只输出JSON。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": llm_config.temperature,
            "response_format": {"type": "json_object"},
        },
        timeout=llm_config.timeout_sec,
    )
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                text_parts.append(str(item.get("text", "")))
            else:
                text_parts.append(str(item))
        return "\n".join(part for part in text_parts if part)
    return str(content)


def _call_gemini(prompt: str, llm_config: LLMConfig, api_key: str) -> str:
    url = (
        f"{llm_config.gemini_base_url.rstrip('/')}/models/"
        f"{llm_config.gemini_model}:generateContent?key={api_key}"
    )
    response = httpx.post(
        url,
        json={
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": llm_config.temperature,
                "responseMimeType": "application/json",
            },
        },
        timeout=llm_config.timeout_sec,
    )
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def generate_event_analysis(
    event: Dict[str, Any],
    detail_mode: str,
    llm_config: LLMConfig,
    provider: str,
    environ: Optional[Mapping[str, str]] = None,
) -> Dict[str, Any]:
    env = dict(environ or os.environ)
    prompt = _build_prompt(event, detail_mode)

    final_provider = provider
    final_model = llm_config.bailian_model if provider == "bailian" else llm_config.gemini_model

    raw_text = ""
    if provider == "bailian":
        try:
            raw_text = _call_bailian_with_retry(prompt, llm_config, env["BAILIAN_API_KEY"])
        except Exception as primary_exc:
            print(f"[tradepulse][llm] primary model {llm_config.bailian_model} failed: {str(primary_exc)}, trying fallback model...")
            try:
                raw_text = _call_bailian_fallback(prompt, llm_config, env["BAILIAN_API_KEY"])
                final_model = llm_config.bailian_fallback_model
                print(f"[tradepulse][llm] fallback model {llm_config.bailian_fallback_model} succeeded")
            except Exception as fallback_exc:
                if env.get("GEMINI_API_KEY"):
                    raw_text = _call_gemini_with_retry(prompt, llm_config, env["GEMINI_API_KEY"])
                    final_provider = "gemini"
                    final_model = llm_config.gemini_model
                else:
                    raise fallback_exc
    elif provider == "gemini":
        raw_text = _call_gemini_with_retry(prompt, llm_config, env["GEMINI_API_KEY"])
    else:
        raise RuntimeError("no provider available")

    fallback = _fallback_analysis(event, detail_mode)
    try:
        parsed = _extract_json(raw_text)
    except Exception:
        parsed = {
            "summary_zh": raw_text.strip()[:120] or fallback["summary_zh"],
            "impact_reason_zh": fallback["impact_reason_zh"],
            "direction": fallback["direction"],
            "affected_tickers": fallback["affected_tickers"],
            "beginner_note_zh": fallback["beginner_note_zh"],
        }

    return {
        "summary_zh": str(parsed.get("summary_zh") or fallback["summary_zh"]),
        "impact_reason_zh": str(parsed.get("impact_reason_zh") or fallback["impact_reason_zh"]),
        "direction": _normalize_direction(parsed.get("direction"), fallback["direction"]),
        "affected_tickers": _normalize_tickers(parsed.get("affected_tickers"))
        or fallback["affected_tickers"],
        "beginner_note_zh": str(parsed.get("beginner_note_zh") or fallback["beginner_note_zh"]),
        "provider": final_provider,
        "model": final_model,
    }


def enrich_top_events_with_llm(
    events: List[Dict[str, Any]],
    llm_config: LLMConfig,
    environ: Optional[Mapping[str, str]] = None,
    generate_fn: Optional[
        Callable[[Dict[str, Any], str, LLMConfig, str], Dict[str, Any]]
    ] = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    if not events:
        return events, {"provider": "rule", "model": "rule-engine"}

    provider = select_provider(llm_config, environ)
    if not llm_config.enabled or provider == "none":
        return events, {"provider": "rule", "model": "rule-engine", "attempted_provider": provider, "failures": 0}

    generator = generate_fn or (
        lambda event, detail_mode, cfg, selected_provider: generate_event_analysis(
            event=event,
            detail_mode=detail_mode,
            llm_config=cfg,
            provider=selected_provider,
            environ=environ,
        )
    )

    enriched: List[Dict[str, Any]] = []
    used_provider = provider
    used_model = llm_config.bailian_model if provider == "bailian" else llm_config.gemini_model
    failures = 0

    for index, event in enumerate(events):
        detail_mode = "detailed" if index < llm_config.detail_top_n else "brief"
        fallback = _fallback_analysis(event, detail_mode)
        try:
            analysis = generator(event, detail_mode, llm_config, provider)
        except Exception as exc:
            failures += 1
            print(
                f"[tradepulse][llm] analysis failed for provider={provider}: {str(exc)}"
            )
            analysis = fallback

        merged = dict(event)
        merged["summary_zh"] = analysis.get("summary_zh", fallback["summary_zh"])
        merged["impact_reason_zh"] = analysis.get("impact_reason_zh", fallback["impact_reason_zh"])
        merged["direction"] = _normalize_direction(
            analysis.get("direction"),
            fallback["direction"],
        )
        merged["affected_tickers"] = analysis.get("affected_tickers", fallback["affected_tickers"])
        merged["beginner_note_zh"] = analysis.get("beginner_note_zh", fallback["beginner_note_zh"])
        merged["analysis_level"] = detail_mode
        merged["analysis_provider"] = analysis.get("provider", fallback["provider"])
        merged["analysis_model"] = analysis.get("model", fallback["model"])

        used_provider = merged["analysis_provider"]
        used_model = merged["analysis_model"]
        enriched.append(merged)

    return enriched, {
        "provider": used_provider,
        "model": used_model,
        "attempted_provider": provider,
        "failures": failures,
    }
