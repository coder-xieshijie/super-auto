---
source: 子代理核对（general-purpose），2026-10-01；只读原文存档，引文逐字核对
scope: Anthropic 原文（15 份存档加 A07）对 MR 7595 交付 trace 归纳出的 16 条流程优化方向（O1–O16）的态度；另列原文有而 16 条未覆盖的做法 5 条
---

# Anthropic 原文对 O1–O16 的逐条核对

## 说明

- 原文目录 `/Users/minimax/code/github/xieshijie/dev-skills/skills/agent-prompt-rules/references/sources/anthropic/`。简称：CCBP=claude-code-best-practices.md，EH=effective-harnesses-for-long-running-agents.md，HD=harness-design-long-running-apps.md，BMAS=building-multi-agent-systems-when-and-how.md，MARS=multi-agent-research-system.md，MSPP=multiagent-systems-patterns-and-problems.md，ECE=effective-context-engineering.md，BEA=building-effective-agents.md，SMA=scaling-managed-agents.md，CPBP=claude-prompting-best-practices.md，SABP=skill-authoring-best-practices.md，O5=prompting-claude-opus-5.md，O55=prompting-claude-opus-5-5.md，F5=prompting-claude-fable-5.md，F51=prompting-claude-fable-5-1.md。A07=`/Users/minimax/code/github/xieshijie/super-auto/research/agent-delivery-2026-09-28/raw/architecture/A07-anthropic-compiler.md`。
- 15 份原文和 A07 都已通读。每条引文都用 python 把空白规范化后，在所标行做子串匹配，全部命中；说明里只给行号、不加引号的参考位置，也逐个打开核对过。原文里的弯引号（’ “ ”）照原样保留。上一轮核对结果（`research/goal-final-delivery-trace-2026-09-30/source-check/anthropic.md`）只作线索，其中的引文本轮重新核对过。
- 态度分四种：支持、部分支持、相反、未涉及。一条建议里有几个分项时，分别说明哪部分有依据、哪部分没有。
- 原文按模型给出的建议有时不同。交付 owner 用的是哪个模型，决定该采用哪一条，下文遇到时单独标出。

## 态度一览

| 编号 | 方向 | 态度 | 原文与建议有出入的地方 |
|---|---|---|---|
| O1 | 流程更新不打断在途交付 | 部分支持 | F5 说 Fable 5 能在任务中途自己更新 skill；CCBP 把按 Esc 中断后改方向当作正常纠偏手段；F51 提供了会话中途改指令的正式通道 |
| O2 | 等人的问题不无限挂起 | 支持 | F51 提醒这类指令会让模型少问歧义问题 |
| O3 | 交付中修改 verify 的成本 | 部分支持 | HD 认为前期把技术细节定得太细，错误会传到实现；"一次列全"未涉及 |
| O4 | 冻结前核实验证可行性 | 支持（间接） | 无 |
| O5 | 验证环境不需要人 | 支持，有限制 | 原文把 `rm -rf` 列为应当确认的操作，修法应是把清理收窄成预授权命令，而不是去掉确认 |
| O6 | 质量命令按 CI 选 | 部分支持 | "尽早推送读合并结果流水线"未涉及 |
| O7 | 审查与场景运行并行 | 支持 | 里程碑检查本身要不要做，Opus 5 与 Fable 5 的建议相反 |
| O8 | 计划里的时间要可核对 | 支持 | 无 |
| O9 | 主会话协调、大块实现交给子代理 | 部分支持 | BMAS 主张按上下文边界拆分，同一功能的连续阶段不宜拆；各模型对委派的建议不同 |
| O10 | 长时间等待时给出状态和预计时间 | 状态支持；预计时间部分相反 | 原文说模型没有时间感，预计时间不宜由模型自报 |
| O11 | 给用户的问题写得通俗 | 支持 | 无 |
| O12 | 定义阶段先查事实再提问 | 支持 | 无 |
| O13 | 默认决定成批列出 | 支持 | CCBP 在写 spec 阶段主张详细访谈，需要划清哪些题该问 |
| O14 | 最后一次 rebase 的风险前移 | 部分支持 | 依赖另一个未合入 MR 的情况未涉及 |
| O15 | 证据入库 | 部分支持（间接） | CCBP 重视留证据；仓库体积未涉及 |
| O16 | 门禁报错写明修法 | 支持 | 无 |

