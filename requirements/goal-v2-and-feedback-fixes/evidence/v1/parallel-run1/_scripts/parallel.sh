#!/usr/bin/env bash
# R103 实跑：3 Electron（--auth-lease 30）+ 1 接口 + 1 TUI，各自反复跑简单 Goal 到 DEADLINE，然后 down
set -u
export M2_ROOT=/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/v1/parallel-run1
export M3_UP_LOCK=/tmp/gv2-v1-up.lock M2_UP_LOCK=/tmp/gv2-v1-up.lock
mkdir -p "$M2_ROOT"
cd /Users/minimax/code/mm/worktrees/agent-archon/gv2-verify-tools
git rev-parse HEAD >"$M2_ROOT/git-head"; git status --porcelain >"$M2_ROOT/git-status"
START=$(date +%s); DEADLINE=$((START + 22*60))
echo "{\"startEpoch\":$START,\"deadlineEpoch\":$DEADLINE,\"electronAuthLease\":30}" >"$M2_ROOT/plan.json"
W=/tmp/gv2-v1/worker.sh
bash $W runtime api $DEADLINE >"$M2_ROOT/worker-api.log" 2>&1 &
bash $W tui tui $DEADLINE >"$M2_ROOT/worker-tui.log" 2>&1 &
for i in 1 2 3; do bash $W electron electron-$i $DEADLINE --auth-lease 30 >"$M2_ROOT/worker-electron-$i.log" 2>&1 & done
wait
echo "all workers finished $(date +%s)" >>"$M2_ROOT/worker-done.txt"
