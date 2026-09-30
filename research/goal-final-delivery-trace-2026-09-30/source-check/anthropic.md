---
source: 子代理核对（general-purpose，claude-opus-5-5），2026-09-30；只读原文存档，引文由子代理用脚本核对逐字存在
scope: Anthropic 原文对 24 条建议的态度
---

# Anthropic 原文对 24 条建议的逐条核对

16 份原文都已通读。下面每条引文都用脚本做过逐字比对，行号可以直接定位。原文里有些撇号是弯引号（’），引文照原样保留。没有改任何文件。

## 文件缩写

目录 `/Users/minimax/code/github/xieshijie/dev-skills/skills/agent-prompt-rules/references/sources/anthropic/` 下：

- CCBP = claude-code-best-practices.md
- EH = effective-harnesses-for-long-running-agents.md
- HD = harness-design-long-running-apps.md
- BMAS = building-multi-agent-systems-when-and-how.md
- MARS = multi-agent-research-system.md
- MSPP = multiagent-systems-patterns-and-problems.md
- ECE = effective-context-engineering.md
- BEA = building-effective-agents.md
- SMA = scaling-managed-agents.md
- CPBP = claude-prompting-best-practices.md
- SABP = skill-authoring-best-practices.md
- O5 = prompting-claude-opus-5.md
- O55 = prompting-claude-opus-5-5.md
- F5 = prompting-claude-fable-5.md
- F51 = prompting-claude-fable-5-1.md

另有 A07 = `/Users/minimax/code/github/xieshijie/super-auto/research/agent-delivery-2026-09-28/raw/architecture/A07-anthropic-compiler.md`。

## 先说总体：用户的原则有依据，但有一处例外

"prompt 只写边界，必须每次发生的动作交给钩子"这条原则，Anthropic 原文有直接依据：

- "Use hooks for actions that must happen every time with zero exceptions." / "Unlike CLAUDE.md instructions which are advisory, hooks are deterministic and guarantee the action happens."（CCBP L241、L243，Set up hooks）
- "Ruthlessly prune. If Claude already does something correctly without the instruction, delete it or convert it to a hook."（CCBP L578）
- "Skills developed for prior models are often too prescriptive for Claude Fable 5 and can degrade output quality."（F5 L174）

例外是：Anthropic 在旧模型上自己也用过强措辞来约束验证者，例如 BMAS L354 "Without explicit requirements for comprehensive validation, verification agents take shortcuts."，以及 EH L53 "we use strongly-worded instructions like “It is unacceptable to remove or edit tests because this could lead to missing or buggy functionality.”"。但它对新模型的建议是把措辞调回常态："Where you might have said "CRITICAL: You MUST use this tool when...", you can use more normal prompting like "Use this tool when..."."（CPBP L521，Tool usage）。

---

## A 组：定义阶段

**A1 第 0 轮先问框架（截止、上线分支、影响范围、目标 MR、授权边界）**
- **结论**：部分支持。原文支持"spec 写明不做什么、边界要显式"，没有涉及"第 0 轮先问"这个顺序。
- "The most useful specs are self-contained: they name the files and interfaces involved, state what is out of scope, and end with an end-to-end verification step that proves the feature works."（CCBP L373，Let Claude interview you）
- "Define explicit constraints on what Claude Fable 5 should and should not do"（F5 L77，State the boundaries）
- **提示**："Don't ask obvious questions, dig into the hard parts I might not have considered."（CCBP L366）。据此，框架题只问读仓库得不出的项；分支、目标 MR 如果能从仓库查到，就不该问用户。

**A2 默认决定成批列出，用户有异议再改**
- **结论**：支持。"每题开头说明决定什么、用户会看到什么差别"这一要求原文未涉及。
- "Read ambiguity the way a careful colleague would: make routine judgment calls yourself, and check in only when different readings would lead to materially different work."（F51 L836，Finish the whole task）
- "If you are weighing a choice, give a recommendation, not an exhaustive survey."（F5 L38）
- "Three: a list of decisions for the user when, by your own account, none of them blocks the rest of the work."（O55 L74，Unattended agentic runs）。这句把"停下来列一串不阻塞的决定"列为反例，恰好支持改成"默认决定、用户有异议再改"。

