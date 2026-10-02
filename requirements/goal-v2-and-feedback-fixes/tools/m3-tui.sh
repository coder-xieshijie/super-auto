#!/usr/bin/env bash
# M3 TUI 场景：verify.md S13、S40（不带故障注入），S18、S30（--fault）。命令照抄各场景步骤。
# 用法（agent-archon worktree 根目录）：bash <tools>/m3-tui.sh <S13|S18|S30|S40> <尝试名>
set -u
source "$(dirname "${BASH_SOURCE[0]}")/m3-lib.sh"
SCN=$1
ATTEMPT=$2
T() { vr tui "$@"; }
idle() { T wait --status "state=ready|done|fail|cancel|error" --timeout "${2:-120}" --save "$1" >/dev/null; }
sess() { tui_status | jget "d.get('session') or ''"; }
reset_at() { python3 -c 'import json,sys
def walk(o):
    if isinstance(o,dict):
        if isinstance(o.get("resetAtMs"),(int,float)): return int(o["resetAtMs"])
        for v in o.values():
            r=walk(v)
            if r: return r
    elif isinstance(o,list):
        for v in o:
            r=walk(v)
            if r: return r
    return 0
try: print(walk(json.load(sys.stdin)))
except Exception: print(0)'; }
# 等 TUI 新的一轮开始再结束：先记 seq，发命令，等 seq 变大且不在运行
cmd_and_settle() { # cmd_and_settle <命令> <save> [timeout]
  local seq0
  seq0=$(tui_seq)
  echo "{\"at\":$(now_ms),\"cmd\":\"$1\",\"seqBefore\":\"$seq0\"}" >>"$OUT/commands.jsonl"
  T type "$1" >/dev/null
  tui_wait_turn_after "$seq0" "${3:-120}" "$2"
}
end_scenario() {
  T screen --all --save final-screen >/dev/null
  m2_down
}

m2_begin "$SCN" "$ATTEMPT"
case $SCN in
S13)
  # 8765 与 Electron S12 相同：先等端口空闲（不同实例的场景不并发占用）
  for _ in $(seq 1 120); do
    [ "$(curl -s -o /dev/null -m 2 -w '%{http_code}' http://127.0.0.1:8765/ 2>/dev/null)" = "000" ] && break
    sleep 5
  done
  port_probe 8765 s13-port-before >/dev/null
  m3_up tui || exit 1
  # 1
  T type "Start the shell command python3 -m http.server 8765 as a background task (bash tool with run_in_background: true) and end your turn right away." >/dev/null
  idle s13-bg-turn-end 180
  T screen --save s13-step1-screen >/dev/null
  S=$(sess); echo "$S" >"$OUT/session"
  bg_tasks "$S" s13-bg-tasks-step1 >/dev/null
  port_probe 8765 s13-port-step1 >/dev/null
  # 2
  T type "/goal Write the numbers 1 to 3 into count.txt, one number per line, then stop." >/dev/null
  # 3
  T wait --text "✓ Goal complete" --timeout 420 --save s13-complete >/dev/null
  idle s13-final-idle 120
  T screen --all --save s13-final-screen >/dev/null
  bg_tasks "$S" s13-bg-tasks-final >/dev/null
  port_probe 8765 s13-port-final >/dev/null
  T snapshot --save s13 >/dev/null
  end_scenario
  port_closed_after_down 8765
  ;;
S40)
  m3_up tui || exit 1
  # 1
  T type "/goal Start a background subagent task (task tool, run in background) that waits 40 seconds and then writes sub.txt containing sub-done. End your turn right away without waiting. The goal is met only when sub.txt contains sub-done." >/dev/null
  T wait --text "Waiting for background tasks" --timeout 150 --save s40-waiting >/dev/null
  S=$(sess); echo "$S" >"$OUT/session"
  bg_tasks "$S" s40-bg-tasks-waiting >/dev/null
  # 2
  T type "/goal pause" >/dev/null
  T wait --text "◎ Goal · Paused" --timeout 30 --save s40-paused >/dev/null
  T screen --save s40-paused-screen >/dev/null
  bg_tasks "$S" s40-bg-tasks-paused >/dev/null
  # 3
  echo "{\"at\":$(now_ms),\"cmd\":\"/goal resume\"}" >>"$OUT/commands.jsonl"
  T type "/goal resume" >/dev/null
  sleep 3
  T screen --all --save s40-resume-screen >/dev/null
  bg_tasks "$S" s40-bg-tasks-after-resume >/dev/null
  # 4
  T wait --text "✓ Goal complete" --timeout 600 --save s40-complete >/dev/null
  idle s40-final-idle 120
  T screen --all --save s40-final-screen >/dev/null
  bg_tasks "$S" s40-bg-tasks-final >/dev/null
  T snapshot --save s40 >/dev/null
  end_scenario
  ;;
