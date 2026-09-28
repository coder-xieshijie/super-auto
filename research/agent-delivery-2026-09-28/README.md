# AI / agent 工业级需求交付调研（2026-09-28）

## 先读

新增：[用户补充的 Pi / Factory 两视频分析](supplement-videos/analysis.md)，含全片字幕、关键画面核对和 Pi 示例源码审计。

1. [综合结论](conclusions/report.md)：Lauren 遗漏、企业实践、并发、人类瓶颈、与你工作流的具体对应。
2. [两周试验方案](conclusions/experiments.md)：先核实已有能力，再试连续交付、并发和流程删减。
3. [Lauren 遗漏矩阵](intermediate/lauren/findings.md)：pstack 固定源码、两种 autopilot、owner、SHA 验收、持续落地、指令消融。
4. [9 月 27 日新访谈笔记](intermediate/lauren/interview-2026-09-27-notes.md) / [完整英文自动字幕](raw/lauren/interview-2026-09-27/transcript/youtube-browser-export.txt)。

## 证据链

- [来源索引](sources.md) / [总文件哈希](manifest.json) / [验证结果](intermediate/validation.json)。
- [企业案例](intermediate/industry/findings.md)：Stripe、Ramp、Spotify、Shopify、Uber；13 篇原文。
- [架构与编排](intermediate/architecture/findings.md)：Cursor、OpenAI、Anthropic、StrongDM；12 份一手材料。
- [实验与论文](intermediate/evidence/findings.md)：METR、DORA、多 agent、MirrorCode、SWE-Bench Pro、真实 PR 研究，保留版本和样本边界。
- [证据审核](intermediate/review/evidence-review.md) / [架构审核](intermediate/review/delivery-review.md) / [修改收敛](intermediate/review/resolution.md)。
- [范围和方法](REQUEST.md)：检索时间、分工、失败降级、原始资料边界。

## 基线与旧材料

本轮调研前已提交旧成果：`9481ec5481ba8a91a9e31ff5e66b2c0f47fc12c0`，见 [提交凭据](baseline-commit.txt)。

用户工作流依据旧档案 **2026-08-25 17:33 至 2026-09-24 17:33 CST**；未重新扫描后四天会话。原两段收藏视频和逐字稿：[旧视频档案](../lauren/bookmark-videos/README.md)。历史分析：[30 天工作流](../workflow-30d/conclusions/analysis.md)。

本轮产出研究与建议；没有安装 pstack、修改 Agent Lord、执行改造试验或设置自动合并。企业数字属于自报或有特定范围的实验，不能作为通用收益承诺。
