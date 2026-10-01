#!/usr/bin/env bash
# M2 G2 前提：在迁移前验证基线构建（d770f05f30，v1 Goal owner）上生成 S01、S02 的数据目录，down --keep-data 保留。
# 用法（agent-archon worktree 根目录，HEAD 为基线提交、已 prepare runtime）：
#   bash <tools>/m2-baseline-data.sh s01   # defaultMainTurns=10 的配置；Goal 跑几轮后暂停，停机后把 legacy 表 turns_used 写成 6
#   bash <tools>/m2-baseline-data.sh s02   # 六个状态的 Goal + 三个 Goal 问卷会话，记录升级前读数
# 输出：<M2_ROOT>/S01|S02/baseline-data/，其中 runId 是保留的数据目录所属实例，pre-upgrade.json 是升级前记录。
set -u
source "$(dirname "${BASH_SOURCE[0]}")/m2-lib.sh"
MODE=$1
P="$API/agent/mavis/questionnaire/pending?session_id="

OBJ_COUNT20="Write the numbers 1 to 20 into count.txt, one number per line, writing one number per turn and ending your turn after each number."
OBJ_COUNT3="Write the numbers 1 to 3 into count.txt, one number per line, then stop."
OBJ_SLEEP30="Run the shell command sleep 30 in the foreground, then write done.txt containing ok."
OBJ_BLOCKED="This goal cannot be done yet because the input file is missing. Call update_goal with status blocked and a short reason, then stop."
OBJ_NOTES="Write a file notes.md with ten numbered one-line facts about the Rust programming language, then verify the file has exactly ten lines."
OBJ_USAGE="Create files e1.txt, e2.txt, e3.txt one at a time, each containing its own number, then stop."
OBJ_LONG="Create files g1.txt to g8.txt one at a time, each containing its own number. After writing each file, run the shell command sleep 10 in the foreground."
OBJ_FRUIT='First call the ask_user tool exactly once with one single-choice question "Which fruit?" and two options: "Apple" (recommended, listed first) and "Banana". Do not set requiresExplicitResponse. After you get the answer, write the chosen fruit name to fruit.txt (only the name).'
OBJ_FRUIT_EXPLICIT='First call the ask_user tool exactly once with one single-choice question "Which fruit?" and two options: "Apple" (recommended, listed first) and "Banana". Set requiresExplicitResponse to true. After you get the answer, write the chosen fruit name to fruit.txt (only the name).'

goal_of() { vr api GET $API/session/$1/goal --save "$2"; }

if [ "$MODE" = s01 ]; then
  m2_begin S01 baseline-data
  M2_UP_CONFIG=$(m2_config turns10 10 1) m2_up runtime || exit 1
  S=$(m2_session "s01 legacy" s01-session); echo "$S" >"$OUT/session"
  m2_goal_create "$S" "$OBJ_COUNT20" s01-create >/dev/null
  # 跑到 turns_used>=4 后暂停（停机后把 turns_used 安排为 6）
  vr poll $API/session/$S/goal --until 'goal.turns_used=4|5|6|7|8' --show "$SHOW" --interval 2 --timeout 420 --save s01-run >/dev/null
  vr api PATCH $API/session/$S/goal --data '{"status":"paused"}' --save s01-pause >/dev/null
  vr poll $API/session/$S/goal --until goal.status=paused --hold 5 --show "$SHOW" --interval 1 --timeout 60 --save s01-paused >/dev/null
  vr snapshot --session "$S" --save s01-before-arrange >/dev/null
  m2_down --keep-data
  # 安排前提（verify S01：可直接写 legacy 表安排 turns_used=6）
  node "$V" db --data "$RID" --sql "UPDATE local_runtime_thread_goals SET turns_used = 6, status = 'paused', status_reason = 'paused(user_requested)' WHERE session_id = '$S'" --save s01-arrange-turns6 >"$OUT/arrange.json" 2>>"$OUT/steps.stderr.log"
  node "$V" db --data "$RID" --query "SELECT goal_id, session_id, objective, status, status_reason, tokens_used, turns_used, time_used_seconds, token_budget, updated_at_ms FROM local_runtime_thread_goals" --save s01-legacy-row >"$OUT/pre-upgrade.json" 2>>"$OUT/steps.stderr.log"
  m2_log "s01 data runId=$RID session=$S"
  exit 0
