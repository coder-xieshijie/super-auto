# 本地数据索引

下列数据只保存在本机，不进 Git，也不推送到 GitHub。[`.gitignore`](../.gitignore) 排除它们；2026-10-01 已用 `git filter-repo` 把它们从历史里去掉。

逐文件清单见 [files.tsv](files.tsv)，只列不进 Git 的文件，用来核对本地或其他副本是否完整。

- 生成时间：2026-10-02 12:06 Asia/Shanghai。
- 规模：29,215 个文件，约 3.32 GB（十进制）。
- 列：`path`、`bytes`、`sha256`、`backup`。`backup` 写这个文件在哪份备份里，见下文“备份”。
- 2026-10-01 的旧版清单（15,097 个文件、三列）在 Git 历史里。

各目录里的 `*.md`（分析稿、案例摘录、场景报告、README）仍在仓库中。evidence 里的文本类文件也在仓库中，包括 txt、html、diff、patch、脚本、`checks.json`、`*run.json`。文档里指向数据文件的相对链接只在本机有效。

## 排除范围

文件数与大小按 2026-10-02 12:06 的清单统计。大小为十进制，旧版本用的是二进制单位，所以数字略有差别。

| 路径 | 文件数 | 大小 | 内容 | 原始来源 |
|---|---:|---:|---|---|
| `research/workflow-30d/raw/` | 2,618 | 603 MB | Codex、Claude Code、MCode、Agent Lord 的脱敏窗口事件快照，窗口见 [scope.json](../research/workflow-30d/scope.json) | `~/.codex/sessions`（含 archived）、`~/.claude/projects`（`cleanupPeriodDays` 为 365）、MCode profile 与数据库、Agent Lord operation 元数据；采集方法见 [workflow-30d README](../research/workflow-30d/README.md) |
| `research/workflow-30d/intermediate/` | 46 | 916 MB | 由快照抽取的消息、会话索引与统计（`messages.jsonl` 等） | 用 [scripts](../research/workflow-30d/scripts/) 从 raw 重新生成 |
| `research/lauren/bookmark-videos/raw/*.mp4` | 2 | 324 MB | Lauren 两段视频 | X 原帖，URL 与 sha256 见 [manifest.json](../research/lauren/bookmark-videos/manifest.json)；字幕与文字稿仍在仓库 |
| `requirements/goal-final-result-delivery/evidence/` 除文本类 | 1,067 | 73 MB | 示例 1 的验收证据：模型请求体 payloads、截图、运行日志、jsonl 流水、状态快照 json | 无其他副本：spec 约定证据只放本仓库，不进 agent-archon |
| `requirements/goal-v2-and-feedback-fixes/evidence/` 除文本类 | 25,391 | 1,345 MB | 示例 2（!7595）的验收证据，同上；10-01 之后新增约 14,000 个 | 同上。deliver 仍在进行，这个目录还在增长 |
| `research/goal-v2-deliver-trace-2026-10-02/local/` | 91 | 61 MB | 10-02 复盘的分析投影（不含 thinking）与 CI 日志 | 由该目录的 [extract.py](../research/goal-v2-deliver-trace-2026-10-02/extract.py) 从 `~/.claude/projects/` 原始会话生成；源文件哈希见 [manifest](../research/goal-v2-deliver-trace-2026-10-02/manifest.json)；由该目录自己的 `.gitignore` 排除 |

## 备份

两份备份都在本机，合起来覆盖清单里的全部文件。2026-10-02 12:06 已逐个核对 sha256，全部一致。

| `backup` 列 | 位置 | 内容 |
|---|---|---|
| `20261001` | `/Users/minimax/code/_archive/super-auto-backup-20261001` | 改写历史前的完整副本，含旧历史、工作区与未跟踪文件，HEAD `5cae28e`；清单中 15,026 个文件在这里 |
| `20261002-incremental` | `/Users/minimax/code/_archive/super-auto-backup-20261002-incremental` | 按仓库相对路径保存；清单中 14,189 个文件（约 0.865 GB）在这里 |

增量备份包括三部分：
- 10-01 之后新增或改过的文件。
- 10-01 旧清单里有、但完整副本里没有的 61 个文件：旧清单 17:00 生成，晚于 16:19 的备份。
- 10-02 复盘的 `local/`。

**本机之外没有任何副本。** 两份备份和工作区在同一块磁盘上，只能防误删，防不了磁盘损坏或换机。要不要放到私有数据仓或其他介质，待用户决定（[待决事项](../process/open-items.md)）。

以后新增的本地数据不会自动进入清单和备份。需要时重跑一次同样的步骤：
1. 列出 ignored 文件。
2. 计算 sha256。
3. 与 `files.tsv` 比对，把新增或改过的复制进新的增量目录。
4. 核对哈希，再重写清单。

旧提交号到新提交号的对照见 [commit-map.tsv](commit-map.tsv)，用于查找文档里引用的本仓库旧提交号（如 `9481ec5`）。`git add` 这些被忽略的路径会报错。
