#!/usr/bin/env bash
# M2 TUI 入口场景：verify.md S04、S09，命令照抄各场景步骤。
# 用法（agent-archon worktree 根目录）：bash <tools>/m2-tui.sh <S04|S09> <尝试名>
set -u
source "$(dirname "${BASH_SOURCE[0]}")/m2-lib.sh"
SCN=$1
ATTEMPT=$2
m2_begin "$SCN" "$ATTEMPT"

summary() { # 空闲时查看 /goal 摘要（lifecycle.md 的按键顺序）
  vr tui type "/goal" --no-submit >/dev/null
  vr tui keys escape >/dev/null
  vr tui keys enter >/dev/null
  vr tui wait --text "Objective:" --timeout 15 --save "$1" >/dev/null
}

case $SCN in
S04)
  m2_up tui ${M2_TUI_UP_EXTRA:-} || exit 1
  # 1
  vr tui type "/goal Write the numbers 1 to 3 into count.txt, one number per line, then stop." >/dev/null
  vr tui wait --text "◎ Goal · Active" --timeout 30 --save s04-active >/dev/null
  # 2 第一个 Goal Turn 有至少 2 次请求后暂停（横幅的请求数）
  vr tui wait --text "2 requests|3 requests|4 requests|5 requests" --timeout 120 --save s04-two-requests >/dev/null
  vr tui type "/goal pause" >/dev/null
  vr tui wait --text "◎ Goal · Paused" --timeout 30 --save s04-paused >/dev/null
  vr tui screen --save s04-paused-screen >/dev/null
  vr tui wait --status "state=ready|done|fail|cancel|error" --timeout 60 --save s04-idle >/dev/null
  vr tui snapshot --save s04-paused-snap >/dev/null
  # 3
  summary s04-summary
  vr tui screen --all --save s04-summary-screen >/dev/null
  # 4
  vr tui type "/goal resume" >/dev/null
  vr tui wait --text "Goal complete" --timeout 420 --save s04-complete >/dev/null
  vr tui wait --status "state=ready|done|fail|cancel|error" --hold 3 --timeout 120 --save s04-final-idle >/dev/null
  vr tui screen --all --save s04-final-screen >/dev/null
  vr tui snapshot --save s04 >/dev/null
  [ -n "${M2_TUI_UP_EXTRA:-}" ] && vr fault log --on tui --tail 500 --save fault-s04 >/dev/null
  m2_down
  ;;
S09)
  M2_UP_CONFIG=$(m2_config turns3 3 1) m2_up tui ${M2_TUI_UP_EXTRA:-} || exit 1
  # 1
  vr tui type "/goal Create files d1.txt, d2.txt, d3.txt, d4.txt, d5.txt one at a time, each containing its own number. In each response make at most one tool call. Keep working in this turn until all five exist." >/dev/null
  # 2
  vr tui wait --text "Budget limited" --timeout 420 --save s09-budget >/dev/null
  vr tui wait --status "state=ready|done|fail" --timeout 120 --save s09-idle >/dev/null
  vr tui screen --all --save s09-budget-screen >/dev/null
  vr tui snapshot --save s09 >/dev/null
  # 3 前提核对由分析脚本读 s09 的 Inspector；4 等 60 秒
  vr tui wait --text "Budget limited" --hold 60 --timeout 90 --save s09-hold >/dev/null
  vr tui snapshot --save s09-after-hold >/dev/null
  # 5
  vr tui type "/goal resume" >/dev/null
  vr tui wait --text "Goal resumed|rror|budget|Budget" --timeout 20 --save s09-resume >/dev/null
  vr tui screen --all --save s09-resume-screen >/dev/null
  vr tui wait --status "state=ready|done|fail|cancel|error" --hold 5 --timeout 60 --save s09-resume-idle >/dev/null
  vr tui snapshot --save s09-after-resume >/dev/null
  [ -n "${M2_TUI_UP_EXTRA:-}" ] && vr fault log --on tui --tail 500 --save fault-s09 >/dev/null
  m2_down
  ;;
*) echo "unknown scenario $SCN" >&2; exit 2 ;;
esac
m2_log "done"
