# 原始约定：用户最终决定的原话与对应问题

供 core-spec 第 7 步的跨模型查漏使用。摘自 2026-09-30 的 grill 会话（Claude Code，agent-archon 需求 `fix/goal-final-result-delivery`），以及“目标交付与开发流程澄清”会话转来的一项决定。每条先列用户原话，再列它所回答的问题与选项；“同意”表示采纳助手在该题给出的建议，建议原文一并列出。完整过程见 super-auto 仓库 `discussions/2026-09-30-goal-final-delivery.md` 第 12–19 节。

需求来源：`/Users/minimax/Documents/Codex/2026-09-29/goal-final-response-clarification/需求澄清.md`（sha256 `bc7c4e40215bb0512d7cc037c4b96e04919faf84e717ecd7a4e3f5f6b752901c`）。本需求没有已接受的 ADR。

## 1. 用户补充的前提（第一轮问题未逐条回答，由这些前提和第二轮替代）

> 在补充几个前提
>
> 1. 本次的 修复 要控制影响范围, 因为本次封板的核心需求不是 goal, 所以要避免改动过多而造成影响扩散
> 2. 创建的 mr 应该是向 feat/verify-archon-skill 这个分支合入, 因为是要利用这个分支的 skill 和功能地图
> 3. 截止时间就是 10.2 中午 12 点, 我的想法是往这个 feature 分支创建代码，到时候再单独 cherry-pick 出一个需求，只合入 preview train。因为它的核心不是为了解决本次的 goal，所以要尽量控制范围，但又需要复用我们之前讨论的那些 skill 的能力。

## 2. 第二轮

用户原话：

> Q1 ①，Q2 R3，Q3/Q4/Q5 同意

- **Q1 修哪几条路径。** 选项：① 修 A（续跑折叠已交付内容）和 B（complete 结束本轮、没有最终回复，含 TUI 自动化与 headless 把成功判成失败），blocked 两种都不动；② 只修 A。用户选 ①。助手建议中的附注：第 8 项按 B 类场景验收，不要求证明同一轨迹。
- **Q2 结果说明怎么来。** 选项：R3 = R2 加 Desktop 卡片提升（把折叠段里的交付卡片提到结果区，取 !7424 的 UI 部分，不要它“有媒体的正文优先”的规则，也不要 `deliverables`）；R2 = 已接纳的 complete 不再结束本轮，工具返回要求模型立刻写一段面向用户的最终回复（结果、文件位置、交付标记），回复为空就重试一次；R1 = 保留结束本轮、提示词要求先交付；b′ = 把 `summary` 直接显示成结果说明；a = 只做卡片提升。用户选 R3。R3 附带的约束（随建议给出，用户选 R3 时一并接受）：
  - 最终回复不宣称验证已通过，verifier 在这次回复之后才跑，Goal 最终状态仍由 Host 结算；verifier 判定口径不改，不采用 !7435 的“也验证用户可见交付”。
  - 重试一次仍为空时，按现有流程结算，照常进入验证，不因为缺最终回复把 Goal 判失败。
  - 提示词改在 TS 常量里，`.md` 同步成相同措辞，随客户端发布生效，不需要 Apollo；md 与 TS 原有的其他差异不顺手对齐。（原建议还有“措辞对老客户端也成立”一条，其依据随后被更正作废：3.0.73 起客户端不读 Apollo 上的提示词。）
  - `not_met` 照常续跑，前一次最终回复会进入过程区，接受。
  - complete 之后模型仍调用工具：不新增代码限制，列为已接受代价。（此条在第四轮 Q2 被改为 (b)，见下文。）
