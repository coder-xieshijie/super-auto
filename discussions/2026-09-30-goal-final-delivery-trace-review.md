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

## 用户确认里程碑检查的三条；列出全部建议

用户原话（引用上一轮建议的三条：计划格式三个勾选项、deliver 说明写清顺序、检查报告落盘并由 `check-delivery.mjs` 核对）：

> 这个可以, 除了这些, 还有哪些建议, 一起都列出来

决定：上述三条用户已确认，记为研究档案第 6 节的 B1–B3，写入[流程文档](../process/complex-requirement-delivery.md)的决定表（v0.17）。dev-skills 尚未修改，等用户看完全部建议后一起定范围。

执行：研究档案第 6 节改写为完整清单，按阶段分五组、24 条，每条写依据、改哪里、优先级，替代原来的三档写法。原编号的对应：原第 1 条 → B5、B6；原第 2 条 → C1–C3；原第 3 条 → C4；原第 4 条 → B1–B4；原第 5 条 → A6、B7；原第 6 条 → E1；原第 7 条 → A1–A3；原第 8 条 → E2；原第 9 条 → D1–D4；原第 10 条 → B9、E3。新增：A4（检查点写明证据形式，并核对工具能产出）、A5（确认时单列只靠单测证明的用户可见行为）、B8（场景尽早脚本化）、C5（Agent Lord 派发的验证留等价记录）、D5（回流缺口写明去处）、E4（每个需求结束出一份 trace 数字）。

待用户决定：C3（Codex 验证是否不用沙箱）、C4（复验能否沿用上一轮结论），以及这次改 dev-skills 的范围。

## 追问：三家依据、我们的限制、少写 prompt

用户原话：

> 还是我们之前的讨论：
> 1. 要找 3 家的理论去做支撑，以及说明我们的限制。
> 2. 写 prompt 的时候，要根据 agent for prompt 去写。不要有太多的僵硬限制, 不要写太多 prompt，而是发挥模型自身的能力，我们只做边界。

“agent for prompt”按 dev-skills 的 agent-prompt-rules 理解。

过程：

- 开三个只读子代理，分别核对 OpenAI、Anthropic、Lauren 的本地原文存档（agent-prompt-rules 的 references/sources、本仓库 research 下的 Symphony、ExecPlan、pstack 源码、PR 419/422、访谈字幕），对 24 条逐条给出支持、部分、相反或未涉及，并附逐字引文。三份结果存为 [source-check/](../research/goal-final-delivery-trace-2026-09-30/source-check/)，助手抽查 17 处引文，都能在原文逐字找到。
- 发给子代理的 prompt 里也出现了几处坏字符（例如“清单没有覆盖”写成乱码），语义可由上下文还原，没有重发。
- 依据 trace 和此前记录整理了我们的 10 条限制（K1–K10）。

答复要点（详见研究档案[第 6 节](../research/goal-final-delivery-trace-2026-09-30/README.md)，替代此前的 24 条清单）：

1. **三家立场一致：规则进结构，prompt 只写边界。** OpenAI “promote the rule into code”、边界只写一两条；Anthropic“hooks are deterministic”、为旧模型写的 Skill 往往规定过细；Lauren“The instruction is the symptom”，PR 419 只删经对照验证的规则，固定条数上限反而让评审凑数。
2. **逐条复核后的结果：** 机制 14 条（A4、A5、B1、B3、B5、B7、B9、C1–C5、E1、E2）；写进 Skill 的一句话只有 A2、B2、B5（环境知识）三处，加上 core-spec 里 A6 一句和交接模板的 A1 四个输入项；删除 A3、B4、B6、B8 四条和 A2 里的格式要求；其余是仓库能力和本仓库约定。改完 deliver 的 prompt 净增约为零。
3. **有三处与原建议相反，需要改：**
   - B1：OpenAI ExecPlan 规定勾选清单只放在进度一节、里程碑用叙述写；建议不改计划格式，由 B3 的脚本保证。这是此前已确认的一条，改动待用户确认。
   - C4：Lauren 只在补丁不变或差异仅限测试、文档、配置时沿用结论，Anthropic 提醒验证者会走捷径；不再让验证者按推理收窄，改为脚本判断沿用，否则全量复验，慢的问题靠 C1–C3 解决。
   - E2：Lauren 要求坏 Skill 在需求中途就单独修，OpenAI 让改动对之后的会话立即生效；改为“在途会话绑定版本，改进照常合入”，不等需求结束。
4. **我们的限制里影响最大的：** 跨家族验证要调另一家的 CLI（K1，Lauren 在 Cursor 里直接选模型）；桌面端会话不能新建会话、定时唤醒不可靠（K2）；真实 Electron 与 staging 登录（K3）；中文坏字符（K7）。
5. **三家提到而原清单没有的：** 文字结尾当汇报、由 Stop 钩子判断是否续做（N1）；开工先让一个单元走完全程，包括跨家族验证者的预检（N2）；一次上一项、删规则要有对照（N3）；新句与旧规则逐条对照，避免冲突（N4）；脚本报错写明修法（N5）。

待用户决定：研究档案 6.6 的五项（B1 改由脚本核对、C3、改写后的 C4、N1、上线顺序）。流程文档本轮没有改；B1 若按新建议调整，再更新 v0.17 的决定行。

## 用户同意全部五项；按顺序提 PR

用户原话：

> 都同意，按你建议的顺序提 PR

决定（写入[流程文档](../process/complex-requirement-delivery.md) v0.18）：B1 改为由脚本核对、计划格式不加勾选项；C3 run-verifier 加不带沙箱的 codex 选项；C4 报告沿用只在差异仅限测试、文档、lint 配置时由脚本判断，否则完整复验；N1 试行 Stop 钩子；按“一次一项、先机制后 prompt”的顺序上线。

