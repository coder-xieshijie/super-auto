---
id: research-goal-v2-deliver-trace-approaches
recorded_on: 2026-10-01
timezone: Asia/Shanghai
source: 本仓库已有调研（零基设计、派系归类、工业交付证据卡）、三家原文的本机存档、两次试跑的 trace
scope: 回答“减少人工介入目前走的是什么方案、用的是哪一家、各家有哪些方案、哪家效果最好、哪种方案代码效果最好成功率最高”
---

# 减少人工介入：我们用的方案、三家各自的方案与效果证据

讨论记录见 [2026-10-01 MR 7595 复盘](../../discussions/2026-10-01-goal-v2-deliver-trace-review.md)。三家原文的逐字核对在 [source-check/](source-check/)，各家方案的出处在[零基设计](../zero-based-delivery-2026-09-29/design.md)和[派系归类](../../discussions/2026-09-28-workflow-schools.md)里，第三方研究在[证据卡](../agent-delivery-2026-09-28/intermediate/evidence/findings.md)。

## 1. 我们目前走的方案

[复杂需求交付流程](../../process/complex-requirement-delivery.md) v0.21，把人的参与压到两头：

| 阶段 | 人做什么 | 减少人工的手段 |
|---|---|---|
| 定义 | 回答 grill 的问题，确认一次 spec 和 verify | 一次把会改变验收结果的决定问完；spec 写明交付授权；另一家模型查漏，问题在冻结前问完 |
| 交付 | 只在四种情况被找：spec 矛盾或缺决定、缺权限或环境、授权外的不可逆操作、卡住 | 一个 owner 连续做到 MR；agent 自己在真实入口跑场景（verify-archon、功能地图）；每个里程碑由新上下文的子代理检查；最后另一家模型独立验证；必须发生的步骤交给脚本（read-handoff、check-delivery、record-milestone-check、run-verifier 的预检与限时） |
| 合入 | 用户看 MR、合入 | — |

## 2. 用的是哪一家

不是某一家，是按环节组合的。下表是每个环节的主要来源：

| 环节 | 主要来源 | 说明 |
|---|---|---|
| 一个 owner 从开工负责到 MR | OpenAI（Codex 单会话连续约 25 小时，LH L7；Symphony 一个 issue 一次运行）、Lauren（autopilot-full 每个 PR 一个 owner） | Anthropic 也主张先用单 agent（BMAS） |
| 执行者自己写、持续更新的计划（plan.md） | OpenAI ExecPlan（PL L36：只读计划就能重启） | 三家都不让人审计划 |
| agent 能自己启动、操作、观察产品 | 三家共同：OpenAI 每个 worktree 一个应用实例并接入 CDP（HE L43）；Anthropic `init.sh` 加浏览器自动化（EH）；Lauren 控制命令加功能地图（create-verification-skill） | OpenAI 把它当最主要的手段：人的瓶颈从写代码变成 QA，于是把 UI、日志、指标都交给 agent 读（HE L41） |
| 里程碑由新上下文的子代理检查 | Anthropic（Fable 5 建议按间隔用子代理对照 spec 检查，F5 L173；独立 evaluator 比自评严，HD） | Anthropic 内部也有相反意见：Opus 5 上建议去掉额外验证（O5 L61） |
| 最终由另一家模型验证 | Lauren（验证者与写代码者用不同模型家族，orchestrate:17；show-me-your-work:67） | 只有 Lauren 明确要求跨家族；OpenAI、Anthropic 都用自家模型 |
| 规则进脚本和钩子，prompt 只写边界 | 三家共同：OpenAI “promote the rule into code”（HE L108）；Anthropic 钩子是确定性的（CCBP L241）；Lauren “The instruction is the symptom.” | — |
| 只在少数情况停下找人 | 三家共同：OpenAI 只在需要判断时找人（HE L152）；Anthropic 只在破坏性操作、真正的范围变化、只有用户能给的输入时停（F5 L64）；Lauren 待决问题带默认答案、绕开继续（orchestrate:105，`orch gate park --default`） | — |
| 少写 prompt，删之前做对照 | Lauren（PR 419 的 A/B）、Anthropic（一次去掉一个组件做对照，HD L119） | — |
| **先冻结 spec 和 verify，交付中只读** | **三家都没有这一环**，是我们自己的前提（用户 2026-09-29：人只在开始时定 spec 和 verify） | 最接近的是派系归类里的“规格和场景先行”（StrongDM、Factory）。Lauren：“the best spec is code”；OpenAI 的 `/goal` 目标文本就是完成标准，运行中可直接改；Anthropic 的 sprint contract 每段开工前协商，后来随模型升级去掉了 |

