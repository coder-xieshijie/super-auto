---
id: discussion-2026-10-01-skills-consistency-check
recorded_on: 2026-10-01
timezone: Asia/Shanghai
source: 本会话（Claude Code，claude-opus-5-5），用户原话逐字保存；两个子代理（general-purpose）的整理稿存于研究目录
scope: 三家方法综合，对照 agent-prompt-rules 与两家最新写法依据，检查开发流程相关 Skill 的一致性
---

# 开发流程 Skill 一致性检查：三家综合与对照

## 用户问题

2026-10-01，原话：

> 综合以下内容进行汇总分析：
> 1. 当前 3 家的理论、整体开发流程、skill 创建方式以及 prompt 书写规则；
> 2. 之前收集到的 agent for prompt；
> 3. 参考 Anthropic 和 OpenAI 最新的 prompt 书写规则。
>
> 综合汇总之后，再对当前 dev skills 中涉及开发流程相关的 skill 整体 check 一遍。因为现在已经改了很多，需要确认是否有不一致的地方, 是否符合预期。

理解：“3 家”按 2026-09-29 的确认指 OpenAI、Anthropic、Lauren（pstack）；“agent for prompt”按 [2026-09-30 的记录](2026-09-30-goal-final-delivery-trace-review.md)指 dev-skills 的 `agent-prompt-rules`。这是用户在 [MR 7595 复盘](2026-10-01-goal-v2-deliver-trace-review.md) 里说的“我还需要对当前的 skill 再做一轮 check”的那一轮。

## 过程

1. 读本仓库已有的三家材料（零基设计、approaches、两次复盘的 source-check）、流程文档 v0.23、grill 交接模板，以及 dev-skills main `74ae69d` 的全部流程类 Skill、references、脚本和说明文档。
2. 派两个子代理并行整理：一个抓取 Anthropic、OpenAI 截至 10-01 的新内容并与 agent-prompt-rules 逐条对照；一个整理 Lauren / pstack 并核查上游。两份整理稿和抓到的原文都存在研究目录。
3. 跑 deliver 现有的五套用例（191 条）和链接检查；用门禁的解析器读 MR 7595 冻结的 verify；在临时仓库复现 `select-scenarios.mjs` 的漏选；按提交统计 core-spec、deliver 的体量。
4. 想用接口实测 deliver 正文的 token 数，本机 `claude -p` 显示未登录，改为按字数粗估，结论标为未实测。

## 结果

资料：[研究目录](../research/skills-consistency-2026-10-01/README.md)（综合与摘要）、[checks.md](../research/skills-consistency-2026-10-01/checks.md)（检查明细）、[vendor-latest.md](../research/skills-consistency-2026-10-01/vendor-latest.md)、[lauren.md](../research/skills-consistency-2026-10-01/lauren.md)。

助手答复要点：

- 三家在主干上一致：目标加可检查的完成条件，一个 owner 做到底，agent 能自己操作和观察产品，检查交给不是作者的新上下文，规则进代码或钩子，删改指令要对照运行。分歧在写不写原因、写不写验证指令、子 agent 由谁决定、Skill 能否被模型自动调用。
- 两家截至 10-01 没有改写 prompt 的原则，4 个持续更新页的改动都是加新模型。新依据里最有用的是 Anthropic 的 prompt-audit。pstack 上游在 `ecc249f` 之后没有 Lauren 的改动。
- agent-prompt-rules 大体仍成立，建议改 4 处措辞、补 4 条（研究目录第 2 节）。
- 开发流程 Skill：用户的决定都已落地，191 条用例全部通过，两个客户端的手动调用设置一致。发现 16 条，其中：
  - P0：门禁认不出 7595 verify 里的 `S12b`、`S21b`、`S29b` 和 M01–M17，报告少了这 20 项也能过（F1）；独立验证默认 90 分钟到点后按“CLI 用不了”处理，换 CLI 一样会超时（F2，风险，未实测）。
  - P1：里程碑检查两轮后能不能往下做，正文两处说法相反（F3）；“涉及路径写漏只会让重跑变多”不成立（F4，已复现）；grill 的默认决定与 core-spec 的“没反对不等于批准”之间缺一步（F5）；流程文档五处过时（F6）；重新确认的用户原话没有交到 deliver 读得到的地方（F7）。
  - deliver 正文从 #15 到现在长了七成，含限制词的句子从 30 到 50，每次修复都加一段，只有 #23 删过。
- 建议顺序：先上 F1、F2 的机制改动，再修互相矛盾的规则，再整理本仓库的模板和流程文档，然后更新 agent-prompt-rules，最后做减量；用例迁进 dev-skills CI。

## 决定

