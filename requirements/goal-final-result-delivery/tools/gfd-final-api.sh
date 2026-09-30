#!/bin/bash
# Run from the repository root (or set GFD_REPO); evidence goes to $GFD_EVIDENCE/<subdir>.
# Final-head API entry: smoke set, then S03. Usage: gfd-final-api.sh <evidence-subdir>
set -u
cd "${GFD_REPO:-$PWD}"
V=.agents/skills/verify-archon/scripts/verify-archon.mjs
EV=${GFD_EVIDENCE:-/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-final-result-delivery/evidence}/$1
mkdir -p $EV
UP=$(node $V up --evidence-dir $EV 2>/dev/null); echo "$UP" > $EV/up.json
R=$(echo "$UP" | jq -r .runId); echo "runId $R head=$(echo "$UP" | jq -r .git.head) dirty=$(echo "$UP" | jq -r .git.dirty) model=$(echo "$UP" | jq -c .model)"
"$(dirname "$0")/gfd-smoke-api.sh" $R smoke
S=$(node $V api POST /minimax-desktop/api/v1/agent/mavis/session --run $R --data '{"title":"s03"}' --save s03-session 2>/dev/null | jq -r .body.session_id)
echo "s03 session $S"
node $V api POST /minimax-desktop/api/v1/session/$S/goal --run $R --data '{"objective":"Create a file named hello.html in the workspace. It should be a small web page whose main heading reads Hello Goal."}' --save s03-create 2>/dev/null | jq -c '.body.goal | {status}'
node $V poll /minimax-desktop/api/v1/session/$S/goal --run $R --until goal.status='complete|paused|blocked|budget_limited|usage_limited' --show goal.status,goal.status_reason --interval 4 --timeout 420 --save s03-run 2>/dev/null | jq -c '.final.goal | {status,status_reason,backend:.last_verification.backend,verdict:.last_verification.verdict}'
node $V snapshot --session $S --run $R --save s03 2>/dev/null | jq -c '{ok}'
node $V api POST /minimax-desktop/api/v1/session/$S/message --run $R --data '{"content":"Create a file named after.txt in the workspace containing the word ok."}' --save s03-after 2>/dev/null | jq -c '{ok, status: .status}'
node $V snapshot --session $S --run $R --save s03-after 2>/dev/null | jq -c '{ok}'
echo "RUN=$R SESSION=$S"