一句话：骨架主要来自 OpenAI（单 owner、活计划、可观测的环境、规则进代码），检查分层来自 Anthropic（新上下文检查）和 Lauren（跨家族验证），prompt 写法来自 Lauren 和 Anthropic；“冻结 spec 和 verify”是我们自己加的。

## 3. 三家各自减少人工介入的方案

| | OpenAI | Anthropic | Lauren（pstack） |
|---|---|---|---|
| 人在哪里介入 | 写 issue 或目标；运行停在 Human Review 状态时看（A05 L43） | 开头访谈写 spec（CCBP L366–368）；结束时审阅 | 交接时给目标、完成条件、权限、逃生口（guide/07:9）；预先点名的 gate；交互类改动在合入前看截图和视频（multi-phase-plan:13） |
| 主要手段 | 让环境对 agent 可读（应用、日志、指标）；自定义 lint 强制架构，报错里写修法（HE L100）；运行时编排：issue 驱动、静默超时判停滞并重试（A05 L828）；最少的阻塞门禁、短命 PR，“改错便宜、等待昂贵”（HE L114） | harness：初始化 agent 加进度文件和 JSON 功能清单（EH）；planner、generator、evaluator 三角色，独立 evaluator 要调教（“Out of the box, Claude is a poor QA agent”，HD L113）；钩子保证必须发生的动作；无人值守时由 harness 判断回合是否真的做完，最多续跑两三次（O55 L61）；随模型升级删脚手架（HD L180） | 执行期授权，默认决定带一句理由和一个推翻词（poteto-mode SKILL:20）；待人决定的事进 gates 并必须带默认答案（脚本强制）；root 每 30 分钟审计，只把提交、推送等副作用算进展（autopilot-full:10）；按 SHA 记的验证账本；先让一个单元走完全程（pilot）；改指令先做 A/B |
| 计划与验收 | ExecPlan 由 agent 写；目标即完成标准 | planner 只写产品级 spec，路径由 generator 定（HD L64） | 不写 spec，给能跑的检查（“Now the agent has three checks it can run”） |
| 侧重 | 环境与编排 | harness 结构与模型提示 | Skill 规则与监督循环 |

三家并不互斥。它们回答的是同一件事的不同层：OpenAI 管环境和运行时，Anthropic 管 harness 结构和对模型怎么说，Lauren 管写给 agent 的规则和谁来监督。我们的流程三层都在用。

## 4. 哪一家效果最好

**现有证据回答不了。** 各家的数字都是自报，任务、模型、指标都不同，没有同难度、同预算的对照：