---

## O1 流程更新不打断在途交付

**态度：部分支持。** "不要因为发布更新而打乱正在运行的 agent"有直接依据；"开工时绑定版本、在里程碑边界由 owner 比对版本后自己拉取"这个具体机制原文未涉及；"只投递阻塞本次交付的修复"未涉及。

- MARS L78（Production reliability and engineering challenges）：“This means that whenever we deploy updates, agents might be anywhere in their process. We therefore need to prevent our well-meaning code changes from breaking existing agents. We can’t update every agent to the new version at the same time.”
  - 说明：这是绑定版本的直接依据，原文的做法是新旧版本同时运行、逐步切换（rainbow deployments），由部署系统承担，而不是要求 agent 自己处理。技术上，会话中途改 system prompt 还会让此前的 thinking blocks 失效（见 O55 L71）。
- CCBP L389（Course-correct early and often）：“stop Claude mid-action with the `Esc` key. Context is preserved, so you can redirect.”
  - 说明：原文把中断当作人纠正方向的正常手段，没有讨论模型会把中断理解成用户拒绝；所以"投递不用中断"要靠流程规定，原文不能直接引来反对中断。原文给出的不中断投递方式是等当前工作结束、把结果作为下一条 user message 送回（见 F51 L903、O55 L67），或者用 mid-conversation system message 改指令（见 F51 L770）。
- F5 L174（Recommended scaffolding changes）：“Claude Fable 5 also does a good job of updating skills on the fly based on what it learns from the task at hand.”
  - 说明：这一句与"交付期间冻结流程版本"方向相反，不过它说的是模型根据本次任务所学自己改 skill，不是外部会话往在途 owner 推送新版本。若 owner 是 Fable 5，可以允许它把经验记下，但流程规则本身仍按开工版本执行。

## O2 等人的问题不无限挂起

**态度：支持。** 原文给出的做法和建议一致：不阻塞的问题写明假设后继续，只为少数几类情况停下；无人值守时由外层框架限制自动续跑次数。

- F51 L838（Finish the whole task）：“If a question comes up partway, first do everything that doesn't depend on the answer; then state the assumption you made, or — when going ahead on a wrong guess would be unsafe or would make the work useless — put the question at the end of a turn that also delivers that progress.”
  - 说明：与"写明默认做法并继续"一致；原文还给了例外条件，即猜错会不安全或会让工作白做时才把问题留到回合末尾。
- F5 L64（Strong instruction following）：“Pause for the user only when the work genuinely requires them: a destructive or irreversible action, a real scope change, or input that only they can provide.”
  - 说明：原文列的停下情形是三类（破坏性或不可逆操作、真正的范围变化、只有用户能提供的输入），可以拿来对照流程里"四种停下"的定义。执行顺序这类问题不在其中。
- O55 L61（Unattended agentic runs）：“Either way, stop after two or three automatic continuations on the same task rather than repeating them indefinitely, so that a run that is genuinely stuck ends and can be reviewed.”
  - 说明：无人值守时的等待策略，原文放在外层框架里：自动续跑有上限，卡住的运行要结束并留给人看，而不是一直挂着。
- 限制：F51 L830 提醒这类"自主运行"指令会让模型更少就歧义提问，要在自己的任务上检查这个取舍；O55 L71 说这段补充不适用于有人在场应答的场景。

## O3 交付中修改 verify 的成本

**态度：部分支持。** "验收口径不能由执行者随手改、发现冲突要报给用户确认"有依据；"重新冻结做成脚本"有一般性依据（确定性操作用脚本，见 SABP L1051）；"改动部分由另一家模型查漏"原文只说用新上下文的模型复核（见 CCBP L52），没说要换厂商；"同一类问题一次列全"未涉及；"记录是谁确认的"只有相近做法（压缩摘要要逐字保留已决定、已同意的事项，见 F51 L848）。

