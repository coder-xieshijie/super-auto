#!/usr/bin/env bash
# 冒烟集（verify.md“冒烟集”5 条）在当前 checkout 的 HEAD 上跑一遍，三个入口各起一个实例。
# 接口、TUI 直接调用 smoke-api.sh、smoke-tui.sh（GV2_RUN 指向本实例）；Electron 用 smoke-electron.sh 的同一组命令，
# 只是授权模式按 rg1-electron.sh 的 set_permission 处理（--config 下默认已是“始终授权”，smoke-electron.sh 先点
# “智能授权”会点空、留下打开的菜单），并把每步经 vr 记进 steps.jsonl。
# 每个实例记录 git-head / git-status，结束时 rg1_down（down + auth-check.json）。
# 用法（agent-archon worktree 根目录）：
#   RG1_ROOT=<证据根> RG1_TAG=<前缀> [SMOKE_ENTRIES="electron api tui"] bash <tools>/m1-smoke.sh
# 本脚本按顺序执行三个入口。设了 RG1_UP_LOCK / M2_UP_LOCK 时 up 经共享锁错开（与并行的其他验证线共用）。
# Electron 打字后读回核对输入框（type_checked），不一致即中止、写 input-contaminated、down。
set -u
source "$(dirname "${BASH_SOURCE[0]}")/rg1-lib.sh"
API=/minimax-desktop/api/v1
SMOKE_ENTRIES=${SMOKE_ENTRIES:-electron api tui}

record_head() {
  git rev-parse HEAD >"$RUNDIR/git-head"
  git status --porcelain >"$RUNDIR/git-status"
}

smoke_api() {
  rg1_up runtime smoke-api || return 1
  record_head
  GV2_RUN=$RID GV2_TAG=$T-api bash "$RG1_TOOLS/smoke-api.sh" >"$RUNDIR/smoke.log" 2>&1
  echo "smoke-api rc=$?" >>"$RUNDIR/smoke.log"
  rg1_down runtime api
}

smoke_tui() {
  rg1_up tui smoke-tui || return 1
  record_head
  GV2_RUN=$RID GV2_TAG=$T bash "$RG1_TOOLS/smoke-tui.sh" >"$RUNDIR/smoke.log" 2>&1
  echo "smoke-tui rc=$?" >>"$RUNDIR/smoke.log"
  vr tui screen --all --save "$T-tui-final-all" >/dev/null
  vr tui snapshot --save "$T-tui-snap" >/dev/null
  rg1_down tui tui
}

set_permission() { # 同 rg1-electron.sh
  local want=$1 other n
  [ "$want" = 智能授权 ] && other=始终授权 || other=智能授权
  n=$(vr electron count --text "$want" --exact | jget "d.get('count')")
  if [ "${n:-0}" = 0 ]; then
    vr electron click --text "$other" --exact --timeout 10 >/dev/null
    vr electron click --text "$want" --exact --timeout 10 >/dev/null
  fi
  vr electron count --text "$want" --exact --save "$2" >/dev/null
}

# 输入框写入并核对（同 m2-lib.sh type_checked，2026-10-01 S03 事故后加）：测试窗口在屏幕上时，真实键盘输入可能混进输入框。
# 写入前非空先清空；写入后读回，逐字一致才返回 0；不一致清空重写一次，仍不一致返回 1。不一致只记长度和哈希，不记混入原文。
type_checked() {
  local want=$1 got i
  for i in 1 2; do
    got=$(node "$V" electron text --testid message-textarea --timeout 5 --run "$RID" 2>/dev/null | jget "(d.get('text') or '').strip()")
    if [ -n "$got" ]; then
      vr electron press --testid message-textarea --key "Meta+a" >/dev/null
      vr electron press --testid message-textarea --key Backspace >/dev/null
    fi
    vr electron type --testid message-textarea --value "$want" >/dev/null
    got=$(node "$V" electron text --testid message-textarea --timeout 5 --run "$RID" 2>/dev/null | jget "(d.get('text') or '').strip()")
    [ "$got" = "$want" ] && { echo "{\"try\":$i,\"match\":true}" >>"$RUNDIR/input-check.jsonl"; return 0; }
    python3 -c 'import hashlib,json,sys,time
w,g=sys.argv[1],sys.argv[2]
print(json.dumps({"at":int(time.time()*1000),"try":int(sys.argv[3]),"wantLen":len(w),"gotLen":len(g),"gotSha1":hashlib.sha1(g.encode()).hexdigest()[:12],"gotEndsWithWant":g.endswith(w)}))' "$want" "$got" "$i" >>"$RUNDIR/input-mismatch.jsonl"
    rg1_log "message-textarea content mismatch (try $i)"
  done
  return 1
}

smoke_electron() {
  rg1_up electron smoke-electron || return 1
  record_head
  local S
  {
    vr electron click --selector 'role=dialog >> role=button[name="关闭"]' --timeout 8 >/dev/null
    vr electron click --role button --name "关闭签到" --exact --timeout 5 >/dev/null
    set_permission 始终授权 "$T-e-mode"
    if ! type_checked "/goal $OBJ_COUNT3"; then
      # 输入被污染：清空、截图、down，作废本次 Electron 运行（不发送）
      vr electron press --testid message-textarea --key "Meta+a" >/dev/null
      vr electron press --testid message-textarea --key Backspace >/dev/null
      echo input-contaminated >"$RUNDIR/input-contaminated"
      vr electron screenshot --save "$T-input-contaminated" >/dev/null
      rg1_log "input contaminated: aborting electron smoke"
      rg1_down electron electron
      return 3
    fi
    vr electron click --testid send-button >/dev/null
    vr electron wait --testid thread-goal-banner --timeout 60 --save "$T-goal-banner" >/dev/null
    vr electron text --testid thread-goal-banner-status --save "$T-banner-status-start" >/dev/null
    S=$(vr api GET $API/agent/mavis/session --on electron | python3 -c 'import json,sys
d=json.load(sys.stdin).get("body") or {}
items=d.get("sessions") or d.get("items") or d.get("list") or []
items=[s for s in items if not s.get("parent_session_id")]
items.sort(key=lambda s: s.get("created_at") or 0)
print(items[-1]["session_id"] if items else "")')
    echo "$S" >"$RUNDIR/session"
    vr poll $API/session/$S/goal --on electron --until "$GOAL_TERMINAL" --show "$SHOW_RUN" --interval 3 --timeout 420 --save "$T-e-run" >/dev/null
    vr electron wait --testid goal-completion-marker --timeout 60 --save "$T-completion-marker" >/dev/null
    vr electron text --testid goal-completion-marker --save "$T-completion-marker-text" >/dev/null
    vr electron text --testid thread-goal-banner-status --save "$T-banner-status-final" >/dev/null
    vr electron aria --save "$T-aria" >/dev/null
    vr snapshot --session "$S" --on electron --save "$T-electron" >/dev/null
  } 2>>"$RUNDIR/smoke.log"
  rg1_down electron electron
}

for e in $SMOKE_ENTRIES; do
  FLOW=smoke-$e
  "smoke_$e"
  rg1_log "smoke $e done"
done
