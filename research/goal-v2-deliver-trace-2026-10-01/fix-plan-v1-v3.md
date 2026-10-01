---
id: research-goal-v2-fix-plan-v1-v3-2026-10-01
recorded_on: 2026-10-01
timezone: Asia/Shanghai
source: verify-archon 源码（`gv2-verify-tools` 检出，`9521a8b053`）、`@mavis/oauth-core` 源码、共享登录存储的元数据（不含 token）、M2 第 2 轮的 401 记录、dev-skills main `4c45165` 的 deliver 脚本与说明
scope: [并行分析](parallelism.md)里 V1、V2、V3 的修复方案；未实施
---

# V1–V3 修复方案

用户（2026-10-01）对 V1、V2、V3：“先修这个, 给出修复方案”。三项的背景与数据见 [parallelism.md](parallelism.md)。

## 1. 三项改在哪里

| 项 | 改哪里 | 对在途的 MR 7595 |
|---|---|---|
| V1 实例互不使登录失效，场景分组并行 | agent-archon 的 verify-archon（`.agents/skills/verify-archon/`，随 7595 合入） | 需要用户决定放不放进 7595（第 5 节） |
| V2 修复后的重跑由脚本选场景 | dev-skills 的 deliver：新脚本、计划格式加一列、SKILL 一句 | 按 O1 收窄后的约定，不阻塞就不推给在途交付；owner 现在已经手工这样做（16:17） |
| V3 代码审查提到提交后 | dev-skills 的 deliver：SKILL 一段、检查说明拆成两部分、记录脚本收两份报告 | 同上，下一个需求起用 |

## 2. V1：多个实例同时跑而不让登录失效

### 2.1 根因

| 事实 | 出处 |
|---|---|
| 所有实例共用 `~/.minimax/auth/staging/cn/mcode-public/` 的同一份登录；access token 有效期 60 分钟，到现在已刷新到第 262 代 | `auth-state.json`、`auth.json` 的元数据（`auth.json` 写入 16:26:46，过期 17:26:46） |
| Electron 实例启动时要求 token 至少还剩 50 分钟，不够就刷新 | `electron-server.mjs` `readAccessToken`：`minValidityMs: 50 * 60_000` |
| Electron 实例只拿到一个 access token（写进临时 profile 的旧版存储），自己不能刷新 | `electron-server.mjs` `prepareUserData`：只写 `{ tokens: { accessToken } }` |
| 接口实例每 60 秒从共享存储取一次 token；被拒时没有立即重取 | `runtime-server.mjs` `createManagedAuth`：`setInterval(refresh, 60_000)`，只把 `authContextGetter` 交给运行时，没有交 `authContextInvalidator` |
| 刷新后，旧的 access token 被服务端作废 | M2 第 2 轮：12:14:13 同时起两个 Electron 后，先起的接口、TUI 实例出现内容审核 401（S02 16 次、S04 1 次、S08 16 次、S11 5 次），之后错开启动就是 0（`evidence/m2-163f/README.md`） |

于是：距上次刷新超过 10 分钟后，再起任何一个 Electron 都会刷新一次，正在跑的 Electron 从此 401；接口实例最多 60 秒内 401。所以 plan 规定“同一时刻只启动一个 Electron”。

“服务端刷新后作废旧 access token”是从现象推断的，第 2.5 节的探针先确认。

### 2.2 修法 A：verify-archon 统一管刷新（不需要人，不改产品代码）

1. **Electron 启动只要求“够跑完这一次”。** `electron-server.mjs` 的 50 分钟改成租约参数 `--auth-lease`，默认 20 分钟；本需求单次 Electron 运行最长 11.4 分钟。
2. **刷新只在没有 Electron 在跑时做。** verify-archon 的进程需要刷新时，先查 `$TMPDIR/verify-archon/*/state.json` 里有没有进程还活着的 `electron` 实例：
   - Electron 启动方：token 剩余不够租约、又有别的 Electron 在跑，就等它们结束（最多等一个租约）再刷新。
   - 接口实例的定时刷新：有 Electron 在跑时推迟，直到 token 剩余不到 2 分钟。
   - 没有 Electron 在跑：照常刷新。
3. **接口实例被拒时立即重取。** `runtime-server.mjs` 给运行时加上 `authContextInvalidator`（运行时已有这个钩子，Electron 产品用它在 token 被拒后恢复）：被拒时立即从共享存储重读，不等 60 秒。
4. **留痕。** 每次刷新写一行到 `$TMPDIR/verify-archon/auth-refresh.log`：时间、触发的实例、新的 generation。场景分析脚本已有 `contentSafety401`、`electronAuthLost` 两个计数，再加一个 429 计数。

效果：一个 token 窗口（60 分钟）的前约 40 分钟里，可以同时起多个 Electron，都不触发刷新；之后新起的 Electron 等正在跑的结束、刷新一次再起。

剩余风险：用户自己在 staging 环境用的 TUI 或 Desktop 也用这份登录，它们刷新时 verify-archon 管不到。`doctor` 加一行提示；需要时用修法 B。