**A3 推荐依据先核实并附行号；依赖子任务的问题等子任务回来再问**
- **结论**：支持。
- "Never speculate about code you have not opened."（CPBP L1076，Minimizing hallucinations）
- "Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for; if something is not yet verified, say so explicitly."（F5 L72）
- 后半句的相近做法："If a question comes up partway, first do everything that doesn't depend on the answer; then state the assumption you made"（F51 L838）
- **形式**：CPBP 的样例用了 "MUST"，但按 L521 应写成一句平常的话。

**A4 每个检查点写明证据形式，核对工具能否产出，不能就列为工具缺口**
- **结论**：支持。
- "Have Claude show evidence rather than asserting success: the test output, the command it ran and what it returned, or a screenshot of the result."（CCBP L56）
- "The generator proposed what it would build and how success would be verified, and the evaluator reviewed that proposal to make sure the generator was building the right thing."（HD L70，sprint contract）
- 工具缺口会造成实际损失："For example, Claude can’t see browser-native alert modals through the Puppeteer MCP, and features relying on these modals tended to be buggier as a result."（EH L75，Testing）

**A5 冻结时单列"只靠单测证明的用户可见行为"**
- **结论**：支持这条建议的前提（单测不等于端到端）。"单列给用户确认"这个具体做法原文未涉及。
- "Claude tended to make code changes, and even do testing with unit tests or `curl` commands against a development server, but would fail recognize that the feature didn’t work end-to-end."（EH L65）
- "However, whereas automated testing helps verify functionality, human review remains crucial for ensuring solutions align with broader system requirements."（BEA L208）
- "For autonomous systems, it is easy to see tests pass and assume the job is done, when this is rarely the case."（A07 L125）

**A6 写出产品改动允许的路径清单，供机械检查**
- **结论**：支持，但原文有一条提醒。
- CCBP L373 的 "name the files and interfaces involved, state what is out of scope"；review 时检查 "nothing outside the task's scope changed. Report gaps, not style preferences."（CCBP L558）
- **提醒**："if the planner tried to specify granular technical details upfront and got something wrong, the errors in the spec would cascade into the downstream implementation. It seemed smarter to constrain the agents on the deliverables to be produced and let them figure out the path as they worked."（HD L64）。据此，清单宜按目录粒度写，并留出经用户确认后修订的口子。

---

## B 组：交付阶段

**B1 每个里程碑三个勾选项（场景跑通、里程碑检查、提交）**
- **结论**：勾选清单本身受支持；"里程碑检查"这一项在原文里因模型而异，意见相反。
- 支持清单："For particularly complex workflows, provide a checklist that Claude can copy into its response and check off as it progresses."（SABP L437）；"Keep the task's parts in a checklist the model updates, such as a to-do tool or a file."（O55 L61）
- 支持检查点："However, verification subagents remain valuable when using less capable orchestrators, when verification requires specialized tools, or when you want to enforce explicit verification checkpoints in your workflow."（BMAS L258）；F5 L173 建议 "Establish a method for checking your own work at an interval of [X] as you build. Run this every [X interval], verifying your work with subagents against the specification."
- 反对（Opus 5）："remove them: instructions like these cause over-verification on Claude Opus 5, and removing them reduces wasted tokens with no loss in quality. The same applies to legacy harness scaffolding that adds separate verification steps."（O5 L61）
- 反对（HD）："With the sprint construct removed, I moved the evaluator to a single pass at the end of the run rather than grading per sprint."（HD L129）；"It is worth the cost when the task sits beyond what the current model does reliably solo."（HD L131）
- **含义**：如果保留，应作为运行时强制的检查点，并且按任务难度和所用模型决定要不要，不要写成 prompt 里的验证指令。

**B2 场景跑通后后台启动检查，下一次提交前必须处理完结果**
- **结论**：异步这部分支持；"提交前必须处理完"这个闸门原文未直接涉及。
- "On coding tasks, letting the lead continue while subagents run lowers average time to completion at similar quality, token usage, and cost."（F51 L900）
- 实现方式要落在运行时："Have the tool that starts a subagent return immediately." / "Pass each subagent's result back to the lead in a later `user` message once it's ready."（F51 L902–903）
- "The model still often chooses to wait."（F51 L906）。也就是说，只写 prompt 不够，要由工具机制保证。
- 相近的闸门逻辑："If something the model started is still running, such as a background command or a subagent, don't treat the task as done yet: wait for it to finish and return its output to the model as the next user message."（O55 L67）

