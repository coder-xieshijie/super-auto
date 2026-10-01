---
id: research-skills-consistency-checks
recorded_on: 2026-10-01
timezone: Asia/Shanghai
source: dev-skills main `74ae69d`（dev-skills#26 合入后）；本仓库流程文档 v0.23、grill 交接模板 v1；mattpocock-skills `74ca5fe`；agent-lord `9bf101a`；MR 7595 冻结的 verify.md（sha256 `33cd80c9…`）
scope: 开发流程相关 Skill 的一致性与是否符合用户已确认的决定；不改 dev-skills，修改建议待用户决定
---

# 开发流程 Skill 一致性检查（dev-skills `74ae69d`）

总述与三家综合见 [README](README.md)。本文只写检查本身：查了什么、怎样查的、发现了什么、建议怎么处理。

## 1. 范围与方法

**检查对象。**

| 类别 | 文件 |
|---|---|
| 流程主干 | core-spec：`SKILL.md`、`references/{verify,gap-check,cross-model,spec-example,verify-example}.md`、`scripts/freeze.mjs`；deliver：`SKILL.md`、`references/{plan-format,milestone-check,verifier-brief}.md`、`scripts/` 11 个文件（2,399 行） |
| 被流程引用 | review-rules（验证者审代码）、mr-for-human（MR 描述）、explain-as-fool（汇报）、agent-prompt-rules（写法依据） |
| 相邻、不在主干 | plan-for-agents、design-for-review、recon-to-contract |
| 说明文档 | dev-skills `README.md`、`docs/core-spec-design.md`、`docs/deliver-design.md` |
| 本仓库 | [流程文档 v0.23](../../process/complex-requirement-delivery.md)、[grill 交接模板](../../process/grill-handoff-template.md) |
| 上游与编排 | grill-with-docs（mattpocock-skills `74ca5fe`）；Agent Lord `9bf101a` 只核对与流程编排有关的说法 |

**方法。**

1. 逐份通读，按“用户已确认的决定 → Skill 正文 → references → 脚本实际行为 → 说明文档”交叉核对。
2. 跑已有用例，对象是当前 main 的脚本：`deliver-rebase-cases.sh` 33 条、`deliver-refreeze-cases.sh` 29 条、`deliver-rehandoff-cases.sh` 16 条、`deliver-deviation-cases.sh` 58 条、`deliver-select-cases.sh` 55 条，共 191 条全部通过；`check-links.mjs` 25 个 Markdown 文件通过。
3. 用门禁的共享解析器（`report-format.mjs` 的 `parseVerify`，`run-verifier.mjs` 和 `check-delivery.mjs` 都用它判断报告是否完整）读 MR 7595 冻结的 verify.md。
4. 在临时仓库复现 `select-scenarios.mjs` 的一种漏选。
5. 按提交统计 core-spec、deliver 的字数和含限制词的句子数，看“少写 prompt”执行得怎样。

## 2. 结论

- 用户确认过的机制基本都落到了 Skill 和脚本里，191 条用例全部通过。
- 有两处会影响 MR 7595 的收尾：门禁认不出 7595 verify 里的 20 个编号（F1）；独立验证默认 90 分钟上限，到点按“CLI 不可用”处理，换 CLI 也没用（F2）。
- 有四处规则互相矛盾或说法不成立（F3–F5、F7）。
- 流程文档有五处过时（F6），其中第二至四节仍是旧流程，却没有标成旧的。
- 与“少写 prompt、只做边界”相比在变重：deliver 正文从 #15 的 4,687 字到现在 7,945 字，含限制词的句子从 30 句到 50 句，除 #23 外每次都只加不减（F12）。
- 用户同意过、还没做的：Stop 钩子试行、改动范围检查（A6、B7）、由 Agent Lord 派发最终验证（F13）。
- 按两家最新的写法依据再看，有两处写法问题：“停下”在正文后半段，Claude Code 压缩上下文后可能保不住（F15，粗估）；规则里夹着事故经过和相对旧版本的说法（F16）。

## 3. 发现

严重度：**P0** 影响进行中的交付或门禁的正确性；**P1** 规则互相矛盾、会让 agent 无所适从；**P2** 文档过时或可以更好。

