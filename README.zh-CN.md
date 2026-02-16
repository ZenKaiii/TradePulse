# TradePulse（中文说明）

TradePulse 是一个面向股票交易者的 AI 新闻聚合与分析工具，采用“重要性优先”策略。
它可以在 GitHub Actions 上按小时运行，输出中文快报，并为每条事件附带来源链接。

## 解决的问题

- 聚合交易相关的高信号新闻/RSS
- 按重要性排序输出 TopN
- 支持专题命中（股票/关键词/地缘）作为附加视图，不干扰主排序
- 支持 Section 4 市场结构（美股板块轮动 + 美股资金流代理 + A股资金流 + SEC披露）
- 每条事件都给出：
  - `利好 / 利空 / 中性`
  - 影响股票代码和公司名
  - 中文影响说明
  - 来源名称 + 原文链接
- 增量推送（只推送新事件簇）到：
  - 钉钉
  - Telegram
  - 飞书

## 架构（MVP）

1. 按 profile + tier 拉取 RSS 源
2. 计算信息源健康度并过滤低质量源
3. 对重复报道进行聚类
4. 规则打分（重要性 + 初始方向/股票识别）
5. LLM 增强解读：
   - 前5条详细中文分析
   - 后5条简版中文分析
   - 百炼优先，Gemini 备援
6. 事件筛选约束：
   - A区仅显示增量未推送事件（不重复）
   - 新鲜度过滤（`max_age_hours`）
   - 单来源上限（`max_per_source`）
7. 生成市场结构快照：
   - 美股：11 个 SPDR 行业 ETF 的 `4W/12W` 相对强弱（对比 `SPY + QQQ`）
   - 美股：板块/个股当日资金流代理（`成交额 × 当日涨跌幅`）
   - 美股：机构13F + 内部人Form4 披露追踪
   - A股：行业资金净流入/净流出排名
8. 可选搜索增强：
   - Tavily 对详细事件做外部信息补充（默认关闭）
9. 生成快报（TopN + 专题层 + Section 4）
10. SQLite 记录已推送事件，实现增量推送
11. 按渠道发送消息（显式 channels 优先，否则按密钥自动识别）

## 快速开始

```bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e .
cp config/user.example.yaml config/user.yaml
.venv/bin/python -m tradepulse.cli run --dry-run
```

## 配置优先级

运行时配置读取顺序（高到低）：

1. GitHub Actions 环境变量（`TRADEPULSE_*`）
2. `config/user.yaml`
3. `config/user.example.yaml` 默认值

这意味着你可以把不敏感配置放到 GitHub Variables，用于覆盖仓库里的默认配置。

## GitHub Actions 配置说明

工作流文件：

- `.github/workflows/hourly.yml`

默认计划：

- 每小时一次（`0 * * * *`）

### 1）Secrets（敏感信息）

| 名称 | 是否必填 | 用途 | 示例 |
|---|---|---|---|
| `BAILIAN_API_KEY` | 推荐 | 阿里云百炼，主 LLM | `sk-***` |
| `GEMINI_API_KEY` | 可选 | Gemini，备用 LLM | `AIza***` |
| `DINGTALK_WEBHOOK_URL` | 可选 | 钉钉机器人 webhook | `https://oapi.dingtalk.com/robot/send?access_token=***` |
| `TELEGRAM_BOT_TOKEN` | 可选 | Telegram Bot Token | `123456:ABC-DEF...` |
| `TELEGRAM_CHAT_ID` | 可选 | Telegram 目标会话 ID | `-1001234567890` |
| `FEISHU_WEBHOOK_URL` | 可选 | 飞书机器人 webhook | `https://open.feishu.cn/open-apis/bot/v2/hook/***` |
| `TAVILY_API_KEY` | 可选 | Tavily 搜索增强 key（可选） | `tvly-***` |

说明：

- 若希望推送消息，至少应配置一个渠道所需的 Secret。
- 若同时配置 `BAILIAN_API_KEY` 与 `GEMINI_API_KEY`，系统优先使用百炼。

