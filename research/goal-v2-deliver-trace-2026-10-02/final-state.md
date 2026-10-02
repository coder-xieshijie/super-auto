# Trace 末端：交付到了哪里，接下来缺什么

记录时间：2026-10-02，Asia/Shanghai。原始 trace 截止 01:50:03；GitLab 快照为 10:26:59。这里记录执行状态和证据缺口，不代替 owner 续跑、不修改产品或验收结果。

## 1. 中断的直接证据

主会话 `062c5e8b-f847-4f5a-81b3-a4291994c2b5` 原文件 L19881，时间 01:50:03.314：

> Failed to authenticate. API Error: 403 预算不足，请申请或调整预算后重试。

其 Electron C 子任务 `agent-a232ae546f632eb34` L854 在 01:50:01.234 出现完全相同的错误。原文件路径和哈希见 [manifest](manifest.json)，主会话导航见 [deliver 时间线](timelines/deliver.md)。

这是 **Claude Code 外层执行服务拒绝请求**，不是被测产品 Goal 达到请求/额度上限，也不是完成答复。错误文字包含 authenticate 和预算两层信息；没有服务端账单与额度资料，不能进一步确认是哪个预算桶、谁应调整、是否与当晚路由变更有关，更不能把 token 统计直接换算成费用。没有证据证明用户在此时取消了任务。

在此之前，主记录 21:09–21:46 有 18 条去重后的 `api_error`（500 无可用渠道、429 无 OAuth 账号池、503 暂不可用等），其后继续产出了代码、证据和提交，所以不能把这整个 37 分钟窗口都算停机。

## 2. 平台、代码、验证分别报告

| 层次 | 本轮核对的状态 | 依据与界限 |
|---|---|---|
| MR | !7595 opened、Draft；`not_approved` | [GitLab 快照](mr-snapshot.json)；没有取消 Draft、合入或发布 |
| 已推送产品代码 | `eb1b2af2716b70ff68fbc78cc802a13864ed7052` | MR 的 source SHA |
| 本地 owner HEAD | `b62d4f0af02554733a1e82a1eb6d3f9878204f21`，工作区干净 | 比 MR 多一个 7 文件的文档提交；diff 没有产品代码 |
| 配套 IDL | weaver/idl!13599 opened，`204400c9a…` | 开发阶段按 feature IDL 生成符合用户约定；不能因 IDL 未合入而判本阶段违规。正式合入前仍需用户合 IDL，再用 main 生成对齐 |
| 第一轮最终自验 | `d5bc1acab4`，5 条 lane 跑完 | 发现 S25 真缺陷、M6 恢复组合缺陷；后续产品已改变，不能整份报告原样当新 head 通过 |
| 第二轮自验 | `eb1b2af271`，4 条 lane；3 条已汇报、C 线未交最终报告 | 后续另开 S02 fixture 重建任务，已汇报通过；C 线实际已有多数材料，但 X1 尚未收敛 |
| R103 最终并行稳定性 | 旧版 V1 有 20.8 分钟、159 个 Goal 的记录；新 head 的最后一次计划未找到完成记录 | 普通场景同时跑不能自动替代指定 20 分钟验收 |
| 最终另一家模型独立验证 | 未找到启动最终验证与 PASS 的证据 | q1–q5 是决策咨询，core-spec 的三轮是文档查漏；二者都不是最终产品独立验证 |
| CI | pipeline 945337 failed | 在 merge-result `4585529c…` 上；2 个失败 job，详见 [CI 摘录](ci-evidence.md) |
| 交付收口 | 未完成 | MR 描述仍写“当前只有文档与术语改动，尚未运行产品验证”，plan 的第二轮任务仍勾为未完成 |

CI 的具体失败：`check:unit:local-runtime-v2` 在执行单元测试前的 `check:dead-code` 报 6 个未用导出和 2 个未用类型；`check:fast:lint` 在 TUI 新增测试报 `no-lone-blocks`。不能把这两个失败说成“都在等 IDL 合入”或“都是基线已有”。本轮只读诊断，没有触发或修复 CI。

## 3. 第二轮有哪些有效结果

以下是 trace 和已有证据的对照，不重新运行产品，不把单个检查点通过改写成整个需求通过。

