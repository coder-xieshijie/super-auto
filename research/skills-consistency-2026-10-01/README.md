---
id: research-skills-consistency-2026-10-01
recorded_on: 2026-10-01
timezone: Asia/Shanghai
source: 本仓库已有三家调研；dev-skills `agent-prompt-rules` 及其 2026-09-28 原文存档；本轮新抓的 Anthropic、OpenAI 原文（raw/）；pstack 快照 `ecc249f` 与上游核查；dev-skills main `74ae69d`
scope: 综合三家的理论、开发流程、Skill 创建方式与 prompt 书写规则，对照 agent-prompt-rules 和两家截至 2026-10-01 的新内容，再检查开发流程相关 Skill 是否一致、是否符合用户的决定
---

# 三家方法综合与开发流程 Skill 检查（2026-10-01）

讨论记录见 [2026-10-01 开发流程 Skill 一致性检查](../../discussions/2026-10-01-skills-consistency-check.md)。本目录的文件：

| 文件 | 内容 |
|---|---|
| 本文 | 三家综合、agent-prompt-rules 要改的地方、检查结论摘要、建议顺序 |
| [checks.md](checks.md) | 检查本身：范围、方法、16 条发现、逐条对照用户决定、体量统计 |
| [vendor-latest.md](vendor-latest.md) | Anthropic、OpenAI 截至 10-01 的新内容与 agent-prompt-rules 逐条对照（子代理整理，引文已存 [raw/](raw/)） |
| [lauren.md](lauren.md) | Lauren / pstack 的理论、流程、Skill 写法、prompt 规则与上游核查（子代理整理） |

“三家”指 OpenAI、Anthropic、Lauren（pstack），用户 2026-09-29 确认。下文引用的简写：HE = OpenAI Harness engineering，PL = ExecPlan，CCBP = Claude Code best practices，HD = Anthropic Harness design，EH = Effective harnesses，prompt-audit = Anthropic 官方 claude-api Skill 里的 `shared/prompt-audit.md`。

## 结论

1. **三家在主干上一致**：人给目标和可检查的完成条件；一个 owner 做到底；agent 能自己启动、操作、观察产品；检查交给不是作者的新上下文；必须每次发生的规则放进代码或钩子，文字只写边界；删改指令要靠对照运行来定。分歧集中在几个细节上：要不要在指令里写原因、要不要写验证指令、子 agent 由谁决定、Skill 能不能被模型自动调用。
2. **两家截至 10-01 没有改写 prompt 的原则。** 存档的 12 个持续更新页里有 4 页改了，都是加新模型（Claude Sonnet 5.5、GPT-6.1 Sol）。新增的依据里最有用的是 Anthropic 的 prompt-audit：它列出的过时写法我们都有，例如为一次事故加一条特例、越加越多，规则里写事故经过。pstack 上游在 `ecc249f` 之后没有 Lauren 的改动。
3. **agent-prompt-rules 大体仍成立，有 4 处措辞需要改**：区分“再检查一遍”的仪式和“跑真实检查”的手段；子 agent 用不用是成本边界，不只是方法；“最少的必要信息”要区分背景和约束；补上“不写历史”“最重要的放前面”“删改要对照运行”几条。见第 2 节。
4. **开发流程 Skill：机制都已落地，191 条用例全部通过。但有两处会影响 MR 7595 的收尾**：一是门禁认不出 7595 verify 里的 `S12b`、`S21b`、`S29b` 和 M01–M17，验证报告少了这 20 项也能过；二是独立验证默认 90 分钟就停，超时后 SKILL 让换一个 CLI，换了一样会超时。另有四处规则互相矛盾，流程文档有五处过时，deliver 正文从 #15 到现在长了七成。见第 3 节和 [checks.md](checks.md)。

## 1. 三家综合

### 1.1 理论：各自押注什么