TUI 实例：`tui-server.mjs` 里没有登录代码，TUI 自己读共享登录。它受刷新的影响方式在探针里确认。

### 2.3 修法 B：登录槽位（需要用户一次性操作，按需做）

- 两个脚本已支持 `VERIFY_ARCHON_AUTH_HOME`。建几个槽位目录（例如 `~/.minimax-verify/slot-1` 到 `slot-3`），每个槽位单独登录一次：新命令 `verify-archon auth login --slot <n>`，用 oauth-core 的设备码登录，用户在浏览器确认一次。
- `up` 时领一个空闲槽位（锁文件），`down` 时释放。不同槽位的刷新互不影响。
- 用不同的测试账号登录不同槽位，还能把额度和限流分开。Goal 场景用真实模型，同一账号同时跑多个实例，可能触发 429，把“额度受限”混进本来不测它的场景。
- 前提：同一账号的两次登录各自刷新、互不作废，要先在探针里确认。

建议先做 A。A 之后仍出现用户自己刷新导致的作废，或出现 429，再做 B。

### 2.4 场景分组并行

- **分组。** plan 的“验证与验收”表加一列“lane”。owner 按入口和依赖分组：在同一个 Electron 实例上连续跑的场景放一组（例如 S03、S06、S07、S32）；种子数据和读取要先后进行的放一组（例如 S41）；其余按入口分开。
- **执行。** 每组一个 runner 子代理，后台同时启动；默认最多 3 组，按探针的内存实测调整（本机 24 GB、12 核）。
- **构建只做一次。** 先 `prepare`，各组用同一个检出，启动前核对 head。
- **清理。** 用 `down --run <id>`（复盘 8.8 的 O5(a)），不手写 `rm -rf`。
- **独立验证者。** 验证说明已经要求给验证者独立的实例；修法 A 之后，验证者的实例也不会和 owner 的互相作废。

### 2.5 探针：实施前先做，约 30 分钟

只用测试账号，不改代码：

1. 起一个接口实例；10 分钟后起一个 Electron（会触发刷新）。看接口实例的 401 出现几次、持续多久，确认“刷新作废旧 access token”。
2. 同时起两个 Electron，看先起的一个是否从此 401（`electronAuthLost`）。
3. 同时起 3 个 Electron、1 个接口、1 个 TUI，记录内存峰值。

如果做修法 B，再加一项：同一账号登录两个槽位，刷新槽位 1 后，槽位 2 的 token 是否仍然有效。

### 2.6 怎样判定修好了

- **脚本测试。** verify-archon 的 `scripts/*.test.mjs` 加用例：租约够时不刷新；有 Electron 在跑时推迟刷新；刷新后被拒的接口实例立即拿到新 token。
- **实跑。** 修法 A 之后重做探针第 3 项，跑满 20 分钟，`contentSafety401`、`electronAuthLost` 都是 0；`auth-refresh.log` 里没有在 Electron 运行期间的刷新。
- **一整轮场景。** 下一轮场景按 3 组跑，墙钟与 401 计数写进 plan。

### 2.7 对 7595 的价值

7595 剩下的验证：M3 第二轮、M4 约 12 个场景（S22–S29b、S31、S33、S39）、M6 的 44 个场景全量自验，以及另一家模型对同样 44 个场景的独立验证。M2 的 15 个场景串行一轮约 70 分钟，44 个场景串行一遍约 3 小时；分 3 组同时跑约 1 小时（推算）。M6 要跑两遍，省下约 4 小时。

## 3. V2：修复后的重跑由脚本选场景

### 3.1 改动

- **计划格式。** `references/plan-format.md` 的“验证与验收”表加一列“涉及路径”：每个场景经过哪些代码目录（glob）。owner 绑定命令时一起写，因为这时它最清楚场景走哪些代码。
- **新脚本** `scripts/select-scenarios.mjs`：

  ```bash
  node <deliver>/scripts/select-scenarios.mjs --plan <plan.md> --repo <worktree> --from <上一轮场景所在的 head> --to <当前 head> [--failed S04,S09]
  ```

  - 取 `git diff --name-only <from>..<to>`。
  - 测试与文档文件（`**/*.test.*`、`**/test/**`、`*.md`）不触发重跑。
  - 其余改动文件按“涉及路径”匹配，匹配上的场景要重跑。
  - **有改动文件没有任何场景认领时，选全部场景。** 漏写路径时宁可多跑。
  - 冒烟集和 `--failed` 给出的场景总在里面。
  - 输出每个场景和选中原因（哪个文件），另给一份 JSON 给 runner。
- **SKILL 一句**（“里程碑”一节）：修复后的重跑用这个脚本选；里程碑检查前，这个里程碑的每个场景要在“之后改动都被脚本判为不影响它”的 head 上通过；最终 head 照旧全量。

### 3.2 不变的部分

完成条件 1（最终 head 上全部场景实际跑通）和独立验证（另一家模型完整验证）都不变。脚本只决定中间轮跑哪些。

### 3.3 判定修好

