# Incremental Digest + Overlay + Telegram Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 让 TradePulse 实现真正增量推送，修复专题匹配与 Telegram 无输出问题，并增强 Section C 候选观察清单。

**Architecture:** 在 `run_once` 中把“候选事件排序”和“可推送增量筛选”分离；overlay 从字符串列表升级为结构化命中结果；通知通道增加自动探测；`compose` 增加无新增提示与 C 区候选观察模板。

**Tech Stack:** Python 3.11, dataclasses, sqlite ledger, pytest, GitHub Actions

---

### Task 1: 增量与排序规则测试先行

**Files:**
- Modify: `tests/test_pipeline_run_once.py`
- Modify: `src/tradepulse/pipeline/run_once.py`

**Step 1: Write the failing test**
- 新增测试：第一次 run 推送 1 条事件；第二次 run 同事件应显示“无新增关键事件”，且 `new_events == 0`。
- 新增测试：当单一来源占多数时，A 区应受 `max_per_source` 限制。

**Step 2: Run test to verify it fails**
Run: `python3 -m pytest tests/test_pipeline_run_once.py -q`
Expected: FAIL（当前实现会重复输出）

**Step 3: Write minimal implementation**
- 在 `run_once` 中先生成候选事件，再用 ledger 过滤新增事件并用于 A 区展示。
- 增加 `digest.max_age_hours` 和 `digest.max_per_source` 配置并用于排序/截断。

**Step 4: Run test to verify it passes**
Run: `python3 -m pytest tests/test_pipeline_run_once.py -q`
Expected: PASS

**Step 5: Commit**
```bash
git add tests/test_pipeline_run_once.py src/tradepulse/pipeline/run_once.py src/tradepulse/config.py
git commit -m "fix: make digest incremental and reduce stale single-source dominance"
```

### Task 2: Overlay 引擎精确匹配 + 命中详情

**Files:**
- Modify: `src/tradepulse/overlays.py`
- Modify: `tests/test_overlays.py`
- Modify: `src/tradepulse/compose.py`

**Step 1: Write the failing test**
- 测试 `MU` 不应命中 `community`。
- 测试 `us-china-tech` 不应仅因 `us` 命中。
- 测试命中返回条目详情（标题/来源）并在 B 区渲染。

**Step 2: Run test to verify it fails**
Run: `python3 -m pytest tests/test_overlays.py tests/test_compose.py -q`
Expected: FAIL

**Step 3: Write minimal implementation**
- 用正则边界匹配股票代码。
- 地缘 token 至少命中2个（或全部可用 token）。
- `match_overlays` 输入改为事件列表并输出结构化命中详情。

**Step 4: Run test to verify it passes**
Run: `python3 -m pytest tests/test_overlays.py tests/test_compose.py -q`
Expected: PASS

**Step 5: Commit**
```bash
git add src/tradepulse/overlays.py src/tradepulse/compose.py tests/test_overlays.py tests/test_compose.py
git commit -m "fix: improve overlay precision and show matched items"
```

### Task 3: Telegram 自动通道启用

**Files:**
- Modify: `src/tradepulse/pipeline/run_once.py`
- Modify: `tests/test_pipeline_run_once.py`
- Modify: `tests/test_notifiers.py`

**Step 1: Write the failing test**
- 当 `TRADEPULSE_CHANNELS` 为空且 Telegram token/chat_id 存在时，应自动启用 telegram sender。

**Step 2: Run test to verify it fails**
Run: `python3 -m pytest tests/test_pipeline_run_once.py tests/test_notifiers.py -q`
Expected: FAIL

**Step 3: Write minimal implementation**
- 增加 `resolve_channels`：显式 channels 优先；否则按密钥自动启用。
- 将 `_collect_senders` 改为基于 resolved channels。

**Step 4: Run test to verify it passes**
Run: `python3 -m pytest tests/test_pipeline_run_once.py tests/test_notifiers.py -q`
Expected: PASS

**Step 5: Commit**
```bash
git add src/tradepulse/pipeline/run_once.py tests/test_pipeline_run_once.py tests/test_notifiers.py
git commit -m "fix: auto-enable telegram when credentials exist"
```

### Task 4: Section C 增加候选观察清单

**Files:**
- Modify: `src/tradepulse/compose.py`
- Modify: `tests/test_compose.py`

**Step 1: Write the failing test**
- 当有美股领先板块时，C 区应输出“候选观察清单（非投资建议）”与代表股。

**Step 2: Run test to verify it fails**
Run: `python3 -m pytest tests/test_compose.py -q`
Expected: FAIL

**Step 3: Write minimal implementation**
- 在 C 区渲染观察清单和三步法（周线基座/日线收紧/风控）。

**Step 4: Run test to verify it passes**
Run: `python3 -m pytest tests/test_compose.py -q`
Expected: PASS

**Step 5: Commit**
```bash
git add src/tradepulse/compose.py tests/test_compose.py
git commit -m "feat: add sector-rotation watchlist ideas section"
```

### Task 5: OpenSpec + 文档 + 验证

**Files:**
- Create: `openspec/changes/tradepulse-incremental-overlay-telegram/*`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `config/user.example.yaml`

**Step 1: Update OpenSpec change docs**
- proposal/design/tasks/specs 补齐本次行为变化。

**Step 2: Update README and examples**
- 写清 `max_age_hours`, `max_per_source`, 频道自动探测规则，overlay 命中逻辑。

**Step 3: Run full verification**
Run: `python3 -m pytest -q`
Expected: PASS
Run: `openspec validate tradepulse-incremental-overlay-telegram --type change`
Expected: PASS

**Step 4: Commit**
```bash
git add openspec README.md README.zh-CN.md config/user.example.yaml docs/plans
git commit -m "docs: document incremental digest and channel auto-detection"
```
