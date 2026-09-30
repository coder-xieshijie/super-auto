#!/bin/bash
# Run from the repository root (or set GFD_REPO); evidence goes to $GFD_EVIDENCE/<subdir>.
# S02 per verify.md, then the TUI smoke message. Usage: gfd-s02.sh <evidence-subdir>
set -u
cd "${GFD_REPO:-$PWD}"
V=.agents/skills/verify-archon/scripts/verify-archon.mjs
EV=${GFD_EVIDENCE:-/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-final-result-delivery/evidence}/$1
mkdir -p $EV
UP=$(node $V tui up --evidence-dir $EV 2>/dev/null); echo "$UP" > $EV/tui-up.json
R=$(echo "$UP" | jq -r .runId); echo "runId $R ok=$(echo "$UP" | jq -r .ok) state=$(echo "$UP" | jq -r .status.state)"
node $V tui type "/goal Create a file named hello.html in the workspace. It should be a small web page whose main heading reads Hello Goal." --run $R 2>/dev/null | jq -c '{ok}'
node $V tui wait --text "Goal complete" --timeout 420 --save tui-s02 --run $R 2>/dev/null | jq -c '{ok}'
sleep 3
node $V tui screen --all --save tui-s02-screen --run $R 2>/dev/null | jq -c '{ok, status}'
node $V tui snapshot --save s02 --run $R 2>/dev/null | jq -c '{ok}'
node $V tui type "Reply with exactly the word PONG and nothing else." --run $R 2>/dev/null | jq -c '{ok}'
node $V tui wait --status state=done --timeout 120 --save tui-smoke --run $R 2>/dev/null | jq -c '{ok}'
node $V tui screen --save tui-smoke-screen --run $R 2>/dev/null | jq -c '{ok, status}'
echo "RUN=$R"
