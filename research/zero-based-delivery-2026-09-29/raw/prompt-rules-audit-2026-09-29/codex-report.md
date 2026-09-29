已按 brief 只读审查，未修改文件。共发现 24 项会改变 agent 行为的问题。

## 审查结果

### 1. 两个 description 混入执行流程

- **规则编号：** 三-1
- **位置：** [core-spec/SKILL.md:4](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/SKILL.md:4)、[deliver/SKILL.md:4](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/SKILL.md:4)
- **原句：** `另一家模型在新 session 中查漏后……`；`逐里程碑在应用里验证、另一家模型的独立验证、MR/PR 与 CI……`
- **为什么违反：** description 应只负责“做什么、什么时候用”。这里塞入模型选择、查漏、冻结、里程碑和 CI 流程，会让触发判断过窄，并提前加载正文才需要的实现方法。
- **建议：** 改为：
  - core-spec：`将已结束的需求讨论和材料收敛为用户可确认的 spec.md，并在需要自动交付时生成 verify.md。用于“整理核心决策”“写验收要求”；只要 spec 时不生成 verify。`
  - deliver：`按已确认并冻结的 spec.md 和 verify.md 实现需求并交付可合入的 MR/PR。用于“按 spec 和 verify 交付”“做到 MR 可合入”。`

### 2. 未取得用户指定目录时擅自选择目录

- **规则编号：** 一-1、一-3
- **位置：** [core-spec/SKILL.md:95](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/SKILL.md:95)
- **原句：** `使用用户指定路径；未指定时沿用当前项目文档惯例。`
- **为什么违反：** 用户已决定需求文档目录每次由用户指定；当前 fallback 会在缺少必要输入时自行决定位置，导致交接文件写错目录。
- **建议：** 改为：`spec 与 verify 写入用户本次指定的目录；未提供目录时，先完成不依赖落盘的整理，并请求用户给出目录。`

### 3. 把“没有非目标”一律当成缺陷

- **规则编号：** 一-4、二-9
- **位置：** [core-spec/SKILL.md:61](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/SKILL.md:61)、[gap-check.md:17](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/gap-check.md:17)
- **原句：** `非目标和授权只能由用户决定：讨论中没有定下时，作为最小必要问题提出`；`缺项：没有目的或非目标`
- **为什么违反：** 即使不存在容易误扩展的相邻范围，agent 也必须停下来要求用户发明“非目标”；查漏方也会固定报错。
- **建议：** 改为：`非目标只在用户已经明确，或存在会实质改变交付范围的相邻事项时记录；否则不补写，也不为此单独提问。`

### 4. 固定的金字塔写法属于通用写作脚手架

- **规则编号：** 一-1、一-6、三-3
- **位置：** [core-spec/SKILL.md:63](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/SKILL.md:63)
- **原句：** `正文采用两层`、`通常选 3–5 个`、`每点用结论句 + 必要解释`
- **为什么违反：** 当前模型能自行组织文档；固定层数和条目数会让简单需求被填充、复杂需求被硬压成 3–5 点。
- **建议：** 合并为：`开头突出足以理解方向的核心决定；详细约束按议题组织，每条规则只保留一个权威位置。`

### 5. 作者被要求做两轮通用自查

- **规则编号：** 一-2、二-5、三-5
- **位置：** [core-spec/SKILL.md:97](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/SKILL.md:97)、[verify.md:108](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/verify.md:108)
- **原句：** `对照原始约定检查 spec`；`交付前对照 spec 核对`
- **为什么违反：** 同一作者先写、再逐项复查 spec、再逐项复查 verify，之后还有独立查漏；增加重复轮次，同时仍保留作者自证偏差。
- **建议：** 删除独立的自查步骤，改成结果要求：`产物必须能双向追溯：每项已确认约定在 spec/verify 中有落点，每项规范性断言有来源；由独立查漏 session 核验。`

### 6. 查漏方拿不到原始材料

- **规则编号：** 二-3
- **位置：** [core-spec/SKILL.md:142](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/SKILL.md:142)、[gap-check.md:7](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/gap-check.md:7)、[cross-model.md:3](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/cross-model.md:3)
- **原句：** `它只拿到 spec、verify 和相关仓库`；`你看不到产生这两份文件的讨论，这是有意的`
- **为什么违反：** 独立验证者应拿到完成标准、产物和原始材料，只排除过程讨论。当前查漏方无法发现遗漏的用户决定或无依据新增。
- **建议：** 改为：`查漏方拿到 spec、verify、相关仓库，以及第 1 步声明的原始需求、ADR 和最终澄清范围；不提供作者的过程性推理和中间草稿。`

