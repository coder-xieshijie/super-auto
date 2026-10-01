---
id: research-goal-v2-deliver-trace-deviation-change-list
recorded_on: 2026-10-01
timezone: Asia/Shanghai
source: dev-skills main `4c45165`（含 #25）的 deliver、core-spec 现行文字与脚本
scope: “交付中验收口径不一致时由 owner 自定、记偏差、跨家族验证者判断是否放宽”这一改动的具体落点；用户 2026-10-01 同意方向与清单（milestone-check.md 的半句不加），已提 coder-xieshijie/dev-skills#26
---

# 改动清单：验收口径偏差由 owner 自定，验证者判断是否放宽

讨论见[讨论记录“逐项讨论”](../../discussions/2026-10-01-goal-v2-deliver-trace-review.md)。三家依据：OpenAI ExecPlan“Resolve ambiguities autonomously”、决策日志写清原因（PL L34、L36）；Anthropic“keep building under stated assumptions”（F51 L836），验收项不许执行者改（EH L53）；Lauren 默认答案加推翻词（poteto-mode SKILL:20），不许为交差放宽验收（autonomous-run:11），放宽要验证者证明、上层会签（autopilot-full:10）。

## 1. 要解决的事

MR 7595 交付中三次停下（S04、S05、S09）都是同一类：spec 规定的产品行为清楚，实现也符合 spec，只是 verify 的检查方法和观测工具对不上。按现行 deliver，这属于“停下”第 1 种，要用户决定、用 core-spec 改 verify、重新冻结。6 次提问、约 52 分钟等待、两次中途冻结。

## 2. 概念

**口径偏差**：verify 某个检查点按字面判不了或必然判错，而 spec 规定的产品行为清楚、实现符合 spec。例如拿两个观测源对数，观测工具不记录被取消的请求（S04、S05）；检查范围把与本需求无关的辅助请求算进去（S09）。

不属于口径偏差、仍按“停下”第 1 种处理的：spec 自相矛盾；缺一个会改变产品行为的决定。

和 #25 已有的“用户改了 spec、verify 并重新确认”的关系：两条路径并存。口径偏差不改冻结文件，由验证者把关；用户决定改文件的，仍走重新确认。

## 3. dev-skills 的改动（一个 PR）

### deliver/SKILL.md

| 位置 | 现在 | 改为 |
|---|---|---|
| “停下”第 1 种（第 73 行） | spec 自相矛盾，或缺少一个会改变场景判定结果的决定。 | spec 自相矛盾，或缺少一个会改变产品行为的决定。verify 的检查方法与 spec 对不上、产品该怎样表现已经清楚时，不停，按“口径偏差”处理。 |
| “要求”里“绑定命令”之后（第 55 行后）新增一段 | 无 | **口径偏差。** spec 规定的产品行为清楚、实现也符合 spec，但 verify 某个检查点按字面判不了或必然判错时，你自己定改用的判定方法，不停下，不改 verify.md。按计划格式在 plan.md 记一条，写明字面为什么不成立、证据和改用的方法；verify 里用同一判定方式的检查点一并列出、一并处理。最终的独立验证者逐条判断偏差是否放宽了验收；判为放宽的按“停下”第 1 种交给用户。 |
| 独立验证的命令（第 62 行） | `run-verifier.mjs … --verify <verify.md> …` | 加 `--plan <plan.md>`，脚本从 plan.md 取口径偏差交给验证者 |
| “MR”一节（第 88 行后） | 有“验收文档改动”一条 | 新增一条：口径偏差：每条偏差、改用的判定方法和证据、验证者的判断；写明推翻某条后要重跑哪些场景 |
| “汇报”一节（第 100 行后） | — | 新增一条：口径偏差的条数，以及验证者判为放宽、需要用户决定的 |

### deliver/references/plan-format.md

在“决策日志”之后新增一节：

````markdown
### 口径偏差（持续更新）

verify 某个检查点按字面判不了、而产品行为已由 spec 规定清楚时，记一条。编号固定，`check-delivery.mjs` 按编号核对验证报告：

```text
- D1 S04 检查点 3；同类：S05 步骤 3
  - 字面：完成时请求数 = Inspector 条数
  - 不成立的原因：Inspector 只保存成功的调用；暂停打断已发出的请求时，spec R20 要计数，Inspector 不记（运行 <编号>：7 对 6）
  - 改用：请求数 = Inspector 条数 + 故障注入代理日志中已发出、被暂停取消的主执行请求数
  - 推翻后重跑：S04、S05
```
````

### deliver/references/verifier-brief.md

