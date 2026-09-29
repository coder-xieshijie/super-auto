---
id: subagent-vs-cross-model
status: 候选，未经用户确认
created_on: 2026-09-29
timezone: Asia/Shanghai
---

# 独立验证：用 subagent，还是换一家模型开新 session

对象：deliver 的独立验证（C4、C5）。当前做法是由 owner 用另一家模型的 CLI 开新 session（`codex exec` / `claude -p`），对方不可用时降级为同家族 subagent。来源编号见 [design.md](design.md)。

## 一、三家原文

| 来源 | 原文 | 用什么验证 | 要不要换模型家族 |
|---|---|---|---|
| Anthropic S7 | "Before treating a task as done, have a subagent review the diff in a fresh context and report gaps." 新上下文的 subagent "sees only the diff and the criteria you give it, not the reasoning that produced the change" | subagent | 没要求 |
| Anthropic S9 | "Separate, fresh-context verifier subagents tend to outperform self-critique." 长任务中按间隔 "verifying your work with subagents against the specification" | subagent，任务进行中按间隔验证 | 没要求 |
| Anthropic S5 | 把干活的 agent 和评判的 agent 分开是有效的办法，但评判者仍然倾向于放过 LLM 的产出；"Out of the box, Claude is a poor QA agent"。靠反复读评判日志、对照人的判断、改评判提示词，才调到可用。"tuning a standalone evaluator to be skeptical turns out to be far more tractable than making a generator critical of its own work" | 独立的评判 agent，与生成方同一家模型 | 没要求；关键在调教评判提示词 |
| OpenAI S1 | 让 Codex 先自己审改动，再请本地和云端的其他 agent 审，"almost all review effort towards being handled agent-to-agent" | 其他 Codex agent | 没要求 |
| OpenAI Codex subagents | 示例："Review this branch with parallel subagents…"；subagent 可以配置不同的模型和推理强度 | subagent | 没要求 |
| Lauren L1 `orchestrate` | "Scale verification to the unit." 验证只是一条便宜命令时，由 worker 自己跑、协调者抽查；"A dedicated verifier agent (on a different model family than the worker) is for units whose verification is expensive, judgment-laden, or high-blast-radius." 只重跑一条命令的验证 agent 是走形式 | 验证 agent。在 Cursor 里，subagent 可以指定任意家族的模型 | 验证昂贵、需要判断或影响面大时要求换家族 |

## 二、分开两件事

1. **新上下文**：验证者看不到作者的推理，只看 diff、spec 和判定标准。三家一致要求。subagent 和 CLI 开的新 session 都满足，在这一点上没有差别。
2. **换模型家族**：只有 Lauren 要求，而且只用于昂贵、需要判断或影响面大的验证。Anthropic 和 OpenAI 用同一家模型，靠调教评判提示词提高质量。

我们用 CLI 开新 session，唯一的原因是为了换家族。Claude Code 的 subagent 只能用 Claude 模型，Codex 的 subagent 只能用 OpenAI 模型。

## 三、对比

| | 同家族 subagent | 另一家模型的 CLI 新 session |
|---|---|---|
| 新上下文 | 有 | 有 |
| 与三家主流写法一致 | 与 Anthropic、OpenAI 的写法一致 | 与 Lauren 在高风险验证上的要求一致 |
| 模型盲点 | 与作者同一家，可能犯同样的错 | 不同家族，犯同样错误的可能更小（L1；dev-skills agent-prompt-rules 二-7） |
| 运行应用 | 继承 owner 的权限和环境，直接能跑 | 要单独配置沙箱、网络和目录权限；`claude -p` 在本机未登录 |
| 结果返回 | 自动回到 owner | 写文件，owner 读回 |
| 可查证据 | Claude Code 会保存 subagent 的对话记录 | CLI 输出 session id 和模型，Codex 有会话日志 |
| 能否被 owner 跳过 | 能，要不要启动由 owner 决定 | 能，同上。两者都需要调用记录加机械检查，或改由作者以外的一方派发 |
| 成本与稳定性 | 低，少一层外部依赖 | 高，多一个 CLI 的登录、限流、网络问题 |
| 效果数据 | 本仓库没有 | 本仓库没有 |

## 四、建议

**subagent 和 CLI 新 session 只是两种启动方式。** 决定用哪种，要看这一处验证需不需要换模型家族。

| 验证 | 需要换家族吗 | 依据 | 用什么启动 |
|---|---|---|---|
| 每个里程碑的自验 | 不需要 | L1：验证便宜时由 worker 自己跑；S9：长任务中按间隔用新上下文 subagent 对照 spec 验证 | 现在由 owner 自己跑场景。试跑中如果出现"做到后面才发现前面坏了"，再加同家族 subagent 按间隔验证，成本低 |
| 最终独立验证（C4、C5） | 需要 | L1：昂贵、需要判断或影响面大的验证用另一家族。最终验证要跑全部场景、对照 spec 审代码，是无人值守流程的最后一道关，三个条件都满足。dev-skills agent-prompt-rules 二-7："同一模型、相近上下文的多个 agent 会犯同样的错" | 在 Claude Code 和 Codex 里，subagent 只能用本家模型，所以只能用 CLI 开新 session。如果宿主的 subagent 能指定另一家模型（Cursor 可以；MCode 待核实），就用 subagent，更简单 |
| 定义阶段查漏（core-spec 第 7 步） | 需要，你已决定 | 你 2026-09-29 的决定 | CLI，只读，`codex exec -s read-only` 已跑通 |

Anthropic 和 OpenAI 用同家族的新上下文做验证，所以同家族 subagent 不算违背三家。但在"最后一道关"这个位置，Lauren 的规则和你自己的规则都要求换家族，所以维持现在的做法。

真正要投入的是下面三件：

1. **调教验证说明（S5）。** Anthropic 的经验是评判者一开始会放水，靠读它的日志、对照人的判断、改提示词才调到可用。试跑时用 goal-v2 当时漏掉的问题校准 `verifier-brief.md`。
2. **让跨家族调用稳定。**
   - 登录 `claude` CLI，这样在 Codex 里也能调用 Claude；
   - 把验证者能用的环境、profile 和测试数据范围写进调用输入（另一个会话的 [agent-prompt-rules 审查](prompt-rules-audit.md) 第 18 条）；
   - 留下调用记录，并交给脚本检查（[deliver-new-sessions.md](deliver-new-sessions.md) 第四节）。
3. **另一家不可用时，不静默降级。** 采纳同一份审查第 17 条：交付阶段没人再看，降级为同家族后不能宣称可合入，按"缺环境"停下找你。定义阶段的查漏之后还有你的确认，所以保留降级加标注。

**用数据检验。** 前 1–2 个试跑需求可以额外跑一次同家族 subagent 验证，和跨家族验证对比各自发现的真问题和误报。如果同家族从不漏掉跨家族能发现的问题，再考虑简化（依据 S5、L1 PR #419：逐个删组件并对照）。

## 五、待你决定

1. 最终独立验证维持跨家族；另一家不可用时停下，不降级到可合入。
2. 里程碑中间暂不加 subagent 验证，试跑出现问题再加。
3. 前 1–2 个试跑需求，是否额外跑同家族 subagent 验证做对比。
