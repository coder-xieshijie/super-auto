---
source: 子代理核对（general-purpose），2026-10-01；只读原文存档，引文逐字核对
scope: OpenAI 原文对 MR 7595（Goal v2 迁移与 11 项反馈修复）交付复盘归纳出的 16 条流程优化方向（O1–O16）的态度；另列原文有、16 条未覆盖、与长时间无人值守交付、人工介入、验收口径相关的做法
---

# OpenAI 原文核对：16 条流程优化方向

## 核对方法

只读下面 11 份本机存档，没有联网，没有改动其他文件。文中每段英文引文都用 Python 脚本核对过：把原文和引文里的连续空白压成一个空格后做子串匹配，全部在对应文件里逐字找到，且每段只出现一次。行号是原文件的实际行号，跨行写成 `L1096-1098`；小节标题取引文上方最近的标题。"另见"后面只给位置、不引原句的地方，也用同一脚本核对过原句。

上一轮核对（`research/goal-final-delivery-trace-2026-09-30/source-check/openai.md`）只当作线索，本文引文全部重新核对。

文件简称：

- `HE` harness-engineering.md
- `PR` codex-prompting.md
- `LRW` codex-long-running-work.md
- `LH` run-long-horizon-tasks-with-codex.md
- `SUB` codex-subagents.md
- `ORC` orchestration-and-handoffs.md
- `AST` rethinking-skills-and-prompts-for-gpt-6-astra.md
- `G6` using-gpt-6.md

以上 8 份在 `/Users/minimax/code/github/xieshijie/dev-skills/skills/agent-prompt-rules/references/sources/openai/`。另外三份：

- `PL` `/Users/minimax/code/github/xieshijie/super-auto/research/self-verifying-loop-2026-09-28/raw/codex-exec-plans.md`
- `A04` `/Users/minimax/code/github/xieshijie/super-auto/research/agent-delivery-2026-09-28/raw/architecture/A04-openai-symphony.md`
- `A05` 同目录下的 `A05-symphony-spec.md`

## 态度一览

| 编号 | 方向 | 态度 |
|---|---|---|
| O1 | 流程更新不打断在途交付 | 部分支持，部分相反 |
| O2 | 等人的问题不无限挂起 | 支持 |
| O3 | 降低交付中修改 verify 的成本 | 部分支持 |
| O4 | 冻结前核实验证可行性 | 支持 |
| O5 | 验证环境不需要人 | 支持 |
| O6 | 质量命令按 CI 选 | 部分支持 |
| O7 | 里程碑检查的审查与场景运行并行 | 支持（原则层面） |
| O8 | 计划里的时间要可核对 | 支持 |
| O9 | 主会话做协调、大块实现交给子代理 | 部分支持 |
| O10 | 长时间等待时给出状态和预计时间 | 部分支持 |
| O11 | 给用户的问题写得通俗 | 支持 |
| O12 | 定义阶段先查事实再提问 | 支持 |
| O13 | 默认决定成批列出 | 支持（"成批列出"这一形式未涉及） |
| O14 | 最后一次 rebase 的风险前移 | 部分支持（方向一致，做法不同） |
| O15 | 证据精简入库 | 支持 |
| O16 | 门禁报错写明修法 | 支持 |

与建议相反或有明显出入的地方集中在 O1（原文让流程改动自动作用于之后的会话，不按"是否阻塞"过滤，也不由 owner 自己拉取）、O6（原文刻意减少阻塞性门禁，不支持在本地把 CI 全量复制一遍）、O9（原文提醒并行写代码有冲突成本，长任务的主要手段是写进文件的项目记忆）、O14（原文靠短命 PR 和系统随时 rebase，依赖建成阻塞关系）。

---

## O1 流程更新不打断在途交付 —— 部分支持，部分相反

- 「Tool specs, adapter selection, and effective tracker settings MUST be bound to one session snapshot. A workflow reload applies to future sessions; it MUST NOT make an in-flight session advertise one provider and execute another.」（A05 L1096-1098，§10.5 Approval, Tool Calls, and User Input Policy）
  - 支持"在途会话绑定开工时的版本"；A05 L571-572（§6.2）还写明不要求在配置变化时自动重启在途会话。但 Symphony 绑定的单位是一个会话：同一 issue 的下一个会话就用新版本（A05 L565 要求检测到 WORKFLOW.md 变化后不重启就重新读取并应用），整个需求并不锁在开工时的版本上。
