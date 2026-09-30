#!/bin/bash
# Run from the repository root (or set GFD_REPO); evidence goes to $GFD_EVIDENCE/<subdir>.
# S01 per plan.md, with readings saved. Usage: gfd-s01.sh <evidence-subdir>
set -u
cd "${GFD_REPO:-$PWD}"
V=.agents/skills/verify-archon/scripts/verify-archon.mjs
EV=${GFD_EVIDENCE:-/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-final-result-delivery/evidence}/$1
mkdir -p $EV
node $V electron up --evidence-dir $EV 2>/dev/null > $EV/electron-up.json
R=$(jq -r .runId $EV/electron-up.json); echo "runId $R $(jq -c '{ok, mainUrl, git}' $EV/electron-up.json)"
node $V electron status --run $R 2>/dev/null > $EV/electron-status.json; jq -c '{userData}' $EV/electron-status.json
e() { node $V electron "$@" --run $R 2>/dev/null; }
e click --selector 'role=dialog >> role=button[name="关闭"]' | jq -c '{close_dialog: .ok}'
# Electron smoke
e type --testid message-textarea --value "Reply with exactly the word PONG and nothing else." >/dev/null
e click --testid send-button >/dev/null
e wait --testid assistant-segment-active --timeout 90 >/dev/null; sleep 5
e text --testid assistant-segment-active --save e-smoke-body | jq -c '{smoke_body: .text}'
e count --testid goal-completion-marker --save e-smoke-marker | jq -c '{smoke_marker: .count}'
# S01
e click --role button --name "新建任务" >/dev/null
e click --text "智能授权" --exact >/dev/null
e click --text "始终授权" --exact >/dev/null
e type --testid message-textarea --value "/goal Create a file named hello.html in the workspace. It should be a small web page whose main heading reads Hello Goal." >/dev/null
e click --testid send-button >/dev/null
e wait --testid thread-goal-banner --timeout 60 --save goal-banner | jq -c '{banner: .ok}'
S=$(node $V api GET /minimax-desktop/api/v1/agent/mavis/session --on electron --run $R 2>/dev/null | jq -r '[.body.sessions // .body.items // .body | .[]?] | sort_by(.created_at) | last | .session_id // .id'); echo "S=$S"
node $V poll /minimax-desktop/api/v1/session/$S/goal --on electron --run $R --until goal.status='complete|paused|blocked|budget_limited|usage_limited' --show goal.status,goal.status_reason,goal.execution.wait_reason,goal.turns_used --interval 3 --timeout 420 --save e-run 2>/dev/null | jq -c '.final.goal | {status,status_reason,backend:.last_verification.backend,verdict:.last_verification.verdict}'
sleep 3
node $V snapshot --session $S --on electron --run $R --save s01 2>/dev/null | jq -c '{snapshot: .ok}'
e screenshot --save s01-complete >/dev/null
e text --testid assistant-segment-active --save s01-body-text | jq -c '{body: .text}'
e aria --selector '[data-testid="assistant-segment-active"]' --save s01-body-aria >/dev/null
e count --selector '[data-testid="assistant-segment-active"] [data-testid="deliver-assets-card"]:has-text("hello.html")' --save s01-result-hello-cards-in-body | jq -c '{body_cards: .count}'
e count --testid goal-lifted-delivery-cards --save s01-lifted-area | jq -c '{lifted_area: .count}'
e count --selector '[data-testid="goal-lifted-delivery-cards"] [data-testid="deliver-assets-card"]:has-text("hello.html")' --save s01-result-hello-cards-lifted | jq -c '{lifted_cards: .count}'
e text --testid goal-completion-marker --save s01-marker | jq -c '{marker: .text}'
e text --testid thread-goal-banner-status --save s01-banner | jq -c '{banner: .text}'
# card click: body card, else lifted card
if [ "$(jq -r .result.count $(ls $EV/*-s01-result-hello-cards-in-body.json | tail -1))" != "0" ]; then CARD='[data-testid="assistant-segment-active"]'; else CARD='[data-testid="goal-lifted-delivery-cards"]'; fi
e click --selector "$CARD [data-testid=\"deliver-assets-card\"]:has-text(\"hello.html\") [data-testid=\"file-display\"]" --save s01-card-click | jq -c '{card_click: .ok}'
sleep 3
e click --role button --name "关闭 Mini App 提示" >/dev/null
e text --selector '[role="tab"][aria-selected="true"]' --save s01-preview-tab-title | jq -c '{tab: .text}'
e click --testid file-panel-browser-address-input >/dev/null; sleep 1
e aria --selector '[data-testid="file-panel-browser-address-input"]' --save s01-preview-address | jq -r .aria
e screenshot --save s01-preview >/dev/null
e click --testid turn-process-trigger --save s01-process-expanded >/dev/null; sleep 2
e count --selector '[data-testid="message-item"][data-role="assistant"] [data-testid="deliver-assets-card"]:has-text("hello.html")' --save s01-expanded-hello-cards | jq -c '{expanded_cards: .count}'
e aria --selector '[data-testid="message-item"][data-role="assistant"]' --save s01-expanded-aria >/dev/null
e click --testid workspace-button >/dev/null; sleep 2
e text --testid workspace-panel --save s01-workspace-panel >/dev/null
e count --selector '[data-testid="workspace-panel"] button:has-text("hello.html")' --save s01-workspace-hello-count | jq -c '{panel_hello: .count}'
# reload
e reload --save s01-after-reload | jq -c '{reload: .ok}'
e wait --role button --name "新建任务" --timeout 90 >/dev/null
e wait --testid assistant-segment-active --timeout 60 >/dev/null; sleep 2
e text --testid assistant-segment-active --save s01-reload-body-text | jq -c '{reload_body: .text}'
e count --selector '[data-testid="assistant-segment-active"] [data-testid="deliver-assets-card"]:has-text("hello.html")' --save s01-reload-result-hello-cards-in-body | jq -c '{reload_body_cards: .count}'
e count --testid goal-lifted-delivery-cards --save s01-reload-lifted-area | jq -c '{reload_lifted_area: .count}'
e text --testid goal-completion-marker --save s01-reload-marker | jq -c '{reload_marker: .text}'
e text --testid thread-goal-banner-status --save s01-reload-banner | jq -c '{reload_banner: .text}'
e click --testid turn-process-trigger --save s01-reload-process-expanded >/dev/null; sleep 2
e count --selector '[data-testid="message-item"][data-role="assistant"] [data-testid="deliver-assets-card"]:has-text("hello.html")' --save s01-reload-expanded-hello-cards | jq -c '{reload_expanded_cards: .count}'
if [ "$(e count --testid workspace-panel | jq -r .count)" = "0" ]; then e click --testid workspace-button >/dev/null; sleep 2; fi
e text --testid workspace-panel --save s01-reload-workspace-panel >/dev/null
e count --selector '[data-testid="workspace-panel"] button:has-text("hello.html")' --save s01-reload-workspace-hello-count | jq -c '{reload_panel_hello: .count}'
echo "RUN=$R SESSION=$S"