| ID | 严重度 | 位置 | 问题 | 证据 | 建议 |
|---|---|---|---|---|---|
| F1 | P0 | core-spec `references/verify.md` 第 2、3 节；deliver `scripts/report-format.mjs`、`select-scenarios.mjs` | verify 的编号格式没有规定，门禁却只认一种。`parseVerify` 只认 `S\d{2,}`（无后缀）为场景、证明方式一栏写着“机械检查/已有检查”的 `R\d{2,}` 为要单列的要求；`select-scenarios.mjs` 认 `S\d+[a-z]?` 和 `RG\d+`。7595 的 verify 用了 `S12b`、`S21b`、`S29b`，机械检查另编 M01–M17，回归用 RG1–RG3、RG1b，要求表的证明方式一栏写的是编号（“M01；RG1”）而不是“机械检查” | 解析 7595 verify（`33cd80c9…`）：场景 41 个（S01–S41），漏 3 个；要单列的要求 0 个，M01–M17 共 17 条都不要求出现在报告里。验证报告少了这 20 行，`run-verifier.mjs` 和 `check-delivery.mjs` 都不会报错。core-spec 的 `verify-example.md` 要求表只演示了“场景 S01”一种证明方式，没有演示机械检查怎样写才能被门禁读到 | 一处定义编号：在 core-spec 的 verify 写法里写明场景、要求、机械检查、回归项各用什么编号；`freeze.mjs` 冻结前用同一个解析器读 verify，遇到认不出的编号就失败，作者当场改。`select-scenarios.mjs` 改用同一个解析器。7595 已冻结，可以在 deliver 侧让解析器兼容这几种写法，或者由 owner 在验证输入里点名这 20 项（只能靠 prompt） |
| F2 | P0（风险，未实测） | deliver `run-verifier.mjs` 默认 `--timeout 90`；SKILL“独立验证” | 总时长默认 90 分钟，SKILL 没说按需求规模设多少；到点返回 3，SKILL 规定返回 3 就“换另一个不同家族的 CLI”，都不行就按停下第 2 种处理。超时是工作量问题，不是 CLI 不可用，换 CLI 只会再超时一次 | 7595 有 44 个场景、三个入口，RG1 要在两个提交上各跑一遍功能地图；交付中由已写好脚本的子代理跑部分场景，每轮墙钟 36–80 分钟（[parallelism.md](../goal-v2-deliver-trace-2026-10-01/parallelism.md)）；首个试跑的 mcode 复验跑了 2 小时 3 分钟仍未出报告 | 超时与“CLI 不可用”分开：超时用另一个返回码，SKILL 写一句“按全集自验的实际耗时设 `--timeout`”；或者默认值按 verify 的场景数估。停滞上限（20 分钟没有新证据）不变 |
| F3 | P1 | deliver SKILL 第 51、53 行 | 第 51 行：里程碑做完的标准包括“里程碑检查没有未解决的问题”，才进入下一个；第 53 行：每个里程碑最多两轮，“两轮后仍未解决的问题也记在那里，在请独立验证之前解决”，意思是可以先往下做。两轮之后还有问题时，两句给出相反的做法 | 原文 | 保留一种：建议沿用第 53 行（记下、继续、在独立验证前解决），第 51 行改成“检查结果已处理（修好，或两轮后记入进度）” |
| F4 | P1 | deliver `references/plan-format.md` 第 80 行；`select-scenarios.mjs` 文件头 | “路径写漏只会让重跑变多”不成立。只有改动的文件没有任何一行认领时才会全部重跑；某场景漏写了一个路径、而这个路径被别的场景认领时，这个场景会被漏选 | 临时仓库复现：S01 认领 `src/a/**`，S03 实际也经过 `src/a` 但没写；改 `src/a/x.ts` 后脚本只选 S01。里程碑检查的证据部分会把 S03 在更早 head 上的证据当作有效（milestone-check 第 2 步）；要到最终 head 全量跑时才会发现 | 改正说法：写漏会少选；同时提醒涉及路径宁宽勿窄（例如按入口包写到目录）。不必改脚本：最终 head 仍全量 |
| F5 | P1 | [grill 交接模板](../../process/grill-handoff-template.md)“提问边界”；core-spec SKILL 第 32 行 | 模板让 grill 把不影响用户可见结果的事“列成默认决定，用户有异议再改”；core-spec 第 1 步规定“用户没有反对，不等于已经批准”。默认决定到了 core-spec 不算已确认，要么再问一遍，要么不进 spec | 7595 的做法是把默认答案放进决定汇总、用户确认一次（[original-decisions.md](../../requirements/goal-v2-and-feedback-fixes/original-decisions.md) 第 6 节标题“汇总中列出，用户确认”），实际没出问题，但两处文字没写这一步 | 在模板里补一句：默认决定写进结束时的决定汇总，用户确认汇总即确认这些默认 |
| F6 | P1 | [流程文档](../../process/complex-requirement-delivery.md) | 五处过时：（a）决定表“交付中验收口径偏差”“里程碑检查的时机与重跑的选择”两行仍写 dev-skills#26“未合入”，实际已合入（`74ae69d`）；（b）第二至四节（各环节说明、文档之间的交接、待讨论问题）描述的是 v0.3–v0.6 的旧流程（plan 在 grill 里写、cross review 改 verify 和 plan、core-verify“本机未安装”），没有标成旧的；（c）决定表前六行（串行产出、同一 session、三份独立文档、spec 唯一依据、cross review、冻结时点）已被 v0.7 的重建取代，没有标注；（d）“需求文档位置”写 `.harness/docs/spec/<需求>/`，“交接方式”和 7595 实际用的是 `.harness/docs/specs/<需求>/`；（e）“对应的 Skill”一段只指到 #12、#13 | 原文 | 一次性整理：第二至四节移到“旧流程（对照）”下或改写成现行各阶段的说明；被取代的决定加“已被 v0.7 取代”；目录统一为 `specs/`（以用户确认为准）；Skill 版本指到 `74ae69d` |
| F7 | P1 | core-spec SKILL 第 175 行；deliver SKILL 第 80 行、plan-format 第 27 行 | 交付中改了 spec 或 verify 后，deliver 要在 plan.md 写带“用户重新确认时的原话”的 `- 重新确认:` 行，门禁核对这一行；但 core-spec 重新交接时没有把用户原话记在 deliver 读得到的地方（提交信息只有两行 sha256），owner 只能靠转述 | 7595 的 plan.md 里这几行由 owner 从会话转述写成 | core-spec 重新交接时把确认原话写进交接提交的信息（例如再加一行 trailer），`read-handoff.mjs` 直接输出 `- 重新确认:` 行，与“sha256 不手抄”同一个思路 |
| F8 | P2 | deliver SKILL 第 23、51 行 | 完成条件 1 写“之后代码又有改动的，受影响的场景在改动后重跑”，第 51 行写“最终 head 上照常跑全部场景”。独立验证通过后又改了代码（CI 修复、评审意见）时，owner 是重跑受影响的还是全部，两处说法不同；验证者那边则是完整复验 | 原文 | 写成一句：最终 head 全量，由 owner 自验一次、验证者再验一次；中间修复按脚本选 |
| F9 | P2 | deliver `references/verifier-brief.md`“复验” | “调用方另外给出上一次验证的 head 和报告时，这次是复验”，但验证输入的清单里没有这一项，`run-verifier.mjs` 也没有对应参数，owner 不知道放在哪 | 原文；脚本参数表 | 在验证输入清单加一项“上一次验证的 head 和报告（复验时）” |
| F10 | P2 | deliver `record-milestone-check.mjs` | 里程碑检查“分代码、证据两部分”“模型 ID 与 owner 不同则作废”只写在 prompt 里，记录脚本不核对报告里有没有 `part: code`、`part: evidence` 两段、模型 ID 是否与 plan.md 的 owner 一致 | 脚本源码；用户 2026-10-01 决定 V3“记录脚本不改” | 维持用户决定；记为已知的“只靠 prompt”项，下一个需求观察是否漏做，漏了再加脚本核对 |
| F11 | P2 | dev-skills `README.md`、`docs/` | README 说 deliver 安装时保留 core-spec、mr-for-human、explain-as-fool，漏了 review-rules（SKILL 引用 `../review-rules/SKILL.md`）；`docs/deliver-design.md` 开头的设计表仍写“只在三种情况停下”（后文第四种已补）；`docs/core-spec-design.md` 最后更新于 #20，#26 给 core-spec 加的“口径偏差不回到本 Skill”没有记录 | 原文；`git log` | 顺手修，不单独开 PR |
| F12 | P2 | core-spec、deliver 整体 | 体量持续增长，见第 5 节 | 第 5 节 | 见第 5 节 |
| F13 | P2 | 流程 | 用户同意、还没做：N1 Stop 钩子试行（v0.18）；A6、B7 改动范围清单与提交前检查；最终验证在无人值守或多需求并行时由 Agent Lord 派发（v0.13）。Agent Lord 目前没有 core-spec、deliver 节点，它的 `plan-to-implement` 按“每轮新 session、读上一轮最后一条消息”接续，与 agent-prompt-rules 二-11（默认同一 session 接续）和 deliver 的单 owner 连续运行不一致 | 流程文档修订记录；agent-lord `SKILL.md`、`references/pipelines/plan-to-implement.md` | 不在本轮修；需要编排时再定 Agent Lord 的节点设计 |
| F14 | P2 | dev-skills CI | deliver 的 191 条用例放在本仓库 `research/` 下，dev-skills 的 CI 只查链接；脚本改动的回归只能靠人记得去跑 | `.github/workflows/check.yml` | 把五个用例脚本迁进 dev-skills（例如 `skills/deliver/tests/`），CI 里跑 |
| F15 | P2（粗估，未实测） | deliver SKILL 结构 | “停下”一节从第 6,855 字开始（全文 7,945 字），“MR”“汇报”更靠后。Claude Code 自动压缩上下文后，每个已加载的 Skill 只保留前 5,000 tokens（[code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) § Skill content lifecycle）。“停下”之前有 3,621 个汉字和 3,234 个其他字符，按每个汉字 0.7–1.2 token、其他字符约 0.3 token 粗估，起点在 3.5k–5.3k token，可能在压缩后丢失 | 字数统计；本机 `claude -p` 未登录，没能用接口实测 | 把四种停下移到正文开头（“你是 owner”之后）：它是全程适用的边界，Claude Code 文档也建议把最重要的指令放在 SKILL.md 开头。减量（第 5 节）后整篇会更短 |
| F16 | P2 | core-spec `references/cross-model.md` 第 31 行；deliver SKILL 第 49、69 行 | 规则里夹着历史和相对旧版本的说法：“2026-09-30 实测 Playwright 报 …，用户 2026-09-30 决定验证时去掉沙箱”“例如交接早于这条规则”“试跑中两次都没有唤醒会话”。Anthropic 的 prompt-audit 把这类写法列为过时模式：规则的效力来自它规定的行为，不来自起因；相对说法会让模型以为还有别的版本 | [vendor-latest.md](vendor-latest.md) 3.3 S4 引 prompt-audit Group 2、1d | 正文只写当前规则和一句原因，历史留在 `docs/*-design.md` |