- EH L53（Feature list）：“We prompt coding agents to edit this file only by changing the status of a passes field, and we use strongly-worded instructions like “It is unacceptable to remove or edit tests because this could lead to missing or buggy functionality.””
  - 说明：原文让执行者只能改状态、不能改验收项，这支持把修改 verify 放到 owner 之外的正式步骤里。原文没有讲"验收项本身错了怎么办"，这正是本条要补的部分。
- F51 L836（Finish the whole task）：“If you see a real problem with the task as specified, say so in a sentence or two and keep building under stated assumptions; if the user hears the concern and reaffirms, that is their decision, so deliver the full request.”
  - 说明：发现口径冲突时，原文的做法是简短说明、在假设下继续，由用户决定；这与"等用户确认后才重新冻结"相比更偏向不停工。
- HD L64（The architecture）：“This emphasis was due to the concern that if the planner tried to specify granular technical details upfront and got something wrong, the errors in the spec would cascade into the downstream implementation.”
  - 说明：这条限制的是冻结设计本身：前期写得越细，后面越容易冲突。HD 的替代做法是在每段工作开工前由生成方和评估方商定"做到什么算完成"（见 HD L70），而不是一开始就把全部检查点定死；不过 HD 后来在 Opus 4.6 上去掉了分段，评估改为最后一次性做（见 HD L129）。

## O4 冻结前核实验证可行性

**态度：支持（间接）。** 原文没有"冻结前试跑"这个说法，但有三处相近做法：开工前先商定怎样验证；先小规模试跑再全量；观测源在不同故障下可能记成一样，需要事先弄清。

- HD L70（The architecture）：“The generator proposed what it would build and how success would be verified, and the evaluator reviewed that proposal to make sure the generator was building the right thing.”
  - 说明：验证方式在写代码之前就要被另一方审过，这与"冻结前核实验证能否做到"同向。验证工具本身有盲区的例子见 EH L75，验证器不准的后果见 A07 L64。
- SMA L25（Don’t adopt a pet）：“Our only window in was the WebSocket event stream, but that couldn’t tell us _where_ failures arose, which meant that a bug in the harness, a packet drop in the event stream, or a container going offline all presented the same.”
  - 说明：这正是"没核实观测源在中断、失败、辅助请求下记什么"的问题：一个观测源对不同故障给出相同记录，就分辨不出原因。冻结前应确认每个观测源在这些情况下各记什么。
- CCBP L527（Fan out across files）：“Refine your prompt based on what goes wrong with the first 2-3 files, then run on the full set.”
  - 说明：原文场景是批量迁移，但"先拿少量样本试跑、修正后再全量"的做法可以直接用到冻结前的只读试探。

## O5 验证环境不需要人

**态度：支持，有限制。** 预授权常用命令、无人值守运行不因审批停住、每个实例独立环境，都有依据。限制在于原文把 `rm -rf` 列为应当确认的操作。

- CCBP L208（Configure permissions）：“To get fewer prompts without giving up control, pre-approve the tools you trust with `/permissions` and let sandboxed commands run without asking with `/sandbox`.”
  - 说明：把清理做成验证工具里的固定命令，就能整体预授权，不必每次审批子代理手写的命令。原文还说，`-p` 非交互运行在 auto mode 下即使分类器反复拦截也不会停住整个运行（见 CCBP L543）；工具参数应设计得不容易用错（见 BEA L227）。
- CPBP L948（Balancing autonomy and safety）：“Destructive operations: deleting files or branches, dropping database tables, rm -rf”
  - 说明：原文样例把 `rm -rf` 列为需要确认的操作；O55 L74 那段要求模型不要停下的指令也写明，它不取代对危险或破坏性操作的确认。因此修法应是把清理限定在验证工具自己的临时目录、做成预授权命令，而不是让任意 `rm -rf` 免审。
- A07 L46（Running Claude in parallel）：“A new bare git repo is created, and for each agent, a Docker container is spun up with the repo mounted to `/upstream`. Each agent clones a local copy to `/workspace`, and when it's done, pushes from its own local container to upstream.”
  - 说明：原文每个 agent 有自己的容器和工作副本，支持"每个验证实例独立登录态"。登录态互相作废这一具体问题原文未涉及。

## O6 质量命令按 CI 选

