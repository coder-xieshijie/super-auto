**V1 探针 probe1（gv2-verify-tools，wip/gv2-v1 be34cd7334，工作区干净）**

结论：通过。Electron 运行期间没有刷新；需要刷新的 Electron 启动方等到 Electron 1 结束才刷新；接口实例的请求被拒后 1 秒内从共享登录重读，同一请求随后得到回复；刷新记录含时间、触发实例、新旧代次。

实例：接口 20261001-201409-22b4b4（api/），Electron 1 20261001-201504-1174b9（electron-1/，默认 `--auth-lease 20`），Electron 2 20261001-202224-4afad3（electron-2/，`--auth-lease 60`，用来强制出现一次刷新需求）。时间线见 timeline.txt（Unix ms）。

1. 接口实例启动时登录代次 274，剩余约 50 分钟，`lastAction: reuse`。Electron 1 默认租约 20 分钟，剩余足够，直接使用，没有刷新。
2. 两个实例并行各跑一个简单 Goal，都是 `complete(verifier_met)`（electron-1 的 goal 1 没有发出：首次启动弹窗没关，输入框读回为空，见 tool-invalid-goal1；关弹窗后 goal 2 完成）。期间 auth-refresh.log 不存在（没有任何刷新）。
3. Electron 1 运行中启动 Electron 2（租约 60 分钟，剩余不够，必须刷新）：Electron 2 的 state.json 出现 `authWait.electrons = [Electron 1]`，没有刷新。等了 60263 ms 后停掉 Electron 1，Electron 2 才刷新。
4. 刷新记录唯一一行：`at 2026-10-01T12:23:25.821Z`、`runId` 为 Electron 2、`kind electron`、`reason electron-lease`、`waitedMs 60263`、`electronsRunning []`、`generation 275`、`previousGeneration 274`，不含 token（副本 auth-refresh.log.copy）。
5. 刷新后接口实例仍持有代次 274，立即发一条 PONG 请求：内容审核用旧 token 返回 401（20:23:26.886），同一毫秒级 server.log 记 `managed auth re-read after rejection` generation 275（20:23:26.887）；回复为 PONG。之后 doctor 的 auth 为 generation 275、`rejected 1`、`reread 1`、`refreshes 0`（api/reread-*、api/reread-refresh-seen-at）。

auth-check.json（verify-archon down 写出）：

| 实例 | contentSafety401 | electronAuthLost | http429 | refreshesDuringRun | refreshesWhileElectronRunning |
|---|---|---|---|---|---|
| api | 1（第 5 步有意制造的那次拒绝） | 0 | 0 | 1 | 0 |
| electron-1 | 0 | 0 | 0 | 0 | 0 |
| electron-2 | 0 | 0 | 0 | 1（自己启动时的刷新） | 0 |

三个实例都已 down，`list` 无存活实例。
