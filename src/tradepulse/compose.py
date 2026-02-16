from typing import Dict, List, Optional

US_SECTOR_REP_STOCKS = {
    "XLK": "AAPL, MSFT, NVDA",
    "XLF": "JPM, BAC, WFC",
    "XLE": "XOM, CVX, COP",
    "XLV": "LLY, UNH, JNJ",
    "XLY": "AMZN, TSLA, HD",
    "XLP": "PG, KO, PEP",
    "XLI": "CAT, GE, HON",
    "XLC": "GOOGL, META, NFLX",
    "XLRE": "PLD, AMT, EQIX",
    "XLB": "LIN, APD, SHW",
    "XLU": "NEE, SO, DUK",
}
A_SHARE_SECTOR_REP_STOCKS = {
    "电子": "立讯精密, 工业富联, 歌尔股份",
    "半导体": "中芯国际, 北方华创, 韦尔股份",
    "银行": "招商银行, 工商银行, 建设银行",
    "房地产": "保利发展, 万科A, 招商蛇口",
    "电力设备": "宁德时代, 隆基绿能, 阳光电源",
}


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
    analysis_meta: Optional[Dict] = None,
    market_regime: Optional[Dict] = None,
) -> str:
    provider = (analysis_meta or {}).get("provider", "rule")
    model = (analysis_meta or {}).get("model", "rule-engine")
    lines = [
        "# 📡 TradePulse 每小时快报",
        "",
        f"> 🤖 分析引擎: `{provider}/{model}` | 策略: 前5条详细 + 后5条简版",
        "",
        "## A. 本小时关键事件 Top10（含中文解读）",
    ]

    for index, event in enumerate(top_events, start=1):
        level = event.get("analysis_level", "brief")
        level_text = "详细" if level == "detailed" else "简版"
        summary = event.get("summary_zh") or event.get("title", "暂无")
        lines.append(f"{index}. 📰 {event.get('title', 'Untitled')}（{level_text}）")
        lines.append(f"   - 🧠 中文摘要: {summary}")
        lines.append(f"   - 📈 市场方向: {_map_direction(event.get('direction', 'neutral'))}")
        lines.append(f"   - 🎯 相关标的: {_format_tickers(event.get('affected_tickers', []))}")
        lines.append(f"   - 🔍 影响说明: {event.get('impact_reason_zh', '暂无')}")
        if level == "detailed":
            lines.append(
                f"   - 👶 小白解读: {event.get('beginner_note_zh', '可先关注是否影响行业龙头和市场风险偏好')}"
            )

        for source in event.get("sources", []):
            lines.append(f"   - 🔗 来源: {source.get('name', 'Unknown')} {source.get('url', '')}")

    lines.append("")
    lines.append("## B. 专题命中（你关注的附加主题）")
    lines.append("- ℹ️ 说明: 专题命中不会改变主线Top10排序，只做额外提醒。")
    lines.append(f"- 🏷️ 股票专题: {', '.join(overlays.get('stocks', [])) or '无'}")
    lines.append(f"- 🧷 关键词专题: {', '.join(overlays.get('keywords', [])) or '无'}")
    lines.append(f"- 🌍 地缘专题: {', '.join(overlays.get('geopolitics', [])) or '无'}")

    if market_regime:
        lines.append("")
        lines.append("## C. Section 4 板块轮动与资金流")
        lines.append("- ℹ️ 指标说明: 4W/12W 表示近4周/12周相对SPY+QQQ的强弱，综合分越高说明资金偏好越强。")

        us = market_regime.get("us", {})
        lines.append("### 美股行业相对强弱（4W/12W 对比 SPY+QQQ）")
        if us.get("status") == "ok":
            leaders = us.get("leaders", [])
            laggards = us.get("laggards", [])

            if leaders:
                lines.append("- 领先板块:")
                for item in leaders:
                    rep = US_SECTOR_REP_STOCKS.get(item.get("symbol", ""), "代表股待补充")
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
                    lines.append(f"    - 代表股: {rep}")
            else:
                lines.append("- 领先板块: 无")

            if laggards:
                lines.append("- 落后板块:")
                for item in laggards:
                    rep = US_SECTOR_REP_STOCKS.get(item.get("symbol", ""), "代表股待补充")
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
                    lines.append(f"    - 代表股: {rep}")
            else:
                lines.append("- 落后板块: 无")
        else:
            lines.append(f"- {us.get('message', '美股板块数据暂不可用')}")

        a_share = market_regime.get("a_share", {})
        lines.append("### A股行业资金流（东财）")
        lines.append("- ℹ️ 指标说明: 净流入为正代表资金净买入，净流出为负代表资金净卖出。")
        if a_share.get("status") == "ok":
            inflow = a_share.get("inflow", [])
            outflow = a_share.get("outflow", [])

            if inflow:
                lines.append("- 净流入前列:")
                for item in inflow:
                    rep = A_SHARE_SECTOR_REP_STOCKS.get(item.get("name", ""), "对应行业龙头（请结合自选股）")
                    lines.append(
                        "  - {name} 净流入 {flow} | 涨跌幅 {pct:+.2f}%".format(
                            name=item.get("name", ""),
                            flow=_format_net_flow(float(item.get("net_flow", 0.0))),
                            pct=float(item.get("change_pct", 0.0)),
                        )
                    )
                    lines.append(f"    - 代表股: {rep}")
            else:
                lines.append("- 净流入前列: 无")

            if outflow:
                lines.append("- 净流出前列:")
                for item in outflow:
                    rep = A_SHARE_SECTOR_REP_STOCKS.get(item.get("name", ""), "对应行业龙头（请结合自选股）")
                    lines.append(
                        "  - {name} 净流出 {flow} | 涨跌幅 {pct:+.2f}%".format(
                            name=item.get("name", ""),
                            flow=_format_net_flow(float(item.get("net_flow", 0.0))),
                            pct=float(item.get("change_pct", 0.0)),
                        )
                    )
                    lines.append(f"    - 代表股: {rep}")
            else:
                lines.append("- 净流出前列: 无")
        else:
            lines.append(f"- {a_share.get('message', 'A股资金流数据暂不可用')}")

    return "\n".join(lines)
