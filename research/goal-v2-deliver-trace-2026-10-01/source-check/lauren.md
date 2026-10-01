---
source: 子代理核对（general-purpose），2026-10-01；只读 pstack 源码快照与 PR 存档，引文用 grep -F 核对
scope: Lauren（pstack）原文对 MR 7595（Goal v2 迁移与 11 项反馈修复）交付复盘归纳出的 16 条流程优化方向（O1–O16）的态度；另列 pstack 有、16 条未覆盖、与长时间无人值守交付、人工介入、验收口径相关的做法 5 条
---

# Lauren（pstack）原文核对：16 条流程优化方向

## 核对方法

- 路径简写：`ps/` = `/Users/minimax/code/github/xieshijie/super-auto/research/agent-delivery-2026-09-28/raw/lauren/pstack-source/`；`raw/` = 同级的 `.../raw/lauren/`。
- 每段英文引文都用 `grep -Fn` 在所标文件里逐字找到，行号取 grep 输出。Markdown 粗体标记（`**`）会打断匹配，所以引文只取标记之间的连续文字。
- `raw/pr419.json`、`raw/pr422.json` 是单行 JSON，引文在 `body` 字段里，另用 Python 确认过在 body 中。访谈字幕是自动生成的，每行一条字幕，跨行引文分行核对，行号写成区间。
- "另见"后面只给位置、不加引号或只引短语的地方，也逐个用 `grep -F` 核对过。
- 上一轮核对（`research/goal-final-delivery-trace-2026-09-30/source-check/lauren.md`）只当线索，本文引文全部重新核对。
- 背景：Lauren 不写 spec，"i don't believe in planning. the best spec is code."（`ps/README.md:241`）。pstack 里没有"冻结 spec/verify"和"另一会话投递流程更新"这两个环节，对应做法要从 autopilot-full、autopilot-stack、orchestrate、multi-phase-plan 这几份长程 playbook 里找。pstack 的规则大多写在 skill 正文里，用脚本强制的只有几处：`check-plan.mjs`（计划格式）、`orch`（状态表、验证账本、待人决定的 gate）、`log.sh`（决策日志）、`watch-pr`（PR 状态）、`worktree-audit.sh`（清理）。下文逐条注明是脚本强制还是正文要求。

## 态度一览

| 编号 | 态度 | 要点 |
| --- | --- | --- |
| O1 | 部分支持；"绑定开工时的版本"一点相反 | 不用中断、只投递阻塞性修复、在边界上拉取，都有依据；但 Lauren 每个 tick 从主干重读最新版 |
| O2 | 支持 | `orch gate park` 不给默认答案就报错 |
| O3 | 部分支持 | 单独改口径、记录会签、同类问题一次查全有依据；没有"冻结"环节，且对放宽口径更严 |
| O4 | 支持 | pilot、启用前的试跑检查、亲眼核对测试模式实际行为 |
| O5 | 支持 | 清理只清自己启动的东西，实例互相隔离，提前给出权限 |
| O6 | 支持 | 按改动路径跑仓库规定的检查，开工 15 分钟内推送并开 PR |
| O7 | 部分支持 | 审查与场景同一轮并行有依据；但补丁一变整轮重跑，并行省不掉第二轮 |
| O8 | 支持 | 时间戳由脚本写，进度页由表格生成 |
| O9 | 支持 | 实现必须委派，PR 419 删减指令时保留了这一条 |
| O10 | 部分支持；"无变化也报状态"一点相反 | 预计时长写进文件；聊天里只报新变化 |
| O11 | 支持 | 先讲影响再给标识符，另有 `/bro` 兜底 |
| O12 | 支持 | 能观测到的事实不问人 |
| O13 | 支持 | 默认决定带理由和一个词的推翻方式，要人决定的事汇总一次给出 |
| O14 | 部分支持；"定期真做 rebase"一点相反 | 用 `git merge-tree` 试合并、点名排查主干新增调用者；真实 rebase 只在固定时点做 |
| O15 | 支持 | 截图、录屏、日志不进仓库，大迁移可提交文本记录 |
| O16 | 支持 | 门禁报错写明"实际是什么、应该是什么"，机制能管的不写进正文 |

没有"相反"或"未涉及"的整条；相反的部分在 O1、O10、O14 的分项里。

## 逐条结论

### O1 流程更新不打断在途交付

**态度：部分支持。** "不用中断投递""只投递阻塞本次交付的修复""在边界上自己拉取"都有依据。"在途会话绑定开工时的流程版本"与 Lauren 的做法相反。

- "Completions are queue events, not interrupts."（`ps/skills/poteto-mode/playbooks/orchestrate.md:9`）
  子代理完成后只进队列，协调者在固定的 drain 点统一处理，不打断手上的事。这是 playbook 正文规则，没有脚本强制。
