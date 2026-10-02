# 本轮理论来源与原文核查

采集日期：2026-10-02，Asia/Shanghai。网页使用 Agent Reach 的 Jina Reader；OpenAI ExecPlan 另经官方 documentation MCP 取回正文；GitHub 使用 `gh api`。只保留短摘、哈希、版本和定位，已有全文不重复入库。本文件的英文短摘每个来源累计不超过 25 词。完整元信息见 [manifest.json](manifest.json)。

pstack 复核：当前 `cursor/plugins` main `c47b12849e43f18d5c374c7069c744cc55b0ea00`；相对已有快照多 22 个提交，`pstack/` 零变化，故仍引用固定快照 `ecc249f1e306fc64ddf83c7bed16cacf7c2239db`。Symphony 使用 `be10a1b79df723d6d7612b5651c8522704dafb2e`，原文与已有 A05 存档一致。

## O1

[OpenAI · Using PLANS.md for multi-hour problem solving](https://developers.openai.com/cookbook/articles/codex_exec_plans)。

抓取：`2026-10-02T02:24:50.640314+00:00`；页面未提供稳定 Git 版本，以本轮正文 SHA-256 固定证据：`c132f9f9e024363c42ee798f9f526a1f40ceecf8f8dbeb63c9fa230f77e34d02`。

已有原文：[仓库档案](../../self-verifying-loop-2026-09-28/raw/codex-exec-plans.md)。

> Resolve ambiguities autonomously, and commit frequently.

定位：本轮抓取正文 L33。

支持与边界：自主解决执行歧义、可恢复计划、可观测验收；原文是活计划，不等于本地的冻结 spec。

## O2

[OpenAI · Harness engineering](https://openai.com/index/harness-engineering/)。

抓取：`2026-10-02T02:24:48.277302+00:00`；页面未提供稳定 Git 版本，以本轮正文 SHA-256 固定证据：`5a5d352acbc5f73593e75d0e8e87d01c628ab592c84a3b14088b9d204ce79c04`。

> minimal blocking merge gates

定位：本轮抓取正文 L118。

> one instance per change

定位：本轮抓取正文 L44。

支持与边界：最少阻塞门禁、每 worktree 的运行与观测隔离、仓库知识索引；不是跨项目效果保证。

## O3

[OpenAI · Symphony Specification](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/SPEC.md)。

版本：`be10a1b79df723d6d7612b5651c8522704dafb2e`。

已有原文：[仓库档案](../../agent-delivery-2026-09-28/raw/architecture/A05-symphony-spec.md)。

> Distinct terminal reasons are important because retry logic and logs differ.

定位：本轮抓取正文 L692。

> track deltas relative to last reported totals to avoid double-counting.

定位：本轮抓取正文 L1430。

支持与边界：Failed、TimedOut、Stalled 分型和可恢复调度；Draft 规范不证明 Claude Code 自带这些能力。

## A1

[Anthropic · Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)。

抓取：`2026-10-02T02:24:48.535586+00:00`；页面未提供稳定 Git 版本，以本轮正文 SHA-256 固定证据：`51b6ca378bf011069e86c317eadca483fc8ed890d321d9ede7855682cbb36c4c`。

> compaction isn’t sufficient

定位：本轮抓取正文 L18。

> clear artifacts for the next session

定位：本轮抓取正文 L12。

支持与边界：跨上下文靠进度、git、可运行环境承接；不能从该实验推导固定切 session 的阈值。

## A2

[Anthropic · Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)。

抓取：`2026-10-02T02:24:52.942151+00:00`；页面未提供稳定 Git 版本，以本轮正文 SHA-256 固定证据：`b2dae50b7b186970ebc6eb08d754c9f3132d4c1768460a2442dfe08624718cdb`。

> moved the evaluator to a single pass at the end of the run

定位：本轮抓取正文 L132。

支持与边界：验证方法可先协商，特定模型上取消 sprint、保留最终 evaluator；不是取消所有独立验证。

## A3

[Anthropic · Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler)。

抓取：`2026-10-02T02:24:49.928818+00:00`；页面未提供稳定 Git 版本，以本轮正文 SHA-256 固定证据：`89e1f6b4bceafcdc1fbce6d5315bb55cf16d65a5008d16994590e20caa490da8`。

已有原文：[仓库档案](../../agent-delivery-2026-09-28/raw/architecture/A07-anthropic-compiler.md)。

> The test harness should not print thousands of useless bytes.

定位：本轮抓取正文 L76。

支持与边界：验证器准确性、机器可读摘要、时间盲区、快速抽样；抽样不是按改动路径选场景。

## A4

[Anthropic · Best practices for Claude Code](https://code.claude.com/docs/en/best-practices)。

抓取：`2026-10-02T02:24:50.974778+00:00`；页面未提供稳定 Git 版本，以本轮正文 SHA-256 固定证据：`ab318ac5185f636e24f076c147bbddb2e2006b48888b3e3cf3a02b01a1314cbd`。

> permit specific tools you know are safe

定位：本轮抓取正文 L102。

支持与边界：明确工具授权可减少审批噪声；独立上下文 review、可续接会话；不能泛化为绕过宿主权限。

## A5

[Anthropic · Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)。

抓取：`2026-10-02T02:25:46.661861+00:00`；页面未提供稳定 Git 版本，以本轮正文 SHA-256 固定证据：`703c4a4a391c7fd2234e727e0ec4346ae817d3c594a76d0749f049c7800bce1c`。

> grade what the agent produced, not the path it took.

定位：本轮抓取正文 L253。

> Each trial should be “isolated” by starting from a clean environment.

定位：本轮抓取正文 L247。

支持与边界：结果与 trace 分开、稳定干净环境、检查评分器是否误罚有效结果；不主张任意放宽验收。

## A6

[Anthropic · Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents)。

抓取：`2026-10-02T02:25:44.272358+00:00`；页面未提供稳定 Git 版本，以本轮正文 SHA-256 固定证据：`838840ffc471fbe2b2fa963e75e93ad4e03e34a38c84f61b9046c80979cf7bb2`。

> Because the session log sits outside the harness

定位：本轮抓取正文 L36。

支持与边界：持久 session 与执行器、sandbox 解耦；凭据离开被执行代码环境；不是当前客户端现状说明。

## A7

[Anthropic · Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)。

抓取：`2026-10-02T02:25:44.556112+00:00`；页面未提供稳定 Git 版本，以本轮正文 SHA-256 固定证据：`bc781cda5534786c60f77083f12f3fc3ded56429bde9bd737859dc2415e300e0`。

> smallest

定位：本轮抓取正文 L40。

> high-signal tokens

定位：本轮抓取正文 L40。

支持与边界：高信号最小上下文、索引按需读、持久笔记；不证明本 trace 延迟全部由上下文导致。

## L1

[Lauren · Create a verification skill](https://github.com/cursor/plugins/blob/ecc249f1e306fc64ddf83c7bed16cacf7c2239db/pstack/skills/create-verification-skill/SKILL.md)。

版本：`ecc249f1e306fc64ddf83c7bed16cacf7c2239db`。

已有原文：[仓库档案](../../agent-delivery-2026-09-28/raw/lauren/pstack-source/skills/create-verification-skill/SKILL.md)。

> Never kill by process name; kill what you started.

定位：档案 L31。

> auth valid

定位：档案 L28。

支持与边界：doctor、真实入口、side effects、实例隔离与清理证据保留；没有 token 刷新租约具体实现。

## L2

[Lauren · Orchestrate](https://github.com/cursor/plugins/blob/ecc249f1e306fc64ddf83c7bed16cacf7c2239db/pstack/skills/poteto-mode/playbooks/orchestrate.md)。

版本：`ecc249f1e306fc64ddf83c7bed16cacf7c2239db`。

已有原文：[仓库档案](../../agent-delivery-2026-09-28/raw/lauren/pstack-source/skills/poteto-mode/playbooks/orchestrate.md)。

> Bound your own infra retries the same way you bound a child's.

定位：档案 L100。

> When in doubt, act and log.

定位：档案 L107。

支持与边界：有界基础设施重试、持久交接、pilot、人工问题分类；大项目专用 ceremony 不应照搬单 MR。

## L3

[Lauren · Autopilot-full](https://github.com/cursor/plugins/blob/ecc249f1e306fc64ddf83c7bed16cacf7c2239db/pstack/skills/poteto-mode/playbooks/autopilot-full.md)。

版本：`ecc249f1e306fc64ddf83c7bed16cacf7c2239db`。

已有原文：[仓库档案](../../agent-delivery-2026-09-28/raw/lauren/pstack-source/skills/poteto-mode/playbooks/autopilot-full.md)。

> Count only side effects as progress

定位：档案 L10。

支持与边界：按实际提交/检查/证据变化判进展，保留 operator gate；时间参数为该流程选择。

## L4

[Lauren · Shipping](https://github.com/cursor/plugins/blob/ecc249f1e306fc64ddf83c7bed16cacf7c2239db/pstack/skills/poteto-mode/playbooks/shipping.md)。

版本：`ecc249f1e306fc64ddf83c7bed16cacf7c2239db`。

已有原文：[仓库档案](../../agent-delivery-2026-09-28/raw/lauren/pstack-source/skills/poteto-mode/playbooks/shipping.md)。

> Never use matching commit messages or a green check from an older SHA as a substitute.

定位：档案 L9。

支持与边界：head/base/patch-id 区分 rebase 与补丁改变；代码判定可继承不等于运行环境与 CI 可继承。

## L5

[Lauren · Prove It Works](https://github.com/cursor/plugins/blob/ecc249f1e306fc64ddf83c7bed16cacf7c2239db/pstack/skills/principle-prove-it-works/SKILL.md)。

版本：`ecc249f1e306fc64ddf83c7bed16cacf7c2239db`。

已有原文：[仓库档案](../../agent-delivery-2026-09-28/raw/lauren/pstack-source/skills/principle-prove-it-works/SKILL.md)。

> When verification fails, suspect the observation method before suspecting the system

定位：档案 L16。

支持与边界：先核对真实值和观察器；不是遇到 FAIL 就先认定产品没错。

## L6

[Lauren · Separate Before Serializing Shared State](https://github.com/cursor/plugins/blob/ecc249f1e306fc64ddf83c7bed16cacf7c2239db/pstack/skills/principle-separate-before-serializing-shared-state/SKILL.md)。

版本：`ecc249f1e306fc64ddf83c7bed16cacf7c2239db`。

已有原文：[仓库档案](../../agent-delivery-2026-09-28/raw/lauren/pstack-source/skills/principle-separate-before-serializing-shared-state/SKILL.md)。

> Instructions and conventions are not concurrency control.

定位：档案 L9。

支持与边界：先消除共享，必须共享再用结构性串行；refresh owner/lease 是本地工程推导。

## L7

[Lauren · Poteto-mode](https://github.com/cursor/plugins/blob/ecc249f1e306fc64ddf83c7bed16cacf7c2239db/pstack/skills/poteto-mode/SKILL.md)。

版本：`ecc249f1e306fc64ddf83c7bed16cacf7c2239db`。

已有原文：[仓库档案](../../agent-delivery-2026-09-28/raw/lauren/pstack-source/skills/poteto-mode/SKILL.md)。

> Every claim carries its evidence or its label in the same sentence.

定位：档案 L107。

支持与边界：授权范围内自主决定并报告、不可逆操作仍停；事实/推断/猜测区分。

## L8

[Lauren · Session pickup](https://github.com/cursor/plugins/blob/ecc249f1e306fc64ddf83c7bed16cacf7c2239db/pstack/skills/poteto-mode/playbooks/session-pickup.md)。

版本：`ecc249f1e306fc64ddf83c7bed16cacf7c2239db`。

已有原文：[仓库档案](../../agent-delivery-2026-09-28/raw/lauren/pstack-source/skills/poteto-mode/playbooks/session-pickup.md)。

> Read the prior trail, don't redo it.

定位：档案 L3。

支持与边界：先还原分支/未完成项/决定，再核对继承结论；不把整轮从头重跑当默认恢复。
