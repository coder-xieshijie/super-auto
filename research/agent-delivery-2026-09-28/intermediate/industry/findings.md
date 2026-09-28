# 企业一手案例：从需求到可合并 PR 的自动化

调研日：2026-09-28。13 篇可读取的公司原文，覆盖 Stripe、Ramp、Spotify、Shopify、Uber；以下归纳 7 类强案例。正文快照、HTML 日期核实、检索记录和 SHA256 清单在 `../../raw/industry/`。这是企业自述的机制与结果，没有独立审计其内部 PR 或事故数据。

## 最值得补进既有 Lauren 研究的 5 点

1. **交付链路本身需要确定性代码。** Git、测试入口、来源 SHA、去重、分页、状态恢复、交付核销不应全靠 agent 记住；让 agent 负责代码探索、修复与难判断的语义。Stripe Blueprints、Spotify Fleet Management 和 Shopify River 在不同环节采取同一分工。
2. **把一次性环境准备移出请求关键路径。** 预制镜像、缓存、预热服务能改善第一次可验证结果的延迟；隔离环境还解除共享文件、端口、数据库的并发约束。仅增加 worker 数不会自动获得这种能力。
3. **拆任务和安排并发依据可验证边界。** 独立仓库迁移、独立界面可以并行；共享 fixture 的验证可能必须串行。内部 checkpoint 的顺序与 PR 之间的并发是两个层级。
4. **减少人类搬运状态，保留人类决定业务语义。** 从 PR 生成继续跟到最新 SHA、审查反馈、合并后状态；必要提问应附带完整调查和最小待决事项。人类不必再充当 Git、CI、工单之间的同步器。
5. **审查也要控制噪声与成本。** 不把“评论更多”“双 review 一致”当正确性证明；审查意见需要去重、校验、按价值筛选。通用任务宜有修复预算和停止原因，避免把模型分歧变成无限循环。

以上是跨案例推论；各家公司并没有共同提出一套统一框架。

## 1. Stripe Minions：无人值守执行，人工审查交付

[Part 1](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents) / [Part 2](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2)

- 用既有 devbox 承载独立任务：预热目标约 10 秒，代码、缓存和服务已准备；生产访问与任意网络访问受限，允许执行过程免逐步确认。
- Blueprints 把实现、诊断等 agent 节点与 lint、push 等确定性节点组合；按目录加载规则，复用多个客户端相同的规则源，只给任务需要的工具子集。
- 本地快速反馈优先；CI 最多两轮，第二轮后交回人类，避免无上限试错。这里的 one-shot 指无人中途指导，内部仍可运行反馈和修复循环。
- **数字边界：** 2026-02 两篇文章分别自述每周 >1,000 / >1,300 个完全由 minion 编码、经人工 review 的已合并 PR。不是一次尝试成功率，也不是无人审核上线率；没有总需求数、返工率和线上缺陷率。

**可借鉴：** 给已有 Agent Lord 节点补确定性前后处理与标准验证命令，先衡量准备时间和首轮 CI 通过率。Stripe 的资源规模不能直接证明个人团队需要完整云平台。

## 2. Ramp Inspect：完整环境与可继续的共享会话

