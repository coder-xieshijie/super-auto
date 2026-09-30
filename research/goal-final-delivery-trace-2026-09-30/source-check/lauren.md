---
source: 子代理核对（general-purpose，claude-opus-5-5），2026-09-30；只读 pstack 源码快照、PR 419/422 与访谈字幕，引文由子代理用 grep -F 核对
scope: Lauren / pstack 对 24 条建议的态度
---

下面是 24 条的逐条结论。英文引文都用 `grep -F` 在原文件里逐字核对过；访谈字幕是自动生成的，跨行引文是把相邻几行拼起来的。我没有改任何文件。

**路径简写**
- `ps/` = `/Users/minimax/code/github/xieshijie/super-auto/research/agent-delivery-2026-09-28/raw/lauren/pstack-source/`
- `raw/` = 同级的 `.../raw/lauren/`，PR 引文取自 `pr419.json`、`pr422.json` 的 body 字段。

**先说 A 组的背景。** Lauren 自己不写 spec，只给目标和能跑的检查：
- "i don't believe in planning. the best spec is code."（`ps/README.md:241`）
- "Now the agent has three checks it can run, not a mood to satisfy."（`ps/docs/guide/06-verify-and-ship.md:15`）

## 逐条结论

**A1 支持。** pstack 的做法是 agent 先把框架写出来给人看，而不是让人逐题回答。
- "A good handoff has the goal, the finish condition, permissions, and an escape hatch. It doesn't need to be long"（`ps/docs/guide/07-overnight.md:9`）
- "Quantify scope: units, rough effort, expected stacks, and the wall-clock budget."（`ps/skills/poteto-mode/playbooks/orchestrate.md:60`）

**A2 支持。** 注意 pstack 的“默认决定”用在执行期、有完全授权的情况下，不在定义期。
- "Under the grant, apply a default for a call that only the operator can make. Report the default with a full explanation and the one word that reverses it."（`ps/skills/poteto-mode/SKILL.md:20`）
- "Name who the work is for (an end user, a colleague importing the library) and what changes for them before any implementation detail."（同文件 :105）

**A3 前半支持，后半只有部分依据。** “等子任务回来再问”最接近的做法是先用原型把问题定下来，再写计划。
- "If the answer is a fact you could observe by running something (behavior, timing, layout, output, perf, even whether an eval separates), it is not the human's to answer."（`ps/skills/poteto-mode/SKILL.md:20`）
- "Every claim carries its evidence or its label in the same sentence." / "Never hand the human a check you could run."（同文件 :107）
- "Settle open questions by prototype before you write."（`ps/skills/poteto-mode/playbooks/multi-phase-plan.md:6`）

**A4 支持，而且 Lauren 用脚本强制。** `check-plan.mjs:145-146` 会报错 "names no screenshot" 和 "has no pass predicate"。
- "One box is one unit of work. Every box names the evidence that checks it."（`multi-phase-plan.md:24`）
- "A surface with no control skill is a risk in Appendix C, and its live block still names how each lane drives it."（同文件 :15）

**A5 支持，而且更严。** 用户可见的行为必须有在真实界面上跑的验证（live 验证），不是“列出来让用户接受”。ledger 会把每一项的验证等级显式记下来。
- "Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked"；"The live block is mandatory."（`multi-phase-plan.md:13`）
- "Unit tests show branch behavior, not bug absence."（`playbooks/bug-fix.md:10`）
- "Behavioral work needs better than `type-check-only`."（`orchestrate.md:89`）

**A6 支持。**
- "SCOPE        paths this unit may write; paths it may not; its exclusive worktree or branch"（`orchestrate.md:40`）
- "Hold the file boundaries. <PR id or class> touches only `<glob>`."（`multi-phase-plan.md:52`）
- "…the do-not-touch fences in one artifact. Keep it outside the delegates' write scope so they can't quietly edit the contract."（`ps/skills/principle-build-the-lever/SKILL.md:17`）

**B1 支持，计划格式由脚本检查。**
- "The plan is a checklist an owner runs box by box and the operator audits from the evidence."（`multi-phase-plan.md:3`）
- "Check a box only when its evidence exists, a file, a log line, a screenshot, a test run, or a SHA."（:24）
- 第 10 行要求跑 `check-plan.mjs`，并且 "fix every line it prints"。

