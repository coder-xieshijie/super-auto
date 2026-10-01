---
id: discussion-2026-10-01-skills-consistency-check
recorded_on: 2026-10-01
timezone: Asia/Shanghai
source: 本会话（Claude Code，claude-opus-5-5），用户原话逐字保存；两个子代理（general-purpose）的整理稿存于研究目录
scope: 三家方法综合，对照 agent-prompt-rules 与两家最新写法依据，检查开发流程相关 Skill 的一致性
---

# 开发流程 Skill 一致性检查：三家综合与对照

## 用户问题

2026-10-01，原话：

> 综合以下内容进行汇总分析：
> 1. 当前 3 家的理论、整体开发流程、skill 创建方式以及 prompt 书写规则；
> 2. 之前收集到的 agent for prompt；
> 3. 参考 Anthropic 和 OpenAI 最新的 prompt 书写规则。
>
> 综合汇总之后，再对当前 dev skills 中涉及开发流程相关的 skill 整体 check 一遍。因为现在已经改了很多，需要确认是否有不一致的地方, 是否符合预期。

理解：“3 家”按 2026-09-29 的确认指 OpenAI、Anthropic、Lauren（pstack）；“agent for prompt”按 [2026-09-30 的记录](2026-09-30-goal-final-delivery-trace-review.md)指 dev-skills 的 `agent-prompt-rules`。这是用户在 [MR 7595 复盘](2026-10-01-goal-v2-deliver-trace-review.md) 里说的“我还需要对当前的 skill 再做一轮 check”的那一轮。

## 过程

1. 读本仓库已有的三家材料（零基设计、approaches、两次复盘的 source-check）、流程文档 v0.23、grill 交接模板，以及 dev-skills main `74ae69d` 的全部流程类 Skill、references、脚本和说明文档。
2. 派两个子代理并行整理：一个抓取 Anthropic、OpenAI 截至 10-01 的新内容并与 agent-prompt-rules 逐条对照；一个整理 Lauren / pstack 并核查上游。两份整理稿和抓到的原文都存在研究目录。
3. 跑 deliver 现有的五套用例（191 条）和链接检查；用门禁的解析器读 MR 7595 冻结的 verify；在临时仓库复现 `select-scenarios.mjs` 的漏选；按提交统计 core-spec、deliver 的体量。
4. 想用接口实测 deliver 正文的 token 数，本机 `claude -p` 显示未登录，改为按字数粗估，结论标为未实测。

## 结果

资料：[研究目录](../research/skills-consistency-2026-10-01/README.md)（综合与摘要）、[checks.md](../research/skills-consistency-2026-10-01/checks.md)（检查明细）、[vendor-latest.md](../research/skills-consistency-2026-10-01/vendor-latest.md)、[lauren.md](../research/skills-consistency-2026-10-01/lauren.md)。

助手答复要点：

- 三家在主干上一致：目标加可检查的完成条件，一个 owner 做到底，agent 能自己操作和观察产品，检查交给不是作者的新上下文，规则进代码或钩子，删改指令要对照运行。分歧在写不写原因、写不写验证指令、子 agent 由谁决定、Skill 能否被模型自动调用。
- 两家截至 10-01 没有改写 prompt 的原则，4 个持续更新页的改动都是加新模型。新依据里最有用的是 Anthropic 的 prompt-audit。pstack 上游在 `ecc249f` 之后没有 Lauren 的改动。
- agent-prompt-rules 大体仍成立，建议改 4 处措辞、补 4 条（研究目录第 2 节）。
- 开发流程 Skill：用户的决定都已落地，191 条用例全部通过，两个客户端的手动调用设置一致。发现 16 条，其中：
  - P0：门禁认不出 7595 verify 里的 `S12b`、`S21b`、`S29b` 和 M01–M17，报告少了这 20 项也能过（F1）；独立验证默认 90 分钟到点后按“CLI 用不了”处理，换 CLI 一样会超时（F2，风险，未实测）。
  - P1：里程碑检查两轮后能不能往下做，正文两处说法相反（F3）；“涉及路径写漏只会让重跑变多”不成立（F4，已复现）；grill 的默认决定与 core-spec 的“没反对不等于批准”之间缺一步（F5）；流程文档五处过时（F6）；重新确认的用户原话没有交到 deliver 读得到的地方（F7）。
  - deliver 正文从 #15 到现在长了七成，含限制词的句子从 30 到 50，每次修复都加一段，只有 #23 删过。
- 建议顺序：先上 F1、F2 的机制改动，再修互相矛盾的规则，再整理本仓库的模板和流程文档，然后更新 agent-prompt-rules，最后做减量；用例迁进 dev-skills CI。

## 决定

本轮没有用户决定。待用户决定的五项见[研究目录](../research/skills-consistency-2026-10-01/README.md)第 4 节：F1 的编号方案、F2 的超时、F1 和 F2 是否在给 7595 投递消息前合入、流程文档第二至四节的处理、agent-prompt-rules 是否本轮更新。

本轮没有改 dev-skills，也没有改流程文档和 grill 模板。

## 待验证

- F2：7595 的最终独立验证实际要跑多久，还没有数据。
- F15：deliver 正文的 token 数是粗估，需要用接口实测；Claude Code 压缩后保留前 5,000 tokens 的说法来自官方文档，没有在本机复现。
- vendor-latest.md 记了几处没取到的内容：一篇博客结尾的清单是图片；Codex Best practices 的小标题在转换中丢失；claude.com 博客的文章清单可能不全。
- lauren.md 读过的 pstack PR 正文和两家在线页面只给了 URL，没有存进仓库。