| 位置 | 改动 |
|---|---|
| 开头的输入清单 | 加一项：plan.md 记的口径偏差（由 `run-verifier.mjs` 交给你，不靠 owner 的验证输入） |
| “要做的事”第 2 步末尾 | 加：有口径偏差的检查点，先判断偏差是否成立、改用的方法是否放宽了验收（例如不再检查 spec 要求的某个结果、放松数值、把应计入的排除掉）。成立且没有放宽的，按改用的方法判定；不成立的，按 verify 字面判定；放宽了的，这个检查点记 FAIL，说明以“口径偏差放宽”开头 |
| “报告格式”的表后各部分 | 加一部分：**口径偏差**：只在调用说明列出口径偏差时写，每条一行 `D<n>：成立|不成立；未放宽|放宽；理由` |

### deliver/references/milestone-check.md（可选）

“看证据”一步加半句：plan.md 记了口径偏差的检查点，按改用的方法看证据，同时指出偏差会不会让某条 spec 要求不再被检查。作用是在里程碑阶段提前发现放宽；最终把关仍在验证者。可以先不加，看下一个需求。

### deliver/scripts/run-verifier.mjs

- 新增参数 `--plan <plan.md>`；从“口径偏差”一节取出各条，原文附在给验证者的调用说明里（与 #25 指向第一次交接的做法相同），要求按验证说明“口径偏差”一节报告。
- 调用记录 `.run.json` 加 `deviations: ["D1", …]`。
- plan.md 有口径偏差而没给 `--plan` 时报错退出。

### deliver/scripts/check-delivery.mjs 与 report-format.mjs

完整检查新增一项，报错写明怎样修：

1. 从 plan.md 读出口径偏差的编号；没有就跳过。
2. 调用记录的 `deviations` 与 plan.md 一致；不一致说明验证之后又加了偏差，要求重新验证。
3. 报告有“口径偏差”一节，每个编号都有判断。
4. 有判为“放宽”的：不通过，报错写“口径偏差 D<n> 被验证者判为放宽验收：按 deliver 停下第 1 种交给用户”。
5. 全部未放宽：通过，并在输出里列出各条，供 MR 描述使用。

`report-format.mjs` 增加对这一节的解析。

### core-spec/SKILL.md

第 175 行“交接之后 spec 或 verify 需要改变时，deliver 会停下”改为：交接之后需要改变产品行为的决定时，deliver 会停下；verify 检查方法与 spec 对不上的口径偏差，由 deliver 记录、独立验证者判断，不回到本 Skill。

### 测试

照 #24、#25 的做法，在本仓库写一组用例脚本（`deliver-deviation-cases.sh`），覆盖：无偏差时行为不变；有偏差但没给 `--plan`；验证后新增偏差；报告缺偏差一节；判为放宽；全部未放宽。改前的脚本应有若干条不通过，原有各组用例全部通过。

## 4. 本仓库的改动

- [复杂需求交付流程](../../process/complex-requirement-delivery.md)：“交付中停下的情况”“交付中改验收文档”两行按上面改写，版本 v0.22，修订记录写原因与用户原话（方向已在本轮写入，实现状态待 PR）。

## 5. prompt 的净变化

deliver 正文：改一句（停下第 1 种）、加一段（口径偏差，四句）、MR 与汇报各加一条；plan-format 加一节；verifier-brief 加一条输入、一句判定、一节报告格式；core-spec 改一句。其余落在 `run-verifier.mjs`、`check-delivery.mjs`、`report-format.mjs`。

## 6. 待用户决定

1. 清单是否照此提 PR；milestone-check.md 的半句加不加。
2. 合入后是否通知在途的 MR 7595：它还有 M3、M4、M6 的场景要跑，可能再遇到口径问题。

## 7. 执行结果（2026-10-01）

- 用户：“按清单提 PR，可选的那半句先不加”。
- [coder-xieshijie/dev-skills#26](https://github.com/coder-xieshijie/dev-skills/pull/26)，分支 `shijie/deliver-acceptance-deviation`（worktree `dev-skills-deliver-acceptance-deviation`），两个提交 `c5b9d5a`、`452fe22`；未合入。
- 与清单的差别：Codex 审查后，偏差原文改为写进报告旁的 `<报告>.deviations.md`（不再放在命令行里），调用记录存每条的 sha256；plan.md 的条目要求字面、不成立的原因、改用、推翻后重跑四项都不能空；新增共用模块 `scripts/deviations.mjs`；另改了 dev-skills 的 README 与 `docs/deliver-design.md`。
- 验证：[deliver-deviation-cases.sh](deliver-deviation-cases.sh) 58 个断言全部通过，改前的脚本 41 个不通过；原有七组用例全部通过；链接检查通过。
- Codex（gpt-6-astra，high，session `01a0f6b6-97ff-79d2-bf08-805c4950ba56`）报 6 条（4 条 P1），都已修正，修正后没有再送审。
