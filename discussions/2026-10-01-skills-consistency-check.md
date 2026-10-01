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

## 后续：core-grill 同意；代码质量 review、测试、F2 与 F7 的解释

用户原话（2026-10-01）：

> 1. 同意
> 2. 代码质量 review 是指在哪个环境的 review, 是阶段 review 还是整体 review?
> 3. 新代码没有测试是什么含义? 不是有 verify 吗? 
> 4. F2和 F7 的方案和要解决的问题是什么?
>
> /explain-as-fool

**决定：** grill 迁成 dev-skills 里自成一体的 core-grill（流程文档 v0.27 决定表“grill 的 Skill”）。

**助手答复要点（按 explain-as-fool 写）：**

- 代码质量 review 指整体 review，即最后另一家模型的独立验证读整个 diff 时按 review-rules 看的那部分。阶段 review（每个里程碑的代码部分检查）只对照 spec 查对不对，不看代码质量，也不读 review-rules。整体 review 里，质量意见只能是“可选建议，最多三条”，不影响 PASS。建议：不拦合入，但 owner 对每条要么改、要么写理由，全部列进 MR 描述，用户合入前看。
- verify 和测试是两回事：verify 的场景由 agent 在这次交付中操作真实应用跑一遍，证明这个 MR 现在是对的；跑完就结束，合入后没有人再自动跑。测试是提交进仓库的代码，以后每次有人改代码，CI 都会自动跑，防止别的改动把这次的行为弄坏。deliver 要求前者，后者写不写由 owner 定、没人查。7595 的 owner 实际改了不少测试（plan 记录 v2 测试 67 个文件 941 个通过），只是流程没有要求。建议：整体 review 多看一项“新增或改变的行为有没有测试覆盖”，没覆盖的列进 MR，不拦合入。
- F2：独立验证 90 分钟被停后，脚本报“这个 CLI 用不了”，deliver 让换一家 CLI；但停下多半是因为活多（7595 有 44 个场景），换了也会到点被停，最后流程错误地停下来找人；而且验证者只在最后交报告，被停时已验的部分全丢。方案：60 分钟上限；“到点或久无进展”和“CLI 用不了”用不同的返回码；验证者每验完一个场景就写一行结果；被停时脚本写停止分析；owner 看分析决定接着验、分批验、先修环境，或换 CLI；门禁允许同一版本代码的几段验证合起来算，合起来要覆盖全部场景和机械检查。最后这条待用户确认。
- F7：交付中改了 spec 或 verify，plan.md 要有一行带用户原话的“重新确认”，门禁只查这行在不在。重新交接的提交里只记新的 sha256，不记原话；重新确认若发生在 owner 以外的会话，owner 看不到原话，只能靠转述，也可能自己编。方案：core-spec 把原话写进重新交接的提交信息，`read-handoff.mjs` 直接输出这一行，`check-delivery.mjs` 核对 plan.md 里的与提交里的一致。7595 的重新确认在 owner 自己的会话里，没碰到这个问题；重新确认在 owner 会话里做时，这个改法也挡不住 owner 自己写，那种情况靠另一家模型对照第一次交接判断是否放宽。收益中等，改动小。

待用户确认：整体 review 的质量意见按上面处理；测试覆盖作为整体 review 的一项、不拦合入；F2 的“几段验证合起来算”；F7 做不做。

## 后续：质量与测试意见、F2 周期检查；F7 并入人工介入的讨论

用户原话（2026-10-01）：

> 1 2 3 同意，
> F2
> 这个改成 60 分钟的限制。60 分钟停掉之后，需要主 Agent 再去看一眼 CLI 具体的执行过程：
>
> 1. 如果没有执行完，就在当前的 CLI 继续追加。
> 2. 如果执行失败了，就由 Agent 自己去判断。
>
> 总之，是以 60 分钟为一个周期去做 check，然后由 Agent 自己去决定后面的任务。同时这里的 prompt 约束不要有太多限制。
>
> F7, 需要你看下 MR 7595 deliver session 链路分析 (fork) 这个 session 的讨论, 我需要重新讨论一下关于人工介入的问题和流程自动进行的问题。