### 7. 冻结哈希只靠 prompt 保证

- **规则编号：** 二-10
- **位置：** [core-spec/SKILL.md:156](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/SKILL.md:156)
- **原句：** `计算两份文件最终的 sha256，确认 verify.md 来源中记录的 spec 哈希与最终 spec 一致。`
- **为什么违反：** 这是每次冻结都必须发生、且完全可以机械校验的动作；只写在 prompt 中会出现漏算或旧哈希仍被提交确认。
- **建议：** 改为：`请求确认前运行冻结检查脚本，由脚本校验 spec、verify 的 sha256 及 verify 中记录的 spec 哈希；检查失败时不得请求冻结。`

### 8. 两轮后把所有剩余问题都交给用户

- **规则编号：** 二-8、二-9
- **位置：** [core-spec/SKILL.md:150](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/SKILL.md:150)
- **原句：** `第二轮仍有的问题列为待确认，交给用户决定。`
- **为什么违反：** 剩余问题可能只是覆盖缺失、入口写错等作者应修的缺陷，并不需要用户决定；当前措辞会造成不必要停顿。
- **建议：** 改为：`第二轮后保留未决项和证据；只有确需用户选择的 spec 决定才提问，其余作者缺陷不得转交用户，也不得宣称通过。`

### 9. 每个场景强制填写基线预期和错误实现

- **规则编号：** 一-1、一-6、三-3
- **位置：** [verify.md:40](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/verify.md:40)、[gap-check.md:20](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/gap-check.md:20)
- **原句：** `错误实现：一个看似合理……`；`每个场景都有……基线预期和错误实现`
- **为什么违反：** 这是测试设计方法而非验收结果；简单场景也会被迫编造错误实现、检出基线，产生填表式内容和额外操作。
- **建议：** 改为：`每个场景必须有能区分符合与不符合 spec 的检查点；仅在基线行为或具体错误实现有助于消除歧义时记录它们。`

### 10. 写 verify 时要求实际试运行验证工具

- **规则编号：** 一-2、二-5
- **位置：** [verify.md:80](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/verify.md:80)
- **原句：** `能低成本试运行的，试运行一次。`
- **为什么违反：** 这是给文档作者增加的通用验证步骤，还与 core-spec 的“不执行验证”冲突；可能在尚未授权的环境产生状态。
- **建议：** 改为：`引用的入口应对应来源中记录的 commit；无法从仓库确认时，标为“实现后绑定命令”或验证工具缺口。`

### 11. 强制先建设可复用验证基础设施

- **规则编号：** 一-1、一-6
- **位置：** [verify.md:84](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/verify.md:84)、[deliver/SKILL.md:47](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/SKILL.md:47)
- **原句：** `缺口补成项目可复用的验证能力`；`验证工具缺口排在最前面`
- **为什么违反：** spec 未要求时，agent 也会先新增日志、查询、指标或控制命令，扩大交付范围并规定实现顺序。
- **建议：** 改为：`记录无法观察的检查点及所需能力；是否新增验证工具及其顺序，由 owner 按 spec、成本和仓库规则决定。`

### 12. 每个 session 都强制重复冒烟检查

- **规则编号：** 一-2、二-5、三-5
- **位置：** [verify.md:100](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/verify.md:100)、[deliver/SKILL.md:45](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/SKILL.md:45)
- **原句：** `每个实现会话开始时先跑一遍`；`每次开工或接续，先跑 verify.md 的冒烟集，不通过就先修好`
- **为什么违反：** 这是重复的通用验证轮次；无关的基线失败也会阻止 owner 继续完成不受影响的部分。
- **建议：** 改为：`verify 只列与本次改动风险对应的冒烟和回归要求；owner 在相关改动后运行，不把“每次 session 开始”设为门槛。`

### 13. 一律把界面或日志证据降为辅助证据

