#!/usr/bin/env bash
# X2 补充验证“补充消息那一轮失败后 Goal 自动续跑”（不是 verify 场景；对应提交 669f179230）。
# 用法（gv2-tests 根目录，已 source /tmp/gv2-final2/env.sh）：bash <tools>/x2-failure-continue.sh <尝试名>
# 证据：<M2_ROOT>/X2/<尝试名>/。Electron 以 --fault 启动，故障闸门见 x2-fault-gate.py：
#   1 /goal 创建 Goal；2 Goal Turn 运行中按 Enter 默认排队发送 “Reply with the word apple.”；
#   3 闸门只让补充消息那一轮的请求最终失败（第一次 attempt 可重试 500，重发 attempt 502/50113，不可重试）；
#   4 不点任何按钮、不再发消息，记录失败、新 goal.turn_bound、队列暂停、最终状态与 c.txt；结束前关闭并清空故障规则。
# 前提不成立（Goal Turn 未见运行、补充消息没排队、闸门没在补充消息那一轮命中）时写 premise-failed，退出码 4，本次不计。
set -u
source "$(dirname "${BASH_SOURCE[0]}")/x-lib.sh"
ATTEMPT=$1
export M2_ELECTRON_UP_EXTRA=${M2_ELECTRON_UP_EXTRA:---auth-lease 40}
OBJ="Run the shell command sleep 30 in the foreground, then write c.txt containing c."
SUP="Reply with the word apple."
GATE_BODY='{"type":"error","error":{"type":"api_error","message":"upstream network error, please retry"}}'
F() { vr fault "$@" --on electron; }
faults_off() {
  F list --save fault-rules-before-off >/dev/null
  [ -n "${R:-}" ] && F disable "$R" >/dev/null
  [ -n "${EF:-}" ] && F disable "$EF" >/dev/null
  F list --save fault-rules-after-off >/dev/null
  F clear --save fault-rules-cleared >/dev/null
}
premise_fail() {
  echo "$1" >"$OUT/premise-failed"; m2_log "premise failed: $1"
  [ -n "${GATE:-}" ] && kill "$GATE" 2>/dev/null
  [ -n "${SAMPLER:-}" ] && kill "$SAMPLER" 2>/dev/null
  faults_off; F log --save fault-log-final >/dev/null; end_scenario; exit 4
}
new_task() { E click --role button --name "新建任务" --exact --timeout 10 >/dev/null || E click --role button --name "新建任务" >/dev/null; sleep 1; }

