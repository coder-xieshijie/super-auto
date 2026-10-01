#!/usr/bin/env bash
# V1 并行实跑的单实例工作进程：worker.sh <runtime|tui|electron> <实例名> <截止 epoch 秒> [up 额外参数...]
# 在 gv2-verify-tools 根目录运行；M2_ROOT 指向本轮证据根；M3_UP_LOCK 串行启动。
# 截止前反复创建简单 Goal 跑到终态；每个 Goal 结束后检查会话历史里有没有 workspace 以外的路径，有就立即 down 并记 incident。
set -u
KINDW=$1; NAME=$2; DEADLINE=$3; shift 3
source /Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/tools/m3-lib.sh
m2_begin "$NAME" "."
TL=$M2_ROOT/timeline.jsonl
tl() { printf '{"at":%s,"instance":"%s","event":"%s"%s}\n' "$(now_ms)" "$NAME" "$1" "${2:+,$2}" >>"$TL"; }
E() { vr electron "$@"; }
outside_check() { # outside_check <session>：历史里出现 /Users/、~/、.claude 视为 workspace 以外的读写
  local hist
  hist=$(node "$V" api GET $API/session/$1/message $(ON) --run "$RID" 2>/dev/null)
  if printf '%s' "$hist" | python3 -c 'import sys,re; t=sys.stdin.read(); sys.exit(0 if re.search(r"/Users/|~/|\.claude\b|\.minimax\b", t) else 1)'; then
    echo "outside-workspace session=$1" >"$OUT/incident.json"
    tl incident "\"session\":\"$1\""
    m2_log "INCIDENT: path outside workspace in session $1; stopping instance"
    m2_down; exit 4
  fi
}
tl up-start
case $KINDW in
  runtime) m3_up runtime "$@" || { tl up-failed; exit 1; } ;;
  tui) m3_up tui "$@" || { tl up-failed; exit 1; } ;;
  electron) m3_up electron "$@" || { tl up-failed; exit 1; }; m2_close_popups ;;
esac
tl up-ready "\"runId\":\"$RID\""
n=0
while [ "$(date +%s)" -lt "$DEADLINE" ]; do
  n=$((n+1))
  OBJ="Write the numbers 1 to 3 into count-$n.txt, one number per line, then stop."
  tl goal-start "\"n\":$n"
  case $KINDW in
    runtime)
      s=$(m2_session "v1 $NAME $n" "g$n-session")
      m2_goal_create "$s" "$OBJ" "g$n-create" >/dev/null
      vr poll $API/session/$s/goal --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 300 --save "g$n-run" >/dev/null
      st=$(vr api GET $API/session/$s/goal --save "g$n-final" | jget "d['body']['goal']['status_reason']")
      outside_check "$s" ;;
    tui)
      vr tui type "/goal $OBJ" >/dev/null
      vr tui wait --text "Goal complete|Goal · Paused|Goal · Blocked|Budget limited|Usage limited" --timeout 300 --save "g$n-end" >/dev/null
      vr tui wait --status "state=ready|done|fail|cancel|error" --timeout 120 >/dev/null
      st=$(vr tui screen --save "g$n-screen" | python3 -c 'import json,sys,re
d=json.load(sys.stdin); t=json.dumps(d); m=re.search(r"Goal complete|Goal · (Paused|Blocked)|Budget limited|Usage limited", t); print(m.group(0) if m else "?")')
      if vr tui screen --all | python3 -c 'import sys,re; sys.exit(0 if re.search(r"/Users/|~/|\.claude\b|\.minimax\b", sys.stdin.read()) else 1)'; then
        echo "outside-workspace tui goal $n" >"$OUT/incident.json"; tl incident "\"n\":$n"; m2_down; exit 4
      fi ;;
    electron)
      E click --role button --name "新建任务" --exact --timeout 10 >/dev/null || E click --role button --name "新建任务" >/dev/null
      sleep 1
      type_checked "/goal $OBJ" || { tl input-contaminated "\"n\":$n"; input_abort; }
      E click --testid send-button >/dev/null
      E wait --testid thread-goal-banner --timeout 60 >/dev/null
      s=$(m2_latest_session)
      vr poll $API/session/$s/goal --on electron --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 300 --save "g$n-run" >/dev/null
      E wait --testid stop-button --state hidden --timeout 120 >/dev/null
      st=$(vr api GET $API/session/$s/goal --on electron --save "g$n-final" | jget "d['body']['goal']['status_reason']")
      outside_check "$s" ;;
  esac
  tl goal-end "\"n\":$n,\"result\":\"$st\""
done
tl down-start
m2_down
tl down-done "\"runId\":\"$RID\""
