#!/usr/bin/env bash
# 接管 TUI：按屏幕底部（最后 14 行）的 Goal 横幅判定终态，Goal 仍 Active 时不发下一个 /goal
set -u
RID=$1; DEADLINE=$2; n=$3
export M2_ROOT=/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/v1/parallel-run1
cd /Users/minimax/code/mm/worktrees/agent-archon/gv2-verify-tools
source /Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/tools/m3-lib.sh
OUT=$M2_ROOT/tui; SC=tui; KIND=tui; NAME=tui
TL=$M2_ROOT/timeline.jsonl
tl() { printf '{"at":%s,"instance":"%s","event":"%s"%s}\n' "$(now_ms)" "$NAME" "$1" "${2:+,$2}" >>"$TL"; }
banner() { node "$V" tui screen --run "$RID" 2>/dev/null | python3 -c 'import json,sys,re
d=json.load(sys.stdin); s=d.get("screen",d); t="\n".join(s.get("lines") or [])
tail="\n".join((s.get("lines") or [])[-14:])
m=re.search(r"Goal complete|Goal · (Active|Paused|Blocked)|Budget limited|Usage limited", tail)
st=(s.get("status") or {}).get("state","?")
print((m.group(0) if m else "none")+"|"+st)'; }
wait_goal_end() { # 等横幅离开 Active 且状态栏空闲，最多 $1 秒
  local deadline=$(( $(date +%s) + $1 )) b
  while [ "$(date +%s)" -lt "$deadline" ]; do
    b=$(banner)
    case $b in *"Goal · Active"*|*"|run"*|*"|ask"*) ;; *) echo "$b"; return 0 ;; esac
    sleep 3
  done
  echo "timeout:$b"; return 1
}
tl tui-loop2-takeover "\"note\":\"tui-loop.sh retyped /goal while the Goal was still Active (objective updates for 101-104); replaced\""
wait_goal_end 300 >/dev/null
while [ "$(date +%s)" -lt "$DEADLINE" ]; do
  n=$((n+1))
  OBJ="Write the numbers 1 to 3 into count-$n.txt, one number per line, then stop."
  tl goal-start "\"n\":$n"
  vr tui type "/goal $OBJ" >/dev/null
  vr tui wait --status "state=run" --timeout 30 >/dev/null
  st=$(wait_goal_end 300)
  vr tui screen --save "g$n-screen" >/dev/null
  if vr tui screen --all | python3 -c 'import sys,re; sys.exit(0 if re.search(r"/Users/|~/|\.claude\b|\.minimax\b", sys.stdin.read()) else 1)'; then
    echo "outside-workspace tui goal $n" >"$OUT/incident.json"; tl incident "\"n\":$n"; m2_down; exit 4
  fi
  tl goal-end "\"n\":$n,\"result\":\"$st\""
done
wait_goal_end 300 >/dev/null
tl down-start
m2_down
tl down-done "\"runId\":\"$RID\""
