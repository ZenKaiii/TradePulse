from typing import Dict, List, Optional


def _map_direction(direction: str) -> str:
    return {"bullish": "利好", "bearish": "利空", "neutral": "中性"}.get(direction, "中性")


def _format_tickers(tickers: List[Dict[str, str]]) -> str:
    if not tickers:
        return "未识别"
    return ", ".join(f"{item['symbol']} ({item['name']})" for item in tickers)


def _format_net_flow(value: float) -> str:
    return f"{value / 100000000.0:+.2f}亿"


def compose_digest(
    top_events: List[Dict],
    overlays: Dict[str, List[str]],
    market_regime: Optional[Dict] = None,
) -> str:
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

    if market_regime:
        lines.append("")
        lines.append("## C. Section 4 板块轮动与资金流")

        us = market_regime.get("us", {})
        lines.append("### 美股行业相对强弱（4W/12W 对比 SPY+QQQ）")
        if us.get("status") == "ok":
            leaders = us.get("leaders", [])
            laggards = us.get("laggards", [])

            if leaders:
                lines.append("- 领先板块:")
                for item in leaders:
                    lines.append(
                        "  - {symbol} ({name}) 综合 {score:+.2f}%"
                        " | 4W {rs_4w:+.2f}% | 12W {rs_12w:+.2f}%".format(
                            symbol=item.get("symbol", ""),
                            name=item.get("name", ""),
                            score=float(item.get("score", 0.0)),
                            rs_4w=float(item.get("rs_4w", 0.0)),
                            rs_12w=float(item.get("rs_12w", 0.0)),
                        )
                    )
            else:
                lines.append("- 领先板块: 无")

            if laggards:
                lines.append("- 落后板块:")
                for item in laggards:
                    lines.append(
                        "  - {symbol} ({name}) 综合 {score:+.2f}%"
                        " | 4W {rs_4w:+.2f}% | 12W {rs_12w:+.2f}%".format(
                            symbol=item.get("symbol", ""),
                            name=item.get("name", ""),
                            score=float(item.get("score", 0.0)),
                            rs_4w=float(item.get("rs_4w", 0.0)),
                            rs_12w=float(item.get("rs_12w", 0.0)),
                        )
                    )
            else:
                lines.append("- 落后板块: 无")
        else:
            lines.append(f"- {us.get('message', '美股板块数据暂不可用')}")

        a_share = market_regime.get("a_share", {})
        lines.append("### A股行业资金流（东财）")
        if a_share.get("status") == "ok":
            inflow = a_share.get("inflow", [])
            outflow = a_share.get("outflow", [])

            if inflow:
                lines.append("- 净流入前列:")
                for item in inflow:
                    lines.append(
                        "  - {name} 净流入 {flow} | 涨跌幅 {pct:+.2f}%".format(
                            name=item.get("name", ""),
                            flow=_format_net_flow(float(item.get("net_flow", 0.0))),
                            pct=float(item.get("change_pct", 0.0)),
                        )
                    )
            else:
                lines.append("- 净流入前列: 无")

            if outflow:
                lines.append("- 净流出前列:")
                for item in outflow:
                    lines.append(
                        "  - {name} 净流出 {flow} | 涨跌幅 {pct:+.2f}%".format(
                            name=item.get("name", ""),
                            flow=_format_net_flow(float(item.get("net_flow", 0.0))),
                            pct=float(item.get("change_pct", 0.0)),
                        )
                    )
            else:
                lines.append("- 净流出前列: 无")
        else:
            lines.append(f"- {a_share.get('message', 'A股资金流数据暂不可用')}")

    return "\n".join(lines)