- "Answer a user question mid-loop and continue. Only an explicit stop ends the loop before the active forge's stop condition."（`ps/skills/poteto-mode/playbooks/babysit.md:20`）
  只有明确的停止指令才结束循环，其他插话一律答完继续。按这条，owner 不应把一次中断理解为用户拒绝。pstack 里"停止"有固定含义：操作者的 hold 会变成"零写入"命令，owner 持有任务直到被放行（`ps/skills/poteto-mode/playbooks/autopilot-full.md:11`）。
- "At each tick, re-read this playbook from trunk with `git show origin/main:pstack/skills/poteto-mode/playbooks/autopilot-full.md`, then re-read the armed `/goal`."（`ps/skills/poteto-mode/playbooks/autopilot-full.md:10`）
  root 大约每 30 分钟一次审计 tick，每次从主干重读最新 playbook，并在这次 tick 里修正偏差。这支持"在边界上拉取"，但拉的是主干最新版，不是开工时的版本。计划骨架同样要求 "Re-read them at every tick."（`ps/skills/poteto-mode/playbooks/multi-phase-plan.md:36`），而且 `check-plan.mjs` 会检查计划里出现 `git show origin/main:`（`ps/skills/poteto-mode/scripts/check-plan.mjs:20`），这一点是脚本强制的。

另见：途中发现的问题只修阻塞前沿的，其余记为后续（`ps/skills/poteto-mode/playbooks/orchestrate.md:109`）；坏掉的 skill 另开 PR 修，不阻塞任务（`ps/skills/poteto-mode/SKILL.md:34`）；不要用 resume 去探一个 agent 是否还活着（`ps/skills/poteto-mode/playbooks/orchestrate.md:95`）。

与建议的出入：Lauren 敢让在途运行每个 tick 读最新版，前提是 skill 改动先单独开 PR、做过对照实验才进主干。PR 419 的说法是 "Each cut held up in A/B runs on tasks that exercise it, with and without the text."（`raw/pr419.json` body），guide 也要求 "A skill edit affects every future session, so test it like the experiment it is"（`ps/docs/guide/09-make-it-yours.md:55`）。我们这次流程改动没有经过这道检验。采纳 O1 时要说明取舍：要么绑定版本，要么像 Lauren 一样让改动先过检验再让在途会话读到。

### O2 等人的问题不无限挂起

**态度：支持。** pstack 用脚本强制每个待人决定的问题都带默认答案。

- "When in doubt, act and log."（`ps/skills/poteto-mode/playbooks/orchestrate.md:107`）
  同一行列出不该找人的事，包括 restack 操作、重试、CI flake 判定，以及 "should I keep going"。执行顺序这类问题属于这一类。
- "Park each as a `gates.md` entry before asking, and route work around it."（`ps/skills/poteto-mode/playbooks/orchestrate.md:105`）
  真要人决定的事先记进 `gates.md`，然后绕开它继续做别的，不原地等。`gates.md` 每项写"问题、选项、无人回答时的默认"（`ps/skills/poteto-mode/playbooks/orchestrate.md:30`）。
- `.requiredOption("--default <answer>", "default answer")`（`ps/skills/poteto-mode/scripts/orch/orch.ts:439`）
  `orch gate park` 不给默认答案就报错。"每个问题都写明默认做法"由脚本强制，不靠正文提醒。

另见：仍然要等人的只有操作者点名的 gate 和 Autonomy 里的"Always pause"清单（`ps/skills/poteto-mode/SKILL.md:20`、`:83`）。无人值守时的等待策略在 Benny 里做成配置：等 triage 结论有时间预算（`ps/automations/benny/templates/configuration.example.yaml:72`，`verdict_wait_minutes: 45`），超时就静默停止（`ps/automations/benny/skills/reproduce-and-fix-issues/SKILL.md:76`）。

与建议的出入：Lauren 列的"要找人"的情况与我们的"四种停下"不完全相同。她的清单是不可逆操作、实验无法决定的产品或偏好问题、与现实冲突的常设指令、重新规划后仍走不通的死路（`ps/skills/poteto-mode/playbooks/orchestrate.md:105`）。

### O3 交付中修改 verify 的成本

**态度：部分支持。** "改动单独做""记录是谁确认的""同一类问题一次列全"有依据。pstack 没有"冻结 spec/verify"这一环，也就没有重新冻结脚本；它对放宽验收口径比 O3 更严。

- "If the gate itself is wrong, fix the gate in its own change rather than routing around it."（`ps/skills/figure-it-out/SKILL.md:42`）
  验收口径本身错了，就单独改它，不绕过。支持把重新冻结做成独立、可审查的一步。