- **Q3 怎样算已声明交付（同意）。** 建议：只认正文里的交付标记，不新增 `deliverables` 字段；产物面板、资产索引、IM 三处读取不改；模型没写交付标记就不出卡片，接受；最终回复里仍要写出文件路径。
- **Q4 入口范围（同意）。** 建议：Desktop 必须满足实时对话、刷新和重启后的历史、右侧产物面板（现有读取已覆盖折叠段，只验证不改代码）；TUI 必须满足最终回复可见，自动化模式和 headless 下 Goal 完成那一轮不再报 `EMPTY_RESPONSE` 或 `state=fail`，按 R2 或 R3 做时 TUI 代码不用改，文件入口沿用现有的 `Created` 行；非目标：IM、Fork、v1、RC、Cloud；Windows 路径解析用单测覆盖，列为覆盖盲区。
- **Q5 交付流程（同意）。** 建议：
  - (a) 开发 MR 只用来开发和验证，产品代码不合入 `feat/verify-archon-skill`；本需求顺带对 verify-archon 和功能地图的改进单独提交，交给 7556 的会话并入；`preview_train` 的 MR 合入后关闭开发 MR。
  - (b) 产品代码，加上 `preview_train` 上已有的文档（Goal spec、implementation、verification、`changes/` 里的一条变更记录、`CONTEXT.md` 术语），放在能干净 cherry-pick 的提交里；功能地图和 verify-archon 的改动单独提交。
  - (c) deliver 在开发分支验证通过后，从 `origin/preview_train` 建 `fix/goal-final-result-delivery-preview-train`，cherry-pick 产品提交，跑相关单测和 typecheck，证明产品改动与已验证的分支一致，真实模型证据沿用开发分支上的；开 MR（显式 squash=true 并回读）、处理 CI，停在可合入，不合入。
  - (d) 10 月 2 日 09:00 前把 `preview_train` 的 MR 做到可合入，到点没完成就停下汇报已有证据和缺口。
  - (e) 只推送两条需求分支；不推送 `feat/verify-archon-skill`，不发布 Apollo，不改飞书和工作项，不动 !7424 和 !7435，不发消息。
  - (f) spec、verify、plan、证据放 super-auto `requirements/goal-final-result-delivery/`；agent-archon 只放派生的长期文档（Goal `changes/` 变更记录、Goal spec、`CONTEXT.md`；功能地图只进开发分支）；MR 描述写决定摘要和两个 sha256；不写 ADR。（其中 spec、verify 的位置被第 5 节替代。）

## 3. 第三轮

用户原话：

> Q1–Q5 都同意

- **Q1 术语。** 建议：完成提案、Goal 完成、最终回复、完成摘要、交付标记、交付卡片、卡片提升、过程区（定义见需求 worktree 根目录 `CONTEXT.md` 的“Goal 收口与交付”一节）；“结果说明”统一改叫“最终回复”。
- **Q2 有最终回复时正文选哪段。** 选项：固定取最终回复（Goal 消息里 complete 之后有文字时，正文固定取最后一段，不再比长度，只改 Goal 消息的这一分支）；保持现状。建议并采纳：固定取最终回复。
- **Q3 卡片提升的触发与范围。** 建议：在 Goal 结算为 `complete` 时触发（与过程区折叠同时），不像 !7424 那样“完成工具调用成功就触发”；提升这条 Goal 消息过程区里的全部交付卡片（含更早各轮）；同一文件路径（规范化后）只显示一张，正文已有的不再重复；展开过程区时已提升的卡片不在过程区再显示一次。
- **Q4 同一轮里完成提案被接纳后又调用 `update_goal`。** 选项：Goal 工具拒绝（返回工具错误，不改已接纳的提案，只改 Goal 工具）；不管（接受 `blocked` 覆盖 `complete`）。建议并采纳：拒绝，不论第二次填 `complete` 还是 `blocked`。（用户追问“为什么是 block 而不是 update”，助手解释 `update_goal` 是工具名、`blocked` 是其 `status` 取值后，用户同意。）
- **Q5 真实模型验收最小集合。** 建议：Electron 和 TUI 各跑一次 B 类任务（让 Goal 生成一个文件并完成），核对最终回复可见且带文件卡片、Goal 完成、右侧产物面板有这个文件、刷新后仍然一样、TUI 不出现 `EMPTY_RESPONSE`；使用会触发子代理验证的模型路由；A 类改用固定消息数据的 UI 测试覆盖卡片提升和去重；blocked 不变、非 Goal 对话不变、`not_met` 续跑用单测或脚本 provider 覆盖；deliver 的跨模型独立验证照常进行。
- 另附说明（用户未提出异议）：决定写进 Goal 的 `changes/` 变更记录，不单独写 ADR。

## 4. 第四轮

用户原话：

> Q1 (ii)，Q2 (b)，汇总确认

