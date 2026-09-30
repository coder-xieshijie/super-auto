---
source: 子代理核对（general-purpose，claude-opus-5-5），2026-09-30；只读原文存档，引文由子代理用脚本核对逐字存在
scope: OpenAI 原文对 24 条建议的态度
---

## OpenAI 原文逐条核对：24 条流程改进建议

我读完了 11 份原文。下面引用的每段英文都用脚本核对过：空白规范化后能在原文件里逐字找到。行号按文件的实际行数计。没有改动任何文件。

**文件简称**
- `HE` harness-engineering.md
- `PR` codex-prompting.md
- `LRW` codex-long-running-work.md
- `LH` run-long-horizon-tasks-with-codex.md
- `SUB` codex-subagents.md
- `ORC` orchestration-and-handoffs.md
- `AST` rethinking-skills-and-prompts-for-gpt-6-astra.md
- `G6` using-gpt-6.md

以上 8 份都在 `/Users/minimax/code/github/xieshijie/dev-skills/skills/agent-prompt-rules/references/sources/openai/` 下。另外三份：
- `PL` = `/Users/minimax/code/github/xieshijie/super-auto/research/self-verifying-loop-2026-09-28/raw/codex-exec-plans.md`
- `A04` 和 `A05` = `/Users/minimax/code/github/xieshijie/super-auto/research/agent-delivery-2026-09-28/raw/architecture/` 下的 A04-openai-symphony.md 和 A05-symphony-spec.md

**"prompt 少、规则进代码"这个原则本身，OpenAI 原文有直接依据：**
- 「give Codex a map, not a 1,000-page instruction manual.」（HE L51，We made repository knowledge the system of record）
- 「Focus on the one or two boundaries that matter most. You don't need to control every step ChatGPT takes.」（PR L96-97，Set boundaries that prevent real problems）
- 「When documentation falls short, we promote the rule into code」（HE L108，Enforcing architecture and taste）

---

### A 定义阶段

**A1 部分支持。** 原文支持在开工前讲清约束和边界、明确完成标准；结果不清楚时先让模型访谈用户。"第 0 轮"这个顺序和五项清单原文没有涉及。原文同时提醒两点：边界只写最要紧的一两条；过去为约束旧模型写的强硬边界，会让新模型提前停下。
- 「If the outcome is still unclear, start with `/plan`. Ask ChatGPT to interview you, identify constraints, and turn the result into a goal with measurable success criteria.」（LRW L50-52，Start a goal）
- 「Name required tools, boundaries, compatibility needs, or approaches to avoid.」（LRW L64，Define what done means）
- 「Astra could take it too seriously and may stop work where you'd actually be happy for it to continue.」（AST L53，Decision boundaries）

**A2 支持。** 原文的做法是：模型自己决定实现细节并写明理由，只在答案会改变结果时才问用户；讲解时多写用户可见的影响。"成批列出默认决定"这个形式原文没有涉及。
- 「Do not outsource key decisions to the reader. When ambiguity exists, resolve it in the plan itself and explain why you chose that path. Err on the side of over-explaining user-visible effects and under-specifying incidental implementation details.」（PL L66，Guidelines）
- 「When instructions leave room for interpretation, it uses the context it has to fill in routine gaps and asks focused questions when the answer could change the outcome.」（G6 L11，Introduction）

**A3 支持。** 原文要求先把已授权的工作做完、让提议可供审阅，再问用户。探查类 agent 要引用文件和符号；派子任务时要写明是否等子任务全部返回。注意原文说的是"文件和符号"，没有专门要求行号。
- 「Before asking the user clarifying questions, you should complete the work that is already authorized from context and necessary to make the proposed action concrete and reviewable. The user should be approving a concrete, reviewable result.」（G6 L62，Initiative and follow-through）
- 「Trace the real execution path, cite files and symbols, and avoid proposing fixes unless the parent agent asks for them.」（SUB L379，Example 1: PR review）
- 「A good subagent prompt should explain how to divide the work, whether Codex should wait for all agents before continuing, and what summary or output to return.」（SUB L112-114，Triggering subagent workflows）