**态度：部分支持。** "agent 本地跑的检查要和真正的门禁一致"有依据；"按改动选出检查集"只有相近做法；"尽早推送、读合并结果流水线"未涉及。

- A07 L66（Write extremely high-quality tests）：“To address this, I built a continuous integration pipeline and implemented stricter enforcement that allowed Claude to better test its work so that new commits can’t break existing code.”
  - 说明：原文是搭建 CI 并加严执行，让 Claude 能把自己的改动测到、新提交不能破坏已有功能；这支持 agent 跑的检查要和门禁一致，而不是靠里程碑检查或 CI 事后发现。
- CCBP L168（Write an effective CLAUDE.md）：“Include Bash commands, code style, and workflow rules. This gives Claude persistent context it can't infer from code alone.”
  - 说明：CI 会跑哪些检查（死代码、边界脚本、迁移测试、敏感词）属于 agent 从代码推不出的信息，应写成可执行的命令清单，而不是让 owner 自选。
- A07 L77（Put yourself in Claude’s shoes）：“includes a default `--fast`option that runs a 1% or 10% random sample. This subsample is deterministic per-agent but random across VMs, so Claude still covers all files but each agent can perfectly identify regressions.”
  - 说明：原文本地跑的是抽样子集、全量交给多个 agent 和 CI 覆盖，这与"本地跑按改动选出的子集、合入前以 CI 全量为准"一致；但原文是随机抽样，不是按改动选。另一处原文要求验证者跑全量（见 BMAS L351），两者合起来看，子集只能用于迭代，不能代替最终全量。

## O7 里程碑检查的代码审查与场景运行并行

**态度：支持（并行本身）。** 两项检查互不依赖，并行有依据。但"里程碑检查要不要单独做"这个前提，原文按模型给出相反建议。

- F51 L900（Let the lead agent keep working while subagents run）：“On coding tasks, letting the lead continue while subagents run lowers average time to completion at similar quality, token usage, and cost.”
  - 说明：支持让审查和场景同时跑，原文测得质量和成本基本不变、完成时间缩短。
- BMAS L246（Context-centric decomposition）：“A verifier that only needs to run tests and report results does not require implementation context.”
  - 说明：场景运行只需要跑和报结果，和读代码的审查没有共享上下文，属于原文说的可以拆开的边界。
- O5 L61（Task scope and over-verification）：“instructions like these cause over-verification on Claude Opus 5, and removing them reduces wasted tokens with no loss in quality. The same applies to legacy harness scaffolding that adds separate verification steps.”
  - 说明：若 owner 是 Opus 5，原文建议去掉额外的验证步骤；HD 在 Opus 4.6 上也把评估改为最后一次性做（见 HD L129）。相反，Fable 5 的建议是按固定间隔用子代理对照 spec 检查（见 F5 L173）。所以并行之前，先按所用模型和任务难度决定里程碑检查留不留。

## O8 计划里的时间要可核对

**态度：支持。** 原文的立场是模型没有时间感，时间应由外层框架提供，进度说法要对得上工具结果。

- A07 L77（Put yourself in Claude’s shoes）：“Claude can't tell time and, left alone, will happily spend hours running tests instead of making progress.”
  - 说明：这解释了 plan 里出现估计时间、且有晚于实际的情况；时间不该由模型填写。
- O55 L115（Time signals for multiagent harnesses）：“have your harness add a short line at the end of each message it sends back to the model giving the elapsed time against that budget, in seconds, for example `elapsed 340s / 1200s`.”
  - 说明：原文由框架把真实时间送给模型。据此，plan 里的时间最好由脚本从 git 提交时间或日志写入，而不只是事后核对。
- F5 L72（Ground progress claims during long runs）：“Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for; if something is not yet verified, say so explicitly.”
  - 说明：进度里的每一项（包括时间）都应能指到工具结果；不能指到的要标为未核实。

## O9 主会话做协调、大块实现交给子代理

**态度：部分支持。** "主会话保持干净、深度工作放到子代理"有依据；但原文对拆分方式有明确限制，而且不同模型的委派建议不同。

- ECE L109（Context engineering for long-horizon tasks，Sub-agent architectures）：“The main agent coordinates with a high-level plan while subagents perform deep technical work or use tools to find relevant information.”
  - 说明：直接支持主会话协调、子代理做深度工作并只回传摘要。
