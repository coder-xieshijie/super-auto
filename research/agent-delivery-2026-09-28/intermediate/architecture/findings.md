# 工业级 agent 交付架构：12 份一手资料核查

检索与访问：2026-09-28。范围：Cursor 2 篇、OpenAI 2 篇与 Symphony 固定 SHA 规范、Anthropic 4 篇、StrongDM 3 篇。原文、SHA256 与日期见 `source-manifest.json`；代码规范版本为 `8001b52e3062495a16e520e4ceaf8f9de868c4d0`。这些是一手团队报告与公开规范，不是独立生产审计，也没有在本机复现其收益。

## 五条结论

1. **把交付对象提升到需求/issue。** 持续运行、恢复、审查反馈、CI 与合入应围绕同一个需求身份；session、run、commit、PR 是它的产物。让人不断打开新 session、复制上下文、发“继续”，会把人工注意力变成吞吐上限。[A04][A05]
2. **并发取决于可独立验收的工作量。** 增加 worker 前，先拆出不同失败样例、接口边界和可运行环境；巨大单点故障会让十几个 agent 重复修同一个问题。[A07] 同时要有整体目标所有者，避免人人选小改动、无人负责端到端结果。[A01][A02]
3. **执行并发和发布正确性分层。** 多 worker 可以独立工作、频繁交换上游事实；发布/合入必须验证真实候选版本。Cursor 的实验允许短暂错误，不能据此取消工业系统的发布验收。[A02] OpenAI 的高吞吐依赖每 worktree 可运行产品、可查询日志和观测数据。[A03]
4. **让验收更独立、更接近用户行为。** 自写代码、自改测试、自称完成容易形成封闭自证；需要受保护的验收场景、实机交互、外部 oracle 或校准过的 evaluator。独立 evaluator 也可能放水，必须拿人类认定的错例校准。[A06][A07][A08][A10]
5. **稳定的是状态与恢复接口，角色编排应可删。** 保留需求身份、工作区、外部事件日志、故障分类、恢复与证据；每增加一道 planner/reviewer/judge 都要能指出实际修复的失败。模型提升后做逐组件消融，防止旧脚手架变成串行成本。[A08][A09]

## 各体系实际说了什么

### Cursor：不能只读 1 月的 planner–worker–judge 图