本轮没有用户决定。待用户决定的五项见[研究目录](../research/skills-consistency-2026-10-01/README.md)第 4 节：F1 的编号方案、F2 的超时、F1 和 F2 是否在给 7595 投递消息前合入、流程文档第二至四节的处理、agent-prompt-rules 是否本轮更新。

本轮没有改 dev-skills，也没有改流程文档和 grill 模板。

## 待验证

- F2：7595 的最终独立验证实际要跑多久，还没有数据。
- F15：deliver 正文的 token 数是粗估，需要用接口实测；Claude Code 压缩后保留前 5,000 tokens 的说法来自官方文档，没有在本机复现。
- vendor-latest.md 记了几处没取到的内容：一篇博客结尾的清单是图片；Codex Best practices 的小标题在转换中丢失；claude.com 博客的文章清单可能不全。
- lauren.md 读过的 pstack PR 正文和两家在线页面只给了 URL，没有存进仓库。

## 后续：F1、F2 的决定与 P1 的建议

用户原话（2026-10-01）：

> F1 选 b
> F2 独立验证 60 分钟就停, 然后不按 cli 用不了, 分析停止的原因, 并让主agent 判断后续, 派生新的还是其他方案
>
> P1的问题, 你的建议都是什么?

“主agent”按上下文理解为 deliver 的 owner。

**决定（写入[流程文档](../process/complex-requirement-delivery.md) v0.24 决定表）：**

- F1 选 (b)：门禁和 `select-scenarios.mjs` 用同一个解析器，认带字母后缀的场景号、M 开头的机械检查、RG 开头的回归项；`freeze.mjs` 冻结前用它校验 verify。
- F2：独立验证 60 分钟就停；到点不算“CLI 用不了”，脚本分析停止原因，由 owner 判断后续。

dev-skills 尚未修改。

**F2 落地时要定的一处设计（助手提出，未确认）：** 7595 有 44 个场景，60 分钟内一次验完的可能性不大，owner 选“派生新的验证者接着验”或“分批验”时，几段验证的结果要能合起来通过门禁。现在 `check-delivery.mjs` 只认一份覆盖全部场景的报告。建议：`run-verifier.mjs` 加参数指定本次验哪些场景，同一个 head 可以有多段验证，每段都由另一家模型、都有调用记录；`check-delivery.mjs` 把同一 head 的几段合起来，要求合起来覆盖全部场景和机械检查，冒烟集、回归范围和代码审查至少有一段做完；验证说明要求验证者每验完一个场景就把结果写进证据目录，被停掉时已验的部分不丢。停止分析写成报告旁的一个文件：停止原因（总时长或停滞）、已用时间、最后一次写证据的时间、已有结果的场景、日志末尾。

**P1 的建议（未确认）：**

| ID | 建议 | 改哪里 |
|---|---|---|
| F3 | 两轮后仍未解决的问题允许带着往下做，记进进度，在请独立验证之前解决；第 51 行“里程碑检查没有未解决的问题”改成“检查结果已处理：问题已修好，或两轮后仍未解决的已记入进度” | deliver SKILL |
| F4 | 改正说法：漏写的路径被别的场景认领时，这个场景会被漏选；写法上提醒涉及路径按场景经过的包或目录写，宁宽勿窄。脚本不改，最终 head 仍全量 | deliver `plan-format.md`、`select-scenarios.mjs` 文件头 |
| F5 | grill 模板加一句：结束前把默认决定和用户答过的决定一起写进决定汇总，请用户确认一次；core-spec 的“认可”已经涵盖确认过的汇总，不改 | 本仓库 grill 交接模板 |
| F6 | #26 两行改为已合入；第二至四节和决定表前六行移到“旧流程（对照）”附录；需求目录统一写 `.harness/docs/specs/<需求>/`；Skill 版本指到 `74ae69d` | 本仓库流程文档 |
| F7 | 重新交接的提交信息多记一行用户确认原话的 trailer，`read-handoff.mjs` 据此输出 `- 重新确认:` 行，`check-delivery.mjs` 核对两者一致。7595 的重新确认是在 owner 自己的 session 里做的，原话就在上下文里，没有碰到这个缺口；缺口只在重新确认发生在别的 session 时出现，收益中等 | core-spec 第 9 步、`freeze.mjs`、deliver `read-handoff.mjs`、`check-delivery.mjs` |

P2 里的 F8（完成条件与“最终 head 全量”说法不一）、F9（复验输入没有通道）可以随 F3、F2 一起改。

## 后续：产出只看 dev-skills，本仓库只做记录

用户原话（2026-10-01）：

> 为什么要在本仓库里面去修改呢？这个grill模板放在本仓库，它不会沉淀成对应的 skill 吗？
>
> 我的理想预期是，当我整个流程优化完了之后，产出的所有内容应该只看 dev skill 就可以了。当前的仓库只是一些过程和优化的记录。

