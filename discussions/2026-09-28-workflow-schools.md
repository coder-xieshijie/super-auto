---
id: discussion-2026-09-28-workflow-schools
recorded_on: 2026-09-28
timezone: Asia/Shanghai
source: current-conversation
topics: [研发流程, 派系, Lauren, Stripe, StrongDM, Factory, OpenAI Symphony, Cursor, Anthropic]
---

# 仓库资料中的 agent 研发流程派系

## 用户问题（原文）

> 根据目前仓库里面已有的资料，研发流程都分成哪几个主流的派系？除了 Lauren 的研发流程，还有其他的研发流程吗?

## 资料范围

只用本仓库已有资料，未新增调研：

- [工业交付综合报告](../research/agent-delivery-2026-09-28/conclusions/report.md) 第 2 节
- [企业案例](../research/agent-delivery-2026-09-28/intermediate/industry/findings.md)：Stripe、Ramp、Spotify、Shopify（Helix、River、Dispatch）、Uber
- [架构资料](../research/agent-delivery-2026-09-28/intermediate/architecture/findings.md)：Cursor、OpenAI（harness engineering、Symphony）、Anthropic（长任务 harness、C 编译器、harness design、Managed Agents）、StrongDM
- [补充视频](../research/agent-delivery-2026-09-28/supplement-videos/analysis.md)：Factory Missions、Pi 多角色工作流
- [Lauren 源码核查](../research/agent-delivery-2026-09-28/intermediate/lauren/findings.md)、[站外分析](../research/lauren/external-analysis/findings.md)
- dev-skills `agent-prompt-rules` 收录的 Anthropic 多 agent 指南（`88efec7`）

资料本身没有做派系划分。企业案例一节明确写“各家公司并没有共同提出一套统一框架”，综合报告写“没有一篇资料证明一个框架适合所有团队”。下文按“核心押注在哪一环”归类，是助手的综合，同一家可以跨多类。

## 助手答复（分析）

### 五类

| 派系 | 核心押注 | 代表 | 典型做法 | 最适合 |
|---|---|---|---|---|
| A 自证闭环 | 先让一个 agent 能启动、操作、观察真实产品，再扩大并发 | Lauren pstack；Anthropic 长任务 harness；OpenAI harness engineering | 控制命令 + 功能地图；功能清单与进度文件，浏览器端到端验证；每个 worktree 可运行产品并可查日志和指标 | 有可运行产品、要长期迭代的仓库 |
| B 确定性流水线包住 agent | 交付链路由代码控制，agent 只替换最难自动化的一步 | Stripe Minions；Spotify Honk；Shopify River、Roast；Uber uReview | Blueprint 把 agent 节点和 lint、push 等确定性节点串起来；预热 devbox；CI 修复限两轮；统一 verify 命令；操作前核对实时状态和当前 SHA；评审意见评分去重 | 同类批量迁移、依赖升级、安全修复、代码评审 |
| C 规格和场景先行 | 验收依据独立于实现、写在前面，由它判定对错 | StrongDM Software Factory；Factory Missions；Shopify Helix | specs + scenarios 放在实现仓库外，外部服务用对真实服务校准过的行为替身；实现前写断言并分配到切片，同一 Mission 一次只有一个 worker 写代码；以原应用为参照，逐个 checkpoint 过行为 CLI、截图比对、两名隔离 reviewer | 需求能写清、有参照或能写出场景的功能开发和迁移 |
| D 以需求为单位持续编排 | 交付对象是 issue 或需求，session、PR 只是它的产物 | OpenAI Symphony；Ramp Inspect；Anthropic Managed Agents；Lauren 的 orchestrate、autopilot-full | tracker 当控制入口，claim 去重、调度前 reconciliation、失败退避；Slack、网页、PR、编辑器共享同一会话；会话日志与运行环境分离，故障后从事件恢复；一个 owner 跟到 CI、review、合入 | 大量并行需求，需要无人值守推进和故障恢复 |
| E 多 agent 规模化 | 靠拆分和并行提高吞吐 | Cursor 自驱代码库实验；Anthropic C 编译器；Pi 多角色团队；Lauren 的 swarm、arena | 递归 planner + 隔离 worker，后来删掉 judge 和集中 integrator；用 oracle 把大故障拆成独立子集恢复并行；按角色（researcher、critic、QA）分工并用 contracts 交接 | 能按接口或失败样例切开的大工程；只读调研 |

### 派系之间的主要分歧

1. **按角色拆还是按上下文拆。** Pi 按角色分工，用户旧版 plan-to-implement 按模块并行。Factory 在同一 Mission 内串行写代码，只把搜索和评审并行；Anthropic 多 agent 指南主张按上下文边界拆，指出按“规划、实现、评审”拆会变成传话；Cursor 实验删掉了集中 integrator。用户 PR #44 改为串行，站在后一边。
2. **人审代码还是只审场景。** Stripe 每个 merged PR 都经人 review，Symphony 的 worker 成功可以只到 Human Review；StrongDM 宣称人不写也不审代码，Lauren 部分 PR 自动合入后再看。后一种都以可靠的场景或验证基础设施为前提，资料没有给出缺陷率。
3. **加脚手架还是删脚手架。** Pi 七角色、pstack 的 multi-phase-plan（每 PR 十条实时验证通道）偏重；Anthropic harness design 在模型升级后逐项删掉 context reset 和 sprint 结构，pstack PR #419 用种子缺陷实验删指令，Cursor 删掉 judge 角色。共同做法是删之前做对照。

### 各派共识

- 验证要打到真实产品、真实入口和当前版本上，自写测试不够。
- 机械步骤（Git 身份、SHA 核对、等待、重试、交付核销）交给确定性代码，语义判断交给 agent。
- 以需求而不是 PR 为单位衡量，PR 数不能单独当目标。
- 独立 evaluator 也会放水，需要用已知错例校准。

### 证据边界

所有吞吐数字都是各家自述，没有独立审计，也没有同难度、同预算的跨派对照。仓库资料不能排出哪一派最好。

### 用户当前流程的位置

- grill → spec → verify → plan，再由新 session 按 spec 校验：属于 C 类的规格和场景先行；实现侧 plan-to-implement v2 串行单 owner，与 Factory 做法一致。
- 与其他派相比还缺：A 类的项目级验证能力（控制命令、功能地图）；D 类的 owner 一直跟到 CI、review、合入，以及主会话故障后的恢复；B 类把机械步骤交给运行时（Agent Lord backlog 里的告警、轮询、自动登记）。

### 仓库没有覆盖的

GitHub Spec Kit、Kiro、BMAD 等公开的 spec 驱动方法没有调研过，仓库里没有资料。用户在用的 mattpocock skills（grill-with-docs、to-spec、implement-spec）只作为工具记录在流程文档里，没有作为一种方法论研究过。

## 决定状态

- 纯分析，用户未做决定。
- 待用户选择：是否补调研仓库未覆盖的 spec 驱动方法。

## 后续：提交

用户原话：`先提交`。

- 本仓库：本轮及此前未提交的讨论记录、流程文档 v0.4、README 与 AGENTS.md 入口一并提交为本地 commit（以包含本条记录的 commit 为准），未推送；本仓库没有配置远端。其中 `2026-09-28-core-verify-build-plan.md` 由本对话的 fork 会话写入。
- dev-skills#11：吸收 Lauren 资料的改动提交到 `shijie/core-verify` 并推送，更新 PR 描述；PR 未合并。
