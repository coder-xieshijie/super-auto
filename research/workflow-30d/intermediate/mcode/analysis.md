# MCode 最近30天工作流证据分析

窗口：2026-08-25 09:33:02 UTC ≤ event timestamp < 2026-09-24 09:33:02 UTC。

## 3 个优先结论

1. 用户最稀缺的注意力集中在产品边界、复用和验收语义；重复解释已定边界、询问任务状态、收紧入口的工作应迁到可执行契约与调度事实。
2. 并行规模已经很高。最明显的收益点是让 integrator 提前跑最薄生产链路，并使依赖交付后的真实基线进入下游，降低末端补接线与边界返工。
3. 恢复、固定 SHA、独立复核与诚实的 PARTIAL 报告已经是优势。应延续这些能力，将重复的人肉检查固化到现有工具、真实产品探针与 CI，而不是再增加通用审批层。

## 覆盖与口径

全量机器扫描65个可发现 `.minimax*` profile的已知runtime目录、SQLite及旧版SQLite；16个profile在窗口有可见消息。归并得到758会话、38,995条可见消息，其中主profile644会话/38,478消息，开发profile114会话/517消息。主profile43,535次tool-call条目，不等于独立命令或实际有效动作。

主profile分为显式Agent Lord委派148、native child257、推断委派6、交互或未分类233。569条主profile根输入并未逐条证明为真人输入，不估算真人占比。父子及Agent Lord关系见sessions.jsonl。下述13条任务链共5,759条窗口可见消息；阅读方式是完整提取链条，重点核对用户要求、纠正、阶段交接、最后可见结果及关联工具证据，未逐字人工听读所有工具输出。

不提供session成功率或以首末timestamp估计工作时长。缺少结尾可能来自中断、截窗、迁移、另一个端点交付；current_status是采集时元数据，不代表历史结果。以下“后续报告称”均指session内可见声明，本次未实时回读历史MR。

## C01 sandbox 层次边界被反复重新解释

会话：`mvs_a7d6c18b259a452e85f5e2e43539b6e0`；分类：interactive_or_unclassified；窗口消息：589；[完整可见文本摘录](case-evidence/mvs_a7d6c18b259a452e85f5e2e43539b6e0.md)。

- 2026-09-03T13:14:52.448000Z，user，SQLite `local_runtime_message_rows.id=3801`：

  > 沙箱只负责 bash 的拦截与否

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=3801`。

- 2026-09-04T06:37:20.764000Z，user，SQLite `local_runtime_message_rows.id=4483`：

  > 我现在就希望, permission, sandbox, execute 三层分开

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=4483`。

- 2026-09-04T07:35:12.243000Z，user，SQLite `local_runtime_message_rows.id=4497`：

  > 在开发期间, 都是用 feature 的 idl 去 generate的

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=4497`。

- 2026-09-04T09:03:46.586000Z，assistant，SQLite `local_runtime_message_rows.id=4854`：

  > 第四轮修复已提交推送，CI 正在跑

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=4854`。

**观察与后续边界：** 用户在确定职责与产品语义，属于高价值决策；同一边界在实现后反复重申，则是契约没有约束实现的成本。IDL feature 分支协作规则也被 agent 误当问题，需要用户纠正。后续可见 depcruise 修复与提交声明，不能据此判定整条任务最终合入。

**可以改进：** 把 permission 判定、sandbox 放行、execute 可恢复删除写成少量可执行契约测试；先跑原功能保真案例。已决定的 feature IDL 顺序用同一来源引用，避免每个 reviewer 重新裁决。

## C02 四档权限之外增加保护

会话：`mvs_3d431041062b4c44aedde68b990055d5`；分类：interactive_or_unclassified；窗口消息：425；[完整可见文本摘录](case-evidence/mvs_3d431041062b4c44aedde68b990055d5.md)。

- 2026-09-04T10:33:37.213000Z，user，SQLite `local_runtime_message_rows.id=4951`：

  > 我预设的等级是

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=4951`。

- 2026-09-04T10:39:50.779000Z，user，SQLite `local_runtime_message_rows.id=4969`：

  > 我就希望按照这个来, 其他不符合的去掉

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=4969`。

- 2026-09-04T14:33:00.440000Z，user，SQLite `local_runtime_message_rows.id=6802`：

  > 基于 architect 表格的 4个限制, 不要在加额外的保护

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=6802`。

- 2026-09-05T03:39:52.071000Z，assistant，SQLite `local_runtime_message_rows.id=7093`：

  > 已按你的决定在两个仓库都移除了

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=7093`。

