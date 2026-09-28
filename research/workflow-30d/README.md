# 最近 30 天工作流调研档案

先读 [综合结论](conclusions/analysis.md)，再看 [两周试验方案](conclusions/two-week-experiments.md)。Lauren 的视频、字幕、文字稿和外部文章继续保存在 [原调研目录](../lauren/analysis.md)。

## 窗口与覆盖

按事件时间取北京时间 **2026-08-25 17:33:02 至 2026-09-24 17:33:02** 的滚动 30 天。固定边界见 [scope.json](scope.json)。旧会话在窗口内的续接会被纳入；本次分析会话及已发现的后代排除。没有以文件 mtime、会话创建时间代替消息时间。

| 来源 | 本次扫描 | 窗口内会话身份 | 规范化可见记录 | 解释 |
| --- | --- | ---: | ---: | --- |
| Codex | 1,903 个 JSONL，约 7.10 GB；含主目录、archived、codex-cli、codex-api | 749（783 个源文件） | 115,150 | user 3,194；assistant 13,632；工具调用/返回 98,324。含 141 个语音转写段；回放行另保留并标记。 |
| Claude Code | 720 个 JSONL，约 540.9 MB；含 projects、子 agent、agent-switch-backups | 173 | 17,361 | 136 根、37 子 agent；含工具调用/返回 15,252。 |
| MCode | 65 个可发现 profile，2,428 个文件扫描计数；含数据库的来源清单共 2,472 条 | 758 | 38,995 | 主 profile 644 会话/38,478 记录；开发 profile 114/517。工具调用多数嵌入消息内部，主 profile 43,535 条。 |
| Agent Lord | 562 个 operation 元数据文件 | 214 个 task ID | 490 次窗口操作 | 与上述会话交叉，不加入会话/消息总数。 |

**这些是本机可发现来源的全量机器扫描与索引，不是所有消息都经人工逐字精读。** Codex 12、MCode 13、Claude 15 条重点任务链做了语义深读；跨端可能属于同一任务。源目录发现范围、缺失时间戳、排除项、去重与脱敏细节分别见三个来源 README 和分析稿。

Codex 的 `human_candidate=2,193`、Claude 的 `user_candidate=186`、MCode 的 `user_or_unclassified=569` 都只是候选类别，不能当真人输入或干预次数。Claude 的原始 `user` 事件可能是工具结果；MCode 主 profile 也有测试/探针；Codex 有 fork、回放和自动协议，语音段不等于独立 turn。不同客户端的工具序列化方式不同，不能用消息总量排名生产率。

已删除、其他设备、未同步或远程专有的记录无法从本机补齐；没有声称覆盖这些来源。已保存的历史会话分析稿用于方法校准，不作为本次新事件重新计数。历史 MR 交付声明未在本次重新访问远端验证。

## 文件结构

```text
workflow-30d/
  scope.json
  raw/
    codex/          源清单、读取前缀哈希、脱敏窗口事件 gzip
    claude/         源清单、175 份窗口事件 gzip
    mcode/          profile/数据库来源、表结构、脱敏行及会话快照
    orchestration/ Agent Lord 操作元数据允许字段快照与源哈希
  intermediate/
    codex/         消息/会话索引、统计、12 条链及原文定位
    claude/        消息/会话索引、统计、15 条链/108 个定位点
    mcode/         消息/会话索引、统计、13 条链/5,759 条链内记录
    orchestration/ 操作、task 归并、失败后接续统计
    cross-client/  显式跨端映射、六个五天窗口、Lauren 一手锚点、抽查
  conclusions/     综合分析、两周试验方案
  scripts/         只读采集、归一化、案例生成和校验脚本
```

这里的“原始资料”是**带来源定位的脱敏可见事件快照**，不是逐字节克隆用户配置目录。没有复制凭据文件；私有推理、二进制和冗余系统载荷排除。工作内容、内部路径和链接保留在本地；这些档案不是公开发布稿。Lauren 的媒体原件与字幕另存于 `../lauren/bookmark-videos/raw/`。

## 三端证据入口

- Codex：[分析](intermediate/codex/analysis.md)、[12 条链](intermediate/codex/deep-read.md)、[统计](intermediate/codex/summary.json)、[原始快照说明](raw/codex/README.md)。
- Claude：[分析](intermediate/claude/analysis.md)、[15 条原文链](intermediate/claude/cases.md)、[统计](intermediate/claude/summary.json)、[原始快照说明](raw/claude/README.md)。
- MCode：[分析与 13 条链](intermediate/mcode/analysis.md)、[结构化案例](intermediate/mcode/cases.json)、[统计](intermediate/mcode/summary.json)、[原始快照说明](raw/mcode/README.md)。
- 跨端：[关联统计](intermediate/cross-client/summary.json)、[operation→caller/endpoint 显式映射](intermediate/cross-client/explicit-operation-links.jsonl)、[六段时间覆盖](intermediate/cross-client/five-day-coverage.jsonl)、[Lauren 五处一手锚点](intermediate/cross-client/lauren-primary-anchors.md)。

488/490 操作匹配到原生 endpoint，剩余两条是没有 endpoint 的启动失败；397 条有 caller ID 的操作全部匹配本地会话。这里只合并**显式身份关系**，未用相似标题猜测全部逻辑任务。原生子 agent 还有各自父子关系，因此 Agent Lord 映射不是完整执行图。

## 复现顺序

脚本对来源只读，但重新运行会更新本目录的生成文件。源会话可能继续增长；本次快照和其哈希才是稳定输入。需要保持这份审计原样时，先复制研究目录再运行。

```bash
python3 research/workflow-30d/scripts/orchestration_extract.py
python3 research/workflow-30d/scripts/codex_extract.py
python3 research/workflow-30d/scripts/codex_finalize.py
python3 research/workflow-30d/scripts/codex_realtime.py
python3 research/workflow-30d/scripts/claude_extract.py
python3 research/workflow-30d/scripts/mcode_extract.py
python3 research/workflow-30d/scripts/mcode_postprocess.py
python3 research/workflow-30d/scripts/combine.py
python3 research/workflow-30d/scripts/verify_selected_evidence.py
python3 research/workflow-30d/scripts/validate_delivery.py
```

案例选取与报告脚本也保存在 scripts；部分分析是人工归纳，不会由扫描自动生成。`messages.jsonl` 每条保留来源路径/行号/时间；MCode 的 `#local_runtime_message_rows` 对应数据库表，`line` 是 row ID。Codex 消费时排除 `replay_of` 行。

## 核验与判断边界

本次主分析独立回查了三端关键引文 **127 处**，全部匹配原始 JSONL 或只读 SQLite；另外保存三端自己的解析、引用和快照校验结果。见 [引文核验](intermediate/cross-client/selected-source-verification.json)与各端 validation 文件。跨端归并校验没有发现规范消息时间落在固定窗口外。

[交付检查](intermediate/cross-client/delivery-validation.json)验证必需文件、主报告本地链接与时间覆盖；[产物哈希清单](intermediate/cross-client/artifact-manifest.jsonl)记录本研究目录的文件和 SHA256。本次新增档案约 1.52 GB，不含此前保存的 Lauren 视频和网页资料。

源证据分级：用户原话证明其要求/体验；工具输出证明当时具体操作/观察；助手最终报告只证明当时的交付声明；本报告建议是从案例作出的推论。无结尾、cancelled、operation failed 和 MR 未合并，分别解释；不把它们合成失败率。首末时间是墙钟跨度，无法代替实际工作时长。

此前 60 天历史分析只用于提示去重和证据分类方法。本次三端数字、案例与跨端映射均重新从当前本机记录读取。