| | OpenAI | Anthropic | Lauren（pstack） |
|---|---|---|---|
| 核心押注 | 环境与运行时。把仓库、应用、日志、指标做成 agent 读得懂、能操作的样子；“Humans steer. Agents execute.”（HE） | harness 结构和对模型怎么说。每个组件都是对“模型做不到”的一项假设，模型变强就删（HD）；先用单 agent，有明确收益才拆 | 先让单个 agent 可信，再谈并行；验证能力是基础设施；规则要落到结构里，“The instruction is the symptom.”（[lauren.md](lauren.md) 1.1–1.3） |
| 规则放在哪 | 进代码：自定义 lint、结构测试，报错里写修法；仓库是唯一的事实来源，AGENTS.md 只当目录（HE） | 进钩子：钩子确定执行，说明文件只是建议（CCBP）；prompt-audit：“Enforce in code what can be enforced in code” | 进 lint、元数据、运行时检查、脚本；文字只写机制管不到的事（`principle-encode-lessons-in-structure`） |
| 质量从哪来 | agent 互审到所有 reviewer 满意；最少的阻塞门禁，“改错便宜、等待昂贵”（HE） | 独立 evaluator，“Out of the box, Claude is a poor QA agent”（HD）；新上下文的验证子 agent 比自评好（Fable 5） | 评判改动的 agent 从不是写它的那个；验证者用不同模型家族；按 PR 和 head SHA 记验证账本 |
| 人在哪里 | 写目标和验收标准，在 Human Review 状态看结果 | 开头访谈写 spec，结尾审阅 | 交接时给目标、完成条件、权限和逃生口；待人决定的事带默认答案进 gates |
| 怎样改进流程本身 | 缺什么能力就补什么 | 一次去掉一个组件做对照（HD） | 种子缺陷、A/B 删指令，PR 里写明没测什么 |

### 1.2 整体开发流程

| 环节 | OpenAI | Anthropic | Lauren |
|---|---|---|---|
| 定义 | 目标文本就是完成标准（`/goal`）；提示里写 Goal、Context、Constraints、Done when（Codex Best practices） | 先访谈写 spec，再开新 session 执行（CCBP）；planner 只写产品级 spec，路径由 generator 定（HD） | 不写 spec，给能跑的检查：“Now the agent has three checks it can run”；先原型再设计 |
| 计划 | ExecPlan 由 agent 写，是活文档，只读它就能重新开始（PL） | 同一 session 先探索再计划；一句话说得清的改动不写计划 | 不信抽象计划，“abstract plans only give you the illusion of progress”；执行清单每格要有证据 |
| 实现 | 单个 agent 端到端：复现、实现、驱动应用验证、开 PR、回应评审、修构建 | 单 session 连续运行；新模型上去掉了 context reset | 每个 PR 一个 owner；实现强制委派给子 agent |
| 验证 | 应用按 worktree 启动、接 CDP，日志指标可查；agent 互审 | `init.sh` 加浏览器自动化，像用户一样测；独立 evaluator；完成前让新上下文审 diff | 在真实界面上验证，结论分三态；非作者独立出结论才合入 |
| 长任务与接续 | 一个 Codex 连续约 25 小时，计划和状态各一个文件 | 进度文件、JSON 功能清单；无人值守时由 harness 判断这一轮是否真的做完，最多续 2–3 次（Opus 5.5） | autopilot：root 约每 30 分钟审计，只把提交、推送等副作用算作进展；orchestrate：验证账本、gates、standing orders |
| 什么时候找人 | 只在需要判断时 | 破坏性操作、真正的范围变化、只有用户能给的输入 | 不可逆操作、产品或偏好决定、指令与现实冲突、重新规划后仍走不通 |

我们的流程（[流程文档 v0.23](../../process/complex-requirement-delivery.md)）三层都用：骨架主要来自 OpenAI（单 owner、活计划、可观测的环境、规则进代码），检查分层来自 Anthropic（新上下文检查）和 Lauren（跨家族验证），prompt 写法来自 Anthropic 和 Lauren。“先冻结 spec 和 verify、交付中只读”是我们自己加的前提，三家都没有（[approaches.md](../goal-v2-deliver-trace-2026-10-01/approaches.md) 第 2 节）。

### 1.3 Skill 创建方式