**A4 支持。** 原文要求每项验收写明预期输出，好区分成功和失败。工具做不到时，原文的处理是把它当成"缺少的能力"去补；跳过的检查要标成跳过，不能算通过。
- 「Include expected outputs and error messages so a novice can tell success from failure.」（PL L74，Guidelines）
- 「“what capability is missing, and how do we make it both legible and enforceable for the agent?”」（HE L33，Redefining the role of the engineer）
- 「A skipped real-integration test SHOULD be reported as skipped, not silently treated as passed.」（A05 L2200，§17.8）

**A5 间接支持。** 原则一致：要能演示出可工作的行为，内部改动除了"改前失败、改后通过"的测试，也要给出一个用上新行为的场景。"冻结时单列给用户确认"这个形式原文没有涉及。
- 「Every ExecPlan must produce a demonstrably working behavior, not merely code changes to "meet a definition".」（PL L47，Requirements）
- 「If a change is internal, explain how its impact can still be demonstrated (for example, by running tests that fail before and pass after, and by showing a scenario that uses the new behavior).」（PL L68，Guidelines）
- 「The bar for this run was not "it compiles"; it was "does it follow the instructions, and does it actually work?"」（LH L162，What the agent built）

**A6 部分支持。** 原文限制改动范围的方式是运行手册条目和 agent 指令，另有一个用户 prompt 示例要求计划写明每个里程碑移动哪些文件。被机械强制的是架构不变量，没有"允许路径白名单"。原文还提醒：强制边界，不要细管实现。
- 「Keep diffs scoped (don’t expand scope)」（LH L126，Implement.md）
- 「specify exactly which files move in each milestone」（PR L560，Delegate refactor to the cloud）
- 「By enforcing invariants, not micromanaging implementations, we let agents ship fast without undermining the foundation.」（HE L92，Enforcing architecture and taste）

### B 交付阶段

**B1 支持，附一条格式提醒。** 原文的计划要求每个里程碑有验收标准和验证命令，失败先修再往下走。但原文规定勾选框只放在 `Progress` 区段，里程碑本身用叙述写，不要写成官样清单。
- 「Acceptance criteria + validation commands per milestone」「Stop-and-fix rule: if validation fails, repair before moving on」（LH L109-110，Plan.md）
- 「Checklists are permitted only in the `Progress` section, where they are mandatory.」（PL L60，Formatting）
- 「Milestones are narrative, not bureaucracy.」（PL L80，Milestones）

**B2 部分支持。** "提交前必须处理完检查结果"这个门槛与原文的 stop-and-fix 一致。检查属于读为主的工作，放到后台并行也有依据。但原文的写法比 B2 更严："修完再继续"。检查还在跑时就推进下一个里程碑，原文没有涉及。
- 「After milestones, it ran verification commands and repaired failures before continuing.」（LH L150，Verification at every milestone）
- 「As a starting point, use parallel agents for read-heavy tasks such as exploration, tests, triage, and summarization.」（SUB L81-82，Why subagent workflows help）
- 「In a system where agent throughput far exceeds human attention, corrections are cheap, and waiting is expensive.」（HE L114，Throughput changes the merge philosophy）

**B3 原则上支持。** 原文把规则交给 lint 和 CI 机械校验。按 commit 范围核对报告覆盖，原文没有涉及。
- 「We enforce this mechanically. Dedicated linters and CI jobs validate that the knowledge base is up to date, cross-linked, and structured correctly.」（HE L72，We made repository knowledge the system of record）
- 「Use timestamps to measure rates of progress.」（PL L118，Skeleton / Progress）

**B4 支持放宽。** 在 Codex 里，"继承推理强度"是没配置时运行时的默认行为；原文还说不同 agent 本来就该用不同设置。原文的做法是在配置层显式设定，而不是事后核对。原文只讲 Codex，没讲其他厂商的 subagent。
- 「If you don't configure a subagent model or `model_reasoning_effort`, the subagent inherits the parent agent's model and reasoning effort.」（SUB L137-138，Choosing models and reasoning）
- 「Different agents need different model and reasoning settings.」（SUB L122）
- 「To balance intelligence, speed, and price for each task, request a specific model or reasoning effort in your prompt, configure `[agents]` defaults in `config.toml`, or set `model` and `model_reasoning_effort` directly in the custom agent file.」（SUB L141-144）