**B2 支持，但和另一条原则有张力。** B2 让场景跑通保持同步、只把审查放到后台，两边都能兼容。
- 支持："The sampled brief audit runs alongside the wave it samples and stops the next refill on failure, not the current one."（`orchestrate.md:63`）
- 支持："Self-proof, CI, and babysit then run in parallel with the swarm."（`autopilot-full.md:6`）
- 张力："…each ending in a state you can check, and don't advance until the current one is green."（`ps/skills/principle-sequence-verifiable-units/SKILL.md:9`）

**B3 支持。** 按 SHA 记录结论、由工具核对这部分有依据。“报告必须早于下一里程碑第一个提交”这个时间顺序条件没有涉及。
- "A new head SHA voids the row, so re-verify after restack. The ledger answers "was this verified", not memory and not the transcript."（`orchestrate.md:89`）
- "Drop a result that does not record the SHAs and method its brief names, and rerun that worker once."（`ps/skills/swarm/SKILL.md:40`）

**B4 支持放宽。**
- "Call-mechanics instructions in skill prose do not change agent behavior; the subagent tool schema (model optional, omitted inherits the parent) governs."（`raw/upstream-history.json`，#167 的提交信息）
- "When the Task tool rejects a configured slug, the skill runs that role on its default and says so."（`raw/pr422.json`）
- "Do not block the review on the slug issue."（`ps/skills/interrogate/SKILL.md:49`）

**B5 部分支持，部分相反。**
- 支持的部分：用事件脚本等待，到终态就退出。`watch-pr` 有 `--timeout "deadline; 0 disables it"`（`scripts/watch-pr/cli.ts:119`），超时退出码是 5（`types.ts:333`），但默认不开超时。
  - "Watcher output drives wakeups. Never add a second sleep loop."（`babysit.md:12`）
- 相反的部分：Lauren 保留定时心跳作兜底，而且明确说不能只靠完成通知。
  - "…gets a watcher subagent that wakes you on the event, with a long time-based heartbeat as fallback."（`autonomous-run.md:6`）
  - "A local root arms each tick as a real terminal `/loop`. The loop uses a monitored-shell 30-minute sleep and emits an output-notification sentinel." 和 "Never leave the cadence to memory or lossy completion notifications."（`autopilot-full.md:10`）
- 访谈里提到唤醒太频繁的代价："if you have them run too often it can be quite expensive on your usage because it just keeps you know waking up the agent"（访谈 [21:09–21:16]）

**B6 部分支持。** 只在状态有新变化时发，预计时长写进文件。“进入长等待时说一句”这个时机没有直接涉及。
- "…post a short status message to the operator in chat only when the audit found a tracked change that no earlier status message reported"；"Do not repeat a table, the merged list, or an unchanged blocker."（`multi-phase-plan.md:43`）
- "…expected runtime (at least the longest past run of that kind), and state to a `children.tsv`…"（`autopilot-full.md:6`）

**B7 原则上支持，但 pstack 没有比对改动路径的脚本。**
- "Structural mechanisms (lint rules, metadata flags, runtime checks, automation scripts) enforce the rule without cooperation."（`principle-encode-lessons-in-structure/SKILL.md:11`）
- "Run them on the committed head. A hook pass is not proof."（`autopilot-full.md:6`）

**B8 支持，有一个细节不同。** Lauren 是先手工跑第一个单元，再写脚本，然后用脚本重跑这个单元和手工结果对比。
- "Do the first unit by hand to learn the recipe, then build the tool. Prove it by rerunning it on that unit and diffing against your hand-done version."（`principle-build-the-lever/SKILL.md:14`）
- "The strongest proof is a deterministic script that re-runs the same comparison, not a one-time eyeball."（`principle-prove-it-works/SKILL.md:20`）

**B9 支持。** 清理是用脚本审计，不是在需求结束时照一张固定清单删。
- "Work from a git worktree off main."（`opening-a-pr.md:5`）
- "It reads paths from `git worktree list`, never hand-typed"（`worktree-cleanup.md:5`）
- "`wip` and in-use pause."（同文件 :8）

**C1 支持超时，对心跳有一个提示。** 心跳只能说明进程还活着，不代表有进展；Lauren 只把副作用算作进展。
- "TIMEBOX      rough cap on runtime; on expiry, return partial findings and stop rather than run on"（`orchestrate.md:45`）
- "Count only side effects as progress… Treat a lane that errors, or that passes its expected runtime without a side effect, as stuck. Stand it down and dispatch a replacement at once."（`autopilot-full.md:10`）
- "Transcript mtime is not liveness."（`orchestrate.md:95`）

