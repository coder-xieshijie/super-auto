# Lauren Tan / pstack：站外资料索引

采集日期：2026-09-24。采集方式：按 `agent-reach` 的 Exa 搜索与 Jina Reader 网页阅读路径。`search-*.txt`、`discussion-*.txt`、`claims-check-*.txt` 保存原始搜索结果；其余 `.md` 保存网页原始提取结果。网页提取可能包含导航、评论或付费墙提示，阅读时以原链接复核。

## 一手材料

| 本地原始文件 | 原链接 | 用途 |
| --- | --- | --- |
| `lauren-linkedin-aug12.md` | https://www.linkedin.com/posts/laurenelizabethtan_how-cursor-turned-ai-agents-into-better-engineers-activity-7493165544628703233-ZfM- | Lauren 8 月 12 日使用“shipping 2,000 PRs a month”的表述。 |
| `lauren-linkedin-aug19.md` | https://www.linkedin.com/posts/laurenelizabethtan_cloud-agents-and-cursor-harness-improvements-activity-7495972438262853632-bLQ5 | Lauren 8 月 19 日细化为“上月 1000，本月有望翻倍”；直接解释 pstack、Grok Bot 线索采集、`/goal` `/loop` `/swarm`、云端全天运行。 |
| `paper-ai-review.md` | https://arxiv.org/html/2607.03316v2 | 研究团队对 CodeRabbit 评论及开发者反馈的实证研究，与 Lauren 无直接关系，提供自动 Review 局限的外部数据。 |
| `paper-review-bottleneck-abstract.md` | https://arxiv.org/abs/2607.01904 | 企业 AI 编码推广的纵向研究摘要，与 Lauren 无直接关系。 |

## 二手分析与实操反馈

| 本地原始文件 | 原链接 | 评价 |
| --- | --- | --- |
| `flavio-pstack.md` | https://flaviocopes.com/pstack/ | 最完整的独立上手拆解：路由、playbook、技能、验证、适用范围和成本。文章中的技能数量为发表时快照，会变。 |
| `theneuron-explainer.md` | https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/ | 梳理“先建立信任再并行”、上下文工程、验证成本；引用 Lauren 原帖与 Rob 实操。它转述 8 月 2462 PR，尚需从原帖或仓库记录核验。 |
| `rob-shocks-review.md` | https://moderncreator.app/2026-09-08-rob-shocks-pstack-is-agent-overkill-use-it-anyway | Rob O’Shaughnessy 的上手视频全文稿和摘要。一次技能管理器项目对比：无 pstack 约 30 分钟，完整 pstack 约 1 小时；后者检查出 agent 自述的三处错误。单例体验，不能外推产能比例。原视频 https://www.youtube.com/watch?v=lUhXa8GiXns 。 |
| `xiaohu-chinese.md` / `xiaohu-agent-team.md` | https://best.xiaohu.ai/article/cursor-agent-team-24x7/ | Lauren 工作坊二次解读：600+ 重构 PR、Dune 架构、约 20 个夜间自动合并；网页仅可见部分内容。 |
| `jishuzhan-analysis.md` | https://jishuzhan.net/article/2101331266118012929 | 中文综合分析；有关验证地图腐化、机械约束、人工判断的观点有启发，但若干量化数据未附可核查的论文直链，须分开验证。 |
| `theclarity-pstack.md` | https://theclarity.today/story/pstack-explained-lauren-tan-s-system-for-trustworthy-ai-agents-36efac25 | 对 theneuron 等来源的再整理，属于三手材料；指出调用次数不能证明缺陷率。 |
| `newstack-verification.md` | https://thenewstack.io/agentic-verification-distributed-systems/ | 从分布式系统环境隔离角度指出移植障碍。**Signadot 赞助，作者是 Signadot CEO**；环境方案和“一进程应用”判断带产品立场，不能当作 Lauren 的原意或既定事实。 |

## 排除/注意

- Reddit 定向搜索未发现与 Lauren/pstack/2000 PR 高相关的可靠讨论，搜索快照在 `discussion-*.txt`。未用泛 AI PR 争论冒充相关评论。
- `paper-review-bottleneck.md` 是 Jina 把 arXiv HTML 误提取成一张 SVG 的文本，不作证据；改用同论文摘要文件。
- 技术栈中文文中“87% 架构问题被遗漏”的来源未在已核对的一手论文中找到，**不要复述为已证实统计**。论文确实报告 CodeRabbit 的高层架构、系统上下文理解不足，但不能据此推出 87%。
- 2000 PR 与 2462 PR 目前都是本人或二手媒体的数量陈述；本组资料没有独立的 PR 清单、合并记录或质量审计，不能把数字等同于单人从零编写或每个 PR 都有独立业务价值。

结论见 `findings.md`。