### 2）Variables（非敏感配置）

| 名称 | 是否必填 | 用途 | 示例 |
|---|---|---|---|
| `TRADEPULSE_CONFIG_PATH` | 可选 | 自定义配置文件路径（相对仓库或绝对路径） | `config/user.yaml` |
| `TRADEPULSE_TOP_N` | 可选 | 主摘要 TopN（1-50） | `10` |
| `TRADEPULSE_MAX_AGE_HOURS` | 可选 | 新闻新鲜度窗口（小时） | `72` |
| `TRADEPULSE_MAX_PER_SOURCE` | 可选 | A区同一来源最多条数 | `3` |
| `TRADEPULSE_SOURCE_PROFILE` | 可选 | 信息源 profile | `trader` |
| `TRADEPULSE_SOURCE_TIER` | 可选 | 信息源层级（`core/extended/experimental`） | `core` |
| `TRADEPULSE_MIN_HEALTH_SCORE` | 可选 | 信息源健康度阈值（0-100） | `30` |
| `TRADEPULSE_STOCKS` | 可选 | 股票专题列表（逗号分隔） | `NVDA,AAPL,MSFT` |
| `TRADEPULSE_KEYWORDS` | 可选 | 关键词专题（逗号分隔） | `fed rate cut,treasury yield` |
| `TRADEPULSE_GEOPOLITICS` | 可选 | 地缘专题（逗号分隔） | `middle-east,us-china-tech` |
| `TRADEPULSE_CHANNELS` | 可选 | 启用渠道（逗号分隔） | `dingtalk,telegram` |
| `TRADEPULSE_MARKET_ENABLED` | 可选 | 是否启用 Section 4 | `true` |
| `TRADEPULSE_MARKET_US_ENABLED` | 可选 | 是否启用美股板块轮动 | `true` |
| `TRADEPULSE_MARKET_A_SHARE_ENABLED` | 可选 | 是否启用 A股资金流排名 | `true` |
| `TRADEPULSE_MARKET_US_TOP_N` | 可选 | 美股领先/落后板块显示行数 | `3` |
| `TRADEPULSE_MARKET_US_STOCK_FLOW_TOP_N` | 可选 | 美股个股资金流代理条数 | `5` |
| `TRADEPULSE_MARKET_A_SHARE_TOP_N` | 可选 | A股净流入/净流出显示行数 | `5` |
| `TRADEPULSE_MARKET_TIMEOUT_SEC` | 可选 | 市场数据请求超时（1-30秒） | `8` |
| `TRADEPULSE_MARKET_SEC_ENABLED` | 可选 | 是否启用 SEC 披露追踪 | `true` |
| `TRADEPULSE_MARKET_SEC_13F_CIKS` | 可选 | 机构13F CIK 列表（逗号分隔） | `0001067983,0001350694` |
| `TRADEPULSE_SEC_USER_AGENT` | 可选 | SEC API 的 User-Agent（带联系方式） | `TradePulse/0.1 (contact: you@example.com)` |
| `TRADEPULSE_LLM_ENABLED` | 可选 | 是否启用 LLM 解读 | `true` |
| `TRADEPULSE_LLM_PROVIDER` | 可选 | `auto/bailian/gemini` | `auto` |
| `TRADEPULSE_LLM_DETAIL_TOP_N` | 可选 | 详细解读条数 | `5` |
| `TRADEPULSE_LLM_TIMEOUT_SEC` | 可选 | LLM 请求超时 | `20` |
| `TRADEPULSE_LLM_TEMPERATURE` | 可选 | LLM 温度参数 | `0.2` |
| `TRADEPULSE_BAILIAN_MODEL` | 可选 | 百炼模型名 | `qwen3.5-plus` |
| `TRADEPULSE_BAILIAN_BASE_URL` | 可选 | 百炼兼容模式地址 | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `TRADEPULSE_GEMINI_MODEL` | 可选 | Gemini 模型名 | `gemini-3-pro-preview` |
| `TRADEPULSE_GEMINI_BASE_URL` | 可选 | Gemini API 地址 | `https://generativelanguage.googleapis.com/v1beta` |
| `TRADEPULSE_SEARCH_ENABLED` | 可选 | 是否启用搜索增强 | `false` |
| `TRADEPULSE_SEARCH_PROVIDER` | 可选 | 搜索提供方（`tavily`） | `tavily` |
| `TRADEPULSE_SEARCH_TOP_N` | 可选 | 搜索增强事件条数 | `3` |
| `TRADEPULSE_SEARCH_MAX_RESULTS` | 可选 | 每条事件搜索返回条数 | `3` |
| `TRADEPULSE_SEARCH_TIMEOUT_SEC` | 可选 | 搜索请求超时秒数 | `12` |

