#!/usr/bin/env bash
# M2 S41 步骤 4（TUI /goal 摘要）一次跑完：把 m2-163f 里手动执行的按键序列（tui-run2/manual-steps.txt）写成脚本。
# 用法（agent-archon worktree 根目录）：bash <tools>/m2-s41-tui.sh <尝试名>；种子取 <M2_ROOT>/S41/seed/runId
set -u
source "$(dirname "${BASH_SOURCE[0]}")/m2-lib.sh"
m2_begin S41 "tui-$1"
SEED=$(cat "$M2_ROOT/S41/seed/runId")
m2_up tui --from-data "$SEED" || exit 1
vr tui screen --save s41-tui-start >/dev/null
# /sessions，Ctrl+A 切到全部会话，Enter 打开唯一的会话
vr tui type "/sessions" >/dev/null
sleep 2
vr tui type $'\x01' --no-submit >/dev/null
sleep 2
vr tui screen --save s41-tui-sessions-panel >/dev/null
vr tui keys enter >/dev/null
sleep 3
vr tui screen --save s41-tui-opened >/dev/null
# /goal 摘要（lifecycle.md 的按键顺序）
vr tui type "/goal" --no-submit >/dev/null
vr tui keys escape >/dev/null
vr tui keys enter >/dev/null
vr tui wait --text "Objective:" --timeout 15 --save s41-tui-summary >/dev/null
vr tui screen --all --save s41-tui-summary-screen >/dev/null
m2_down
m2_log "S41 tui done"