**观察与后续边界：** 用户首先发现 full access 与预期不符，然后授权去掉表格以外的行为。后续报告称删除 unused mandatoryDenyWrite，保留产品依赖的 unlinkAllowOnly；还承认自己引入敏感词 gate 失败并修复。这里存在明确的产品契约偏离及修复回路。

**可以改进：** 从四档矩阵生成正反例，真实 shell 对读/写/删除逐项跑；把“未声明的保护也改变产品行为”加入 spec 验收，减少新增抽象后再拆除。

## C03 sandbox 拆分与调度产生用户协调负担

会话：`mvs_e63208d747624f249704be7af9ba3d37`；分类：interactive_or_unclassified；窗口消息：466；[完整可见文本摘录](case-evidence/mvs_e63208d747624f249704be7af9ba3d37.md)。

- 2026-09-12T07:00:44.301000Z，user，SQLite `local_runtime_message_rows.id=23561`：

  > 我现在觉得特别繁琐，实现起来特别慢

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=23561`。

- 2026-09-12T07:16:42.946000Z，user，SQLite `local_runtime_message_rows.id=23645`：

  > tickets 需要这么多吗? 不能合并

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=23645`。

- 2026-09-12T08:18:59.976000Z，user，SQLite `local_runtime_message_rows.id=24422`：

  > wp6 不对吧, 这都读一小时了

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=24422`。

- 2026-09-12T08:30:19.423000Z，user，SQLite `local_runtime_message_rows.id=24682`：

  > 不是要复用吗? 为什么还要改

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=24682`。

- 2026-09-12T13:30:14.191000Z，user，SQLite `local_runtime_message_rows.id=27516`：

  > 为什么不能多派点, 只要不依赖, 不能都派出去吗

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=27516`。

- 2026-09-13T01:43:56.999000Z，user，SQLite `local_runtime_message_rows.id=30020`：

  > 开发完成之后就进行合并 然后交付完整的 MR

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=30020`。

**观察与后续边界：** 同一 session 里同时出现“任务太细”“独立任务为什么不并行”“复用为何变重写”。这不是简单要求更多或更少 agent，而是分解没有对应到用户期望的完整交付和依赖。用户暂停某个 WP、保留其他任务继续，也显示其承担了运行时调度。实际结束转向 Windows 真机验证条件，不据此认定两个 MR 已完成。

**可以改进：** 按能独立验证的产品行为切片，先给单一 integrator 一个纵向运行路径；仅对可独立产出证据的分支并行，自动释放 ready-set，并把已有决策传给 worker。

## C04 多 MR 汇总与固定头交叉审查

会话：`mvs_c04f334a2fbb4b328d994c86f0bd1c6b`；分类：agent_lord_delegated；窗口消息：445；[完整可见文本摘录](case-evidence/mvs_c04f334a2fbb4b328d994c86f0bd1c6b.md)。

- 2026-09-10T08:19:50.680000Z，user，SQLite `local_runtime_message_rows.id=17208`：

  > 把三个已创建 MR 整合为一个 MR

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=17208`。

- 2026-09-10T09:37:48.565000Z，user，SQLite `local_runtime_message_rows.id=18802`：

  > preserve all M6 code and tests

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=18802`。

- 2026-09-10T10:50:48.257000Z，user，SQLite `local_runtime_message_rows.id=19314`：

  > 保持 Opus 5 xhigh，禁止派生或调用其他 agent/reviewer

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=19314`。

- 2026-09-10T11:58:04.009000Z，assistant，SQLite `local_runtime_message_rows.id=19807`：

  > 真实 QueueRepository + 真实 priorityFence

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=19807`。

**观察与后续边界：** 这是已在使用的强流程：唯一整合者、保护其他 worker 已交付代码、独立审查后针对原 MR 修复。最终报告明确新 head 尚未交叉审查、checker 从未启动，保留验证边界。审查抓到了 selection 层让行未穿过真实 admit transaction 的缺口，说明模块自测不足以覆盖装配。

**可以改进：** 保留独立审查，但让最便宜的真实 Queue→priorityFence→admit 测试先成为 worker 完成条件；每次只复查受改动影响的事实，避免固定头失效后重新整轮分析。

## C05 短暂 provider 故障后的同会话恢复

会话：`mvs_4f8094b2e63a41f096d8c10bb37226a5`；分类：agent_lord_delegated；窗口消息：372；[完整可见文本摘录](case-evidence/mvs_4f8094b2e63a41f096d8c10bb37226a5.md)。

- 2026-09-09T11:56:54.648000Z，user，SQLite `local_runtime_message_rows.id=14209`：

  > Continue the original task in this same session

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=14209`。

- 2026-09-09T13:36:16.654000Z，assistant，SQLite `local_runtime_message_rows.id=15077`：

  > TUI tarball 端到端产物验证 PASS

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=15077`。