**决定（流程文档 v0.28）：**

- 代码质量意见和测试覆盖由最后的独立验证列出，不拦合入；owner 逐条改或写明理由，列进 MR 描述。
- 同一版本代码的几段验证可以合起来过门禁。
- F2：60 分钟一个检查周期。到点脚本停下验证者并交回控制；owner 看这段执行过程，没做完就在同一个 CLI 会话里续接，失败由 owner 判断；给 owner 的说明不加更多限制。核对过三个 CLI 都能续接：`codex exec resume <id>`、`claude -p --resume <id>`、`mcode exec --session <id>`。

**读了 fork 会话（`local_1eaf0ee6…`，提交 `9424415`、`f9277c3`）：** 它为“交付中什么时候找人”起草了闭合清单（[human-intervention-policy.md](../research/goal-v2-deliver-trace-2026-10-01/human-intervention-policy.md)）：A 停下等（产品决定、权限凭据环境、授权外不可逆操作、卡住、验证者判为放宽），B 攒着一起确认（新文案），C 只通知，D 不找人（spec、verify 把现有快捷键、文案、默认值等事实写错而意图已定，记“事实更正”、不改冻结文件；实现选择；能自修的环境问题）。起因是 S24：spec 把现有的“立即发送”快捷键写成 ⇧⌘⏎，owner 按现行规则（口径偏差只管 verify，改 spec 要用户原话）问了两次、重新冻结。三项待用户确认。

**助手对人工介入与自动进行的整理（未确认），见本节下方答复要点：**

- F7 的前提是交付中常有重新冻结。按草案，事实写错不再改冻结文件；剩下的重新确认只来自产品决定和用户自己新增的需求，这两种情况用户本来就在和 owner 对话，原话就在 owner 的会话里。F7 建议取消。
- 进一步建议：产品决定的答复不再走“core-spec 改文件、查漏、重新交接”，改为原话记进 plan.md，与口径偏差、事实更正放在同一节，由验证者对照判断、MR 列出；冻结文件保持第一次交接的版本。#25 的重新交接只在用户主动要重写 spec 时用。
- 少写 prompt：deliver 只写 A 类和一句判断标准，其余一句“自己定、记进决策日志、MR 里列出”；B1 的新文案并入 MR 里的“自主决定”，合入时看，不再单独中途确认；C 类不需要规则。
- 不是 owner 提问造成的中断：Stop 钩子（N1，v0.18 同意试行，未做）解决“回合以文字结束后没人接着做”，这是 7576 空转 81 分钟、7595 停工 10.6 小时的原因；测试窗口抢焦点、删除审批属于 agent-archon 的 verify-archon。

待用户确认：A 类清单与“其余全部 owner 定”；产品决定的答复走轻量记录还是重新冻结；事实更正并入口径偏差一节；Stop 钩子是否进这个 PR；core-spec 查漏是否加“spec 写到的现有事实对代码核对”。

## 追问：不设停下的情况，全程做完、决定列在最前面，合入前看

用户原话（2026-10-01）：

> 如果我不设置 A 类，就是需要它在流程中完全进行下去，最后把对应的清单列出来。在中间过程中，自己做决定并写下来，放在最前面。在我合入之前，会重点 check, 这种流程可以吗? 三家理论有怎么做的吗?
> 这样做的话, 流程会不会更轻量? 感觉现在有很多校验脚本，导致流程会比较重。

**助手答复要点（未确认）：**