| 子任务 / 场景 | 已见结果 | 仍需保留的边界 |
|---|---|---|
| Electron A | S01、S16 hold/nohold、S17、S19、S20 通过 | S01 分析器曾把“至多一次收尾”写成“必须一次”；修正后按现存证据通过，但本轮没有触发的收尾工具丢弃路径仍不能声称本轮验证过 |
| Electron B | S25 三次有效运行都回答 7、未继续旧 Goal；S21、S26、S28、S10 通过 | 三次是有限样本，不是提示词保证；应保留第一轮两次失败和代码修复因果链 |
| S39 | owner 经 Codex q5 讨论，采用 f1 的功能读数 | 三次均有 workspace 外列目录事件；功能 PASS 与 incident 分开，不能宣传为执行全程没有越界；[q5](../../requirements/goal-v2-and-feedback-fixes/evidence/decisions/q5-codex.md)还指出，f3 发生在前提满足前本身并不能证明污染了结果 |
| TUI + API | S18、S30、S40、S09、S34 通过 | S02 最初失败因旧数据重置时间已过，不能拿这一轮作升级保持的有效判定 |
| S02 重建 | f4 8/8，通过时距离额度重置约 52 分钟 | `M2_S02_RESET_IN` 已可配置，但默认仍为 3600 秒；下一次验证必须重新核实余量 |
| Electron C / S24 | 已有 f1 `checks.json` | 整条 lane 没有最终报告；不要以“还在跑”覆盖已落盘的材料，也不要因此跳过 X1 问题 |
| Electron C / X2 | f1 界面一项 UNVERIFIED，f2 6 项 PASS | f2 的 UI 判断包含单独截图观察，不是只凭 API 失败；原始材料在 X2/f2，需由 owner 收口、最终验证者复核 |
| Electron C / X1 | f1–f4 都有恢复成功读数，但都未命中预期队列暂停状态；f3 另有约 300 秒窗口 | 不能把四次恢复成功等同于“修复的 user-stop 队列路径已实测通过” |

## 4. X1 是当前最需要收敛的验证问题

来源：[X1/f1](../../requirements/goal-v2-and-feedback-fixes/evidence/final-eb1b2af271/X1/f1/checks.json)、[f2](../../requirements/goal-v2-and-feedback-fixes/evidence/final-eb1b2af271/X1/f2/checks.json)、[f3](../../requirements/goal-v2-and-feedback-fixes/evidence/final-eb1b2af271/X1/f3/checks.json)、[f4](../../requirements/goal-v2-and-feedback-fixes/evidence/final-eb1b2af271/X1/f4/checks.json)，以及 [分析器](../../requirements/goal-v2-and-feedback-fixes/tools/x-analyze.py)。这些文件本轮均未改。

四次的共同事实：

- 停止后 Goal 为 `paused(user_requested)`；点击继续后约 118–151 ms 出现新的 `goal.turn_bound`，最后完成。
- 但要求命中的状态“`queue pause.cause=user-stop` 且队列中有这个 Goal 的 continuation”全部 FAIL：`pause=null`、队列为空。
- 分析器把 `userStopPathExercised=false` 放进 detail 和一个 FAIL 检查，却仍可能给 `valid=true`、`precondition.ok=true`。这并非已产生总 PASS，但说明“运行有效”与“目标代码路径已命中”不是同一个标志。
- f3 的 `longestIdleMs=300094`，时间与一个 pending Goal 问卷的 300 秒存活窗口吻合。子任务 L787 开始增加问卷观察，尚未完成原因判定就遇到外层 403。

应分别处理两件事：先确保目标队列状态在点击前真的成立，才谈该修复的运行时覆盖；再单独核实 f3 的问卷期间等待投影是否违反 spec。后者目前是有证据的异常信号，不是已经确认的产品根因，也不能因为 f4 没重现就删除。

## 5. 恢复工作需要的最小入口

1. 先解决外层执行服务可用性/预算问题；本轮未调整额度、凭据或路由，也未给原会话发消息。
2. 读取 MR head、本地文档提交、现有 plan 和本文件，复用已落盘的场景结果；核对是否有本次采集之后的新运行。
3. 收敛 X1 的命中条件与 f3 问卷窗口，汇总 C 线与第二轮的全部结果；不要先从头重跑所有场景。
4. 修 CI 两项实际失败；判断新改动影响，必要的场景、质量检查和最终 R103 补齐。
5. 自验完成后发起独立验证，并把决定清单、盲区、报告 head 和证据链接写入 MR；完成条件满足再取消 Draft。
6. IDL 和主 MR 的合入保持用户既定顺序。这里是分析出的续接清单，不是本轮已执行的工作。

## 6. plan 的时间应回到证据

现有 plan 中 `669f179230` 写在 00:35、`eb1b2af271` 写在 00:50；实际 Git 作者/提交时间分别是 00:03:43、00:15:32，主会话在 00:05、00:18 已汇报推送。plan 紧接着又写“00:2x 构建、00:30 启动”，时间出现倒置。此前 11:50 已纠正过估算时间，这次又复现了。最小改进是记录 Git/运行器时间，不能把写报告的估计时间当实际发生时间。
