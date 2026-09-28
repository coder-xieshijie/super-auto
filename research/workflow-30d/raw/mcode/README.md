# MCode 原始证据快照

这些文件是本机 session 数据的**窗口内脱敏投影**，不是完整数据库备份。窗口为 `2026-08-25T09:33:02Z <= event timestamp < 2026-09-24T09:33:02Z`。源文件只读访问；没有读取 auth、账号配置、cookie 文件。

- `profiles.json`：65 个 `.minimax*` profile 的已知存储位置审计。16 个 profile 有窗口可见消息。
- `source-manifest.jsonl`：2,472 个源文件或数据库的路径、大小、SHA-256、窗口内记录数、快照相对路径。包括窗口无命中的文件，以证明按事件筛选而不是按目录日期或 mtime。
- `minimax*-schema.json` / `minimax*-legacy-schema.json`：SQLite 表结构，仅用于理解数据模型，不含配置表内容。
- `minimax*-database-rows.jsonl.gz`：从 `local_runtime_message_rows` 以只读连接提取窗口行。外层 `source_path/table/line` 中的 `line` 是 SQLite **id/rowid**，不是物理行号；`event` 是脱敏后的可见消息对象。
- `minimax*-legacy-rows.jsonl.gz`：旧版 `session_messages` 查询结果，同样按事件 timestamp，`line` 是表 id。
- `minimax*-mvs_*-messages.jsonl.gz` / `ledger.jsonl.gz` / `display.jsonl.gz`：外层 `line` 为原 JSONL 的一基物理行号，`event` 保留原对象结构并去掉私有 reasoning、签名、图片/音视频二进制与识别到的凭证。
- `snapshot.json.gz`：旧版快照若本身有窗口 timestamp，则保留可见投影、移除 piHistory；其中的 displayMessages 另逐条按自身 timestamp 纳入规范化候选。
- `session-metadata.jsonl`：来自 SQLite columnar fields 的 session 当前父子、title、cwd、runtime、status、created/updated 时间，用于关联，不把当前 status 当历史结局。
- `artifact-checksums.jsonl`：已落盘原始快照的 hash/size（README 后加，不含自身）。

## 归并方法与边界

读取每个已知 profile 的 `v2/sessions/*/*/*/*/{manifest,messages,ledger,display,snapshot}`，以及 `v2/sqlite/runtime-state.sqlite` 和旧 `sqlite.db`。新版 messages 已取代大量 ledger，旧版目录也按源事件时间扫描，避免漏掉早创建但窗口内继续的 session。主 `.minimax/sessions` 有旧会话目录但没有 JSON/JSONL 消息；`.minimax-agent* / projects` 存在但没有 JSONL；`.mcode` 不存在。其他自定义环境变量指向的未知目录不在已发现覆盖声明内。

模型上下文压缩快照、history mutation 备份、llm request/response dump 是同一会话的重放投影，不重复计为新 session 或用户消息。规范化统计优先 SQLite 可见 display rows；缺失时使用 direct display / history / snapshot。tool calls 和结果保留在消息的 `tool_calls` 中，不能再与单独工具结果相加当成独立工作量。

`source-manifest` 中活跃 SQLite 文件 SHA 只是读取时主 DB 文件的校验值，**不等于 DB+WAL 一致性备份**。稳定证据是抽出的 gzip 及其 hash。所有 schema/current metadata 和 window evidence 用途不同；窗口外当前元数据只用来解释身份/父子关系，不作为活动量。

开发 profile 的 114 个有消息 session 单列，包含自动化验证夹具，不进入用户主工作流数量。主 profile 也可能有测试或探针，233 个“交互或未分类”不能直接称为233个用户任务，569条根输入不能直接称为真人消息。

完整可见消息归一化、会话统计、13条任务链分析见 `../../intermediate/mcode/`。仅保存 session 内证据，本次未联网重新验证历史 MR 的当前状态。