**观察与后续边界：** 调度续跑明确要求先检查已有会话、worktree 和后台任务，保留进度。后续报告给出 !6680 与受影响单测/打包产物证据，并明确未跑 Electron 安装包链。该例体现恢复能力已存在；不能把所有续跑都算返工。

**可以改进：** 复用同一 endpoint、提交和已有检查结果。把恢复后是否重复安装/搜索/测试作为专项指标；只在固定头发生变化或证据缺失时补跑。

## C06 E2E 的入口和覆盖纠偏

会话：`mvs_d4af9fb602c14d2997f103f175f69717`；分类：agent_lord_delegated；窗口消息：284；[完整可见文本摘录](case-evidence/mvs_d4af9fb602c14d2997f103f175f69717.md)。

- 2026-09-11T07:02:18.453000Z，user，SQLite `local_runtime_message_rows.id=20668`：

  > 只通过 TUI（真实终端 PTY）

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=20668`。

- 2026-09-11T07:51:32.316000Z，user，SQLite `local_runtime_message_rows.id=21233`：

  > 不把文本 PASS 当作附件 PASS

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=21233`。

- 2026-09-11T08:23:02.597000Z，assistant，SQLite `local_runtime_message_rows.id=21624`：

  > G04 整体降为 **PARTIAL**

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=21624`。

**观察与后续边界：** 原验收被调度纠正为真实 TUI 入口；第二轮纠正附件覆盖、stale 计费/恢复路径和事件顺序推断。结果退回 PARTIAL/NOT_RUN，并撤回 token 近乎翻倍与微观时序结论。说明独立核验有价值，也说明最初验收矩阵未强制绑定产品入口与证据。

**可以改进：** 为每个验收项绑定入口、预期可观察量、源记录和允许的状态（PASS/PARTIAL/NOT_RUN）。runner 在入口错误或缺失证据时不能输出 PASS；依赖真实 provider 的测试与确定性集成测试分开。

## C07 安装排障扩大任务范围

会话：`mvs_ed3fb5789c7449899cde012d690472cd`；分类：agent_lord_delegated；窗口消息：196；[完整可见文本摘录](case-evidence/mvs_ed3fb5789c7449899cde012d690472cd.md)。

- 2026-09-11T08:11:52.077000Z，user，SQLite `local_runtime_message_rows.id=21448`：

  > 正常终止但没有任何有效输出时静默结束

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=21448`。

- 2026-09-11T08:30:26.537000Z，user，SQLite `local_runtime_message_rows.id=21678`：

  > 安装排障已越界且耗时过多

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=21678`。

- 2026-09-11T09:08:53.464000Z，user，SQLite `local_runtime_message_rows.id=21892`：

  > 不要再 sleep 或轮询等未来状态

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=21892`。

- 2026-09-11T09:11:50.039000Z，assistant，SQLite `local_runtime_message_rows.id=21916`：

  > 已完成并收尾

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=21916`。

**观察与后续边界：** 实际修复目标是空响应重试，期间扩展到共享 pnpm store 索引与编辑器目录权限探针，调度 SIGINT 后要求恢复 7 个缓存索引，再以现有 CI 验证交付。后续报告提供 !6832/SHA，明确 CI 与未做真实上游回放边界。SIGINT 是主动纠偏，不能计成模型故障。

**可以改进：** 给环境恢复设行为边界：复用已可用依赖与现有 CI，依赖修复触及共享目录时回到任务检查点。以“能否验证本次改动”决定下一步，避免把修工具环境变成隐含子项目。

## C08 嵌套 runtime 修复先膨胀再缩小

会话：`mvs_f6523fb596974197931841d92a3e414f`；分类：agent_lord_delegated；窗口消息：437；[完整可见文本摘录](case-evidence/mvs_f6523fb596974197931841d92a3e414f.md)。

- 2026-09-18T09:07:47.146000Z，user，SQLite `local_runtime_message_rows.id=52165`：

  > 不得只缩短锁超时

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=52165`。

- 2026-09-18T10:06:19.509000Z，user，SQLite `local_runtime_message_rows.id=52509`：

  > Continue the original task in this same session

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=52509`。

- 2026-09-19T03:07:47.262000Z，user，SQLite `local_runtime_message_rows.id=52912`：

  > without reimplementing the fix

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=52912`。