**B5 支持：等待和超时由运行时承担。** Symphony 的定时轮询和重试计时器都在编排进程里，不靠模型自己约定唤醒。模型自己排定唤醒，或者口头承诺"几分钟后再看"，原文没有涉及。
- 「Your application still executes the tool and manages pending work.」（G6 L17，What's new）
- 「The system watches CI, rebases when needed, resolves conflicts, retries flaky checks, and generally shepherds changes through the pipeline.」（A04 L104，An increase in exploration...）
- 「Hook timeouts are REQUIRED to avoid hanging the orchestrator.」（A05 L1769，§15.4）

**B6 部分支持。** 原文的状态放在持久文件（documentation.md / Progress）和运行时状态界面里；聊天中的状态是用户主动来问的。主动发一句状态，以及其中"预计多久、超时怎么办"，原文没有涉及。
- 「This is the shared memory and audit log. It’s how I can step away for hours and still understand what happened.」（LH L133，Documentation.md）
- 「Current milestone status (what’s done, what’s next)」（LH L137）
- 「Use a side chat when you want a status recap or an explanation without interrupting the main chat.」（LRW L82-83，Steer a running goal）

**B7 原则上支持。** 原文用自定义 linter 和结构测试做机械强制。pre-commit 这个挂载点原文没有涉及。
- 「These constraints are enforced mechanically via custom linters (Codex-generated, of course!) and structural tests.」（HE L94，Enforcing architecture and taste）
- 「In a human-first workflow, these rules might feel pedantic or constraining. With agents, they become multipliers: once encoded, they apply everywhere at once.」（HE L102）

**B8 支持。** 原文要求步骤可以重复执行、命令写全。"独立验证复用同一个脚本"原文没有专门涉及。
- 「Be idempotent and safe. Write the steps so they can be run multiple times without causing damage or drift.」（PL L72，Guidelines）
- 「How to run + demo (commands + quick smoke tests)」（LH L139，Documentation.md）

**B9 支持。** 原文每项改动一个 worktree 实例，任务结束即拆除。注意原文的清理是运行时做的（终态触发清理、`before_remove` 钩子），不是靠人或 agent 照清单清理。
- 「we made the app bootable per git worktree, so Codex could launch and drive one instance per change.」（HE L43，Increasing application legibility）
- 「Codex works on a fully isolated version of that app—including its logs and metrics, which get torn down once that task is complete.」（HE L45）
- 「Startup terminal cleanup removes stale workspaces for issues already in terminal states.」（A05 L731，§7.4）

### C 验证工具

**C1 支持。** 原文的超时按"静默时长"计，每次有输出就重置；超过停滞时限就杀掉进程并排队重试；失败必须让操作者直接看得见。
- 「`codex.turn_timeout_ms`: maximum silence interval while a turn stream is active; each app-server output resets it, so it is not a total turn runtime cap」（A05 L1147-1148，§10.6）
- 「If `elapsed_ms > codex.stall_timeout_ms`, terminate the worker and queue a retry.」（A05 L828，§8.5）
- 「Operators MUST be able to see startup/validation/dispatch failures without attaching a debugger.」（A05 L1385，§13.2）

**C2 支持，并提醒预检保持轻量。**
- 「Validate configuration before starting the scheduling loop.」「If startup validation fails, fail startup and emit an operator-visible error.」（A05 L588-589，§6.3）
- 「A remote host SHOULD satisfy the same basic contract as a local worker environment: reachable shell, writable workspace root, coding-agent executable, and any required auth or repository prerequisites.」（A05 L2275-2277，Appendix A.1）
- 「It validates the workflow/config needed to poll and launch workers, not a full audit of all possible workflow behavior.」（A05 L582-584，§6.3）

