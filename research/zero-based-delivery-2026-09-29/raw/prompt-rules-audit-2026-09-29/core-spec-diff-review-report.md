发现 **5 个问题**。已排除已知的跨模型降级规则冲突；全程未修改文件。

1. **类型：脚本错误／与表格不符**  
   **位置：** [freeze.mjs:48](/Users/minimax/code/github/xieshijie/dev-skills-core-spec-rules/skills/core-spec/scripts/freeze.mjs:48)  
   **问题：** 脚本搜索 verify 全文中的哈希，任意一个匹配就通过，不能保证来源记录正确。来源仍是旧哈希、正文其他位置含当前哈希时，会错误允许冻结。  
   **依据：** 表格要求“核对 verify.md 来源里记的 spec 哈希”，实际判断为 `recorded.includes(specHash)`。已用内存模拟文件读取复现：上述错误输入返回 `0`。  
   **建议：** 明确来源字段，只校验该字段对应的 spec 哈希，其他位置的哈希不参与匹配。

2. **类型：新的矛盾／与表格不符**  
   **位置：** [verify.md:64](/Users/minimax/code/github/xieshijie/dev-skills-core-spec-rules/skills/core-spec/references/verify.md:64)、同文件第 66 行、[gap-check.md:20](/Users/minimax/code/github/xieshijie/dev-skills-core-spec-rules/skills/core-spec/references/gap-check.md:20)  
   **问题：** 新规则允许展示类要求用界面直接证明，但保留的规则仍无条件要求交互效果，会误拒正确的纯展示实现。  
   **依据：** 新增“要求本身是展示时，界面就是直接证据”；后文仍要求“检查点断言交互产生的效果”，查漏仍要求“只有界面没有交互效果……场景都会失败”。  
   **建议：** 将交互效果要求限定于 spec 规定了交互或副作用的场景。

3. **类型：引用／调用输入缺失**  
   **位置：** [cross-model.md:21](/Users/minimax/code/github/xieshijie/dev-skills-core-spec-rules/skills/core-spec/references/cross-model.md:21)、第 25 行  
   **问题：** 两条调用模板没有传入原始约定路径，按模板启动的新 session 缺少执行新增查漏第 6 项的材料。  
   **依据：** 新版查漏说明要求“调用方在命令里给出 spec、verify、原始约定和相关仓库的路径”；模板仍只有“spec：<路径>；verify：<路径>；仓库：<路径>”。  
   **建议：** 两条模板均补充原始约定文件路径。此问题独立于已知的降级规则冲突。

4. **类型：新的矛盾／要求不可执行**  
   **位置：** [gap-check.md:26](/Users/minimax/code/github/xieshijie/dev-skills-core-spec-rules/skills/core-spec/references/gap-check.md:26)、[cross-model.md:25](/Users/minimax/code/github/xieshijie/dev-skills-core-spec-rules/skills/core-spec/references/cross-model.md:25)  
   **问题：** 查漏新增报告两份 SHA256 的要求，但 Claude 调用模板没有允许哈希计算工具，也没有传入两份哈希。  
   **依据：** “报告开头写明你检查的 spec、verify 的 sha256”；工具仅放行 `Read Grep Glob`、`git log`、`git show`、`ls`，并注明“`dontAsk` 拒绝所有未列出的工具”。  
   **建议：** 放行只读哈希计算命令，或由调用方计算并提供对应输入版本的哈希。

5. **类型：规则丢失／新增强约束**  
   **位置：** [verify.md:110](/Users/minimax/code/github/xieshijie/dev-skills-core-spec-rules/skills/core-spec/references/verify.md:110)  
   **问题：** 默认同目录变成了无例外的同目录要求，删除了用户单独指定 verify 路径的安排，表格未说明取消这一例外。  
   **依据：** 原句：“默认交付一个 `verify.md`，与 spec 放在同一目录，或使用用户指定路径。”现为：“交付一个 `verify.md`，与 spec 放在同一目录。”表格要求“目录用用户本次指定的”。  
   **建议：** 恢复用户指定路径优先，同目录作为未单独指定 verify 路径时的安排。

检查覆盖了未提交 diff、新增脚本、第四节表格及指定的全部参考文件和 README 部分。步骤编号、第 1–4／5／7 步引用、查漏第 6 项编号，以及检查范围内的相对链接和锚点，未发现其他问题。