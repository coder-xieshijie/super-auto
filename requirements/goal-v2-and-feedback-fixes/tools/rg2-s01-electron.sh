#!/usr/bin/env bash
# RG2：第 2 项 verify（origin/fix/goal-final-result-delivery:.harness/docs/specs/goal-final-result-delivery/verify.md）的 S01，
# Electron 入口。步骤照该 verify 的 S01（1–8），读数沿用第 2 项交付时的 gfd-s01.sh；启动、输入核对、登录核对用本需求的
# m2-lib/m3-lib（共享启动锁、type_checked、--config、auth-check）。
# 用法（agent-archon 被测检出根目录，已 prepare runtime tui electron）：
#   bash <tools>/rg2-s01-electron.sh <尝试名>
# 证据：<M2_ROOT>/RG2-S01/<尝试名>/。判定：python3 <tools>/rg2-s01-analyze.py <尝试名>
set -u
source "$(dirname "${BASH_SOURCE[0]}")/m3-lib.sh"
ATTEMPT=$1
E() { vr electron "$@"; }
HELLO_BODY='[data-testid="assistant-segment-active"] [data-testid="deliver-assets-card"]:has-text("hello.html")'
HELLO_LIFTED='[data-testid="goal-lifted-delivery-cards"] [data-testid="deliver-assets-card"]:has-text("hello.html")'
HELLO_ALL='[data-testid="message-item"][data-role="assistant"] [data-testid="deliver-assets-card"]:has-text("hello.html")'
HELLO_PANEL='[data-testid="workspace-panel"] button:has-text("hello.html")'
OBJ="Create a file named hello.html in the workspace. It should be a small web page whose main heading reads Hello Goal."

# 第 4、6、7 步的读数；<前缀> 为 s01 或 s01-reload
readings() {
  local p=$1
  E text --testid assistant-segment-active --save "$p-body-text" >/dev/null
  E aria --selector '[data-testid="assistant-segment-active"]' --save "$p-body-aria" >/dev/null
  E count --selector "$HELLO_BODY" --save "$p-result-hello-cards-in-body" >/dev/null
  E count --testid goal-lifted-delivery-cards --save "$p-lifted-area" >/dev/null
  E count --selector "$HELLO_LIFTED" --save "$p-result-hello-cards-lifted" >/dev/null
  E text --testid goal-completion-marker --save "$p-marker" >/dev/null
  E text --testid thread-goal-banner-status --save "$p-banner" >/dev/null
}
expanded_and_panel() {
  local p=$1
  E click --testid turn-process-trigger --save "$p-process-expanded" >/dev/null; sleep 2
  E count --selector "$HELLO_ALL" --save "$p-expanded-hello-cards" >/dev/null
  E aria --selector '[data-testid="message-item"][data-role="assistant"]' --save "$p-expanded-aria" >/dev/null
  if [ "$(E count --testid workspace-panel | jget "d.get('count')")" = 0 ]; then E click --testid workspace-button --save "$p-workspace-button" >/dev/null; sleep 2; fi
  E text --testid workspace-panel --save "$p-workspace-panel" >/dev/null
  E count --selector "$HELLO_PANEL" --save "$p-workspace-hello-count" >/dev/null
}

m2_begin RG2-S01 "$ATTEMPT"
m3_up electron || exit 1
E status --save electron-status >"$OUT/electron-status.json"
E config --save electron-config >/dev/null
m2_close_popups
E text --text "始终授权" --exact --timeout 5 --save permission-mode >/dev/null
# 1
m2_send_goal_electron "$OBJ" s01-create
# 2
S=$(m2_latest_session); echo "$S" >"$OUT/session"
vr poll $API/session/$S/goal --on electron --until "$TERMINAL" --show "goal.status,goal.status_reason,goal.execution.wait_reason,goal.requests_used" --interval 3 --timeout 420 --save e-run >/dev/null
E wait --testid stop-button --state hidden --timeout 120 >/dev/null
sleep 3
# 3
vr snapshot --session "$S" --on electron --save s01 >/dev/null
E screenshot --save s01-complete >/dev/null
# 4
readings s01
# 5 点结果区里的 hello.html 卡片：正文里有就点正文的，否则点提升区的
if [ "$(E count --selector "$HELLO_BODY" | jget "d.get('count')")" != 0 ]; then CARD="$HELLO_BODY"; else CARD="$HELLO_LIFTED"; fi
echo "$CARD" >"$OUT/s01-card-clicked-selector"
E click --selector "$CARD [data-testid=\"file-display\"]" --save s01-card-click >/dev/null
sleep 3
E click --role button --name "关闭 Mini App 提示" --timeout 3 >/dev/null
E text --selector '[role="tab"][aria-selected="true"]' --save s01-preview-tab-title >/dev/null
E click --testid file-panel-browser-address-input --timeout 5 >/dev/null; sleep 1
E aria --selector '[data-testid="file-panel-browser-address-input"]' --save s01-preview-address >/dev/null
E screenshot --save s01-preview >/dev/null
# 6、7
expanded_and_panel s01
# 8 重载渲染进程后重复 4、6、7
E reload --save s01-after-reload >/dev/null
E wait --role button --name "新建任务" --timeout 90 >/dev/null
E wait --testid assistant-segment-active --timeout 60 >/dev/null; sleep 2
readings s01-reload
expanded_and_panel s01-reload
vr api GET $API/session/$S/goal --on electron --save s01-goal-final >/dev/null
E screenshot --save final-ui >/dev/null
m2_down
# 完成那一轮的结构（历史、Inspector、事件顺序）
SNAP=$(ls "$OUT"/[0-9][0-9][0-9]-s01.json 2>/dev/null | tail -1)
[ -n "$SNAP" ] && node "$M3_TOOLS/rg2-turn-facts.mjs" "${SNAP%.json}" >"$OUT/s01-turn-facts.json" 2>"$OUT/s01-turn-facts.stderr"
m2_log "RG2-S01 done session=$S"
