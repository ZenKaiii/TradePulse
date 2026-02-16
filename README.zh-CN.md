# TradePulse（中文说明）

TradePulse 是一个面向美股交易者的 AI 新闻聚合与分析工具，采用“重要性优先”策略，每小时产出中文快报，并附带来源链接。

## 核心特性

- 每小时输出 `Top10` 关键事件（按重要性排序）
- 专题层追加展示（不影响主线排序）：
  - 股票专题
  - 关键词专题
  - 地缘专题
- 每条事件包含：
  - `利好 / 利空 / 中性`
  - 关联股票（代码 + 公司名）
  - 简短影响说明
  - 来源名称 + 原文链接
- LLM 自动路由：
  - 百炼优先
  - Gemini 备份
- 多渠道推送：
  - 钉钉
  - Telegram
  - 飞书

## 快速开始

1. 复制配置文件：
```bash
cp config/user.example.yaml config/user.yaml
```

2. 修改你的关注项：
- `watchlists.stocks`
- `watchlists.keywords`
- `watchlists.geopolitics`
- `digest.top_n`（默认 10）

3. 本地干跑：
```bash
.venv/bin/python -m tradepulse.cli run --dry-run
```

## 必要/可选 Secrets

LLM：
- `BAILIAN_API_KEY`（主）
- `GEMINI_API_KEY`（备）

推送渠道：
- `DINGTALK_WEBHOOK_URL`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `FEISHU_WEBHOOK_URL`

## 信息源分层

- `core`：默认高信号源
- `extended`：`core` + 更广覆盖
- `experimental`：`extended` + 实验源

你可通过 `sources.tier` 控制抓取层级，并用 `sources.min_health_score` 过滤低健康度源。

## 定时任务

工作流文件：
- `.github/workflows/hourly.yml`

计划：
- 每小时运行一次（`0 * * * *`）
- 支持手动触发（`workflow_dispatch`）