fi

# ---------------- S02 ----------------
m2_begin S02 baseline-data
m2_up runtime --fault || exit 1
m2_smoke_api
vr fault log --role main --event attempt --tail 5 --save fault-smoke >/dev/null

# 1 complete
S_COMPLETE=$(m2_session "s02 complete" s02-complete-session)
m2_goal_create "$S_COMPLETE" "$OBJ_COUNT3" s02-complete-create >/dev/null
# 2 paused(user_requested)
S_PAUSED=$(m2_session "s02 paused" s02-paused-session)
m2_goal_create "$S_PAUSED" "$OBJ_SLEEP30" s02-paused-create >/dev/null
sleep 3
vr api PATCH $API/session/$S_PAUSED/goal --data '{"status":"paused"}' --save s02-paused-pause >/dev/null
# 3 blocked
S_BLOCKED=$(m2_session "s02 blocked" s02-blocked-session)
m2_goal_create "$S_BLOCKED" "$OBJ_BLOCKED" s02-blocked-create >/dev/null
# 4 usage_limited(provider_quota)：第 2 次主执行请求起返回带可信重置时间（1 小时后）的额度错误
S_USAGE=$(m2_session "s02 usage" s02-usage-session)
vr fault add --session "$S_USAGE" --nth 2- --preset usage-limit-reset --reset-in 3600 --note "S02 usage_limited(provider_quota)" --save fault-rule-usage >/dev/null
m2_goal_create "$S_USAGE" "$OBJ_USAGE" s02-usage-create >/dev/null
# 5 budget_limited(token)：挂起该会话的每个主执行请求，Goal 仍 active 时放行；Goal 已是 budget_limited 时
#   挂起的就是基线另排的预算总结轮次的请求，不放行，停机时它没有执行
S_BUDGET=$(m2_session "s02 budget" s02-budget-session)
vr fault add --session "$S_BUDGET" --nth 1- --action hang --note "S02 budget: gate every main request; keep the post-limit summary request hung" --save fault-rule-budget >/dev/null
m2_goal_create "$S_BUDGET" "$OBJ_NOTES" s02-budget-create 3000 >/dev/null
deadline=$(( $(date +%s) + 420 )); kept=""
while [ "$(date +%s)" -lt "$deadline" ]; do
  pend=$(vr fault pending | python3 -c 'import json,sys
d=json.load(sys.stdin)
def walk(o):
    if isinstance(o,dict):
        if isinstance(o.get("pending"),list): return o["pending"]
        for v in o.values():
            r=walk(v)
            if r is not None: return r
    return None
s=sys.argv[1]
print(" ".join(str(p["id"]) for p in (walk(d) or []) if p.get("sessionId")==s and p.get("kind")=="hang"))' "$S_BUDGET")
  for id in $pend; do
    st=$(vr api GET $API/session/$S_BUDGET/goal | jget "d['body']['goal']['status']")
    if [ "$st" = budget_limited ]; then kept=$id; break; fi
    vr fault release "$id" >/dev/null
  done
  [ -n "$kept" ] && break
  sleep 1
done
echo "${kept:-none}" >"$OUT/budget-summary-held-pending-id"
m2_log "budget summary request held pendingId=${kept:-none}"
vr api GET $API/session/$S_BUDGET/queue --save s02-budget-queue >/dev/null

# 问卷会话：Q1 回答并注入；Q2 待回答未到期；Q3 requiresExplicitResponse
S_Q1=$(m2_session "s02 q answered" s02-q1-session)
m2_goal_create "$S_Q1" "$OBJ_FRUIT" s02-q1-create 100000 >/dev/null
vr poll "$P$S_Q1" --until request.status=0 --show request.id,request.expires_at --interval 2 --timeout 180 --save s02-q1-pending >"$OUT/q1-pending.json"
Q1=$(jget "d['final']['request']['id']" <"$OUT/q1-pending.json")
python3 - "$OUT/q1-pending.json" >"$OUT/q1-reply.json" <<'EOF'
import json,sys
r=json.load(open(sys.argv[1]))['final']['request']
step=r['steps'][0]
opt=[o for o in step['options'] if 'banana' in json.dumps(o).lower()][0]
print(json.dumps({"schema_version":2,"answers":[{"step_id":step['id'],"selected_option_ids":[opt['id']],"selected_other":False}]}))
EOF
vr api POST $API/agent/mavis/questionnaire/$Q1/reply --data @"$OUT/q1-reply.json" --save s02-q1-reply >/dev/null

# 等各 Goal 到位
vr poll $API/session/$S_COMPLETE/goal --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 420 --save s02-complete-run >/dev/null
vr poll $API/session/$S_PAUSED/goal --until goal.status=paused --show "$SHOW" --interval 2 --timeout 60 --save s02-paused-run >/dev/null
vr poll $API/session/$S_BLOCKED/goal --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 300 --save s02-blocked-run >/dev/null
vr poll $API/session/$S_USAGE/goal --until "$TERMINAL" --show "$SHOW" --interval 2 --timeout 180 --save s02-usage-run >/dev/null
vr poll $API/session/$S_Q1/goal --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 420 --save s02-q1-run >/dev/null

# Q2、Q3 放在后面建：Q2 的 5 分钟期限不能在停机前到
S_Q2=$(m2_session "s02 q pending" s02-q2-session)
m2_goal_create "$S_Q2" "$OBJ_FRUIT" s02-q2-create 100000 >/dev/null
S_Q3=$(m2_session "s02 q explicit" s02-q3-session)
m2_goal_create "$S_Q3" "$OBJ_FRUIT_EXPLICIT" s02-q3-create 100000 >/dev/null
vr poll "$P$S_Q2" --until request.status=0 --show request.id,request.expires_at --interval 2 --timeout 180 --save s02-q2-pending >"$OUT/q2-pending.json"
vr poll "$P$S_Q3" --until request.status=0 --show request.id,request.expires_at --interval 2 --timeout 180 --save s02-q3-pending >"$OUT/q3-pending.json"

for s in COMPLETE PAUSED BLOCKED USAGE BUDGET Q1 Q2 Q3; do
  eval "sid=\$S_$s"; low=$(echo "$s" | tr A-Z a-z)
  goal_of "$sid" "s02-$low-pre-goal" >/dev/null
  vr api GET $API/session/$sid/message --save "s02-$low-pre-history" >/dev/null
  vr api GET $API/session/$sid/queue --save "s02-$low-pre-queue" >/dev/null
  vr snapshot --session "$sid" --save "s02-$low-pre-snap" >/dev/null
done

# active：最后建；第 2 个主执行请求发出后（Goal Turn 在途）直接 SIGKILL 服务进程树，模拟升级前带着在途工作退出。
# 正常关闭会中止该轮并把基线 Goal 改成 paused(accounting_unavailable)（第一次尝试实测），不是 active。
S_ACTIVE=$(m2_session "s02 active" s02-active-session)
m2_goal_create "$S_ACTIVE" "$OBJ_LONG" s02-active-create >/dev/null
deadline=$(( $(date +%s) + 120 ))
while [ "$(date +%s)" -lt "$deadline" ]; do
  n=$(vr fault log --session "$S_ACTIVE" --role main --event attempt | python3 -c 'import json,sys
d=json.load(sys.stdin)
def walk(o):
    if isinstance(o,dict):
        for k in ("entries","log","lines","events"):
            if isinstance(o.get(k),list): return o[k]
        for v in o.values():
            r=walk(v)
            if r is not None: return r
    if isinstance(o,list): return o
    return None
print(max([e.get("n") or 0 for e in (walk(d) or [])] or [0]))')
  [ "${n:-0}" -ge 2 ] && break
  sleep 1
done
goal_of "$S_ACTIVE" s02-active-pre-goal >/dev/null
vr api GET $API/session/$S_ACTIVE/message --save s02-active-pre-history >/dev/null
for s in COMPLETE PAUSED BLOCKED USAGE BUDGET Q1 Q2 Q3 ACTIVE; do
  eval "sid=\$S_$s"; echo "$s $sid" >>"$OUT/sessions.txt"
done
vr fault log --save fault-final >/dev/null
HOME_VA=${VERIFY_ARCHON_HOME:-$(node -e "console.log(require('os').tmpdir())")/verify-archon}
PID=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("pid") or "")' "$HOME_VA/$RID/state.json")
m2_log "SIGKILL runtime-server pid=$PID and descendants (active goal in flight, request n=$n)"
kill_tree() { local p=$1 c; for c in $(pgrep -P "$p"); do kill_tree "$c"; done; kill -KILL "$p" 2>/dev/null; }
echo "{\"killedPid\":$PID,\"atMs\":$(now_ms),\"activeInFlightRequestN\":${n:-0}}" >"$OUT/active-kill.json"
kill_tree "$PID"
sleep 2
m2_down --keep-data
# 停机后的存储读数（升级前记录）
node "$V" db --data "$RID" --query "SELECT goal_id, session_id, objective, status, status_reason, tokens_used, turns_used, time_used_seconds, token_budget, execution_wait_reason, usage_recovery_at_ms, kickoff_state, updated_at_ms FROM local_runtime_thread_goals ORDER BY created_at_ms" --save s02-legacy-goals >"$OUT/pre-upgrade-goals.json" 2>>"$OUT/steps.stderr.log"
node "$V" db --data "$RID" --query "SELECT request_id, session_id, status, created_at, answered_at, injected_at, reply_payload, json_extract(request_json,'$.goalId') AS goal_id, json_extract(request_json,'$.expiresAt') AS expires_at, json_extract(request_json,'$.purpose') AS purpose FROM questionnaire_requests ORDER BY created_at" --save s02-legacy-questionnaires >"$OUT/pre-upgrade-questionnaires.json" 2>>"$OUT/steps.stderr.log"
node "$V" db --data "$RID" --query "SELECT id, session_id, item_id, status, client_request_id, claim_id, substr(data_json,1,400) AS data_head FROM local_runtime_queue_items ORDER BY id" --save s02-legacy-queue >"$OUT/pre-upgrade-queue.json" 2>>"$OUT/steps.stderr.log"
# Q2 的到期时间：升级实例要在重新构建之后才能起来，原 5 分钟期限会先到；安排为停机时刻 + 3 小时（安排的前提，不是产品路径），
# 原值与安排值都记下，升级后的检查点按安排值比较
Q2=$(jget "d['final']['request']['id']" <"$OUT/q2-pending.json")
NEWEXP=$(( $(now_ms) + 3*3600*1000 ))
echo "{\"request_id\":\"$Q2\",\"original_expires_at\":$(jget "d['final']['request'].get('expires_at')" <"$OUT/q2-pending.json"),\"arranged_expires_at\":$NEWEXP}" >"$OUT/q2-expiry-arranged.json"
node "$V" db --data "$RID" --sql "UPDATE questionnaire_requests SET request_json = json_set(request_json, '\$.expiresAt', $NEWEXP) WHERE request_id = '$Q2'" --save s02-arrange-q2-expiry >"$OUT/arrange-q2.json" 2>>"$OUT/steps.stderr.log"
node "$V" db --data "$RID" --query "SELECT request_id, status, json_extract(request_json,'$.expiresAt') AS expires_at, json_extract(request_json,'$.goalId') AS goal_id FROM questionnaire_requests ORDER BY created_at" --save s02-legacy-questionnaires-arranged >"$OUT/pre-upgrade-questionnaires-arranged.json" 2>>"$OUT/steps.stderr.log"
m2_log "s02 data runId=$RID"
