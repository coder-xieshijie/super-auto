# 冒烟集 @ d465f843d8

- 代码：worktree `gv2-verify-tools`，detached HEAD `d465f843d8`，工作区无改动；三个实例的 `git-head` 均为 d465f843d8d0ad33ec2726e08ddafc210a112b46、`git-status` 为空，证据文件 `dirty=false`。
- 构建：`prepare runtime tui electron` 通过（pi vendor、oauth-core、local-runtime-v2 and deps 10s、tui 19s、electron build:zh-staging 60s），见 `_logs/prepare.log`。
- 环境：三个入口均 `--config ~/.minimax/verify-goal-v2/config.yaml`（staging，cn/staging），TUI、Electron `--no-proxy`。
- 执行：`RG1_ROOT=evidence/m1-smoke-d465 RG1_TAG=m1s465 bash tools/m1-smoke.sh`，按 Electron → 接口 → TUI 串行，2026-10-01 10:37–10:39；判定 `python3 tools/m1-smoke-analyze.py evidence/m1-smoke-d465 --tag m1s465` → `summary.json`。

## 结果：5/5 通过

| # | 冒烟项 | 入口 | runId | 结果 | 观测 |
| --- | --- | --- | --- | --- | --- |
| 1 | PONG | 接口 | 20261001-103755-1b560e | 通过 | 助手消息 `PONG`；send 15 帧，无 `messages-rewound` |
| 2 | lifecycle 创建并跑到终态 | 接口 | 20261001-103755-1b560e | 通过 | active → paused(user_requested) → 改目标仍 paused → hold 8s 仍 paused → active → complete(verifier_met)；`count.txt` = 1..4 |
| 3 | lifecycle 创建、跑到完成 | Electron | 20261001-103707-aa70a3 | 通过 | 横幅 进行中 → 已完成；`goal-completion-marker` “目标已完成 用时 13s”；接口 complete(verifier_met)；`count.txt` = 1..3 |
| 4 | `/goal` 创建 → Active；`/goal pause` → Paused | TUI | 20261001-103854-0f3a89 | 通过 | `◎ Goal · Active`、`◎ Goal · Paused` |
| 5 | 普通消息 PONG | TUI | 20261001-103854-0f3a89 | 通过 | 屏幕 `● PONG`；`tui-results.jsonl` 该轮 `succeeded`、answer `PONG` |

服务：三个实例 `up` 成功，接口 `doctor` 通过，全部已 `down`。auth-check：三个实例 `contentSafety401=0`、`electronAuthLost=0`。

## 说明
- 接口、TUI 直接执行 `tools/smoke-api.sh`、`tools/smoke-tui.sh`。Electron 使用与 `smoke-electron.sh` 相同的命令，授权模式改用 `rg1-electron.sh` 的 `set_permission 始终授权`（`--config` 下默认已是始终授权，未点击），每步记入 `steps.jsonl`。
- TUI `tui-results.jsonl` 第一行 `cancelled` 是 `/goal pause` 取消的 Goal 轮次。

## 证据
- `_runs/runtime-smoke-api/`、`_runs/electron-smoke-electron/`（含截图）、`_runs/tui-smoke-tui/`：每个实例都有 `git-head`、`git-status`、`auth-check.json`、`steps.jsonl`、snapshot。
- `summary.json`：逐项检查与实际值。