- 脚本单测：只改测试 → 不选；改了没人认领的共享文件 → 全选；改了某场景认领的路径 → 选它；`--failed` 总在里面。
- 用 7595 回放：在 plan 里给 M2、M3 的场景补上涉及路径，跑 `--from c926bcd2e4 --to 69696e4f2c`，对比 owner 16:17 手工选的那批（S13、S18、S30、S40 与 S01、S04、S05、S09、S10、S11、S37）。脚本少选的，说明路径写漏了；多选的，看是不是本该重跑。

### 3.4 依据

- OpenAI：“Once those pass, broaden or repeat testing only when new changes, failures, or unresolved concerns justify it”（G6 L132）
- Anthropic：“includes a default `--fast`option that runs a 1% or 10% random sample”（A07 L77）
- Lauren：“Re-verify anything else when the patch changed.”（shipping:9）。最终 head 照这条做，所以全量不变。

## 4. V3：代码审查提到提交后

### 4.1 改动

- **检查说明拆成两部分**（`references/milestone-check.md`）：
  - 代码部分：输入 spec、verify 的场景 ID、范围起止 commit，不要证据。对照 spec 读 diff。
  - 证据部分：输入场景的证据和同一范围。逐个检查点核对证据。
  - 报告格式不变：第一行模型 ID，之后是问题。
- **记录脚本**（`scripts/record-milestone-check.mjs`）：`--report` 可以给两次（代码、证据各一份），按顺序合成一份记录，各自保留第一行的模型 ID。`milestones.mjs` 不改：一轮仍是一条记录。
- **SKILL“里程碑检查”一段改为下面的顺序。**

### 4.2 新的顺序

1. 里程碑提交，head 为 X。立即在后台启动代码部分的子代理，范围是这个里程碑的起点到 X；同时开始跑场景（V1 的各组）。
2. 代码部分先回来时，owner 在工作区或草稿分支准备修复，**先不提交**。门禁要求第一轮记录早于它之后的第一个提交；不改这条规则，就要求修复等记录存好后再提交。
3. 场景跑完后，启动证据部分的子代理，范围同样到 X。
4. 两部分都回来后，用记录脚本存成第一轮：`--range <起点>..X --report code.md --report evidence.md`。然后提交两边的修复，按 V2 重跑受影响的场景，第二轮同样分两部分，范围是 X 到新的 head。

### 4.3 拿 M2 套一下

- 10:33 提交后立即审代码，大约 10:45 就能拿到两个代码问题：取消且无用量的请求按 0 计；旧总结项启动后仍算待处理。
- 第 1 轮场景 11:55 跑完后核对证据。两边的问题加上场景发现的 4 个缺陷一起修，修完重跑一次。
- 实际做法是三轮场景（80、36、72 分钟）加两次检查。按新顺序是两轮场景加两次检查，省掉第 3 轮。

### 4.4 判定修好

- 记录脚本单测：给两份报告时合成一条记录，两个模型 ID 都在；只给一份时与现在相同。
- 用 7595 现有的 M1、M2 记录回放 `check-delivery.mjs --milestones-only`，结论不变。

### 4.5 依据

- OpenAI：“As a starting point, use parallel agents for read-heavy tasks such as exploration, tests, triage, and summarization.”（SUB L81–82）
- Anthropic：“A verifier that only needs to run tests and report results does not require implementation context.”（BMAS L246）
- Lauren：审代码的 lane 与场景 lane 在同一轮里一起扇出（multi-phase-plan:66），问题合成一次退回（autopilot-full:8）。

## 5. 待用户决定

1. **V1 放不放进 7595。**
   - (a) 放进，并先在 spec §18 加一条要求，例如“verify-archon 的多个实例可以同时运行，不互相使登录失效”，配一条机械检查。用 core-spec 重新冻结一次（#25 之后要带用户原话的确认行），由 7595 的 owner 在 M4 场景之前实现。这与此前“MR 要交付的东西都写进 spec”的决定一致。
   - (b) 放进，但不改 spec。owner 按 deliver“依赖某项验证能力的场景执行前，先补上这项能力”自己补，作为工具改动随 MR 提交。更快，但和上面那条决定不一致。
   - (c) 7595 不用，等它合入后另开 MR。剩下的 M4 和 M6 照现在串行跑。
   - 建议 (a)：M6 两遍全量是 7595 剩余工作里最长的一段，2.7 节推算能省约 4 小时；重新冻结的成本是一次确认。
2. **修法 B（登录槽位、多个测试账号）** 现在做，还是等修法 A 之后看到问题再做。建议等。
3. **V2、V3 推不推给 7595。** 按 O1 收窄后的约定默认不推，下一个需求起用。V2 的做法 owner 现在已经在手工用；V3 对 7595 剩下的 M4 也有用，但要改 owner 的检查顺序。

## 6. 顺序

1. 探针（2.5 节），约 30 分钟。
2. V1 修法 A 与场景分组：按第 5 节第 1 项的决定落到 7595 或另开 MR。
3. dev-skills 一个 PR 做 V3（改动小、省一轮场景），合入后再一个 PR 做 V2（要给计划格式加列）。按“一次上一项”的约定分开。