**B3 报告落盘写明 commit 范围，check-delivery.mjs 核对覆盖和时序**
- **结论**：支持"落盘加脚本核对"。"报告早于下一个里程碑第一个提交"这条时序规则原文未涉及。
- "Subagents call tools to store their work in external systems, then pass lightweight references back to the coordinator."（MARS L104）
- "For complex workflows, break evaluation into discrete checkpoints where specific state changes should have occurred, rather than attempting to validate every intermediate step."（MARS L100）
- "Write `validate_form.py` rather than asking Claude to generate validation code"（SABP L1051）

**B4 推理强度能看到就核对，不作为检查作废条件**
- **结论**：原文没有"subagent 继承推理强度"的说法，未直接涉及。下面两处间接支持"不据此作废"：
- "Accuracy holds at lower effort settings, which supports a fast pass at review time and a more thorough pass later."（O5 L16）
- "Effort level names don't correspond to the same amount of thinking across models"（O55 L38）

**B5 长任务靠完成通知回来，外部状态用会退出的轮询脚本，不用定时唤醒、不承诺"几分钟后再看"**
- **结论**：支持，有一处细节要注意。
- "If you hit one of these, ask and end the turn, rather than ending on a promise."（F5 L64）
- "A step you have decided on is something to run, not to announce: describing the next step and ending the turn leaves it undone until the user replies."（F51 L838）
- "Claude can't tell time and, left alone, will happily spend hours running tests instead of making progress."（A07 L77）
- "if you need a hard stop, keep your own timeout."（O55 L121）
- **细节一**：Anthropic 并不反对定时检查本身，它反对的是让模型自己承诺回来看。原文："consider restructuring harnesses to check on runs asynchronously, for example through scheduled jobs, rather than blocking."（F5 L35）。这里定时检查的主体是外层框架（harness），不是模型。
- **细节二**：轮询要有间隔。"When agents had no other means to coordinate, they quickly flooded the system with high-frequency (30 times per second) polling daemons in order to get their jobs through."（MSPP L60）

**B6 进入长等待时给用户一句状态**
- **结论**：支持，但形式有讲究，而且和模型有关。
- "Third, if you want more frequent or predictable updates, … say so in the system prompt; the model is responsive to such instructions. This helps most in human-in-the-loop work."（O55 L95）
- 也可以由外层框架触发："Fourth, if long tool-calling turns still go quiet for longer than you want, have your harness ask for an update."（O55 L97）
- **警示**：O55 L74 把 "Four: deciding that this is a good place to report, because the turn has been long or a milestone is done." 列为提前停止的反例，并要求 "put them in the same message as your next tool call"。因此状态句应和启动等待脚本放在同一条消息里，不能单独结束回合。
- **模型差异**：Opus 5.5 默认就会写进度更新（O55 L89）；Fable 5.1 相反，"Claude Fable 5.1's default behavior is to write fewer user-facing updates during long tool-calling turns than Claude Fable 5 does."（F51 L42）。

**B7 每次提交前用脚本比对改动文件和清单**
- **结论**：强支持。
- CCBP L241、L243（见"总体"一节）；钩子示例 "Write a hook that blocks writes to the migrations folder."（CCBP L245）
- "I built a continuous integration pipeline and implemented stricter enforcement that allowed Claude to better test its work so that new commits can’t break existing code."（A07 L66）

**B8 第一次跑场景就写成参数化脚本，重跑和独立验证都用它**
- **结论**：支持，有两点提醒。
- "It also helps to ask the initializer agent to write an init.sh script that can run the development server, and then run through a basic end-to-end test before implementing a new feature."（EH L85）
- "Encourage Claude to create setup scripts (for example, `init.sh`) to gracefully start servers, run test suites, and linters. This prevents repeated work when continuing from a fresh context window."（CPBP L882）
- **提醒一**：独立验证不能只跑 owner 的脚本。"Require the verifier to test multiple scenarios and edge cases." / "Direct the verifier to attempt inputs that should fail and confirm they do."（BMAS L352–353）
- **提醒二**：脚本放在需求目录，不要进产品测试。"don't turn scratch checks into additional permanent test files"（F51 L856）

**B9 专用 worktree，结束按清单清理**
- **结论**：支持。
- "run separate CLI sessions in isolated git checkouts so edits don't collide"（CCBP L485）
- "Each subagent works in its own worktree."（CCBP L510）
- 清理在原文里是一条 prompt："If you create any temporary new files, scripts, or helper files for iteration, clean up"（CPBP L1014）。按用户的原则应改用脚本。

---

## C 组：验证工具

