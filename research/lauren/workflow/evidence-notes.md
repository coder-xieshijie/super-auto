# 最近工作流：可核实证据与对照问题

记录时间：2026-09-24 17:00 CST。范围是 9 月 16–24 日的 Agent Lord / Agent Archon Goal v2 工作。这里记录用户侧流程和已发生的摩擦，不预判 Lauren 的方法是否适用。

## 1. 实际流程

| 阶段 | 观察 | 证据 |
| --- | --- | --- |
| 决策 | Goal v2 先写决策文档：4 个核心决定、后附 10 条完整约束；文档是随后 plan、implement、review 的共同输入。Draft feat MR !7252 以文档首提交开始，后续继续在同一 MR 上实施。 | [2026-09-21 任务摘要](/Users/minimax/.codex/memories/rollout_summaries/2026-09-21T11-18-46-MxMM-goal_v2_decision_doc_pyramid_and_draft_feat_mr.md) 第 9、16–26、67–83 行。 |
| 计划 | Planner 把 Goal v2 拆为 8 个模块（1 个 IDL、7 个 Archon），每项有责任、验收、`owned_paths` 和依赖；计划校验 schema、路径冲突和 DAG。 | [原始实施计划](raw/goal-v2-implementation-plan.json)；[Computer History 9/22 摘要](/Users/minimax/.codex/memories/extensions/skysight/resources/2026-09-22T12-00-00-oItP-6h-memory-summary.md) 第 38–44 行。 |
| 派发 | Agent Lord 对所有依赖已交付的模块同时开放 ready set，模块各用隔离 worktree、本地提交；最终由单一 integrator 合并、全局验证、推送并更新 MR。`readySet` 的代码明确无固定并发上限。 | [流程原文](raw/agent-lord-plan-to-implement.md) 的 `Dispatch the ready set`、`Final integration`；[源码](/Users/minimax/code/github/xieshijie/agent-lord/core/src/plan.ts) 第 588–598 行。 |
| 运行与恢复 | CLI 派发成功只说明 operation 已持久化；后台 controller 执行 provider，`checkpoint` 收终态。先前同步 CLI 等待被外层超时杀死，provider 仍运行，造成整合恢复问题；9/16 的 PR #27 引入 detached worker、integration resume、SHA 和远端 PR/MR 核验。 | [2026-09-16 任务摘要](/Users/minimax/.codex/memories/rollout_summaries/2026-09-16T09-08-07-PEGH-agent_lord_durable_execution_integration_resume.md) 第 18–35、50–75 行；[流程原文](raw/agent-lord-plan-to-implement.md)。 |
| 近期观察 | 9/23 的审计时 MR !7252 未闭环；9/24 的 Computer History 窗口仍看到 Goal runtime 的继续开发与监控，没有捕获完成验证。9/23 08:07 CST 的本地 run-state 快照中 8 模块均 `delivered`、integration 为 `dispatched`、report 为空。 | [9/23 审计](/Users/minimax/.codex/memories/rollout_summaries/2026-09-23T06-45-30-Gc7O-claude_opus55_xhigh_mr7252_agent_lord_scheduling_audit.md) 第 34–40 行；[9/24 Computer History 摘要](/Users/minimax/.codex/memories/extensions/skysight/resources/2026-09-24T00-00-00-IKEu-6h-memory-summary.md) 第 9、29–33 行；[提取的运行快照](raw/goal-v2-run-extract.json)。 |

## 2. 已测量的瓶颈（限定于 9/23 那次 Goal v2 运行）

