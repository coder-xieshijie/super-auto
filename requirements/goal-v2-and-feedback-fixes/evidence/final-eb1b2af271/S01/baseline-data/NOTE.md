# S01 旧数据（基线 d770f05f30）

- 检出 gv2-verify-tools，detached 在 d770f05f30，工作区干净。命令：`M2_BASELINE_UP_EXTRA=--allow-stale bash $T/m2-baseline-data.sh s01`。runId 为 `20261001-233215-00aeb4`，实例的 `data/`、`workspace/` 已保留，供 `m2-electron.sh S01 <尝试> 20261001-233215-00aeb4` 使用。
- 为什么加 `--allow-stale`：第一次 `up` 被拒（`_invalid/baseline-data-attempt1-stale-build/up.json`），原因是 packages/config 和 packages/shared 的源码 mtime 比构建新。这两个包的构建产物来自 22:53 在同一提交 d770f05f30 上执行的 `prepare runtime`。之后检出切到 wip/gv2-v1 又切回来，期间没有重新构建，源码 mtime 因此更新。23:30 再次执行 `prepare runtime` 时，`tsc --build` 判断内容没有变化，没有重写产物。核对结果：`dist/global-events.d.ts` 里没有 be34cd7334 新增的 `requestsUsed`、`accountingVersion`、`GlobalThreadGoalRequestAccounting`，构建内容与 d770f05f30 的源码一致；config 在两个提交之间只差一行注释。
- 升级前读数（`pre-upgrade.json`）：paused / paused(user_requested)，turns_used 6（直接写 legacy 表安排），tokens_used 22486，token_budget 为 null。配置为 /tmp/gv2-cfg/turns10.yaml（defaultMainTurns=10，graceSteps=1）。
- 实例 auth-check：contentSafety401 0，electronAuthLost 0。
