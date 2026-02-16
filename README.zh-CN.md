# TradePulse（中文说明）

TradePulse 是一个面向股票交易者的 AI 新闻聚合与分析工具，采用“重要性优先”策略。
它可以在 GitHub Actions 上按小时运行，输出中文快报，并为每条事件附带来源链接。

## 解决的问题

- 聚合交易相关的高信号新闻/RSS
- 按重要性排序输出 TopN
- 支持专题命中（股票/关键词/地缘）作为附加视图，不干扰主排序
- 支持 Section 4 市场结构（美股板块轮动 + A股资金流）
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
4. 规则打分（重要性 + 方向 + 股票识别）
5. 生成市场结构快照：
   - 美股：11 个 SPDR 行业 ETF 的 `4W/12W` 相对强弱（对比 `SPY + QQQ`）
   - A股：行业资金净流入/净流出排名
6. 生成快报（TopN + 专题层 + Section 4）
7. SQLite 记录已推送事件，实现增量推送
8. 按渠道发送消息

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

说明：

- 若希望推送消息，至少应配置一个渠道所需的 Secret。
- 若同时配置 `BAILIAN_API_KEY` 与 `GEMINI_API_KEY`，系统优先使用百炼。

### 2）Variables（非敏感配置）

| 名称 | 是否必填 | 用途 | 示例 |
|---|---|---|---|
| `TRADEPULSE_CONFIG_PATH` | 可选 | 自定义配置文件路径（相对仓库或绝对路径） | `config/user.yaml` |
| `TRADEPULSE_TOP_N` | 可选 | 主摘要 TopN（1-50） | `10` |
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
| `TRADEPULSE_MARKET_A_SHARE_TOP_N` | 可选 | A股净流入/净流出显示行数 | `5` |
| `TRADEPULSE_MARKET_TIMEOUT_SEC` | 可选 | 市场数据请求超时（1-30秒） | `8` |

列表类变量支持逗号或换行分隔。

### 3）渠道配置要点

- 钉钉：
  - 在群里新增自定义机器人，复制 webhook 到 `DINGTALK_WEBHOOK_URL`。
- Telegram：
  - 通过 BotFather 创建机器人并拿到 `TELEGRAM_BOT_TOKEN`。
  - 把机器人拉入目标群/频道。
  - 通过 Bot API 获取 `chat_id`，配置到 `TELEGRAM_CHAT_ID`。
- 飞书：
  - 创建自定义机器人，复制 webhook 到 `FEISHU_WEBHOOK_URL`。

## 信息源层级

- `core`：高信号核心源
- `extended`：`core` + 更广覆盖
- `experimental`：`extended` + 长尾实验源

你可以用 `sources.min_health_score`（或 `TRADEPULSE_MIN_HEALTH_SCORE`）过滤低健康度源。

## 输出结构

1. A. 本小时关键事件 TopN
2. B. 专题命中（股票 / 关键词 / 地缘）
3. C. Section 4 板块轮动与资金流（美股/A股）
4. 每条事件都包含方向、影响标的、影响说明、来源

## Section 4 数据来源

- 美股 ETF 历史数据：Stooq 日线 CSV（`stooq.com`）
- A股行业资金流：东方财富 push2 行业排行接口（`push2.eastmoney.com`）

## 运行命令

```bash
# 本地干跑（不推送）
.venv/bin/python -m tradepulse.cli run --dry-run

# 真实推送
.venv/bin/python -m tradepulse.cli run
```

## 免责声明

TradePulse 仅用于研究与工作流自动化，不构成投资建议。