1. 可行。A 类里有三种在这个流程里自然不再是“中途停下”：授权以外的不可逆操作（合入等）owner 本来就不做，留到最后由用户做；拿不到的权限、环境和卡住，owner 做完其余部分，把受影响的场景标为未验证，列在最后。真正改变的只有产品决定：owner 选一个默认做法继续，记下理由和推翻后要改什么、重跑哪些场景。
2. 三家（本地原文已核对）：
   - Lauren 最接近：`principle-never-block-on-the-human`“Make reasonable decisions, proceed, and let the human course-correct after the fact”；全权授权下“apply a default for a call that only the operator can make. Report the default with a full explanation and the one word that reverses it”（poteto-mode SKILL:20）；待人决定的事进 `gates.md`，必须带默认答案（`orch gate park --default`），不阻塞。保留的例外：“Always pause for irreversible writes”（SKILL:83）。
   - OpenAI：ExecPlan“do not prompt the user for "next steps"; simply proceed to the next milestone”，决定记在 Decision Log（PL L34、L86）；Harness engineering“corrections are cheap, and waiting is expensive”（HE L114），但也写“Escalate to a human only when judgment is required”（HE L152）；GPT-6 Astra 交互时“waits for your input on consequential decisions”。
   - Anthropic：Fable 5 只在“a destructive or irreversible action, a real scope change, or input that only they can provide”时停（F5 L64）；Fable 5.1 在不同理解会导致实质不同的工作时确认（F51 L836），偏保守。
   - 共同点：可逆的工作不等人，决定记下来事后看；都保留“不可逆操作前停”。在本流程里不可逆操作不在授权内，等于流程的终点，不需要中途停。都不做的：为了交差放宽验收（Lauren“never relax the predicate”）。
3. 会更轻。deliver 的 11 个脚本（2,399 行）分三类（粗分）：
   - 查结果的（spec、verify 没被改；最终 head 由另一家模型验证、报告完整、PASS）：约 1,170 行，加 core-spec 的 `freeze.mjs` 112 行。保留。
   - 提效工具（`select-scenarios.mjs`、`report-reuse.mjs`）：约 330 行。owner 想用就用，不当门禁。
   - 管过程的（里程碑检查的顺序与记录、rebase 与重新交接后的记录、重新确认原话、口径偏差逐条按编号和哈希核对）：约 900 行，加现有 191 条用例里的 136 条。可以去掉，改为：里程碑检查保留为一句做法，不再核对时间顺序；口径偏差、事实更正、产品默认决定合成 plan.md 开头的一份“决定清单”，原文交给最后的验证者判断，不按编号、哈希核对。
   - 原则：查结果，不查过程。Anthropic 在 Opus 4.6 上去掉了分段，把 evaluator 改为最后一次（HD“Removing the sprint construct”）；Lauren 的验证账本按 PR 和 head SHA 记结论；OpenAI 主张最少的阻塞门禁。三家原文里没有见到“里程碑检查必须早于下一个提交”这类核对 agent 行动顺序的门禁。
4. 代价：错的默认决定要到合入前才被发现，返工可能比当时问一句更贵；合入前的检查成为唯一的人工关口，清单要按影响排序、写清推翻代价；里程碑检查晚做不会再被拦下（7576 的情况），只多花重跑时间，最终结果仍由最后的验证兜底。
5. 可选的一处例外：发现凭据可能泄露时立即通知用户（不停工），因为等到最后才轮换有安全风险。

待用户确认：采用“全程不停、决定清单放最前、合入前看”；去掉管过程的脚本；凭据泄露的通知例外；core-spec 查漏是否加“现有事实对代码核对”（减少决定清单的条数）。

## 用户：全程不停、不可逆前停；决定先问另一家模型；流程要轻

用户原话（2026-10-01）：

> 首先，将“前程不停决定清单”放在前面。我更倾向于采纳 Lauren 的说法，保留“不可逆操作前一定要停”的原则。
>
> 其次，我会增加一个跨模型的 check 和讨论机制。比如在遇到需要决策时，拉起 Codex 做一个判断并进行讨论，再得出具体的方案，这比在当前模型里面直接做决定会更好。但是，整个流程要尽量做轻一点：不需要有复杂的脚本去 check，只需要通过 prompt 做约束，并且 prompt 也要很轻。
>
> 第二个 spec 还会有换模型查漏的阶段吗？我怎么没印象了

