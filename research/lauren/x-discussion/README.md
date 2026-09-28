# Lauren Tan / @poteto：X 上的“每月 2,000 PR”讨论

采集时间：2026-09-24。平台：X。公开原帖与评论通过 agent-reach 指定的 OpenCLI X 只读通道获取；X Article 由原帖定位后，通过 Thread Navigator 镜像读取。以下只代表可见材料，并非对 PR 数量、质量或生产结果的独立审计。

## 最重要的结论

1. **“2,000”与“2,500”是不同时间的本人表述。** [8 月 11 日](https://x.com/poteto/status/2087311081433964965)说当月*预计*约 2,000；[8 月 31 日](https://x.com/poteto/status/2094229449126629468)称该月完成 2,000；[9 月 21 日](https://x.com/poteto/status/2102050467505430555)发布视频时称“上个月”交付到生产 2,500。没有在公开材料中找到同一口径的仓库、PR 清单、日期边界、撤回数或质量统计。X 上其他人还转述为 1,000、2,000+、3,000，不能视为原始统计。
2. **她自己反对只看 PR 数。** [pstack 第一篇](https://x.com/i/article/2094151284949688320)说原先认为 PR 和代码行数只是虚荣指标；在质量保持甚至提升时，大规模变更才有意义。她将高信心归因于 Grok Bot 的代码库设计（[8 月 31 日回复](https://x.com/poteto/status/2094229449126629468)），并把自验证能力称为基础设施。
3. **方法是先闭环，再扩并发。** 给 agent 可操控、可观察真实应用的 CLI；让它收集运行结果、截图或性能 trace，自己修到通过；维护 Feature Map；将重复错误转换为代码结构、lint、CI 等机械约束。随后才把独立任务交给云端 agent、协调 bot 和自动化。第一篇提供了验证与并行化的细节；第二篇提供了研究、设计和拆分交付的细节。
4. **她的“规划”偏向可执行证据。** [第二篇](https://x.com/poteto/article/2097732320606507506)中，先让 agent 复述问题，使用 `/how` 追踪运行链、`/why` 查历史原因、`/recall` 取旧对话；用多个可丢弃原型回答设计疑问；设计确定后再写多阶段执行计划，每个 PR 附可验证结果。此处“不相信规划”指不信脱离代码和真实运行的抽象长计划，并非完全不规划。
5. **评论提出的关键问题仍需另行验证。** 例如 [可运行但代码过度复杂](https://x.com/t_swap/status/2102696811899044001)、[由谁审核 2,500 个 PR](https://x.com/HemedNir/status/2103009997932413214)、[CI runner 承载](https://x.com/vaughan_gittel/status/2102862804894322975)、[任务规格来源](https://x.com/erikcvilleg87/status/2102669882579960150)。这些是合理质询，不是已证实的缺陷。

## 本人材料与时间线

| UTC 时间 | 资料 | 可直接支持的内容 |
|---|---|---|
| 2026-08-11 22:51 | [本人帖](https://x.com/poteto/status/2087311081433964965) | “on track” 约 2,000 PR，提及 Grok Bot 和 Cursor。是预测口径。 |
| 2026-08-31 01:03 | [本人回复](https://x.com/poteto/status/2094229449126629468) | 声称该月发 2,000 PR；因专门设计 Grok Bot 代码库而有高信心。 |
| 2026-08-31 16:09 | [pstack 第一篇发布帖](https://x.com/poteto/status/2094457600259842065) → [X Article](https://x.com/i/article/2094151284949688320) | 验证技能、控制 CLI、Feature Map、云端并行、示例工作流。原文镜像见 `raw/pstack-part1-threadnavigator.txt`。 |
| 2026-09-10（镜像时间） | [pstack 第二篇](https://x.com/poteto/article/2097732320606507506) | 高质量上下文、研究、原型、架构、多阶段计划。原文镜像见 `raw/pstack-part2-threadnavigator.txt`。 |
| 2026-09-21 15:01 | [本人视频帖](https://x.com/poteto/status/2102050467505430555) | 称“上个月 2,500 PR 到生产”；视频由她本人发布。 |

## 方法链：对应本人原文

### 1. 让 agent 能够验证实际产品

在[第一篇](https://x.com/i/article/2094151284949688320)中，“验证”是 agent 不等人检查，自己运行真实产品、观察结果、修复并再次检查。她将 `/create-verification-skill` 用作生成项目专属验证能力的入口，主张优先造小型 CLI，而非只加 Markdown 指令。CLI 应能启动、导航、交互、检查、抓截图和性能 trace，提供机器可读结果和清楚的错误提示；危险命令支持 dry run。她强调先把 CLI 做稳定，再考虑更高级的并发。

Feature Map 是可搜索的功能目录：功能是什么、用户如何走到那里、如何用控制 CLI 验证，以及已知陷阱。她把代码库视为更权威的长期记忆，Feature Map 则是为 agent 压缩的共享索引，建议定期维护。

### 2. 把人类判断编进环境

[第一篇](https://x.com/i/article/2094151284949688320)描述她持续整理 Grok Bot 的基础、加 lint 和检查、重构代码库，而不是只追新增功能。[9 月 19 日本人帖](https://x.com/poteto/status/2101384547543978195)又明确赞同可形式化验证的代码库能提高交付速度。这支持“修环境来提高默认产出质量”的方向；具体 Dune 架构、禁止 `useEffect`、评论限制等属于特定项目手段，不应直接复制到别的仓库。

### 3. 让 agent 先理解问题，再用实证选择设计

[第二篇](https://x.com/poteto/article/2097732320606507506)归纳两种常见失败：用户意图没有被充分理解、缺少正确完成工作的上下文。她会让 agent 先用自己的话复述 Slack 报错；用 `/how` 追实际运行链，用 `/why` 查 PR、工单、设计与线上证据，用 `/teach` 给人解释权衡，用 `/recall` 复用旧任务上下文。复杂设计先写使用方式和接口草图，派多个独立候选，交叉评审，再用原型测试；若实现暴露接口问题，可丢弃原设计。执行计划在设计稳定后形成，小 PR 要能各自验证。

### 4. 并行建立在可独立验证之上

[第一篇](https://x.com/i/article/2094151284949688320)推荐云端 agent 获得独立机器、可运行应用并生成视频/截图，协调 bot 保持上下文清洁；也提到用 `/swarm` 多次验证性能或回归结果。她对本地 worktree 的反对主要针对其机器资源、并发上限和云端环境可用性，属于她的运行环境选择，不能推出所有团队都应弃用 worktree。

## X 上的解读与质疑

[@distortgeekin 的《Everyone Is Building Agent Teams. Nobody Is Building The Graph》](https://x.com/i/article/2099113086669979653)是另一条值得单独看的分析：它讨论多 agent 的共享状态、条件路由、退出条件和成本基线。文章没有点名 Lauren，不能据此断言她的实现缺少 graph。原帖链、一手正文和 Anthropic 数据核查见 [`graph-article-notes.md`](graph-article-notes.md)。

| 观点 | 来源 | 证据边界 |
|---|---|---|
| “关键是可信度：无人看守时能给 agent 多大自主权。” | [@neil_xbt](https://x.com/neil_xbt/status/2102053088198611414) | 分析者的概括，与她自验证论述相符。 |
| “验证是基础设施；更多 agent 若没有交接和验证，只会更快制造错误。” | [@biektive](https://x.com/biektive/status/2094865972599378413) | 分析者观点。 |
| “可运行不等于简洁，agent 可能写出两倍不必要代码。” | [@t_swap](https://x.com/t_swap/status/2102696811899044001) | 当事人的经验和提问，未见 Lauren 在采集范围内作答。 |
| “谁审 2,500 个 PR、哪些自动合入？” | [@HemedNir](https://x.com/HemedNir/status/2103009997932413214)、[@paulund](https://x.com/paulund/status/2102668174785450180) | 待回答；不能把“自动验证”误读成所有 PR 无人审批。 |
| “大量 PR 是否源于任务过度切碎？” | [@neilsuperduper](https://x.com/neilsuperduper/status/2102071344741359925)、[@gabrycina](https://x.com/gabrycina/status/2102100943785631757) | 数量可能受 PR 粒度影响；公开材料不足以评价实际效用。 |
| “缺少对验收条件本身的独立确认。” | [@billardbb](https://x.com/billardbb/status/2099483674299232549) | 指向验证与需求确认的区别，值得在复用方法时补上。 |

## 原始与中间文件

- `raw/from-poteto-2000.json`、`raw/from-poteto-2500.json`：X 定向搜索的结构化输出。
- `raw/poteto-recent-40.json`：她的近期时间线。
- `raw/pstack-lauren-2000.json`：主题搜索的结构化输出，含支持与转述。
- `raw/pstack-guide-thread.json`：第一篇发布帖的评论；`raw/2500-video-thread-top30.json`：视频帖按互动排序的 30 条评论。
- `raw/pstack-part1-threadnavigator.txt`、`raw/pstack-part2-threadnavigator.txt`：X Article 可读镜像，仅供核查；原始权威地址仍是上表的 X 链接。
- `raw/distort-graph-article-opencli.json`：通过 X 的 OpenCLI 文章接口取得的 @distortgeekin 原文。

## 采集限制

- OpenCLI 的 X 搜索随后返回 HTTP 429（会话限流）；定向验证与评论读取成功，后续搜索没有绕过限流。Lauren 的两篇 X Article 由 OpenCLI `article` 命令读取时返回 `Article not found`，Jina 对 x.com 返回 403，因此使用 Thread Navigator 镜像。镜像保留作者正文但不是 X 官方接口。@distortgeekin 的文章则由 OpenCLI 成功取得 X 原文。
- PR 数量、合并状态、代码体量、线上故障率、token 与 CI 成本，没有找到可独立复核的明细。第二篇与视频中的“质量”均是本人陈述。引用时应写“Lauren 声称”，并以自己的仓库数据设验收指标。