[A01, 2026-01-14](https://cursor.com/blog/scaling-agents) 报告平等 agent + 共享任务文件锁会造成等待、锁遗留和职责真空。改为递归 planner 与窄职责 worker 后扩展。

[A02, 2026-02-05](https://cursor.com/blog/self-driving-codebases) 展开后续迭代：预先整批计划受最慢 worker 阻塞；万能 executor 又因职责过多产生停工、少派发和过早完成。最终递归 planners 负责范围，隔离 workers 回传单次 handoff；删除 judge、集中 integrator。**删除某个 agent 角色不等于删除验收职责。**

限制：浏览器是内部研究项目，原文明确不面向外部用户。约 1,000 commits/hour 的峰值与约 1,000 万 tool calls/周是实验自述；允许分支上少量稳定错误，并提出发布前形成绿色快照。这不是 1,000 个可交付 PR/hour，也不是经过审计的生产质量结论。原文还指出 RAM、磁盘、编译及 Git/Cargo 锁成为并发瓶颈。

### OpenAI：环境可验证，然后把会话管理变成需求管理

[A03, 2026-02-11](https://openai.com/index/harness-engineering/) 的经验包括每 worktree 独立产品和日志/指标、短入口文档指向版本化知识、依赖边界机械检查、把重复审查反馈固化。约 1,500 merged PR/五个月、3.5 PR/工程师/日，以及人工写代码用时的约 1/10 都是团队自述，后者是估计。研究发生在从零构建的内部产品，不能外推到任意遗留仓库。低阻塞合入策略也依赖可快速纠错的环境。

[A04, 2026-04-27](https://openai.com/index/open-source-codex-orchestration-symphony/) 进一步把 issue tracker 变为控制入口：任务可以产生跨仓多个 PR，按依赖启动，持续处理 CI、rebase、review。反馈包包括真实产品视频。部分团队前三周 landed PR 增长 500% 为前后观察，没有公开控制组、缺陷率或单位需求复杂度。明确保留需要判断的交互任务。

[A05, 固定规范](https://github.com/openai/symphony/blob/8001b52e3062495a16e520e4ceaf8f9de868c4d0/SPEC.md) 是 scheduler/runner 规范，不是现成业务验收器：全局/状态并发限额、单一调度状态权威、claim 去重、调度前 reconciliation、失败退避、stall 重启、issue 独立且跨 run 复用的 workspace。worker 成功可只到 Human Review。**规范不要求 durable 调度数据库；重启依靠 tracker/filesystem 重建，不精确恢复内存队列。** blocker eligibility 是 adapter 责任的一部分；不要宣传为普适分布式 DAG 引擎。

### Anthropic：长期运行、可拆并发、独立验收、耐故障是四个不同问题

[A06, 2025-11-26](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) 用初始化脚本、功能列表、git 与进度记录应对上下文交接、未完成就宣告成功和无法启动环境；明确浏览器端到端验证弥补单测/curl 的漏检。它当时没有证明多 agent 必然优于单 agent。

[A07, 2026-02-05](https://www.anthropic.com/engineering/building-c-compiler) 的 16 agents、近 2,000 sessions、近 $20,000、两周是编译器能力实验。Linux 内核单个大故障让 agents 互相覆盖；使用 GCC oracle 混合编译把故障拆成独立子集才恢复并行。使用 Docker + git 任务 claim，并不证明共享锁一概无效。产物依然在性能、汇编/链接和部分平台上不完整；不是生产编译器替代品。

[A08, 2026-03-24](https://www.anthropic.com/engineering/harness-design-long-running-apps) 发现自评偏乐观，独立 QA 也会替错误找理由，需要真实交互与校准。作者随着模型升级删除 context reset 和 sprint 结构，把 evaluator 放到更后面。单个游戏生成样例 $200/6h 对 $9/20min，范围也扩大，**不能证明等成本或等范围提速**。质量提升与时间/费用增加可同时发生。

[A09, 2026-04-08](https://www.anthropic.com/engineering/managed-agents) 将 session append-only 日志、harness、执行 sandbox 解耦，避免容器故障丢会话；从持久事件恢复，按需创建环境。p50 TTFT 约降 60%、p95 超 90%是该服务架构前后自述，衡量首次响应延迟，不是需求交付速度。可借鉴恢复边界，不必照搬托管服务。

### StrongDM：把验证作为产品，仍需验证验证器

[A10, 2026-02-06](https://factory.strongdm.ai/) 以 specs + scenarios 驱动非交互开发；场景常置于实现仓库外，降低 agent 改测试迎合实现的机会；对 agentic 产品采用多条轨迹的 satisfaction 评价。宣言中的“人不写/不 review”及每日每工程师 $1,000 tokens 不是已证实最佳实践或成本门槛。

[A11, 日期未标](https://factory.strongdm.ai/principles) 提出 seed→接近真实环境的验证→反馈闭环。

[A12, 日期未标](https://factory.strongdm.ai/techniques/dtu) 的 DTU 在依赖边界构造行为替身，并对真实服务持续比较。可大规模重放异常而不依赖线上额度；“数千场景/小时”是厂商自述，未公开误判率或完整数据。启示是先覆盖最贵、最不稳定的外部依赖；模拟通过不能自动等价于真实生产通过。

## 从资料推导的交付设计（建议，非已验证收益）

| 已观察的瓶颈 | 建议机制 | 应记录的证据/反证 |
|---|---|---|
| 人在不同窗口接力 | 持久需求身份 + 自动续跑；明确等待人的判断点 | 每完成需求的人类介入次数与分钟、无人值守完成率 |
| agents 重复修同一故障 | 可验证切片 + 故障样例分区 + 明确所有者 | 重复工作/冲突占比、阻塞原因、关键路径 |
| 已完成上游但下游仍按旧假设工作 | handoff 携带实际 SHA/接口变化/验收结果；下游重读真实代码 | stale-base、集成返工、组合验收失败 |
| 更多 worker 造成队列更长 | 工作项 WIP 上限；按 CI/评测/合入容量调节，而非固定追求最大并发 | 队列年龄、吞吐、p50/p90 lead time、资源饱和度 |
| evaluator 只复述实现 | 受保护的需求场景 + 外部 oracle + 真实运行轨迹 | 已知缺陷检出率、误报率、漏检与事后回滚 |
| 万能协调 agent/统一 integrator 阻塞 | 确定性调度管理claims/retries；范围所有者做决策；校验可并行 | 协调耗时与有效工作比；是否失去全局验收 |
| 一次模型升级后流程仍不断加长 | 每次只移除一个组件，在相同需求集比较 | 达标率、成本、耗时、人工分钟同时报告 |

有边界的 reference flow：需求及验收场景 → readiness/依赖判定 → 受限并发工作区 → 真实运行验证 → 独立场景验收 → PR 与证据包 → CI/rebase/review 自动反馈 → 对明确候选版本验收/合入 → 回归监测与恢复。探索性原型可走轻路径；接口迁移、权限、数据一致性等需求应保留对应强验证。这里推荐的是将已有能力接通，不预设必须重写一个编排框架。

## 仍然缺失的证据

这 12 份资料没有给出跨团队、同难度需求、同成本预算下的统一实验，不能排出“最优架构”。PR 数量、代码行数、并发 agent 数和首次响应速度均不能单独证明工业交付收益。真实评估还需要：需求验收达标率、线上回归、变更失败/回滚、交付周期与人工耗时。在当前用户项目落地前，应复用现有 Agent Lord 的 claim/recovery/worktree/验收能力做对照试验。
