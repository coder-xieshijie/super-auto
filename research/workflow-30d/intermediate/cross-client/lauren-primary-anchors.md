# Lauren：与 30 天工作流证据对应的五处一手锚点

本次仅复核已有 research/lauren/analysis.md、两份完整字幕稿及 cue TSV，没有重新抓网。以下均是 Lauren 本人发言，来源为 X 英文字幕；未重新逐字听校，也未核验屏幕展示，故标为本人解释/自述，不标为已独立验证的成效。精确时间来自 cue TSV；Markdown 按 30 秒合段，段标题不等于引文起点。

## L01：让 agent 操作真实应用并取得证据

> run the application itself and take the traces for me

- **00:03:59.410–00:04:02.852，10 个英文词。**
- [原字幕 lauren_2500prs.cues.tsv:93](/Users/minimax/code/github/xieshijie/super-auto/research/lauren/bookmark-videos/transcripts/lauren_2500prs.cues.tsv:93)；[正文 lauren_2500prs.md:38](/Users/minimax/code/github/xieshijie/super-auto/research/lauren/bookmark-videos/transcripts/lauren_2500prs.md:38)。
- **本人回顾：**手工性能分析促使她开发 verification skill。09:00–12:00 又解释稳定 CLI、证据采集、Feature Map 与持续维护。这支持把运行与观察交给 agent，不能单独证明 trace 质量或生产缺陷率。
- **本次工作流映射（分析推论）：**Claude C13 已有真实 SQLite + 假 Turn/Queue 集成测试及 CI；可再挑真实 Goal 用户链验证持久状态、暂停/恢复和可见结果。局部测试通过不等于真实产品验收；复用已有入口。

## L02：先建立单 agent 的可信输出，再扩大并行

> is because you don't have trust in your agent's work yet

- **00:06:24.018–00:06:26.518，11 个英文词。**连续两条 cue。
- [原字幕 lauren_2500prs.cues.tsv:146](/Users/minimax/code/github/xieshijie/super-auto/research/lauren/bookmark-videos/transcripts/lauren_2500prs.cues.tsv:146)，接 L147；[正文 lauren_2500prs.md:58](/Users/minimax/code/github/xieshijie/super-auto/research/lauren/bookmark-videos/transcripts/lauren_2500prs.md:58)。
- **本人方法论判断：**06:15.457–06:36.660 上下文讨论从一到五个 agent 扩到一百个；她认为缺少信任时扩并行会堆积质量差的 PR。这不是公开的单 agent/百 agent 对照实验。
- **本次工作流映射（分析推论）：**Claude C14 用户担忧 CLI 数和重复上下文，C05 细 commit 目的是人工审查。可试连续 owner 保持上下文、多个可审查 commit、一次独立 review，再比较质量、重复读取、token 和返工；细 commit 不必对应更多 agent。

## L03：优先让错误做法无法通过，再叠加提示与技能

> making things categorically impossible through better data structures or algorithms

- **00:18:42.889–00:18:48.771，10 个英文词。**
- [原字幕 lauren_2500prs.cues.tsv:429](/Users/minimax/code/github/xieshijie/super-auto/research/lauren/bookmark-videos/transcripts/lauren_2500prs.cues.tsv:429)；[正文 lauren_2500prs.md:158](/Users/minimax/code/github/xieshijie/super-auto/research/lauren/bookmark-videos/transcripts/lauren_2500prs.md:158)。
- **本人方法论解释：**15:45–18:55 顺序是代码结构/数据结构 → 静态分析（lint、编译诊断、CI）→ rules、Bugbot、skills → 人工 style review。字幕不支持把 rules → skill 理解为严格先后等级：她将 rules、Bugbot、skills 归为较软的引导，可能被忽略。精确上下文：16:28.558–16:38.882 静态分析；16:54.928–17:04.412 lint/结构；17:18.018–17:39.367 软约束；18:49.731–18:55.033 叠加引导。
- **本次工作流映射（分析推论）：**Claude C09 错 target、C12 文档错基线，适合入口核对 repo/target/base SHA；C03/C04/C10 权限语义适合行为测试。重复加长派发说明的可执行性较弱。架构改造仍须对应已出现的问题，不能照搬她项目中的禁注释/useEffect。

## L04：原子 PR 为定位与回滚服务，没有统一行数上限

> each PR to sort of atomically describe what that small piece of thing is doing

- **包含引文的最精确字幕范围：00:39:43.097–00:39:49.118，15 个英文词。**引文从 L1093 内部的 each 起，cue 没有词级起点。
- [原字幕 lauren_graph_harness.cues.tsv:1093](/Users/minimax/code/github/xieshijie/super-auto/research/lauren/bookmark-videos/transcripts/lauren_graph_harness.cues.tsv:1093)，接 L1094；[正文 lauren_graph_harness.md:326](/Users/minimax/code/github/xieshijie/super-auto/research/lauren/bookmark-videos/transcripts/lauren_graph_harness.md:326)。
- **本人偏好/经验自述：**38:30–40:00 先说 PR 从几十行到上千行，没有硬上限，再解释 Git 历史、原子语义、回滚和找 bug 的价值。不能据此把 2000 PR 理解为每个只有几行，也不能把数量当生产率证据。
- **本次工作流映射（分析推论）：**Claude C05 与她一致：用户要求按 commit 理解并 review。保留可审查单元；CLI/worker 粒度按接口耦合和上下文成本另定。是否每个 commit 都拆 MR，需考虑本仓 IDL/集成顺序。

## L05：前期环境投入存在成本，应按 ROI 选择范围

> you spend a lot of money on tokens in the upfront stage

- **00:51:15.523–00:51:19.346，12 个英文词。**连续三条 cue。
- [原字幕 lauren_graph_harness.cues.tsv:1409](/Users/minimax/code/github/xieshijie/super-auto/research/lauren/bookmark-videos/transcripts/lauren_graph_harness.cues.tsv:1409)，接 L1410–1411；[正文 lauren_graph_harness.md:418](/Users/minimax/code/github/xieshijie/super-auto/research/lauren/bookmark-videos/transcripts/lauren_graph_harness.md:418)。
- **本人资源与成本自述：**50:46.606–50:58.076 她说明所在 AI lab 的 token 条件，不能建议所有人完全照做；51:09–51:30 以 ROI 解释前期重构/约束投入。36:30 另有 600 多个重构 PR 的自述，未给独立核验清单。无法推出固定回本期或成本下降比例。
- **本次工作流映射（分析推论）：**先做明确历史返工对应的基线核对、检查入口和一条真实产品验证链，再决定通用能力投入。Claude C14 用户纠正旧 200k 配置后续改 1m，优先级必须绑定当前配置和真实失败。

## 本轮复核的两点校准

1. 代码结构 → lint → 规则 → skill 应表述为：结构/机械检查提供硬约束；规则、Review bot、skills 提供引导。本段没有给 rules 与 skills 的严格总排序。
2. 单 agent 再并行是经验原则；原子 PR 和前期投入是本人偏好/经验。主持人的问题、X 转述和站外分析不是这五条引文的来源。本次未重看视频帧，不能把讲述标成展示效果已验证。
