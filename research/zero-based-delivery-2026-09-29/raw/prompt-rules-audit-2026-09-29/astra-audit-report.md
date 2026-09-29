已按 `main` 当前内容完成只读审查，未修改文件。共发现 **17 项问题**；跨文件同因合并计项。以下不质疑 brief 中明确保留的用户决定。

**1. 查漏交接缺少原始约定，无法发现两份文件共同遗漏的需求**

规则：一-3、二-3。

位置：[core-spec/SKILL.md:142](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/SKILL.md:142)、[gap-check.md:3](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/gap-check.md:3)、[cross-model.md:21](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/cross-model.md:21)。

原句：“它只拿到 spec、verify 和相关仓库”“只按文件本身和仓库判断。”

影响：如果作者同时从 spec 和 verify 漏掉一条已确认要求，两份文件依然自洽，查漏方没有依据发现遗漏。隔离作者的讨论过程，不等于隔离原始需求证据。

建议改写，并同步调用参数：

> 查漏方接收 spec、verify、相关仓库，以及原始需求、已接受 ADR 和用户最终确认记录的路径与适用范围；不传作者的草稿推理和自评结论。检查两份文件是否忠实承接原始约定，以及相互覆盖是否完整。

**2. 独立验证交接遗漏“实现后绑定命令”**

规则：一-3、二-3、二-11。

位置：[verifier-brief.md:3](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/references/verifier-brief.md:3)。

原句：输入仅列出“项目验证能力的位置”等六项；第 14 行又规定“plan.md 里的说法都不能作为依据”。

影响：实际命令按 deliver 第 49 行写在 plan 中，冻结的 verify 只保留占位。验证者没有收到这部分执行输入，容易重复定位命令，或把已经可执行的场景报告为 UNVERIFIED。

建议在输入中增加：

> 提供按场景 ID 对应的实际驱动命令、启动配置和必要前提，可引用 plan.md 的“验证与验收”一节；这些内容仅作执行入口，判定标准仍取自 spec 和 verify。

**3. 定义 session → owner 没有传递用户确认版本的指纹**

规则：一-3、二-11。

位置：[deliver/SKILL.md:15](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/SKILL.md:15)、[第 45 行](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/SKILL.md:45)。

原句：“spec.md、verify.md：用户给出的路径”“开工时把……sha256……记进 plan.md”。

影响：core-spec 输出了确认用的哈希，但 owner 只接收路径并重新计算。确认后、开工前被改动的文件会成为新的冻结基线，后续检查仍能通过。

建议改写：

> 输入包括 spec、verify 的路径、用户确认时的 sha256 和确认记录。开工时由工具核对当前文件与确认版本一致，plan 记录确认版本的哈希。

**4. 代码审查问题没有进入明确的失败判定**

规则：一-2、二-4。

位置：[verifier-brief.md:20](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/references/verifier-brief.md:20)、[第 53 行](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/references/verifier-brief.md:53)；[deliver/SKILL.md:22](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/SKILL.md:22)。

原句：“代码问题”写在场景表之后；交付条件是“独立验证没有 FAIL”，机械检查要求“每个场景都在报告里，而且没有 FAIL”。

影响：违反非目标、硬约束等问题可能没有对应的失败场景。验证者把问题写在正文，场景表全为 PASS，owner 及现有脚本仍可能判定可交付。只读检查脚本也确认它仅解析场景结果，没有解析代码问题。

建议改写报告与完成条件，并同步脚本：

> 报告分别给出场景结果、代码审查结果和总体结果。存在任何未解决的正确性问题或既定要求违例，总体结果为 FAIL；交付门禁同时检查总体结果与场景覆盖。

**5. 作者被要求执行独立的自查和修正后再查**

规则：一-2、二-5、三-5。

位置：[core-spec/SKILL.md:97](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/SKILL.md:97)、[第 116 行](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/SKILL.md:116)；[verify.md:108](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/verify.md:108)。

原句：“对照原始约定检查 spec”“修正后重查受影响条款、相邻边界和摘要的一致性”“交付前对照 spec 核对”。

影响：除了写作和独立查漏，又增加作者的完整检查轮次；第 4 步大部分内容还重复了前面的写作要求。即使产物已满足要求，模型也会额外执行这些轮次。

建议删除单独的作者检查步骤，把必要内容保留为结果标准：

> spec 忠实承接已确认约定；verify 覆盖 spec 的规范性要求，不新增要求。实质遗漏、冲突和判定歧义由独立查漏报告处理。

仅产出 spec 时也用这些结果标准，不另设作者自审轮次。

**6. 无变化也强制重复运行，超出了逐里程碑验证要求**

规则：一-2、一-6、二-5、三-5。

位置：[deliver/SKILL.md:45](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/SKILL.md:45)、[第 47 行](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/SKILL.md:47)；[verify.md:100](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/verify.md:100)。

原句：“每次开工或接续，先跑……冒烟集”“全部里程碑完成后，自己把全部场景和回归范围跑一遍”“冒烟集：2–5 条”。