- 2026-09-19T04:02:53.470000Z，user，SQLite `local_runtime_message_rows.id=53066`：

  > 当前改动（35 files，约 +3291/-49）过多

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=53066`。

- 2026-09-19T04:10:15.664000Z，assistant，SQLite `local_runtime_message_rows.id=53096`：

  > bridge 那 1061 行协议机器

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=53096`。

**观察与后续边界：** 恢复与交付机制表现良好；架构成本却在实现后才被审视。当前报告提出约700–750行的 guard 方案，相比3291行 bridge，并指出常见嵌套 exec 仍 fail fast。这里的规模与方案是当时 agent 审核结论，本次未重读现仓确认后续实施结果。

**可以改进：** 实现前列出“复用已有能力/加一个 guard/新增协议”三种成本，先做最小实验验证需要哪个。对跨进程协议、新生命周期所有权这类复杂度明确要求一个已证实的用户场景。

## C09 owned_paths 与必要架构测试形成边界冲突

会话：`mvs_13120517afbb4af4bb588ddda243dad0`；分类：agent_lord_delegated；窗口消息：582；[完整可见文本摘录](case-evidence/mvs_13120517afbb4af4bb588ddda243dad0.md)。

- 2026-09-22T20:03:25.072000Z，user，SQLite `local_runtime_message_rows.id=71527`：

  > Do not merge or cherry-pick dependency branches

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=71527`。

- 2026-09-22T22:56:09.035000Z，user，SQLite `local_runtime_message_rows.id=72631`：

  > two changed paths outside the module

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=72631`。

- 2026-09-22T23:05:28.479000Z，assistant，SQLite `local_runtime_message_rows.id=72673`：

  > owned-path-only 等价实现不存在

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=72673`。

**观察与后续边界：** worker 在冻结基线上实现 assembly，交付后因两个越界路径返工。一处是目标分支已有的 stub，另一处是新增门面导出必须同步的精确测试白名单。后续报告移除 stub 后 package typecheck 因旧基线 abstract 成员失败，lr2 自身检查通过。该例说明静态路径边界和实际依赖/验证需要不一致。

**可以改进：** planner 在分派前把架构验收文件纳入真实所有权，并验证基线可编译；下游进入执行时用依赖交付后的整合基线。尽量通过包接口/验收边界分工，避免要求 worker 既改公开导出又不能改其契约测试。

## C10 Goal v2 模块完成没有保证默认生产装配启用

会话：`mvs_973ac1224db74f25a177d275465ed8cc`；分类：agent_lord_delegated；窗口消息：1043；[完整可见文本摘录](case-evidence/mvs_973ac1224db74f25a177d275465ed8cc.md)。

- 2026-09-23T00:11:49.068000Z，user，SQLite `local_runtime_message_rows.id=72967`：

  > single final integrator

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=72967`。

- 2026-09-23T02:16:32.789000Z，user，SQLite `local_runtime_message_rows.id=73666`：

  > Diagnose the complete job traces

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=73666`。

- 2026-09-23T04:27:01.759000Z，user，SQLite `local_runtime_message_rows.id=74288`：

  > production Goal composition gap is not a new scope item

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=74288`。

- 2026-09-23T07:05:16.365000Z，assistant，SQLite `local_runtime_message_rows.id=75479`：

  > Environment banner is stale

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=75479`。

**观察与后续边界：** 调度明确指出默认 Goal capability 仍 disabled，是原 assembly 义务未交付，要求真实 production adapter 与生命周期接线。之后仍在探索接口，最后可见工具 cd packages/goal 报 No such file or directory。此 MCode session 内没有最终交付，但跨端关联已发现 Claude session `2d2b5c29-72bd-4513-bdd7-cff795e5f5ad` 于 2026-09-23 07:09Z 明示接续并随后给出交付声明（见 `../claude/analysis.md` C13，原 `/Users/minimax/.claude/projects/-Users-minimax--codex-state-agent-lord-worktrees-goal-v2-feat-mr-mcode-20260921/2d2b5c29-72bd-4513-bdd7-cff795e5f5ad.jsonl` L17/L93 接续，L5216 交付声明；本地失败与CI结果须分开）。因此这里只能说单端没有终局，不能说任务未完成；也不能把工具目录错误推导为全部架构根因。

**可以改进：** 在大并行改造开始前建立最薄默认生产链路测试，明确无注入运行时 Goal 必须可用；之后模块迁移持续保持这一条红绿信号。integrator 早运行，持续检查默认 composition，而非最后把模块相加。

## C11 六模块跨仓整合与 CI 等待

会话：`mvs_68c510859bf74d39ac455693c55c415a`；分类：agent_lord_delegated；窗口消息：206；[完整可见文本摘录](case-evidence/mvs_68c510859bf74d39ac455693c55c415a.md)。

- 2026-09-16T06:53:18.856000Z，user，SQLite `local_runtime_message_rows.id=47288`：

  > worker 全绿不等于可以合入

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=47288`。

