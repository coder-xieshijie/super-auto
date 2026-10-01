#!/usr/bin/env bash
# M2 接口入口场景：verify.md S02、S05、S08、S11、S37，命令照抄各场景步骤。
# 用法（agent-archon worktree 根目录，HEAD 为被测提交、已 prepare）：
#   bash <tools>/m2-api.sh <S02|S05|S08|S11|S37> <尝试名> [S02 的升级前数据 runId]
# 证据：<M2_ROOT>/<场景>/<尝试名>/。每个场景起自己的接口实例，结束 down。
set -u
source "$(dirname "${BASH_SOURCE[0]}")/m2-lib.sh"
SCN=$1
ATTEMPT=$2
m2_begin "$SCN" "$ATTEMPT"

goal_get() { vr api GET $API/session/$1/goal --save "$2"; }

case $SCN in
S05)
  m2_up runtime --fault || exit 1
  m2_smoke_api
  vr fault log --role main --event attempt --tail 5 --save fault-smoke >/dev/null
  OBJ="Create files b1.txt, b2.txt, b3.txt, b4.txt one at a time in this single turn, each containing its own number."
  S=$(m2_session "s05 faults" s05-session); echo "$S" >"$OUT/session"
  # 规则 A：第 2 次主执行请求的第一次 attempt 返回可重试 500；规则 B：第 4 次主执行请求返回 50113
  vr fault add --session "$S" --nth 2 --preset retryable-500 --attempts first --note "S05 rule A" --save fault-rule-a >/dev/null
  vr fault add --session "$S" --nth 4 --preset upstream-50113 --note "S05 rule B" --save fault-rule-b >/dev/null
  # 1
  m2_goal_create "$S" "$OBJ" s05-create >/dev/null
  # 2
  vr poll $API/session/$S/goal --until 'goal.status=complete|paused|blocked|budget_limited|usage_limited' --show "$SHOW" --interval 2 --timeout 420 --save s05-run >/dev/null
  goal_get "$S" s05-goal >/dev/null
  vr snapshot --session "$S" --save s05 >/dev/null
  vr fault log --session "$S" --tail 200 --save fault-s05 >/dev/null
  # 3 新会话、同一 Goal、无故障规则；第 2 次请求进行中暂停
  S2=$(m2_session "s05 cancel" s05-cancel-session); echo "$S2" >"$OUT/session-cancel"
  m2_goal_create "$S2" "$OBJ" s05-cancel-create >/dev/null
  deadline=$(( $(date +%s) + 120 )); inflight=""
  while [ "$(date +%s)" -lt "$deadline" ]; do
    inflight=$(vr fault log --session "$S2" --role main --tail 200 | python3 -c 'import json,sys
d=json.load(sys.stdin); lines=d.get("lines") or []
started={e["attemptId"]:e for e in lines if e.get("event")=="attempt"}
ended={e["attemptId"] for e in lines if e.get("event")=="attempt-end"}
open_=[e for a,e in started.items() if a not in ended and (e.get("n") or 0)>=2]
print(open_[0]["attemptId"] if open_ else "")')
    [ -n "$inflight" ] && break
    sleep 0.3
  done
  echo "$inflight" >"$OUT/cancel-inflight-attempt"
  vr api PATCH $API/session/$S2/goal --data '{"status":"paused"}' --save s05-cancel-pause >/dev/null
  m2_log "paused while attempt $inflight in flight"
  vr poll $API/session/$S2/goal --until goal.reserved_requests=0 --hold 5 --show "$SHOW,goal.reserved_requests" --interval 1 --timeout 60 --save s05-cancel-settled >/dev/null
  goal_get "$S2" s05-cancel-goal >/dev/null
  vr snapshot --session "$S2" --save s05-cancel >/dev/null
  vr fault log --session "$S2" --tail 200 --save fault-s05-cancel >/dev/null
  m2_down
  ;;
S08)
  m2_up runtime || exit 1
  S=$(m2_session "s08 epoch" s08-session); echo "$S" >"$OUT/session"
  # 1
  m2_goal_create "$S" "Create files c1.txt to c4.txt one at a time in this single turn, each containing its own number." s08-create >/dev/null
  goal_get "$S" s08-v0 >"$OUT/v0.json"
  GID=$(jget "d['body']['goal']['goal_id']" <"$OUT/v0.json")
  V0=$(jget "d['body']['goal']['updated_at']" <"$OUT/v0.json")
  R0=$(jget "d['body']['goal'].get('requests_used',0)" <"$OUT/v0.json")
  echo "{\"goal_id\":\"$GID\",\"v0\":$V0,\"requests_used_v0\":${R0:-0}}" >"$OUT/v0-summary.json"
  # 2 请求数比 v0 时多 2 以上且 Goal 仍 active
  want=$(python3 -c "import sys; r=int('${R0:-0}' or 0); print('|'.join(str(i) for i in range(r+2, r+40)))")
  vr poll $API/session/$S/goal --until "goal.requests_used=$want" --show "$SHOW,goal.updated_at" --interval 1 --timeout 180 --save s08-grown >"$OUT/grown.json"
  # 3
  BODY=$(python3 -c 'import json,sys; print(json.dumps({"objective":"Create files c1.txt to c5.txt one at a time in this single turn, each containing its own number.","expected_goal_id":sys.argv[1],"expected_updated_at":int(sys.argv[2])}))' "$GID" "$V0")
  vr api PATCH $API/session/$S/goal --data "$BODY" --save s08-patch >"$OUT/patch.json"
  m2_log "patch status=$(jget "d.get('status')" <"$OUT/patch.json") objective=$(jget "d['body']['goal']['objective'][:40]" <"$OUT/patch.json")"
  vr poll $API/session/$S/goal --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 420 --save s08-run >/dev/null
  vr snapshot --session "$S" --save s08 >/dev/null
  m2_down
  ;;