| 方面 | Anthropic | OpenAI | Lauren |
|---|---|---|---|
| 规范基础 | agentskills.io 开放规范；必填 `name`、`description` | 同一规范；另用 `agents/openai.yaml` 放界面、调用策略、工具依赖 | Cursor 插件；50 个 Skill 里 49 个关闭模型自动调用，由路由 Skill `poteto-mode` 按名字调用 |
| 谁能触发 | 有副作用、要控制时机的设 `disable-model-invocation: true`（Claude Code 文档） | 内置 skill-creator：不要因为操作敏感就设成只能显式调用，保持可发现，在真正执行变更前要授权 | 默认关闭自动调用 |
| description | 写做什么和什么时候用；第三人称；关键用途放前面（列表里会被截断） | 尽量短，前置触发词，写清边界；不列能力清单 | 两种固定句式：“Apply when …” 和 “Use for /x, '<口语>', or …” |
| 正文 | 500 行以内，references 只一层，写清什么时候读；压缩后每个 Skill 只保留前 5,000 tokens，最重要的放开头 | 入口在任务允许时尽量短，“A large upper bound is not a target”；简单的 Skill 不需要路由和额外文件 | 所有权声明、编号步骤、结尾 `Reply:`；原则类 Skill 带 Why；子 agent 模板放 references，原文传递 |
| 脚本 | 提供工具脚本，脚本自己处理错误 | “Prefer instructions over scripts unless you need deterministic behavior” | 优先给工具，“Default to building the lever”；脚本带测试，报错写明实际与期望 |
| 评测与迭代 | 先建评测再写；新 session 里带与不带 Skill 对照；skill-creator 插件做盲 A/B 和触发测试；prompt-audit：删改是假设，要测行为，不问模型 | 10–20 条提示的评测，含不应触发的；独立子 agent 前向测试，不给预期答案；“Prefer a narrow correction to accumulating universal rules” | 盲测：候选看不到任何 eval 字样；删指令做 A/B；不在任务中途改 Skill，另开 PR |

### 1.4 prompt 书写规则

**三家都有原文支持的共识：**

1. 写目标、完成标准和要交回的证据，不写步骤。prompt-audit：“State outcomes, constraints, and how to verify”；Lauren：“Give the agent a goal and a way to check it”。
2. 边界少而真，强调只留给确实被反复忽略的那一条。prompt-audit 1a 指出两个方向都有害：滥用强调会过度触发，残留的“尽量”“如果可能”会被当成可以少做。
3. 能由机制强制的不写成文字。
4. 不加“再检查一遍”这类仪式，但要给能运行的检查手段，把真实检查的输出当证据（Anthropic Reducing cost 博客、Sonnet 5.5 指南；Codex Best practices）。
5. 默认授权把事做完，只在不可逆操作、产品决定、拿不到的输入时停。GPT-6 Astra 会在等回答时继续做不受影响的部分。
6. 删改指令要靠对照运行来定，不靠问模型自己需不需要。
7. 不把一次失误写成永久规则，不写事故编号和“不再”这类相对说法（prompt-audit Group 2；Codex skill-creator；Lauren PR 329 删掉历史和理由）。

**分歧：**

| 问题 | Anthropic | OpenAI | Lauren | agent-prompt-rules 现在的取舍 |
|---|---|---|---|---|
| 指令里写不写原因 | 写（Fable 5；prompt-audit “prose for behavior, carrying the because”）；Claude Code 的 Skill 文档却说不叙述 how 或 why | 边界附原因（Codex Prompting） | 不写，“Tell it to do the thing and skip the reason”；理由只放在原则类 Skill | 一-4：每条附一句原因 |
| 写不写验证指令 | Opus 5 建议删；Fable 5 建议长任务按间隔用子 agent 验；Sonnet 5.5 在低 effort 时要求跑真实检查，高 effort 时不要自加评审 | Codex Best practices 要求跑检查；GPT-6 Astra 文章说测试类指令会引出多余的测试 | 验证委派给非作者，只认证据 | 一-2：写成证据要求，不加通用复查 |
| 子 agent 由谁决定 | Sonnet 5.5 高 effort 时会自派评审子 agent，官方建议不让它派 | Codex 本地版不指示就不派；GPT-5.6 指南建议写明什么时候派 | 实现强制委派 | 一-6：留给执行端 |
| 背景信息给多少 | prompt-audit：背景宁多勿少，“give the model more context than seems necessary”；约束逐条验证后再删 | skill-creator：只写会改变决定的 | 只写会改变决定的 | 总原则：最少的必要信息 |
| 脚本还是文字 | 提供工具脚本 | 默认文字，需要确定性时才用脚本 | 优先工具 | 二-10：每次都必须发生的交给脚本 |

