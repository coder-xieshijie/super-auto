#!/usr/bin/env bash
# M2 S32：接在 flow A 的 Electron 实例上（m2-electron.sh A 结束时实例仍在运行）生成 Goal 诊断，最后 down 该实例。
# 用法（agent-archon worktree 根目录）：bash <tools>/m2-s32.sh <flow A 尝试名>
# 同意框按钮用鼠标点击（electron click）；点击失败时再用键盘（electron press --key Enter）兜底，两者都记入 steps.jsonl。
# 证据写在 <M2_ROOT>/S07/<尝试名>/ 的 s32-* 文件与 s32-diagnostics/。
set -u
source "$(dirname "${BASH_SOURCE[0]}")/m2-lib.sh"
ATTEMPT=$1
SC=S32
OUT="$M2_ROOT/S07/$ATTEMPT"
RID=$(cat "$OUT/runId")
KIND=electron
E() { vr electron "$@"; }
HOME_VA=${VERIFY_ARCHON_HOME:-$(node -e "console.log(require('os').tmpdir())")/verify-archon}
DIAG="$HOME_VA/$RID/data/v2/observability/diagnostics/goal"
nfiles() { ls "$DIAG" 2>/dev/null | grep -c '^goal-decision-evidence' ; }

consent() { # consent <按钮名> <save 名>：先鼠标，失败再键盘
  if ! E click --role button --name "$1" --exact --timeout 8 --save "$2-mouse" >/dev/null; then
    m2_log "mouse click on $1 failed; falling back to keyboard"
    E press --role button --name "$1" --exact --key Enter --save "$2-keyboard" >/dev/null
  fi
}

SIDS=$(cat "$OUT/s32-session-ids")
E click --text "开发者面板" --timeout 10 --save s32-open-dock >/dev/null
E click --role button --name "展开开发者面板" --save s32-expand-dock >/dev/null
# 1 拒绝
E click --testid developer-tools-goal-diagnostics-generate --save s32-generate-1 >/dev/null
E screenshot --save s32-consent >/dev/null
consent "拒绝" s32-decline
sleep 2
echo "files after decline: $(nfiles)" >"$OUT/s32-files-after-decline.txt"
E count --testid developer-tools-goal-diagnostics-feedback --save s32-after-decline-feedback >/dev/null
# 2 同意
E click --testid developer-tools-goal-diagnostics-generate --save s32-generate-2 >/dev/null
E screenshot --save s32-consent-2 >/dev/null
consent "同意并生成" s32-accept
E wait --testid developer-tools-goal-diagnostics-feedback --timeout 30 >/dev/null
E text --testid developer-tools-goal-diagnostics-feedback --save s32-feedback >/dev/null
E count --testid developer-tools-goal-diagnostics-reveal --save s32-reveal-count >/dev/null
# 3 读内容与诊断后的 Goal
mkdir -p "$OUT/s32-diagnostics"
for f in "$DIAG"/goal-decision-evidence*; do
  [ -f "$f" ] && cp "$f" "$OUT/s32-diagnostics/" && echo "$f" >>"$OUT/s32-diagnostics/source-path.txt"
done
echo "files after accept: $(nfiles)" >"$OUT/s32-files-after-accept.txt"
for s in $SIDS; do vr api GET $API/session/$s/goal --on electron --save "s32-after-$s" >/dev/null; done
E screenshot --save s32-generated >/dev/null
m2_down
m2_log "S32 done"