影响：session 接续但代码、环境都没变化，也必须重跑；里程碑已有有效证据，仍要追加一次作者全量验证。固定数量还可能人为增补或压缩冒烟范围。

建议合并到 deliver 一处：

> 每个里程碑在应用中跑通涉及的场景。最终交付保留适用于交付版本的验证证据；代码、环境或前提变化使证据失效时，重跑受影响部分。冒烟范围由项目风险决定。

**7. 强制先建设通用验证能力，把实现方法变成交付前置条件**

规则：一-1、一-5、一-6、二-9。

位置：[verify.md:84](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/verify.md:84)、[deliver/SKILL.md:47](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/SKILL.md:47)、[plan-format.md:56](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/references/plan-format.md:56)。

原句：“缺口补成项目可复用的验证能力”“验证工具缺口排在最前面”“失败先修，再进入下一个里程碑”。

影响：本可借助现有工具取得证据的需求，会被扩展成验证基础设施建设；某项能力受阻时，与之无关的里程碑也被串行阻塞。用户要求应用内运行，并未要求先建设通用工具。

建议合并改写：

> 列明取得验收证据所缺的能力及其影响范围。owner 决定复用、补充方式和实施顺序；只阻塞依赖该能力的场景与工作。

**8. 一概把界面结果降为辅助证据，会误判纯展示要求**

规则：一-2、一-4、二-4。

位置：[verify.md:64](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/verify.md:64)、[第 113 行](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/verify.md:113)；[verifier-brief.md:19](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/references/verifier-brief.md:19)。

原句：“只看到界面显示、函数被调用或某行日志出现，只能作辅助证据”“没有只检查界面或内部调用的检查点”。

影响：若 spec 要求显示某段文本、错误提示或视觉状态，界面就是被验收的结果。该规则会迫使作者增加内部查询，或让验证者拒绝本来充分的证据。

建议改写：

> 证据直接对应 spec 要求的可观察结果。展示要求可用界面证据；涉及持久化、外部调用或其他副作用时，应取得相应结果，不能仅凭界面提示推断。

**9. 每个场景强制编写错误实现，与前文按风险补充的要求冲突**

规则：一-6、三-5、三-6。

位置：[verify.md:68](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/verify.md:68)、[第 76 行](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/verify.md:76)。

原句：“基线……覆盖不到的关键风险，再写一个……错误实现”；随后要求“每个场景都有……错误实现”。

影响：后一个完成条件覆盖了前面的条件判断，模型会给简单场景也机械补一个错误实现，增加文档和推演工作。

建议删除每场景必填要求，合并为：

> 检查点应能区分符合与违反 spec 的结果；存在不明显的误通过风险时，补充一个能说明该风险的错误实现。

**10. 缺少“非目标”章节就提问，把形式缺项当成用户决策缺口**

规则：一-4、二-4、二-9。

位置：[core-spec/SKILL.md:61](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/SKILL.md:61)；[gap-check.md:17](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/gap-check.md:17)、[第 35 行](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/gap-check.md:35)。

原句：“非目标和授权……讨论中没有定下时，作为最小必要问题提出”“缺项：没有目的或非目标”“属于 spec 的问题，写成要用户决定的问题”。

影响：即使已确认范围足以指导交付，也会因为没有单列非目标而提问；能够从原始确认记录恢复的遗漏，也被统一转成新的用户决定。

建议改写：

> 只在缺失信息会造成不同的合理交付范围或验收结论，且现有确认记录不能解决时向用户提问；已有依据的遗漏由作者补齐。

**11. 强制内部台账和通用写作指导，增加了非必要步骤**

规则：总原则、一-1、一-6、三-3。

位置：[core-spec/SKILL.md:28](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/SKILL.md:28)、[第 86 行](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/SKILL.md:86)。

原句：“先在工作过程中建立……议题 → 最终约定 → 依据 → 确认状态 → 成稿位置”“短句适合职责与范围；表格适合条件与行为对照”。

影响：模型必须先维护一个不交付的中间结构；通用写作知识又成为额外指令。这里需要约束的是决定有依据、文档可读，不是内部整理方式。

建议删除通用写作句，将台账要求改为：

> 规范性决定应能定位到已确认依据；存在冲突或替代关系时，在相关决定旁保留必要来源。

**12. plan 强制记录过多实现细节，扩大接续文档的负担**

规则：一-1、一-6、三-3。

位置：[plan-format.md:44](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/references/plan-format.md:44)、[第 52 行](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/references/plan-format.md:52)、[第 68 行](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/references/plan-format.md:68)。

原句：“每个自主决定和每次改变做法”“假设读者对仓库一无所知”“必须存在的类型、接口和函数签名”。

影响：小改动也需要补仓库入门说明、逐项记录普通实现选择、提前维护函数签名，plan 容易演变成与代码同步维护的技术方案。

建议改写：

> plan 保留冻结输入、进度、剩余工作、验证入口，以及影响后续接续的重要决定。仓库知识和接口定义引用现有文件；其余章节按任务需要添加。

**13. 必须发生的机械动作仍由 prompt 调度，没有执行保证**

规则：二-10、三-4。

