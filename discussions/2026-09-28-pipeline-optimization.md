---
id: discussion-2026-09-28-pipeline-optimization
recorded_on: 2026-09-28
timezone: Asia/Shanghai
source: current-conversation + agent-lord sessions (read-only)
topics: [仓库进度, Agent Lord, plan-to-implement v2, 需求验收, 编排器单点, 轮询]
---

# 仓库进度盘点与 Agent Lord pipeline 优化方向

## 来源与覆盖范围

本记录来自当前会话。助手读取了本仓库全部入口文档与结论，Agent Lord 仓库 main（`4669739`）的 `references/pipelines/plan-to-implement.md`，以及两个同日的 Agent Lord 会话（只读，未干预）：

- “Agent 调度 prompt 与 pipeline 优化”：据 Anthropic / OpenAI 官方文档写设计规范，改 cross-review 与 plan-cross-review，产出 PR #46（记录时 open，正在解决与 #44 的冲突）。
- “Codex 会话执行耗时分析”：goal-v2 run-02（MR !7450）的耗时拆解，结论推动 PR #44（plan-to-implement 改为串行）合并，本机 Skill 已更新到 `4669739`。

会话中的数字（耗时、费用、上下文大小）引自上述会话的分析，本轮没有重新计算。

## 一、用户问题（原文）

> 看下当前仓库的内容, 现在的进度是什么?
> 结合刚刚的 agent-lord 相关的 session, 我应该如何优化我的 pipeline?

## 二、助手答复要点

### 仓库进度

全部是研究与设计，没有实施、没有跑过试验：

| 内容 | 状态 |
|---|---|
| 9/24 近 30 天工作流档案与结论、Lauren 分析、两周试验方案 | 完成 |
| 9/28 工业级交付调研、补充视频、Anthropic 长任务解读 | 完成 |
| 9/28 [Agent Lord 缺口分析](../research/agentlord-gaps-2026-09-28/analysis.md) | 完成，基于 `7fd6b38` 的并行版，已部分过时 |
| 9/28 [验收环节设计](../research/verification-stage-2026-09-28/README.md) | 设计与示例完成，未实施；Agent Lord 接入部分已过时 |
| 两周试验 | 未开始 |

### 与 Agent Lord 当前状态对照

1. #44 的串行版（交付分支上连续开 session，最后一个独立 reviewer）结构上解决了缺口分析的前两项：下游拿到上游真实代码、提早组合运行。
2. 本仓库反复得出的第一短板没有动：v2 中验证由实现 session 自行决定，reviewer 对照 plan 看代码；端到端测试只在用户点名时跑（`plan-to-implement.md` 第 16 行）。run-02 的 cutover 报告仍写着“真实模型链路完全没有验证过”。
3. 验收设计的接入方案挂在 receipt、integrator、plan-report 上，这些在 #44 中已删除，需要改接到 v2。

### 优化建议（按优先级，均为建议，未获确认）

- **P0 把需求验收接进 plan-to-implement v2**：验收场景在实现前产出（plan-cross-review 的 plan 增加验收场景一节，D 检查每条需求都有场景；已有 plan 时由一个新 session 从 spec + plan 生成），manifest 记录哈希，实现 session 不能改场景；review 通过后默认启动新的验收 session，从真实入口执行场景并采证，失败交修复 session，重跑受影响场景，限 2 轮；报告逐需求给出通过／失败／未验证。第一个样本用 run-02 的收尾。
- **P1 编排器单点与轮询**：run-02 主会话 401 后闲置约 55 小时；主会话约 75% 时间在轮询。建议无人收结果超时告警，轮询一次等到任务结束或 10–20 分钟、状态不变不发进度，`RESULT_INVALID` 且会话完好时同会话续跑。
- **P2 调和“新 session 还是同 session”**：耗时分析主张按阶段换新 session（上下文 400–560K、失败只丢一段）；prompt 优化会话指出 v2 “你没有记忆、最后消息交给下一段”的写法会诱导提前收尾。建议 session 边界取 plan 阶段，完成标准写成“本阶段检查通过并提交”，去掉交接暗示；阶段未完成且未被卡住时 `turn` 同一 session 续做。
- **P3 SKILL.md 瘦身**（约 44.5KB，每次触发全量加载），按 #46 的设计规范另开 PR。
- **P4 测量**：从 run-02 起按 [试验方案](../research/agent-delivery-2026-09-28/conclusions/experiments.md) 的最小测量表记录，一次只增删一个组件。

建议顺序：合并 #46、#45 → 用 v2 加验收收尾 run-02（会推 !7450，需用户确认）→ 据结果修改 `plan-to-implement.md` 并重写验收设计的接入部分 → 编排器告警与轮询。

## 三、决定与执行状态

- 用户尚未对上述建议做选择。
- 实际执行：新增本记录、更新索引；在缺口分析和验收设计末尾追加“后续变化”说明。未修改 Agent Lord，未提交 Git。

## 四、待验证事项

