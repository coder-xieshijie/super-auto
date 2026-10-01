---
id: research-skills-consistency-change-plan
recorded_on: 2026-10-01
timezone: Asia/Shanghai
source: 本轮讨论中用户确认的决定（流程文档 v0.24–v0.30）；dev-skills main `74ae69d`
scope: 这一轮要改的全部内容、改法与验证方式；一个 dev-skills PR 加本仓库的记录改动。方案待用户确认后实施
---

# 本轮改动方案

讨论过程见 [2026-10-01 开发流程 Skill 一致性检查](../../discussions/2026-10-01-skills-consistency-check.md)，检查明细见 [checks.md](checks.md)。

## 1. 结论到改动的对照

| 用户确认的结论 | 改动 | 解决的发现 |
|---|---|---|
| 产出只看 dev-skills，本仓库只做记录（v0.25） | grill 模板变成 core-grill；流程说明写进 dev-skills README；本仓库流程文档改为演进记录 | F5、F6、F11 |
| 一个 PR（v0.26） | 下面 dev-skills 的改动合成一个 PR | — |
| core-grill 自成一体（v0.27） | 新建 `skills/core-grill/` | F5 |
| 质量与测试意见不拦合入（v0.28） | 验证说明加两项；owner 逐条改或写理由，列进 MR | 第 3 轮讨论的两个缺口 |
| 60 分钟一个周期，同一会话续接（v0.28） | `cross-model.md` 写命令；验证者每验完一个场景写一行结果 | F2、F9 |
| 全程不停，决定清单放最前，不可逆操作前停（v0.29） | deliver 重写“停下”“口径偏差”“自主决定”等段；plan 与 MR 开头放决定清单 | F3、F7、F8、F15 |
| 决定先问另一家模型（v0.29） | deliver 一段话加 `cross-model.md` 一条只读命令 | — |
| 流程要轻，只靠很轻的 prompt，留一个百行结果检查（v0.29、v0.30） | deliver 11 个脚本删到 1 个；正文不再复述脚本 | F1、F4、F10、F12、F14、F16 |
| 查漏加“现有事实对代码核对”（v0.30） | `gap-check.md` 加一项 | 减少交付中的决定 |
| agent-prompt-rules 跟上两家最新写法（第一轮建议，随 PR 一起） | 改 4 处、补 4 条、更新原文存档 | 研究目录第 2 节 |

不做：凭据泄露即时通知；Stop 钩子；Agent Lord 编排（F13）。

## 2. dev-skills 的改动（一个 PR）

### 2.1 新建 core-grill

```text
skills/core-grill/
  SKILL.md              约 2.5–3 KB
  agents/openai.yaml    allow_implicit_invocation: false
  references/context-format.md、adr-format.md   改写自上游，注明来源
```

SKILL.md 写这几件事：

- 开头收四个输入：目标、完成条件、授权（能否推送、开 MR；不可逆操作一律留给用户）、范围。能从仓库查到的不问。
- 一轮一轮问：每轮问当前所有前提已定的问题，每题给推荐答案；事实自己查（可以派子代理），不问用户。
- 提问边界：只问会改变用户可见结果的决定；其余自己定，列成默认决定，写理由和怎样推翻。
- 术语当场写进 `CONTEXT.md`；ADR 只在难以反悔、没有上下文会让人意外、确有取舍三条都满足时写。
- 结束：把用户答过的决定和默认决定写进一份决定汇总（问题、选项、用户原话或默认理由），请用户确认一次。这份汇总就是 core-spec 第 7 步查漏要的“原始约定”。然后交给 core-spec。

来源记在 `docs/core-grill-design.md`：mattpocock-skills `74ca5fe` 的 grilling、domain-modeling，MIT 许可；保留了什么、改了什么（“每个分支都问到”改成只问会改变可见结果的）。上游 Skill 继续装着，用于流程以外的讨论。

### 2.2 deliver 重写

正文目标约 4,000 字（现在 7,945 字），结构如下，最重要的放前面：