m2_begin X2 "$ATTEMPT"
write_commands "source /tmp/gv2-final2/env.sh" "bash \$T/x2-failure-continue.sh $ATTEMPT   # 内部启动 x2-fault-gate.py" "python3 \$T/x-analyze.py X2 $ATTEMPT" "python3 \$T/final-summary-md.py \$M2_ROOT/X2/$ATTEMPT"
m3_up electron --fault || exit 1
FAULT_URL=$(python3 -c 'import json,sys; print((json.load(open(sys.argv[1])).get("fault") or {}).get("url") or "")' "$OUT/up.json")
[ -n "$FAULT_URL" ] || FAULT_URL=$(python3 -c 'import json,sys; print((json.load(open(sys.argv[1])).get("fault") or {}).get("url") or "")' "$HOME_VA/$RID/state.json")
FAULT_LOG=$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); f=d.get("fault") or {}; print(f.get("log") or f.get("logFile") or "")' "$OUT/up.json")
[ -n "$FAULT_LOG" ] || FAULT_LOG="$OUT/fault-proxy.jsonl"
printf '{"faultUrlSet":%s,"faultLog":"%s"}\n' "$([ -n "$FAULT_URL" ] && echo true || echo false)" "$FAULT_LOG" >"$OUT/x2-fault-setup.json"
m2_close_popups
# 冒烟：单独会话 PONG，并确认流量经过代理
type_checked "Reply with exactly the word PONG and nothing else." || input_abort
E click --testid send-button --save smoke-send >/dev/null
sleep 3; turn_end 60
O=$(m2_latest_session); echo "$O" >"$OUT/smoke-session"
wait_reply "$O" "PONG" 60 smoke-history
F log --role main --event attempt --save smoke-fault-log >/dev/null
new_task
# 1
m2_send_goal_electron "$OBJ" x2-create
S=$(m2_latest_session); echo "$S" >"$OUT/session"
[ "$S" != "$O" ] || premise_fail "goal session equals smoke session"
R=$(F add --session "$S" --role main --attempts first --status 500 --body "$GATE_BODY" --headers '{"retry-after-ms":"3000"}' --disabled --note x2-gate-retryable-500 --save fault-rule-gate | jget "(d.get('rule') or {}).get('id') or ''")
EF=$(F add --session "$S" --role main --preset upstream-50113 --times 1 --disabled --note x2-fail-50113 --save fault-rule-fail | jget "(d.get('rule') or {}).get('id') or ''")
printf '{"gate":"%s","fail":"%s"}\n' "$R" "$EF" >"$OUT/x2-rule-ids.json"
[ -n "$R" ] && [ -n "$EF" ] || premise_fail "fault rules not added"
traj_sampler "$S" "$OUT/x2-trajectory.jsonl" &
SAMPLER=$!
# 2
T1=$(wait_open_goal_turn "$S" 90 x2-step2-running) || premise_fail "goal turn not seen running before step 2"
echo "$T1" >"$OUT/x2-goal-turn-1"
type_checked "$SUP" || input_abort
echo "$(now_ms)" >"$OUT/x2-step2-at-ms"
E press --testid message-textarea --key Enter --save x2-step2-enter >/dev/null
sleep 1.2
E count --testid goal-replace-confirm-modal --save x2-replace-dialog-step2 >/dev/null
vr api GET $API/session/$S/queue --on electron --save x2-queue-api-step2 >/dev/null
queue_db "$S" x2-queue-db-step2 >/dev/null
goal_turn_open "$S" >"$OUT/x2-goal-turn-open-step2"
queued=$(python3 -c 'import json,sys
d=json.load(open(sys.argv[1])); print(1 if any("apple" in (i.get("content") or "") for i in d.get("items") or []) else 0)' "$OUT/x2-queue-db-step2.json")
echo "{\"queuedInDb\":$queued,\"goalTurnOpen\":\"$(cat "$OUT/x2-goal-turn-open-step2")\"}" >"$OUT/x2-step2-queued.json"
[ "$queued" = 1 ] || premise_fail "supplement not found in queue at step 2"
# 3 打开闸门，启动观察进程
python3 "$M2_TOOLS/x2-fault-gate.py" "$FAULT_LOG" "$(events_dir)" "$S" "$FAULT_URL" "$RID" "$R" "$EF" "$OUT/x2-gate.jsonl" 600 &
GATE=$!
F enable "$R" --save fault-gate-enabled >/dev/null
echo "$(now_ms)" >"$OUT/x2-gate-enabled-at-ms"
wait "$GATE"; grc=$?; GATE=""
# 失败后立即取界面与会话状态（下一个 Goal Turn 可能在几百毫秒内开始）
E aria --save x2-page-aria-immediate >/dev/null
E screenshot --save x2-immediate >/dev/null
vr api GET $API/session/$S --on electron --save x2-session-immediate >/dev/null
echo "$grc" >"$OUT/x2-gate-rc"
echo "$(now_ms)" >"$OUT/x2-gate-done-at-ms"
F list --save fault-rules-after-gate >/dev/null
[ "$grc" = 0 ] || premise_fail "fault gate did not fire on the supplement turn"
# 4 不点按钮、不发消息
sleep 3
E screenshot --save x2-after-failure >/dev/null
E aria --save x2-page-aria-after-failure >/dev/null
vr api GET $API/session/$S/message --on electron --save x2-history-after-failure >/dev/null
queue_db "$S" x2-queue-db-after-failure >/dev/null
goal_e "$S" x2-goal-after-failure >/dev/null
NB=$(wait_new_turn_bound "$S" "$T1" 90 x2-after-failure) || NB=""
echo "$NB" >"$OUT/x2-new-turn-bound"
queue_db "$S" x2-queue-db-after-new-turn >/dev/null
poll_e "$S" --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 600 --save x2-run >/dev/null
turn_end 180
sleep 2
kill "$SAMPLER" 2>/dev/null
goal_e "$S" x2-final >/dev/null
queue_db "$S" x2-queue-db-final >/dev/null
vr api GET $API/session/$S/queue --on electron --save x2-queue-api-final >/dev/null
vr api GET $API/session/$S/message --on electron --save x2-history >/dev/null
E aria --save x2-page-aria-final >/dev/null
vr api GET $API/session/$S --on electron --save x2-session-final >/dev/null
goal_events "$S" >"$OUT/x2-goal-events.jsonl"
F log --session "$S" --save fault-log-session >/dev/null
faults_off
vr snapshot --session "$S" --on electron --save x2 >/dev/null
end_scenario
m2_log "X2 done"