### 1.5 截至 2026-10-01 的新内容

详见 [vendor-latest.md](vendor-latest.md)。

- 存档的 12 个持续更新页，4 页有改动，都与新模型有关；规范引用的锚点都还在。三个 Codex 页面已 301 跳转到 `learn.chatgpt.com`。
- 新依据：Prompting Claude Sonnet 5.5（09-28）、prompt-audit（08-13 起，09-29 最近修改）、Reducing cost and improving performance 博客的六类反模式（09-08）、Codex 内置 skill-creator 改版（08-13）、Codex Best practices。
- 窗口外（2026-07）、存档也没收的两篇相关文章：Claude 5 一代的 context engineering 新规则、用 Skill 做验证循环。
- Lauren：pstack 上游 main 比快照多 18 个提交，都没动 `pstack/`；pstack 最后一次提交是 9-23 的 #422（[lauren.md](lauren.md) 第 6 节）。

## 2. agent-prompt-rules 要改的地方（建议，未经确认）

依据 [vendor-latest.md](vendor-latest.md) 3.2、3.3 和 [lauren.md](lauren.md) 3.7、4.5。

| 条目 | 改法 | 依据 |
|---|---|---|
| 一-2、二-5 | 区分“再检查一遍”的仪式和“跑真实检查”的手段：前者不写；后者写进完成标准，给出能运行的命令，跑不了要说明哪项没跑、为什么。二-5 的“作者自查一律删掉”改成只删重读自己产出、自己确认的轮次，作者跑测试、脚本、清单并修复的不算 | Reducing cost 博客 “Verification rituals”；Sonnet 5.5 § Verification on coding tasks；agentskills.io Validation loops |
| 一-6 | 子 agent 用不用仍由执行端定；harness 默认不派（Codex 本地版）或容易多派（Sonnet 5.5 高 effort）时，写一条适用或不适用的条件，附上成本或上下文隔离的原因 | Sonnet 5.5 § Thoroughness；GPT-5.6 指南 § Multi-agent；Codex Subagents |
| 总原则 | “最少的必要信息”拆开：背景（受众、环境事实、质量标准、约束的原因）宁多勿少；行为约束逐条验证后再删 | prompt-audit keep list 1 |
| 新增 | 不向作者描述评分者，只写评分者会查的每一项要求 | prompt-audit 1c |
| 新增 | 一次失误不直接写成永久规则；规则只写当前要求，不写事故经过、PR 号、“不再”；同类特例多了合成一条原则 | prompt-audit Group 2、1d；Codex skill-creator；Lauren PR 329 |
| 三-2 补充 | 最重要、全程适用的约束放在 SKILL.md 开头 | Claude Code skills 文档 § Skill content lifecycle、§ Claude stops following a skill |
| 第四节补充 | 删改指令后，用几条真实请求在新 session 里对照改前改后，不以模型自评为准 | prompt-audit Step 7；Claude Code skills 文档 § Evaluate and iterate |
| 第四节补充 | 同一 Skill 里两条规则冲突时，点名哪条在什么情况下优先，不让执行端猜 | Lauren PR 422 |
| 原文存档 | 新增 Sonnet 5.5、prompt-audit、Codex skill-creator；三个 Codex 页面改新地址；替换有改动的四页 | [vendor-latest.md](vendor-latest.md) 第 5 节 |

不建议据此改的：OpenAI Cookbook 的人工分段审批流程、OpenAI Prompt engineering 指南里残留的“plan extensively”类旧建议。它们的权威性低于模型指南，也与 OpenAI 自己的最新指南相反（vendor-latest C7、C8）。

## 3. 开发流程 Skill 检查（摘要）

完整内容在 [checks.md](checks.md)。检查对象是 dev-skills main `74ae69d` 的 core-spec、deliver 及其引用的 Skill，本仓库流程文档 v0.23 和 grill 交接模板。

**已核实一致的：** 用户确认过的决定逐条都能在 Skill 或脚本里找到（checks.md 第 4 节）；deliver 现有五套用例共 191 条全部通过，链接检查通过；9 个 Skill 在 Claude Code 和 Codex 两边都设成只能手动调用。

**要处理的：**

