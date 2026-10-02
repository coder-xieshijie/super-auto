#!/usr/bin/env bash
# X1 补充验证“停止后恢复”（不是 verify 场景；支撑决定清单“用户显式恢复 Goal 时结束 user-stop 造成的队列暂停”，提交 e71be11629）。
# 用法（gv2-tests 根目录，已 source /tmp/gv2-final2/env.sh）：bash <tools>/x1-stop-resume.sh <尝试名>
# 证据：<M2_ROOT>/X1/<尝试名>/。从 Electron 入口驱动：
#   1 /goal 创建 Goal；2 Goal Turn 运行中按 Enter 默认排队发送补充消息（sleep 60）；3 Goal Turn 结束、补充消息那一轮跑到 sleep 60 时点
#   输入框停止按钮；4 读 Goal（应 paused(user_requested)）与队列暂停（cause 应 user-stop）、队列项；5 点 continue-button；
#   6 检查新 goal.turn_bound（10 秒内）、队列暂停清除、最终 complete(verifier_met) 与 a.txt、b.txt，全程轨迹采样。
# 前提不成立（Goal Turn 未见运行、补充消息没排队、补充消息那一轮开始前 Goal 已结束）时写 premise-failed，退出码 4，本次不计。
set -u
source "$(dirname "${BASH_SOURCE[0]}")/x-lib.sh"
ATTEMPT=$1
export M2_ELECTRON_UP_EXTRA=${M2_ELECTRON_UP_EXTRA:---auth-lease 40}
OBJ="Run the shell command sleep 40 in the foreground, then write a.txt containing a. Then write b.txt containing b."
SUP="Run the shell command sleep 60 in the foreground, then reply done."
premise_fail() { echo "$1" >"$OUT/premise-failed"; m2_log "premise failed: $1"; [ -n "${SAMPLER:-}" ] && kill "$SAMPLER" 2>/dev/null; [ -n "${QWATCH:-}" ] && kill "$QWATCH" 2>/dev/null; end_scenario; exit 4; }

m2_begin X1 "$ATTEMPT"
write_commands "source /tmp/gv2-final2/env.sh" "bash \$T/x1-stop-resume.sh $ATTEMPT" "python3 \$T/x-analyze.py X1 $ATTEMPT" "python3 \$T/final-summary-md.py \$M2_ROOT/X1/$ATTEMPT"
m3_up electron || exit 1
m2_close_popups
# 1
m2_send_goal_electron "$OBJ" x1-create
S=$(m2_latest_session); echo "$S" >"$OUT/session"
traj_sampler "$S" "$OUT/x1-trajectory.jsonl" &
SAMPLER=$!
questionnaire_watch "$S" x1 &
QWATCH=$!
# 2 Goal Turn 运行中（turn_bound 已出现且 stop-button 可见）按 Enter 默认排队发送
T1=$(wait_open_goal_turn "$S" 90 x1-step2-running) || premise_fail "goal turn not seen running before step 2"
echo "$T1" >"$OUT/x1-goal-turn-1"
type_checked "$SUP" || input_abort
echo "$(now_ms)" >"$OUT/x1-step2-at-ms"
E press --testid message-textarea --key Enter --save x1-step2-enter >/dev/null
sleep 1.2
E count --testid goal-replace-confirm-modal --save x1-replace-dialog-step2 >/dev/null
vr api GET $API/session/$S/queue --on electron --save x1-queue-api-step2 >/dev/null
queue_db "$S" x1-queue-db-step2 >/dev/null
goal_turn_open "$S" >"$OUT/x1-goal-turn-open-step2"
E screenshot --save x1-step2-queued >/dev/null
queued=$(python3 -c 'import json,sys
d=json.load(open(sys.argv[1])); print(1 if any("sleep 60" in (i.get("content") or "") for i in d.get("items") or []) else 0)' "$OUT/x1-queue-db-step2.json")
inhist=$(history_eval "$S" 'any(m.get("role")=="user" and "sleep 60" in str(m.get("msg_content","")) for m in ms)')
echo "{\"queuedInDb\":$queued,\"inHistory\":$inhist,\"goalTurnOpen\":\"$(cat "$OUT/x1-goal-turn-open-step2")\"}" >"$OUT/x1-step2-queued.json"
[ "$queued" = 1 ] || [ "$inhist" = 0 ] || premise_fail "supplement not queued (already in history at step 2)"
[ "$queued" = 1 ] || premise_fail "supplement not found in queue at step 2"
# 3 等 Goal Turn 结束、补充消息那一轮的 sleep 60 开始执行（live Inspector：T1 以外的 Turn 里 bash 已开始未结束），且 stop-button 可见。
# f1 用历史里的工具调用判断，工具结束后才出现，停止落在 sleep 之后（f1 作废）；f2 起改用 Inspector。
# sleep 执行中再等 T1 的校验判定、Goal 续跑项进入队列（source=thread-goal），最多等到 sleep 开始后 45 秒，然后点停止。
deadline=$(( $(date +%s) + 300 )); ok=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  o=$(goal_turn_open "$S")
  ts=$(supplement_tool_state "$S" "$T1")
  c=$(node "$V" electron count --testid stop-button --run "$RID" 2>/dev/null | jget "d.get('count')")
  st=$(goal_raw "$S" | jget "d.get('status') or ''")
  printf '{"at":%s,"goalTurn":"%s","bash":"%s","stopButton":"%s","goal":"%s"}\n' "$(now_ms)" "$o" "$ts" "$c" "$st" >>"$OUT/x1-step3-wait-trajectory.jsonl"
  if [ "$o" = none ] && [ "${ts#running:}" != "$ts" ] && [ "$c" = 1 ]; then ok=1; break; fi
  case $ts in done:*) premise_fail "supplement bash finished before it was seen running" ;; esac
  case $st in complete|blocked|budget_limited|usage_limited|paused) premise_fail "goal left active ($st) before the supplement turn ran" ;; esac
  sleep 0.5
