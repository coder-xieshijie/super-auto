已按指定 `gap-check.md` 完成只读复查，未修改文件、未运行产品验收。检查版本：

- spec SHA256：`2287ea872016cdbd8cb186697f863530c948fc59546a762fccb45fd9fbd0134a`
- verify SHA256：`5637b90fc56ea33f1a06da754f62eae7d1b340553281e47aa2d04472aae3b710`
- HEAD：`3962b648ff51aabf77484729bcb3ff6de0b5004a`

核对了两份文档、前两轮报告、原始决定（含 5b–5d）、需求稿、PRD 正文、指定版本的两份冻结规格与第 2 项 verify，以及指定分支上的验证 Skill、六份功能地图和相关源码。

**§18 将验证能力、功能地图纳入同一 MR，与原始决定 5d 一致；额度操作授权也有 5c 支持。仍发现以下 6 处验收问题。**

**1. 恢复额度命令缺少结果断言**

类型：判别力不足  
位置：[verify M15](/Users/minimax/.claude/worktree/agent-archon/eager-leavitt-d0d8db/.harness/docs/specs/goal-v2-and-feedback-fixes/verify.md:1133)、R100、S35、S36。  
问题：验收检查恢复子命令存在，却没有证明它实际恢复了规定的账号状态。  
依据：spec §18.1 要求“5h 使用率回到 20%”；授权要求每个场景结束后恢复 Credits 设置。M15 仅要求“有恢复子命令”，S35、S36 的恢复步骤之后没有回读检查点。  
影响：恢复子命令返回成功但没有修改、写错使用率，或最后未恢复 Credits，仍可能满足列出的检查点。场景中先用设置操作降到 20%，也不能证明恢复子命令有效。  
建议：增加独立命令验收：从非 20% 状态执行恢复，再查询确认 5h 为 20%；记录 Credits 原值并在清理后回读。成功、失败和提前退出的场景均保留清理结果证据。账号不可用时，用接口替身验证命令契约，真实结果按 B15 报告。

**2. 真实额度场景的豁免没有延伸到功能地图验收**

类型：越出 spec  
位置：[verify R102](/Users/minimax/.claude/worktree/agent-archon/eager-leavitt-d0d8db/.harness/docs/specs/goal-v2-and-feedback-fixes/verify.md:176)、RG1、B15、完成条件。  
问题：账号不受测试平台覆盖时，S35、S36 可以列为盲区，但同一能力进入功能地图后又被要求实跑通过。  
依据：原始决定 5c 与 spec 授权允许“真实额度场景记为覆盖盲区”；§18.3 允许“没有实跑的标为未实跑”。B15 只明确承接 S35、S36，而 RG1 要求“更新后的地图场景在交付版本上通过”，R102 又引用该条件。  
影响：账号不可用时，一种解释允许交付，另一种解释要求 `limits.md` 的真实额度子功能必须通过，结束条件无法唯一判定。  
建议：明确 B15 同时适用于功能地图中对应的真实额度子功能；索引标为未实跑并关联原因与证据。命令本身的实现、契约检查及故障注入场景仍须通过。

**3. RG1b 混入迁移后的新行为，且未明确进入完成门槛**

类型：不可执行 / 缺少覆盖  
位置：[verify RG1b](/Users/minimax/.claude/worktree/agent-archon/eager-leavitt-d0d8db/.harness/docs/specs/goal-v2-and-feedback-fixes/verify.md:1111)、S17、完成条件。  
问题：RG1b 引用完整 S17，却没有排除迁移基线尚不支持的到点前手动恢复，也没有给出其新增清除路径的步骤。  
依据：RG1b 要求迁移前后各跑“S17 的接口版本”；S17 步骤 4 要求到点前启动 Goal Turn。原始决定 5c 明确这是对 !7181“到点前拒绝恢复”的改变，本地对应分支也仍有该拒绝逻辑。RG1b 还要求“等待期间清除后到点不恢复”，但 S17 没有清除步骤。完成条件只点名 RG1、RG2、RG3。  
影响：照搬 S17 会把正确迁移判失败；仅按 RG1b 摘要自行删步骤，又会形成不同测试。交付时也可能遗漏这组迁移对照。  
建议：将 RG1b 写成两个独立接口流程：自动到点恢复、清除后不恢复，明确不执行到点前手动恢复；新行为留给迁移后 S17 验证。完成条件显式加入 RG1b 及两次提交的对照证据。