- **规则编号：** 一-4
- **位置：** [verify.md:64](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/verify.md:64)、[verifier-brief.md:19](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/references/verifier-brief.md:19)
- **原句：** `只看到界面显示、函数被调用或某行日志出现，只能作辅助证据。`
- **为什么违反：** 当 spec 要求的结果本来就是界面显示或日志输出时，它们是直接证据；该绝对规则会迫使验证者新增无关的内部观测能力。
- **建议：** 改为：`证据应直接对应 spec 要求的可观察结果；只有 spec 同时要求状态变化或副作用时，才需要额外读回该状态。`

### 14. “不汇报进度”是过强边界

- **规则编号：** 一-4
- **位置：** [deliver/SKILL.md:11](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/SKILL.md:11)
- **原句：** `中途不向用户汇报进度，也不问下一步。`
- **为什么违反：** “只在三种情况停下”不等于禁止非阻塞进度更新；该句会压掉宿主要求的长任务状态同步。
- **建议：** 改为：`常规选择不需要停下来询问；可按运行环境要求发送不阻塞工作的简短进度更新。`

### 15. 缺少授权时默认允许 push 和开 MR

- **规则编号：** 一-4、一-5
- **位置：** [deliver/SKILL.md:16](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/SKILL.md:16)
- **原句：** `spec 没写时，可以推送自己的分支并开 MR，但不合入。`
- **为什么违反：** push 和创建 MR 都是外部写操作；缺少目标仓库及授权时擅自执行，也与 core-spec“授权只能由用户决定”冲突。
- **建议：** 改为：`spec 未写交付与授权时，不执行远端写操作；完成本地可做部分后，请用户补定目标仓库、分支及 push、MR/PR、合入授权。`

### 16. 另有两个未列入“停下”章节的停止条件

- **规则编号：** 总原则（用户要求优先）、二-9
- **位置：** [deliver/SKILL.md:53](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/SKILL.md:53)、[deliver/SKILL.md:55](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/SKILL.md:55)
- **原句：** `3 轮之后仍有 FAIL 就停下汇报`；`同一个失败修了 3 次仍不过，停下汇报`
- **为什么违反：** 用户决定 deliver 只在三种情况停下；普通验证或 CI 缺陷即使仍可诊断，也会成为第四、第五种停止条件。
- **建议：** 改为：`同一修复方案三次无效后停止重复该方案，重新诊断并继续；只有问题落入“停下”一节的三类时才交回用户。`

### 17. 跨模型失败后允许同家族替代

- **规则编号：** 二-7
- **位置：** [cross-model.md:46](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/cross-model.md:46)
- **原句：** `改用当前家族的一个新 subagent`
- **为什么违反：** 用户明确要求不同家族；同家族 agent 不能提供规定的独立视角，却可能让流程继续到冻结或交付。
- **建议：** 改为：`另一家模型不可用时，将其作为缺少验证环境报告给调用方；不得用同家族 agent 代替或宣称满足跨模型要求。`

### 18. 验证者被授予绕过沙箱和清理数据的权限，但未交接边界

- **规则编号：** 一-4、一-5、二-3
- **位置：** [cross-model.md:40](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/cross-model.md:40)、[verifier-brief.md:21](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/references/verifier-brief.md:21)
- **原句：** `--dangerously-bypass-approvals-and-sandbox`；`清理测试数据`
- **为什么违反：** 专用 checkout 只能隔离文件，不能隔离外部服务和共享数据；输入中没有允许访问、写入和清理哪些环境的授权。
- **建议：** 增加输入：`允许访问和写入的环境、测试数据范围及清理授权`；并改为：`使用满足验证所需的最小权限；没有明确授权时不得绕过沙箱或清理外部数据，改报环境受阻。`

### 19. `review-rules` 的来源和效力不明确

- **规则编号：** 一-1、二-4
- **位置：** [deliver/SKILL.md:13](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/SKILL.md:13)、[verifier-brief.md:9](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/references/verifier-brief.md:9)、[verifier-brief.md:14](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/references/verifier-brief.md:14)
- **原句：** 输入要求 `review-rules 的路径`，但 deliver 没定义来源；同时又说 `只按 spec 和 verify 判断`
- **为什么违反：** owner 只能猜应传哪个规则；验证者也不知道是忽略 review-rules，还是允许它新增判定要求。
- **建议：** 在 deliver 输入中增加：`仓库指定的 review-rules 路径；没有时明确写“无”`。验证说明改为：`产品行为只按 spec 和 verify 判定；代码质量另按明确提供的 review-rules 判定，review-rules 不得新增产品需求。`

