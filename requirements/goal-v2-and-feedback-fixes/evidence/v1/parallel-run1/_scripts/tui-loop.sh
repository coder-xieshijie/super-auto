#!/usr/bin/env bash
# 接管已 up 的 TUI 实例（worker.sh 的 TUI 循环误判完成后替换）：每个 Goal 等到 Active、运行、回到空闲再读结果
set -u
RID=$1; DEADLINE=$2; n=$3
export M2_ROOT=/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/v1/parallel-run1
cd /Users/minimax/code/mm/worktrees/agent-archon/gv2-verify-tools
source /Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/tools/m3-lib.sh
OUT=$M2_ROOT/tui; SC=tui; KIND=tui; NAME=tui
TL=$M2_ROOT/timeline.jsonl
tl() { printf '{"at":%s,"instance":"%s","event":"%s"%s}\n' "$(now_ms)" "$NAME" "$1" "${2:+,$2}" >>"$TL"; }
tl tui-loop-takeover "\"note\":\"worker TUI loop misdetected completion for goals 3-44 (stale Goal complete text); replaced\""
vr tui wait --status "state=ready|done|fail|cancel|error" --hold 3 --timeout 300 >/dev/null
while [ "$(date +%s)" -lt "$DEADLINE" ]; do
  n=$((n+1))
  OBJ="Write the numbers 1 to 3 into count-$n.txt, one number per line, then stop."
  tl goal-start "\"n\":$n"
  vr tui type "/goal $OBJ" >/dev/null
  vr tui wait --text "◎ Goal · Active" --timeout 30 --save "g$n-active" >/dev/null
  vr tui wait --status "state=run" --timeout 30 >/dev/null
  vr tui wait --status "state=ready|done|fail|cancel|error" --hold 5 --timeout 300 --save "g$n-idle" >/dev/null
  st=$(vr tui screen --save "g$n-screen" | python3 -c 'import json,sys,re
t=json.dumps(json.load(sys.stdin), ensure_ascii=False); m=re.findall(r"Goal complete|Goal · (?:Active|Paused|Blocked)|Budget limited|Usage limited", t); print(m[-1] if m else "?")')
  if vr tui screen --all | python3 -c 'import sys,re; sys.exit(0 if re.search(r"/Users/|~/|\.claude\b|\.minimax\b", sys.stdin.read()) else 1)'; then
    echo "outside-workspace tui goal $n" >"$OUT/incident.json"; tl incident "\"n\":$n"; m2_down; exit 4
  fi
  tl goal-end "\"n\":$n,\"result\":\"$st\""
done
tl down-start
m2_down
tl down-done "\"runId\":\"$RID\""