S11)
  M2_UP_CONFIG=$(m2_config turns1 1 1) m2_up runtime || exit 1
  vr api GET /mavis/api/config --save s11-effective-config >/dev/null
  S=$(m2_session "s11 final reply" s11-session); echo "$S" >"$OUT/session"
  # 1
  m2_goal_create "$S" "This goal has no work to do. Call update_goal to mark it complete right away, then tell me in one sentence that it is done." s11-create >/dev/null
  # 2
  vr poll $API/session/$S/goal --until "$TERMINAL" --show "$SHOW" --interval 2 --timeout 420 --save s11-run >/dev/null
  goal_get "$S" s11-goal >/dev/null
  vr snapshot --session "$S" --save s11 >/dev/null
  m2_down
  ;;
S37)
  m2_up runtime || exit 1
  S=$(m2_session "s37 token budget" s37-session); echo "$S" >"$OUT/session"
  # 1 limits.md“接口”一节：token_budget 3000，poll 到 budget_limited(token) 且当前 Turn 结束
  vr api POST $API/session/$S/goal --data '{"objective":"Write a file notes.md with ten numbered one-line facts about the Rust programming language, then verify the file has exactly ten lines.","token_budget":3000}' --save limits-create >/dev/null
  vr poll $API/session/$S/goal --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 300 --save limits-run >/dev/null
  vr poll $API/session/$S --until session.status.status_type=0 --hold 5 --show session.status.status_type --interval 1 --timeout 180 --save s37-turn-ended >/dev/null
  # 2
  goal_get "$S" s37-goal >/dev/null
  vr snapshot --session "$S" --save s37 >/dev/null
  m2_down
  ;;
S02)
  FROM=$3
  m2_up runtime --from-data "$FROM" || exit 1
  SESS="$M2_ROOT/S02/baseline-data/sessions.txt"
  cp "$SESS" "$OUT/sessions.txt"
  P="$API/agent/mavis/questionnaire/pending?session_id="
  # 1 逐个接口读 Goal；读问卷会话的历史与 pending
  while read -r name sid; do
    low=$(echo "$name" | tr A-Z a-z)
    goal_get "$sid" "s02-$low-goal-after" >/dev/null
    case $name in Q1|Q2|Q3)
      vr api GET $API/session/$sid/message --save "s02-$low-history-after" >/dev/null
      vr api GET "$P$sid" --save "s02-$low-pending-after" >/dev/null ;;
    esac
  done <"$SESS"
  S_ACTIVE=$(awk '$1=="ACTIVE"{print $2}' "$SESS")
  S_BUDGET=$(awk '$1=="BUDGET"{print $2}' "$SESS")
  # 3 budget_limited：读队列，poll 60 秒 hold（先做，hold 期间 active 会话在跑）
  vr api GET $API/session/$S_BUDGET/queue --save s02-budget-queue-after >/dev/null
  vr api GET $API/session/$S_BUDGET/message --save s02-budget-history-before-hold >/dev/null
  vr poll $API/session/$S_BUDGET/goal --until goal.status=budget_limited --hold 60 --show "$SHOW,goal.updated_at" --interval 2 --timeout 90 --save s02-budget-hold >/dev/null
  vr api GET $API/session/$S_BUDGET/message --save s02-budget-history-after-hold >/dev/null
  vr api GET $API/session/$S_BUDGET/queue --save s02-budget-queue-after-hold >/dev/null
  # 2 active：poll 到离开 active
  vr poll $API/session/$S_ACTIVE/goal --until 'goal.status=complete|paused|blocked|budget_limited|usage_limited' --show "$SHOW" --interval 3 --timeout 600 --save s02-active-run >/dev/null
  # 4
  while read -r name sid; do
    low=$(echo "$name" | tr A-Z a-z)
    goal_get "$sid" "s02-$low-goal-final" >/dev/null
    vr snapshot --session "$sid" --save "s02-$low" >/dev/null
  done <"$SESS"
  # 升级后的存储读数（问卷的 goalId 与期限、队列）：保留数据停机，读完删除数据目录
  m2_down --keep-data
  node "$V" db --data "$RID" --query "SELECT request_id, session_id, status, answered_at, injected_at, json_extract(request_json,'$.goalId') AS goal_id, json_extract(request_json,'$.expiresAt') AS expires_at, json_extract(request_json,'$.purpose') AS purpose FROM questionnaire_requests ORDER BY created_at" --save s02-post-questionnaires >"$OUT/post-upgrade-questionnaires.json" 2>>"$OUT/steps.stderr.log"
  node "$V" db --data "$RID" --query "SELECT id, session_id, item_id, status, client_request_id, json_extract(data_json,'$.message.origin') AS origin FROM local_runtime_queue_items ORDER BY id" --save s02-post-queue >"$OUT/post-upgrade-queue.json" 2>>"$OUT/steps.stderr.log"
  node "$V" db --data "$RID" --query "SELECT goal_id, session_id, status, status_reason, tokens_used, turns_used, time_used_seconds, token_budget, usage_recovery_at_ms, updated_at_ms FROM local_runtime_v2_goals ORDER BY created_at_ms" --save s02-post-goals >"$OUT/post-upgrade-goals.json" 2>>"$OUT/steps.stderr.log"
  HOME_VA=${VERIFY_ARCHON_HOME:-$(node -e "console.log(require('os').tmpdir())")/verify-archon}
  rm -rf "$HOME_VA/$RID/data" "$HOME_VA/$RID/workspace"
  ;;
*) echo "unknown scenario $SCN" >&2; exit 2 ;;
esac
m2_log "done"