- 第四轮开头的表格（用户未提出异议，“汇总确认”涵盖）：写最终回复时用户按停止 → Goal 暂停 `paused(user_requested)`，提案作废，恢复后重做，沿用；应用重启或崩溃 → 提案丢失，Goal 仍进行中，启动恢复开一轮新的续跑，沿用；用户“立即发送” → 最终回复不带工具调用，消息退回队列作为新的一轮，沿用；模型两次都回空 → 按正常结束结算，提案照常进入验证，不走 !7435 的失败路径。另说明：`complete` 以后不再写 `terminates_turn`，`blocked` 和 stale 照旧写，完成之后、最终回复之前被打断时会像其他被打断的 Goal 轮一样显示“继续”。
- **Q1 写最终回复时模型服务出错（限流、额度用完、网络错误）。** 选项：(i) 照常进入验证（改 Goal 结算里处理失败的那一步，只对已接纳完成提案生效，安全拒绝仍按阻塞）；(ii) 沿用现有的失败处理（提案作废，Goal 暂停或额度受限，恢复后重做，不改结算代码）。用户选 (ii)，列为已接受代价。
- **Q2 complete 之后要不要拦下工具调用。** 选项：(a) 不拦；(b) 本轮完成提案被接纳后，Goal 的工具执行前检查拦下之后的所有工具调用，包括 `update_goal`（涵盖第三轮 Q4），被拦的调用返回“本轮已提交完成，不要再调用工具，直接写最终回复”，如果模型被拦了还继续尝试，所有尝试都会被拦，到本轮结束仍然没写出回复就按“两次都回空”的规则按正常结束结算。用户选 (b)；汇总的已接受代价删去“complete 之后模型仍可能调用其他工具”，做法增加“complete 之后拦下所有工具调用”。
- **汇总（用户确认）。**
  - 目的：Goal 收口时，用户不用追问，就能看到做成了什么、交付文件在哪；续跑、校验和过程折叠都不能再吞掉这些内容。
  - 范围：修 A 和 B（含 TUI 自动化和 headless 的误判）；blocked 不动。
  - 做法（R3）：已接纳的 complete 不再立刻结束本轮，工具返回要求写一次最终回复；Goal 完成时 Desktop 把过程区里的交付卡片提到结果区，按路径去重、展开过程区时不重复；Goal 消息里 complete 之后有文字时正文固定取最终回复；同一轮再次提交状态由 Goal 工具拒绝；最终回复不宣称验证已通过，verifier 口径不改；两次都回空按正常结束结算；提示词改在 TS 常量里、`.md` 同步；`not_met` 照常续跑；写最终回复时服务出错按 Q1。
  - 交付声明：只认交付标记，不新增 `deliverables`；产物面板、资产索引、IM、TUI 的代码都不改。
  - 入口：Desktop 实时对话、刷新和重启后的历史、右侧产物面板；TUI 最终回复可见、不再误判；非目标 IM、Fork、v1、RC、Cloud；Windows 路径单测，列覆盖盲区。
  - 验收：真实模型在 Electron、TUI 各跑一次 B 类任务；A 类用固定消息数据的 UI 测试；回归用单测或脚本 provider；跨模型独立验证照常。
  - 已接受代价：前一轮长报告正文默认折叠在过程区；模型没写交付标记就没卡片；`not_met` 后前一次最终回复进过程区；最终回复连续几轮逐字相同时触发已有的重复回复暂停；停止或重启时提案作废需重做收尾。
  - 交付：开发 MR 指向 `feat/verify-archon-skill`、不合入产品代码；deliver cherry-pick 出 `fix/goal-final-result-delivery-preview-train`，证明产品改动一致，10 月 2 日 09:00 前可合入，不自己合，到点没完成就停下汇报；用户负责 12:00 前合入；授权按第二轮 Q5。
  - 文档：spec、verify、plan、证据放 super-auto（spec、verify 的位置被第 5 节替代）；agent-archon 只放派生长期文档；不写 ADR。

## 5. spec 与 verify 改为随开发 Draft MR 交接

“目标交付与开发流程澄清”会话转述、并在该会话记录中核实的用户原话：

> 同意，通知 grill 会话，同时改成默认流程提 PR

它回答的建议（该会话“追问：交接改成一个带两份文件的 MR”一节）：

1. core-spec 把 spec.md、verify.md 写到需求 worktree 的 `.harness/docs/specs/goal-final-result-delivery/`。
2. 用户确认冻结后，grill 会话在 `fix/goal-final-result-delivery` 上提交两个提交：`CONTEXT.md` 术语（属于产品一侧，之后 cherry-pick 到 `preview_train`）；spec 与 verify（与功能地图一样只留在开发分支，不 cherry-pick）。推送分支，开指向 `feat/verify-archon-skill` 的 Draft MR（显式 squash 并回读）；旧 worktree 切成 detached，把分支让给 deliver。
3. deliver 在任意新会话、应用自建的 worktree 里开工：输入 MR 链接、spec 提交和两个 sha256，检出需求分支后在同一个 MR 上继续，最后更新描述并取消 Draft。
4. plan.md 和证据仍不提交进 agent-archon，放 super-auto `requirements/goal-final-result-delivery/`。

转来的消息另要求 spec 的“交付与授权”写清：开发 MR 就是交接用的 Draft MR，deliver 在它上面继续；spec、verify 的提交不 cherry-pick；`preview_train` 那条 MR 的证据怎么沿用；冻结以 sha256 为准，7556 再 rebase 时提交 SHA 会变。