- 审计统计了 11 个 CLI 会话、15 次执行；累计执行时间 17:53:28，实际调度跨度 14:02:44，峰值并发 4、平均约 1.27；约 76.3% 的跨度只有一个 CLI 在执行。来源：[计时审计摘要](/Users/minimax/.codex/memories/rollout_summaries/2026-09-23T02-53-04-ZDKw-agent_lord_scheduling_cli_audit_and_optimization_backlog_pr.md) 第 18–30 行。
- 关键路径是 `core → turn → domain → assembly → consumer → integrator`。现有 ready set 无 worker cap；依赖完成屏障和 worktree 写租约限制了可并行工作。来源：同上第 21–27 行、[源码](/Users/minimax/code/github/xieshijie/agent-lord/core/src/plan.ts) 第 588–598 行。仅提高调度并发数不会缩短该 DAG 的串行部分。
- 五个重点 CLI 有 1,121 轮主流程模型响应、1,330 次工具调用和 21 次上下文压缩；工具型响应约 79%–91% 只调用一个工具。`turn` 首次写文件前已有 91 轮模型响应、约 55.9 分钟响应阶段。来源：[计时审计摘要](/Users/minimax/.codex/memories/rollout_summaries/2026-09-23T02-53-04-ZDKw-agent_lord_scheduling_cli_audit_and_optimization_backlog_pr.md) 第 23–31 行。没有逐请求 provider 事件遥测，不能把这些响应阶段全部归因于模型思考或服务端排队。
- 审计发现一种“串行等待却拿不到依赖代码”的结构：下游模块必须等上游 `delivered`，却仍从原始 frozen head 建 worktree，prompt 又阻止合入依赖。造成接口镜像或 stub，真实组合推迟到 integrator。来源：[独立审查摘要](/Users/minimax/.codex/memories/rollout_summaries/2026-09-23T06-45-30-Gc7O-claude_opus55_xhigh_mr7252_agent_lord_scheduling_audit.md) 第 34–36 行；[源码](/Users/minimax/code/github/xieshijie/agent-lord/core/src/plan.ts) 第 429–434 行。
- 验证规则有实际遗漏：文档指向检查器自身的 fixture 测试而非真正的 `pnpm check:local-runtime-layout`；交付未核对 `owned_paths`；knip 在集成/CI 才暴露问题。来源：[独立审查摘要](/Users/minimax/.codex/memories/rollout_summaries/2026-09-23T06-45-30-Gc7O-claude_opus55_xhigh_mr7252_agent_lord_scheduling_audit.md) 第 37–42 行。审查建议替换/删减冗余 prompt 规则，仅对有证据的失败点加校验。

## 3. 与外部方法论比对时值得检查的问题

1. 外部案例如何定义可并行单元：按业务模块、文件、PR，还是可独立验收的行为？与本地 `owned_paths + depends_on` 如何映射？
2. 下游 agent 开始时能否消费上游已交付代码和接口，还是只能拿文字契约？如果前者，如何保持确定性基线和可回滚性？
3. 交付门槛是什么：生成 commit、创建 PR、通过局部测试、CI 成功、还是最终集成验收？与 Agent Lord 的结构化 `plan-report` 如何比较？
4. 如何减少首次有效修改前的大量模型往返和不必要的上下文读取？是否有可重复的任务切分、上下文裁剪和批量工具调用证据？
5. 大量 PR 的数量与质量如何同时度量：合并率、复查/返工率、每个 PR 的可验收价值、集成成本和故障恢复？只有 PR 数量不足以判断方法优劣。

## 4. 边界与原始材料

- 本地原始材料副本：[Agent Lord 流程](raw/agent-lord-plan-to-implement.md)、[Goal v2 模块计划](raw/goal-v2-implementation-plan.json)。运行快照是从原始状态文件提取的有限字段，不是完整原件。
- 本地运行快照的原文件最后修改于 **2026-09-23 08:07:14 CST**；它不是 9/24 的实时状态。9/24 的 Computer History 仅说明当时仍在监控开发，未捕获最终验证结果。
- 尝试用 `glab api --hostname gitlab.xaminim.com` 实时回读 MR !7252 时，内网地址连接超时；本笔记因此不宣称当前 MR 状态。
- 这些数据来自一次复杂 Goal v2 工作流，不能直接推断用户所有项目的常态，也不能直接与 Lauren 的“2000 PR”数据比较。