### 20. 独立验证的代码问题和环境型 UNVERIFIED 不进入机械门禁

- **规则编号：** 二-4、二-10
- **位置：** [deliver/SKILL.md:22](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/SKILL.md:22)、[deliver/SKILL.md:29](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/SKILL.md:29)、[verifier-brief.md:33](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/references/verifier-brief.md:33)、[verifier-brief.md:56](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/references/verifier-brief.md:56)
- **原句：** 报告把代码问题放在独立章节；机械检查只检查场景 `没有 FAIL`
- **为什么违反：** 验证者可以发现违反 spec 的代码问题，但所有场景仍为 PASS；环境原因的 UNVERIFIED 也会被现有脚本放行。实际检查脚本确实不解析这两类失败。
- **建议：** 报告增加固定字段 `verdict: PASS|FAIL|UNVERIFIED` 和机器可读的问题状态；规定：`任何正确性代码问题或环境型 UNVERIFIED 都使 verdict 非 PASS，门禁只允许 verify 已声明覆盖盲区导致的 UNVERIFIED。`

### 21. plan 的持续更新只靠 prompt

- **规则编号：** 二-10
- **位置：** [plan-format.md:13](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/references/plan-format.md:13)
- **原句：** `标“持续更新”的四节，每次停下时都要更新`
- **为什么违反：** 这些字段是跨 session 恢复必须依赖的状态，但现有门禁只解析冻结输入，不检查进度、剩余项或阻塞信息。
- **建议：** 改为：`交接或完成前，由 plan 状态工具写入并校验当前 head、已完成项、剩余项和阻塞项；校验失败不得交接。`

### 22. plan 要求复述仓库中可直接获取的上下文

- **规则编号：** 二-11、三-3
- **位置：** [plan-format.md:52](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/references/plan-format.md:52)
- **原句：** `假设读者对仓库一无所知：相关的文件和模块……它们怎样配合`
- **为什么违反：** 新 session 本可从仓库和 git 获取这些事实；强制复述会制造冗长且容易过期的第二份代码库说明。
- **建议：** 改为：`只记录无法从当前仓库和 git 历史直接恢复的任务上下文、非显然约定和当前状态；其余给出文件路径。`

### 23. plan 强制提前规定接口和函数签名

- **规则编号：** 一-1、一-6
- **位置：** [plan-format.md:68](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/references/plan-format.md:68)
- **原句：** `做完时必须存在的类型、接口和函数签名`
- **为什么违反：** spec 未规定时，owner 也必须在计划阶段选定实现方法，后续 session 会把暂定设计当成约束。
- **建议：** 改为：`只记录 spec 已固定的接口，以及实现过程中已经作出、会影响后续工作的依赖决定；未确定的内部签名不写成必须项。`

### 24. 跨模型调用只检查“报告非空”

- **规则编号：** 二-10
- **位置：** [cross-model.md:44](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/cross-model.md:44)、[gap-check.md:27](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/gap-check.md:27)
- **原句：** `报告文件存在且非空。为空或调用出错时重试一次。`
- **为什么违反：** 登录错误、权限错误或只写了一半的报告同样非空，调用方会把它当作已完成查漏。
- **建议：** 改为：`跨模型包装工具校验退出码及报告必需字段；缺字段、含调用错误或格式无效均视为失败，不能进入冻结或交付。`

## 文件问题数

| 文件 | 问题数 |
|---|---:|
| `skills/core-spec/SKILL.md` | 8 |
| `skills/core-spec/references/verify.md` | 6 |
| `skills/core-spec/references/gap-check.md` | 4 |
| `skills/core-spec/references/cross-model.md` | 4 |
| `skills/deliver/SKILL.md` | 8 |
| `skills/deliver/references/plan-format.md` | 3 |
| `skills/deliver/references/verifier-brief.md` | 4 |

最该先改的三条：

1. 删除“缺少授权时默认 push 并开 MR”，防止未经授权的远端写入。
2. 让独立验证的代码问题和环境型 `UNVERIFIED` 真正进入机械门禁。
3. 给查漏方补齐原始需求、ADR 和最终澄清材料，否则它无法发现 spec 本身漏掉或虚构的决定。