1. 验收场景前置并冻结后，run-02 收尾能否在无人工介入下发现并修复真实入口问题。
2. 串行 v2 在下一次同量级需求上的实际总耗时，与 run-02 拆分版的估算（9–11 小时 vs 11–12 小时）对比。
3. 去掉交接暗示后，实现 session 是否仍提前收尾（观察每个 session 完成的 plan 阶段数与无提交 session 数）。

## 后续：进度复查

记录日期：2026-09-28，Asia/Shanghai。用户原话：`看下最新的进度`。

助手核查结果（只读）：

- Agent Lord PR #46 已于 19:18 squash 合并为 `6cde9e8`；6 篇 Anthropic 平台文档已替换为站点官方 Markdown。#46 未改 `plan-to-implement.md`，v2 仍没有默认验收阶段。
- PR #45（测试 helper 共用 fake provider）仍 open，两项 CI 通过，可合并。
- 本机 Skill 目录 `/Users/minimax/code/github/xieshijie/agent-lord` 停在 `4669739`，落后 main 1 个提交（#46）。
- goal-v2 run-02 状态文件与 operation 最后更新于 9/26 07:55，之后无活动，!7450 未推进。
- 当天 16:56 另有一个 `codex-app` 任务（Computer Use 给本人发飞书测试消息）在创建 thread 时失败：`RESULT_INVALID`，“Codex create result lacks a real threadId and hostId”，`retryable: false`。
- 本仓库上一轮的记录改动仍未提交；上一轮 P0–P4 建议用户尚未选择。

## 后续：P0–P4 实施状态核对

用户原话（引用上文“三、pipeline 怎么优化（按优先级）”）：`这些都没有做吗?`

助手对照 Agent Lord main `6cde9e8` 核对的结果：这些是上一轮提出、尚未获用户选择的建议，助手没有实施，也没有其他会话在实施。已有内容来自别的 PR：

| 项 | 状态 | 依据 |
|---|---|---|
| P0 验收接入 v2 | 未做 | `plan-to-implement.md:16` 仍为“用户点名才跑端到端”；plan-cross-review 无验收场景 |
| P1 编排器单点与轮询 | 大部分未做 | 长轮询写法 `checkpoint --seconds 600` 自 9/21 已在 `SKILL.md:174`，但 run-02 实际按约 50 秒轮询；无人收结果告警、`RESULT_INVALID` 同会话续跑均未做（`retry-invalid` 仍开新会话重放） |
| P2 新／同 session | 一半 | #46 在 `SKILL.md:137` 加了“列出未完成项就 `turn` 同一 endpoint，最多两次”；`plan-to-implement.md:27` 的“无记忆、最后消息交给下一段”写法未改，session 边界未与 plan 阶段对应 |
| P3 SKILL.md 瘦身 | 未做 | 44,733 字节 |
| P4 测量 | 未做 | backlog 有“下一次运行要看的数据”，#44 之后没有新的 plan-to-implement 运行 |

## 后续：现有资料中的结果校验思路

用户原话：`目前的资料, 关于结果校验, 思路是什么?`

助手答复为对已有资料的归纳，没有新增调研。要点：

1. **核心**：验收依据来自需求，不来自实现；写代码前定下；由没参与实现的 session 在真实入口上、对实际交付的版本执行；结论只看证据，缺证据就是未验证；失败回到修复循环，不回到人。
2. **起因**：历史遗漏（D05 Goal 不续跑、D04 effort 显示与首轮请求不一致、M10 默认装配漏接、M06 文本通过但 TUI 附件未验）都是局部测试通过、真实入口或组合路径没验，最后由用户本人发现。见 [30 天结论](../research/workflow-30d/conclusions/analysis.md) 优先级一。
3. **五个环节**：定义什么算对（需求拆成带 ID 的行为，含默认值、例外、禁止结果）→ 选证明方式（单测／集成契约／真实入口，按风险取最少充分；mock 只证明 mock 边界内）→ 证明验证本身可信（已知错例能被检出，空跑、零用例、旧服务、旧证据不算）→ 判定（PASS／FAIL／BLOCKED／NOT_RUN／STALE，证据绑定需求、版本、动作、环境、结果）→ 闭环（失败回原 owner 修复，新版本重跑受影响场景，有界轮次）。详见 [验收设计](../research/verification-stage-2026-09-28/design.md)。
4. **分工**：人定产品语义与不可妥协边界；agent 补场景、命令、证据；业务仓库维护启动、操作、观察入口；Agent Lord 派发、固定版本、保存证据、缺项标未验。
5. **与 Agent Lord #46 设计规范一致**：规范第 2 条禁止给实现端加通用验证步骤、第 3–4 条要求检查交给新 session 且逐项写明怎样算不通过；验收阶段属于后者。
6. **未解决**：设计第 5 节接入点随 #44 失效；从未在真实需求上跑过；业务仓库是否有让 agent 驱动真实入口的工具未核实；验证器自身也会错，需要用已知错例校准。
