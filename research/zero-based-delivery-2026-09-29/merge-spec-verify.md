---
id: merge-spec-verify
status: 候选，未经用户确认
created_on: 2026-09-29
timezone: Asia/Shanghai
---

# core-spec 与 core-verify 是否合并

对象：dev-skills main `97c230f` 中的 `skills/core-spec`、`skills/core-verify`（dev-skills#12 合入后）。来源编号见 [design.md](design.md)。

## 一、三家怎样放"要做什么"和"怎样算做完"

| 来源 | 要做什么 | 怎样算做完 | 谁写、几步 |
|---|---|---|---|
| OpenAI S2 | `Prompt.md`：目标与非目标、硬约束、交付物 | 同一个 `Prompt.md` 里的 "Done when"（检查项与演示流程）；`Plan.md` 里每个里程碑的验收标准和验证命令 | 人写一份 spec，验收写在里面 |
| OpenAI S3 `/goal` | Outcome、Constraints | Verification："tests, measurements, or review criteria that prove the work is complete"，三者写在同一个目标里 | 一步 |
| OpenAI S6 ExecPlan | Purpose / Big Picture | 同一份计划里的 "Validation and Acceptance"：怎样启动、观察什么、具体输入和输出 | agent 写一份文件 |
| Anthropic S7 | 访谈后写 `SPEC.md` | "end with an end-to-end verification step that proves the feature works"，写在同一份 spec 的结尾 | 一个提示完成访谈和写 spec |
| Anthropic S4 | 用户的 spec | `feature_list.json`：初始化 agent 按 spec 展开的端到端功能清单，每项带测试步骤和 `passes` 字段；编码 agent 只能改 `passes` | 同一个初始化 agent 在第一步产出；验收单独成文件，是为了只允许改 `passes` |
| Anthropic S5 | planner 把一两句话展开成产品 spec | 第一版在每个 sprint 前由 generator 和 evaluator 协商"sprint contract"，因为 spec 故意写得很粗；第二版去掉了 sprint，evaluator 在最后按 spec 评判 | 验收曾单独协商，后来取消 |
| Lauren L1 | 第一条指令 | 同一条指令里写完成条件和要看的证据（`06-verify-and-ship`："Put what done means in the first prompt"）；怎样操作应用在项目的验证 Skill 里 | 一步 |

结论：
- 没有一家把"写 spec"和"写验收标准"做成两个独立的工具或步骤。多数把验收写在 spec 或计划里。
- 验收单独成文件的只有 S4，原因是限定编码 agent 只能改 `passes` 字段，便于冻结。产出它的仍是同一个 agent、同一步。
- 三家真正要分开的是**评判的一方与实现的一方**（S5 的 evaluator、S7 的新 session 复查、L1 的"评判改动的 agent 从不是写它的那个"），不是 spec 与验收的作者。

## 二、现在两个 Skill 的实际关系

| 现状 | 说明 |
|---|---|
| 入口已是一个 | `core-verify` 第 1 步：没有 spec 时先按 core-spec 的规则生成 spec；发现 spec 缺口时也按 core-spec 更新 spec |
| spec 要等 verify 写完才算定稿 | 写 verify 时按"入口 × 状态"查出的缺口要回写 spec；查漏说明（`gap-check.md`）同时查 spec 自身、spec → verify、verify → spec |
| 确认和冻结是一次 | 用户一次确认两份文件，两份一起记 sha256，deliver 一起核对 |
| 重复的是过程 | 读会话找最终约定、向用户提最小必要问题、对照核对、最终回复，两个 Skill 各写一遍；core-verify 用"按 core-spec 的规则"引用，但读者要在两个文件间来回看 |
| core-spec 有单独用途 | dev-skills README：core-spec 也供 `design-for-review`、`plan-for-agents` 和给人的汇报使用，"各 Skill 可独立使用"；这些用途不需要 verify |

所以在交付流程里，两者已经是同一件工作：spec 不写完 verify 定不了稿，两份一起查漏、一起确认、一起冻结。拆成两个 Skill，只是让同一件工作的说明分散在两处。

## 三、建议：合并成一个 Skill，产出仍是两份文件

**合并什么：**
- 一个 Skill、一个命令，完成定义阶段 grill 之后的全部工作：收敛决定 → 写 spec → 按入口和状态查缺口并回写 spec → 写 verify → 另一家模型查漏 → 请用户一次确认 → 两份一起冻结。
- 过程只写一遍：找最终约定、提问规则、核对、最终回复。

**保持不变：**
- **两份文件。** spec 写"要做成什么"，给人看、给实现方看；verify 写"怎样判定"，给 owner 和独立验证者看。两份各记 sha256。deliver 的机械检查和"verify 只来自 spec"的规则都依赖这种分开。
- **顺序和规则。** 先定 spec，verify 只从 spec 来。靠 Skill 里的规则和查漏的"verify → spec"一项保证，不需要两个 Skill。
- **只要 spec 的用途。** 用户明确只要 spec（用于 design-for-review、plan-for-agents 或汇报）时，写完 spec 并核对后就交付，不写 verify、不查漏。这是完成条件的一种，不另设流程。

**写法：** SKILL.md 只写目标、步骤、完成条件和停下的规则，细节放进 references。可以整理为以下几份，其中后三份原本就在 core-verify 的 references 里：
- spec 的写法（原 core-spec 第 2–4 步）；
- verify 的写法（原 core-verify 第 2–5 步）；
- 查漏说明 `gap-check.md`；
- 跨模型调用 `cross-model.md`；
- 两个 worked example。

**名字：** 建议用新名字，例如 `core-define`，对应流程里的 B 定义阶段，避免用 `core-spec` 却产出两份文件造成误解。也可以沿用 `core-spec`，把 verify 写成它的第二部分。由用户决定。

**要一起改的地方（dev-skills 一个 PR）：**
- 新 Skill 目录，删去 `skills/core-spec`、`skills/core-verify`；
- deliver 的描述、跨模型调用的链接（原 `../core-verify/references/cross-model.md`）、"停下"一节里"由用户用 core-spec、core-verify 更新"的说法；
- README，以及 `docs/core-spec-design.md`、`docs/core-verify-design.md` 合并；
- 本仓库流程文档与 steps.md 的 B2、B3 两行。

两个 Skill 都还没装软链接，现在合并不影响已安装的环境。

**不合并的部分：** grill-with-docs 保持独立。它是外部仓库（mattpocock-skills）的交互式澄清工具，可以跨多轮使用。Anthropic S7 把访谈和写 spec 放在一个提示里；grill 要不要也并进来，等试跑后再看。

## 四、待确认

1. 是否合并。
2. 名字：`core-define` 还是沿用 `core-spec`。
3. 合并后是否立即提 dev-skills PR。