1. **你是 owner**：做到 MR 可合入，完成标准三条：verify 全部场景在最终代码上跑通；另一家模型的独立验证通过；CI 通过、评审意见处理完。
2. **全程不停**（放在开头）：
   - 只在不可逆操作前停：合入、强推共享分支、删除共享数据、对外发消息、改共享环境。
   - 其余做不了的（缺权限、环境、卡住）标明原因，先做完别的，列进决定清单。
   - 需要决定时：spec 没定、会影响用户看到的结果或验收判定的选择，先用只读命令问另一家模型（问题、spec 原文、可选做法、证据，不给自己的倾向），意见不同在同一会话再谈一轮；然后自己定、继续做。不影响结果的实现选择自己定。
3. **决定清单**：放在 plan.md 和 MR 描述最前面，按影响排序。每条写：决定、理由、另一家模型的意见、推翻后要改什么和重跑哪些场景。包括产品上的默认做法、verify 按字面判不了时改用的判定方法、spec 把现有事实写错时的更正、做不了的部分。spec、verify 不改。
4. **开工**：检出 MR 的源分支，运行 `check-delivery.mjs --frozen`，写 plan.md。
5. **里程碑**：实现，跑这个里程碑的场景和质量命令；做完让一个新的子代理（不指定模型）对照 spec 查一遍，只报告。
6. **独立验证**：按 `cross-model.md` 的命令请另一家模型验证最终代码，60 分钟一个周期，没做完在同一会话续接，失败自己判断下一步。验证者列出的代码质量和测试覆盖意见，逐条改或写理由。
7. **MR**：决定清单在最前；CI、评审意见；运行 `check-delivery.mjs`；到合入前停，告诉用户可以合入。
8. **汇报**：按 explain-as-fool 写。

`references/` 调整：

- `plan-format.md`：只留冻结输入（交接提交、owner 的模型）、决定清单、进度、意外与发现、里程碑、验证与验收（场景与命令）、结果与复盘。去掉口径偏差单独一节、涉及路径列、各种放行行。
- `verifier-brief.md`：加三项：逐条判断决定清单是否放宽了验收或违背 spec 的意图；按 review-rules 列代码质量意见；列新增或改变的行为有没有测试覆盖。后两项不影响 PASS。每验完一个场景就把结果写进证据目录。续接时从没验完的场景接着做。报告格式只固定 `head:`、`verdict:`、`验证模型：` 三行和结果表。
- `milestone-check.md`：缩成一段，不再分代码、证据两部分，不再要求报告模型 ID。

`scripts/`：

| 现在 | 之后 |
|---|---|
| `check-delivery.mjs`、`read-handoff.mjs`、`handoffs.mjs`、`report-format.mjs`、`model-family.mjs` | 合成一个 `check-delivery.mjs`，约 150 行 |
| `run-verifier.mjs`、`milestones.mjs`、`record-milestone-check.mjs`、`deviations.mjs`、`select-scenarios.mjs`、`report-reuse.mjs` | 删除 |

新的 `check-delivery.mjs` 只查结果：

1. MR 上最近一次交接提交（带 `Frozen-Spec`、`Frozen-Verify` 两行）记的 sha256，与 head 上两份文件一致。开工用 `--frozen` 只查这一项。
2. 每份验证报告的 `head:` 等于 MR head；或者报告之后只改了文档、测试文件。
3. 每份报告 `verdict: PASS`。
4. 报告里的验证模型与 plan.md 记的 owner 不是同一家。

可以给多份报告（分段验证时），每份都要满足 2–4。是否覆盖全部场景由验证者对照 verify 负责，并在 MR 里逐个列出，不由脚本解析场景表。用户放宽跨模型要求、里程碑顺序放行这类开关都去掉：做不到的列进决定清单，由用户合入前决定。

### 2.3 core-spec

- `references/gap-check.md` 加一项：spec、verify 写到的现有产品事实（快捷键、文案、入口名、默认值、设置项）逐条对代码核对，写出处，核对不了的报出来。
- 第 9 步末段：交付中 deliver 不再回到 core-spec；只有用户看过决定清单后要重写 spec 时，才按本 Skill 更新并重新交接。
- “交付与授权”去掉“能否合入”：合入是不可逆操作，始终由用户在交付后做。
- `references/cross-model.md`：删去 `run-verifier.mjs` 的说明，改为三类命令：查漏（只读）、交付中的决定咨询（只读，可续接）、独立验证（不带沙箱，用 `perl -e 'alarm 3600; exec @ARGV'` 包住实现 60 分钟周期，macOS 没有 `timeout`；三个 CLI 的续接命令 `codex exec resume <id>`、`claude -p --resume <id>`、`mcode exec --session <id>`）。
- 去掉规则里夹着的历史和日期（F16），原因留在设计记录。
- `freeze.mjs` 不改。

