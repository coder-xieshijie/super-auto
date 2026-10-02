# 本地数据索引

2026-10-01 起，下列数据只保存在本机，不进 Git，也不上传 GitHub。[`.gitignore`](../.gitignore) 排除它们，历史已用 `git filter-repo` 改写去除。逐文件清单见 [files.tsv](files.tsv)（路径、字节数、sha256，按 2026-10-01 17:00 Asia/Shanghai 的本机文件生成，共 15,097 个文件、约 2.34 GB；只列不进 Git 的文件），可用来核对本地或其他副本是否完整。

各目录里的 `*.md`（分析稿、案例摘录、场景报告、README）以及 evidence 中的文本类文件（txt、html、diff、patch、脚本、`checks.json`、`*run.json`）仍在仓库中，文档里指向数据文件的相对链接只在本机有效。

## 排除范围

| 路径 | 文件数 | 大小 | 内容 | 原始来源 |
|---|---:|---:|---|---|
| `research/workflow-30d/raw/` | 2,618 | 575 MB | Codex、Claude Code、MCode、Agent Lord 的脱敏窗口事件快照，窗口见 [scope.json](../research/workflow-30d/scope.json) | `~/.codex/sessions`（含 archived）、`~/.claude/projects`（`cleanupPeriodDays` 为 365）、MCode profile 与数据库、Agent Lord operation 元数据；采集方法见 [workflow-30d README](../research/workflow-30d/README.md) |
| `research/workflow-30d/intermediate/` | 46 | 874 MB | 由快照抽取的消息、会话索引与统计（`messages.jsonl` 等） | 用 [scripts](../research/workflow-30d/scripts/) 从 raw 重新生成 |
| `research/lauren/bookmark-videos/raw/*.mp4` | 2 | 309 MB | Lauren 两段视频 | X 原帖，URL 与 sha256 见 [manifest.json](../research/lauren/bookmark-videos/manifest.json)；字幕与文字稿仍在仓库 |
| `requirements/*/evidence/` 除文本类 | 12,431 | 587 MB | 新流程试跑的验收证据：模型请求体 payloads（约 216 MB）、截图（约 233 MB）、运行与构建日志（约 79 MB）、jsonl 流水、状态快照 json | 无其他副本：spec 约定证据只放本仓库，不进 agent-archon |

## 备份

2026-10-02 MR 7595 复盘新增一份有界索引：[89 个原始会话文件的路径与 SHA-256](../research/goal-v2-deliver-trace-2026-10-02/manifest.json)，以及 [采集范围与方法](../research/goal-v2-deliver-trace-2026-10-02/README.md)。分析投影和本轮 CI 日志放在该研究目录的 `local/`，由目录自己的 `.gitignore` 排除；不含 thinking 的事件导航、结论与来源索引进 Git。这是专项增量，不替代上面的 10/1 全库 `files.tsv`，也不表示所有历史 trace 都已归档。

- 改写前完整副本（含旧历史、工作区与未跟踪文件）：`/Users/minimax/code/_archive/super-auto-backup-20261001`，HEAD `5cae28e`。
- 旧提交号到新提交号的对照见 [commit-map.tsv](commit-map.tsv)，用于查找文档里引用的本仓库旧提交号（如 `9481ec5`）。
- evidence 在本机之外只有上述备份。deliver 之后新产生的证据只写到本地；`git add` 这些路径会因 ignore 报错，需要时用私有数据仓保存。
