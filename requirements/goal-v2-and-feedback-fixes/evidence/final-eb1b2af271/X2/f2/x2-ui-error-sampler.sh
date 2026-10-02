#!/usr/bin/env bash
# X2 f2 外部界面采样：output-error-alert / status-indicator 数量，直到闸门结束后 15 秒
cd /Users/minimax/code/mm/worktrees/agent-archon/gv2-tests
while [ ! -f /Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/final-eb1b2af271/X2/f2/x2-gate-done-at-ms ] || [ $(( $(date +%s) - $(cut -c1-10 /Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/final-eb1b2af271/X2/f2/x2-gate-done-at-ms) )) -lt 15 ]; do
  a=$(node .agents/skills/verify-archon/scripts/verify-archon.mjs electron count --testid output-error-alert --run 20261002-012214-718f5c 2>/dev/null | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("count"))
except Exception: print("")')
  s=$(node .agents/skills/verify-archon/scripts/verify-archon.mjs electron count --testid status-indicator --run 20261002-012214-718f5c 2>/dev/null | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("count"))
except Exception: print("")')
  echo "{\"at\":$(python3 -c 'import time;print(int(time.time()*1000))'),\"outputErrorAlert\":\"$a\",\"statusIndicator\":\"$s\"}" >> /Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/final-eb1b2af271/X2/f2/x2-ui-error-samples.jsonl
done
