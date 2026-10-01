**V1 并行实跑 parallel-run1（R103）**

结论：通过。3 个 Electron、1 个接口、1 个 TUI 同时运行 20.8 分钟（20:26:30–20:47:21），五个实例的 `contentSafety401` 与 `electronAuthLost` 都是 0；刷新记录在本轮没有新增任何一行，所以没有 Electron 运行期间的刷新；`http429` 五个实例都是 0。

- **代码：** gv2-verify-tools，`wip/gv2-v1` be34cd7334，工作区干净；`prepare runtime tui electron` rc=0；verify-archon 脚本测试 61/61 通过（49 + `fault-presets` 12）。
- **启动：** 五个实例经同一把锁 `/tmp/gv2-v1-up.lock` 依次启动、间隔 6 秒。Electron 用 `--auth-lease 30`：每个 Electron 从启动到 down 约 21–22 分钟，超过默认租约 20 分钟，按 SKILL.md 给更长的租约。启动时登录代次 275，剩余约 57 分钟，三个 Electron 都直接使用、没有等待（up.json 无 `authWaitedMs`）。
- **实例清单：** instances.json（runId、端口、就绪与开始 down 的时间）。
- **工作负载：** 每个实例到截止时刻前反复创建简单 Goal（`Write the numbers 1 to 3 into count-N.txt…`）跑到终态。
  - 接口 38 个、Electron 1/2/3 分别 35/32/31 个，全部 `complete(verifier_met)`。
  - TUI：见下文“TUI 工作进程的问题”。
  - 按 runtime 日志里的 `agent_turn_setup_stage_started` 统计，窗口内每个实例每分钟都有新 Turn 开始；只有 TUI 在 20:30 那一分钟没有（turns-per-minute.txt）。
  - Electron 输入框每次都读回核对，没有不一致（没有 input-mismatch.jsonl）。每个 Goal 结束后检查会话历史或屏幕里有没有 workspace 以外的路径，没有触发。
- **auth-check.json**（verify-archon `down` 写出；super-auto 的 m2-lib 读它，日志 `source=verify-archon`）：

| 实例 | runId | contentSafety401 | electronAuthLost | http429 | refreshesDuringRun | refreshesWhileElectronRunning |
|---|---|---|---|---|---|---|
| api | 20261001-202519-7aca50 | 0 | 0 | 0 | 0 | 0 |
| tui | 20261001-202545-eea415 | 0 | 0 | 0 | 0 | 0 |
| electron-1 | 20261001-202555-2addb1 | 0 | 0 | 0 | 0 | 0 |
| electron-2 | 20261001-202610-bed173 | 0 | 0 | 0 | 0 | 0 |
| electron-3 | 20261001-202529-050074 | 0 | 0 | 0 | 0 | 0 |

- **刷新记录：** `auth-refresh.log.copy` 只有探针 probe1 那一行（20:23:25，Electron 2 在探针的 Electron 1 结束后刷新，`electronsRunning []`）。本轮窗口内没有新行。
- **时间线：** timeline.jsonl 记录每个实例的 up、每个 Goal 的开始与结束、down，时间为 Unix ms。各工作进程的日志在 worker-*.log，脚本在 _scripts/。
- **收尾：** 五个实例都已 down，`list` 没有存活实例，进程和端口都已释放。

**覆盖说明：** 本轮登录剩余时间一直足够，没有出现需要刷新的时刻，所以“有 Electron 运行时推迟刷新”和“接口实例被拒后重读”没有在这一轮被触发。这两条在探针 probe1 实际触发过：Electron 启动方等别的 Electron 结束后才刷新；接口实例被拒后 1 秒内重读。接口实例在剩余不足 10 分钟、又有 Electron 在跑时进入 `defer`，这条路径两轮都没有实跑到，只有脚本测试覆盖。

**TUI 工作进程的问题（工具问题，不影响登录判定）：**
- `worker.sh` 的 TUI 循环用 `tui wait --text "Goal complete"` 判断完成。屏幕上留着上一个 Goal 的“Goal complete”，于是第 3–44 个 Goal 每 1.2 秒就发一次 `/goal`。
- 20:28:47 换成 `tui-loop.sh`，但 Goal 在校验期间仍是 Active，第 101–104 个 `/goal` 只是更新了 objective。
- 20:31:26 换成 `tui-loop2.sh`，又把“Verifying the result”当成了结束，第 201–203 个同上。
- 20:35:22 起换成 `tui-loop3.sh`，按底部横幅判定，第 301–324 个都正常跑到“Goal complete”。
- 前面那些 `/goal` 落在同一个仍在运行的 Goal 上，模型请求一直在发；日志和 timeline 里的 `tui-loop*-takeover` 记录了每次替换。