[原文，2026-01-12](https://builders.ramp.com/post/why-we-built-our-background-agent)

- 完整应用环境与监控、feature flag、浏览器验证接通；界面任务交付截图和 live preview。
- 每 30 分钟构建仓库镜像，启动时同步最新基线。可提前只读研究，但同步结束前阻止写文件；请求开始前准备依赖与缓存。
- Slack、网页、PR、编辑器共享同一会话；多人能接续审查修改。agent 可派生小任务、查询状态；并发运行依赖隔离的远程环境。
- **数字边界：** 自述前后端仓库已合并 PR 约 30% 由 Inspect 编写，是采用占比而非任务成功率。“不限并发”“运行近乎免费”为该文产品表述，没有成本、队列或并发实验支撑，不能当容量保证。

**可借鉴：** 优先消除重复 clone/build 与会话转交成本；PR 接受修改后应回到原任务上下文。真正的容量上限还包括模型配额、CI、共享依赖及审查队列。

## 3. Spotify Honk：在成熟批量迁移流水线上替换最难自动化的一段

[Part 1](https://engineering.atspotify.com/2025/11/spotifys-background-coding-agent-part-1) / [Part 2](https://engineering.atspotify.com/2025/11/context-engineering-background-coding-agents-part-2) / [Part 3](https://engineering.atspotify.com/2025/12/feedback-loops-background-coding-agents-part-3) / [Part 4](https://engineering.atspotify.com/2026/4/background-coding-agents-dataset-migrations-honk-part-4)

- 仓库选择、PR 创建、评审与合并沿用 Fleet Management；agent 替换代码转换步骤。此前约一半 PR 自动化主要来自传统系统，不能算成 LLM 产出。
- 针对批量改造，写清前置条件、目标状态和不适用情况；一次做一件改造。准备上下文的上游 agent 与受限 coding worker 分离。
- `verify` 统一封装 formatter/build/test、压缩反馈；PR 前强制跑验证。另用 prompt + diff 的 judge 检查越界，不能替代行为测试。其当时 judge 尚无正式 eval。
- 2025-11 自述累计 >1,500 个 agent PR 合入生产代码库；特定迁移比手写节省 60–90% 时间，无可复算控制实验。2025-12 自述数千会话中 judge 否决约 1/4，被否决时约半数能纠正；不是最终失败率。
- **失败边界更有价值：** 2026-04 数据迁移放弃不够标准化的 Scio 范围；dbt/BigQuery 需要明确字段映射。缺少自动测试使人类验证继续成为瓶颈。文中 240 个自动迁移 PR 不等于 1,800 条管线全部自动完成；10 工程周是人工基线估计。

**可借鉴：** 先从同类、有检查器、可批量复用的需求建立稳定产品线，再扩大范围。不要用一条大 prompt 覆盖不兼容的代码形态。

## 4. Shopify Helix：明确参照物、小 checkpoint、逐关验证

[原文，2026-09-21](https://shopify.engineering/helix)

- 原应用和代码直接作为迁移参照；先让人确认简短 checkpoint 顺序，再做细化。
- 每个 checkpoint 依次经过行为 CLI、同状态截图比较、两位上下文隔离的代码 reviewer、工程师验收；完成后提交，下一段在已验收结果上继续。
- CLI 可脱离模拟器验证行为；视觉审查先核对截图状态是否一致。修复后重跑受影响门禁，保存测试与 review 证据。
- 可明确授权跳过人工 checkpoint 审批，但机器门禁保留；不同 screen 可并行。文章没有本工具的 PR 吞吐、失败率或对照成本数据，不能把另一次 Shop 应用 12 周迁移归因为 Helix 的已证实提速。

**可借鉴：** 复杂需求按可演示、可验证的行为切片；不必把每个 checkpoint 变成独立 PR。其无限重试和双 reviewer 全批准策略是特定案例，不宜无预算照搬；已有行为/规范争议应路由人类决策。

## 5. Shopify River：让自动化一直负责到真实闭环

[修复闭环，2026-09-02](https://shopify.engineering/river-vulnerability-remediation) / [底层平台，2026-05-28](https://shopify.engineering/under-the-river)

- 操作前核对实时仓库、PR、工单；账本只记载历史，不充当事实或锁。发现已被其他变更解决就停止重复修复。
- rebase 后旧 SHA 的 CI 结果作废；共享 lockfile 基于当前 head 重放，避免覆盖邻近升级。人工已接手的分支尊重其所有权。
- 合并后核对默认分支、实际依赖与 tracker；遇到产品语义问题，交付已完成调查和最小待决问题，再继续跟进。
- **数字边界：** 依赖流程最初 11 天 backlog 下降约 70%；下降部分约 2/3 直接合并，余下为过时或其他地方已修，不能称为“70% 被 agent 修复”。freshness-gated merge queue 的安全合并占比 10%→80%，不是所有需求自动交付率。
- 平台把 durable session 与可替换 harness、sandbox 分离。新增 agent 作为 profile 复用基础设施；共享会话沉淀知识。其 30 天 3,536 个 River-coauthored merged PR 不能算完全无人编码或全部会话转化率，session 也包括研究和问答。

**可借鉴：** 和用户既有 fixed SHA、operation/claim/recovery 方向一致，重点应验证现有能力能否跑通“等待→恢复→新 SHA 验收→真实交付核销”，而非再造平台。

## 6. Shopify Dispatch：按资源安排并发，先证明问题再提修复

[原文，2026-07-29](https://shopify.engineering/building-an-agentic-harness-that-outlasts-the-model) / [Roast，2025-06-18](https://shopify.engineering/introducing-roast)

- 首次按领域分区并行查找，后续增量 diff 扫描并复用架构上下文；验证阶段因共享端口、数据库和 fixture 采用串行。
- 先确认测试可运行，再派发验证与修复；漏洞必须由贴近真实公共调用路径的测试证明。更强模型也会增加低价值候选，不能直接交给人类。
- 自述约六周数千次扫描、>80 个应用、>300 个不同严重性 finding；这些不是 PR 或已修缺陷数。全量扫描约 $50–300、增量 $5–50 是其范围内成本，不能套用普通需求。
- Roast 示范把机械改造、类型 autocorrect 与 agent 修剩余错误组合，并支持从步骤重放；没有证明采用该框架本身提高交付成功率。

**可借鉴：** 并行研究/实现时显式列出共享资源，验证可用独立资源才能并行，否则在该环节限流。稳定重复的失败逐步下沉为脚本和检查器。

## 7. Uber uReview：审查吞吐需要精准反馈和去重

[原文，2025-08-12](https://www.uber.com/us/en/blog/ureview/)

- 专项评论生成后，再做质量评分、语义去重、低价值类别过滤；根据语言/类别的用户反馈调整阈值。可由 lint 检查的语法规则仍交给 lint。
- 自述反馈用户中约 75% 评论有用、约 65% 评论在同 changeset 被处理；这是评论口径，不是缺陷检出率、PR 成功率或生产质量。
- 文章承认只有代码上下文，不能据此可靠判断整体系统设计。原文还存在 65,000 diffs “每周”与“每月”的内部冲突，本报告不采纳该吞吐数。其每周 1,500 小时节省来自假设人工第二 reviewer 每 commit 10 分钟的估算，不是观测净工时。

**可借鉴：** 为 cross-review 统计真实采纳的 bug、误报和审查耗时，过滤风格噪声与重复意见；人类 review 只接收有证据、关联最新变更的发现。

## 一套可验证的适用条件，而非“企业都这么做”

| 任务类型 | 优先组织方式 | 可提高并发的条件 | 最可能的人类瓶颈 |
|---|---|---|---|
| 同类依赖/配置/API 迁移 | 样本验证后批量运行 | 输入/输出一致，仓库隔离，清楚的 skip 条件 | 异常语义、缺少自动验证 |
| 明确 bug 或小需求 | 单 agent 闭环，周围确定性步骤 | 测试和真实运行环境齐备 | 需求不明确、现网不可复现 |
| 复杂新功能/跨模块 | 顺序 checkpoint + 独立分支并行 | 接口基线真实可用，整合持续进行 | 业务取舍、系统设计、集成 |
| UI/平台迁移 | 参照实现 + 行为和视觉门禁 | 每 screen 环境/状态可复现 | 审美与兼容语义 |
| 安全或生产敏感修复 | 状态核实→证明→修复→批准→核销 | 可隔离检测；共享测试受控 | 风险接受、权限、上线选择 |

这张表是本次综合建议，并非任一来源的直接结论。扩大并发前可先量化：环境启动、等待上游、运行验证、CI 排队、人工等待、修复次数、最终验收；比较单位已接受需求的人工分钟与总成本。PR 数适合作为产出明细，不适合单独作为目标函数。

## 资料边界与复核

- 13 篇原文均可独立打开；7 个案例是工作流分类，不是 7 家公司。
- 日期以原公司正文/HTML metadata 优先。Jina 的 `Published Time` 对 Stripe 和 Shopify harness 与原始发表信息不同，未据它判定为新文章；Shopify 原始 HTML 日期已保存。
- Exa 第 4 次查询达到免费限流，原错误已保存，随后用 web 搜索和 Jina 获取；未配置新 key。
- 本轮只研究外部机制，没有实测这些私有平台、复查用户四天内新增会话，或修改用户现有实现。
