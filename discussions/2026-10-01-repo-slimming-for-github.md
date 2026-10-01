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

## 追问一：“试跑”是什么

> 这个试跑是什么?

助手答复：指新流程（grill → core-spec → 冻结交 Draft MR → deliver）第一次用于 agent-archon 的两个真实需求：`requirements/goal-final-result-delivery`（matrix/agent-archon!7576）与 `requirements/goal-v2-and-feedback-fixes`（!7595）。`evidence/` 是 deliver 按 verify.md 在接口、TUI、Electron 上跑场景留下的截图、checks.json 与日志。

更正上一轮：evidence 不是 session 数据。goal-v2 的 plan 写明按 spec“交付与授权”，plan 与证据只放本仓库、不进 agent-archon，所以本仓库是唯一副本，不能只留索引后删除，应先搬到私有数据仓。

## 追问二：gitignore 加清理历史能省多少

> 把 evidence 和本地的 session 放到 .gitignore 里面，然后再把本地 Git 的 log 做一些清理：只保留中间过程的那些 git commit，把最开始这些 session 相关的 commit 清掉。这样的话预计会省多少?

实测（HEAD `ee27ac4`，按 pack 内对象磁盘占用 `%(objectsize:disk)` 按路径归类）：

| 类别 | pack 内占用 |
|---|---|
| workflow-30d raw + intermediate（session） | 750.7 MB |
| Lauren 两段视频 | 301.1 MB |
| requirements evidence | 133.0 MB |
| agent-delivery raw | 8.5 MB |
| 其余全部 | 3.8 MB |
| 合计 | 1197.1 MB |

- session 数据只在第一个提交 `9481ec5` 引入，但该提交同时带 Lauren 的文字资料与视频；evidence 分散在 15 个提交里，与 plan 等过程文件同提交。所以不能按“删掉开头几个提交”处理，应按路径改写全部历史（`git filter-repo --invert-paths`），提交保留、只去掉这些文件。
- 去掉 session 与 evidence：`.git` 约 1.2 GB → 约 313 MB，省约 880 MB；其中 301 MB 是视频，且两段视频超过 GitHub 100 MB 单文件上限，不去掉仍推不上去。连视频一起去掉：`.git` 约 12 MB（gc 后实际数值待实测）。
- 加 .gitignore 不会删本地文件，工作区仍约 2.3 GB；磁盘节省全部来自 `.git`。已跟踪文件需 `git rm --cached` 才会停止跟踪。
- 风险：改写历史会改变全部提交号；其他会话正持续向 master 提交（本轮期间新增 `219df51` 到 `ee27ac4`），需在它们停下时操作，并先做完整备份。ignore evidence 后，deliver 新产生的证据只在本地，无版本记录。

决定：待用户确认是否连视频一起去掉、何时执行。

## 执行：去掉数据、改写历史、上传私有 GitHub

> 视频也一起去掉，先备份再改写历史
> 然后上传到 private github

执行结果（2026-10-01 16:20–16:35）：

1. 备份：整个目录 APFS clone 到 `/Users/minimax/code/_archive/super-auto-backup-20261001`（旧 HEAD `5cae28e`），`git fsck --connectivity-only` 通过。
2. 索引：[data-index/README.md](../data-index/README.md) 与 [files.tsv](../data-index/files.tsv)（16,665 个文件、约 2.35 GB，含 sha256）。各数据目录里的 `*.md` 保留在 Git 中（workflow-30d 1.6 MB 分析稿与案例摘录、evidence 场景报告）；Lauren 只去 mp4，字幕与元数据保留。
3. `.gitignore` 排除上述数据，`git rm --cached` 解除跟踪后提交。
4. `git filter-repo --invert-paths --path-regex` 改写全部 157 个提交；另删 3 个 Codex 应用留下的 `refs/codex/turn-diffs/checkpoints/*`（指向旧树，filter-repo 不改写，备份中仍在）；`gc --aggressive --prune=now` 后 `.git` 由 1.2 GB 降到 13 MB（pack 12.6 MiB），`git fsck --full` 无错误。
5. 本地数据核对：索引中的文件全部存在；唯一大小不符的是正在写入的 `evidence/m23-6969/_build/prepare-runtime-d770f05f30.log`（MR 7595 deliver 在跑构建）。
6. 旧新提交号对照：[data-index/commit-map.tsv](../data-index/commit-map.tsv)（如 `9481ec5` → `4e18c1dcf1`）。

## 追问三：evidence 保留文档类，非文档为什么大，提交是否都保留

> 再调整一下 evidence 的内容吧。文档类的东西应该就先保留，然后非文档的内容为什么会这么大呢？哪些内容占得比较大？现在调整之后的 commit 信息是有多少条？中间很多讨论的过程都保留了吗？

evidence 591 MB 的构成（按 data-index 首版清单）：

| 类别 | 大小 | 文件数 | 说明 |
|---|---:|---:|---|
| `payloads/*.request.json` | 216 MB | 4,336 | 故障代理抓下的每次模型请求完整请求体，每个约 100 KB，system prompt 与 tools 大量重复 |
| png 截图 | 233 MB | 942 | Electron 场景截图，其中失败点击截图 21 MB |
| log | 79 MB | 655 | electron-main 44.5 MB、runtime 24 MB、渲染进程 console 7.4 MB |
| jsonl 与 `tui-output.raw` | 30 MB | 约 1,300 | steps、events、fault-proxy 流水与 TUI 原始输出 |
| 其余 json | 28 MB | 约 4,800 | 各步骤 Goal 状态、history、config 快照 |
| 文本类 | 约 5.6 MB | 1,640 | txt（TUI 屏幕文本等）、html、diff/patch、脚本、checks.json、run.json |

提交：改写后 159 个提交（含其他会话之后提交的 `958e229`），commit-map 中被裁掉的为 0，涉及 discussions 与 process 的 121 个提交都在。拿备份旧 HEAD `5cae28e` 与对应新提交 `9f1133137f` 逐文件比对：仅少 16,664 个数据文件，其中没有 `.md`，其余文件内容一致。

执行：`.gitignore` 把 evidence 中的 txt、html、diff、patch、sh、ts、mjs、`checks.json`、`*run.json` 重新纳入，新增 1,640 个文件约 5.6 MB；只追加提交、不再改写历史，这些文件不出现在旧提交里。暂存内容扫描凭据无命中。`data-index/files.tsv` 改为只列不进 Git 的 15,097 个文件（约 2.34 GB）。deliver 会话未提交的 `tools/m*` 文件未纳入。