**C1 run-verifier 异步、持续写日志和心跳、加超时**
- **结论**：强支持。
- "At most, it should print a few lines of output and log all important information to a file so Claude can find it when needed."（A07 L76）
- "Our only window in was the WebSocket event stream, but that couldn’t tell us _where_ failures arose, which meant that a bug in the harness, a packet drop in the event stream, or a container going offline all presented the same."（SMA L25）
- "it’s also common to include stopping conditions (such as a maximum number of iterations) to maintain control."（BEA L141）
- 另见 F5 L35（异步检查）和 O55 L121（自带超时）。

**C2 启动前预检（登录、模型引用、图形入口）**
- **结论**：间接支持；原文没有"预检"这个说法。
- "Don't assume packages are available"（SABP L1098）
- "When writing scripts for Skills, handle error conditions rather than deferring to Claude."（SABP L871）
- 环境能力不足的后果见 EH L75。

**C3 codex 加不用沙箱的选项，并显式设推理强度**
- **结论**：要拆成两部分看。
- **显式推理强度**：支持，但原文讲的是 Claude 的 effort 参数，用到 Codex 上只能类比。"set it explicitly, and test several levels against your own evals rather than carrying over the setting you used on Claude Opus 5."（O55 L38）
- **不用沙箱**：原文倾向保留隔离。"_(Run this in a container, not your actual machine)._"（A07 L22，作者用 `--dangerously-skip-permissions` 时就是这样做的）；"We recommend extensive testing in sandboxed environments, along with the appropriate guardrails."（BEA L151）；"The structural fix was to make sure the tokens are never reachable from the sandbox where Claude’s generated code runs."（SMA L37）
- **含义**：关掉沙箱时，应在别的层面（容器或专用账号）隔离，并让凭据不可达。

**C4 复验只重跑受影响场景、失败项和冒烟，给时间预算**
- **结论**：部分支持，也有警示。
- 支持时间预算："have your harness add a short line at the end of each message it sends back to the model giving the elapsed time against that budget, in seconds, for example `elapsed 340s / 1200s`."（O55 L115）。但同一节又说 "under time pressure the model might search and verify a little less."（O55 L121）
- 支持抽样："includes a default `--fast`option that runs a 1% or 10% random sample"（A07 L77，原文此处少一个空格）
- 支持先快后全："Accuracy holds at lower effort settings, which supports a fast pass at review time and a more thorough pass later."（O5 L16）
- **警示一**："The verifier runs one or two tests, observes them pass, and declares success."（BMAS L347）
- **警示二**："near the end of the project, Claude started to frequently break existing functionality each time it implemented a new feature."（A07 L66）
- **含义**：收窄的范围应由脚本从 diff 算出来，并在合入前保留一次全量验证。

**C5 编排器派发的验证留下等价记录，机械检查接受**
- **结论**：支持。
- "We're opinionated about the shape of these interfaces, not about what runs behind them."（SMA L15）
- "Even with identical starting points, agents might take completely different valid paths to reach their goal."（MARS L60）
- "Adding full production tracing let us diagnose why agents failed and fix issues systematically."（MARS L76）

---

## D 组：仓库和工具能力

**D1 验证实例串行，或共享登录加刷新锁**
- **结论**：间接支持（锁机制）；登录刷新本身原文未涉及。
- "Claude takes a "lock" on a task by writing a text file to current_tasks/"（A07 L50）
- 同一模型的多个 agent 容易撞上同一资源："18 out of 30 agents decided to create a git branch with the exact same branch name"（MSPP L53）

**D2 需求中补的验证能力并回验证工具 MR**
- **结论**：间接支持；"并回哪个 MR"原文未涉及。
- "We even created a tool-testing agent—when given a flawed MCP tool, it attempts to use the tool and then rewrites the tool description to avoid failures."（MARS L51）
- "watching for mistakes Claude was making, then designing new tests as I identified those failure modes."（A07 L64）

**D3 在真实桌面实例里注入固定消息历史**
- **结论**：支持"固定夹具加真实入口"的思路；注入的具体机制原文未涉及。
- "a script that diffs output against a fixture"（CCBP L39）
- "Claude mostly did well at verifying features end-to-end once explicitly prompted to use browser automation tools and do all testing as a human user would."（EH L67）

**D4 按生产装配驱动功能的集成测试夹具**
- **结论**：支持。
- "Digging into the code revealed that the wiring between entity definitions and the game runtime was broken, with no surface indication of where."（HD L93）
- "So it’s important that the task verifier is nearly perfect, otherwise Claude will solve the wrong problem."（A07 L64）

