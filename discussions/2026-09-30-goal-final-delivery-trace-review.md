---
id: discussion-2026-09-30-goal-final-delivery-trace-review
recorded_on: 2026-09-30
timezone: Asia/Shanghai
source: current-conversation（Claude Code 会话，工作目录为本仓库）
topics: [首个需求试跑的完整 trace, deliver 会话复盘, 流程问题与优化建议]
---

# Goal 最终结果与交付：整条开发流程的 trace 与复盘

## 用户原话

> Deliver agent-archon MR 7576
> 看下这个 session, 这是 Deliver 的一个 session。 找一下之前 grill with docs 和 core spec 相关的 session。
> 整体梳理一下整个开发流程的完整 trace，看一看有什么可以优化的地方，有什么问题。
> 过程和结论都记录到当前项目中

## 过程

1. **找会话。** 用会话列表找到五个相关会话：deliver（`local_8e81372c`，“Deliver agent-archon MR 7576”）；grill、core-spec 与交接（`local_c1915f24`，“Goal 最终结果与交付需求澄清”）；旁路的流程澄清（`local_c37d557a`）；需求起步（`local_1cd9acf0`）；A 阶段的 verify-archon（`local_7880aeba`）。前四个的原始记录在 `~/.claude/projects/` 下。
2. **提取时间线。** 写了 [extract_trace.py](../research/goal-final-delivery-trace-2026-09-30/extract_trace.py)，从 JSONL 提取用户输入、助手正文、工具调用、子代理和 token 用量，输出四份[时间线](../research/goal-final-delivery-trace-2026-09-30/timelines/)。提取前后扫描了密钥类字符串，没有命中。
3. **核对细节。** 读了 deliver 的[plan.md](../requirements/goal-final-result-delivery/plan.md)、两份里程碑检查报告（子代理记录）、Codex 独立验证报告和两次 mcode 调用记录，deliver、milestone-check、verifier-brief、run-verifier.mjs 的现行源码（dev-skills `46aa2d5`），唤醒与后台通知在记录里的实际时间，mcode runtime 日志里复验的工具调用，agent-archon 分支的提交和两个 MR 的状态。
4. **写结论。** 完整 trace、数字、问题和建议写在[研究档案](../research/goal-final-delivery-trace-2026-09-30/README.md)。

## 答复要点

**这次跑出来的结果。** grill 14:03 开始，15:44 用户确认冻结，15:47 交接到 Draft !7576；deliver 15:59 开工，17:57 拿到修复后的 head。定义阶段 1 小时 41 分钟，交付实现约 2 小时。spec 在交付中没改过，四种停下一次都没出现。里程碑检查报了 7 项，跨模型验证又报了 1 项同家族漏掉的实现问题，都已修。mcode 复验跑了 2 小时 3 分钟没出报告，20:03 用户在 deliver 会话里取消，改要 Codex App（gpt-6-astra，high）；owner 调度不了 Codex App，且那样出的报告过不了 `check-delivery`，20:05 正在问用户怎么继续。两个 MR 仍是 Draft。

**最大的几个问题：**

1. deliver 用 `ScheduleWakeup` 等 CI 和验证，前两次都没有唤醒会话（它用于 `/loop`；第三次在用户打断那一轮之后才进队列），18:02–19:23 空转 81 分钟，用户前后问了五次。`run-verifier.mjs` 同步等待、没有超时、运行中不写日志。
2. 最终验证受环境左右：Codex 的沙箱起不来 Electron；mcode 的模型引用写错一次；同一个模型，Codex 7 分钟，mcode 跑了 2 小时 3 分钟被取消，场景 23 分钟就跑完，其余时间在读代码和证据。用户想换 Codex App，但 run-verifier 的调用记录要求把它挡住了。
3. 复验没有收窄：只改了 UI 去重，复验者仍重跑三个入口、重读全部代码。
4. 里程碑检查在两个里程碑都做完后才一起开，M1 的问题晚发现，导致三个入口全部重跑；子代理看不到推理强度，“继承推理强度”无法核对。
5. “不改通用代码”靠检查者读 diff 发现，引起一次改写和一遍重跑。
6. 坏字符约 50 次修复调用，漏进过给用户的回复和给子代理的消息。
7. grill：第一轮被用户补充的框架前提覆盖；12 项决定全采纳推荐；一项推荐依据的说法没核实，是用户追问才发现并改掉的。
8. 流程在试跑中途改了两次（dev-skills#19、#20），plan.md 没记 Skill 版本。
9. A 路径的卡片提升在真实入口上一次都没发生，只有 UI 单测证明。

**建议**（分三档，详见研究档案第 6 节）：P0 在下一个需求前改 deliver 的等待方式、run-verifier（异步、超时、预检）、复验收窄；P1 里程碑检查即时后台启动、改动范围做成机械检查、钩子拦坏字符、grill 先问框架并把实现细节作为默认值成批给出；P2 需求期间冻结流程版本、verify-archon 的并发与固定历史注入、专用 worktree 与证据提交规则。

## 决定

本轮没有新的用户决定。以下两项需要用户选：

- Codex 做最终验证时，要不要放开沙箱；或者有图形入口时默认改用 mcode 或 claude。
- 复验能不能沿用上一轮的结论；能的话，限于哪些情况（例如只在改动不涉及产品代码时）。

deliver 会话 20:05 正在问用户：复验在 Codex App 里手动跑（过不了 `check-delivery` 第 4 项，需用户放宽），还是恢复 mcode。研究档案 P0 第 2 条给了第三种做法：run-verifier 加一个不用沙箱的 codex 模式，按用户要的 gpt-6-astra、high 运行，并留下调用记录；要改 dev-skills 的脚本，Codex 不用沙箱时 Electron 能否启动未验证。

其余建议待用户选定后，再改 dev-skills、verify-archon 和[流程文档](../process/complex-requirement-delivery.md)。流程文档本轮没有改。

## 执行结果

- 新增[研究档案](../research/goal-final-delivery-trace-2026-09-30/README.md)、提取脚本、四份时间线。
- 本文件，讨论索引一行，仓库首页“专题解读”一行。
- 没有改 deliver 会话的 plan、证据和两个 MR；没有给 deliver 会话发消息。

## 本轮发现的其他情况

- 本会话写这些文件时也写出了 7 处坏字符：4 处写进了文件（研究档案 2 处、讨论记录 1 处、索引 1 处），3 处出在修改脚本的匹配文本里。都在提交前靠扫描或匹配失败发现并修正，可以作为第 6 条建议的又一个例证。
- [首个需求试跑](2026-09-30-goal-final-delivery.md)第 10 节重复出现了两遍，内容相同；按记录约定没有删，在这里说明。
- 需求目录下的 `evidence/` 有 62 MB 未跟踪，其中包括 Codex 的验证报告和两次失败的 mcode 调用；是否提交由 deliver 会话在收尾时处理，本轮不动。

## 待验证

- 复验改用哪种方式（deliver 会话 20:05 在问用户）；`check-delivery` 与取消 Draft 在复验之后。
- `ScheduleWakeup` 在非 `/loop` 会话里什么时候触发。
- mcode 路径慢的原因。