### 2.4 agent-prompt-rules

按[研究目录](README.md)第 2 节：

- 改：一-2 与二-5 区分“再检查一遍”和“跑真实检查”；一-6 子 agent 用不用是成本边界；总原则区分背景和约束。
- 补：不向作者描述评分者；不把一次失误写成永久规则、不写历史；最重要的约束放 SKILL.md 开头；删改后在新 session 对照运行；两条规则冲突时写明哪条优先。
- 原文存档：新增 Prompting Claude Sonnet 5.5、prompt-audit、Codex skill-creator；更新有改动的四页；三个 Codex 页面改新地址；`check-links.mjs` 通过。

### 2.5 README 与设计记录

- README 加“开发流程”一节：A 仓库准备、B 定义（core-grill → core-spec）、C 交付（deliver）、D 回流；每个阶段用户做什么（回答问题、确认一次决定汇总、确认一次 spec 和 verify、合入前看决定清单并合入）。Skill 表加 core-grill；deliver 安装依赖补 review-rules；删去对已删脚本的描述。
- `docs/deliver-design.md`、`docs/core-spec-design.md` 各加一节：这次删了什么、为什么（查结果不查过程、用户 2026-10-01 的决定、三家依据），设计表里“三种情况”改正。新建 `docs/core-grill-design.md`。

### 2.6 测试与 CI

- 新 `check-delivery.mjs` 的用例放进 dev-skills（`skills/deliver/scripts/check-delivery.test.mjs`，零依赖，临时 git 仓库）：交接后文件被改、报告对应旧 head 且改了代码、只改了文档、verdict 不是 PASS、同一家模型、多份报告、找不到交接提交。
- CI 加一步跑这些用例。
- 本仓库 `research/` 下旧脚本的用例对应已删除的脚本，留作历史记录，文件头注明适用于 `74ae69d` 及以前。

## 3. 本仓库的改动（本地提交）

- `AGENTS.md`“开发流程文档”一节：当前流程以 dev-skills 为准；`process/complex-requirement-delivery.md` 记录流程怎样演进、为什么。
- 流程文档：第一节改为指向 dev-skills README 的一段说明；被取代的决定行标注取代版本；旧的第二至四节移到“旧流程（对照）”下。
- `process/grill-handoff-template.md` 改为一句指向 core-grill 的说明。

## 4. 验证

1. 新 `check-delivery.mjs` 的用例全部通过；故意改坏每项检查，确认对应用例失败。
2. 用 7595 的真实分支只读运行 `check-delivery.mjs --frozen`。
3. 行为探针：开新的子代理和 Codex 会话，只给新版 deliver，问 4 个情境题，看回答是否符合本轮决定：S24 那种快捷键写错；需要选一种交互；独立验证 60 分钟到点；准备合入。core-grill 同样问 2 题：一个只影响实现的问题要不要问用户；结束时交什么。
4. `check-links.mjs` 通过；Codex 审查整个 PR 的 diff，报出的问题逐条修或写理由。
5. PR 描述列出每处增删对应的决定和依据，以及正文、脚本前后的字数和行数。

## 5. 合入之后（需要用户分别同意）

1. 合入 PR，本机 dev-skills main 快进。
2. 安装 core-grill 的两个入口：`~/.agents/skills/core-grill` 指向仓库目录，`~/.claude/skills/core-grill` 指向前者。
3. 7595 正在用旧版 deliver。新版去掉了它依赖的里程碑记录和口径偏差格式；建议在它当前里程碑结束后投递一条消息：按新版继续，旧的记录不再需要，已有的口径偏差和事实更正并入决定清单。

## 6. 预计规模

| | 现在 | 之后（估计） |
|---|---|---|
| deliver SKILL.md | 7,945 字 | 约 4,000 字 |
| deliver references | 3 份，7,414 字 | 3 份，约 4,000 字 |
| deliver scripts | 11 个，2,399 行 | 1 个，约 150 行 |
| deliver 用例 | 191 条，放在本仓库 | 约 15 条，放在 dev-skills，CI 里跑 |
| core-grill | 无（本仓库模板） | 约 3 KB |