位置：[core-spec/SKILL.md:156](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/SKILL.md:156)、[cross-model.md:44](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/cross-model.md:44)、[verifier-brief.md:18](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/references/verifier-brief.md:18)、[deliver/SKILL.md:23](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/SKILL.md:23)。

原句：“计算……sha256，确认……一致”“报告文件存在且非空”“HEAD 等于给定……并且工作树干净”“取 MR……实际 head，运行”。

影响：这些都是确定性的交接门禁，但仍要求模型记住执行。已有 `check-delivery.mjs` 实现了部分检查，**其必然被调用、调用前后的目录核验、报告非空和冻结前哈希一致性**仍没有工具强制。

建议把这些动作移入调用封装或交付门禁，正文改为：

> 运行时负责冻结输入校验、验证目录前后状态、报告有效性和交付版本一致性；检查失败时返回具体失败项，agent 处理原因。

仅改写这句话不算完成修复，需要配套执行入口。

**14. 自动降级到同家族模型，违背明确保留的跨模型要求**

规则：二-7，以及规范总原则中的用户要求优先。

位置：[cross-model.md:46](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/cross-model.md:46)。

原句：“对方 CLI 不可用……改用当前家族的一个新 subagent”。

影响：虽然报告会注明不满足要求，pipeline 仍自动执行替代方案，并可能把它当作已经完成独立验证。披露偏差不能替代用户指定的模型家族条件。

建议改写：

> 首选 CLI 不可用时，使用其他可用工具调用不同家族模型；没有可用能力时，记录该验证环节受阻，继续不受影响的工作。同家族检查不能满足跨模型完成条件。

**15. 路径默认值与“目录每次由用户指定”的决定冲突**

规则：一-3，以及规范总原则中的用户要求优先。

位置：[core-spec/SKILL.md:95](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/SKILL.md:95)、[verify.md:118](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/references/verify.md:118)。

原句：“未指定时沿用当前项目文档惯例”“与 spec 放在同一目录，或使用用户指定路径”。

影响：执行端可以自行选择需求文档目录，与 brief 明确给出的决定不一致。

建议只在入口保留一次：

> 需求文档目录由用户每次指定；未提供时先取得目录。spec.md 与 verify.md 写入该目录。

references 引用该约定，删除另一套默认值。

**16. 两个 description 都塞入了执行流程，并与正文重复**

规则：三-1、三-5。

位置：[core-spec/SKILL.md:4](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/SKILL.md:4)、[deliver/SKILL.md:4](/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/SKILL.md:4)。

原句分别包含：“另一家模型在新 session 中查漏后，请用户一次确认，两份一起冻结”；“由一个 owner session 连续完成实现、逐里程碑在应用里验证、另一家模型的独立验证、MR/PR 与 CI”。

影响：流程要求提前进入技能索引上下文，并在正文再次出现；这些内容不帮助判断何时使用技能。问题不是单纯字数多，而是 description 承担了执行指令。

建议分别改为：

> 在需求讨论结束后，将已确认约定整理为 spec.md 和验收要求 verify.md；也支持只生成 spec.md。

> 按已确认冻结的 spec.md 和 verify.md 完成交付，适用于“按 spec 交付”“做到 MR/PR 可合入”。

**17. core-spec 的条件分支流程没有充分下沉到 references**

规则：三-2。

位置：[core-spec/SKILL.md:19](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/SKILL.md:19)、[第 126 行](/Users/minimax/code/github/xieshijie/dev-skills/skills/core-spec/SKILL.md:126)。

原句：“只要 spec……做完第 1–4 步即交付”，但正文仍完整载入第 5–8 步的验收生成、查漏处置、轮数及冻结流程。

影响：只生成 spec 的调用也载入不适用的流程；已有 spec 的调用同样载入完整的收敛和写作流程。references 已承担部分细节，但入口还保留了仅分支需要的执行规则。

建议将分支细节下沉，正文保留路由句：

> 只生成 spec 时使用 spec 写作说明；需要 verify 时读取验收生成与查漏说明；用户确认与冻结规则随对应产物流程读取。

移走原段，避免复制一份到 references 后两处并存。

各文件问题数如下；同一项涉及多个文件时分别计入，因此文件计数之和大于 17。

| 文件 | 问题数 | 对应编号 |
|---|---:|---|
| `core-spec/SKILL.md` | 8 | 1、5、10、11、13、15、16、17 |
| `core-spec/references/verify.md` | 6 | 5、6、7、8、9、15 |
| `core-spec/references/gap-check.md` | 2 | 1、10 |
| `core-spec/references/cross-model.md` | 3 | 1、13、14 |
| `deliver/SKILL.md` | 6 | 3、4、6、7、13、16 |
| `deliver/references/plan-format.md` | 2 | 7、12 |
| `deliver/references/verifier-brief.md` | 4 | 2、4、8、13 |

最该先改的三条是：**第 4 条**，防止代码问题被场景 PASS 掩盖而放行；**第 1 条**，让独立查漏能够发现共同遗漏；**第 2 条**，让独立验证者拿到实际可执行的场景入口。