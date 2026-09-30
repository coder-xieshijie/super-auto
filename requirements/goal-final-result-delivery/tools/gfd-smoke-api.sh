#!/bin/bash
# Run from the repository root (or set GFD_REPO); evidence goes to $GFD_EVIDENCE/<subdir>.
# Baseline/post-change API smoke per verify.md. Usage: gfd-smoke-api.sh <runId> <prefix>
set -u
cd "${GFD_REPO:-$PWD}"
V=.agents/skills/verify-archon/scripts/verify-archon.mjs
R=$1; P=$2
node $V doctor --run $R > /tmp/$P-doctor.json 2>&1; echo "doctor ok=$(jq -r .ok /tmp/$P-doctor.json)"
S=$(node $V api POST /minimax-desktop/api/v1/agent/mavis/session --run $R --data '{"title":"smoke"}' --save $P-smoke-session 2>/dev/null | jq -r .body.session_id)
echo "smoke session $S"
node $V api POST /minimax-desktop/api/v1/session/$S/message --run $R --data '{"content":"Reply with exactly the word PONG and nothing else."}' --save $P-smoke-send 2>/dev/null > /tmp/$P-smoke-send.json
echo "rewound frames: $(jq '[.frames[]? | select(.type=="messages-rewound")] | length' /tmp/$P-smoke-send.json)"
node $V api GET /minimax-desktop/api/v1/session/$S/message --run $R --save $P-smoke-history 2>/dev/null > /tmp/$P-smoke-history.json
echo "assistant PONG: $(jq '[.body.messages[]? | select(.role=="assistant") | .msg_content] ' -c /tmp/$P-smoke-history.json)"
G=$(node $V api POST /minimax-desktop/api/v1/agent/mavis/session --run $R --data '{"title":"goal lifecycle"}' --save $P-lifecycle-session 2>/dev/null | jq -r .body.session_id)
echo "goal session $G"
node $V api POST /minimax-desktop/api/v1/session/$G/goal --run $R --data '{"objective":"Write the numbers 1 to 3 into count.txt, one number per line, then stop.","token_budget":80000}' --save $P-lifecycle-create 2>/dev/null | jq -c '.body.goal | {status,token_budget}'
node $V poll /minimax-desktop/api/v1/session/$G/goal --run $R --until goal.status='complete|paused|blocked|budget_limited|usage_limited' --show goal.status,goal.status_reason,goal.execution.wait_reason,goal.turns_used --interval 4 --timeout 420 --save $P-lifecycle-run 2>/dev/null | jq -c '.final.goal | {status,status_reason,backend:.last_verification.backend,verdict:.last_verification.verdict}'
node $V snapshot --session $G --run $R --save $P-lifecycle 2>/dev/null | jq -c '{ok}'
echo "GOAL_SESSION=$G SMOKE_SESSION=$S"
