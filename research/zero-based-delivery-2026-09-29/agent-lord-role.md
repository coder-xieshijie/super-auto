---
id: agent-lord-role
status: 候选，未经用户确认
created_on: 2026-09-29
timezone: Asia/Shanghai
---

# Agent Lord 在新流程中的角色

依据：
- Agent Lord main `775bc88`：SKILL.md 与 #48 的提交说明；
- dev-skills main `4818e9f` 中的 core-spec、deliver；
- [design.md](design.md) 第四节，[steps.md](steps.md) 第九节；
- 来源编号见 design.md。

## 一、Agent Lord 现在有什么

| 层 | 内容 |
|---|---|
| 派发与看管（底层） | 用 `node core/dist/cli.js` 在 Codex CLI/App、Claude Code、MCode 上启动任务，状态持久化；`checkpoint` 做有界等待（默认 600 秒）；出错时 `recover` 在同一会话继续；会话丢失或反复失败时换一个新会话，并给它一份自包含的交接材料；并行任务按 worktree 隔离，写入有租约；后台进程在结果 30 分钟没被收走时提醒一次，先发飞书私信，失败再用 macOS 通知（#48） |
| 三条 pipeline（上层） | cross-review、plan-cross-review、plan-to-implement：按固定角色和阶段编排多个会话 |

## 二、新流程里有哪些会话，由谁启动

| 会话 | 谁启动 | 怎样拿回结果 | 需要 Agent Lord 吗 |
|---|---|---|---|
| 定义 session | 你 | — | 不需要，要你逐轮回答 |
| 查漏（core-spec 第 7 步） | 定义 session 用另一家模型的 CLI 启动（`codex exec` / `claude -p`） | 报告写到文件，定义 session 读回 | 不需要，是会话内的一次命令调用 |
| owner（deliver） | 你开新 session 运行 `/deliver`；也可以由 Agent Lord 派发 | 汇报与 MR | 有人在场时不需要 |
| 独立验证与复验 | owner 用 CLI 启动，验证说明是固定文件，不由 owner 临时写 | 报告写到文件；`check-delivery.mjs` 核对报告对应 MR 最终 head、没有 FAIL | 不需要 |
| CI 与评审跟进 | owner 在会话内有界等待（Archon：约 5 分钟查一次，CI 通过就停） | — | 不需要 |

所以单个需求**内部**的调度都在 owner 自己手里，这和三家一致：
- OpenAI 让一个 Codex 运行自己审查、请其他 agent 评审、处理反馈（S1）；
- Anthropic 让主 session 开 subagent 复查（S7）；
- Lauren 让每个 PR 的 owner 自己开 subagent（L1 `autopilot-full`）。

## 三、会话自己做不到、需要会话外一方的事

| 需求 | 为什么会话内做不到 | 三家怎样做 | Agent Lord 现有能力 | 还差什么 |
|---|---|---|---|---|
| 1. 会话死了能被发现并接上（401、额度、进程崩溃、上下文耗尽） | 会话死了不会自己报警。goal-v2 run-02 主会话遇到 401 后闲置约 55 小时 | OpenAI Symphony 定期对账，重启卡住的运行；Anthropic Managed Agents 把会话日志和运行环境分开，从日志恢复；Lauren 的 root 约每 30 分钟巡查一次 | `recover`、换会话接续、30 分钟未收结果提醒 | ① 看管方自己也是一个会话，它死了只剩提醒，不会自动接续；② 判断"卡住"依据的是进程状态，看不出"活着但没进展"。Lauren 是按实际产出判断：提交、推送、PR 变化；③ 换会话时应该直接用 `/deliver` 加 plan.md 接续（S6：只读 plan.md 就能重启），不必另写交接材料 |
| 2. 无人值守地并行跑多个需求 | 需要一个在会话外的起点，给每个需求一个 owner 和一个工作区 | S1 多 worktree 并行；Symphony 每个 issue 一个工作区；Lauren 每个 PR 一个 owner | 多任务派发、worktree 隔离、写租约 | 基本够用 |
| 3. 独立验证由作者以外的一方发起（可选） | owner 选择什么时候验、验哪个 head | Lauren 的 root 负责验证，owner 不自己判定 | 可以派发验证任务 | 目前用固定的验证说明加机械检查代替。试跑中如果发现 owner 挑着验，再交给 Agent Lord |

## 四、结论与建议

**角色从"编排器"改为"会话外的看管与派发层"。**
- v0.6 定的是"编排放在 Agent Lord，由节点加载对应 Skill"。v0.7 推倒重来之后，单个需求内部的编排已经交给 deliver 的 owner。
- Agent Lord 只保留三件事：会话外的存活看管与接续、多需求并行派发，以及以后可能需要的"作者以外的一方发起验证"。

**还有必要存在，但不在主路径上。**

| 用法 | 用不用 Agent Lord |
|---|---|
| 单个需求，你在场 | 不用。你开 owner session 跑 `/deliver` |
| 单个需求，你要离开很久 | 用。它派发 owner，看管，出错时接续，结果没收走时提醒你 |
| 多个需求同时跑 | 用。每个需求一个 owner、一个 worktree |

**不自己另建一套看管。** Agent Lord 已经有派发、恢复、换会话、隔离和提醒，另起一套（例如用定时任务巡查）是重复建设。

**三条 pipeline：**
- plan-cross-review 和 plan-to-implement 已被 core-spec 加 deliver 替代，试跑结束后删除；
- cross-review 的默认用途已被 deliver 的独立验证替代；高风险 MR 要不要保留它作为可以点名使用的额外评审，由你决定。

**要让 Agent Lord 胜任看管层，建议补三处**（放在试跑之后，按试跑中遇到的问题做）：
1. 派发 deliver 的做法：派发时给出 `/deliver` 和 spec、verify 路径，按依赖约定传入 deliver 与 core-spec 的解析路径；换会话时直接让新会话按 plan.md 和 git 历史接续。
2. 按产出判断停滞：plan.md 的进度、提交、MR 状态在一段时间内都没有变化时，视为卡住，先提醒，再按授权换会话。依据 L1 root 的巡查方式。
3. Skill 依赖表加入 core-spec、deliver。

## 五、待你决定

1. 是否确认 Agent Lord 的新角色：会话外的看管与派发层，不再编排需求内部的步骤。
2. 高风险 MR 是否保留 cross-review 作为可以点名使用的额外评审。
3. 第一次试跑是否先不用 Agent Lord：由你在场跑一个需求，遇到会话中断或需要离开时再启用。
