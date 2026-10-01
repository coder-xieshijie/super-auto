model: claude-opus-5-5[1m]
part: code

## 说明

- spec 和 verify 的 sha256 都已核对，分别是 `c6a945d5…` 和 `944fbc45…`。
- 改动范围是 `f938e48db1..19a2b940d2`，只通过 git 对象读取。
- 改动中的产品代码只有 24083bcc3c。8490c9d8a4 只改了 `.agents/skills/verify-archon/`，满足 §18.4“本节只改 verify-archon，不改产品代码”。
- `shared-login.test.mjs` 是用 `git archive` 导出到 `/tmp/m5c-va` 后运行的，15 个用例全部通过；没有动工作区。
- 本范围适用的机械检查：M12、M17、M06，以及 M15、M16 中的文档部分。M13 和 M14 在本范围没有对应改动。

## 问题

**1. TUI 实例的刷新不受并行规则约束，也不写刷新记录（V1，R103 / M17）**
- 位置：`.agents/skills/verify-archon/SKILL.md` 的“并行实例”最后一条，以及 `references/tui.md:29-30`。原文写明 “TUI 由自己的 MCode 登录会话按需刷新……这些刷新不经过上述规则，也不进 `auth-refresh.log`”。
- 依据：spec §18.4 要求 “多个 verify-archon 实例（接口、TUI、Electron）……彼此不使共用的登录失效……登录刷新只在没有 Electron 运行时进行”“每次刷新留下记录（时间、触发的实例、新的登录代次）”。R103 的实跑记录要求 “1 个 TUI 同时运行……刷新记录中没有 Electron 运行期间的刷新”。
- 现状：
  - TUI 在 `packages/tui/src/runtime/lifecycle.ts:234`（剩余 60 秒）和 `src/tui/launcher.ts:178`（30 秒）自行刷新，客观上也只在快过期时才刷，所以把 Electron 登出的风险不大。
  - 但这些刷新没有记录，R103 按刷新记录做的判定看不到它们。
  - 同类的小缺口：`shared-login.mjs` 的 `recover()` 和 `syncApiToken` 的非刷新分支用 `getAccessToken({ minValidityMs: 0 })` 读 token。token 已过期时，oauth-core 会在这里刷新，同样不写日志。
- 影响：“每次刷新留下记录”不满足。R103 的“没有 Electron 运行期间的刷新”可能被误判为通过。

**2. Goal 长期文档的实现基线不在交付分支上（M12）**
- 位置：`.harness/docs/goal/README.md:12` 的“实现提交 `52693d54131c…`”，以及 `goal/spec.md:3`“本文描述入口页所列实现基线”。
- 现状：
  - `git merge-base --is-ancestor 52693d54131c 19a2b940d2` 结果为否。
  - `changes/README.md:10` 的基线还是 `6556142e7d`，和 README 不一致。
- 依据：M12 要求 “Goal 长期文档已按新行为更新”。
- 影响：按基线核对文档的人会拿到错误的代码。下面第 3、4 条的偏差都由此而来。

**3. 文档对“发出后报错”的用量写法与代码和 spec 冲突**
- 位置：`goal/spec.md:301` 和 `goal/implementation.md:283`，原文 “provider 返回错误状态的请求按已知的零计”。
- 依据：
  - spec §4.5 原文：“缺少 usage 时标记为不完整，不当成零”。
  - 代码 `local-runtime-v2/src/service/goal/accounting/request-ledger.ts:206-213`：已发出的 attempt 只要 input+output 为 0，不管成功、取消还是失败，都标为不完整。
- 影响：文档把代码已正确实现的规则写反了。

**4. 长期文档没写 token 预算用尽时在本轮收尾，以及 §5.3 第三条、§5.5（M12）**
- 位置：`goal/spec.md:325-340`、`implementation.md:265-269` 和 `:484`。这几处只写了“工作请求用尽”时的收尾，`graceSteps` 只写成收尾请求数。changes 记录 `:28` 也是这样。
- 代码实际行为：
  - token 用尽时同样关闭普通工作，后续请求改用 `GOAL_TOKEN_BUDGET_WRAP_UP_INSTRUCTION`（`request-accounting.ts:113-132`、`:163-171`）。
  - 工具执行前的检查在 token 或活跃时间用尽时，按 `graceSteps` 先 steer 再停止（`admission-budget.ts:62-86`）。
  - “已关闭普通工作”在 runner 重试等路径中持续生效（`isWorkClosed`），用户 steer 会交还普通输入路径（spec §5.3、§5.5）。
  - 这些都已实现，`verification.md` 却没有对应的测试映射（测试实际存在于 `pi-turn-runner.test.ts:1096/1133`、`steering-requeue.test.ts:181`）。
