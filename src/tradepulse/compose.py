from typing import Dict, List, Optional


def _has_chinese(text: str) -> bool:
    return any('\u4e00' <= c <= '\u9fff' for c in str(text or ""))


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

# 美股公司业务信息映射
US_STOCK_INFO = {
    "AAPL": {"name": "苹果公司", "sector": "科技", "desc": "全球领先的消费电子和软件服务公司"},
    "MSFT": {"name": "微软公司", "sector": "科技", "desc": "全球最大的软件公司，云计算和AI领导者"},
    "GOOGL": {"name": "Alphabet谷歌", "sector": "科技", "desc": "全球最大的搜索引擎和广告平台"},
    "GOOG": {"name": "Alphabet谷歌", "sector": "科技", "desc": "全球最大的搜索引擎和广告平台"},
    "AMZN": {"name": "亚马逊", "sector": "消费", "desc": "全球最大的电商和云计算平台"},
    "NVDA": {"name": "英伟达", "sector": "科技", "desc": "全球领先的GPU和AI芯片供应商"},
    "META": {"name": "Meta Platforms", "sector": "通信", "desc": "全球最大的社交网络平台"},
    "TSLA": {"name": "特斯拉", "sector": "消费", "desc": "全球领先的电动汽车和能源公司"},
    "BRK.B": {"name": "伯克希尔哈撒韦", "sector": "金融", "desc": "全球最大的多元化控股公司"},
    "JPM": {"name": "摩根大通", "sector": "金融", "desc": "全球最大的商业银行之一"},
    "V": {"name": "Visa", "sector": "金融", "desc": "全球最大的支付网络公司"},
    "JNJ": {"name": "强生公司", "sector": "医疗", "desc": "全球最大的医疗健康公司"},
    "WMT": {"name": "沃尔玛", "sector": "消费", "desc": "全球最大的零售连锁企业"},
    "PG": {"name": "宝洁公司", "sector": "消费", "desc": "全球最大的日用消费品公司"},
    "MA": {"name": "万事达卡", "sector": "金融", "desc": "全球领先的支付网络公司"},
    "UNH": {"name": "联合健康", "sector": "医疗", "desc": "美国最大的健康保险公司"},
    "HD": {"name": "家得宝", "sector": "消费", "desc": "全球最大的家居建材零售商"},
    "DIS": {"name": "迪士尼", "sector": "通信", "desc": "全球领先的娱乐媒体公司"},
    "BAC": {"name": "美国银行", "sector": "金融", "desc": "美国第二大商业银行"},
    "XOM": {"name": "埃克森美孚", "sector": "能源", "desc": "全球最大的石油化工公司之一"},
    "CVX": {"name": "雪佛龙", "sector": "能源", "desc": "全球领先的综合性石油公司"},
    "PFE": {"name": "辉瑞制药", "sector": "医疗", "desc": "全球最大的制药公司之一"},
    "KO": {"name": "可口可乐", "sector": "消费", "desc": "全球最大的饮料公司"},
    "PEP": {"name": "百事可乐", "sector": "消费", "desc": "全球领先的食品饮料公司"},
    "COST": {"name": "开市客", "sector": "消费", "desc": "全球最大的会员制仓储超市"},
    "AVGO": {"name": "博通", "sector": "科技", "desc": "全球领先的半导体和基础设施软件公司"},
    "TMO": {"name": "赛默飞世尔", "sector": "医疗", "desc": "全球领先的科学研究服务公司"},
    "MRK": {"name": "默克制药", "sector": "医疗", "desc": "全球领先的制药公司"},
    "CSCO": {"name": "思科系统", "sector": "科技", "desc": "全球领先的网络设备供应商"},
    "ABBV": {"name": "艾伯维", "sector": "医疗", "desc": "全球领先的生物制药公司"},
    "ACN": {"name": "埃森哲", "sector": "科技", "desc": "全球领先的IT服务咨询公司"},
    "LLY": {"name": "礼来公司", "sector": "医疗", "desc": "全球领先的制药公司，专注糖尿病和减肥药"},
    "MCD": {"name": "麦当劳", "sector": "消费", "desc": "全球最大的快餐连锁企业"},
    "DHR": {"name": "丹纳赫", "sector": "医疗", "desc": "全球领先的生命科学和诊断公司"},
    "ADBE": {"name": "Adobe", "sector": "科技", "desc": "全球领先的创意软件公司"},
    "CRM": {"name": "Salesforce", "sector": "科技", "desc": "全球领先的云CRM平台"},
    "WFC": {"name": "富国银行", "sector": "金融", "desc": "美国第三大商业银行"},
    "NFLX": {"name": "Netflix", "sector": "通信", "desc": "全球领先的流媒体平台"},
    "AMD": {"name": "AMD", "sector": "科技", "desc": "全球领先的处理器制造商"},
    "INTC": {"name": "英特尔", "sector": "科技", "desc": "全球最大的半导体芯片制造商"},
    "QCOM": {"name": "高通", "sector": "科技", "desc": "全球领先的无线通信芯片供应商"},
    "TXN": {"name": "德州仪器", "sector": "科技", "desc": "全球领先的模拟芯片制造商"},
    "NKE": {"name": "耐克", "sector": "消费", "desc": "全球最大的运动鞋服公司"},
    "ORCL": {"name": "甲骨文", "sector": "科技", "desc": "全球领先的数据库软件公司"},
    "IBM": {"name": "IBM", "sector": "科技", "desc": "全球领先的企业IT服务公司"},
    "NOW": {"name": "ServiceNow", "sector": "科技", "desc": "全球领先的企业云服务数字化转型平台"},
    "UBER": {"name": "优步", "sector": "科技", "desc": "全球最大的网约车平台"},
    "LYFT": {"name": "Lyft", "sector": "科技", "desc": "美国第二大网约车平台"},
    "SNAP": {"name": "Snap", "sector": "通信", "desc": "全球领先的社交媒体平台(Snapchat)"},
    "SQ": {"name": "Block", "sector": "金融", "desc": "全球领先的移动支付公司"},
    "COIN": {"name": "Coinbase", "sector": "金融", "desc": "全球最大的加密货币交易所"},
    "HOOD": {"name": "Robinhood", "sector": "金融", "desc": "全球领先的零佣金股票交易平台"},
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


def _get_stock_info(symbol: str) -> Optional[Dict]:
    return US_STOCK_INFO.get(symbol.upper())


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
                context = event.get("search_context", "")
                if not _has_chinese(context):
                    context = f"[外部补充] {context}"
                lines.append(f"   - 🔎 外部检索补充: {context}")
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
            stock_outflow = stock_flow.get("outflow", [])
            if stock_inflow:
                lines.append("- 资金流入:")
                for item in stock_inflow:
                    symbol = item.get("symbol", "")
                    stock_info = _get_stock_info(symbol)
                    info_line = f" | {stock_info['name']}({stock_info['sector']})" if stock_info else ""
                    lines.append(
                        "  - {symbol}{info} 代理流入 {flow} | 涨跌幅 {pct:+.2f}% | 成交额 ${dv} | 活跃度 {ar:.2f}x".format(
                            symbol=symbol,
                            info=info_line,
                            flow=_format_usd_million(float(item.get("flow_proxy", 0.0))),
                            pct=float(item.get("change_pct", 0.0)),
                            dv=_format_usd_billion(float(item.get("dollar_volume", 0.0))),
                            ar=float(item.get("activity_ratio", 0.0)),
                        )
                    )
            if stock_outflow:
                lines.append("- 资金流出:")
                for item in stock_outflow:
                    symbol = item.get("symbol", "")
                    stock_info = _get_stock_info(symbol)
                    info_line = f" | {stock_info['name']}({stock_info['sector']})" if stock_info else ""
                    lines.append(
                        "  - {symbol}{info} 代理流出 {flow} | 涨跌幅 {pct:+.2f}% | 成交额 ${dv} | 活跃度 {ar:.2f}x".format(
                            symbol=symbol,
                            info=info_line,
                            flow=_format_usd_million(float(item.get("flow_proxy", 0.0))),
                            pct=float(item.get("change_pct", 0.0)),
                            dv=_format_usd_billion(float(item.get("dollar_volume", 0.0))),
                            ar=float(item.get("activity_ratio", 0.0)),
                        )
                    )
            if not stock_inflow and not stock_outflow:
                lines.append("- 暂无可用关注池资金流代理数据")

            market_stock_flow = us.get("market_stock_flow", {})
            if market_stock_flow:
                lines.append("### 美股市场资金流入TopN（不限关注池）")
                lines.append("- ℹ️ 说明: 以下为美股市场成交额前列的股票资金流向代理，供参考。")
                market_inflow = market_stock_flow.get("inflow", [])
                if market_inflow:
                    lines.append("- 资金流入前列:")
                    for item in market_inflow[:10]:
                        symbol = item.get("symbol", "")
                        stock_info = _get_stock_info(symbol)
                        info_line = f" | {stock_info['name']}({stock_info['sector']})" if stock_info else ""
                        lines.append(
                            "  - {symbol}{info} 代理流入 {flow} | 涨跌幅 {pct:+.2f}% | 成交额 ${dv}".format(
                                symbol=symbol,
                                info=info_line,
                                flow=_format_usd_million(float(item.get("flow_proxy", 0.0))),
                                pct=float(item.get("change_pct", 0.0)),
                                dv=_format_usd_billion(float(item.get("dollar_volume", 0.0))),
                            )
                        )
                else:
                    lines.append("- 暂无可用市场资金流数据")
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
