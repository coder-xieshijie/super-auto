# Codex 原始可见事件快照

这些 gzip 是本机 Codex 来源事件的窗口内、脱敏后快照；并非原始 JSONL 的逐字完整复制。窗口为 2026-08-25T09:33:02Z 至 2026-09-24T09:33:02Z，按每条事件时间筛选，包含窗口前创建的会话在窗口内继续发生的事件。

- `sources.jsonl`：1,903 个来源文件，记录绝对路径、扫描时长度、实际读取长度、行数、读取前缀 SHA256、窗口首末行、坏 JSON 行、快照位置及排除状态。约 7.10 GB 源文件全部扫描，坏 JSON 为 0。
- 783 个 `.jsonl.gz`：342,154 条可见源事件。每行包装为 `source_path`、`source_line`、`event`，可直接回到对应源文件。
- 来源：`~/.codex/{sessions,archived_sessions}`、`~/.codex-cli/{sessions,archived_sessions}`、`~/.codex-api/{sessions,archived_sessions}`。不存在的目录不产生文件。额外检查 `~/.codex-setup-backups`、`~/.cache/codex-profile`，未发现额外 JSONL session。没有读取 auth/config 文件。

保留普通 user/assistant 消息、工具调用与结果、执行/用量等元数据；排除私有 reasoning、analysis channel、system/developer 指令、turn context、compaction context 和二进制/长不透明载荷。常见凭证、Authorization/Cookie、token URL 等使用启发式脱敏。当前研究根任务与其后代排除，防止本次工具日志或研究材料重放污染历史统计。

语音的 `realtime_item/transcript_segment` 已保存，141 个可见段也进入规范消息，其中 user 63、assistant 78。一个段不等于一个 turn；语音和文字可能表达同一请求。本次不把这些段算成独立任务，不在没有稳定 ID/源关系的情况下仅凭相同文本自动合并。

同一 session 可能有续写分片、导入、fork 或子 agent 来源。快照保留这些原始关系；`intermediate/codex/messages.jsonl` 中使用 `replay_of` 标记可证明的重复，不删除相同短句的独立输入。源事件数、规范消息行数、会话身份数和独立任务数不同。

源文件可继续增长。本次 SHA256 对应 manifest 中固定读取范围内的字节，不能拿后续全文件 hash 直接比较。本机已删除、未同步、其他机器和远程专有会话不在覆盖范围内。快照包含私人工作资料，仅用于本地分析。