- 影响：GOAL-07 与代码不符。长期文档没有覆盖本需求的全部新行为。

**5. 功能地图索引仍把行为已变的子功能留在“已实跑”表（R102 / §18.3）**
- 位置：`.agents/skills/verify-archon/features/README.md`。
  - 接口“恢复”、Electron“继续”（:30）与下表的“恢复落地的响应”“继续（恢复落地）”（:51）是同一批子功能。
  - TUI“最终回复”、接口“最终回复的运行顺序”（:32）与下表的“完成轮有最终回复与完成行”“最终回复晚于验证派发”（:53）重复。
  - 接口“token 预算”（:33）的旧记录验的是另起总结轮次，§5.3 已取消这个轮次。
- 依据：上表自己写着“上表只保留行为没有变化、记录仍然适用的子功能”。§18.3 要求“新增或变化的子功能按实际运行结果更新……没有实跑的标为未实跑”。
- 影响：会误导执行者跳过重跑，索引与实际运行不一致。

**6. 功能地图中有两处步骤照做会失败**
- `goal/feature-map/completion.md:75`：`node $V fault disable <ruleId>` 没有带 `--on electron`。而 `verify-archon.mjs:1657` 是 `const kind = flags.on ?? 'runtime'`，命令会打到接口实例，规则关不掉，后面的恢复仍会命中 50113。
- `goal/feature-map/lifecycle.md:74`：写的是“输入 `/goal` 让 `goal-mode-tag` 出现”。但 `MessageInput.tsx:1115` 写明只有在命令面板里选中 goal 项才会进入目标模式，单纯输入 `/goal` 不会出现标签。应补上“选中”一步，S26 的写法就是“输入 `/goal`，选中后”。

**7. 较轻的文档与代码不符**
- `lifecycle.md:119`：TUI 构成行写“没有的部分不列”。实际 `tui/features/goal/banner.ts:290-291` 总是输出 `work`、`wrap-up`，只有 `unconfirmed` 是按条件加的。
- `references/electron.md:137-140`：新加的请求数悬停说明接在“2026-09-30 实跑：”那一段里，读起来像当天已实跑观察过。实际当时这个提示还没实现（旧文写的是“待实现后再核对”），容易被当成编造的实跑结论。
- `goal/implementation.md:78-79` 写 migration 42“全部行原样复制”。实际 `migration-0042…ts:88-93` 会跳过关键列为 NULL 的行。
- `goal/verification.md:37` 写 `--package @mavis/tui`，但 TUI 的 workspace 名是 `@minimax/code`，这条命令跑不起来。
- `changes/2026-10-01-goal-v2-and-feedback-fixes.md` 缺 `changes/README.md:39-47` 要求的几项：取代 GOAL-07 总结 Turn 的替代关系、head SHA、未运行项与风险。不过记录没有把验证写成已通过。

**8. 本范围外的待确认项（不计入本里程碑）**
- 启动顺序：`runtime-services-lifecycle.ts:283-287` 中，`recoverQuestionnairesOnStartup` 排在 `bindConversation`（会接管活跃 Goal 并提交续跑）之后。spec §3.5 原文是“处理旧总结项、问卷恢复和活跃 Goal 接管之后，再唤醒队列”。
- `goal/spec.md:205-208` 列出的启动顺序里也没有问卷恢复。
- 我没有追到问卷阻塞判断是否只依赖已持久化的状态，所以不能确定这是否真的违反 spec，需要 owner 确认。

## 检查过、未发现问题的部分