**原因：** grill 交接模板是 2026-09-30 复盘的 A1、A2 两条，当时的约束是“不改上游的 grill-with-docs”（[复盘第 6 节](../research/goal-final-delivery-trace-2026-09-30/README.md)），于是把四个输入项和一句提问边界写成本仓库的模板，没有为它建 Skill。约束本身只要求不改上游，没有要求放在本仓库。上一轮把 F5、F6 建议成“本仓库直接改”，沿用了这个做法，与用户的预期不符。

**决定：** 用户的预期写入[流程文档](../process/complex-requirement-delivery.md) v0.25 决定表“内容放在哪里”。

**助手盘点本仓库里属于产出的内容（未确认）：**

| 本仓库里的内容 | 性质 | 去处 |
|---|---|---|
| `process/grill-handoff-template.md` | 每个需求都用的输入和提问边界 | dev-skills 新建一个薄 Skill：收四个输入（目标、完成条件、授权、范围），访谈按路径引用上游的 grilling 和 domain-modeling、不复述，写提问边界，结束时把默认决定和用户答过的决定写进一份汇总请用户确认一次（含 F5），然后交给 core-spec |
| 流程文档第一节“当前流程”和决定表里仍有效的部分 | 流程说明 | dev-skills README 新增“开发流程”一节：A–D 各阶段用哪个 Skill、人做什么；规则本身已在各 Skill 里，理由在 `docs/*-design.md` |
| 流程文档的修订记录、用户原话、旧流程 | 记录 | 留在本仓库 |
| deliver 脚本的五套用例（191 条） | 脚本的回归测试 | dev-skills，CI 里跑（F14） |
| `deliver-select-replay-7595.sh`、`extract_trace.py`、`instance_runs.py` | 针对某次需求的一次性回放和复盘分析 | 留在本仓库；复盘以后要成为固定环节时再做成 Skill |
| 补字钩子 | 本机接口问题，用户 2026-09-30 决定不进 dev-skills | 留在本机 |
| verify-archon、功能地图 | 属于 agent-archon | 留在 agent-archon |
| `requirements/<需求>/` 下的 plan、证据、工具 | 某个需求的交付记录 | 留在本仓库 |
| 本仓库 AGENTS.md“以流程文档为当前版本” | 本仓库约定 | 改为当前流程以 dev-skills 为准，流程文档记录演进 |

grill 的 Skill 也可以并入 core-spec，作为“从需求开始”的一种起点。不建议：core-spec 定位是讨论结束后的收敛，已是最长的 Skill，grill 又是多轮问答。

上游依赖仍在：grilling、domain-modeling 来自 mattpocock-skills，在 dev-skills README 里写明依赖，不复制进来。

**改后的 PR 安排（未确认）：** PR 1：F1(b)、F2、F9；PR 2：F3、F4、F8（F7 待定）；PR 3：grill 薄 Skill 与 README 的“开发流程”一节；PR 4：用例迁入与 CI。本仓库：流程文档改为演进记录，F6 的整理随之简化；AGENTS.md 改指向；模板文件改为指向新 Skill。

## 后续：一个 PR；grill 依赖还是迁移；deliver 怎样校验与 review

用户原话（2026-10-01）：

> 首先，所有的改动都要放到一个 PR 里面，
>
> 然后说一下几个讨论点和思路：
> 1. 关于 grill with docs：是把它作为 core-grill 的依赖更好，还是直接把 grill with docs 相关的 skill 都迁移到dev-skills？
> 2. 整体的约束思路：还是不要有太多的 prompt。大前提是要尽最大程度地给模型能力，我们只定义好我们想要的，剩下的交给模型。
>
> 3. 现在的中间过程是怎么去做实现和约束的？尤其是在 delivery 这个阶段：
> 1. 在实现它的流程里面，是包含实现校验和 code review 吗？这个流程现在是什么样子的？
> 2. 目前的约束会有冲突的地方吗？

**决定：** 这一轮的全部改动合成一个 dev-skills PR（流程文档 v0.26，“改进的上线方式”一行追加）。

**1. grill：依赖还是迁移（助手建议，未确认）**

核对了上游（mattpocock-skills `74ca5fe`，MIT 许可）：grill-with-docs 本身只有一句“依次调用 grilling 和 domain-modeling”（247 字节）；grilling 约 2 KB，按决策树逐轮提问，要求“every branch of the design tree visited, nothing left silently assumed”，每个决定都交给用户；domain-modeling 约 3.3 KB，外加 CONTEXT、ADR 两份格式说明。

建议迁移：在 dev-skills 建一个自成一体的 core-grill，把我们实际用到的部分（逐轮问、事实自己查、术语写进 CONTEXT.md、ADR 只在三个条件都满足时写）和我们的输入、边界写成一份，不再依赖上游。理由：

