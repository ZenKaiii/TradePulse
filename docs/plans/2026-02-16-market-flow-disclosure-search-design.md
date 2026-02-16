# TradePulse 市场资金流 + 披露追踪 + Tavily 增强设计

## 目标
- 默认 LLM 模型更新：百炼 `qwen3.5-plus`，Gemini `gemini-3-pro-preview`。
- Telegram 输出支持 Markdown 样式（并保证失败可回退）。
- Section 4 增加美股板块与个股资金流代理指标。
- 增加机构 13F 与内部人 Form4 追踪。
- Tavily 作为可选增强搜索（默认关闭），用于 Top 事件外部补充。
- 扩展 Google News RSS 作为补充信息源。

## 约束与事实
- Gemini REST 官方基址仍为 `https://generativelanguage.googleapis.com/v1beta`。
- SEC `data.sec.gov` 可免费访问，但必须带 `User-Agent`，且需限频。
- 13F 具有披露时延，Form4 也非逐笔实时，需在文案中提示“披露数据”。

## 方案选择
### 方案1：只修模型和Telegram
- 改动小，但无法满足 Section 4 资金流与机构追踪诉求。

### 方案2：完整实现（采用）
- 统一在 market/regime 与 compose 扩展 Section 4。
- SEC 披露与资金流代理同一节输出，增强交易决策上下文。
- Tavily 单独模块，按开关启用，失败不影响主流程。

### 方案3：引入更多搜索引擎聚合
- 成本和复杂度高，先不做主链路。

## 架构设计
1. **配置层**
- 新增 `SearchEnhanceConfig`：`enabled/provider/top_n/max_results/timeout_sec`。
- `MarketRegimeConfig` 增加 `us_stock_flow_top_n`。
- `LLMConfig` 默认模型更新。

2. **市场资金流代理**
- 基于 Stooq 日线 OHLCV。
- 指标：
  - `change_pct = (close_t / close_t-1 - 1) * 100`
  - `dollar_volume = close_t * volume_t`
  - `flow_proxy = dollar_volume * (change_pct / 100)`
- 输出：
  - 板块 ETF 当日资金流代理 Top/Bottom
  - 个股资金涌入代理 TopN（优先用户自选）

3. **机构/内部人追踪**
- 机构：默认追踪 13F CIK 列表。
- 内部人：根据 `watchlists.stocks` 映射 CIK，抓最近 Form4。
- 输出最近申报记录（日期、表单、链接），并标注“披露数据，非实时”。

4. **Tavily 增强**
- 仅对前 N 条详细事件调用 Tavily Search。
- 结果写入 `search_context` 字段，compose 中追加“外部搜索补充”。
- 调用失败不阻断主链路。

5. **Telegram Markdown**
- 增加 `parse_mode=Markdown`。
- 将标题行转换为粗体 Markdown。
- 若 API 报 parse 错误则回退纯文本。

6. **Google News RSS**
- 在 `extended` 源新增 Google News Business/Market 搜索 RSS。

## 风险与缓解
- SEC 限流：加 User-Agent、少量 CIK、失败降级。
- 资金流口径争议：文案明确“代理指标”。
- Tavily 成本：默认关闭+TopN 限制。
- Telegram markdown 解析失败：自动回退纯文本。