done
[ "$ok" = 1 ] || premise_fail "supplement turn with sleep 60 not seen running"
echo "$ts" >"$OUT/x1-supplement-bash"
BASH_START=$(echo "$ts" | awk -F: '{print $3}')
while :; do
  q=$(queue_db "$S" _x1-step3-queue)
  tg=$(printf '%s' "$q" | jget "1 if any(i.get('source')=='thread-goal' for i in d.get('items') or []) else 0")
  ts=$(supplement_tool_state "$S" "$T1")
  printf '{"at":%s,"threadGoalItem":"%s","bash":"%s"}\n' "$(now_ms)" "$tg" "$ts" >>"$OUT/x1-step3-hold-trajectory.jsonl"
  [ "$tg" = 1 ] && break
  [ "${ts#running:}" != "$ts" ] || break
  [ $(( $(now_ms) - BASH_START )) -lt 45000 ] || break
  sleep 0.5
done
vr api GET $API/session/$S/message --on electron --save x1-history-before-stop >/dev/null
queue_db "$S" x1-queue-db-before-stop >/dev/null
goal_e "$S" x1-goal-before-stop >/dev/null
supplement_tool_state "$S" "$T1" >"$OUT/x1-bash-state-at-stop"
echo "$(now_ms)" >"$OUT/x1-stop-at-ms"
E click --testid stop-button --save x1-stop >/dev/null
turn_end 30
sleep 1.5
# 4
goal_e "$S" x1-goal-step4 >/dev/null
vr api GET $API/session/$S/queue --on electron --save x1-queue-api-step4 >/dev/null
queue_db "$S" x1-queue-db-step4 >/dev/null
etext thread-goal-banner-status x1-banner-status-step4 >/dev/null
E count --testid continue-button --save x1-continue-count-step4 >/dev/null
E screenshot --save x1-step4 >/dev/null
# T1 的校验已派发时，等它判定（最多 60 秒）再恢复，避免恢复后的续跑因 required_background 延后而影响 10 秒检查；记录等待
vstart=$(now_ms)
for _ in $(seq 1 120); do
  vd=$(goal_events "$S" goal.verification_dispatched goal.verification_decided | python3 -c 'import json,sys
t=sys.argv[1]; rows=[json.loads(l) for l in sys.stdin if l.strip()]
disp=[r for r in rows if r["eventType"]=="goal.verification_dispatched" and r["payload"].get("turnId")==t]
dec=[r for r in rows if r["eventType"]=="goal.verification_decided" and r["payload"].get("turnId")==t]
print("none" if not disp else ("decided" if dec else "pending"))' "$T1")
  [ "$vd" = pending ] || break
  sleep 0.5
done
printf '{"t1Verification":"%s","waitedMs":%s}\n' "$vd" "$(( $(now_ms) - vstart ))" >"$OUT/x1-verification-before-resume.json"
goal_e "$S" x1-goal-before-resume >/dev/null
queue_db "$S" x1-queue-db-before-resume >/dev/null
# 5
echo "$(now_ms)" >"$OUT/x1-resume-click-at-ms"
if [ "$(E count --testid continue-button | jget "d.get('count')")" = 1 ]; then
  echo continue-button >"$OUT/x1-resume-via"
  E click --testid continue-button --save x1-resume-click >/dev/null
else
  echo thread-goal-banner-resume >"$OUT/x1-resume-via"
  E click --testid thread-goal-banner-resume --save x1-resume-click >/dev/null
fi
# 6
NB=$(wait_new_turn_bound "$S" "$T1" 30 x1-after-resume) || NB=""
echo "$NB" >"$OUT/x1-new-turn-bound"
queue_db "$S" x1-queue-db-after-resume >/dev/null
goal_e "$S" x1-goal-after-resume >/dev/null
etext thread-goal-banner-status x1-banner-status-after-resume >/dev/null
poll_e "$S" --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 600 --save x1-run >/dev/null
turn_end 180
sleep 2
kill "$SAMPLER" "$QWATCH" 2>/dev/null
goal_e "$S" x1-final >/dev/null
queue_db "$S" x1-queue-db-final >/dev/null
python3 - "$(m3_db)" "$S" >"$OUT/x1-questionnaires.json" <<'PYEOF'
import json, sqlite3, sys
c = sqlite3.connect('file:' + sys.argv[1] + '?mode=ro', uri=True, timeout=5)
rows = [dict(zip(['request_id','status','created_at','answered_at','purpose','goalId','expiresAt','title','turnId','replySource'], r)) for r in c.execute(
    "SELECT request_id, status, created_at, answered_at, json_extract(request_json,'$.purpose'), json_extract(request_json,'$.goalId'), json_extract(request_json,'$.expiresAt'), json_extract(request_json,'$.title'), json_extract(request_json,'$.requester.runId'), json_extract(reply_payload,'$.source') FROM questionnaire_requests WHERE session_id=? ORDER BY created_at", (sys.argv[2],))]
print(json.dumps(rows, ensure_ascii=False, indent=2))
PYEOF
vr api GET $API/session/$S/queue --on electron --save x1-queue-api-final >/dev/null
vr api GET $API/session/$S/message --on electron --save x1-history >/dev/null
goal_events "$S" >"$OUT/x1-goal-events.jsonl"
vr snapshot --session "$S" --on electron --save x1 >/dev/null
end_scenario
m2_log "X1 done"
