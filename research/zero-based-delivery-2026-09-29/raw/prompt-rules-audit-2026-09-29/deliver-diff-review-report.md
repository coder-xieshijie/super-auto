发现 5 项问题，均会影响放行或交付行为。未修改文件。

1. **类型：脚本错误／门禁误放**  
   **位置：** [report-format.mjs:53](/Users/minimax/code/github/xieshijie/dev-skills-deliver-followup/skills/deliver/scripts/report-format.mjs:53)、第 74 行。  
   **问题：** 只检查“代码问题”“冒烟集与回归范围”字样存在，不检查内容。报告写 `verdict: PASS`，但代码问题明确写默认入口未接入，或冒烟结果写 FAIL，门禁仍返回 0。  
   **依据：** verifier-brief 第 39 行要求总体结论与这些结果一致；修订表明确要求堵住代码问题无法拦截的缺口。  
   **建议：** 为代码审查、冒烟与回归增加可解析的结果字段，纳入总体结论一致性检查。

2. **类型：脚本错误／门禁误放**  
   **位置：** [report-format.mjs:46](/Users/minimax/code/github/xieshijie/dev-skills-deliver-followup/skills/deliver/scripts/report-format.mjs:46)、第 78 行。  
   **问题：** 解析时丢弃说明列，仅凭编号属于盲区就允许 UNVERIFIED。例如 S01 只有弹窗检查点属于盲区，报告却写“环境受阻：无登录凭据，整个场景未执行”，门禁仍返回 0。  
   **依据：** verifier-brief 第 37、39 行区分“覆盖盲区”和“环境受阻”；SKILL 完成条件要求环境问题解决后复验。  
   **建议：** 保留并检查 UNVERIFIED 原因；环境受阻始终拦截，盲区豁免限定于已声明的检查点。

3. **类型：脚本错误／R 要求漏检**  
   **位置：** [report-format.mjs:19](/Users/minimax/code/github/xieshijie/dev-skills-deliver-followup/skills/deliver/scripts/report-format.mjs:19)。  
   **问题：** R 编号必须是裸文本，且证明方式通过 `split("|")` 取最后一格。编号写成反引号包裹的 `R01`，或证明命令包含 Markdown 转义管道符，都会使该要求消失。删除对应报告行后，门禁仍返回 0。  
   **依据：** 修订表要求所有机械检查、已有检查对应的 R 编号都有结果；verify 写法未禁止这些合法 Markdown 写法。  
   **建议：** 正确解析表格及转义，规范化编号格式；无法识别要求行时明确报错，避免静默忽略。

4. **类型：脚本错误／盲区识别过宽**  
   **位置：** [report-format.mjs:26](/Users/minimax/code/github/xieshijie/dev-skills-deliver-followup/skills/deliver/scripts/report-format.mjs:26)。  
   **问题：** 将盲区章节中出现的所有编号都当作豁免声明。例如“`S01 已完整覆盖，没有覆盖盲区`”仍把 S01 加入允许 UNVERIFIED 的集合。引用、比较或否定说明也会扩大豁免范围。  
   **依据：** 修订表允许的是明确列出的覆盖盲区，并非章节中提及的所有编号。  
   **建议：** 定义明确的盲区条目格式，只读取声明字段中的编号与检查点。

5. **类型：与修订表不符／交付误拦**  
   **位置：** [SKILL.md:50](/Users/minimax/code/github/xieshijie/dev-skills-deliver-followup/skills/deliver/SKILL.md:50)、[milestone-check.md:16](/Users/minimax/code/github/xieshijie/dev-skills-deliver-followup/skills/deliver/references/milestone-check.md:16)。  
   **问题：** 独立验证入口增加了盲区例外，但里程碑仍要求全部对应场景跑通、没有未解决问题；里程碑检查仍把无法证明的检查点一律记为问题。已接受的盲区仍可能让任务无法走到独立验证。  
   **依据：** 修订表第 123 行明确要求解决“存在盲区时进不了独立验证”；完成条件同步尚不完整。  
   **建议：** 同步里程碑、证据检查及完成条件的盲区例外，同时保留盲区之外的实际验证要求。

已用内存虚拟文件系统执行门禁：6 个应拦截输入返回 0；正常报告及 3 个拒绝对照符合预期。三个脚本语法检查通过，未运行真实跨模型 CLI。

未发现未经修订表授权的规范性规则丢失。四种停下、旧“3 轮／3 次”的替换、里程碑模型继承及跨模型不可用时不自行降级均已核对。