**决定（流程文档 v0.29）：** 交付中不停，决定清单放 plan.md 和 MR 描述最前，合入前看；不可逆操作前停（合入、强推共享分支、删除共享数据、对外发消息、改共享环境）；交付中需要决定时先问另一家模型、讨论后再定；流程尽量轻，靠很轻的 prompt。

**助手答复要点（未确认）：**

- 跨模型讨论的依据：Lauren“A second opinion is the same prompt against a different model. Agreement is high-signal.”（poteto-mode SKILL:95）；决策日志收尾时让不同家族的模型审，“Self-review is not a substitute.”（show-me-your-work:67）；`interrogate` 的分歧来自模型不同，不靠指派人设。
- 建议的 deliver 写法（三段，替代现有的“停下”“口径偏差”“自主决定”“交付中改验收文档”）：
  - 决定：spec 没定、会影响用户看到的结果或验收判定的选择，先用只读命令问另一家模型（给问题、相关 spec 原文、可选做法和证据，不给自己的倾向），意见不同在同一会话再谈一轮；然后自己定、继续做，把决定、两边意见、推翻后要改什么写进决定清单。不影响结果的实现选择自己定。
  - 停：只在不可逆操作前停；其余做不了的标明原因、做完其余部分、列进清单。
  - MR：决定清单放最前。
- 脚本：去掉“管过程”的全部（里程碑检查记录与顺序、rebase 与重新交接、确认原话、口径偏差按编号核对、重跑选择、报告沿用），独立验证用命令加 `perl -e 'alarm 3600; exec @ARGV'`（macOS 没有 `timeout`）实现 60 分钟周期，不再用 `run-verifier.mjs`。剩下两种选择：(a) 留一个约百行的小检查，只看结果：spec、verify 自交接后没改，最终验证报告对应 MR 最新代码、结论通过、验证者与 owner 不同家族；(b) 不留脚本，这几项写进 MR 描述由用户合入前看。建议 (a)，这是唯一没有人工兜底就容易被跳过的一步。
- 随之取消或改为 prompt 的已确认决定：v0.17/v0.20 里程碑检查记录与顺序（保留“每个里程碑让新的子代理查一遍”一句）、v0.21 重新交接与确认原话、v0.22 口径偏差核对（并入决定清单）、v0.23 重跑由脚本选与两部分检查、v0.24 F1 的解析器（不再解析场景表，问题消失）、v0.13 用 `run-verifier.mjs` 发起；F7 取消。deliver 脚本由 11 个、2,399 行降到 0–1 个。
- spec 阶段的换模型查漏：有，即 core-spec 第 7 步，用户 2026-09-29 定（“B4 开新 session, 用不同的模型审”）。7576 用 Codex 查两轮共 11 项，7595 查三轮（13、11、6 项），问题在用户确认冻结前处理完。它本来就只靠说明和一条命令。建议保留，并在查漏说明里加一项：spec 写到的现有快捷键、文案、默认值逐条对代码核对，减少交付中的决定。

待用户确认：脚本选 (a) 还是 (b)；上述已确认决定一并取消；查漏说明加“现有事实对代码核对”；凭据泄露即时通知（上一轮提出，用户未回应，暂不加）；Stop 钩子是否进这个 PR。

## 用户：其余同意，汇总改动方案

用户原话（2026-10-01）：

> 凭据通知不加，Stop 钩子不放
> 其他的同意，汇总我们本次讨论产生的结论中，要改动的内容, 你准备怎么改动？方案是什么？

**决定（流程文档 v0.30）：** 只留一个约 150 行、查结果的检查（选 (a)）；取消管过程的已确认机制（v0.13 用 `run-verifier.mjs` 发起，v0.17–v0.24 的里程碑记录与顺序、报告沿用脚本、重新交接与确认原话、口径偏差核对、重跑选择、F1 解析器），F7 取消；查漏加“现有事实对代码核对”；不加凭据通知；Stop 钩子不放进本次 PR。上一轮未单独回答的“流程说明放 dev-skills README”“本仓库 AGENTS.md 改指向”按“其他的同意”处理。