| ID | 严重度 | 问题 |
|---|---|---|
| F1 | P0 | verify 的编号格式没有统一规定，门禁只认 `S01` 和证明方式写着“机械检查”的 `R01`。用门禁的解析器读 MR 7595 冻结的 verify，`S12b`、`S21b`、`S29b` 和机械检查 M01–M17 都认不出来，验证报告少了这 20 项也能过门禁 |
| F2 | P0（风险） | 独立验证默认 90 分钟就停，到点按“CLI 用不了”处理，SKILL 让换一个 CLI，换了同样会超时。7595 有 44 个场景 |
| F3 | P1 | deliver 第 51 行要求里程碑检查没有未解决的问题才进入下一个，第 53 行允许两轮后带着问题往下做 |
| F4 | P1 | “涉及路径写漏只会让重跑变多”不成立：漏写的路径如果被别的场景认领，这个场景会被漏选（已在临时仓库复现） |
| F5 | P1 | grill 模板让 grill 列“默认决定，用户有异议再改”，core-spec 规定“用户没有反对不等于批准”；两处都没写“默认决定进决定汇总，由用户确认” |
| F6 | P1 | 流程文档五处过时：#26 仍写未合入；第二至四节仍是旧流程；前六条决定已被取代未标注；`spec/` 与 `specs/` 两种写法；Skill 版本只指到 #12、#13 |
| F7 | P1 | 交付中重新确认验收文档时，门禁要 plan.md 里有用户原话，core-spec 却没把原话记到 deliver 读得到的地方 |
| F8–F16 | P2 | 完成条件与“最终 head 全量”说法不一；复验输入没有通道；两部分检查只靠 prompt；README 与设计记录过时；体量增长；已同意未做的机制；用例不在 dev-skills CI；“停下”位置靠后（粗估可能在压缩后保留的 5,000 tokens 之外）；规则里夹着历史 |

**与“少写 prompt、只做边界”对照：** deliver 正文从 #15 的 4,687 字长到 7,945 字，含限制词的句子从 30 句到 50 句，脚本从 3 个到 11 个。每次试跑暴露的问题都加一段正文和一道脚本检查，只有 #23 删过。这正是 prompt-audit 说的“patch accretion”。规则进脚本是三家的共识，做对了；没做的是把已由脚本强制的内容从正文删掉。

## 4. 建议的处理顺序（未经确认）

| 顺序 | 内容 | 形式 | 理由 |
|---|---|---|---|
| 1 | F1、F2 | 一个 dev-skills PR：解析器认得 7595 用到的编号，`freeze.mjs` 冻结前用同一解析器校验；超时用单独的返回码，SKILL 写一句按全集自验耗时设 `--timeout` | 机制改动；7595 收尾要用 |
| 2 | F3、F4、F7、F8、F9 | 一个 dev-skills PR，只改措辞，外加交接提交多记一行用户确认原话 | 规则互相矛盾，agent 只能猜 |
| 3 | F5、F6 | 本仓库直接改模板和流程文档 | 不涉及 dev-skills |
| 4 | agent-prompt-rules 更新（第 2 节） | 一个 dev-skills PR | 审查口径先定，再做减量 |
| 5 | 减量与结构（F12、F15、F16） | 一个 dev-skills PR：正文不再复述脚本查什么，开工动作合成一个脚本，条件分支移到 references，“停下”移到开头 | 不改行为；按“一次上一项”，下一个需求观察 owner 是否漏步骤 |
| 6 | F14 | 用例迁进 dev-skills，CI 里跑 | 脚本回归不靠人记得去跑 |

**需要用户决定的：**

1. F1 怎么统一编号：（a）verify 只允许 `S01`、`R01` 两种编号，机械检查写在要求表的证明方式里；（b）门禁也认带后缀的场景号、M 开头的机械检查、RG 开头的回归项，冻结前由脚本校验。建议 (b)，7595 已冻结的 verify 不用改。
2. F2 的超时：按场景数估默认值，还是要求 owner 每次显式给。
3. 顺序 1、2 是否在给 7595 投递消息之前合入。用户此前的安排是 PR 都合入、本机更新后再投递。
4. 流程文档第二至四节：移到“旧流程（对照）”下，还是改写成现行各阶段的说明。
5. agent-prompt-rules 是否这一轮就更新。