- BMAS L238（Context-centric decomposition）：“Dividing by context boundaries means an agent handling a feature should also handle its tests, because it already possesses the necessary context. Work should only be split when context can be truly isolated.”
  - 说明：这是限制：迁移应按能独立的模块或文件组切给子代理，每个子代理连同自己的测试一起做完；同一块工作的计划、实现、测试不宜拆给不同代理。原文还说编码任务可真正并行的部分比研究少（见 MARS L25）。
- O5 L74（Controlling subagent spawning）：“Delegate to a subagent only for large tasks that are genuinely independent and parallelizable, such as a wide multi-file investigation.”
  - 说明：模型差异：Opus 5 原文要压低委派，且称其在 1M 窗口内表现一致（见 O5 L19）；Opus 5.5 原文举的正是"用并行子代理端到端做大代码库迁移"（见 O55 L31）；Fable 5 原文要求多用子代理并异步沟通（见 F5 L85）。HD 在 Opus 4.5 上用单个连续会话加自动压缩也完成了构建（见 HD L60）。所以这条应写成"可独立的大块迁移交给子代理"，而不是"主会话不做实现"。

## O10 长时间等待时给出状态和预计时间

**态度：给状态支持；"预计时间"部分相反。** 原文支持在长时间无输出时补一句状态，并建议由外层框架触发；但原文认为模型没有时间感（A07 L77），预计时间应来自脚本或日志里的进度，而不是模型估算。

- O55 L97（User-facing progress updates）：“Fourth, if long tool-calling turns still go quiet for longer than you want, have your harness ask for an update.”
  - 说明：原文由框架数连续无输出的工具调用步数，到阈值后追加提醒；这比只在 prompt 里要求更可靠。
- F51 L42（Ask for user-facing progress updates）：“Claude Fable 5.1's default behavior is to write fewer user-facing updates during long tool-calling turns than Claude Fable 5 does.”
  - 说明：模型差异：Fable 5.1 默认更安静，需要明确要求；Opus 5 默认爱讲进度（见 O5 L43）；Opus 5.5 默认会写进度，但这些内容以 thinking block 形式返回，客户端要设置后才看得到（见 O55 L89、L91）。
- O55 L74（Unattended agentic runs）：“Four: deciding that this is a good place to report, because the turn has been long or a milestone is done.”
  - 说明：这是限制：给状态不能变成结束回合的理由。状态句要和启动等待的工具调用放在同一条消息里。

## O11 给用户的问题写得通俗

**态度：支持。**

- F5 L136（Readability when communicating with the user）：“The vocabulary you built up while working is yours, not theirs; leave it behind unless you re-introduce it.”
  - 说明：内部编号（如 S04、R20）和工作中形成的术语正属于这一类，问题开头应先用平常话说明场景。
- F5 L138（Readability when communicating with the user）：“When you mention files, commits, flags, or other identifiers, give each one its own plain-language clause.”
  - 说明：可以直接转成提问规则：每个编号后面跟一句平常话解释它是什么。
- O55 L33（Capabilities relevant to prompting）：“Its reports on agentic work, both the updates while it works and the summary when it finishes, say plainly what it did, what it found, and what it needs from you.”
  - 说明：模型差异：Opus 5.5 默认就较通俗；Fable 5 在长会话中容易写得难懂，原文为它准备了专门的补充说明（见 F5 L131）。

## O12 定义阶段先查事实再提问

**态度：支持。**

- CPBP L1076（Minimizing hallucinations in agentic coding）：“Never speculate about code you have not opened.”
  - 说明：代码核对子任务没回来就发问题、再连发修正，正是在没看过代码时给出了判断。
- CCBP L366（Let Claude interview you）：“Don't ask obvious questions, dig into the hard parts I might not have considered.”
  - 说明：查完事实后，能从仓库得出的就不该再问，问题集中在读代码也决定不了的地方。
