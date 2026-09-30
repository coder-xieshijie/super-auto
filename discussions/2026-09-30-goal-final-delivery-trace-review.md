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

## 追问：里程碑检查为什么晚了

用户原话（引用答复中“里程碑检查做晚了”一条）：

> 为什么会发生这个事情?

核对：读 deliver 会话 16:15–16:52 的推理和操作、plan.md 的第一版（本仓库 `a9710ce`）、dev-skills `46aa2d5` 的 deliver 说明、计划格式和 `check-delivery.mjs`。

事实：

- 16:28:43 提交 M1；16:29:49、16:30:01 在后台启动 S03、S02；16:30:06 的推理是“M1 已提交……S03、S02 正在用真实模型后台跑，我接下来开始做 M2”，随即开始读 M2 的代码。16:32 场景跑通、改措辞再提交时，推理写的是“run the tests, then move on to M2”。
- 16:15 到 16:51 的推理和正文里，没有一处提到里程碑检查。第一次提到是 16:51:35，M2 的 S01 跑完之后：“并行让子代理检查 M1、M2 里程碑，同时自己补充文档”。
- plan.md 第一版的进度清单列了 M1、M2、M3、独立验证、MR 各一项，里程碑一节写了每个里程碑的范围、测试和场景，都没有里程碑检查。
- 计划格式里，里程碑检查只出现在进度示例的一行里（“S01 跑通；里程碑检查（…）未发现问题；a1b2c3d”），没有单独的勾选项。
- deliver 说明写了“一个里程碑做完的标准：……里程碑检查没有未解决的问题，已提交……失败先修，再进入下一个里程碑”。`check-delivery.mjs` 不检查里程碑检查做没做、什么时候做。

答复要点：

1. **直接原因是漏做，不是权衡后的推迟。** owner 把“提交”当成里程碑做完，提交后连场景结果都没等就开始 M2；记录里看不到它考虑过这一步。
2. **规则只在说明正文里，owner 实际照着走的清单里没有它。** owner 开工时读过 deliver 说明和里程碑检查说明，之后按自己写的 plan.md 推进；plan 的进度和里程碑都没有这一步，计划格式也没要求单列。
3. **没有任何检查会拦住。** 冻结核对、独立验证都有脚本把关，里程碑检查没有；事后补做，plan 里照样能写成“已检查”。
4. **说明里有两股方向相反的力。** 开头要求“常规进展不停下来等确认”，spec 有截止时间，检查一次要 9–11 分钟；而“做完才能进下一个”只是做完标准里的一项，排在“已提交”前面，没有写成“提交之前”或“开始下一个之前”必须完成。owner 选了往前推。
5. **推断（未验证）：** 说明只在 16:00 读过一次，到 16:30 会话已深入实现细节，相隔越久越容易被自己的 plan 取代；这与第 2 条一致，但记录里没有直接证据。

影响：M1 的三个问题（生产装配里钩子顺序使 R05 的拒绝原因不对；S02、S03 证据不在改过措辞的版本上；集成测试缺两类用例）在 M2 和文档都写完后才发现，修 runtime 之后三个入口一起重跑。若 16:32 在后台启动 M1 检查，结果约 16:43 回来，那时 M2 还在写。

建议（未经确认，补进研究档案 5.4 与第 6 节第 4 条）：

- 计划格式给每个里程碑列三个勾选项：场景跑通、里程碑检查、提交；owner 按 plan 推进时就会碰到它。
- deliver 说明写清顺序：场景跑通后立即在后台启动检查；可以开始下一个里程碑，但提交下一个里程碑、或跑下一轮场景之前，必须处理完上一个的检查结果。
- 检查报告落盘到 `evidence/milestone-<M>-round<N>.md`，写明检查的 commit 范围；`check-delivery.mjs` 核对每个里程碑的提交都被某份报告覆盖，且报告时间早于下一个里程碑的第一个提交。
