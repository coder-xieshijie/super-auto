---
id: discussion-2026-09-28-verify-skill
recorded_on: 2026-09-28
timezone: Asia/Shanghai
source: current-conversation
topics: [verify.md, core-verify, Skill 设计, 验收]
---

# verify.md 的产出 Skill：core-verify 草稿

## 用户要求（原文）

> 我们先确定一下关于 verify 的内容应该怎么去产出这个文档，需要获取一个对应的 skill，类似 core spec 这样的。
>
> 根据当前的流程和之前所做的调研和仓库里面的各种文档和最佳实践，我在获取到决策session之后，如何再根据决策点去产出对应的验证文档？

## 产出

- Skill 草稿：`process/skills/core-verify/`（已删除，现见 [dev-skills#11](https://github.com/coder-xieshijie/dev-skills/pull/11)），含 示例与检查案例 和 `agents/openai.yaml`（关闭 Codex 自动调用）。结构和写法对齐 dev-skills 的 core-spec（`88efec7`）。
- 草稿暂放本仓库，确认并试用后再迁入 `dev-skills/skills/core-verify` 并按全局约定建立软链接；dev-skills 的 main 检出是已安装 Skill 的来源，未确认前不改动。
- 本草稿尚未在真实 spec 上运行过。

## 在流程中的位置

依据 [流程文档 v0.3](../process/complex-requirement-delivery.md)：grill-with-docs session 内，core-spec 产出 spec.md 之后、写 plan.md 之前，由同一 session 调用 `/core-verify` 产出 verify.md。

| 项 | 内容 |
|---|---|
| 输入 | spec.md（唯一需求来源）；当前会话、ADR、术语表只用于理解用词和找例子；当前代码（定位入口和观察手段） |
| 产出 | 一个 `verify.md`：用途与来源、重点、要求表、场景、回归范围、验证工具缺口、完成条件 |
| 不做 | 写测试代码、执行验证、启动其他 agent；执行结果和状态词（PASS/FAIL 等）属于实现后的验收步骤 |
| 触发 | 手动（`disable-model-invocation: true`），与 dev-skills #8 的约定一致 |

## 每条规则弥补什么、依据是什么

按 agent-prompt-rules（`dev-skills/skills/agent-prompt-rules/SKILL.md`，`88efec7`）第四节第 1 条，逐条列出 Skill 中的规则、它针对的模型默认倾向或历史问题，以及依据。

| Skill 中的规则 | 不写时模型或流程容易出的问题 | 依据 |
|---|---|---|
| §1 spec 是唯一需求来源；在 plan 和代码之前写 | 从实现或计划反推验收，与实现共享遗漏；或把会话里的零散说法当要求 | 用户决定（spec 为 SOT，流程 v0.3）；[验收设计](../research/verification-stage-2026-09-28/design.md) §2 步骤 A；[补充视频分析](../research/agent-delivery-2026-09-28/supplement-videos/analysis.md) §2（Factory 先定断言）；[SWE-Bench Pro 证据](../research/agent-delivery-2026-09-28/intermediate/evidence/findings.md) §5 |
| §1 逐条列出默认值、例外、不得发生的事、接受的代价 | 合并条款时吞掉条件；只核对主题 | core-spec 第 4 步；plan-for-agents 第 5 步“正向覆盖”；验收设计 §2 步骤 B |
| §1 未定行为问用户，答复先写进 spec | 模型用看似合理的默认值补齐语义，验收与 spec 分叉 | grilling（决定由用户做）；验收设计 §1.2；agent-prompt-rules 二-9 |
| §2 证明方式三选一，结构性约束走评审 | 把“复用 X、不新增依赖”硬写成运行场景，或干脆不验 | 验收设计 §1.1、§2 步骤 C |
| §3 观察实际参数、持久状态、默认装配、最终副作用 | 只看界面显示或内部调用，漏掉真正的结果 | [30 天结论](../research/workflow-30d/conclusions/analysis.md)优先级一（D04 显示与首轮请求不一致、D05 Goal 不续跑、M10 默认装配漏接、M06 文本通过但 TUI 未验） |
| §3 每个必需场景写一个错误实现 | 断言太松，错误实现照样通过 | 验收设计 §2 步骤 E；SWE-Bench Pro 证据 §5（漏测）；core-spec 第 4 步反例法 |
| §3 只约束 spec 约定的内容 | 断言太窄，把实现细节写死，误拒其他正确实现 | SWE-Bench Pro 证据 §5（过窄测试） |
| §3 最少且足够的层次，一个场景可覆盖多条要求 | 每条要求铺满单测到 E2E，或全部推给昂贵的 E2E | 验收设计 §1.1；[此前讨论](2026-09-28-verification-and-delivery.md) A1；agent-prompt-rules 一-2 所引 Opus 5 过度验证 |
| §3 mock 只证明它边界内的行为 | mock 通过被当成真实验证 | 验收设计 §2 步骤 C |
| §4 在当前代码中定位入口，列出工具缺口 | 验证工具到最后才发现不存在；配置写了验证步骤但脚本缺失 | [Lauren 源码核查](../research/agent-delivery-2026-09-28/intermediate/lauren/findings.md)（`create-verification-skill`）；30 天结论的 Feature Map；补充视频分析（Pi 缺 QA 脚本）；[Anthropic 长任务解读](../research/anthropic-long-running-2026-09-28/analysis.md)第 5 条 |
| §4 执行状态如实标注 | 占位命令被当作可执行 | 验收设计 §2 步骤 D |
| §5 重点区放 3–5 个最易出错的场景 | 用户在 grill session 里难以快速判断验收抓没抓住要害 | core-spec 两层写法 |
| §5 回归范围 | 改动触及的旧行为被漏掉 | 验收设计 §1.1 |
| §5 交付前双向核对 | 与 core-spec、plan-for-agents 相同，作为完成条件写入；独立校验由 cross review 承担 | core-spec 第 4 步；agent-prompt-rules 一-2、二-5 |

## 有意不放进 Skill 的内容

| 内容 | 原因 |
|---|---|
| 执行状态词与聚合规则（PASS/FAIL/BLOCKED/NOT_RUN/STALE） | 属于实现后的验收执行；写 verify.md 时还没有执行 |
| 每个场景的环境、数据隔离、清理、超时 | 功能尚未实现，多数只能在验收时绑定；验收设计 §2 步骤 D 的字段留给执行步骤 |
| JSON 格式 | 第一版人和 agent 读同一份 Markdown；Agent Lord 需要机器判定时再定 |
| 独立核查 session | 用户决定由 cross review 按 spec 校验 verify.md |
| 性能、权限、并发等专项清单 | spec 有要求时自然进入要求表；Skill 不额外加没有依据的标准（验收设计 §1.2） |

## 建议的试用方式

用一份已经有真实结果的 spec 回测，例如 goal-v2（MR !7450）的 spec：检查 core-verify 产出的场景能否提前覆盖当时实际发生的遗漏（Goal 后台结束后不续跑、默认装配漏接）。能覆盖再迁入 dev-skills；覆盖不了就据结果修改 Skill。

## 待用户确认

1. 名称用 `core-verify`。
2. 写 verify 时发现 spec 没定的行为：Skill 当前的做法是问用户、答复先写进 spec 再写验收。这与“spec 产出即冻结”的关系需要确认：此时仍在 grill session 内、cross review 之前，是否允许这样修订 spec。
3. 先回测再迁入 dev-skills，还是直接迁入。

## 后续：用户确认并提交 PR

用户原话：

> 1. core-verify 可以
> 2. 没有 spec 就调用 core-specskill 生成
> 3. 直接在 dev-skills 上创建 pr

执行：

- 第 2 条理解为两种情况都按 core-spec 处理：尚无 spec 时先生成；写验收时发现 spec 缺少会改变判定的行为，按 core-spec 更新 spec（core-spec 在决定未定时会向用户提问），再写验收。core-spec 仅手动触发，模型无法直接调用，所以 SKILL.md 按 design-for-review 读取 explain-as-fool 的方式，直接读取同仓库 `core-spec/SKILL.md`。
- dev-skills 为公开仓库。设计记录 `docs/core-verify-design.md` 去掉了内部案例编号、产品名和本仓库链接，依据改引公开来源和 dev-skills 内的 agent-prompt-rules 原文。
- 在独立 worktree `dev-skills-core-verify`（分支 `shijie/core-verify`）提交 `72ccb7f` 并创建 [dev-skills#11](https://github.com/coder-xieshijie/dev-skills/pull/11)，未合并；dev-skills 主检出保持在 main。
- 本仓库草稿删除，以 dev-skills 为唯一维护源。
- 验证：链接与锚点可解析、无乱码；Codex `quick_validate.py` 只报 `disable-model-invocation`（已知）。未在真实 spec 上试用。

## 后续：吸收 Lauren 资料

用户原话：

> 现在的 verify 产出过程，你似乎没有提到 Lauren 的相关资料。她 SHIP 2000 个 PR 的流程，是否能够对当前的 verify 构造和产出提供一些参考？

助手核查的资料：[Lauren 源码核查](../research/agent-delivery-2026-09-28/intermediate/lauren/findings.md)、[访谈笔记](../research/agent-delivery-2026-09-28/intermediate/lauren/interview-2026-09-27-notes.md)、[Lauren 综合分析](../research/lauren/analysis.md)，以及 pstack 固定源码 `ecc249f` 中的 `create-verification-skill`、`maintain-verification-skill`、功能地图示例、`principle-test-behavior-not-implementation`、`principle-prove-it-works`、`principle-sequence-verifiable-units`、`tdd`、`docs/guide/06-verify-and-ship.md`、`playbooks/{feature,bug-fix,multi-phase-plan,autopilot-full,shipping}.md`、Benny 的 `control-adapter.md`。

结论：能提供参考。此前草稿只借用了 `create-verification-skill` 的“定位入口”，以下机制此前未吸收：

| Lauren 的机制 | 出处（pstack 路径） | 对 core-verify 的改动 |
|---|---|---|
| 控制命令 + 功能地图由项目长期维护，是验证的唯一来源 | `skills/create-verification-skill`、`docs/guide/06-verify-and-ship.md`、访谈（控制 CLI 与 Feature Map） | verify.md 只写本次验什么、怎样判定；驱动步骤引用项目验证能力；工具缺口补成可复用能力，不写一次性脚本 |
| 功能地图列出全部用户入口；跳过的入口不能借另一入口宣称已验 | `feature-map-example/README.md` | 新增场景字段“入口”；新增“覆盖每个入口”规则 |
| 功能状态清单（默认、加载、空、错误、禁用等） | Benny `control-adapter.md` | §1 用入口和状态清单查 spec 缺口 |
| 证明走真实用户路径；安排前提不等于注入现象 | `create-verification-skill` 证明标准；`control-adapter.md` | 新增“走真实用户路径” |
| 动作与结果状态都要观察；写入要从只读第二视图读回 | 证明标准；功能地图示例 | “观察实际结果”补充；证明形式表“存储” |
| 导入函数全返回 undefined 仍能通过的测试要重写；“不存在”断言要配正向观察；期望值用字面值 | `principle-test-behavior-not-implementation` | 新增“断言要能失败”：字面预期、正向配对、空实现检验 |
| 修复前先确认测试因预期原因失败；回归对照在主干和改动上各跑同一场景 | `tdd`、`bug-fix.md`、`multi-phase-plan.md`、`autopilot-full.md` | 新增场景字段“基线预期”和“用基线对照”；基线作为第一个现成的错误实现 |
| 按改动类型选检查：CLI 跑命令、UI 走流程、迁移重放输入、存储读回、性能前后对比 | `06-verify-and-ship.md`、`multi-phase-plan.md`（双侧性能门槛） | 新增证明形式对照表 |
| 在目标平台上验证 | 访谈 14:23–16:50（Linux 虚拟机） | 证明形式表“平台支持”；mock 规则补“spec 点名的平台在该平台上验” |
| 技能改动用 eval 验证：种子缺陷、盲评，同时看漏报和噪声 | PR #419；访谈 16:53–17:50 | 设计记录补评估方法：用带已知遗漏的历史 spec 做种子缺陷 |

未照搬：每 PR 十条实时通道、swarm 裁决、Graphite、模型配置、自动合入、以 PR 数为目标。它们属于执行与合入阶段或个人偏好。2,000 PR 是本人自述，不作为依据。

执行：

- 改动直接做在 dev-skills#11 的 worktree（`/Users/minimax/code/github/xieshijie/dev-skills-core-verify`，分支 `shijie/core-verify`）：`skills/core-verify/SKILL.md`、`references/worked-example.md`（S01/S02 补入口与基线预期，新增 5 个检查案例，共 13 个）、`docs/core-verify-design.md`（新增 pstack 依据表，链接到公开固定 SHA，不含本仓库内部案例）、`README.md` 摘要。未提交、未推送。
- 本轮开始时误在本仓库重建了 `process/skills/core-verify/SKILL.md`（当时未看到 fork 会话已将草稿迁出），已删除，恢复为以 dev-skills 为唯一维护源。

待用户确认：是否把上述改动提交并推送到 dev-skills#11。