**C3 支持做成显式、写进文档的配置项，但原文提示放宽沙箱有风险。**
- 「Implementations are expected to document their trust and safety posture explicitly. This specification does not require a single approval, sandbox, or operator-confirmation policy; some implementations target trusted environments with a high-trust configuration, while others require stricter approvals or sandboxing.」（A05 L31-34，§1）
- 「A permissive deployment can lead to data leaks, destructive mutations, or full machine compromise if the agent is induced to execute harmful commands or use overly-powerful integrations.」（A05 L1774-1776，§15.5）
- 显式设推理强度：「Use when an agent needs to trace complex logic, check assumptions, or work through edge cases (for example, reviewer or security-focused agents).」（SUB L167，Reasoning effort，`high` 条目）

**C4 支持收窄复验。** 原文对应"时间预算"的是运行时超时（见 C1），不是写进说明里。"沿用上次结论并写明依据"原文没有涉及。
- 「Run tests appropriate to the change and complete required checks. Once those pass, broaden or repeat testing only when new changes, failures, or unresolved concerns justify it; otherwise, continue toward completing the task.」（G6 L132，Testing and verification）
- 「After the fix, run lint + the smallest relevant test suite. Report the commands and results.」（PR L389，Fix a bug）
- 「Previous models needed encouragement to run tests and check their work. GPT-6 Astra does that on its own, so the same instructions can lead to unnecessary testing.」（AST L43）

**C5 原则上支持。** 原文要求统一的结构化记录，编排逻辑不依赖人读的文字。
- 「Structured logs with `issue_id`, `issue_identifier`, and `session_id`」（A05 L2230，§18.1）
- 「Do not make orchestrator logic depend on humanized strings.」（A05 L1457，§13.6）
- 「Add specialists only when they materially improve capability isolation, policy isolation, prompt clarity, or trace legibility.」（ORC L104）

### D 验证能力

**D1 原则上支持。** 原文避免多个并发单元同时写同一个共享资源，凭证集中由宿主持有。"刷新锁"原文没有涉及。
- 「avoid giving two tasks write access to the same connected source.」（LRW L22）
- 「The orchestrator serializes state mutations through one authority to avoid duplicate dispatch.」（A05 L727，§7.4）
- 「Tools execute in Symphony with the configured adapter credential; the child receives tool results, not a raw token.」（A05 L1316-1317，§11.5）

**D2 支持。**
- 「When the agent struggles, we treat it as a signal: identify what is missing—tools, guardrails, documentation—and feed it back into the repository, always by having Codex itself write the fix.」（HE L133）
- 「Instead of patching the result manually, we added guardrails and skills so the agents could succeed the next time.」（A04 L114，Progress comes with new, different problems）

**D3 原则上支持。** 原文让真实 UI 对 agent 可读、可驱动。注入固定消息历史原文没有涉及。
- 「We also wired the Chrome DevTools Protocol into the agent runtime and created skills for working with DOM snapshots, screenshots, and navigation. This enabled Codex to reproduce bugs, validate fixes, and reason about UI behavior directly.」（HE L43）

**D4 部分支持。** "按生产装配"这一点原文没有涉及。
- 「`Real Integration Profile`: environment-dependent smoke/integration checks RECOMMENDED before production use.」（A05 L2059-2060，§17）
- 「Real integration tests SHOULD use isolated test identifiers/workspaces and clean up tracker artifacts when practical.」（A05 L2198-2199）

**D5 支持，且原文做得更早：发现就立刻建 issue，不等需求结束。**
- 「When that happens, they simply file a new issue that we can evaluate and schedule later—many of these follow-up tasks also get picked up by agents.」（A04 L88）
- 「Active plans, completed plans, and known technical debt are all versioned and co-located, allowing agents to operate without relying on external context.」（HE L68）

### E 其他

