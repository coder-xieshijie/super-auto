#!/bin/bash
# Run from the repository root (or set GFD_REPO); evidence goes to $GFD_EVIDENCE/<subdir>.
# Regression: Goal lifecycle interface steps and completion "no continuation". Usage: <runId> <s03-session>
set -u
cd "${GFD_REPO:-$PWD}"
V=.agents/skills/verify-archon/scripts/verify-archon.mjs
R=$1; S03=$2
q() { jq -c "$1" 2>/dev/null; }
# completion.md: 完成后不续跑
node $V api POST /minimax-desktop/api/v1/session/$S03/message --run $R --data '{"content":"Reply with just OK."}' --save reg-completion-plain 2>/dev/null | q '{ok,status}'
node $V poll /minimax-desktop/api/v1/session/$S03/goal --run $R --until goal.status=complete --hold 10 --show goal.status,goal.turns_used --save reg-completion-no-continuation 2>/dev/null | q '{ok, final: (.final.goal | {status, turns_used})}'
node $V api GET /minimax-desktop/api/v1/session/$S03/queue --run $R --save reg-completion-queue 2>/dev/null | q '{items: (.body.items|length)}'
# lifecycle.md 接口
L=$(node $V api POST /minimax-desktop/api/v1/agent/mavis/session --run $R --data '{"title":"goal lifecycle"}' --save reg-lifecycle-session 2>/dev/null | jq -r .body.session_id)
echo "lifecycle session $L"
node $V api POST /minimax-desktop/api/v1/session/$L/goal --run $R --data '{"objective":"Write the numbers 1 to 3 into count.txt, one number per line, then stop.","token_budget":80000}' --save reg-lifecycle-create 2>/dev/null | q '.body.goal | {status, token_budget}'
node $V api PATCH /minimax-desktop/api/v1/session/$L/goal --run $R --data '{"status":"paused"}' --save reg-lifecycle-pause 2>/dev/null | q '.body.goal | {status, status_reason}'
node $V api PATCH /minimax-desktop/api/v1/session/$L/goal --run $R --data '{"objective":"Write the numbers 1 to 4 into count.txt, one number per line, then stop."}' --save reg-lifecycle-edit-paused 2>/dev/null | q '.body.goal | {status, status_reason, objective}'
node $V poll /minimax-desktop/api/v1/session/$L/goal --run $R --until goal.status=paused --hold 8 --show goal.status,goal.turns_used --save reg-lifecycle-still-paused 2>/dev/null | q '{ok}'
node $V api PATCH /minimax-desktop/api/v1/session/$L/goal --run $R --data '{"status":"active"}' --save reg-lifecycle-resume 2>/dev/null | q '.body.goal | {status}'
node $V poll /minimax-desktop/api/v1/session/$L/goal --run $R --until goal.status='complete|paused|blocked|budget_limited|usage_limited' --show goal.status,goal.status_reason,goal.execution.wait_reason,goal.turns_used --interval 4 --timeout 420 --save reg-lifecycle-run 2>/dev/null | q '.final.goal | {status, status_reason, backend: .last_verification.backend}'
node $V snapshot --session $L --run $R --save reg-lifecycle 2>/dev/null | q '{ok}'
node $V api DELETE /minimax-desktop/api/v1/session/$L/goal --run $R --save reg-lifecycle-clear 2>/dev/null | q '{ok, status}'
node $V api GET /minimax-desktop/api/v1/session/$L/goal --run $R --save reg-lifecycle-after-clear 2>/dev/null | q '{body}'
# replace a completed Goal (S03 session)
node $V api POST /minimax-desktop/api/v1/session/$S03/goal --run $R --data '{"objective":"Reply with the single word DONE.","token_budget":40000}' --save reg-completion-replace 2>/dev/null | q '.body.goal | {goal_id, status, turns_used}'
node $V api DELETE /minimax-desktop/api/v1/session/$S03/goal --run $R --save reg-completion-replace-clear 2>/dev/null | q '{ok, status}'
echo "LIFECYCLE=$L"
