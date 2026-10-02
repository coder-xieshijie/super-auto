# 独立验证输入：MR !7595（Goal v2 迁移、请求计量与反馈修复）

按 `/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/references/verifier-brief.md` 验证。下面是验证说明要求调用方给出的全部输入。

## 需求文件

- spec：检出目录内 `.harness/docs/specs/goal-v2-and-feedback-fixes/spec.md`（sha256 `c6a945d5ac961f85ae0701ab9e92ac6432f2225c5070c13881dc70d7702a60c8`）
- verify：检出目录内 `.harness/docs/specs/goal-v2-and-feedback-fixes/verify.md`（sha256 `944fbc45c45fca70c7c74ee72699e113f2967445d9dae4a4ec094ebeb6db71df`）
- 两份都是用户确认冻结的版本；交接提交 `d46dc1c7e1`。

## 待验证的代码

- head：`{{HEAD}}`
- 基线：`c92ef87c95176bda8310cafff357d86478fcb3f1`（与 `preview_train` 的 merge-base）。代码审查读 `git diff c92ef87c95..{{HEAD}}`。
- 迁移前验证基线（RG1、RG1b、RG2 对照用）：`d770f05f30`。它的已有运行记录在 `$REQ/evidence/rg1-baseline/`、`$REQ/evidence/rg1b-s17/`、`$REQ/evidence/rg2-migration/`，可直接作为对照；需要在基线提交上重新生成数据的，只用下面“测试数据”里已备好的旧数据。
- 检出目录：`/Users/minimax/code/mm/worktrees/agent-archon/gv2-verify-final`（专给你用，`HEAD` 应为上面的 head，工作树干净；依赖已安装。需要时你自己构建：`node .agents/skills/verify-archon/scripts/verify-archon.mjs prepare runtime tui electron`，构建不算改代码，但构建后 `git status --porcelain` 仍须为空）。

## 项目验证能力

- verify-archon Skill：检出目录内 `.agents/skills/verify-archon/SKILL.md`（启动、操作、观察 Electron / TUI / 接口实例；故障注入 `references/fault.md`；数据目录与旧数据启动 `references/data.md`；额度 `references/quota.md`；先读“并行实例”一节）。
- Goal 功能地图：检出目录内 `.harness/docs/goal/feature-map/`（每个子功能的入口与操作步骤）。
- 本需求的场景驱动脚本与判定脚本：`REQ=/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes`，`$REQ/tools/`。脚本只是 owner 写的辅助，判定以 verify 的检查点为准；你可以用它们，也可以自己从入口操作，判定器有疑问时按 verify 原文自己读值。
- 场景与命令的对应：`$REQ/plan.md` 的“验证与验收”一节（只用来执行场景）。脚本默认读 `/tmp/gv2-final3/env.sh` 一类的环境文件、写 owner 的证据根；你要另写一份环境文件，把 `M2_ROOT` 指向你的证据目录、`M23_HEAD` 写你验证的 head、启动锁换成 `/tmp/gv2-verify-codex-up.lock`，并把 `cd` 指向你的检出目录。

## 代码质量准则

- review-rules：`/Users/minimax/code/github/xieshijie/dev-skills/skills/review-rules/SKILL.md`

## 证据目录

- `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/verify-codex-{{SHORT}}/`。每验完一个场景就在其中 `results.md` 追加一行结果表的行。被调用方在同一个会话里请你接着验时，从 `results.md` 里还没有结果的场景接着做。

## 允许使用的环境

- 实例：只用你自己经 verify-archon `up` 启动的实例（每次 `up` 会分配独立的 profile、端口和数据目录，在 `$TMPDIR/verify-archon/<runId>/`）。不要停、不要读写别人的实例。owner 的自验已结束；若 `verify-archon list` 里仍有别人的活实例，不要动它们。
- 并行：verify-archon 支持 3 个 Electron、1 个接口、1 个 TUI 同时运行而互不登出；启动走共享锁，错开 6 秒。
- 配置：验证统一用 staging，配置文件 `~/.minimax/verify-goal-v2/config.yaml`（含凭据，**不要打印、不要复制进证据**）；需要特定预算配置时，按 `$REQ/tools/m2-lib.sh` 的 `m2_config` 生成到 `/tmp` 下。证据里不得出现 token 或 JWT。
- 测试数据：S01、S02 的升级前旧数据已在基线提交 d770f05f30 上生成，见 `$REQ/evidence/final-c9ee596180/_baseline/README.md`（runId、数据目录、引用方式）。`--from-data` 会复制数据，旧数据可重复使用。**S02 对时间敏感**：运行前用 sqlite 只读核对 USAGE 会话 Goal 的 `usage_recovery_at_ms` 仍在将来至少 10 分钟；已过期就把 S02 记为 UNVERIFIED（环境受阻）并说明，不要自己生成新数据。
- 额度：**不修改任何额度**。S35、S36 及 limits.md 中依赖修改额度的子功能是覆盖盲区 B15（Payment 测试台查不到 staging 登录账号），只允许只读的 `quota show`。
- 模型调用：场景里的模型是 staging 的 MiniMax 模型，按 verify 原文执行即可；verify 写了“模型没有…时本次不计”的，按无效重跑，每个场景最多 4 次。
- 安全：Electron 场景会弹出测试窗口；往输入框打字后先读回核对，不一致就中止该次运行。发现被测模型在 workspace 以外读写时，立即停掉该实例，记录事件，记录里不含原文。不要用测试实例访问真实用户的数据目录（`~/.minimax` 下除上面的配置文件外都不要读）。
- 清理：结束时停掉你启动的全部实例（`verify-archon down`），删除你在 `/tmp` 下生成的临时配置；证据保留。

## plan.md

- `$REQ/plan.md`：“验证与验收”一节是场景对应的实际命令；“决定清单”是 owner 的主张，由你按验证说明第 4 步判断（是否放宽验收或违背 spec 意图）。决定清单里引用的另一家模型意见在 `$REQ/evidence/decisions/`。
- owner 的自验证据在 `$REQ/evidence/final-c9ee596180/`（只作参考，不能作为你的判定依据）。

## 本次范围

verify 的全部内容：冒烟集、全部场景（S01–S41 含 b 场景）、回归范围（RG1、RG1b、RG2、RG3）、要求表里以机械检查或已有检查证明的要求（M01–M17 等），以及 R103（3 个 Electron、1 个接口、1 个 TUI 同时运行 20 分钟）。覆盖盲区里的检查点按验证说明记 UNVERIFIED。

## 报告

按验证说明的报告格式，作为你的最终回复输出；开头三行固定（`head:`、`验证模型：`、`verdict:`），`head:` 写 40 位 SHA。
