---
id: discussion-2026-09-28-acceptance-from-decisions
recorded_on: 2026-09-28
timezone: Asia/Shanghai
source: current-conversation
topics: [验收定义, grill-with-docs, core-spec, plan-cross-review, 独立核查]
---

# 从决策点产出验收文档

## 用户问题（原文）

> 根据当前的流程和之前所做的调研和仓库里面的各种文档和最佳实践，我在获取到决策session之后，如何再根据决策点去产出对应的验证文档？
> 给出方案和依据的文档

## 助手方案（建议，未经确认）

以下为本轮答复的完整方案。流程指 [复杂需求交付流程 v0.2](../process/complex-requirement-delivery.md)。

### 结论

在 ②a（产出 spec 的 fork）里，spec 定稿后由同一 session 接着写一份《验收定义》；再开一个新 session 独立核查；核查通过后记下哈希冻结，交给 plan-cross-review、实现和最终验收使用。

```text
① grill session → 决策点
② fork
   ├─ ②a core-spec → spec → 同一 session 写《验收定义》
   │        写场景时发现未定的行为 → 问用户 → 答案写回 spec
   │   → ②c 新 session 独立核查验收定义（只报问题，最多 2 轮修订）→ 冻结（记哈希）
   └─ ②b 初版 plan
③ plan-cross-review：spec + 初版 plan + 验收定义 → 最终 plan（验证部分按场景 ID 引用）
④ 实现：验收定义只读
⑤ 验收 session：补齐命令并执行，产出结果和证据
```

### 一、为什么单独成文，为什么在 ②a 里写

单独成文：

1. spec 不放测试：core-spec 第 2 步明确删除“详细测试清单”。
2. 不并入 plan：plan 会被 plan-cross-review 的 C 重写，实现 session 也会报告对 plan 的偏离；验收依据要来自需求，plan 里的遗漏不能缩小验收范围，而且实现方不能改它。单独文件才能用哈希冻结。
3. 避免重复清单：plan 的“验证与验收”只按场景 ID 引用，写执行时机和工具缺口任务，不重抄场景。

在 ②a 里写：

1. ②a 在写 spec 时已经建了“议题 → 最终约定 → 依据”的对应表，正好是生成验收要求的输入。
2. 写场景常会暴露没定的行为（例如取消后该不该继续）。在 ②a 里问，答案能直接写回 spec；若另开第三个 fork 来问，答案只留在那个 fork，spec 和 plan 都看不到。
3. ②b 写 plan 通常更久，②a 多做一轮不拉长总时间。

备选：从 grill session 再 fork 一个 ②c 专写验收定义，与 spec、plan 三路并行。代价是新决定无法回流到 spec。

### 二、验收定义写什么

第一版用一个 Markdown 文件，人和 agent 读同一份；Agent Lord 需要机器判定时再定 JSON schema，不维护两份。

```markdown
# <主题>：验收定义

来源：spec 路径与 sha256；grill session ID；ADR / CONTEXT.md；源码 base SHA
状态：草案 / 已独立核查 / 已冻结（sha256）
效力：实现方只读；需要修改时先改 spec 并重新确认

## 1. 要求
| ID | 要求（可观察的行为或约束） | 来源（spec 章节） | 验证方式 |
验证方式三选一：场景（行为）/ 评审或静态检查（如“复用 X，不新增依赖”）/ 不适用（写明依据）

## 2. 场景
### S01 <标题>　覆盖：R01、R03　层次：真实入口
- 前提：
- 操作（从哪个真实入口）：
- 必须观察到：
- 不得出现：
- 观察方式与证据：
- 它必须拒绝的错误实现：
- 执行细节：已定位入口 / 缺观察工具（进 plan）/ 待实现后绑定命令

## 3. 回归范围
受影响的旧行为，以及对应的现有测试

## 4. 通过规则
PASS / FAIL / BLOCKED / NOT_RUN / STALE；全部必需场景 PASS 才算通过；证据绑定代码版本和运行实例

## 5. 验证工具缺口
现在观察不到、需要先补的能力，作为 plan 的前置任务
```

### 三、怎样从决策点生成