- 「**Queue** saves the message for the next run. Use it for a follow-up that should wait until the current work finishes.」（PR L135-136，Steering and queuing）
  - 支持"投递不用中断"。Codex 把运行中追加的消息分成 Steer（并入当前轮）和 Queue（留到下一轮），两种都不需要停止当前回合；G6 L18 的 mid-turn steering 也写明更新并入续写，已完成的工作保留。
- 「Reloaded config applies to future dispatch, retry scheduling, reconciliation decisions, hook execution, and agent launches.」（A05 L569-570，§6.2 Dynamic Reload Semantics）
  - 这条与建议的后两点相反：新配置由运行时自动作用于之后的派发、重试和启动，不区分是否阻塞本次交付；加载也由运行时完成，不是 owner 在里程碑边界跑脚本比对后自己拉取。A05 L1710 把"编辑 WORKFLOW.md"列为操作者的常规干预方式，L1716-1717 说重启才不是应用配置变更的常规路径。
- 另见：SUB L324 的 `agents.interrupt_message` 配置，回合被中断时由运行时给模型留一条可见消息。本次 owner 把中断当成用户拒绝，原文的处理是由运行时告诉模型"这是中断"，而不是让模型自己推断。

## O2 等人的问题不无限挂起 —— 支持

- 「Approval requests and user-input-required events MUST NOT leave a run stalled indefinitely. An implementation MAY either satisfy them, surface them to an operator, auto-resolve them, or fail the run according to its documented policy.」（A05 L1073-1075，§10.5 Approval, Tool Calls, and User Input Policy）
  - 直接支持"无人值守时等待用户输入要有策略"：规格把它列为必须项，并给出四种可选处理。
- 「When implementing an executable specification (ExecPlan), do not prompt the user for "next steps"; simply proceed to the next milestone.」「Resolve ambiguities autonomously, and commit frequently.」（PL L34，How to use ExecPlans and PLANS.md）
  - 支持"写明默认做法并继续"。执行顺序这类问题属于这里说的 next steps 和歧义，原文要求自己定、继续做。
- 「Treat user-input-required turns as hard failure.」（A05 L1081，§10.5，Example high-trust behavior）
  - 这是规格给的高信任示例：遇到需要用户输入的回合直接判失败，而不是带默认值继续。原文接受"失败并上报"作为无人值守的一种策略；交互式的 Goal 模式则是"pauses when it needs a decision"（LRW L112-113）。所以"继续"只适用于不属于停下情况的问题，这与建议的划分一致。

## O3 降低交付中修改 verify 的成本 —— 部分支持

- 「record decisions in a log in the spec for posterity; it should be unambiguously clear why any change to the specification was made.」（PL L36，How to use ExecPlans and PLANS.md）
  - 支持"记录为什么改、谁确认的"：Decision Log 模板里有 `Date/Author` 一栏（PL L133，Skeleton / Decision Log）。
- 「When you revise a plan, you must ensure your changes are comprehensively reflected across all sections, including the living document sections, and you must write a note at the bottom of the plan describing the change and the reason why.」（PL L175，PLANS.md 结尾段，位于 Skeleton of a Good ExecPlan 之后）
  - 支持把重新冻结做成一个动作，一次改全所有相关位置。原文只对计划文档提要求，没有提到提交、MR 描述哈希或交接文件。
- 「The goal text becomes both the first prompt and the completion criteria for the task.」（LRW L46-48，Start a goal）
  - 这条说明原文没有"冻结、重新冻结"这道程序：Goal 模式下 goal 文本就是完成标准，用户在运行中可以直接编辑 goal（LRW L78-79）。原文降低改口径成本的方式是把编辑做成一个界面操作，比建议更轻。"改动部分仍由另一家模型查漏"原文未涉及；"同一类问题一次列全"最接近的是 PR L267 示例 prompt 里的一句：在产出最终文件前先标出缺失的决定。