## 4. 对照用户已确认的决定

流程文档决定表逐行核对（第 1–6 行已被 v0.7 取代，不再核对，见 F6）。

| 决定 | 现状 | 说明 |
|---|---|---|
| 方向：自证闭环 | 一致 | verify 以真实入口场景为单位；deliver 自己驱动应用 |
| 沉淀与编排 | 部分 | 沉淀到 dev-skills 已做；Agent Lord 编排未做（F13） |
| 重建前提三条 | 一致 | 人只在 B 阶段决定；C 阶段四种停下 |
| B4 查漏：新 session、不同家族 | 一致 | core-spec 第 7 步、`cross-model.md`；不可用时不降级 |
| C 阶段每个里程碑跑场景 | 一致 | deliver“里程碑” |
| 需求文档位置每次指定 | 一致 | core-spec 第 3 步“没有给出目录时先问”；目录名写法见 F6（d） |
| 交接方式：提交到需求分支、Draft MR | 一致 | core-spec 第 9 步、`read-handoff.mjs` |
| 功能地图位置 | 不在 Skill 中规定 | 属于 Agent-Archon 仓库 |
| 验证入口：用户实际使用的入口 | 一致 | verify 写法“走真实用户路径”“覆盖每个入口” |
| spec 与 verify 合并为 core-spec | 一致 | |
| 中间 subagent 继承模型和推理强度，最终另一家单独 session | 一致 | 推理强度的核对已按 #23 删去，继承保留 |
| 最终验证由 owner 经 `run-verifier.mjs` 发起 | 一致 | 无人值守时改由 Agent Lord：未做（F13） |
| 四种停下 | 一致 | |
| 里程碑检查的顺序与把关 | 一致 | 用例全过；F3 是正文措辞矛盾 |
| 报告沿用由脚本判断 | 一致 | `report-reuse.mjs` |
| 最终验证的运行（限时、预检、无沙箱、`--effort`） | 一致，有风险 | 默认 90 分钟见 F2；`--effort` 实为可选，`cross-model.md` 写“显式设”，SKILL 写成可选参数，意思是“要设时显式传”，不矛盾 |
| 交付中改验收文档 | 一致，有缺口 | 用户原话的来源见 F7 |
| 交付中验收口径偏差 | 一致 | 流程文档仍写未合入（F6 a） |
| 里程碑检查分两部分、重跑由脚本选 | 一致，有缺口 | 漏选见 F4；两部分只靠 prompt 见 F10 |
| 写给 agent 的 prompt：少写、只做边界 | 偏离 | 第 5 节 |
| 改进一次上一项 | #26 合了三项 | 用户 2026-10-01 的决定，已记录 |
| 开发 Skill 只能手动调用（dev-skills#8） | 一致 | 9 个 Skill 都同时设了 Claude Code 的 `disable-model-invocation: true` 和 Codex 的 `allow_implicit_invocation: false`，两个客户端行为相同。Codex 的 skill-creator 主张有副作用的 Skill 也保持可发现，与 Claude Code 文档相反（[vendor-latest.md](vendor-latest.md) 4.6）；这里以用户的决定为准 |