- "The owner records it in the form that the tool's approval contract allows, with a pointer to the root's countersign. A lane checks the record against that countersign."（`ps/skills/poteto-mode/playbooks/autopilot-full.md:10`）
  同一行前文规定：放宽一个已固定的门槛值，要在验证者给出证明之后由 root 重新会签。会签要记录，并由验证 lane 核对记录，对应"记录是谁确认的"。这是正文规则，没有脚本。
- "Check for the pattern, not just the instance (grep for the same pattern, fix all instances)"（`ps/skills/principle-fix-root-causes/SKILL.md:18`）
  发现一处口径冲突，先把同类位置查全再一起处理。对行为问题，autopilot-full 也要求 "ask for a red test that covers every site with the same defect."（`ps/skills/poteto-mode/playbooks/autopilot-full.md:8`）。

另见：常设指令与观察到的现实冲突，属于要报给人的事（`ps/skills/poteto-mode/playbooks/orchestrate.md:105`，"a standing order that contradicts observed reality"）；验证者与工作者用不同模型家族（`ps/skills/poteto-mode/playbooks/orchestrate.md:17`），对应"改动部分仍由另一家模型查漏"；重复操作做成工具（`ps/skills/principle-build-the-lever/SKILL.md:8`），对应"重新冻结做成脚本"。

与建议的出入：Lauren 反复强调不能为了交差放宽验收条件，"never relax the predicate to declare victory"（`ps/skills/poteto-mode/playbooks/autonomous-run.md:11`）。她放宽门槛要先有验证者的证明，再会签。O3 只讲降低重新冻结的成本，没有讲"改口径前先证明原口径确实错了"。建议补上这一条。

### O4 冻结前核实验证可行性

**态度：支持。** pstack 在三处要求先试跑一次再放量。

- "The pilot exists to falsify the brief template, the verify recipe, and the unit size while that costs one agent instead of fifty."（`ps/skills/poteto-mode/playbooks/orchestrate.md:62`）
  铺开之前先让一个单元走完全流程，专门用来证伪验证方法。对应"冻结前试跑"。
- "Before enabling the repro automation, run one harmless adapter check:"（`ps/automations/benny/skills/reproduce-and-fix-issues/references/control-adapter.md:157`）
  其后九步（启动、确认应用标记、驱动、检查状态、截图、录屏、清理）全部成功才允许启用。同文件还要求 "Report capabilities before the repro starts."（`:131`）。对应"测试台能否覆盖测试账号"这类外部能力的事先确认。
- "When the safe path is a dry-run or test mode, verify what it actually skips by observing (files, network, git refs) rather than trusting its name"（`ps/skills/create-verification-skill/SKILL.md:30`）
  测试模式实际做了什么要亲眼观察，不按名字推断。对应"没核实观测源在中断、失败、辅助请求下记什么"。

另见：写计划前先用原型解决开放问题（`ps/skills/poteto-mode/playbooks/multi-phase-plan.md:6`）；验证失败时先怀疑观测方法（`ps/skills/principle-prove-it-works/SKILL.md:16`）；用一个真实状态值交叉核对 UI 上看到的结果（`ps/automations/benny/skills/reproduce-and-fix-issues/SKILL.md:179`）；到不了的功能只有写明具体前置条件（认证、权限、系统、外部状态）和尝试过的路径，才能标 `verified-unreachable`（`ps/skills/maintain-verification-skill/SKILL.md:33`）。

与建议的出入：pstack 的 pilot 在执行开始、铺开之前，不在"冻结前"，因为它没有冻结环节。放到我们的流程里，对应位置就是冻结前。

### O5 验证环境不需要人

**态度：支持。**

- "how to tear down instances the run created. Never kill by process name; kill what you started."（`ps/skills/create-verification-skill/SKILL.md:31`）
  清理是验证 skill 必备的一节，只清本次启动的东西。同文件要求附带的脚本可执行、调用方式写进 skill 正文（`:32`）。对应"清理做成验证工具的命令"。
- "can two instances run side by side (ports, data dirs, profiles)? If not, say so in the generated skill: refusing to double-drive a shared instance beats corrupting the user's session."（`ps/skills/create-verification-skill/SKILL.md:19`）
  并行实例要分开端口、数据目录、profile；做不到就拒绝共用一个实例。Doctor 检查里包含 "auth valid"（`:28`）。对应"每个实例独立登录态"和多实例共享登录导致 401 的问题。
- "\"don't ask me before committing\" pre-answers the permission the agent would otherwise block on."（`ps/docs/guide/07-overnight.md:23`）
  无人值守前，把运行中会卡住的权限提前给出。对应"审批不应让无人值守的运行挂起"。