**4. S29 依赖了本次明确取消的后台 shell 等待**

类型：不可执行  
位置：[verify S29](/Users/minimax/.claude/worktree/agent-archon/eager-leavitt-d0d8db/.harness/docs/specs/goal-v2-and-feedback-fixes/verify.md:822)、spec §8、§18.3。  
问题：通知场景没有固定一个仍会触发依赖等待的目标。  
依据：S29 要求发送 `continuation.md` 的后台任务目标并等待 `required_background`；指定版本地图的目标使用 `bash run_in_background`。spec §8 明确 Goal 自己启动的后台 shell 不阻塞续跑，§18.3 也要求地图按此更新。  
影响：保留该 shell 目标、正确取消等待的实现会卡在 S29 第一步；地图仅更新预期而不替换目标，同样无法验证同会话普通 Turn 的通知。  
建议：S29 直接使用 S14 的后台 subagent 目标，并确认任务未结束、普通消息对应未绑定 Goal 的 Turn 后再检查通知。地图分别保留“shell 不等待”和“subagent/workflow 等待”的步骤，避免依赖一个会随修改改变含义的目标文本。

**5. S41 的预占样本可能在启动时被合法处理**

类型：判别力不足  
位置：[verify S41 前提及检查点](/Users/minimax/.claude/worktree/agent-archon/eager-leavitt-d0d8db/.harness/docs/specs/goal-v2-and-feedback-fixes/verify.md:1087)、spec §4.1、§4.5。  
问题：场景把停机时写入的预占直接当作启动后的固定预占，却没有规定它为何应在恢复后保留。  
依据：S41 给 paused Goal 写入一条预占，启动实例后固定要求“预占 1、未知 1、本目标请求数 5”；spec 要求可靠证明未发送时释放预占，发送情况未知时保留未知占用。  
影响：正确恢复实现可能释放该孤立预占，或依据执行事实将其归为未知，使固定断言失败；为通过场景而永远保留孤立预占的实现反而可能通过。  
建议：将启动恢复测试与投影测试分开。投影样本在受控的发送前屏障下形成有效预占，再读取各消费面；启动样本则明确执行身份和发送事实，按释放或转未知的预期检查。所需屏障及 TUI 样本加载能力明确登记。

**6. S41 仍没有检查事件和 `get_goal` 的完整字段投影**

类型：缺少覆盖  
位置：[verify S41 检查点](/Users/minimax/.claude/worktree/agent-archon/eager-leavitt-d0d8db/.harness/docs/specs/goal-v2-and-feedback-fixes/verify.md:1095)、R35、B18。  
问题：固定样本补齐了部分消费面的数值检查，但事件与工具结果仍可漏掉工作、收尾、预占及口径版本。  
依据：spec §4.6 要求各消费面分别表达 `accountingVersion`、请求数、工作、收尾、历史、预占、未知和 `usageIncomplete`；S41 对事件与 `get_goal` 只检查历史、未知、`usageIncomplete` 和总请求数。B18 仅覆盖 TUI。  
影响：API 字段完整，而事件或 `get_goal` 只返回总数、没有工作/收尾拆分或预占字段，仍能通过当前检查点。  
建议：列出“消费面 × 适用字段”的断言表，逐项核对固定值及 `accountingVersion=2`。恢复后新增请求导致样本变化时，固定读取水位或明确预期增量，不能仅与另一个可能同样漏字段的接口比较。