## O4 冻结前核实验证可行性 —— 支持

- 「When researching a design with challenging requirements or significant unknowns, use milestones to implement proof of concepts, "toy implementations", etc., that allow validating whether the user's proposal is feasible.」（PL L38，How to use ExecPlans and PLANS.md）
  - 直接支持：方案有重大未知时，先用概念验证确认可行。
- 「consider creating spikes that evaluate the feasibility of these features _independently_ of one another, proving that the external library performs as expected and implements the features we need in isolation.」（PL L96，Prototyping milestones and parallel implementations）
  - 支持对外部依赖单独试探；"测试台能否覆盖测试账号"属于同一类问题。出入：原文把试探作为计划里的"原型里程碑"，并写明保留或丢弃的标准（PL L94），没有"冻结"这一关，因此没有"冻结前还是开工后"的区分。
- 「The core `attempt` value does not distinguish a normal continuation from an error/timeout/stall retry.」（A05 L1348-1349，§12.3 Retry/Continuation Semantics）
  - 与"没核实观测源在中断、失败下记什么"相关：规格把某个字段区分不了哪些情况直接写出来，使用者不用自己猜。"两个观测源相互核对"原文未涉及；做不到的真实集成检查，原文要求标为跳过，不能当作通过（A05 L2200）。

## O5 验证环境不需要人 —— 支持

- 「Codex works on a fully isolated version of that app—including its logs and metrics, which get torn down once that task is complete.」（HE L45，Increasing application legibility）
  - 支持"每个实例独立"和"清理由工具做"：每个 worktree 一个隔离的应用实例（HE L43），日志和指标随任务结束拆除。清理是环境自带的，不靠 agent 手写删除命令。
- 「In non-interactive flows, or whenever a run can't surface a fresh approval, an action that needs new approval fails and Codex surfaces the error back to the parent workflow.」（SUB L261-263，Approvals and sandbox controls）
  - 支持"审批不让无人值守的运行挂起"：Codex 在不能弹出审批时直接失败并把错误交回上层，不等待。
- 「The local tests use disposable fixtures and have no production access. Run them, fix failures caused by the requested change, and rerun affected tests without asking for approval at each step.」（AST L47，Up-to-date AGENTS.md）
  - 原文的另一种做法是对已知安全的流程预先授权。限制：A05 L1774-1776 提醒权限放得过宽会导致数据泄露或破坏性修改，所以方向是把危险操作收进范围明确的工具或明确授权，而不是整体关掉审批。共享登录导致 401 的问题，原文最接近的是"不要让两个任务同时写同一个连接的数据源"（LRW L22）和"真实集成测试使用隔离的测试标识和工作区"（A05 L2198-2199）。

## O6 质量命令按 CI 选 —— 部分支持

- 「Run tests appropriate to the change and complete required checks.」（G6 L132，Testing and verification）
  - 支持"按改动选，但必需的检查要做完"。
- 「If you have a standard check pipeline, ask it to run it:」「After the fix, run lint + the smallest relevant test suite. Report the commands and results.」（PR L386、L389，Fix a bug / CLI workflow）
  - 原文的写法是有标准检查流水线就跑它，否则跑 lint 和最小的相关测试。"跑标准流水线"与"按 CI 选"一致；本地检查集与 CI 逐项对齐，原文未涉及。
- 「The repository operates with minimal blocking merge gates. Pull requests are short-lived. Test flakes are often addressed with follow-up runs rather than blocking progress indefinitely.」（HE L114，Throughput changes the merge philosophy）
  - 这条限制建议的前半部分：OpenAI 这个仓库刻意减少阻塞性门禁，理由是改错便宜、等待昂贵（同段）。它支持"尽早推送、读流水线结果"（HE L151 也把"发现并修复构建失败"列为 agent 自己的步骤），不支持在本地把 CI 全量复制一遍再推。

## O7 里程碑检查的代码审查与场景运行并行 —— 支持（原则层面）