**助手答复：** 汇总为[改动方案](../research/skills-consistency-2026-10-01/change-plan.md)：一个 dev-skills PR（新建 core-grill；deliver 重写，正文约 7,945 字到约 4,000 字，脚本 11 个到 1 个；core-spec 的查漏、交接、跨模型命令；agent-prompt-rules 跟上两家最新写法；README 流程说明与设计记录；新检查的用例进 CI），本仓库的记录改动（AGENTS.md、流程文档改为演进记录、模板改指向），验证方式（用例、7595 只读运行、新 session 行为探针、Codex 审查），合入后的安装与 7595 投递。待用户确认后实施。

## 用户：创建 PR

用户原话（2026-10-01）：

> 创建 pr

按[改动方案](../research/skills-consistency-2026-10-01/change-plan.md)实施，开了 [coder-xieshijie/dev-skills#27](https://github.com/coder-xieshijie/dev-skills/pull/27)（分支 `flow-lightweight-core-grill`，提交 `cd75427`、`eba4e7e`，未合入）。

**结果：**

| 项 | 改前 | 改后 |
|---|---|---|
| deliver SKILL.md | 7,945 字 | 2,986 字 |
| deliver references（3 份） | 7,414 字 | 4,213 字 |
| deliver 脚本 | 11 个，2,399 行 | 1 个 `check-delivery.mjs`，236 行（方案估计 150 行；多出的是审查后加的包根识别和交接包含关系） |
| deliver 用例 | 191 条，在本仓库 | 20 条，在 dev-skills，CI 运行 |
| core-grill | 本仓库模板 | 新 Skill，正文 1,217 字，另有术语表、ADR 两份格式 |
| agent-prompt-rules SKILL.md | 15,443 字 | 20,384 字（新增条目各带依据链接）；原文存档新增 5 篇、重抓 4 篇、改地址 3 篇 |

与方案的出入：agent-prompt-rules 由一个子代理按研究目录第 2 节完成，多存了一篇 Claude Code skills 文档作三-2、四-5 的依据；新条目加在各节末尾（一-9、三-7、四-5），没有重排已被引用的编号。core-spec 的 `freeze.mjs` 只改了注释里的脚本名；`verify.md` 写法里“门禁读取盲区”改为“验证者认”；`spec-example.md` 里“问用户能否合入”的检查案例改为“停在可合入”。

**验证：**

- 新用例 20 条全部通过；故意改坏 10 处检查，每处都有用例失败（其中一处起初没被抓到：本机 git 关了 `core.quotePath`，用例改为显式打开）。
- 在 7595 的真实分支上只读运行 `--frozen`：认出最近一次交接 `9a596da696`，通过。
- 行为探针：新开 Claude 子代理和 Codex 会话，只给新版 deliver、core-grill，问 6 个情境，两边回答都符合本轮决定。探针暴露两处缺口已修：验证说明的 PASS 条件仍写“符合 spec 字面预期”，与决定清单的更正冲突；正文没写验证后只改 plan 要不要重验。
- Codex 审查第一版：P1 两条（重新交接后旧报告仍能过；任意层级的 `tests/` 被当成测试），P2 四条（中文路径、咨询范围漏了事实更正、`mcode --cwd` 用错、本地交接时 plan 不记哈希），都已修正，修正后没有再送审。

**本仓库：** AGENTS.md 改为当前流程以 dev-skills 为准；流程文档 v0.31 改为演进记录；grill 交接模板改为指向 core-grill；`research/` 下针对已删脚本的六个用例脚本文件头注明只适用于 `74ae69d` 及以前。

**待用户决定（合入后各自需要同意）：** 合入 PR 并快进本机 dev-skills；安装 core-grill 的两个入口；7595 当前里程碑结束后投递消息，让它按新版继续。

**待验证：** 新流程在真实需求上的效果（owner 是否不停、决定清单是否够用户判断、60 分钟续接是否顺利），下一个需求观察。