另见：删除路径从 `git worktree list` 读出，不手写（`ps/skills/poteto-mode/playbooks/worktree-cleanup.md:5`，由 `worktree-audit.sh` 实现）；每条 live lane 在自己的云端 VM 上跑（`ps/skills/poteto-mode/playbooks/multi-phase-plan.md:72`）；并发的执行者各写各的状态目录（`ps/skills/principle-separate-before-serializing-shared-state/SKILL.md:15`）。

与建议的出入：pstack 规定删除数据要停下等人（`ps/skills/poteto-mode/SKILL.md:83`）。所以提前授权只能覆盖验证工具自己创建的临时数据，清理命令要能证明它只删自己创建的东西。这正是 "kill what you started" 的要求，也是子代理手写含变量的 `rm -rf` 会触发审批的原因。

### O6 质量命令按 CI 选

**态度：支持。**

- "Before a push that starts a round, run the pre-review checks that the repo's AGENTS.md files and rules name for the touched paths. Run them on the committed head. A hook pass is not proof."（`ps/skills/poteto-mode/playbooks/autopilot-full.md:6`）
  检查集按改动路径、由仓库自己的 AGENTS.md 和规则决定，不由 owner 自选，并在已提交的 head 上跑。
- "Open the PR before self-proof so the URL, decisions, and checks form a durable trail."（`ps/skills/poteto-mode/playbooks/autopilot-full.md:6`）
  同一行要求 owner 开工约 15 分钟内推第一个分支快照，并直接开非草稿 PR。对应"尽早推送、读合并结果流水线"。
- "CI green is an input to a verdict, not a verdict."（`ps/skills/poteto-mode/playbooks/orchestrate.md:89`）
  CI 只是结论的输入之一。root 的验证轮里还有一条 lane 在该 SHA 上重跑门禁（`ps/skills/poteto-mode/playbooks/autopilot-full.md:8`，"The lanes: re-run the gates at that SHA."）。

另见：推送前跑一次仓库的 lint 和 typecheck（`ps/skills/poteto-mode/playbooks/multi-phase-plan.md:59`）；CI 失败在 diff 没碰过的代码里，说明基线过旧，先查再重试（`ps/skills/poteto-mode/playbooks/babysit.md:21`）。

与建议的出入：pstack 没有"本地检查集与 CI 自动对齐"的脚本，靠仓库的规则文件按路径写明。O6 若做成脚本，比 pstack 更强。

### O7 里程碑检查的代码审查与场景运行并行

**态度：部分支持。** 审查与场景同一轮并行有依据。但按 pstack 的规则，审查找出代码问题后场景仍要整轮重跑，并行省不掉第二轮。

- "Two or more audit lanes, each with its own focus, that read the diff and the receipts and distrust the PR body."（`ps/skills/poteto-mode/playbooks/multi-phase-plan.md:66`）
  同一行先列了一条 gates lane、十条 live 场景 lane、一条 perf lane。代码审查 lane 和场景 lane 在同一轮里一起扇出、并行跑。
- "When the lanes return, send every proven finding against the PR to the owner in one fix-forward."（`ps/skills/poteto-mode/playbooks/autopilot-full.md:8`）
  所有 lane 的问题合成一次退回给 owner，只改一轮。
- "Re-verify anything else when the patch changed."（`ps/skills/poteto-mode/playbooks/shipping.md:9`）
  补丁一变，除非差异只在测试、文档、lint 配置且构建比对确认是噪声，之前的 lane 结果都作废、要重跑。

与建议的出入：照这套规则，审查若发现代码问题，修完后场景还要再跑一轮。并行只省掉"等审查"的时间，那 71 分钟的第二轮场景省不掉。Lauren 减少返工的办法是把自查放在报告 code-ready 之前：deslop 和 no-comments 做完才报 head，"When the shipped code is final, after the slop-strip and `/no-comments`, it reports the code-ready head SHA."（`ps/skills/poteto-mode/playbooks/autopilot-full.md:6`）。若目标是省掉第二轮，应把代码审查放到场景之前，而不只是并行。另外 "don't advance until the current one is green."（`ps/skills/principle-sequence-verifiable-units/SKILL.md:9`）管的是单元之间的先后，不反对同一单元内的检查并行。

### O8 计划里的时间要可核对

**态度：支持。** pstack 的做法更进一步：时间戳由脚本写，不让 agent 手填。

- `ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"`（`ps/skills/show-me-your-work/scripts/log.sh:25`）
  决策日志的时间由 `log.sh` 自动盖章，正文写作 "It stamps `ts`"（`ps/skills/show-me-your-work/SKILL.md:38`）。`orch` 写验证账本和 inbox 时同样用 `new Date().toISOString()`（`ps/skills/poteto-mode/scripts/orch/store.ts:1344`、`:1384`）。