- O55 L105（Explore context in multi-app workflows）：“Claude Opus 5.5 tends to get to work quickly, and on loosely specified tasks it helps to tell the model to look through the relevant sources before acting.”
  - 说明：模型差异：Opus 5.5 倾向于很快动手，原文建议明确要求先查再动。已发出的推荐需要更正时，O5 L86 建议只在错误会影响用户的结论或决定时才更正，并简短直接地说明。

## O13 默认决定成批列出

**态度：支持。** 需要和 CCBP 的访谈建议划清边界。

- F51 L836（Finish the whole task）：“Read ambiguity the way a careful colleague would: make routine judgment calls yourself, and check in only when different readings would lead to materially different work.”
  - 说明：约 36/45 题用户直接采纳推荐，说明这些属于"常规判断"，按原文应自己定、列出来供用户改。
- O55 L74（Unattended agentic runs）：“Status notes are welcome, and so are your recommendations on open decisions, but put them in the same message as your next tool call and carry on with whatever does not depend on the user's answer.”
  - 说明：原文把推荐和继续工作放在一起，不为等答复而停。
- CCBP L368（Let Claude interview you）：“Keep interviewing until we've covered everything, then write a complete spec to SPEC.md.”
  - 说明：这是限制：写 spec 阶段原文主张详细访谈，所以不是少问，而是把显而易见的题改成默认列表，把读代码定不了、影响大的题留作单独提问（与 CCBP L366 合起来看）。

## O14 最后一次 rebase 的风险前移

**态度：部分支持。** 频繁合入上游、在开工前先确认基线没坏，有依据；"定期试 rebase 并记录冲突"这个具体做法和"依赖的另一个 MR 未合入"未涉及。

- A07 L51（Running Claude in parallel）：“Claude works on the task, then pulls from upstream, merges changes from other agents, pushes its changes, and removes the lock. Merge conflicts are frequent, but Claude is smart enough to figure that out.”
  - 说明：原文每完成一个任务就合入上游，冲突分散处理，而不是攒到最后。原文同时用 CI 防止新提交破坏已有功能（见 A07 L66），对应"基线新代码调用了已迁走的接口"这类问题。
- EH L87（Getting up to speed）：“This ensured that Claude could quickly identify if the app had been left in a broken state, and immediately fix any existing bugs. If the agent had instead started implementing a new feature, it would likely make the problem worse.”
  - 说明：每次开工先跑基本检查确认基线状态；可以对应到每个里程碑开始前试 rebase 一次。
- MSPP L43（Measuring coordination）：“a very low fraction of these PRs were merged, which suggests a lack of coordination—the PRs often conflicted with one-another, at which point they were then abandoned.”
  - 说明：冲突拖到最后的后果在原文实验里是大量 PR 被放弃；这说明问题存在，但没有给出解法。

## O15 证据入库

**态度：部分支持（间接）。** 原文支持"日志写到文件、只回传引用和摘要"，也支持草稿性检查不必保留（见 F51 L856）；"哪些提交进 git、仓库体积多大合适"未涉及。原文 A07 的日志按提交号命名（见 A07 L29），但没说日志是否入库。

- A07 L76（Put yourself in Claude’s shoes）：“At most, it should print a few lines of output and log all important information to a file so Claude can find it when needed.”
  - 说明：原文要求完整日志存在文件里便于查找，并没有要求入版本库。
- MARS L104（Appendix，Subagent output to a filesystem）：“Subagents call tools to store their work in external systems, then pass lightweight references back to the coordinator.”
  - 说明：支持"大文件放外部存储、仓库里只留引用和摘要"的做法。
- CCBP L56（Give Claude a way to verify its work）：“Reviewing evidence is faster than re-running the verification yourself, and it works for sessions you weren't watching.”
  - 说明：这是限制：证据对无人值守的会话很重要，不能为了减小体积把证据删掉；要做的是把原始大文件和可审阅的摘要分开存放。

## O16 门禁报错写明修法

**态度：支持。**

- SABP L1016（Create verifiable intermediate outputs）：“Make validation scripts verbose with specific error messages such as "Field 'signature\_date' not found. Available fields: customer\_name, order\_total, signature\_date\_signed" to help Claude fix issues.”
  - 说明：直接支持报错写清缺什么、可选项是什么；对"按作者时间核对"这条规则，报错应说明别的分支上的提交也会被算进去、该怎样处理。原文还要求脚本自己处理错误情形，不要留给模型去猜（见 SABP L871）。
