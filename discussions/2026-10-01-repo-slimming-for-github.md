---
id: discussion-2026-10-01-repo-slimming-for-github
recorded_on: 2026-10-01
timezone: Asia/Shanghai
source: current-conversation
topics: [仓库体积, GitHub, session 数据, 索引]
---

# 上传 GitHub 前的仓库瘦身估算

## 用户问题（原文）

> 我想要你分析当前项目, 现在本地的 session 数据是不是太多了？我想要把它上传到 GitHub 上。
>
> 我的想法是：
> 1. 只保留过程理论，还有 3 家的理论。
> 2. 本地的 session 数据就做一个索引就行了。因为这些应该在原始的地方都存着，我会把它们上传成 private 仓库，所以不需要一起放到当前的仓库里面。
>
> 如果是这样的话，当前仓库处理后大概会有多大？

## 现状（2026-10-01 实测，提交 `86e2c58` 加未跟踪文件）

- 工作区文件约 2.3 GB，`.git` 约 1.2 GB（pack 1.12 GiB），磁盘合计约 3.5 GB。
- 大头：`research/workflow-30d/raw` 581 MB、`intermediate` 875 MB（三端 session 快照与抽取的 messages.jsonl）；`research/lauren/bookmark-videos/raw` 309 MB（两段 mp4）；`requirements/*/evidence` 约 565 MB（截图、json、日志）。
- 超过 GitHub 单文件 100 MB 上限的文件：`intermediate/codex/messages.jsonl` 491 MB、`intermediate/mcode/messages.jsonl` 331 MB、`lauren_graph_harness.mp4` 192 MB、`lauren_2500prs.mp4` 117 MB。它们都在历史里，直接 push 会被拒。
- 原始位置核对：`~/.claude/settings.json` 的 `cleanupPeriodDays` 为 365，最早 transcript 为 2026-07-18；`~/.codex/sessions` 有 2026/07–09。MCode 数据库原件未核对。

## 助手估算（未经确认）

| 保留部分 | 大小 |
|---|---|
| `process/`、`discussions/`、根文件 | 0.4 MB |
| 研究结论目录（anthropic-long-running、self-verifying-loop、zero-based-delivery、verification-stage、agentlord-gaps、两份 trace） | 1.2 MB |
| `research/agent-delivery-2026-09-28`（三家原文 raw 13 MB，只留文本约 3.5 MB） | 4–15 MB |
| `research/lauren` 去掉视频（字幕、文字稿、X 讨论、站外分析） | 1.9 MB |
| `research/workflow-30d` 的 README、scripts、conclusions | 0.1 MB |
| `requirements/*` 去掉 evidence（plan、决定、查漏记录；其中 .log 2.4 MB） | 1.3–3.8 MB |

合计约 9–22 MB，加索引文件不足 1 MB。用新历史推送时，`.git` 预计约 3–8 MB（按文本压缩比估算，未实测）。

注意事项：

1. 只在工作区删除不够，旧历史仍有 1.2 GB 且含超限文件；需要新起一条历史（orphan 分支或新仓），或用 `git filter-repo` 改写历史。
2. 有 30 个 md 文件共 44 处链接指向将移走的路径；索引应保留原相对路径到私有仓或原始位置的映射。
3. 内容涉及 MiniMax 内部需求与内网链接，只适合私有仓库。

## 决定

待用户确认保留范围（agent-delivery 的 raw、requirements 的 .log 是否保留）和历史处理方式。