| 来源 | 自报结果 | 缺什么 |
|---|---|---|
| OpenAI harness engineering | 5 个月约 100 万行代码、约 1500 个合入的 PR，起初 3 名工程师，人均每天 3.5 个 PR（HE L23）；Codex 单次连续运行约 25 小时（LH L7） | 缺陷率、人工审查分钟、需求完成率 |
| Anthropic harness design | 同一句话的需求：单 agent 20 分钟、9 美元，核心功能不能玩；完整 harness 6 小时、200 美元，能玩（HD L84–103）；Opus 4.6 上的第二版 harness 3 小时 50 分钟、124.70 美元（HD L145–153） | 只有一两个示例应用，作者本人评判 |
| Anthropic C 编译器 | 16 个 agent、约 2000 个会话、约 2 万美元，10 万行，能编译可启动的 Linux 6.9（A07 L12、L101–103） | 单个项目，有现成测试集和参照编译器 |
| Lauren | 自述 2000/2500 个 PR（[交付调研报告](../agent-delivery-2026-09-28/conclusions/report.md) L48） | 没有 PR 审计、复杂度归一、人工时间或线上缺陷数据。PR 419 的 A/B 是受控的，但测的是单条指令，不是整套方法 |
| 第三方 | 多 agent 在 SWE-bench Verified 子集上平均比单 agent 低 2%–15%（只抽 20 题，区间约 ±20 个百分点）；SWE-Bench Pro 公开集约 30% 的题目验收本身有问题（[证据卡](../agent-delivery-2026-09-28/intermediate/evidence/findings.md)第 3、5 节） | 不是三家方法之间的对照 |

本仓库 9/28 的派系归类已经得出同样的结论：“所有吞吐数字都是各家自述，没有独立审计，也没有同难度、同预算的跨派对照。仓库资料不能排出哪一派最好。”

## 5. 哪种方案代码效果最好、成功率最高

“成功率”目前也算不出来：我们自己只有两个样本。MR 7576 交付到可合入（跨模型验证 PASS、CI 通过，一处偏离由用户接受），MR 7595 还在进行。

能说的是：三家共同支持、我们两次试跑也确实抓到问题的几个环节，对代码质量贡献最大。

| 环节 | 三家 | 我们的数据 |
|---|---|---|
| 在真实入口上跑验收场景，而不是只看作者自己的测试 | 三家共同；Anthropic 的单 agent 与 harness 的差别主要来自 QA 抓出的缺口（HD） | 7595 的 M2 场景第 1 轮抓到 4 个产品缺陷 |
| 新上下文的独立检查 | Anthropic、Lauren 支持；OpenAI 用 agent 互审 | 7595 的里程碑检查三轮报 14 项，全部属实，带来 7 个修复提交；7576 报 7 项 |
| 另一家模型的验证 | Lauren | 7576 的跨模型验证抓到 1 个同家族检查漏掉的问题；7595 定义阶段的跨模型查漏改掉 verify 的 30 处问题 |
| 事前写清能检查的验收 | 三家共同；第三方的 MirrorCode 显示有明确行为参照的任务能长时间自主纠错 | 两个需求的 spec 在交付中都没改过；verify 在 7595 交付中改了 3 处口径 |
| 必须发生的步骤交给脚本 | 三家共同 | 7595 里门禁拦住了检查顺序问题；6 个修复提交来自 owner 手选检查命令的漏项（O6 要补的就是这里） |

和“减少人工介入”直接相关的一点：7595 里代价最大的几次人工介入（中断后停工 10.6 小时、审批挡住子代理、验收口径冲突），原因都在我们自己的流程和环境，不在模型能力，也不是因为选错了哪一家。眼下回报最高的是修这些（研究档案第 8 节的 O1、O5、O3、O4），而不是改用另一家的方法论。

## 6. 怎样才能回答“哪种最好”

按[零基设计](../zero-based-delivery-2026-09-29/design.md)第五节和交付调研报告的建议，每个需求记同一组数字，攒几个需求再比：

- 定义阶段之后用户介入几次，各是什么原因（本次第 6 节的分类可以直接用）；
- 各检查层抓到的问题数（跨模型查漏、里程碑检查、场景、CI、独立验证），以及 MR 之后用户自己又发现了几个；
- 墙钟时间、主会话实际工作时间、费用；
- 有没有中断、停工，多长。

要比较两种做法（例如里程碑检查留不留、跨家族验证要不要），一次只改一项，同类需求上对照，这是 Lauren PR 419 和 Anthropic HD L119 的做法。
