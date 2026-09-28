# Lauren 更新核查：快速交付 PR 的遗漏

核查日 2026-09-28。上次主要抓住“先让单个 agent 深入理解、操作和验证产品，再放心并行”；本轮补上具体执行、恢复、审查、合入机制。源码是公开方法的直接证据，不等于这些方法的生产收益已经得到验证。

## 1. 来源与版本

- **L01 官方 pstack**：[固定 SHA](https://github.com/cursor/plugins/tree/ecc249f1e306fc64ddf83c7bed16cacf7c2239db/pstack)，本地 [完整目录](../../raw/lauren/pstack-source/README.md)。版本 0.15.5，README 列 23 个 playbooks、23 个 principles；158 个文件归档。没有采用第三方 fork 的旧数量或模型默认值。
- **L02 指令消融**：[PR #419](https://github.com/cursor/plugins/pull/419)，9 月 23 日合入；[API 原文](../../raw/lauren/pr419.json)。
- **L03 规则冲突修复**：[PR #422](https://github.com/cursor/plugins/pull/422)，9 月 23 日合入；[API 原文](../../raw/lauren/pr422.json)。
- **L04 最新访谈**：[Peter Yang 原文](https://creatoreconomy.so/p/grok-bot-team-14-best-bots-peng-zheng-lauren-tan)，2026-09-27，作者页 45:03、YouTube 播放器 45:04；[网页快照](../../raw/lauren/interview-public-page.html)。作者链接 [YouTube](https://www.youtube.com/watch?v=xZ5TEaleUdg)。文章后半付费未读取；匿名视频采集失败、字幕重试 429，[状态](../../raw/lauren/interview-2026-09-27/run-status.json)、[重试日志](../../raw/lauren/interview-2026-09-27/retry.log)。随后浏览器公开字幕导出成功，[完整自动字幕](../../raw/lauren/interview-2026-09-27/transcript/youtube-browser-export.txt)，这是 **L05**，没有绕过订阅墙。
- 先前的两段视频、2,000/2,500 PR 自述及时间核查仍在 [旧档案](../../../lauren/bookmark-videos/README.md) 和 [X 讨论](../../../lauren/x-discussion/README.md)。本轮没有取得可审计的个人 PR 总表、净人工时间或生产质量数据。

固定仓库 HEAD 的日期为 9 月 25 日；pstack 自身最新路径提交为 9 月 23 日 PR #422。下表多数是**此前未覆盖的已存在材料**，不应包装成全部是四天内新增的方法。

## 2. 遗漏矩阵

下表路径相对 [pstack 源码根目录](../../raw/lauren/pstack-source/README.md)，每项均可用固定 SHA 的 GitHub 目录核查。

| 上次不足 | 本次源码确认的机制 | 对快速交付的作用 | 适用限制 |
|---|---|---|---|
| 并发原则较抽象 | `playbooks/feature.md`：阻塞首步、独立工作流、共享可变状态、最小安全拆分四项检查；耦合功能交一个 owner | 避免拆成大量缺上下文的小工单 | 不同文件不必然语义独立；源码自己也要求按阶段重写拆分 |
| 只有多 agent 分工，没有调度节奏 | `orchestrate.md`：滚动补充 ready work、批量 drain 完成事件、避免全批次等最慢任务 | 保持吞吐且减少协调中断 | 大约十个直接子任务是作者经验，非最佳人数实验 |
| 整合像尾声 | `orchestrate.md`：第一项验收后持续落地；单一 stack topology writer；记录 frontier/generation | 早发现组合问题和基线漂移 | 拓扑写入串行不等于所有编码/验证串行；其具体 Graphite 流程不可直接套 GitLab |
| owner 在代码完成后退出 | `autopilot-full.md`：一个 owner 负责实现、自证、CI、babysit 到 merge；root 独立裁决 | 减少人类转交 review/CI 反馈 | 明确 full 自主授权；人类拥有的 PR 不接管；本轮未授权执行该流程 |
| 自动化模式未区分 | `autopilot-stack.md` 负责构建验证线性 stack，由操作者审查合入；`autopilot-full.md` 处理独立 PR 到合入 | 区分“自主做到可审”与“允许自主合入” | 无需把自动合并设为统一默认；独立 PR 默认基于主干，真依赖再排顺序 |
| PR 绿色等同完成 | `babysit.md` 只负责 merge-ready；`shipping.md` 独立验证并逐个合入连续已验证前缀 | 避免 PR 创建、开 automerge 就宣告交付 | 已合入也不是已经发布；需要项目另行定义生产验收 |
| review 证据缺时效定义 | 验证绑定 head/base/patch identity；新 patch 使旧结论失效；rebase 后重查 CI/mergeability | 不把旧 SHA 的 PASS 带到新代码 | patch 相同也不能无条件复用运行结论：依赖、构建、环境变化仍需对应验证 |
| agent 活着与有进度混用 | `orchestrate.md`、watcher 脚本：从实际副作用判断活性，读状态不等于恢复；晚到回报需核对 | 降低不断问“继续了没”的成本 | `orch` CLI **只记账**，不负责派发、唤醒或等待；记录不自动构成完整调度系统 |
| 验收只保留最终截图 | `create-verification-skill`：启动、doctor、真实驱动、动作+结果+副作用、隔离、清理后保留证据 | agent 可以复现真正的用户路径 | 新生成的 verify skill 要自己跑通一次；无法隔离的实例不得盲目双驱动 |
| 所有任务倾向重流程 | `orchestrate` 区分便宜命令验证与昂贵独立判断；`babysit` 给小改动/docs check 模式 | 按成本和风险配验证深度 | 同时 `multi-phase-plan` 模板又强制十条 live lane；这是具体重型模板，不能套到所有任务 |
| 只有交付内循环 | Benny 把报告分诊与已确认 bug 的复现/小修复拆成自动化包 | 连接问题来源、去重、复现、修复 | 包处于 dormant 状态，需配置；不是任意需求自动实现的证据 |
| 提示越多似乎越好 | PR #419 用种子缺陷、盲评/结构化评分删除冗余指令；PR #422 修角色冲突 | 控制框架自身的复杂度和错误 | 局部 A/B，不是广泛生产评估；#422 明确未跑真实 agent 流程 |

上表简写的 playbooks 均位于 `skills/poteto-mode/playbooks/`。其他入口：`skills/swarm/SKILL.md`、`skills/create-verification-skill/SKILL.md`、`automations/benny/README.md`。

## 3. 核心变化：从个人提示习惯到持续交付协议

### 一个需求 owner，多个可独立判断的工作者

协调者维护目标、依赖、授权和外部事实；实现者拥有完整切片。scope 太大才加中间协调者。独立调查、方案竞赛、模块实现和 review 是不同工作，不能只统一算作“开了几个 agent”。`swarm` 区分 partition、race、mixed，并要求事先确定 first-pass / rank-all / best-of 的取舍规则；失败 worker 不得被隐藏成覆盖完成。

`autopilot-full` 的 code-ready SHA 出现后，owner 继续处理 CI 和自证，同时独立开展 gate/live/diff/regression 判断。发现汇总为一个修复波次，再对新版本裁决。这有望减少角色接力造成的闲置，但收益需在自身任务上量化。

### 人类等待要分类

`principle-never-block-on-the-human` 主张对可逆、可审查工作先做出结果，产品方向仍来自人。`orchestrate` 把真正的决定收集成有上下文的 gates，能绕开的任务继续运行。移植时应继承用户现有授权，不能把源文件中的自动合入权限当作本次授权。

### 代码身份与验证身份一致

`shipping` 处理的是实际可落地前缀，而非任何“绿”标记。合一个 PR 后刷新主干、重新核对下一项；watcher 负责让等待变成可恢复事件。它与用户已经强调的 fixed SHA、默认装配、真实验收一致，更值得做的是验证已有能力是否连成完整链路。

## 4. 真正新增的 9 月 27 日访谈

完整自动字幕补齐了摘要，详见 [逐段核查笔记](interview-2026-09-27-notes.md)：

- 14:16–17:50：Lauren 描述让 agent 控制真实 Linux VM 验证平台支持；pstack 变更派不同模型做 eval，目标达成才落地。
- 20:01–21:25：Dr. Eggbot 从历史对话发现反复错误、过杂上下文，建议调整 skill、bot 和 routine；过频唤醒消耗预算。
- 25:22–27:57：chief of staff → Matcha lead → 工程 supervisor bots → cloud coding agents。该层次是个人做法，不能证明多一层协调必然更快。
- 28:02–29:53：她自述 agent-friendly 代码库支持部分自动合并，强调规模与质量兼顾。没有给出可审计事故/返工数据。
- 32:46–35:00：社交 bot 聚合用户重复 bug；工程 bot 直接拿对应上下文并提出设计，减少手工复制粘贴。这是需求反馈外循环，仍包含人触发工程安排。
- 39:34–42:07：先观察、纠偏，沉淀 skill；确认能重复一次完成，再设置自动 routine。不是一开始就无人看管。

这些是**口述证据**，未经人工逐字听校或画面核验。专名错识明显，原始字幕保留不改写。Peng 的关键帧比例与主持人的 80% 设问不应写成 Lauren 的工业自动化效果；字幕也未给出完整权限策略、失败率、质量和成本。

## 5. 两个很值得学习的维护实例

**PR #419：用实验决定删什么。** 作者自报在两个种子缺陷 diff、每边 22 次 review 上，删去部分指令后命中 142/154，对照 139/154；其中一个模型的噪声增加。reflect 的固定 3–5 项上限也会制造填充项。实验样本和 lead 模型受限，有些规则因没有覆盖实验而保留。可迁移方法是“固定任务集、一次改变一个组件、同时看漏报和噪声”，不能推导为指令越少必然越好。

**PR #422：消除相互冲突的角色规则。** babysit 不 rebase 与 owner 必须 rebase、append-only 与审计时删旧行、开 PR 的子 agent 不跟进与 autopilot owner 需跟进，这些矛盾均通过明确角色或追加 superseding 记录修正。模型配置读取和失败 fallback 也被统一。它本身是流程复杂度能制造故障的例子；代码检查通过不能替代真实运行验证。

## 6. 不建议照搬

- 不以 2,000/2,500 PR、agent 数、模型 effort 或 token 消耗作为成功门槛。
- 不强制所有小需求经历十条 live lane、完整方案竞赛和多轮全量审查。
- 不复制特定模型 slug、Graphite 命令、默认 ready PR、删除注释等个人偏好。
- 不用 coordinator 的“已完成”覆盖真实工具证据，也不把账本当运行事实或互斥锁。
- 不把 pstack 安装视作工业自动化已经成立；仓库可运行性、真实验收、权限、恢复和代码身份都要在项目里成立。

更适合用户的增量是：**稳定需求 owner、验收入口、真实上游产物、持续合入准备、按能力限流、删掉无收益的编排**。详见 [综合报告](../../conclusions/report.md)。