- "`status.md` is derived from `units.tsv` and `ledger.tsv` at each drain, never hand-maintained."（`ps/skills/poteto-mode/playbooks/orchestrate.md:32`）
  进度页从表格生成，不手写叙述。
- "Every claim carries its evidence or its label in the same sentence."（`ps/skills/poteto-mode/SKILL.md:107`）
  同一行接着要求标明 "Measured, inferred, or guess"。估计值必须写成估计。

另见：收尾前对照 transcript 核对日志每一行的证据（`ps/skills/show-me-your-work/SKILL.md:60`）；"Numbers from the tables, not narrative."（`ps/skills/poteto-mode/playbooks/orchestrate.md:111`）。

与建议的出入：O8 是"写了再用脚本核对"，pstack 是"时间直接由脚本写"。后者能从源头去掉估计值，可以一并考虑。

### O9 主会话做协调、大块实现交给子代理

**态度：支持。**

- "Delegate implementation. Stay in the lead."（`ps/skills/poteto-mode/playbooks/feature.md:3`）
  同文件规定委派是强制的，"Mandatory: no skip-with-reason escape"（`:12`）。PR 419 删减 19 条指令时特意保留："Delegation stays mandatory."（`raw/pr419.json` body）。
- "Code-coupled work (one feature, one migration) goes to a single owner with the checkpoint inline. That owner fans out internally after the blocking phase."（`ps/skills/poteto-mode/playbooks/feature.md:19`）
  一次迁移交给一个 owner，这和我们的做法一致；但 owner 在阻塞阶段之后要向下派子代理，不自己写全部代码。
- 访谈里 Lauren 说她给工程 lead bot 定的职责是 "break down tasks into smaller pieces and" / "delegate and uh supervise other bots" / "rather than do work on its own."（`raw/interview-2026-09-27/transcript/youtube-browser-export.txt:684-686`，自动字幕）
  她自己的 bot 也按"主管只拆分、派活、监督"来设置。

另见：大段输出、截图、长文档交给子代理，主上下文只留摘要（`ps/skills/principle-guard-the-context-window/SKILL.md:14`）；上下文即将压缩时走 Pause safely（`ps/skills/poteto-mode/SKILL.md:140`）。

与建议的出入：orchestrate 对"一个 agent 在预算内能做完"的工作说 "do the work directly in this session, plain workers where they help"（`ps/skills/poteto-mode/playbooks/orchestrate.md:60`）。意思是不必搭 orchestrate 那套机制，不是让主会话亲手写全部代码；Feature playbook 的强制委派仍然适用。

### O10 长时间等待时给出状态和预计时间

**态度：部分支持。** "记录预计时间"有依据。"没有新变化时也主动报状态"与 pstack 的做法相反。

- "As soon as a subagent starts, the owner adds its ID, expected runtime (at least the longest past run of that kind), and state to a `children.tsv` kept the same way."（`ps/skills/poteto-mode/playbooks/autopilot-full.md:6`）
  每个子代理启动时就记下预计时长，取同类任务以往最长的一次。预计时间写进文件，root 用它判断是否卡住。
- "post a short status message to the operator in chat only when the audit found a tracked change that no earlier status message reported"（`ps/skills/poteto-mode/playbooks/multi-phase-plan.md:43`）
  只在出现新的可追踪变化时发聊天消息。同一行列出的变化里包括 "a stuck agent and the action taken"。
- "If the audit found none, end the turn with no reply text."（`ps/skills/poteto-mode/playbooks/multi-phase-plan.md:43`）
  没有变化就不发，但每次 tick 都要在决策日志里记一行（同行 "Either way, log this tick's row in your decision trail."）。

另见：每次 drain 结束输出 `orch status` 的三行，即各状态计数、变化、未决 gate（`ps/skills/poteto-mode/playbooks/orchestrate.md:75`）；Benny 等待时保持静默（`ps/automations/benny/skills/reproduce-and-fix-issues/SKILL.md:58`），只发一条实质结论、不播报进度（`ps/automations/benny/skills/triage-issue-reports/SKILL.md:20`）。

与建议的出入：Lauren 默认人是异步查看的，状态放在文件和日志里，聊天里只报变化。我们的情况是用户在线等了 21 分钟。按 pstack 的思路，可以在进入长等待时把预计时长写进可查的状态文件并告知一次，超过预计时长时把"卡住及处理"作为一次变化报出；不必定时发"仍在等"。这是推论，原文没有针对"用户在线等待"的条款。

### O11 给用户的问题写得通俗

**态度：支持。**