- 2026-09-16T07:56:44.290000Z，assistant，SQLite `local_runtime_message_rows.id=48133`：

  > do a final CI check

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=48133`。

- 2026-09-16T08:11:38.419000Z，assistant，SQLite `local_runtime_message_rows.id=48219`：

  > newly failed after a docs-only merge

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=48219`。

- 2026-09-16T08:12:07.531000Z，assistant，SQLite `local_runtime_message_rows.id=48226`：

  > never reached typecheck

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=48226`。

**观察与后续边界：** 整合任务明确给两个 worktree、唯一整合责任、6模块来源，属于合理分工。最后可见 CI 失败发生 pnpm install、未到 typecheck，agent 决定重试；本记录没有最终报告。不能把这次基础设施问题当代码测试失败。文档合并后的 CI 追踪也提示验证触发需按实际 diff，而当前全局已有 docs-only 不追CI规则。

**可以改进：** 保存 checks→SHA→影响路径的映射，复用有效结果；依赖安装失败按基础设施单列，避免重启整条验证；让当前 docs-only 规则由执行入口识别，不依赖长提示词中途提醒。

## C12 视频迭代需要真正的视觉闭环

会话：`mvs_a08618b5e6e94310aa0e8f43503d051f`；分类：interactive_or_unclassified；窗口消息：499；[完整可见文本摘录](case-evidence/mvs_a08618b5e6e94310aa0e8f43503d051f.md)。

- 2026-09-20T11:30:17.742000Z，user，SQLite `local_runtime_message_rows.id=62955`：

  > 排名超过 GLM 5.3 max

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=62955`。

- 2026-09-20T11:48:01.806000Z，user，SQLite `local_runtime_message_rows.id=63221`：

  > 插入速度有点快

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=63221`。

- 2026-09-20T12:17:18.010000Z，user，SQLite `local_runtime_message_rows.id=63804`：

  > 我图片这个是水平排列, 你为什么是垂直排列

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=63804`。

- 2026-09-20T12:28:08.235000Z，user，SQLite `local_runtime_message_rows.id=63976`：

  > 模型保留颜色

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=63976`。

- 2026-09-20T12:59:14.056000Z，assistant，SQLite `local_runtime_message_rows.id=64486`：

  > 模型无图像视觉能力

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=64486`。

- 2026-09-20T13:00:12.801000Z，assistant，SQLite `local_runtime_message_rows.id=64498`：

  > 视频已渲染完成并通过成片验证

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=64498`。

**观察与后续边界：** 用户先后纠正速度、横竖布局、后半空白、模型色和移动路径。agent 最后用 ffprobe+像素聚类验证几何，仍明确模型无图像视觉能力。几何信号有价值，但不足以证明视觉语义或审美；这是可借 Lauren 操作真实产品并看到结果的直接案例。

**可以改进：** 选有图像输入的验证 agent，在布局原型、运动中帧、最终帧与成片四个点核对原参考；把方向、颜色、最终排序先变成短验收表，避免渲染后由用户承担全部视觉判断。

## C13 已经把重复问题变成工具和 CI

会话：`mvs_20a4a71feb5945f990e3c38388d0f875`；分类：interactive_or_unclassified；窗口消息：215；[完整可见文本摘录](case-evidence/mvs_20a4a71feb5945f990e3c38388d0f875.md)。

- 2026-09-21T12:47:49.694000Z，user，SQLite `local_runtime_message_rows.id=65167`：

  > skill 的目前描述是不是太多了

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=65167`。

- 2026-09-21T12:55:57.137000Z，user，SQLite `local_runtime_message_rows.id=65207`：

  > 整体扫描下列出优化项

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=65207`。

- 2026-09-22T03:41:16.032000Z，assistant，SQLite `local_runtime_message_rows.id=66193`：

  > schemas round-trip 测试

  来源：`/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite#local_runtime_message_rows`；规范化`messages.jsonl`字段`line=66193`。

**观察与后续边界：** 后续报告称修复 schema 漂移、拆分协议文档、加 docs 链接与 skill体积门禁，交付 PR34；335/336 的测试结果没有被写成全绿，说明边界意识已较成熟。这里与 Lauren 把重复错误转成可执行约束一致，不需要再加一层通用流程。

**可以改进：** 优先继续这条路线：当同类协调错误重复发生，改已有工具的返回结构/自动检查；定期删除已由代码保证的提示词。选择能阻止真实已发生错误的 gate。