1. **逐条取最终约定。** 每条约定，包括默认值、例外、否定条件和接受的代价，变成一条要求；不需要场景的写明用什么方式验证。
2. **写成可观察的行为。** 前提、操作、必须出现、不得出现。重点看四类：实际发出的参数、持久化状态、默认装配、最终副作用。
3. **给关键场景写一个错误实现。** 即“符合文字却违反约定”的实现（core-spec 第 4 步的反例法），用来确认断言能把它拒掉。
4. **按风险选层次。** 局部规则用单测；模块接线用集成或契约测试；用户可见流程、默认装配、跨模块路径用真实入口。
5. **在仓库里定位入口。** 找现有测试、CLI、日志、调试接口；找不到的观察能力列为工具缺口，交给 plan 在实现前补上。
6. **没定的行为问用户。** 答案写回 spec 再写场景，不自行补语义。

### 四、独立核查查什么

新 session，只拿 spec、验收定义、ADR / CONTEXT.md 和源码 SHA，看不到 grill 会话；只报告问题，不改文件；由 ②a 修订，最多 2 轮。逐项检查：

- **覆盖：** spec 每条约定都有必需场景，或写明的非场景验证方式。
- **判别力：** 每条场景对其列出的错误实现会失败；断言没有只检查 UI 显示或内部调用而漏掉实际结果。
- **不越界：** 没有 spec 以外的新要求。
- **可执行：** 入口和观察方式在仓库中存在，或已列入工具缺口。

只把影响正确性或既定要求的问题列为实质问题，其余标为可选。

### 五、和后面步骤的衔接

- **plan-cross-review：** 验收定义作为冻结输入之一；最终 plan 的“验证与验收”按场景 ID 引用，并把工具缺口排成实现前的任务。这要改 Agent Lord 的 pipeline，可以先手工把文件放进输入。
- **实现：** 只读。实现方认为场景有误时提出来，走 spec 修改。
- **最终验收：** 新 session 为每条场景补齐命令、数据和超时，执行并产出结果和证据；失败交给实现方修复，再重跑受影响场景。见[验收设计](../research/verification-stage-2026-09-28/design.md)第 3、4 节。

### 六、依据

| 方案要点 | 依据 |
|---|---|
| 验收依据在写代码前、从需求产出 | [验收设计](../research/verification-stage-2026-09-28/design.md) §2 步骤 A、§5；[补充视频分析](../research/agent-delivery-2026-09-28/supplement-videos/analysis.md) §2；[此前讨论](2026-09-28-verification-and-delivery.md) A1 |
| 单独成文，spec 和 plan 都不承载 | core-spec `SKILL.md` 第 2 步；验收设计 §2 步骤 A、F；[SWE-Bench Pro 证据](../research/agent-delivery-2026-09-28/intermediate/evidence/findings.md) §5 |
| 不另建重复清单，plan 按 ID 引用 | [试验方案](../research/agent-delivery-2026-09-28/conclusions/experiments.md)“不要再加第二份 coverage/ledger”；补充视频分析 §2；agent-prompt-rules 三-5 |
| 在 ②a 同一 session 写 | agent-prompt-rules 二-2（掌握上下文的角色接着做下一步）、二-11；core-spec 第 1 步对应表；[流程文档](../process/complex-requirement-delivery.md)第四节第 1 条 |
| 重点查实际参数、持久状态、默认装配、副作用 | [30 天结论](../research/workflow-30d/conclusions/analysis.md)优先级一（D04、D05、M10、M06） |
| 错误实现与判别力检查 | 验收设计 §2 步骤 E；SWE-Bench Pro 证据 §5；core-spec 第 4 步 |
| 入口索引与工具缺口 | [Lauren 源码核查](../research/agent-delivery-2026-09-28/intermediate/lauren/findings.md)（`create-verification-skill`：启动、真实驱动、动作加结果加副作用、保留证据）；30 天结论的 Feature Map 与“入口→动作→观察→证据”索引；补充视频分析中 Pi 公开配置缺 QA 脚本 |
| 独立核查：新 session、逐项写明、只报实质问题、限 2 轮 | agent-prompt-rules 二-3、二-4、二-5、二-8；plan-cross-review 的 D |
| 未定行为回问用户 | grilling（决定由用户做）；验收设计 §1.2；agent-prompt-rules 二-9 |
| 状态与通过规则 | 验收设计 §4 |
| 冻结用哈希，不靠提示 | agent-prompt-rules 二-10；plan-cross-review 冻结输入 |