- "Restate your last message. Stop using jargon and speak coherently. State it more simply and concisely, like one human talking to another."（`ps/skills/bro/SKILL.md:7`）
  pstack 专门有 `/bro`，就是"用大白话再说一遍"。guide 说它用于 "Use it when a reply is technically thorough and you still don't know what it said."（`ps/docs/guide/10-recipes-and-pitfalls.md:79`）。它是用户手动调用的补救，不是默认行为。
- "Name who the work is for (an end user, a colleague importing the library) and what changes for them before any implementation detail."（`ps/skills/poteto-mode/SKILL.md:105`）
  先说对谁有什么影响，再说实现细节。对应"问题不以内部编号和术语开头"。
- "Don't invent jargon. Use the words a developer would say out loud"（`ps/skills/technical-writing/SKILL.md:19`）
  不自造术语。unslop 另有一条反对缩写和符号式压缩（`ps/skills/unslop/SKILL.md:67`）。

与建议的出入：technical-writing 同时要求 "The codebase is the word list. Write the real symbol, file, flag, or command name, not a synonym or a description of it."（`ps/skills/technical-writing/SKILL.md:17`）。Lauren 并不排斥编号和标识符，她要求先讲影响、再给真实标识符。O11 落地时可以按这个顺序写，不必删掉编号。

### O12 定义阶段先查事实再提问

**态度：支持。**

- "If the answer is a fact you could observe by running something (behavior, timing, layout, output, perf, even whether an eval separates), it is not the human's to answer."（`ps/skills/poteto-mode/SKILL.md:20`）
  能靠运行或读代码得到的事实，不拿去问人。
- "Answer these from the codebase and only ask the user what you cannot observe:"（`ps/skills/create-verification-skill/SKILL.md:13`）
  先从代码库回答，只问看不到的部分。
- "Never hand the human a check you could run."（`ps/skills/poteto-mode/SKILL.md:107`）
  自己能跑的检查不交给人。

另见：Benny triage 先用线程里已有的证据，再向报告人追问（`ps/automations/benny/skills/triage-issue-reports/SKILL.md:67`）；multi-phase-plan 先原型、再派子代理探索、再写计划（`ps/skills/poteto-mode/playbooks/multi-phase-plan.md:6`、`:7`）；interrogate 只在意图不清时问用户（`ps/skills/interrogate/SKILL.md:32`）。

与建议的出入：pstack 没有明文写"等代码核对子任务返回后再发问"，这是上面几条的直接推论。PR 419 删掉了 never-block-on-the-human 里的 "Reserve questions" 一条（`raw/pr419.json` body，"The \"Reserve questions\" bullet in never-block-on-the-human."），理由是 Opus 5.5 不写也会照做。所以把 O12 写成泛泛的"先查后问"，按 Lauren 的实验可能是多余文字。值得写的是本流程特有的时序，例如"代码核对子任务没返回前不发第一轮问题"，最好做成可检查的步骤。

### O13 默认决定成批列出

**态度：支持。**

- "Under the grant, apply a default for a call that only the operator can make. Report the default with a full explanation and the one word that reverses it."（`ps/skills/poteto-mode/SKILL.md:20`）
  默认决定要写清理由，并给出一个词就能推翻的方式。
- "Reaches the human, batched into the status page rather than per item"（`ps/skills/poteto-mode/playbooks/orchestrate.md:105`）
  要人决定的事汇总到状态页一次给出，不逐条打断。
- "Present the framing once. Reversible prep proceeds without waiting."（`ps/skills/poteto-mode/playbooks/orchestrate.md:60`）
  框架只讲一次，可逆的准备工作不等回复。

另见：每个 gate 带默认答案（`ps/skills/poteto-mode/playbooks/orchestrate.md:30`，由 `orch.ts:439` 强制）；"A recommendation is a judgment, not a validation."（`ps/skills/poteto-mode/SKILL.md:87`）。

与建议的出入：pstack 的默认决定用在执行期、已有完全授权的场景，它没有 grill 这种定义期问答。约 45 个问题里 36 个直接采纳推荐，按 Lauren 的分类，这些多半是"可逆、按默认继续、事后报告"的问题，只有产品或偏好问题需要人逐个回答。

### O14 最后一次 rebase 的风险前移

**态度：部分支持。** "提前发现基线漂移和主干新增的调用者"有依据。"定期真的 rebase 到最新基线"与 pstack 相反。

- "Rebase onto current trunk before the code-ready report and babysit. Keep that merge base in fix rounds. Rebase again only at merge prep, on a `git merge-tree` conflict with trunk, or on a CI failure that comes from a change on trunk."（`ps/skills/poteto-mode/playbooks/multi-phase-plan.md:62`）
  修复轮里保持合并基不变，只在三种情况下再 rebase，其中之一是 `git merge-tree` 显示与主干冲突。`git merge-tree` 是不改分支的试合并，对应 O14 的"试 rebase 并记录冲突"。pstack 不做周期性的真实 rebase。
