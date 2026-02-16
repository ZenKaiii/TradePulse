from typing import Dict, List


def _map_direction(direction: str) -> str:
    return {"bullish": "利好", "bearish": "利空", "neutral": "中性"}.get(direction, "中性")


def _format_tickers(tickers: List[Dict[str, str]]) -> str:
    if not tickers:
        return "未识别"
    return ", ".join(f"{item['symbol']} ({item['name']})" for item in tickers)


def compose_digest(top_events: List[Dict], overlays: Dict[str, List[str]]) -> str:
    lines = [
        "# TradePulse 每小时快报",
        "",
        "## A. 本小时关键事件 Top10",
    ]

    for index, event in enumerate(top_events, start=1):
        lines.append(f"{index}. {event.get('title', 'Untitled')}")
        lines.append(f"   - 市场方向: {_map_direction(event.get('direction', 'neutral'))}")
        lines.append(f"   - 相关标的: {_format_tickers(event.get('affected_tickers', []))}")
        lines.append(f"   - 影响说明: {event.get('impact_reason_zh', '暂无')}")

        for source in event.get("sources", []):
            lines.append(f"   - 来源: {source.get('name', 'Unknown')} {source.get('url', '')}")

    lines.append("")
    lines.append("## B. 专题命中")
    lines.append(f"- 股票专题: {', '.join(overlays.get('stocks', [])) or '无'}")
    lines.append(f"- 关键词专题: {', '.join(overlays.get('keywords', [])) or '无'}")
    lines.append(f"- 地缘专题: {', '.join(overlays.get('geopolitics', [])) or '无'}")

    return "\n".join(lines)