- 我们的提问边界（只问会改变用户可见结果的决定，其余列默认决定）与上游 grilling 的“每个分支都问到、不默认”相反。做成依赖，模型会同时读到两份相反的指令，这正是 prompt-audit 列的“contradictory rules”和 Lauren PR 422 修的问题。
- 上游近期改动频繁（问题之间加分隔线、去掉破折号、调用措辞），流程行为会随上游变化。
- 迁移后只保留用到的部分，总字数比“上游三份加一层包装”少。
- 符合“只看 dev-skills 就够”。

代价是上游后续的改进不会自动进来。在设计记录里记下来源提交和许可证，更新上游时对照差异，按需吸收。上游 grilling、grill-with-docs 继续装着，用于流程以外的讨论。

**2. 约束思路**

与 agent-prompt-rules 和三家共识一致。落到这个 PR：正文只写想要的结果、完成标准和少数边界；每次都必须发生的交给脚本；已由脚本强制的规则不在正文复述；PR 描述列出每处增删，目标是改完后 deliver 正文比现在短。

**3. deliver 的实现、校验与 code review（现状）**

| 阶段 | 谁做 | 做什么 | 怎样约束 |
|---|---|---|---|
| 开工 | owner | 读交接提交、核对冻结的 sha256、预检验证用的 CLI、写 plan.md、需要时跑冒烟 | `read-handoff.mjs`、`check-delivery.mjs --frozen-only`、`run-verifier.mjs --preflight` |
| 实现 | owner，可派子代理 | 按里程碑写代码；缺验证能力先补 | 方法不规定；写不写新测试由 owner 定，deliver 没有要求 |
| 自验 | owner | 质量命令（lint、类型检查、已有测试）；从真实入口跑这个里程碑的场景；失败先修 | 完成条件 1；修复后重跑哪些由 `select-scenarios.mjs` 选 |
| 里程碑检查 | 两个新上下文子代理，同模型同推理强度 | 代码部分：读 diff，对照 spec 找问题，提交后就开始；证据部分：逐个检查点核证据，场景跑完后开始。只报告，最多两轮 | `record-milestone-check.mjs` 存档，`check-delivery.mjs` 核对顺序 |
| 全集自验 | owner | 最终 head 上跑全部场景、冒烟、回归、机械检查 | 完成条件 1 |
| 独立验证 | 另一家模型，单独 session | 重跑全部场景、冒烟、回归、机械检查；读基线到 head 的 diff 对照 spec 审代码，代码质量按 review-rules；判断口径偏差 | `run-verifier.mjs` 留调用记录；`check-delivery.mjs` 要求 PASS、`code-issues: 0` |
| MR | owner；评审人 | 取消 Draft，处理 CI 和评审意见；改了代码要重新验证 | 完成条件 4；只改测试、文档、lint 配置时沿用报告 |

所以有两层机器 code review（里程碑检查的代码部分、独立验证的代码审查），加上 MR 的人工评审。两层机器 review 都按 spec 查正确性；代码质量（复用、最少改造、复杂度、责任边界，即 review-rules 的第 2–5 条）只能作为“可选建议，最多三条”，不影响结论，owner 可以不改。新代码有没有测试，没有人查。

**约束之间的冲突（助手整理）**

| 冲突 | 位置 | 性质 |
|---|---|---|
| 里程碑检查两轮后能不能往下做 | deliver 第 51 行与第 53 行 | 两句给出相反做法（F3） |
| 最终 head 全量还是只重跑受影响的 | 完成条件 1 与第 51 行 | 说法不一（F8） |
| “写漏只会让重跑变多” | plan-format 与脚本实际行为 | 说法与行为不符（F4） |
| 默认决定算不算确认 | grill 模板与 core-spec 第 1 步；模板与上游 grilling | 相反（F5，以及上面第 1 点） |
| 超时按“CLI 用不了”处理 | deliver 与实际原因 | 已由用户决定改（F2） |
| review-rules 的作用 | deliver 写“验证者用它审代码质量”，验证说明只让影响正确性的算问题 | review-rules 五条里四条只能是可选建议，名义上在审、实际不起作用 |
| 少写 prompt 与 deliver 的写法 | 原则与正文 | 正文复述脚本、条件分支都在正文、每次修补加一段（F12）；不是两条规则冲突，是做法偏离原则 |
| 多层验证与 Opus 5 指南“删掉额外验证” | 流程设计与模型指南 | 用户 2026-09-29 定“效果优先”，保留；不是 Skill 内部冲突 |

待用户确认：grill 迁移方案；代码质量 review 维持非阻塞、只在 MR 里列出，还是让 review-rules 的部分条目能阻塞；新代码测试是否要有人查。
