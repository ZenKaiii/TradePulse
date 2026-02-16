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


def _format_usd_million(value: float) -> str:
    return f"{value / 1_000_000.0:+.2f}M"


def _format_usd_billion(value: float) -> str:
    return f"{value / 1_000_000_000.0:.2f}B"


def _format_overlay_topic_list(values: List[Dict]) -> str:
    topics = [str(item.get("topic", "")).strip() for item in values if str(item.get("topic", "")).strip()]
    return ", ".join(topics) if topics else "无"


def _append_overlay_details(lines: List[str], label: str, values: List[Dict]) -> None:
    if not values:
        return
    lines.append(f"- {label}命中详情:")
    for item in values[:3]:
        topic = item.get("topic", "")
        lines.append(f"  - `{topic}` 命中 {int(item.get('count', 0))} 条")
        for hit in item.get("items", [])[:2]:
            lines.append(
                f"    - {hit.get('title', 'Untitled')} | {hit.get('source_name', 'Unknown')}"
            )


def compose_digest(
    top_events: List[Dict],
    overlays: Dict[str, List[Dict]],
    analysis_meta: Optional[Dict] = None,
    market_regime: Optional[Dict] = None,
) -> str:
    provider = (analysis_meta or {}).get("provider", "rule")
    model = (analysis_meta or {}).get("model", "rule-engine")
    attempted_provider = (analysis_meta or {}).get("attempted_provider", "none")
    failures = int((analysis_meta or {}).get("failures", 0) or 0)
    engine_line = f"> 🤖 分析引擎: `{provider}/{model}` | 策略: 前5条详细 + 后5条简版"
    if failures > 0:
        engine_line = (
            f"{engine_line} | ⚠️ LLM失败 {failures} 条 (尝试: {attempted_provider})，已回退规则解释"
        )
    lines = [
        "# 📡 TradePulse 每小时快报",
        "",
        engine_line,
        "",
        "## A. 本小时关键事件 Top10（含中文解读）",
    ]

    if not top_events:
        lines.append("- ⏳ 本小时无新增关键事件（已做增量去重）")
    else:
        for index, event in enumerate(top_events, start=1):
            # Keep display policy stable even when LLM is disabled/fallback:
            # top 5 are rendered as detailed, remaining as brief.
            level = str(event.get("analysis_level", ""))
            if level not in {"detailed", "brief"}:
                level = "detailed" if index <= 5 else "brief"
            level_text = "详细" if level == "detailed" else "简版"
            summary = event.get("summary_zh") or event.get("title", "暂无")
            lines.append(f"{index}. 📰 {event.get('title', 'Untitled')}（{level_text}）")
            lines.append(f"   - 🧠 中文摘要: {summary}")
            lines.append(f"   - 📈 市场方向: {_map_direction(event.get('direction', 'neutral'))}")
            lines.append(f"   - 🎯 相关标的: {_format_tickers(event.get('affected_tickers', []))}")
            lines.append(f"   - 🔍 影响说明: {event.get('impact_reason_zh', '暂无')}")
            if event.get("search_context"):
                lines.append(f"   - 🔎 外部检索补充: {event.get('search_context')}")
            if level == "detailed":
                lines.append(
                    f"   - 👶 小白解读: {event.get('beginner_note_zh', '可先关注是否影响行业龙头和市场风险偏好')}"
                )

            for source in event.get("sources", []):
                lines.append(f"   - 🔗 来源: {source.get('name', 'Unknown')} {source.get('url', '')}")

    lines.append("")
    lines.append("## B. 专题命中（你关注的附加主题）")
    lines.append("- ℹ️ 说明: 专题命中不会改变主线Top10排序，只做额外提醒。")
    lines.append(f"- 🏷️ 股票专题: {_format_overlay_topic_list(overlays.get('stocks', []))}")
    lines.append(f"- 🧷 关键词专题: {_format_overlay_topic_list(overlays.get('keywords', []))}")
    lines.append(f"- 🌍 地缘专题: {_format_overlay_topic_list(overlays.get('geopolitics', []))}")
    _append_overlay_details(lines, "股票", overlays.get("stocks", []))
    _append_overlay_details(lines, "关键词", overlays.get("keywords", []))
    _append_overlay_details(lines, "地缘", overlays.get("geopolitics", []))

    if market_regime:
        lines.append("")
        lines.append("## C. Section 4 板块轮动与资金流")
        lines.append("- ℹ️ 指标说明: 4W/12W 表示近4周/12周相对SPY+QQQ的强弱，综合分越高说明资金偏好越强。")
        lines.append("- ℹ️ 资金流代理说明: 美股部分为 `成交额 × 当日涨跌幅` 的代理指标，用于观察资金偏好，不等同于逐笔真实净流入。")

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

            if leaders:
                lines.append("### 美股轮动候选观察清单（非投资建议）")
                lines.append("- 先看前3强板块，再从对应代表股里找“周线基座 + 日线收紧”的形态。")
                for item in leaders[:3]:
                    rep = US_SECTOR_REP_STOCKS.get(item.get("symbol", ""), "代表股待补充")
                    lines.append(f"- {item.get('symbol', '')} 候选关注: {rep}")
                lines.append("- 入场前自检: 日线波动收敛、站上9/21或50EMA、止损位清晰（风险收益至少1:3）。")

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

            flow_proxy = us.get("flow_proxy", {})
            lines.append("### 美股板块当日资金流代理")
            inflow = flow_proxy.get("inflow", [])
            outflow = flow_proxy.get("outflow", [])
            if inflow:
                lines.append("- 板块资金流入代理前列:")
                for item in inflow:
                    lines.append(
                        "  - {symbol} ({name}) 代理流入 {flow} | 涨跌幅 {pct:+.2f}% | 成交额 ${dv}".format(
                            symbol=item.get("symbol", ""),
                            name=item.get("name", ""),
                            flow=_format_usd_million(float(item.get("flow_proxy", 0.0))),
                            pct=float(item.get("change_pct", 0.0)),
                            dv=_format_usd_billion(float(item.get("dollar_volume", 0.0))),
                        )
                    )
            else:
                lines.append("- 板块资金流入代理前列: 无")

            if outflow:
                lines.append("- 板块资金流出代理前列:")
                for item in outflow:
                    lines.append(
                        "  - {symbol} ({name}) 代理流出 {flow} | 涨跌幅 {pct:+.2f}% | 成交额 ${dv}".format(
                            symbol=item.get("symbol", ""),
                            name=item.get("name", ""),
                            flow=_format_usd_million(float(item.get("flow_proxy", 0.0))),
                            pct=float(item.get("change_pct", 0.0)),
                            dv=_format_usd_billion(float(item.get("dollar_volume", 0.0))),
                        )
                    )
            else:
                lines.append("- 板块资金流出代理前列: 无")

            stock_flow = us.get("stock_flow", {})
            lines.append("### 美股个股资金流入代理（关注池）")
            stock_inflow = stock_flow.get("inflow", [])
            if stock_inflow:
                for item in stock_inflow:
                    lines.append(
                        "  - {symbol} 代理流入 {flow} | 涨跌幅 {pct:+.2f}% | 成交额 ${dv} | 活跃度 {ar:.2f}x".format(
                            symbol=item.get("symbol", ""),
                            flow=_format_usd_million(float(item.get("flow_proxy", 0.0))),
                            pct=float(item.get("change_pct", 0.0)),
                            dv=_format_usd_billion(float(item.get("dollar_volume", 0.0))),
                            ar=float(item.get("activity_ratio", 0.0)),
                        )
                    )
            else:
                lines.append("- 暂无可用个股资金流代理数据")
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

        sec = market_regime.get("sec", {})
        lines.append("### 机构13F与内部人Form4（披露追踪）")
        lines.append("- ℹ️ 披露说明: 13F与Form4来自SEC公开申报，属于披露数据，不是实时交易流水。")
        if sec.get("status") == "ok":
            institutions = sec.get("institutions_13f", [])
            insiders = sec.get("insiders_form4", [])

            if institutions:
                lines.append("- 机构13F最新披露:")
                for item in institutions[:5]:
                    lines.append(
                        "  - {institution} {form} | {date} | {url}".format(
                            institution=item.get("institution", ""),
                            form=item.get("form", ""),
                            date=item.get("filing_date", ""),
                            url=item.get("url", ""),
                        )
                    )
            else:
                lines.append("- 机构13F最新披露: 无")

            if insiders:
                lines.append("- 内部人Form4最新披露:")
                for item in insiders[:5]:
                    lines.append(
                        "  - {symbol} ({issuer}) {form} | {date} | {url}".format(
                            symbol=item.get("symbol", ""),
                            issuer=item.get("issuer", ""),
                            form=item.get("form", ""),
                            date=item.get("filing_date", ""),
                            url=item.get("url", ""),
                        )
                    )
            else:
                lines.append("- 内部人Form4最新披露: 无")
        else:
            lines.append(f"- {sec.get('message', 'SEC披露数据暂不可用')}")

    return "\n".join(lines)
