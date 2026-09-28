# 需求验收环节设计

先读 [完整设计](design.md)。它回答：验证范围、从需求生成步骤、最终产物、修复重验、自动通过条件，以及怎样接入 Agent Lord。

- [示例验收包](examples/README.md)：虚构 Goal 需求的要求/场景/结果结构；DRAFT/NOT_RUN，尚不可执行。
- [独立审查](intermediate/independent-review.md)：设计缺口与当前源码兼容性核查。
- [审查处理](intermediate/resolution.md)。
- [本机源码版本与原文](raw/source-state.json)：当前 Agent Lord `cf06465`，含 #43 worktree 依赖安装。
- [已有研究输入](inputs.json)：本轮使用的本地资料及哈希。
- [本轮用户原文](raw/user-request.md)与[讨论记录](../../discussions/2026-09-28-verification-stage-design.md)。
- [文件完整性与链接验证](intermediate/validation.json)。
- [本目录文件清单与哈希](manifest.json)。

本轮交付设计与示例，不包含 Agent Lord 实现、可运行的业务验收脚本或实际测试结果。下一步应选择真实需求绑定执行工具并完成一次完整试验，再将必要变动收敛到现有 pipeline/receipt。
