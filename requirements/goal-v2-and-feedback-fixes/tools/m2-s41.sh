#!/usr/bin/env bash
# M2 S41：固定账本样本在各消费面的投影。
# 用法（agent-archon worktree 根目录）：
#   bash <tools>/m2-s41.sh seed            # TUI 实例建一个 Goal 后暂停，保留数据停机，再直接写存储安排账本事实
#   bash <tools>/m2-s41.sh api <尝试名>     # 步骤 1、2、5（接口、事件、get_goal）
#   bash <tools>/m2-s41.sh tui <尝试名>     # 步骤 4（TUI /goal 摘要）
#   bash <tools>/m2-s41.sh electron <尝试名> # 步骤 3（Electron 横幅、token 文字、悬停）
# 种子数据的 runId 记在 <M2_ROOT>/S41/seed/runId，后三者都 --from-data 它（各自复制，互不影响）。
set -u
source "$(dirname "${BASH_SOURCE[0]}")/m2-lib.sh"
MODE=$1
SEED_DIR="$M2_ROOT/S41/seed"
OBJ_SEED="Write the numbers 1 to 3 into count.txt, one number per line, then stop."
OBJ_GET="Call get_goal once first, then write the numbers 1 to 3 into count.txt, one number per line, then stop."

case $MODE in
seed)
  m2_begin S41 seed
  # 用接口实例建种子：TUI 实例的数据目录在 --from-data 改写路径时触发 local_runtime_projects.workspace_dir 唯一约束失败
  # （第一次尝试，evidence/m2/S41/seed-attempt1-tui 与 api-run1 的 steps.stderr.log）
  m2_up runtime || exit 1
  S=$(m2_session "s41 ledger sample" s41-seed-session)
  m2_goal_create "$S" "$OBJ_SEED" s41-seed-create >/dev/null
  vr api PATCH $API/session/$S/goal --data '{"status":"paused"}' --save s41-seed-pause >/dev/null
  vr poll $API/session/$S/goal --until goal.reserved_requests=0 --hold 5 --show "$SHOW,goal.reserved_requests" --interval 1 --timeout 60 --save s41-seed-paused >/dev/null
  vr snapshot --session "$S" --save s41-seed >/dev/null
  m2_down --keep-data
  G=$(node "$V" db --data "$RID" --query "SELECT goal_id, session_id FROM local_runtime_v2_goals" 2>>"$OUT/steps.stderr.log")
  GID=$(printf '%s' "$G" | jget "d['rows'][0]['goal_id']")
  SID=$(printf '%s' "$G" | jget "d['rows'][0]['session_id']")
  echo "$SID" >"$OUT/session"; echo "$GID" >"$OUT/goal-id"
  NOW=$(now_ms)
  # 安排的账本事实（直接写存储，verify S41 前提）：历史占用 6、已确认工作请求 3、收尾 1、未知占用 1、usageIncomplete 为 true、无进行中预占
  ROWS=""
  i=0
  for spec in "work settled success 0" "work settled success 0" "work settled success 1" "grace settled success 0" "work unresolved NULL 0"; do
    set -- $spec; i=$((i+1))
    out=$([ "$3" = NULL ] && echo NULL || echo "'$3'")
    tin=$([ "$4" = 1 ] && echo 0 || echo 1000); tout=$([ "$4" = 1 ] && echo 0 || echo 100)
    ROWS="$ROWS INSERT INTO local_runtime_v2_goal_requests (request_id, goal_id, session_id, turn_id, kind, phase, attempts, outcome, input_tokens, output_tokens, cache_read_tokens, cache_write_tokens, usage_incomplete, discard_reason, created_at_ms, updated_at_ms) VALUES ('m2seed-req-$i', '$GID', '$SID', 'turn_m2seed', '$1', '$2', 1, $out, $tin, $tout, 0, 0, $4, NULL, $((NOW + i)), $((NOW + i)));"
  done
  node "$V" db --data "$RID" --sql "DELETE FROM local_runtime_v2_goal_requests WHERE goal_id = '$GID'; UPDATE local_runtime_v2_goals SET turns_used = 6, status = 'paused', status_reason = 'paused(user_requested)', execution_wait_reason = NULL, execution_wait_since_ms = NULL, execution_wait_epoch = NULL WHERE goal_id = '$GID'; $ROWS" --save s41-arrange-ledger >"$OUT/arrange.json" 2>>"$OUT/steps.stderr.log"
  node "$V" db --data "$RID" --query "SELECT request_id, kind, phase, outcome, input_tokens, output_tokens, usage_incomplete FROM local_runtime_v2_goal_requests WHERE goal_id = '$GID' ORDER BY created_at_ms" --save s41-arranged-ledger >"$OUT/arranged-ledger.json" 2>>"$OUT/steps.stderr.log"
  node "$V" db --data "$RID" --query "SELECT goal_id, session_id, status, status_reason, tokens_used, turns_used, updated_at_ms FROM local_runtime_v2_goals" --save s41-arranged-goal >"$OUT/arranged-goal.json" 2>>"$OUT/steps.stderr.log"
  m2_log "seed runId=$RID session=$SID goal=$GID"
  ;;
api)
  m2_begin S41 "api-$2"
  SEED=$(cat "$SEED_DIR/runId"); S=$(cat "$SEED_DIR/session")
  m2_up runtime --from-data "$SEED" || exit 1
  echo "$S" >"$OUT/session"
  # 1
  vr api GET $API/session/$S/goal --save s41-step1-goal >/dev/null
  # 2 改 objective（仍暂停），读随之发出的 thread_goal.updated
  vr api PATCH $API/session/$S/goal --data '{"objective":"Write the numbers 1 to 3 into count.txt, one number per line, then stop. Keep each number on its own line."}' --save s41-step2-patch >/dev/null
  sleep 2
  grep '"thread_goal.updated"' "$OUT/events.jsonl" | tail -1 >"$OUT/step2-thread-goal-updated.json"
  vr api GET $API/session/$S/goal --save s41-step2-goal-after >/dev/null
  # 5 改 objective 并恢复；等模型调用 get_goal（跑到终态），读其结果与 Inspector
  BODY=$(python3 -c 'import json,sys; print(json.dumps({"objective":sys.argv[1]}))' "$OBJ_GET")
  vr api PATCH $API/session/$S/goal --data "$BODY" --save s41-step5-objective >/dev/null
  vr api PATCH $API/session/$S/goal --data '{"status":"active"}' --save s41-step5-resume >/dev/null
  vr poll $API/session/$S/goal --until "$TERMINAL" --show "$SHOW,goal.reserved_requests" --interval 2 --timeout 420 --save s41-step5-run >/dev/null
  vr api GET $API/session/$S/goal --save s41-step5-goal >/dev/null
  vr snapshot --session "$S" --save s41-step5 >/dev/null
  m2_down
  ;;
tui)
  m2_begin S41 "tui-$2"
  SEED=$(cat "$SEED_DIR/runId")
  m2_up tui --from-data "$SEED" || exit 1
  # 打开该会话：/sessions 搜索并恢复（交互由调用方用 tui keys 完成，这里只到列表）
  vr tui screen --save s41-tui-start >/dev/null
  ;;
*) echo "unknown mode $MODE" >&2; exit 2 ;;
esac