## 5. 对照“少写 prompt、只做边界”

用同一方法统计（按句号、分号拆句，含“不、只、必须、最多、一律、不得”等限制词的句子；与 2026-09-29 审查的口径不同，只用来前后对比）：

| 文件 | #15（`65c57bb`） | 现在（`74ae69d`） |
|---|---|---|
| deliver/SKILL.md | 4,687 字，116 句，限制 30 句 | 7,945 字，175 句，限制 50 句 |
| deliver/references（3 份） | 4,440 字 | 7,414 字 |
| deliver/scripts | 3 个文件 | 11 个文件，2,399 行 |
| core-spec/SKILL.md | 5,752 字，限制 60 句 | 7,514 字，限制 75 句 |

增长的来源是试跑中暴露的问题：每次修复都在正文加一段，同时在脚本里加一道检查；只有 #23 删过内容。agent-prompt-rules 第四节第 2 步要求改动时对照旧内容、删掉不再需要的，这一步在 #19–#26 里基本没做。

可以减的地方（建议，未经确认）：

1. **正文复述脚本在查什么。** 完成条件 3 把 `check-delivery.mjs` 的六项检查写了一遍，“开工与接续”把 `read-handoff.mjs` 的核对写了一遍。规则已经由脚本强制（二-10），正文只需写“运行它，按报错处理”；报错信息里写明修法（上一轮复盘的 N5）。
2. **开工的固定动作合成一个脚本。** `read-handoff` → 写冻结输入 → `--frozen-only` → `--preflight` 是每次都要做、顺序固定的窄桥（三-4），可以由一个脚本做完并输出 plan.md 冻结输入一节。
3. **只在某些情况才用到的分支移到 references（三-2）。** 找不到交接提交、只交本地路径、重新交接、放宽跨家族、里程碑顺序放行、口径偏差的细节。
4. **同一意思只写一处（三-5）。** 覆盖盲区怎样处理在正文的 6 处都写了一遍，“只改了测试、文档（和 lint 配置）”出现 3 次。Anthropic 的 prompt-audit 认为重复本身不算问题，重复的几处说法不一致才要合并（keep list 8）；F3、F8 就是说法不一致的重复，先修这两处，其余重复不必为了精简去动。

这几项都不改变行为，只改写法。按“一次上一项”的约定，建议放在 F1–F7 之后，单独一个 PR，并在下一个需求里观察 owner 是否漏做步骤。

## 6. 本次没有查的

- Agent-Archon 的 verify-archon 与功能地图（在 agent-archon 仓库，V1 的落点另议）。
- core-spec 的 `spec-example.md`、`verify-example.md` 逐条内容只核对了链接和与正文的对应，没有逐例复核。
- mr-for-human、design-for-review、recon-to-contract、plan-for-agents 只核对了它们与流程的关系（谁引用、是否冲突），没有按 agent-prompt-rules 逐句审。plan-for-agents 与 deliver 的 `plan-format.md` 是两套计划写法：自动交付用后者，前者用于需要人看的计划。README 写“core-spec 固化要求与决定，plan-for-agents 将其展开为执行计划”，容易让人以为自动交付也走 plan-for-agents，可以在 README 里补半句。