- A07 L76（Put yourself in Claude’s shoes）：“if there are errors, Claude should write ERROR and put the reason on the same line so grep will find it.”
  - 说明：原因和错误标记写在同一行，方便模型 grep 到后直接修。
- CCBP L196（Write an effective CLAUDE.md）：“Common gotchas or non-obvious behaviors”
  - 说明：该行在"应写入"一列。门禁会把并行子代理在别的分支上的提交也算进去，属于不看门禁代码就想不到的行为，应在 SKILL 正文写明，门禁再负责拦截。

---

## 原文有、16 条未覆盖的做法（5 条）

**1. 回合结束时由外层框架判断是否真的做完，并限制自动续跑次数。**

- O55 L61（Unattended agentic runs）：“Treat a text-only end of turn as a report rather than as proof the task is done.”
- O55 L61（Unattended agentic runs）：“You can also state the completion condition up front and have a separate, smaller model check the conversation against it at each end of turn, returning its reason as the next user message when the condition isn't met.”
- CCBP L51（Give Claude a way to verify its work）：“runs your check as a script and blocks the turn from ending until it passes.”
- 说明：本次 owner 在中断后停了 10.5 小时。若有完成条件检查，回合结束时会发现交付条件未满足，并以 user message 让它继续，而不是一直等人。

**2. 压缩前写明摘要必须保留什么。**

- CCBP L410（Manage context aggressively）：“Customize compaction behavior in CLAUDE.md with instructions like `"When compacting, always preserve the full list of modified files and any test commands"` to ensure critical context survives summarization”
- F51 L848（Tell the model what to preserve in compaction summaries）：“(3) anything that was asked for, decided, agreed, ruled out, or established as a preference, constraint, or boundary — stated exactly”
- 说明：owner 会话压缩了两次。O9 只讨论了少占上下文，没有讨论压缩时保留什么；冻结版本号、已确认的口径修改、用户授权范围都属于应逐字保留的内容。

**3. 检查者该报什么要校准，两处原文取向不同。**

- CCBP L565（Add an adversarial review step）：“Tell the reviewer to flag only gaps that affect correctness or the stated requirements, and treat the rest as optional.”
- O5 L16（Capability improvements）：“If your review prompt says "only report high-severity issues" or "be conservative," the model may follow that instruction literally and report less; ask it to report everything and filter in a separate pass instead.”
- 说明：里程碑检查和最终跨模型验证的 prompt 都会碰到这个取舍。按 O5，过滤宜放在单独一步，不要写进检查者的 prompt。

**4. 验收看最终状态，并包含应当失败的输入。**

- MARS L100（Appendix，End-state evaluation）：“Instead of judging whether the agent followed a specific process, evaluate whether it achieved the correct final state.”
- MARS L100（Appendix，End-state evaluation）：“For complex workflows, break evaluation into discrete checkpoints where specific state changes should have occurred, rather than attempting to validate every intermediate step.”
- BMAS L353（The early victory problem）：“Direct the verifier to attempt inputs that should fail and confirm they do.”
- 说明：本次 3 处口径冲突中，S04 的"请求数等于 Inspector 条数"依赖暂停发生的时机，属于对中间过程计数。按原文，检查点应写成"某个状态应当已经出现"，对时机不敏感，冻结前更容易核实。

**5. 同一问题纠正超过两次，就换新会话重来。**

- CCBP L394（Course-correct early and often）：“If you've corrected Claude more than twice on the same issue in one session, the context is cluttered with failed approaches.”
- CCBP L394（Course-correct early and often）：“A clean session with a better prompt almost always outperforms a long session with accumulated corrections.”
- HD L60（The architecture）：“The agents were run as one continuous session across the whole build”
- 说明：这条是人工介入方式。交付中为 3 处口径冲突提问 6 次、重新冻结两次；按 CCBP，同一问题纠正超过两次时，应考虑带着整理好的结论换新会话；但 HD 说明新模型在单个连续会话里也能完成长构建，所以是否换会话要看会话里失败尝试积累了多少，而不是固定规则。