执行（dev-skills 三个叠放的 PR，按序合入）：

| PR | 内容 | 验证 | Codex 审查 |
|---|---|---|---|
| [coder-xieshijie/dev-skills#21](https://github.com/coder-xieshijie/dev-skills/pull/21) | `record-milestone-check.mjs` 存每轮里程碑检查；`check-delivery.mjs` 第 5 项与 `--milestones-only`（写了场景的里程碑都有记录、连续覆盖、第一条只覆盖自己的提交、早于之后的提交）；报告沿用（仅测试、文档、lint 配置）；验证说明的复验改为完整验证；B2 的一句随顺序检查一起改 | 临时仓库 37 + 23 个用例；按 !7576 两个检查的真实返回时间回放，报出 M1、M2 第一轮都晚于之后的提交 | 两轮：8 条（4 条 P1）、复审 4 条（1 条 P1），都已修正 |
| [#22](https://github.com/coder-xieshijie/dev-skills/pull/22) | `run-verifier.mjs` 异步、流式日志、状态文件、总时长与停滞上限、终止原因；`--preflight`（deliver 开工时跑）；`--needs-gui` + `--unsandboxed`；`--effort`；claude、mcode 改用 stream-json | 假 CLI 40 个用例；真实预检：codex 两种、mcode 正确引用通过，试跑中写错的 mcode 引用 3 秒返回 3 | 11 条（3 条 P1），都已修正 |
| [#23](https://github.com/coder-xieshijie/dev-skills/pull/23) | 删去核对子代理推理强度；一句环境知识：长任务靠后台结束通知，CI 用会退出的轮询脚本，不靠 `ScheduleWakeup`；不新增等待前的状态汇报 | 链接检查；与现有规则逐条对照 | 只改文字，未送审 |

与建议的差异：

- B2 的一句放进了 #21，没有放在 prompt PR：顺序由 `check-delivery.mjs` 核对，说明必须同时告诉 owner，否则单独合入 #21 会让 owner 碰上事后无法补救的失败。
- A1、A2 写成本仓库的 [grill 交接模板](../process/grill-handoff-template.md)，不改上游的 grill-with-docs。
- 报告沿用没有实现 pstack 的“patch-id 不变时沿用”和两次构建比对，rebase 后仍要完整复验；已写进 #21 的未验证与注意。

过程中的发现：

- Codex 审查 #22 时指出，按块解码子进程输出会把跨块的中文变成替换字符（“验证模型”变成乱码）。这是本次一直遇到的坏字符的一种来源，#22 已改为按流解码。
- deliver 会话在 20:21–20:32 按用户同意改用 `codex exec --dangerously-bypass-approvals-and-sandbox`、推理强度 high 复验：Electron 20:27 启动成功，11 分钟完成，结论 PASS（session `01a0f244-6650-73a0-b71f-5a5aff6e6df1`）。这是 C3 的实际佐证；同一模型经 mcode 的那次跑了 2 小时没有报告。
- deliver 会话在复验后又在同一个验证者 session 里续问一次，请它按 verify 的覆盖盲区 B6 自行重判 S01，验证者改判为 PASS（首次回复原文已留存）。调用方在验证者 session 里追问，会削弱验证的独立性，待讨论；deliver 会话另提出 check-delivery 对“盲区给了替代判断标准”的判定口径要与验证说明对齐，待办。
- 最终 !7576、!7590 都已取消 Draft、CI 通过；`check-delivery` 四项过三项（第 4 项缺 run-verifier 调用记录，属用户接受的偏离）。

待办：

- 按 #21 → #22 → #23 合入；每合一个，把下一个的 base 改成 main。合入后快进本机 dev-skills main。已经按旧版本开工的交付（如 !7576）沿用开工时的版本。
- 下一批：N1 Stop 钩子试行；A6 与 B7（改动范围清单与提交前检查）；E1（坏字符钩子）。
- 下一个需求结束后，用 `extract_trace.py` 出数字，对照本次看这批改动的效果（N3）。

## 追问：三个 PR 都做了什么

用户原话：

> 这三个 pr 都做了什么?

答复要点（按 PR 讲清对应的问题、改动和对 owner 的影响）：

- **#21**：`record-milestone-check.mjs` 把每轮里程碑检查的报告存成带范围、时间、哈希的文件；`check-delivery.mjs` 核对每个带场景的里程碑都检查过、范围连续、第一次检查只覆盖自己的提交、检查早于之后的提交；报告只在之后仅改测试、文档、lint 配置时沿用，否则完整复验；deliver 加一句“检查可后台进行，下一个里程碑提交前处理完”，计划格式要求里程碑编号和场景 ID。
- **#22**：`run-verifier.mjs` 边跑边写日志和状态文件；总时长（默认 90 分钟）和停滞（默认 20 分钟没有证据变化）两个上限，到了就结束整个进程组并换 CLI；`--preflight` 开工时先试一次；`--needs-gui` 时 codex 须加 `--unsandboxed`；`--effort` 显式设推理强度；审查后补了进程组清理、信号、按流解码和流式输出。core-spec 的跨模型调用说明同步改掉“不许去掉沙箱”。
- **#23**：删去核对子代理推理强度；加一句等长任务的环境知识（后台运行、结束通知、会退出的 CI 轮询脚本，不靠 `ScheduleWakeup`）；不加“等待前报状态”。
- 对 owner 只多两个动作：开工跑一次预检；每轮里程碑检查多一条命令存报告。其余由脚本自动完成。

## 追问：验证环节默认去掉沙箱

用户原话：

> run Verify 这个环节，去掉沙箱。默认使用 code CLI 的时候就是不带沙箱的状态，现在是这样的吗？

“code CLI”按上下文理解为 codex CLI。

核对当时 #22 的状态：codex 默认带沙箱（`-s workspace-write`），要显式加 `--unsandboxed` 才不带，加了 `--needs-gui` 却没加 `--unsandboxed` 会直接报错；claude 用 `bypassPermissions`，用户的 `settings.json` 里 sandbox 没有 `enabled: true`，不带沙箱；mcode 用 `--permission full`，运行日志里 `sandboxEnabled: false`。答复：不是，只有 codex 默认带沙箱。

执行：

- `run-verifier.mjs`：验证时 codex 改用 `-s danger-full-access -c approval_policy=never`，去掉 `--needs-gui`、`--unsandboxed`；调用记录的 `sandbox` 写 `none (...)`。查漏（core-spec）只读代码，仍用 `-s read-only`，没改。
- deliver、跨模型调用说明、设计记录相应修改；#22 的标题和描述改为“验证时默认不带沙箱”。
- 验证：假 CLI 用例 22 + 16 个通过；真实 codex 预检（默认、`--effort high`）通过；codex 以新参数在验证检出目录 `electron up` 成功（`mainUrl` 为 `app://./archon`）、`electron down` 成功、检出目录干净（session `01a0f28e-233b-7c70-8387-c259f080f8dd`）。
- #22 推送 `d3d63ff`；#23 变基到它之上（设计记录末尾两段冲突，两段都保留），强推 `8ee7b6c`。三个 PR 的 CI 都通过、可合并。
- 流程文档升到 v0.19。

## 按顺序合入 dev-skills#21–#23，快进本机 main

用户原话：

> 按顺序合入三个 PR，然后本地 main 快进

执行（沿用此前的 squash 合入）：

| 顺序 | PR | main 上的提交 | 做法 |
|---|---|---|---|
| 1 | #21 里程碑检查记录与报告沿用 | `90c12c9` | 直接 squash；合入内容与 PR head `29c246a` 逐字相同 |
| 2 | #22 run-verifier 限时、预检、验证默认不带沙箱 | `4a00174` | `rebase --onto` 只搬自己的 3 个提交到新 main，`--force-with-lease` 钉住旧 head 推送，base 改为 main；内容与变基前逐字相同 |
| 3 | #23 删去推理强度核对、写明怎样等长任务 | `9af8ba1` | 同上，1 个提交 |

- #22、#23 强推后 GitHub 没有触发 PR 的 CI。核对新旧 head 的文件树哈希完全相同（#22 都是 `84f0ebc…`，#23 都是 `065e892…`），旧 head 的 CI 已通过，本地链接检查也通过，据此合入。合入后 main 上三次推送的 CI 都通过。
- 失误：#21 的 squash 说明里有一处坏字符（“下一个里程碑”中的“一”），扫描报了但命令没有停下就合入了。内容不受影响；改写需要强推 main，没有做。之后两次合入改为扫到坏字符就中止，#23 的说明因此被拦下一次，修正后才合入。
- 本机 `/Users/minimax/code/github/xieshijie/dev-skills` 工作区干净，从 `46aa2d5` 快进到 `9af8ba1`。`~/.claude/skills/deliver`、`core-spec` 经 `~/.agents/skills/` 指向这个主检出，新脚本（`record-milestone-check.mjs`、`milestones.mjs`、`report-reuse.mjs`）都在，全部 `node --check` 通过；在主检出上重跑四组用例：37、23、22、16 个都通过。
- 三个 PR 的 worktree 与分支（`dev-skills-deliver-milestone-gate`、`-verifier-runtime`、`-prompt-trim`）保留，未清理。

待办：下一个需求用新版 deliver 交付后，用 `extract_trace.py` 出数字对照本次；下一批（Stop 钩子、A6 与 B7、E1）在那之后。

## 追问：下一批三项要做什么、服务什么场景

用户原话（引用上一轮答复中的“下一批：试行 Stop 钩子，改动范围清单和提交前检查（A6、B7），拦坏字符的钩子（E1）”）：

> 解释下这个内容, 要实现什么? 服务的场景是什么? explain as fool

答复要点（三项都是把靠 agent 自觉的事交给自动检查；定义见[研究记录 6.3、6.4](../research/goal-final-delivery-trace-2026-09-30/README.md)）：

| 项 | 试跑里碰到的事 | 比方 | 要做的 | 难点或管不到的 |
|---|---|---|---|---|
| N1 Stop 钩子（试行） | agent 定了时唤醒自己看 CI 就结束回合，唤醒没发生，空转 81 分钟，用户来问五次；M1 跑通后说“接下来做 M2”，漏了里程碑检查（5.1、5.4） | 下班打卡机：还有没做完、又没写卡在哪的活，就不让走 | agent 结束回合前跑脚本，对照 plan 和进度，有未完成又没说明阻塞的事项就推回去续做，最多 2–3 次 | 正当地等后台任务（完成会通知）时不能推，否则逼出忙等；所以是试行 |
| A6 + B7 改动范围清单与提交前检查 | spec 写了不改通用代码，agent 为修 M1 改了 `runner/contracts.ts` 等通用文件，第二轮检查读 diff 才发现，改写后全部场景重跑（5.5） | 装修合同写明只动厨房和卫生间，门口保安对着清单查 | A6：spec 把能改、不能改的目录写成清单，要改清单外的先问用户（core-spec 加一句，这批唯一的 prompt 改动）；B7：提交前比对改动文件与清单，越界就拒绝并说明两条路（改回去，或请用户扩清单），`check-delivery` 在最终 head 上再查 | 提交前检查可以被跳过，所以终点再查一次 |
| E1 坏字符钩子 | 长段中文偶发 U+FFFD，试跑约 50 次工具调用花在找和修；本轮 #21 合入说明写进临时文件时就坏了一个字，合入后才发现（5.6） | 打字机装报警器，打出乱码当场响 | 每次写、改文件后自动扫并报行号；提交时扫改动和提交说明；`check-delivery` 在最终 head 上再扫 | agent 直接回给用户的文字不经过工具，拦不到 |

为什么先不做：第一批（dev-skills#21–#23）还没在真实需求上用过。按 N3 一次上一项：下一个需求用新版 deliver 交付，用 `extract_trace.py` 出数字对照，再加下一项；一起上则效果好坏都分不清是哪一项。

建议：三项里 E1 可以不等。它不改 agent 的做法，只多一道检查，管的事与第一批不重叠，不影响对照，效果也好数（修坏字符的次数）。Stop 钩子风险最大，放最后。

本轮没有新决定。

## 把 dev-skills#21–#23 的改动同步给 MR 7595 的 deliver 会话

用户原话：

> 把最新的 PR 的一些改动发送到正在运行的 deliver session (正在开发的 MR 7595)，保证它的过程跟最新的流程对齐。

发送前的核对（22:01）：

- 会话是 Deliver agent-archon MR 7595（`local_ecce30d4-…`，owner worktree `wizardly-nobel-612509`，plan 在本仓库 `requirements/goal-v2-and-feedback-fixes/plan.md`）。它正在做 M1：迁移已有 3 个 wip 提交，测试迁移和 RG1 基线交给了 subagent；还没做过里程碑检查，也还没有 M2 的提交，这时对齐正好。
- 在它的 plan 上只读地跑了一次新版 `check-delivery.mjs --milestones-only`：解析出 M0–M6，M1–M4 写了场景、需要检查记录，M0、M5、M6 不需要。里程碑的写法不用改。
- 新规则落到它的分支上，有两处和别的需求不同：
  - 工具分支的 5 个提交（作者时间 20:07–21:18）最终要排在 !7181 和第 2 项 runtime 提交 `d0eb97c`（20:09）之间。覆盖要求连续，单独给 M0 补记录，后面紧跟的 `d0eb97c` 作者时间更早，必然判为晚；
  - wip 提交检查后再 squash 或改写，记录就对不上了，而重做的检查会判为晚。

发现 #21 的一个缺陷，已用小仓库复现（[rebase-gap.sh](../research/goal-final-delivery-trace-2026-09-30/rebase-gap.sh)）：

- 需求分支无冲突地 rebase 到更新后的基线，只要满足下面任一条件，覆盖这个提交的整条记录就不再计入：
  - 某个已检查的提交因上游已含同样改动而被丢掉（git 提示 `patch contents already upstream`）；
  - 上游改了已检查提交 diff 上下文里的一行。
- 结果是门禁报“M1 没有检查记录”和“提交未被覆盖”。重做的检查晚于之后的提交，只能由用户放行。
- 原因在 `checkMilestones`：记录里的每个提交都要在分支上找到，逐字比较时还保留了上下文行。
- MR 7595 计划在 M6 rebase，并与 !7590 去重，会碰上。

发出的消息全文见 [deliver-7595-sync-message.md](../research/goal-final-delivery-trace-2026-09-30/deliver-7595-sync-message.md)。

- 要点：
  - 重读 SKILL.md 和三份 references；
  - 里程碑记录的规则，以及落到它的分支上的三处注意；
  - 缺陷已报告用户，不要为绕开它去改提交时间或调整历史，到 M6 还没有结论就在汇报里写明；
  - 补跑 `--preflight`；
  - 复验改为完整验证，报告能否沿用由脚本判断；
  - 只核对模型 ID；
  - 长任务的等法；
  - 记进决策日志；
  - 改正进度里 M0 的时间：写成 22:30，实际不到 22:01。
- 发出去的消息里又出现一处坏字符（“或者它 diff”中的“它”），发送前的文件扫描是干净的，坏字符是发送时新产生的。紧接着补发了一条更正。
- 两条消息都在排队，等对方当前这一轮结束后处理。

待用户决定：这个缺陷怎么修。建议的方向：

- 记录里已不在分支上的提交直接略去。覆盖仍然按当前分支逐个提交检查，所以不会放松；
- 比较时只比文件和增删的行，不比上下文；
- 只有 rebase 冲突改了增删内容的提交，才需要重新检查。

## 追问：MR 7576 会话里关于交叉 Review 的讨论，建议是什么

用户原话：

> 在重新看下 MR 7576 这个 session, 关于 cross review 的讨论, 你的建议是什么?

### deliver 会话里的讨论（21:28–21:32）

- 用户问：交付里有没有 code review，需不需要交叉 Review；接着问：用 skill、流程还是单独 session，出了问题怎么修，怎样保证修复不引入新问题、是否要再走一遍验证，放在整个流程的哪一环。
- deliver 会话的答复：
  - 现有三道评审（同模型里程碑检查、Codex 最终验证、!7590 的 4 个人工审批）都没有专门从代码质量角度审过；
  - 建议用 Agent Lord 的 cross-review 流程审 !7590，MCode Opus 5 xhigh 与 Codex gpt-6-astra high 各审、互相质询，新会话 MCode 核对，约 1 小时；
  - 修由 owner 做，改 spec 行为就停下问用户；修完补测试、重跑受影响场景、Codex 复验；
  - 理想位置在全部场景跑通之后、最终验证之前；要长期融入，就在 deliver 里加这一步，并写清何时必做、何时可跳过。
- 会话停在等用户回“交叉 Review”（transcript 第 7885 行，21:32）。

### 核对的事实

- 最终验证（head `c071a9c`）的代码核对记录 `evidence/verifier-c071a9c86eac/review/review-notes.md` 共 9 条，全部按 R 编号对照 spec，没有一条针对 review-rules 的第 2–5 条（最少改造、复杂度、扩展性、理解成本）。
- 验证说明第 3 步规定只把影响正确性或违反 spec 的情况记为问题，其他建议最多三条（`dev-skills` `9af8ba1` `skills/deliver/references/verifier-brief.md`）。
- 第一轮跨模型验证读 diff 查出了 R22；此前两轮同模型里程碑检查都没发现（plan.md 复盘一条）。
- 2026-09-29 的设计已判断 cross-review 作为默认环节被最终验证替代，高风险改动可以点名使用（[design.md](../research/zero-based-delivery-2026-09-29/design.md) 第四节）；“高风险 MR 是否保留 cross-review 作为可以点名使用的额外评审”一直留给用户决定（[agent-lord-role.md](../research/zero-based-delivery-2026-09-29/agent-lord-role.md) “待你决定”第 2 条）。
- Agent Lord cross-review 正常路径 5 次模型调用，初审不设严重度门槛，互审按证据、严重度、最小修法三项裁定，核对者用新会话、看不到谁同意了什么（`agent-lord` `references/pipelines/cross-review.md`）。
- !7590 head `7337b129ad` 与 `preview_train` 的合并基点是 `f344353`：38 个文件，+2397/−169；`preview_train` 此后又前进了 8 个提交。
- 在 deliver 会话的 worktree 上用新版脚本跑 `check-delivery.mjs --milestones-only`：M1、M2 没有里程碑检查记录，报 2 个问题（这个需求开工早于 dev-skills#21）。
- 此刻 22:05：!7576、!7590 均已取消 Draft、CI 通过；!7590 等 4 个审批。离 10 月 2 日 09:00 约 35 小时。

### 建议

**这次做，作为点名使用的额外评审，同时当试点。流程上不设成 deliver 的默认步骤，由用户在冻结 spec 时决定。**

这次做的理由：

- 缺口成立：代码质量至今只有作者自己看过；守卫依赖“同一次运行里几个钩子拿到同一个上下文对象”这类取舍没人审。
- 这个需求处在模型独自做不可靠的边缘，同模型两轮检查漏了 R22。Anthropic：“It is worth the cost when the task sits beyond what the current model does reliably solo.”（HD L131）；“Separating the agent doing the work from the agent judging it proves to be a strong lever”（HD L25）；“A fresh context improves code review since Claude won't be biased toward code it just wrote.”（CCBP L492）
- Lauren：“Before handing back, spawn a subagent on a different model family from the one that did the work. Self-review is not a substitute.”（`show-me-your-work/SKILL.md:67`）
- OpenAI 把评审几乎全交给 agent 互审，人可以不看（HE L35、L37）。我们的仓库要求 4 个人审批，这一点不变；交叉 Review 先把问题滤掉，给审批人一张确认过的问题表。

不设成默认步骤的理由：

- Anthropic 也提醒：任务在模型能力内时，评估者是纯开销（HD L129）；额外的验证步骤会导致过度验证（O5 L61）；评审者被要求找问题总能找出一些，照单全改会过度设计（CCBP L565）。这条流程约 1 小时、5 次模型调用。
- 该不该做不由 owner 判断：让作者评估自己改动的风险，正是自评偏宽（HD L23）。由用户在冻结时决定，spec 的“交付与授权”加一行；core-spec 在改动涉及运行时、并发、持久化、权限时提示。这回答了 9 月 29 日留下的问题：保留，点名使用。

deliver 会话方案要改的地方：

| 它的说法 | 应改为 | 原因 |
|---|---|---|
| 修完后 Codex 复验“重跑受影响的场景” | 完整验证；只有改动只在测试、文档、lint 配置时才沿用旧报告，由 `check-delivery.mjs` 判断 | dev-skills#21 已合入 |
| 复验照今天的方式直接调 Codex | 走 `run-verifier.mjs`，开新会话，不在原验证会话里追问 | #22 后默认不带沙箱，能留回执，第 4 项检查可以通过；上次 S01 在同一会话里重判，独立性打了折扣 |
| 审“!7590 相对 `preview_train` 的改动” | 固定为相对合并基点 `f344353` | `preview_train` 已前进 8 个提交，直接比会混进别人的改动 |
| 没说评审拿到什么 | 只给固定的 head 与 base、spec（行为边界）、review-rules；不给 MR 描述、plan.md、验证报告 | Lauren：“Audit the diff, distrusting the PR body.”（`autopilot-full.md:6`）；不让评审者先知道已经验证通过 |

另外两点：

- 新版 `check-delivery.mjs` 多了里程碑记录一项，本需求 M1、M2 没有记录会报错。属于开工早于新机制的已知偏离，在 MR 里写明，不为过检查补记录。
- MCode 占两个角色，今天 mcode 进程改过 `~/.minimax/config.yaml`。开跑前备份、结束后比对，并且不和场景验证同时跑。最好赶在审批人开始看之前跑完，修完要新推送，已给的审批可能要重给。

查出问题后的处理：

- 分三类，参照 pstack 的 `references/bugbot-triage.md`（fix / dismiss / ask）：
  - 确认的正确性问题：修，并补一个先失败的测试，覆盖同类缺陷的所有位置（`autopilot-full.md:6`：“ask for a red test that covers every site with the same defect”）；
  - 质量取舍：改动小且明显降风险就修，否则写进 MR 作为已知取舍，留给审批人；
  - 要改 spec 规定行为的：停下问用户。
- 确认的问题写进复验输入，作为复验重点（`autopilot-full.md:6`：“Add that defect to the next round's review brief.”）。
- 修复默认不再走一遍交叉 Review，由完整复验把关；修得多时请原评审者只复查“修对没有”，最多一轮。

试点要记的数：两位初审各报几条，互审和核对后确认几条、放弃几条，耗时和 token。初审的结果就是“两家各审一遍”这种轻量做法的产出，一次运行就能比较。互审和核对刷掉的很少，以后简化成两家各一个评审者并行、owner 按上面三类处理（OpenAI `codex-subagents.md` 的 PR review 示例、pstack 的多条评审通道都是这种形状）；刷掉的多，保留现流程。反复出现的问题类型写进 review-rules、lint 或测试（HE L108：“When documentation falls short, we promote the rule into code”）。

待用户决定：

1. 这次是否做交叉 Review（deliver 会话在等回复），以及是否按上面的改法做。
2. 是否确认“交叉 Review 作为点名使用的额外评审，由用户在冻结 spec 时决定”。确认后写进流程文档，试点有了数字再改 dev-skills。

本轮没有改流程文档：以上是建议，用户尚未确认。

## 追问：E1 改为本机钩子；坏字符能否直接还原

用户原话：

> 这个 E1 可以改成本地的 hook 吧?
> 这个乱码的原因主要是因为 API 的一些接口，不是常规原因，而是我本机可能某些 API 有问题。所以这个问题不具备通用性，只放在我本地解决就行。
>
> 但是我不明白它的原理：
> 1. 是在遇到乱码的时候直接拦截，让模型重新写？
> 2. 还是说直接能够把这个乱码给还原？
>
> 有办法能够把乱码直接还原，不用让 Agent 重新去实现吗？

决定：E1 不进 dev-skills 和通用流程（不加 `check-delivery` 扫描，不加仓库钩子），改为本机 `~/.claude/settings.json` 的钩子。

答复要点（方法与数据见 [坏字符能否就地补回](../research/goal-final-delivery-trace-2026-09-30/fffd/README.md)）：

- 原先 E1 的设计是第 1 种：拦下，让模型自己改。
- 严格意义上的还原做不到：字节在到达本机前就丢了，会话记录里存的已经是 U+FFFD。但每处丢字（连续 2 个或 3 个 U+FFFD）恰好丢一个字，补字是定长填空。
- 过去 10 天 28 个会话共 901 处：工具输入 612 处，其中 108 处（18%）在丢字之前会话里已有原文，可一字不差补回；直接回复用户的文字 289 处。
- 按前后各 40 字猜：`claude-opus-5` 猜中 47/60，`qw-mid-5` 45/60；猜错的多是同义替换，少数改了意思。
- 让 agent 重写也是猜，而且多一轮；写大文件要整份重新生成，还可能再丢字。
- 建议：PreToolUse 钩子就地补。先查原文，查不到再让模型猜（回码点，回程不再丢字），补不出来才拦下；用 `updatedInput` 替换工具输入，不设 `permissionDecision`，权限照常判断；用 `additionalContext` 告诉 agent 补了哪几处、哪几处是猜的。回复用户的文字不经过工具，管不到。
- 顺带发现：在会话里嵌套调用 `claude -p` 要用干净环境，否则报 “Not logged in”；`haiku` 别名在本机网关上映射到无法识别的模型。

待用户决定：是否按此实现；猜出的字是直接替换并告知 agent（建议），还是只替换有原文的、猜的仍拦下。

## 追问：rebase 让检查记录作废是什么问题

用户原话：

> 解释一下这是什么问题？我没理解。

回答要点（从零讲，不用比喻）：

- 新规则：每个里程碑的检查报告存成记录，写明检查了哪些提交（SHA）和存的时间。门禁最后核对：每个里程碑有记录；分支上每个提交都被某条记录检查过；记录早于下一个里程碑的第一个提交。
- rebase 会让每个提交的 SHA 都换掉。脚本的做法是在新分支上找改动内容完全相同的提交，找到了就当作同一个。
- 两种没有冲突的 rebase 也会让脚本找不到：
  - 提交因上游已有同样改动被 git 去掉（MR 7595 的 `d0eb97c` 在 !7590 合入后会这样）；
  - git 显示改动时带出的前后 3 行里，有一行被上游改过。
- 一个提交找不到，整条记录作废。门禁报缺记录；重做的检查晚于后面的提交，只能由用户放行。
- 修法建议不变：跳过已不在分支上的提交；只比较改了哪些文件、增删了哪些行，不比较改动前后没变的那几行。

本轮没有新决定。

## 装本机钩子；提交整个项目

用户原话：

> 1. 创建一个钩子吧
> 2. 把 super auto 项目 commit 下

用户没有另选，按建议：猜出的字直接替换并告知 agent。

执行：

- 钩子已装在 `~/.claude/hooks/restore-lost-chars.py`，挂在 `~/.claude/settings.json` 的 PreToolUse；做法、选型数据与验证见[坏字符能否就地补回](../research/goal-final-delivery-trace-2026-09-30/fffd/README.md#本机钩子2026-09-30-装好)。
- 选型：同一批 60 处逐条测，`qw-mid-5` 默认思考猜中 44 处，中位 3.6 秒；`claude-opus-5` 有 22 处被网关的安全过滤拦下，只作后备。
- 会话里实测：Write 一处按原文补对；Bash 一处猜错（“补上”猜成“补还”），agent 收到了标注。
- 上一轮给用户的答复里有两处丢字（“改意思”“这个字”），当时钩子还没装；钩子管不到直接回复的文字。
- 提交：本轮记录一个提交；工作区里其他会话留下的未跟踪文件（goal-final-result-delivery 的两份查漏日志，goal-v2 的基线证据与工具脚本）按用户要求另作一个提交。

## 修复里程碑记录的 rebase 缺陷，合入并同步给 MR 7595 的会话

用户原话：

> 按你的建议提修复 PR, 然后合入，同时把本地更新到最新的，最后再向运行中的 session 去投递最新的变更，保证进行中的任务能够符合最新的变更。

修复：[coder-xieshijie/dev-skills#24](https://github.com/coder-xieshijie/dev-skills/pull/24)。

- 第一版按建议做了两件事：按增删的行认提交，不比较上下文行；跳过记录里已不在分支上的提交。
- 做的时候发现还缺一处：rebase 冲突改过的提交重查一轮后，这一轮必然晚于之后的提交。因此改为时间只核对每个里程碑第一次仍然有效的检查，后几轮不再核对。
- Codex 审查报出 7 条，其中 2 条 P1：二进制内容被换后认不出；用后一轮可以掩盖晚了的第一次检查。
  - 修正了 6 条。改为用作者时间和标题认出“检查后被改过”的提交，并要求重查；被其他里程碑记录覆盖的提交，不能拿来跳过。
  - 剩下一条（重命名的文件被上游大改，相似度跌破阈值）记为已知限制，后果是多查一轮。
- 验证：新增 33 个断言，改前的脚本有 13 个不通过；原有 37、23、22、16 个都通过。在 MR 7595 的真实 plan 上，新旧两版结论一致。
- CI 通过后 squash 合入 main `fbcf3b7`，main 的 CI 也通过；本机 main 已快进，已安装的 deliver 直接生效，五组用例在主检出上全部通过。
- 合入说明里有一处坏字符，钩子把它自动猜成了“复”，main 上写成了“依据复验证见”，原意是“依据与验证见”。没有强推 main 去改。

同步给运行中的会话（Deliver agent-archon MR 7595）：

- 中途查看发现它有两件事与新规则冲突：
  - 它另开的 worker 在各自的 worktree 里提交了 M3、M4，早于 M1、M2 的检查。
  - 上次的两条消息还在排队，它没看到。
- 我补发一条消息说明 worker 提交的作者时间问题，然后中断了它当前的一轮，让排队的消息生效。
  - 副作用：它把中断当成用户拒绝它的操作，停下来等指示，从 2026-09-30 22:42 一直等到用户第二天 09:17 通过 Codex 给出决定。
  - 用户的决定：先检查再提交，worker 的提交只作草稿；不得伪造检查时间、改提交时间或自行写放行。
- 我当时也用提问工具问了用户怎么安排，这个问题悬到了第二天。用户回复“你在看看最新的状态”，此时它已按用户的决定在推进。
- 合入后发第四条消息，这次没有中断，对方当轮就收到了，没有坏字符。内容：
  - 修复对它的影响；
  - 按“第一次检查早于之后的提交”核对它当前分支的结果：需求分支上 M2 的三个提交之后已有 `384cef525d`（10:51）和 `42c9857a02`（10:55），M2 的检查还没存；`wip/gv2-m3` 上的提交作者时间是 10:41–10:53。两处处理不当都会让 M2 判晚，怎么安排由它定。
- 它回复已按 `fbcf3b7` 调整 plan，写明了 M2 检查的范围和 M3 提交的生成方式。

教训：

- 中断别的会话会让它停下来等人，代价可能是几个小时。只有消息要在下一个提交之前生效时，才值得中断；中断前先在消息里说明“这是投递消息用的中断，不是拒绝你的操作”。
- 规则写成“按作者时间核对”，并行的 worker 在别的分支上的提交也算在内。这一点 SKILL 正文没写，只能靠门禁事后发现。是否在 deliver 里加一句，待下次复盘决定。

## MR 7595 会话回复的安排

对方会话（Deliver agent-archon MR 7595）回复：

- 已按 deliver `fbcf3b7` 执行，并记进 plan。
- M2 第一次检查的范围取 `a7899522d3..`（到 M2 场景修完后的 head），包含 `d465f843d8`、`384cef525d` 和 `42c9857a02`。
- `wip/gv2-m3` 只当草稿：等 M2 检查落盘后，在需求分支上用 `cherry-pick -n` 加 `commit --reset-author` 生成新提交。不改已有提交的时间，也不写放行。

核对：

- 这几个提交都不在别的里程碑第一轮记录里，放进 M2 的第一轮不会报重叠，`384cef525d` 也不会成为 M2 之后的提交。
- `--reset-author` 让 M3 的新提交以进入需求分支的时间为作者时间。这和用户经 Codex 给的决定一致：已有分支的提交只作草稿，检查之后再提交。
- 门禁本身分不清“检查后新建的提交”和“把早先写好的提交改了时间”。这里放行的依据是用户的决定，以及 SKILL“检查进行时可以接着做，提交要等”的写法，不是门禁。

没有回复对方，避免在它那边多排一轮。

## 追问：补字钩子的完整执行流程

用户原话：

> 现在的整个坏字符脚本的执行流程是什么？把流程完整地说一下。
> /explain-as-fool

答复要点（按 `~/.claude/hooks/restore-lost-chars.py` 当前版本逐段核对）：

1. 触发：本机任何 Claude Code 会话（含子代理）每次调用工具前，Claude Code 把这次调用的内容（工具名、参数、会话记录路径）交给脚本。
2. 快速检查：整段输入里没有 U+FFFD 就立即结束，不输出任何东西，工具照常执行，约 44 毫秒。
3. 找丢字：只认连续 2 个及以上的 U+FFFD；按个数推丢了几个字（2–3 个为 1 字，4–5 个为 2 字，6 个为 2 或 3 字）。单个的不管。
4. 查原文：Edit 的 `old_string` 先整段去目标文件里对；其余每处取前后各 6 个字，去“目标文件 + 会话里的用户消息和工具结果”里找，唯一一处就照抄，几处说法不一就放宽到 12、24 个字再找，找不到就交给下一步。
5. 让模型猜：剩下的打包成一次请求，每处给前后各 80 个字，要求回答字的编码；先问 `qw-mid-5`，没答或字数不对的再问 `claude-opus-5`。
6. 替换并决定去留：补好的换进工具输入；全部补上或只剩写文件、改文件的没补上，照常执行，并告诉 agent 补了什么、哪些是猜的、哪些要事后改；其他工具还有没补上的，就拦下让 agent 补好重来。
7. 记日志：每次处理写一行到 `~/.claude/hooks/restore-lost-chars.log`。

核对时发现的缺口：取 API 密钥这一步（读 `settings.json`、运行 `apiKeyHelper`）不在出错保护里，这里出错（例如钥匙串超时）时脚本整体退出、什么都不输出，工具会带着乱码照常执行，跑命令也不会被拦。已告诉用户，修不修由用户定。

## 用户定补字钩子的前提：Sonnet 5.5、medium、失败放行

用户原话：

> 整个脚本的大前提如下：
>
> 1. 模型调用：脚本需要使用模型判断时，模型选择 Sonnet 5.5 进行判断。
> 2. 推理设置：推理强度选择 Medium。
> 3. 异常处理：如果判断失败，直接放行，不做拦截，也不升级高级模型去判断。
> 4. 脚本定位：整个脚本作为一个备选方案，仅起强化作用。能尽量修复就修复，修复不了就保持现状。

决定：按这四条改钩子。上一轮发现的“取密钥出错会原样放行”在新前提下就是应有的行为，不再算缺口。

执行（详见[本机钩子](../research/goal-final-delivery-trace-2026-09-30/fffd/README.md#本机钩子)）：

- 模型改为 `claude-sonnet-5-5`，`output_config.effort: "medium"`；去掉 `qw-mid-5`、`claude-opus-5` 两级后备和 `RESTORE_LOST_CHARS_MODELS`。
- 去掉拦截：原先跑命令、发消息等工具有补不上的丢字时 `deny`，现在一律放行；补上的照换，补不上的保持原样并告诉 agent。
- 取设置和密钥、网络、拒答、回复解析、脚本异常都只记日志并放行。
- 同一批 60 处实测 Sonnet 5.5 medium 猜中 48 处，中位 2.9 秒；4 处没答案，其中 3 处是 `cyber` 类拒答，按前提放行。
- 测试 13 项通过；会话里实测“补回”猜对。超时从 90 秒改为 45 秒。

## 追问：MR 7595 的会话为什么弹出审批框

用户原话：

> 刚刚 7595 这个session 弹出审批框, 为什么?

查到的事实（2026-10-01 12:00 前后）：

- 会话一直以 `bypassPermissions` 运行，工具调用本身不会弹出审批。用户的全局设置里 `defaultMode` 是 `bypassPermissions`，PreToolUse 钩子也都不返回“ask”。
- 会话记录里没有任何审批、拒绝或权限相关的事件。最近的调用都是读代码、改代码、跑测试，已经正常返回；唯一没结束的是一次测试运行，属于正常等待。
- 子代理记录里也没有审批相关的调用。最近一个子代理在 03:55Z 跑完 M2 场景，期间启动过 Electron 实例。
- 我这边最后一次给它发消息是 02:57Z，已经送达，不是这次弹框的来源。
- 本机找不到 Claude 桌面应用记录这类审批的日志，也截不到屏幕。

结论：从记录里查不出弹框的来源，已请用户提供弹框上的文字或截图。

推测的方向，都未证实：

- 桌面应用自己的确认框，这类确认在 bypass 模式下也会出现，且不写进会话记录；
- 场景运行中 Electron 实例触发的 macOS 系统授权框，例如通知或钥匙串访问。

## MR 7595 报告的第二个门禁缺陷：重新交接后检查记录不再计入

对方会话报告：用户 2026-10-01 决定修改 verify 的 S04，它按 deliver“停下”一节重新交接（新交接提交 `9d998c8968`），把新交接行写进 plan.md 后，门禁报 M1–M4 都没有检查记录，M1 已存的两轮记录不再计入。

核对：在真实 plan 上复现成立。原因是 #21 让门禁从交接行起算，并把“早于新交接”的记录当历史，而 deliver 允许交付中途重新交接，两条规则冲突。

修复：[coder-xieshijie/dev-skills#25](https://github.com/coder-xieshijie/dev-skills/pull/25)，已开 PR，未合入，等用户确认。

- 有交接行时，从需求分支上最早的交接提交起算。
- 之后只改冻结文件的交接提交，不要求检查覆盖，也不当作“之后的提交”。
- Codex 审查 4 条（1 条 P1：合并形式的交接提交带进的代码被跳过），都已修正。
- 新增 16 个断言（[deliver-rehandoff-cases.sh](../research/goal-final-delivery-trace-2026-09-30/deliver-rehandoff-cases.sh)），改前 11 个不通过；原有用例都通过。真实 plan 上，M1 记录重新计入。

## 追问：审批框是什么，能不能跳过

用户原话：

> 看下这个图, 这是什么审批?
>
> 怎么没有办法跳过吗?

回答要点：

- 这是 Claude Code 的 critical-path 删除检查：`rm -rf $H/$r/data` 里的变量没有守卫，为空时会删到顶层目录 `/data`。官方文档（code.claude.com/docs/en/permission-modes，Critical paths 一节）写明，任何模式都不自动批准这类删除，bypassPermissions 也要问。`permissions.allow` 和 PreToolUse 钩子返回 allow 都不能放行它。
- 这条命令本身是安全的：删的是 verify-archon 三次实跑留在系统临时目录的实例数据，`H` 不会为空。我核对时这些目录已经删掉了。
- 怎样不再弹框：
  - 命令里每个变量都用 `"${H:?}"` 守卫，或者直接写字面路径。文档写明这样写的删除能通过检查，bypass 模式下不再询问。
  - `PermissionRequest` 钩子可以代为回答这类提示，但这等于关掉这道保护，不建议。
  - 没有环境变量能整体关掉它。`CLAUDE_CODE_DISABLE_SUBSTITUTION_RM_PROMPT` 只管“目标完全是命令替换结果”这一种。
- 建议在全局 CLAUDE.md 加一句环境知识：删除含变量的路径时用 `${VAR:?}` 守卫或字面路径。是否加由用户决定。