- 「As a starting point, use parallel agents for read-heavy tasks such as exploration, tests, triage, and summarization.」（SUB L81-82，Why subagent workflows help）
  - 代码审查和场景运行都以读为主，原文建议这类工作并行。
- 「Review this branch with parallel subagents. Spawn one subagent for security risks, one for test gaps, and one for maintainability. Wait for all three, then summarize the findings by category with file references.」（SUB L117，Triggering subagent workflows）
  - 原文示例就是把审查拆成并行子代理，全部返回后汇总。
- 「If at any point you can parallelize work by delegating tasks to another agent (no matter if you are the root or subagent), you should do so using collaboration tools if it could save time or improve quality.」（G6 L114，Subagent delegation）
  - 支持在能省时间时主动并行。限制：并行不改变"验证失败先修再往下走"（LH L110），审查找出代码问题后相关场景仍要重跑。审查与场景运行的先后，原文未涉及。

## O8 计划里的时间要可核对 —— 支持

- 「This section must always reflect the actual current state of the work.」（PL L112，Skeleton / Progress）
  - Progress 必须反映实际状态，估计时间不符合这条。
- 「Use timestamps to measure rates of progress.」（PL L118，Skeleton / Progress）
  - 原文在 Progress 每步前加带时区的时间戳（示例格式见 PL L114），用来衡量进度快慢。原文没有提到用脚本核对。
- 「The app-server client emits structured events to the orchestrator callback. Each event SHOULD include:」「`timestamp` (UTC timestamp)」（A05 L1041-1042、L1045，§10.4 Emitted Runtime Events）
  - Symphony 的时间来自运行时事件自带的时间戳，不靠 agent 填写。照这个做法，比"核对估计值"更直接的是让脚本从提交记录或会话日志里取时间写进 plan。

## O9 主会话做协调、大块实现交给子代理 —— 部分支持