**S26 修复（24083bcc3c），对照 §6、§10：**
- `canSteerActiveTurn` 新增了一个条件：只有在 `isSessionBusy` 为真，或会话里还有已绑定、尚未结束的 Goal Turn（`hasBindingInSession`）时才走 steer。会话空闲时直接 kick，只绑定一个 Turn，满足 §6“只开始一次”。
- 运行中修改目标：`isSessionBusy` 为真，仍然 steer，行为不变（测试 `steers the objective_updated prompt into the busy Turn immediately`）。
- 已准入但尚未运行的 Turn：binding 在准入提交时写入（`admission.ts:338`），Turn 计时结束时才删除（`lifecycle.ts:500`）。所以这种情况仍走 steer 并被隔离，现有测试 `fences an admitted Turn before its running timing event…`（`isSessionBusy: () => false`）依赖的正是这个新条件。
- 检查之后才出现的激活竞争仍走原有回退（`rejects an activation race…`）。
- S24、S27 的补充消息路径不经过 objective steering，不受影响。新增测试覆盖了“暂停的 Goal 用一次 PATCH 改目标并恢复，只开始一个 Turn”。

**ADR（19a2b940d2）：**
- 内容满足“交付与授权”的要求：Goal 业务整体归 v2 owner；问卷、权限、附件、任务留在 v1 复用；不保留 fallback 和双写；计量单位是逻辑 LLM 请求。
- 已登记到 `adr/README.md` 索引，格式是 Decision、Context、Consequence 三节。
- 文中引用的标识符都存在：`GoalController`、`GoalService`、`withGoalAgentProduct`、`RuntimeGoalPort`、503 `GOAL_UNAVAILABLE`、`local_runtime_v2_goals`、`local_runtime_v2_goal_requests`、migration 42/43。v1 表只在 migration 42 中读取。
- 提交按要求分开：S26 修复、验证能力、功能地图、长期文档、ADR 各自独立成提交。

**V1 的其余部分（M17）：**
- 测试覆盖了 M17 要求的各点：租约够时不刷新；有 Electron 运行时推迟刷新，直到剩余不足 2 分钟；被拒后立即重读；每次刷新写记录。
- `authContextInvalidator` 真实接入了 runtime：`compat/v1/runtime.ts:423`、content-safety `checker.ts:91`、`model-resolver-helpers.ts:78`。
- SKILL.md 写明了并行规则和“改额度的场景独占账号”，`quota.md` 也有对应说明。
- `auth-check` 统计了 `contentSafety401`、`electronAuthLost`、`http429`。

**其余文档检查：**
- 功能地图覆盖了 §18.3 列出的全部变化。
- `limits.md` 的 `usage_limited` 改为用 `quota` 命令构造；“不要为了验证去制造配额耗尽”在全仓已删除；到点自动恢复的计时注明用故障注入构造。
- M16：§18.2 的七项能力都有命令或启动选项，并写明了用法。
- M15 文档部分：Weekly 低位、Credits 自动消耗、需要一次真实请求确认、2056/2067→42212、50111 都已写入 SKILL.md“边界”和 `quota.md`。
- M06：`implementation.md:482`、`goal/spec.md:313-315` 和 `goal-config.ts:22` 都写明单位是工作请求，缺省不设上限。
- 长期文档没有把未执行的验证写成已通过。
- 已检查的文件：`.agents/skills/verify-archon/{SKILL.md,features/README.md,references/*.md,scripts/shared-login*.mjs,runtime-server.mjs,electron-server.mjs,verify-archon.mjs}`、`.harness/docs/goal/**`、`.harness/docs/adr/{README.md,goal-v2-ownership.md}`、`packages/local-runtime-v2/src/service/goal/{continuation/continuation.ts,admission/turn-context.ts}` 及两份 integration 测试。

## 可选

1. 把 README 基线改为本分支可达的最后一个代码提交，然后按它修正第 3、4 条，并在 `verification.md` 补上测试映射。
2. R103 的实跑要求 20 分钟，和 Electron 默认租约同样是 20 分钟。起跑时如果 token 剩余接近 20 分钟，接口实例会在剩余不足 2 分钟时按规则刷新，这次刷新会以 `electronsRunning` 非空的形式记下来，R103 的判定就会失败。实跑时可以给 Electron 更长的 `--auth-lease`，或者确认起跑时 token 剩余足够长。