- "Name the drift sweep in that report, since trunk may have grown callers of code the stack deletes or moves, and the owner's rebase has to reconcile them in the same wave."（`ps/skills/poteto-mode/playbooks/babysit.md:11`）
  主干新增了对"已删除或已迁走代码"的调用，就是 O14 说的漂移。pstack 要求在报告里点名做这项排查，并在同一次 rebase 里处理。
- "Start dependent work only after its parent merges, or base it on the parent branch when the execution playbook stacks."（`ps/skills/poteto-mode/playbooks/multi-phase-plan.md:49`）
  依赖的改动要么等父 PR 合入后再开始，要么直接基于父分支。对应"依赖的另一个 MR 未合入"。

另见：不频繁 rebase 的原因是 "A rebase or base retarget rewrites SHAs and can silently invalidate a verdict without touching a check."（`ps/skills/poteto-mode/playbooks/shipping.md:9`）；"Landing is continuous, never a terminal phase."（`ps/skills/poteto-mode/playbooks/orchestrate.md:65`）；CI 在未改动的代码里失败时，先用 `git merge-base --is-ancestor` 查基线是否过旧（`ps/skills/poteto-mode/playbooks/babysit.md:21`）。

与建议的出入：如果 O14 指"定期真的 rebase 到最新基线"，每次 rebase 都会让已有验证结果按 patch-id 规则失效、需要重跑，Lauren 刻意避免这样做。如果指"定期用 `git merge-tree` 试合并，grep 主干新增的调用者并记录"，与 pstack 一致。建议写明是后者。

### O15 证据入库

**态度：支持。**

- "Keep captures, recordings, logs, and tokens out of source control."（`ps/automations/benny/skills/reproduce-and-fix-issues/SKILL.md:30`）
  截图、录屏、日志不进仓库。Benny 的配置样例把产物放在 `/tmp/benny-artifacts`，保留 24 小时（`ps/automations/benny/templates/configuration.example.yaml:51`、`:52`）。
- "By default the log is a working artifact, not committed."（`ps/skills/show-me-your-work/SKILL.md:46`）
  连决策日志默认也不提交。
- "Commit it only for large or complex work where the trail has to be auditable later, like a big port or migration"（`ps/skills/principle-prove-it-works/SKILL.md:22`）
  例外是大迁移这类需要事后审计的工作，可以提交验证脚本的输出或决策日志。MR 7595 是迁移，适用这个例外，但例外针对的是文本记录，不是截图和 jsonl 原件。

另见：swarm 截图存到 `/tmp/swarm-<pr-id>/...`（`ps/skills/poteto-mode/playbooks/multi-phase-plan.md:77`）；验证 skill 维护时的运行笔记不提交（`ps/skills/maintain-verification-skill/SKILL.md:39`）；PR 描述里的细节放到链接的产物里（`ps/skills/poteto-mode/playbooks/opening-a-pr.md:23`）；orchestrate 的 store 留在 agent 自己的目录里作事后复盘（`ps/skills/poteto-mode/playbooks/orchestrate.md:66`）；要提交的是脚本，"Commit the lever when the work outlives the session."（`ps/skills/principle-build-the-lever/SKILL.md:19`）。

### O16 门禁报错写明修法

**态度：支持。**

- "Run `node pstack/skills/poteto-mode/scripts/check-plan.mjs <plan.md>` and fix every line it prints"（`ps/skills/poteto-mode/playbooks/multi-phase-plan.md:10`）
  门禁是工作中的一步，交回之前就跑，不是事后才发现。
- `` sub-blocks are [${names.join(", ")}], expected [${SUB_BLOCKS.join(", ")}] ``（`ps/skills/poteto-mode/scripts/check-plan.mjs:120`）
  报错同时给出"实际是什么、应该是什么"，并带 `文件:行号`（同文件 `:39`）。这就是"报错写明修法"，由脚本实现。
- "Skill prose is for things mechanisms cannot enforce."（`ps/skills/reflect/references/synthesizer.md:20`）
  机制已经能强制的规则不再写进 skill 正文。按这条，"按作者时间核对、别的分支上的提交也算"这类细则，应写在门禁的报错里，而不是补进 SKILL 正文。

另见：`orch ledger record` 收到非法结论时，报错直接列出全部合法取值（`ps/skills/poteto-mode/scripts/orch/store.ts:290`）；"If the fix is structural, only use the structural fix. The instruction is the symptom."（`ps/skills/principle-encode-lessons-in-structure/SKILL.md:21`）；PR 422 修的正是规则之间互相矛盾、agent 只能猜的问题，"Three pstack rules contradicted other rules in the same skills, so an agent had to guess which rule wins."（`raw/pr422.json` body）。

