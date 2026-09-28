# 交付架构独立审查

审查日：2026-09-28。读取 `conclusions/report.md`、`conclusions/experiments.md`、`intermediate/lauren/findings.md`，核对固定 pstack 的 `feature.md`、`orchestrate.md`、`autopilot-full.md` 以及已归档 30 天分析。没有修改根报告，没有重审当前 Agent Lord 实现。

## 判断

未发现需要推翻主结论的事实或架构错误。报告已正确区分：实验提交吞吐与工业交付、需求并发与单需求多 agent、拓扑单写与整合角色、源码规则与运行收益、已有授权与新合入权限。docs-only 短路径、现有能力优先、历史问题不等于当前缺陷等用户边界保留得当。

有 3 处值得在交付前小幅补清，均为 P2：

### 1. 明确开发依赖与合入依赖，避免把用户现有 IDL 协作串行化

位置：`report.md:134`、`experiments.md:46`。

“上游交付后，下游接收真实 SHA”和“需要真实上游代码的任务不能提前实现”方向正确，但对当前用户的 Archon/IDL 双仓场景不够精确：开发阶段可以使用尚未合入的 IDL feature 分支，合入 Archon 前才要求 IDL 先合入 main，并重新生成。历史研究也明确该契约已被澄清并正确执行（`research/workflow-30d/conclusions/analysis.md:74`）。

建议补一句：**依赖就绪应按阶段定义：开发可消费已验证的上游 feature SHA；合入再执行项目的跨仓顺序。例如 IDL feature 可支撑 Archon 开发，Archon 合入前才要求 IDL 合入及再生成。**

不需要加新模型/字段体系；用既有依赖说明即可。否则把 `Done/merged` 作为所有下游启动前提，会重新制造用户想消除的等待。

### 2. 阶段二是组合干预，不能据此识别 owner 单项收益

位置：`experiments.md:32-42`、`report.md:177`。

阶段二同时引入 owner 连续性、真实验收、自动接续，且可能新增独立 reviewer；标题“试连续 owner”容易让后续读者把整体差异都归因于 owner。末句要求验证强度相近，也需要与新增真实验收区分。

建议二选一：

- 最小改文：改名为“试连续交付组合”，明确**这一轮只判断整套组合的净收益，不能归因于单组件**；两组保留相同最终质量门槛。后续再逐项消融。
- 若主要想识别 owner 收益：两组都使用已建立的真实验收与相同 reviewer，阶段二只改变任务生命周期的自动接续。

这是测量解释问题，不影响先接通现有能力的实施顺序。

### 3. 连续 owner 指责任与状态连续，不能绑定同一进程或会话

位置：`report.md:89`、`report.md:143`、`experiments.md:25-27`。

报告已说规划器可替换，但反复使用“同一/原 owner”仍可被实现者理解为必须无限 resume 原会话。pstack `feature.md:19` 要求必要时新 owner；`orchestrate.md:56,101` 允许 consolidated brief 重建及重启后按 PR/branch 重连。Anthropic Managed Agents 也以外部事件支持替换运行单元。

建议补一句：**连续 owner 是需求责任和权威状态的连续性；允许在上下文污染、provider 故障或进程死亡后更换 session/agent，先核对旧执行已停止或失去写权限，再接续同一任务与产物。**

这能同时避免上下文无限增长与新旧 owner 双写。复用现有 claim/fence/recovery，不建议新增通用平台。

## 可选改善，不作为本轮交付阻塞

- 试验开始时应在样本表记下实际预算/停止阈值与扩容决策窗口，避免看到结果后再定义“不可接受”；无需在研究报告里发明通用次数或金额。
- 2 周小样本的 p90 很不稳定，样本少时展示逐项时间和样本量更有用。现有报告已承认小样本方向性限制。
- `report.md` 的流程图是一条默认链；正文已明确 docs-only 例外和授权终点，无需为了图的完整性新增一整套状态机。

## 已核对的关键源文一致性

- `autopilot-full.md:3,6-10` 确实是每 PR owner 到 merge、root verdict；与 `orchestrate` coordinator 维护 stack 的角色不同，报告没有混为同一默认模式。
- `orchestrate.md:62-65,87` 明确 pilot 按任务成本缩放、rolling refill、第一项开始持续落地，便宜命令验收不需独立 verifier；报告忠实保留这些限制。
- `orchestrate.md:105-109` 将人类 gates 汇总、路由绕开，并把不阻塞当前目标的新发现转后续；报告的人类瓶颈建议符合此意，未要求消除真实产品判断。
- `orch` CLI 只记账不派发/唤醒，以及 Cursor 后续移除集中 integrator 的限制，均已准确区分。