**C2 支持。**
- "process up, right version/build, port owned by us, auth valid. An agent runs this first whenever anything looks off."（`create-verification-skill/SKILL.md:28`）
- "Report capabilities before the repro starts."（`automations/benny/.../control-adapter.md:131`）
- "Never write a real slug you have not confirmed is available."（`setup-pstack/SKILL.md:14`）

**C3 部分涉及。** 按验证需要选择运行环境，推理强度写在模型名里。Codex 沙箱开关本身没有涉及。
- "Always `environment: "cloud"` unless the task needs this machine: `control-ui` or `control-cli` runtime verification…"（`orchestrate.md:17`）
- "…set the effort token of every real slug… to `xhigh`, `high`, or `medium`."（`setup-pstack/SKILL.md:29`）

**C4 部分相反。** 沿用旧结论只有一个机械条件：patch-id 不变，或者差异只在测试、文档、lint 配置，并且经构建比对确认只是噪声。只要补丁变了就整轮重验，不靠推理去挑“受影响场景”。复验时读上一轮报告这一点是支持的。
- "If only noise differs, that lane's result stays valid…"；"Re-verify anything else when the patch changed."（`shipping.md:9`）
- "The new head gets a fresh swarm and a fresh verdict, except for lane results that stay valid under the patch-id rule…"；"Add that defect to the next round's review brief."（`autopilot-full.md:8`）

**C5 支持。**
- "A worker may self-report. A verifier overrides it on the same key."（`orchestrate.md:89`）
- "A unit is not done until its output is externalized the moment it lands…"（`orchestrate.md:91`）

**D1 部分支持。** 串行驱动一个实例，或者每个实例各自隔离，都有依据。对“共享登录加刷新锁”，Lauren 的原则是先消除共享；确实需要锁时，用能按 PID 自动清理的锁（`orchestrate.md:101`）。
- "can two instances run side by side (ports, data dirs, profiles)? If not… refusing to double-drive a shared instance beats corrupting the user's session."（`create-verification-skill/SKILL.md:19`）
- "Treat "we need a lock" as a design smell to check, not as the default answer."（`principle-separate-before-serializing-shared-state/SKILL.md:16`）

**D2 支持。**
- "Fix it in its own PR and keep the task moving. A skill edit that ships tangled into feature work is invisible to review and impossible to evaluate."（`docs/guide/09-make-it-yours.md:65`）
- "Only edit the verification skill's own directory"（`maintain-verification-skill/SKILL.md:21`）

**D3 支持，有边界。** 注入的只能是前置状态，要验证的展示结果必须在真实入口上观察。
- "Arrange a state through safe fixture data, permissions, flags, service responses, or supported test controls."（`control-adapter.md:62`）
- "Arranging a precondition is not permission to inject the reported symptom."（同文件 :68）

**D4 方向支持。** “按生产装配驱动的夹具”本身没有涉及。
- "A test calls the code the way its users do and asserts the result they observe against a literal expected value."（`principle-test-behavior-not-implementation/SKILL.md:9`）
- "Prefer no new test over a bad test."（`tdd/SKILL.md:26`）

**D5 支持。**
- "Mid-run discoveries fix only what blocks the frontier. Everything else parks in follow-ups."（`orchestrate.md:109`）
- "**Close the loop.** Don't just record. Apply now or create a concrete todo."（`principle-encode-lessons-in-structure/SKILL.md:26`）

**E1 支持。** U+FFFD 这个字符本身没有涉及，但有同类实例：`check-plan.mjs:58` 用 `if (/[\u2013\u2014]/.test(prose)) fail(n, "long dash");` 机械拦截长破折号。另外钩子通过不算证据，还要在已提交的 head 上检查（B7 已引）。
- "**Corollary:** If the fix is structural, only use the structural fix. The instruction is the symptom."（`principle-encode-lessons-in-structure/SKILL.md:21`）

**E2 部分相反。**
- 支持的部分：流程改进另开 PR（D2 已引 guide/09:65）；经验在任务刚结束后提炼，"Right after a task that taught you something, run:"（`guide/09:23`，这里 run 的是 `/reflect`）。
- 相反的部分：发现坏 skill 要立即单独修，不能冻结到需求结束；长程运行每个周期都从 trunk 重读最新流程。
  - "Broken skill mid-task → fix it in its own PR. Don't block. Don't silently work around it."（`poteto-mode/SKILL.md:34`）
  - "At each tick, re-read this playbook from trunk with `git show origin/main:…`"（`autopilot-full.md:10`）