与建议的出入：pstack 把门禁放在流程中段就跑。只改报错文字还不够，还应让 owner 在每次里程碑提交后就能跑这道门禁，把"事后发现"变成"当场发现"。这一点是推论。

## pstack 有、16 条没覆盖的做法（5 条）

这些做法与长时间无人值守交付、人工介入、验收口径有关。

1. **定时审计 tick，用"有没有副作用"判断是否卡住。**
   - "Count only side effects as progress: commits, pushes, PR or check deltas, and store reports. Treat a lane that errors, or that passes its expected runtime without a side effect, as stuck. Stand it down and dispatch a replacement at once."（`ps/skills/poteto-mode/playbooks/autopilot-full.md:10`）
   - "Never leave the cadence to memory."（`ps/skills/poteto-mode/playbooks/multi-phase-plan.md:42`）

   root 大约每 30 分钟用真实的 `/loop` 唤醒一次，检查每个 owner 有没有提交、推送、检查状态变化，超过预计时长没有变化就判为卡住并替换。本次 owner 停了 10.5 小时，这样的 tick 在半小时内就会发现。计划骨架里必须有 30 分钟 tick，由 `check-plan.mjs` 检查（`ps/skills/poteto-mode/scripts/check-plan.mjs:20`）。

2. **先定时间预算，用到七成就收口。**
   - "Schedule landing against the budget. By roughly 70% of it, stop spawning and land what is verified."（`ps/skills/poteto-mode/playbooks/orchestrate.md:60`）
   - "/loop until done. if you're truly stuck after a few hours, stop and write up why."（`ps/docs/guide/07-overnight.md:15`）

   长程运行开始前定总时长，用到约七成就停止开新工作，先合入已验证的部分；真卡住了就停下写明原因。guide 还提醒 "a duration is not a finish condition."（`ps/docs/guide/07-overnight.md:79`），时长只是止损点，不是完成条件。

3. **验收结论分三态，"不确定"和"环境受阻"都不算通过。**
   - "A verdict is VERIFIED, NOT VERIFIED, or INCONCLUSIVE. Inconclusive is not a pass."（`ps/skills/figure-it-out/SKILL.md:43`）
   - "`verifier-blocked` is not a pass. Respawn when the environment heals."（`ps/skills/poteto-mode/playbooks/orchestrate.md:89`）
   - "If trunk does not have the feature, the lane records that fact and gates the behavior the diff adds plus the end state the user waits for instead of inventing a trunk result."（`ps/skills/poteto-mode/playbooks/multi-phase-plan.md:13`）

   环境做不到时记为 blocked，等环境恢复再验，不降成"通过"，也不顺手改口径。主干没有该功能时如实记录，改为验收新增行为和用户最终看到的状态。这和 O3、O4 里"测试台覆盖不了测试账号""验收口径与 spec 冲突"直接相关。验证账本的五种结论由 `orch ledger record` 校验（`ps/skills/poteto-mode/scripts/orch/store.ts:1334` 调用 `parseVerdict`）。

4. **人工评审关口在计划里预先写明。**
   - "A PR that changes an interaction is review-gated. The operator reviews it in chat with screenshots and a video before merge."（`ps/skills/poteto-mode/playbooks/multi-phase-plan.md:13`）
   - "State-then-wait, so a request to state the plan is not a go."（`ps/skills/poteto-mode/playbooks/autopilot-stack.md:7`）

   哪些改动要人看、看什么材料（截图加 30 到 60 秒的视频，`ps/skills/poteto-mode/playbooks/multi-phase-plan.md:124`）、在什么时点看，事先写进计划；"讲一下计划"不等于"开始执行"。人工介入点是事先约定的，不在执行中临时决定。`check-plan.mjs` 检查评审关口里有 screenshot、video、operator 三个词（`ps/skills/poteto-mode/scripts/check-plan.mjs:164`）。

5. **上下文压缩前写续接说明，接手时以记录为准。**
   - "Write the resume note off-context. Capture intent, what you were doing, progress and what's verified, current state, next steps, key files, and gotchas."（`ps/skills/poteto-mode/playbooks/pause-safely.md:8`）
   - "The prior trail is authoritative input. Resist the bias to re-derive it."（`ps/skills/poteto-mode/playbooks/session-pickup.md:6`）

   pstack 把"即将压缩上下文"列为暂停的触发条件之一（`ps/skills/poteto-mode/SKILL.md:140`），要求先把续接说明写到文件，例如 `/tmp/<slug>-resume.md`。本次主会话压缩了两次，这一步能减少压缩后的重复核对。暂停只能显式触发："This is explicit only."（`ps/skills/poteto-mode/playbooks/pause-safely.md:3`），这与 O1 里"中断不等于停止"一致。
