# S02 命令记录（被测 eb1b2af271）

环境：`source /tmp/gv2-final2/env.sh`（设 `REQ`、`T`、`M2_ROOT`、共享启动锁 `/tmp/gv2-final2-up.lock`，cd 到 gv2-tests）。

## f1–f3（作废，证据保留）

- 旧数据 r1：runId `20261001-225409-10fc0d`（10-01 22:54 在 d770f05f30 上生成，USAGE 规则 `--reset-in 3600`，重置时间 10-01 23:54:35）。目录已改名为 `baseline-data-r1-expired/`。
- `bash $T/m2-api.sh S02 f1|f2|f3 20261001-225409-10fc0d`；`python3 $T/m2-analyze.py S02 f1|f2|f3`。
- f1、f3：`valid=false`，`invalidReason`=“旧数据的额度重置时间已过，前提不成立”（10-02 在两个 checks.json 里补标）。f2：内容审核 401，原本已作废。

## 旧数据 r2（2026-10-02 01:27–01:31）

```bash
cd /Users/minimax/code/mm/worktrees/agent-archon/gv2-verify-tools
git checkout --detach d770f05f30          # 原在 wip/gv2-v1 be34cd7334，工作区干净
git rev-parse HEAD                         # d770f05f30684417fbede1791371a7a392a90840
node .agents/skills/verify-archon/scripts/verify-archon.mjs prepare runtime   # rc=0，_logs-r2/prepare-d770.log
mv $M2_ROOT/S02/baseline-data $M2_ROOT/S02/baseline-data-r1-expired
bash $T/m2-baseline-data.sh s02            # up 被拒：build older than sources → _invalid/baseline-data-r2-attempt1-stale-build/
M2_BASELINE_UP_EXTRA=--allow-stale bash $T/m2-baseline-data.sh s02   # runId 20261002-012823-666f5d，_logs-r2/baseline-s02-a2.log
python3 $T/m2-s02-arrange-budget-item.py 20261002-012823-666f5d mvs_4654e39db387406b8b42c7dc0899b257 $M2_ROOT/S02/baseline-data
cp -R $M2_ROOT/S02/baseline-data $M2_ROOT/S02/baseline-data-r2
git checkout wip/gv2-v1                    # 生成完毕后还原（be34cd7334）；构建产物仍是 d770f05f30 的
```

- `--allow-stale` 理由：packages/config、packages/shared 源码 mtime 因检出切换晚于构建；`prepare runtime` 后 tsc 判断无变化未重写；`packages/shared/dist/global-events.d.ts` 不含 be34cd7334 新增的 `requestsUsed`/`accountingVersion`/`GlobalThreadGoalRequestAccounting`，构建内容与 d770f05f30 一致。
- `--reset-in`：脚本写死 `--reset-in 3600`，不支持参数，按原样使用。

## 时间前提核对（只读）

```bash
sqlite3 -readonly -json $TMPDIR/verify-archon/20261002-012823-666f5d/data/v2/sqlite/runtime-state.sqlite \
  "SELECT session_id, goal_id, status, status_reason, usage_recovery_at_ms, ... FROM local_runtime_thread_goals WHERE status='usage_limited'"
```

读数（`f4/precheck-usage-recovery.json`）：`usage_recovery_at_ms=1790879327000`（10-02 02:28:47），读于 01:32:06，剩余 56.7 分钟（≥10 分钟，满足）。

## f4（有效，8/8 PASS）

```bash
bash $T/m2-api.sh S02 f4 20261002-012823-666f5d    # gv2-tests eb1b2af271；runId 20261002-013220-c84f2b，01:32:20–01:36:14
python3 $T/m2-analyze.py S02 f4
python3 $T/final-summary-md.py $M2_ROOT/S02/f4 /tmp/gv2-final2/lane-s02r/f4-extra.md
```

## 时间敏感说明

S02 的 USAGE 前提依赖旧数据里的可信重置时间：从基线生成 USAGE Goal 起算 `--reset-in` 秒（当前 3600）。升级实例必须在这之前启动并完成读数，否则 v2 按 R55 启动即自动恢复，USAGE 字段保持一项必然 FAIL。复验时在基线生成后立即跑 S02，运行前用上面的只读查询确认剩余时间。
