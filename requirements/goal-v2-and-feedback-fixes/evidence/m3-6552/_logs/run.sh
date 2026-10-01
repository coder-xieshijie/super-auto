#!/usr/bin/env bash
# m3-6552 @ 6552dcbd9c 编排：三条链并行，链内串行；所有 up 经同一把锁串行并错开 6 秒。
set -u
export M2_ROOT=/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/m3-6552
export T=/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/tools
export M2_UP_LOCK=/tmp/gv2-m3-6552-up.lock M3_UP_LOCK=/tmp/gv2-m3-6552-up.lock
L=$M2_ROOT/_logs
cd /Users/minimax/code/mm/worktrees/agent-archon/gv2-tests || exit 1
rmdir $M2_UP_LOCK 2>/dev/null
log() { echo "$(date +%T) $*" >>"$L/$1.chain.log"; }
( c=T1
  bash $T/m23-obs-budget-steer.sh run1 >"$L/OBS-run1.log" 2>&1; log $c "OBS run1 rc=$?"
  bash $T/m23-obs-budget-steer.sh run2 >"$L/OBS-run2.log" 2>&1; log $c "OBS run2 rc=$?" ) &
sleep 2
( c=T2
  OBS_GRACE=0 bash $T/m23-obs-budget-steer.sh run1 >"$L/OBS-g0-run1.log" 2>&1; log $c "OBS-g0 run1 rc=$?"
  M2_TUI_UP_EXTRA=--fault bash $T/m2-tui.sh S04 run1 >"$L/S04-run1.log" 2>&1; log $c "S04 run1 rc=$?" ) &
sleep 2
( c=T3
  bash $T/m2-s41.sh seed >"$L/S41-seed.log" 2>&1; log $c "S41 seed rc=$?"
  bash $T/m2-s41-tui.sh run1 >"$L/S41-tui-run1.log" 2>&1; log $c "S41 tui-run1 rc=$?" ) &
wait
echo "$(date +%T) all chains done" >>"$L/run.log"