**D5 汇报里的缺口写明去处，需求结束建成任务**
- **结论**：支持"作为后续事项报告"；"建成任务"原文未涉及。
- "If, while working or testing, you find a pre-existing bug, a performance concern, or behavior the task doesn't mention, don't fix, optimize or extend it in this change unless the requested behavior cannot work without it; report it as a follow-up in your summary."（F51 L856）
- "a change to a file the task didn't require — is a suggestion to make at the end, not a change to make"（F51 L840）

---

## E 组：运行时和流程

**E1 pre-commit 钩子和 PostToolUse 钩子拦截 U+FFFD**
- **结论**：强支持；U+FFFD 这个具体场景原文未涉及。
- CCBP L241、L243；"Write a hook that runs eslint after every file edit"（CCBP L245，相当于 PostToolUse 的用法）
- "Use `claude -p "prompt"` in CI, pre-commit hooks, or scripts."（CCBP L460）

**E2 一个需求期间冻结流程版本，改进另开会话，结束后统一合入**
- **结论**：支持，但原文有一处相反的表述。
- "This means that whenever we deploy updates, agents might be anywhere in their process. We therefore need to prevent our well-meaning code changes from breaking existing agents."（MARS L78，rainbow deployments 一段）
- 技术上，会话中途改指令也有代价："adding it partway through changes the `system` prompt and invalidates the conversation's earlier thinking blocks"（O55 L71）
- **相反表述**："Claude Fable 5 also does a good job of updating skills on the fly based on what it learns from the task at hand."（F5 L174）

**E3 文本提交、截图日志按大小忽略；证据目录按 head 命名**
- **结论**：部分支持。按 commit 命名有原文先例；"哪些类型提交、哪些按大小忽略"原文未涉及。
- `LOGFILE="agent_logs/agent_${COMMIT}.log"`（A07 L29）

**E4 每个需求结束出 trace 与耗时、人工、返工数字**
- **结论**：强支持。
- "It is always good practice to experiment with the model you're building against, read its traces on realistic problems, and tune its performance to achieve your desired outcomes."（HD L180）
- HD L145–153 本身就按阶段列了耗时和成本表。
- "The key to success, as with any LLM features, is measuring performance and iterating on implementations."（BEA L166）

---

## 清单没有覆盖的做法（5 条）

1. **回合结束由外层框架判定"是否真的做完"。** "Treat a text-only end of turn as a report rather than as proof the task is done." / "If a turn ends with items still open and no blocker stated, send a short user message naming them, like the following one." / "Either way, stop after two or three automatic continuations on the same task rather than repeating them indefinitely, so that a run that is genuinely stuck ends and can be reviewed."（O55 L61）。确定性的版本是 Stop hook："runs your check as a script and blocks the turn from ending until it passes."（CCBP L51）。这对应试跑中的空转和漏做里程碑检查。

2. **外层框架给模型注入已用时间。** "have your harness add a short line at the end of each message it sends back to the model giving the elapsed time against that budget, in seconds, for example `elapsed 340s / 1200s`."（O55 L115）。背景是 A07 L77 说的模型对时间没有感知。这对应那一路 2 小时没有结果的验证。

3. **状态清单用 JSON，只允许改状态字段。** "After some experimentation, we landed on using JSON for this, as the model is less likely to inappropriately change or overwrite JSON files compared to Markdown files."（EH L53）；"When tracking structured information (like test results or task status), use JSON or other structured formats to help Claude understand schema requirements."（CPBP L903）。B1 目前是 plan.md 里的 Markdown 勾选框。

4. **检查者报什么要校准（两处原文取向不同）。** 一处要求只报影响正确性的问题："Tell the reviewer to flag only gaps that affect correctness or the stated requirements, and treat the rest as optional."（CCBP L565）。另一处提醒不要限制上报："the model may follow that instruction literally and report less; ask it to report everything and filter in a separate pass instead."（O5 L16）。里程碑检查和最终验证的 prompt 都会碰到这个取舍。

5. **一次去掉一个组件做对照，换模型时重审框架。** "I moved to a more methodical approach, removing one component at a time and reviewing what impact it had on the final result."（HD L119）；"when a new model lands, it is generally good practice to re-examine a harness, stripping away pieces that are no longer load-bearing to performance"（HD L180）。E4 提供了数字，但没有说明怎么判断 24 条里哪条真正起作用；这条给了方法。