- 「If you flood the main chat (where you're defining requirements, constraints, and decisions) with noisy intermediate output such as exploration notes, test logs, stack traces, and command output, the session can become less reliable over time.」（SUB L60，Why subagent workflows help）
  - 支持建议的动因。原文的做法是主会话只管需求、决定和最终输出（SUB L71），子代理只交回摘要（SUB L73）；Codex 内置的 `worker` 角色就是做实现和修复的子代理（SUB L284）。
- 「Be more careful with parallel write-heavy workflows, because agents editing code at once can create conflicts and increase coordination overhead.」（SUB L82-84，Why subagent workflows help）
  - 限制：原文推荐的起点是读为主的工作，多个代理同时改代码有冲突和协调成本。大块实现交给子代理时，原文的提醒指向串行交付或按文件划清范围。
- 「ExecPlans are living documents, and it should always be possible to restart from _only_ the ExecPlan and no other work.」（PL L36，How to use ExecPlans and PLANS.md）
  - 原文处理长任务上下文的主要手段是写进文件的项目记忆：LH 的单次运行约 25 小时、约 1300 万 token（LH L7），靠的是规格、计划、状态文件（LH L83），没有用子代理。也就是说，压缩本身不是要避免的事，压缩后能否只凭 plan 恢复才是关键。ORC L104 也建议能用一个 agent 时先用一个。

## O10 长时间等待时给出状态和预计时间 —— 部分支持

- 「Use a side chat when you want a status recap or an explanation without interrupting the main chat.」（LRW L82-83，Steer a running goal）
  - 原文的状态是用户来问时给，并且不打断主任务。
- 「The returned document SHOULD depict the current state of the system (for example active sessions, retry delays, token consumption, runtime totals, recent events, and health/error indicators).」（A05 L1491-1492，§13.7.1 Human-Readable Dashboard）
  - Symphony 把状态放在运行时的状态页上，用户随时能看，不依赖 agent 在对话里汇报。ChatGPT 桌面端还用通知告诉用户何时需要输入或可以审阅（LRW L128-129）。
- 「Retry queue entries include attempt, due time, identifier, and error」（A05 L2134，§17.4 Orchestrator Dispatch, Reconciliation, and Retry）
  - 原文里唯一接近"预计时间"的是重试队列记下次运行时间。agent 主动在对话中报告状态和预计耗时，原文未涉及；原文的方向是由运行时提供状态。

## O11 给用户的问题写得通俗 —— 支持

- 「Use plain language over jargon, and reference technical details only to the degree that it helps illustrate an idea or your work to the user.」（G6 L98，Personality and writing style）
  - 直接支持：少用术语，技术细节只在有助于说明时出现。
- 「Make sure to state the main point clearly and early, then develop it with the explanation and detail the reader needs.」（G6 L92，Personality and writing style）
  - 对应"问题不要以内部编号和术语开头"：先说要点。
- 「Every ExecPlan must define every term of art in plain language or do not use it.」（PL L48，Requirements）
  - 术语要么用平实语言定义，要么不用。G6 L106 还要求避免自造的复合标签。

## O12 定义阶段先查事实再提问 —— 支持

- 「Before asking the user clarifying questions, you should complete the work that is already authorized from context and necessary to make the proposed action concrete and reviewable.」（G6 L62，Initiative and follow-through）
  - 问用户之前，先把已授权、能让问题变具体的工作做完；代码核对属于这类工作。
- 「A good subagent prompt should explain how to divide the work, whether Codex should wait for all agents before continuing, and what summary or output to return.」（SUB L112-114，Triggering subagent workflows）
  - 派子任务时要写明是否等全部返回再继续。第一轮问题在核对子任务返回前发出，正是没有写明"等待"的情形。
- 「Be thorough in reading (and re-reading) source material to produce an accurate specification.」（PL L32，How to use ExecPlans and PLANS.md）
  - 写规格前要反复读原始材料。

## O13 默认决定成批列出 —— 支持（"成批列出"这一形式未涉及）

- 「Do not outsource key decisions to the reader. When ambiguity exists, resolve it in the plan itself and explain why you chose that path.」（PL L66，Guidelines）
  - 有歧义时自己定下并写明理由，不推给读者。
- 「When instructions leave room for interpretation, it uses the context it has to fill in routine gaps and asks focused questions when the answer could change the outcome.」（G6 L11，Introduction）
  - 只有答案会改变结果时才问。约 45 个问题里约 36 个直接采纳推荐，说明多数属于可以用上下文补上的常规空缺。
- 「The model also likes to ask non-blocking questions as it’s working by default, so adjust these prompts to match the level of autonomy your application needs.」（G6 L67，Initiative and follow-through）
  - 原文指出模型默认会问不阻塞的问题，需要用 prompt 调整。"成批列出默认决定"的形式原文未涉及，最接近的是"让用户审批一个具体、可审阅的结果"（G6 L62）。

## O14 最后一次 rebase 的风险前移 —— 部分支持（方向一致，做法不同）

- 「The system watches CI, rebases when needed, resolves conflicts, retries flaky checks, and generally shepherds changes through the pipeline.」（A04 L104，An increase in exploration from working this way）
  - 支持"不要把同步基线攒到最后"。原文是系统随时 rebase、解决冲突，不是"定期试 rebase 并记录冲突"。
- 「Pull requests are short-lived.」（HE L114，Throughput changes the merge philosophy）
  - 原文减少基线漂移的前提是 PR 存活时间短。本需求是长周期 MR，与这个前提不同。
- 「Agents only start working on tasks that aren’t blocked, so execution unfolds naturally and optimally in parallel for this DAG (a sequence of execution steps).」（A04 L86，Turning our issue tracker into an agent orchestrator）
  - Symphony 把依赖建成任务之间的阻塞关系，被阻塞的任务不开工。这与本需求"基于未合入的 IDL MR 开发、合入前再对齐"的做法不同（用户的全局规则允许这样做），所以对"依赖 MR 未合入"这一点，原文只提供对照，不直接支持定期试 rebase。

## O15 证据精简入库 —— 支持

- 「Keep them concise and focused on what proves success. If you need to include a patch, prefer file-scoped diffs or small excerpts that a reader can recreate by following your instructions rather than pasting large blobs.」（PL L76，Guidelines）
  - 证据只留能证明成功的简短片段，不贴大块内容。
- 「Avoid logging large raw payloads unless necessary.」（A05 L1377，§13.1 Logging Conventions）
  - 日志同样避免记录大块原始数据。
- 「put it in progress so the PM knows it’s being worked on, add the PR, move it to the **Review** status, attach videos, etc.」（A04 L146，Using Symphony to build Symphony）
  - Symphony 的演示视频挂在任务单上，不进代码仓库；HE L45 的日志和指标在任务结束时拆除。限制：HE L80 说 agent 在运行中看不到的东西等于不存在，所以结论和精简证据仍应入库，截图、jsonl 这类大文件放在仓库外并留链接。

## O16 门禁报错写明修法 —— 支持

- 「Because the lints are custom, we write the error messages to inject remediation instructions into agent context.」（HE L100，Enforcing architecture and taste）
  - 直接支持：自定义检查的报错信息里写修复方法，送进 agent 上下文。
- 「When documentation falls short, we promote the rule into code」（HE L108，Enforcing architecture and taste）
  - 原文的顺序是文档不够时把规则升级成代码。按这个顺序，规则进了门禁后报错本身要带修法；SKILL 正文是否也写这条，原文没有要求。
- 「“what capability is missing, and how do we make it both legible and enforceable for the agent?”」（HE L33，Redefining the role of the engineer）
  - 规则既要让 agent 看得见，也要能强制。"并行子代理在别的分支上的提交是否应计入"属于门禁规则本身是否合理，原文未涉及。

---

## 16 条未覆盖、原文有的相关做法（5 条）

1. **停滞由运行时按静默时长判定，并区分终止原因。** 与本次 owner 停 10.5 小时、21 分钟无输出相关：原文不靠人发现停滞，由编排进程计时后终止并重试。
   - 「If `elapsed_ms > codex.stall_timeout_ms`, terminate the worker and queue a retry.」（A05 L828，§8.5 Active Run Reconciliation）
   - 「`codex.turn_timeout_ms`: maximum silence interval while a turn stream is active; each app-server output resets it, so it is not a total turn runtime cap」（A05 L1147-1148，§10.6 Timeouts and Error Mapping）
   - 「Distinct terminal reasons are important because retry logic and logs differ.」（A05 L692，§7.2 Run Attempt Lifecycle）

2. **人工介入点放在任务状态上，不放在会话中途。** 成功的运行可以停在"Human Review"这样的交接状态；操作者通过改任务状态来停止会话，不需要向在途会话塞消息。
   - 「A successful run can end at a workflow-defined handoff state (for example `Human Review`), not necessarily `Done`.」（A05 L43-44，§1 Problem Statement）
   - 「Changing issue states in the tracker:」「non-active state -> running session is stopped without cleanup」（A05 L1713、L1715，§14.4 Operator Intervention Points）

3. **只在需要判断时上报人；中途"停下等审阅"的要求会让模型更早停。** 与里程碑检查、冻结交接等人工节点的设计有关：每加一个停下审阅的点，都要先确认这个决定确实需要人来做。
   - 「Escalate to a human only when judgment is required」（HE L152，Increasing levels of autonomy）
   - 「A requirement to stop for review after the first implementation will pull the model toward an earlier stopping point, so check whether that's a decision you actually need to make.」（AST L59，Persistence）

4. **验收写成人能核对的行为，不写内部属性。** 与本次 3 处验收口径和 spec 冲突有关：口径写成可观察的输入和输出，更容易在冻结前发现冲突。
   - 「Acceptance should be phrased as behavior a human can verify」「rather than internal attributes ("added a HealthCheck struct").」（PL L68，Guidelines）

5. **skill 导致停顿时，要求模型指出是哪个文件的哪条规则；用户指令优先于 skill。** 与 O1 中 owner 停 10.5 小时有关：这样停下时能看出是哪条流程规则在起作用。
   - 「If a skill causes you to ask for permission or confirmation, pause, leave requested work unfinished, or diverge from the user's intent, name and link to the exact SKILL.md file you read, quote the relevant instruction, and briefly explain how it applies.」（G6 L80，Instruction following）
   - 「The user's instructions take precedence over guidelines provided in a skill.」（G6 L74，Instruction following）