S30)
  m3_up tui --fault || exit 1
  RULE=$(vr fault add --on tui --session next --preset upstream-50113 --disabled --note "S30: 50113 for the session's main requests while enabled" --save fault-rule | jget "(d.get('rule') or {}).get('id') or d.get('id') or d.get('ruleId')")
  echo "$RULE" >"$OUT/rule-id"
  # 1
  T type "Start the shell command sleep 600 as a background task (bash tool with run_in_background: true) and end your turn right away." >/dev/null
  idle s30-bg-turn-end 180
  T screen --save s30-step1-screen >/dev/null
  S=$(sess); echo "$S" >"$OUT/session"
  bg_tasks "$S" s30-bg-tasks-step1 >/dev/null
  # 2
  vr fault enable "$RULE" --on tui --save fault-enable >/dev/null
  T type "/goal Write the numbers 1 to 3 into count.txt, one number per line, then stop." >/dev/null
  T wait --text "◎ Goal · Paused" --timeout 180 --save s30-paused >/dev/null
  idle s30-paused-idle 60
  T screen --all --save s30-step2-screen >/dev/null
  T snapshot --save s30-step2 >/dev/null
  # 3
  cmd_and_settle "/goal resume" s30-resume-settled 120
  sleep 3
  T screen --all --save s30-step3-screen >/dev/null
  T snapshot --save s30-step3 >/dev/null
  # 4
  vr fault disable "$RULE" --on tui --save fault-disable >/dev/null
  echo "{\"at\":$(now_ms),\"cmd\":\"/retry\"}" >>"$OUT/commands.jsonl"
  T type "/retry" >/dev/null
  T wait --text "✓ Goal complete" --timeout 420 --save s30-complete >/dev/null
  idle s30-final-idle 120
  T screen --all --save s30-final-screen >/dev/null
  bg_tasks "$S" s30-bg-tasks-final >/dev/null
  T snapshot --save s30 >/dev/null
  vr fault log --on tui --session "$S" --tail 500 --save fault-s30 >/dev/null
  end_scenario
  ;;
S18)
  m3_up tui --fault || exit 1
  RULE=$(vr fault add --on tui --session next --nth 2- --preset usage-limit-reset --reset-in 180 --note "S18: from the 2nd main request until the reset time" --save fault-rule | jget "(d.get('rule') or {}).get('id') or d.get('id') or d.get('ruleId')")
  echo "$RULE" >"$OUT/rule-id"
  # 1
  T type "/goal Create files e1.txt, e2.txt, e3.txt one at a time, each containing its own number, then stop." >/dev/null
  T wait --text "Usage limited" --timeout 180 --save s18-limited >/dev/null
  idle s18-limited-idle 60
  T screen --all --save s18-step1-screen >/dev/null
  S=$(sess); echo "$S" >"$OUT/session"
  vr fault log --on tui --session "$S" --event attempt-end --save fault-s18-step1 | reset_at >"$OUT/reset-at-ms"
  T snapshot --save s18-step1 >/dev/null
  # 2
  cmd_and_settle "/goal resume" s18-resume-settled 60
  sleep 2
  T screen --all --save s18-step2-screen >/dev/null
  # 2b
  cmd_and_settle "/retry" s18-retry-settled 60
  sleep 2
  T screen --all --save s18-step2b-screen >/dev/null
  echo "$(now_ms)" >"$OUT/step2b-done-at-ms"
  T snapshot --save s18-step2b >/dev/null
  # 3
  T wait --text "✓ Goal complete" --timeout 600 --save s18-complete >/dev/null
  idle s18-final-idle 120
  T screen --all --save s18-final-screen >/dev/null
  T snapshot --save s18 >/dev/null
  vr fault log --on tui --session "$S" --tail 500 --save fault-s18 >/dev/null
  vr fault list --on tui --save fault-list >/dev/null
  end_scenario
  ;;
*) echo "unknown scenario $SCN" >&2; exit 2 ;;
esac
m2_log "scenario $SCN done"