列表类变量支持逗号或换行分隔。

若 `TRADEPULSE_CHANNELS` 为空，系统会按密钥自动识别渠道：
- 配置了 `DINGTALK_WEBHOOK_URL` -> 自动启用 `dingtalk`
- 同时配置 `TELEGRAM_BOT_TOKEN` 和 `TELEGRAM_CHAT_ID` -> 自动启用 `telegram`
- 配置了 `FEISHU_WEBHOOK_URL` -> 自动启用 `feishu`

### 3）渠道配置要点

- 钉钉：
  - 在群里新增自定义机器人，复制 webhook 到 `DINGTALK_WEBHOOK_URL`。
  - TradePulse 会发送 `msgtype=markdown`，标题/列表会按富文本样式渲染。
- Telegram：
  - 通过 BotFather 创建机器人并拿到 `TELEGRAM_BOT_TOKEN`。
  - 把机器人拉入目标群/频道。
  - 通过 Bot API 获取 `chat_id`，配置到 `TELEGRAM_CHAT_ID`。
  - 超长快报会自动拆分为多条 Telegram 消息，避免因长度限制导致发送失败。
  - 优先按 Markdown 模式发送；若解析失败会自动回退纯文本，保证可达。
- 飞书：
  - 创建自定义机器人，复制 webhook 到 `FEISHU_WEBHOOK_URL`。

## 信息源层级

- `core`：高信号核心源
- `extended`：`core` + 更广覆盖（包含 Google News 商业/市场 RSS）
- `experimental`：`extended` + 长尾实验源

你可以用 `sources.min_health_score`（或 `TRADEPULSE_MIN_HEALTH_SCORE`）过滤低健康度源。

## 输出结构

1. A. 本小时关键事件 TopN（前5条详细 + 后5条简版，中文AI解读）
2. B. 专题命中（股票 / 关键词 / 地缘）
3. C. Section 4 板块轮动与资金流（美股/A股 + SEC披露）
4. 每条事件都包含方向、影响标的、影响说明、来源
5. 若本轮无新增事件，A区会明确显示“本小时无新增关键事件”

## LLM 数据源

- 百炼兼容模式：`https://dashscope.aliyuncs.com/compatible-mode/v1`
- Gemini API：`https://generativelanguage.googleapis.com/v1beta`

## Section 4 数据来源

- 美股 ETF 历史数据：Stooq 日线 CSV（`stooq.com`）
- A股行业资金流：东方财富 push2 行业排行接口（`push2.eastmoney.com`）
- SEC 披露：`data.sec.gov/submissions`（13F / Form4）
- 可选搜索增强：Tavily Search API（`api.tavily.com`）

## 运行命令

```bash
# 本地干跑（不推送）
.venv/bin/python -m tradepulse.cli run --dry-run

# 真实推送
.venv/bin/python -m tradepulse.cli run
```

## GitHub Actions 的增量状态

工作流 `.github/workflows/hourly.yml` 会通过 Actions cache 恢复/保存 `data/state.db`，保证跨小时运行也能做增量去重。

## 免责声明

TradePulse 仅用于研究与工作流自动化，不构成投资建议。