**E3 部分支持。** 截图和日志不入库、按 SHA 记录，这两点支持。“文本证据默认提交”比 Lauren 重，她默认不提交。
- "Keep captures, recordings, logs, and tokens out of source control."（`benny/.../reproduce-and-fix-issues/SKILL.md:30`）
- "By default the log is a working artifact, not committed."（`show-me-your-work/SKILL.md:46`）

**E4 部分支持。** 耗时、人工、返工这组固定指标没有涉及。
- "Leave the store intact. It is the postmortem."（`orchestrate.md:66`）
- "Numbers from the tables, not narrative."（:111）
- "One weird session is an anecdote, not a rule."（`guide/09:29`）

## PR 419、422 与“prompt 写多少”

**PR 419：只删做过对照实验的规则。**
- 方法："Most repeat a rule that stays in the same skill or in the mode skill. Each cut held up in A/B runs on tasks that exercise it, with and without the text."
- 固定数量上限会适得其反："The 3-5 cap made reviewers pad a session that held one real learning. Without it, padding over 12 runs fell from 34 items to 14, and recall on a session with eight learnings rose from 47 to 75 of 96."
- 被删的包括 "Always run final verification before declaring done"、"Reserve questions for genuine ambiguity"、"Supervision is async"，以及每个步骤里重复的 "Review its diff yourself"。
- 同时有三条边界：
  - "Delegation stays mandatory."
  - 没测过的不删："The perf-issue playbook keeps its "Review the diff." line, because no A/B task exercised it."
  - 删了有代价："Noise rose by 0.83 findings per review on Opus 5.5…"
  - 结论只覆盖 Opus 5.5 作为主导模型的情况："no other lead model ran."

**PR 422：规则冲突让 agent 只能猜。**
- "Three pstack rules contradicted other rules in the same skills, so an agent had to guess which rule wins."
- 修法是点名例外角色，例如 "A standalone babysit keeps the full ban."，并把检查写进 `check-plan.mjs`。
- "Not tested in a live agent run."

**另一边：Lauren 仍然会写 prose 的情形。**
- "Skill prose is for things mechanisms cannot enforce."（`reflect/references/synthesizer.md:20`）
- "If no (requires judgment), make the instruction more prominent and add an example of the failure mode"（`principle-encode-lessons-in-structure/SKILL.md:17`）
- "Every spawn and every resume carries the standing orders verbatim." 和 "Directives decay across resumes, and each dropped one costs a human turn."（`orchestrate.md:10, :25`）

**我的推断（没有原文逐条对应）：**
- A2、A3 里“推荐明确就别问”“先查事实”这类通用行为，和被删的 "Reserve questions for genuine ambiguity" 是同一类。值得写的只是本项目特有的格式，比如成批默认加反转词、附 file:line。
- 以下几条和现有规则之间，存在 PR 422 那类冲突风险，需要点名例外：
  - B2 与“不绿不前进”
  - E2 与“坏 skill 立即修”
  - B5 与原有唤醒规则

## 清单没有覆盖、但相关的 pstack 做法

1. **把流程步骤原样抄进 todo 列表，跳过的步骤也留着并写理由。** 可对应 owner 漏做里程碑检查的问题。
   - "Open a todolist whose first items are the matched playbook's steps, copied in verbatim… A step you choose not to do stays in the list with a one-line `skip: <reason>`."（`poteto-mode/SKILL.md:117`）
2. **按失败类型重试；连续工具失败就停下，并写好交接。** 可对应验证跑 2 小时无结果的问题。
   - "Retry by mode: cap-hit or oom, respawn with smaller scope… Two retries, then abandon the unit and replan around it."（`orchestrate.md:97`）
   - "After a few consecutive tool aborts, stop retrying. Write a terminal handoff to durable state…"（:100）
3. **先用一个单元把全流程走一遍（pilot）。** Codex 沙箱起不来 Electron 这类环境问题会在这一步暴露。
   - "Push one unit through the whole path… The pilot exists to falsify the brief template, the verify recipe, and the unit size while that costs one agent instead of fifty."（`orchestrate.md:62`）
4. **流程改动先盲测对照，再推广。** 可以直接用来决定这 24 条的去留。
   - "A skill edit affects every future session, so test it like the experiment it is:"（`guide/09:55`）
   - "The candidate prompt looks like an organic user request. State the goal, not the meta."（`eval.md:8`）
5. **决策日志对照 transcript 审计，再由另一家模型审阅。**
   - "Check that each row's evidence resolves and shows what the row claims."（`show-me-your-work/SKILL.md:60`）
   - "Before handing back, spawn a subagent on a different model family from the one that did the work. Self-review is not a substitute."（:67）