**E1 原则上支持。** U+FFFD 这个具体字符原文没有涉及。另外，对一个相近的问题（agent 之间消息的空格和语法错误），OpenAI 给的是 prompt，不是钩子（G6 L117）。
- 「For example, we statically enforce structured logging, naming conventions for schemas and types, file size limits, and platform-specific reliability requirements with custom lints.」（HE L100）
- 「Human taste is captured once, then enforced continuously on every line of code.」（HE L165，Entropy and garbage collection）

**E2 部分支持，部分相反。**
- 支持的一面：进行中的会话绑定配置快照；计划要引用流程文档。
  - 「Tool specs, adapter selection, and effective tracker settings MUST be bound to one session snapshot. A workflow reload applies to future sessions; it MUST NOT make an in-flight session advertise one provider and execute another.」（A05 L1096-1098，§10.5）
  - 「If PLANS.md file is checked into the repo, reference the path to that file here from the repository root and note that this document must be maintained in accordance with PLANS.md.」（PL L104）
- 相反的一面：原文要求改进持续回灌，并对之后的运行立即生效，而不是等需求结束统一合入。
  - 「On change, it MUST re-read and re-apply workflow config and prompt template without restart.」（A05 L565，§6.2）
  - 「Human taste is fed back into the system continuously.」（HE L108）

**E3 部分支持。** 原文要求证据精简，不贴大块内容。按 head 命名证据目录原文没有涉及。
- 「Keep them concise and focused on what proves success. If you need to include a patch, prefer file-scoped diffs or small excerpts that a reader can recreate by following your instructions rather than pasting large blobs.」（PL L76，Guidelines）
- 「Avoid logging large raw payloads unless necessary.」（A05 L1377，§13.1）

**E4 支持。** 在 Symphony 里，耗时和 token 这类数字由运行时累计，不靠 agent 自报。"人工次数、返工数"原文没有涉及。
- 「At completion of a major task or the full plan, write an `Outcomes & Retrospective` entry summarizing what was achieved, what remains, and lessons learned.」（PL L90）
- 「Accumulate aggregate totals in orchestrator state.」（A05 L1433，§13.5）

---

### 清单没覆盖、但原文有的做法（5 条）

1. **别把 agent 当成状态机里的固定节点，给目标而不是固定流转。** 这可以用来衡量 B1–B3 会不会做得过细。
   「We also learned that treating agents as rigid nodes in a state machine doesn’t work well.」「So we eventually moved toward giving agents _objectives_ instead of strict transitions, much like a good manager would assign a goal to a direct report on their team.」（A04 L120、L122）
2. **检查脚本的报错信息里直接写修复方法。** 适用于 B7、E1 和 check-delivery 的输出。
   「Because the lints are custom, we write the error messages to inject remediation instructions into agent context.」（HE L100）
3. **无人值守时，等用户输入或审批不能无限挂起，要按写明的策略失败或上报；终止原因要分类。** 与空转 81 分钟、验证跑 2 小时无结果直接相关。
   「Approval requests and user-input-required events MUST NOT leave a run stalled indefinitely. An implementation MAY either satisfy them, surface them to an operator, auto-resolve them, or fail the run according to its documented policy.」（A05 L1073-1075）
   「Distinct terminal reasons are important because retry logic and logs differ.」（A05 L692）
4. **定期审计每条指令是否还需要，并考虑哪些模型会读到它。** 两家模型共用同一套 skill 时尤其相关。
   「you should frequently revisit each instruction and ask yourself whether it's still needed.」（AST L35）
   「Guidance that helps Sol or Luna may overconstrain GPT-6 Astra, so consider which models will use the instructions you leave behind.」（AST L31）
5. **用户指令优先于 skill；skill 导致停顿时，要求模型指出是哪条规则。** 与 grill 第一轮被用户补充的前提覆盖有关，也方便定位是哪条 skill 规则导致停顿。
   「The user's instructions take precedence over guidelines provided in a skill.」（G6 L74）
   「If a skill causes you to ask for permission or confirmation, pause, leave requested work unfinished, or diverge from the user's intent, name and link to the exact SKILL.md file you read, quote the relevant instruction, and briefly explain how it applies.」（G6 L80）