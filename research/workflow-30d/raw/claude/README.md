# Claude 窗口原始记录（脱敏快照）

范围：`~/.claude/projects/**/*.jsonl` 与 `~/.claude/agent-switch-backups/**/*.jsonl`。`~/.claude/sessions` 和 `~/.claude/backups` 未发现 JSONL。未扫描全盘任意复制的 Claude 日志；iCloud 旧分析稿没有当作新源重新计入。没有读取 auth/config/凭据文件。

按 `scope.json` 的每条事件时间筛选，不按文件 mtime，不按会话创建日期。无时间戳记录只统计缺失，不猜测日期。本月正在运行的源可能增加窗口外事件；本次 SHA256 对应脚本读取到的字节，不代表以后文件不变。

- `source-manifest.jsonl`：每个已扫描源的绝对路径、大小、SHA256、总行数、窗口事件数、重复数、坏 JSON 数、snapshot 位置。窗口无事件源也列出。
- `<path-hash>.jsonl.gz`：按原文件对应的窗口事件，每行 `{source_path, line, event}`。`line` 是原始 JSONL 的一基行号。快照保留事件UUID/parentUuid/sessionId/timestamp/type/cwd/isSidechain/isMeta及普通 message/tool 内容。未对快照去重，便于核对源覆盖；去重发生在 `intermediate/claude/messages.jsonl`。
- 不保留私有 thinking/reasoning、signature、二进制内容；hook/progress 内嵌冗余载荷与附件不用于用户行为分析。对常见 token、Authorization/Bearer、密码等做模式脱敏。脱敏可能掩掉同名普通配置值；原始工具证据可能因此不是字节相同副本。
- 这批是用户授权的本地资料保存，不是公开稿。会话包含私人工作文本、内部路径和URL；最终公共分享需另作审查。

提取脚本：`../../scripts/claude_extract.py`。校验结果：`../../intermediate/claude/validation.json`。完整正文索引和分析：`../../intermediate/claude/analysis.md`。