agent-prompt-rules 指 `dev-skills/skills/agent-prompt-rules/SKILL.md`（`88efec7`）；core-spec 指 `dev-skills/skills/core-spec/SKILL.md`（`88efec7`）。

### 七、边界

本方案没有在真实需求上跑过。第一次试用建议选一个有真实入口遗漏历史的需求，确认：错误实现会被场景拒掉、核查能找出真实遗漏、工具缺口在实现前被补上。

## 决定状态

- 用户尚未确认本方案。
- 待用户决定：在 ②a 里写还是另开第三个 fork；第一版用 Markdown 还是 JSON；是否每次都做独立核查。

## 后续：用户提出改为串行产出三份文档

用户原话：

> 这里的流程我想改一下：
>
> 首先，在 grill with doc 之后，我觉得 spec、验证和最终的 plan 应该是串行的：
> 1. 先产生 spec；
> 2. 然后产生验证的具体内容；
> 3. 最后根据这两个共同产出详细的 plan 计划。
>
> 后续再根据 cross review 做确认。所以，在这个串行的产生过程中，每一份都应该是一个单独的文档，比如说是 spec.md、verify.md 和 plan.md。
>
> 你觉得合理吗?

助手答复要点（分析，未经确认）：

- 合理，并且比上一轮“②a 写 spec 和验收、②b 并行写 plan”更好。它消除了 spec 与 plan 分别收敛、fork 之间新决定不互通两个问题；plan 能依据验收场景安排实现顺序，把验证工具缺口排在前面，并尽早跑通第一条真实入口场景。依据：补充视频分析 §2（Factory 先定断言再分配到切片）、Anthropic 长任务解读（先有功能清单再实现）、30 天结论（尽早跑通真实纵向路径）、agent-prompt-rules 二-2。
- 需要定的四点：
  1. 三份文档在同一个 session 里依次写（从 grill fork 一次），不每份换新 session；依据 agent-prompt-rules 二-2、二-11，以及 plan-for-agents 要求 plan 让没参与讨论的 agent 也能执行。
  2. cross review 的范围扩大到三份：reviewer 读三份文档，plan 和 verify 可在评审中修改，spec 有问题回到用户；这样上一轮提议的单独核查 session 可以取消。需要修改 plan-cross-review：冻结输入加 verify.md，D 增加 verify 对 spec 的覆盖与判别力检查、plan 对 verify 场景的承接检查。
  3. spec 是否忠实于 grill 决策，cross review 看不到 grill，只能由作者自查（core-spec 第 4 步）和用户确认；建议用户读 spec 开头 3–5 条核心决定后再往下写。
  4. verify.md 在 cross review 通过后冻结；实现后补的命令、数据写进验收结果，不改 verify.md。verify.md 目前没有对应 Skill，先按上一轮模板写，用过一两次再固化为 Skill。
- 流程文档等用户确认后更新为 v0.3。

## 后续：用户确认 spec 为唯一依据

用户原话：

> 首先，在 cross review 的阶段，根据 spec 做严格的一致性校验即可。因为在 spec 产出之后，就认为已经需求完全冻结，不需要再有其他的上下文，完全以 spec 作为最终结果（SOT）去做校验。
> Verify 和 Plan.md 在 Cross review 产出之后进行冻结，这 3 份文档都在 Grill with doc 这个 session 中产出。
>
> Cross review 需要新开 session，根据 spec.md 对 Verify 和 Plan.md 进行校验和修改。

用户确认的决定：三份文档都在 grill-with-docs session 内串行产出；spec 产出即需求冻结，是唯一依据；cross review 新开 session，只按 spec 校验并修改 verify 和 plan；两份在 cross review 产出后冻结。上一轮助手提出的“用户读 spec 核心决定”和单独核查 session 未被采纳，由 cross review 承担校验。

执行：[流程文档](../process/complex-requirement-delivery.md)更新为 v0.3。

助手提出、待用户确认：源码是否作为 cross review 的事实输入；cross review 发现 spec 本身有问题时如何处理。
