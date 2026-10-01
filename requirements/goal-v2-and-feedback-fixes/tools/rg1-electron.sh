#!/usr/bin/env bash
# RG1 Electron 入口：功能地图索引“Electron”列的全部子功能，命令照抄各地图“Electron”一节。
# 每个流程起自己的 Electron 实例（electron up --config $RG1_CONFIG，zh-staging 构建），跑完 snapshot --on electron、
# electron down、整理证据。--config 使输入框默认“始终授权”；授权卡片子功能在发送前改选“智能授权”。
# 用法（agent-archon worktree 根目录）：
#   RG1_ROOT=<证据根> RG1_TAG=<前缀> [RG1_FLOWS="lifecycle continuation-bg attachments questionnaire-manual questionnaire-auto"] bash <tools>/rg1-electron.sh
# 不要和 rg1-api.sh 同时运行：electron up 要求共享登录剩余至少 50 分钟，不足时会刷新登录，正在运行的接口实例手里的旧 token
# 随之失效（内容审核 401、输出被撤回）。Electron 实例注入的 token 也不会自动更新，别的进程刷新登录后会跳到登录页。
set -u
source "$(dirname "${BASH_SOURCE[0]}")/rg1-lib.sh"
API=/minimax-desktop/api/v1

close_popups() { # 首次启动的“模型上新”对话框和“每日签到”浮层；没有时失败，忽略
  vr electron click --selector 'role=dialog >> role=button[name="关闭"]' --timeout 8 >/dev/null
  vr electron click --role button --name "关闭签到" --exact --timeout 5 >/dev/null
  return 0
}

# set_permission <智能授权|始终授权> <save>：输入框的授权模式按钮显示目标值时不动，否则打开菜单改选
set_permission() {
  local want=$1 other n
  [ "$want" = 智能授权 ] && other=始终授权 || other=智能授权
  n=$(vr electron count --text "$want" --exact | jget "d.get('count')")
  if [ "${n:-0}" = 0 ]; then
    vr electron click --text "$other" --exact --timeout 10 >/dev/null
    vr electron click --text "$want" --exact --timeout 10 >/dev/null
  fi
  vr electron count --text "$want" --exact --save "$2" >/dev/null
}

latest_session() { # 按 created_at 取最新的顶层会话
  vr api GET $API/agent/mavis/session --on electron | python3 -c 'import json,sys
d=json.load(sys.stdin).get("body") or {}
items=d.get("sessions") or d.get("items") or d.get("list") or []
items=[s for s in items if not s.get("parent_session_id")]
items.sort(key=lambda s: s.get("created_at") or 0)
print(items[-1]["session_id"] if items else "")'
}

# 输入框写入并核对（2026-10-01 最终全量自验加，规则同 m2-lib.sh 的 type_checked）：测试窗口在屏幕上时真实键盘输入
# 可能混进输入框。写入前输入框非空先清空；写入（type，或 fill 整体替换）后读回，必须与预期逐字一致才返回 0；
# 不一致清空重写一次，仍不一致返回 1。不一致时只记长度和哈希（input-mismatch.jsonl），不记录混入的原文。
rg1_type_checked() { # rg1_type_checked <value> [type|fill]
  local want=$1 mode=${2:-type} got i
  for i in 1 2; do
    got=$(node "$V" electron text --testid message-textarea --timeout 5 --run "$RID" 2>/dev/null | jget "(d.get('text') or '').strip()")
    if [ -n "$got" ] && [ "$mode" = type ]; then
      vr electron press --testid message-textarea --key "Meta+a" >/dev/null
      vr electron press --testid message-textarea --key Backspace >/dev/null
    fi
    vr electron "$mode" --testid message-textarea --value "$want" >/dev/null
    got=$(node "$V" electron text --testid message-textarea --timeout 5 --run "$RID" 2>/dev/null | jget "(d.get('text') or '').strip()")
    [ "$got" = "$want" ] && return 0
    python3 -c 'import hashlib,json,sys,time
w,g=sys.argv[1],sys.argv[2]
print(json.dumps({"at":int(time.time()*1000),"try":int(sys.argv[3]),"wantLen":len(w),"gotLen":len(g),"gotSha1":hashlib.sha1(g.encode()).hexdigest()[:12],"gotEndsWithWant":g.endswith(w)}))' "$want" "$got" "$i" >>"$RUNDIR/input-mismatch.jsonl"
    rg1_log "message-textarea content mismatch (try $i)"
  done
  return 1
}
# 输入被污染：清空输入框、截图、down，作废本流程（流程在子 shell 里运行，exit 3 只结束该流程）
rg1_input_abort() {
  vr electron press --testid message-textarea --key "Meta+a" >/dev/null
  vr electron press --testid message-textarea --key Backspace >/dev/null
  echo input-contaminated >"$RUNDIR/input-contaminated"
  rg1_log "input contaminated: aborting flow"
  vr electron screenshot --save "$T-input-contaminated" >/dev/null
  rg1_down electron electron
  exit 3
}

send_goal() { # send_goal <objective> <save 前缀>
  rg1_type_checked "/goal $1" || rg1_input_abort
  vr electron click --testid send-button >/dev/null
  vr electron wait --testid thread-goal-banner --timeout 60 --save "$2--banner" >/dev/null
}

# 智能授权下跑到终态：分段 poll，每段之间查“仅本对话”卡片并点击；横幅为“正在验证目标结果”时出现的卡片记在
# completion.verify-auth-card，其余记在 lifecycle.auth-card。
run_with_cards() { # run_with_cards <session> <总秒数>
  local S=$1 deadline=$(( $(date +%s) + $2 )) n=0 st cnt sub captured=0
  while [ "$(date +%s)" -lt "$deadline" ]; do
    if vr poll $API/session/$S/goal --on electron --until "$GOAL_TERMINAL" --show "$SHOW_RUN" --interval 3 --timeout 15 >/dev/null; then
      break
    fi
    st=$(vr electron text --testid thread-goal-banner-status --timeout 5 | jget "d.get('text')")
    if [[ "$st" == *正在验证* ]] && [ $captured = 0 ]; then
      vr electron text --testid thread-goal-banner-status --save "$T-completion.complete--verifying" >/dev/null
      captured=1
    fi
    cnt=$(vr electron count --role button --name "仅本对话" | jget "d.get('count')")
    if [ "${cnt:-0}" != 0 ]; then
      n=$((n + 1))
      [[ "$st" == *正在验证* ]] && sub=completion.verify-auth-card || sub=lifecycle.auth-card
      vr electron click --role button --name "仅本对话" --save "$T-$sub--card-$n" >/dev/null
    fi
  done
}

flow_lifecycle() {
  rg1_up electron lifecycle || return 1
  close_popups
  local S S2 S3
  # 创建、授权卡片、完成（智能授权）
  set_permission 智能授权 "$T-lifecycle.auth-card--mode"
  send_goal "$OBJ_COUNT3" "$T-lifecycle.create"
  vr electron text --testid thread-goal-banner-status --save "$T-lifecycle.create--status" >/dev/null
  S=$(latest_session); echo "$S" >"$RUNDIR/session-complete"
  vr snapshot --session "$S" --on electron --save "$T-lifecycle.create--snap" >/dev/null
  run_with_cards "$S" 600
  vr poll $API/session/$S/goal --on electron --until "$GOAL_TERMINAL" --show "$SHOW_RUN" --interval 3 --timeout 30 --save "$T-lifecycle.complete--run" >/dev/null
  vr electron wait --testid goal-completion-marker --timeout 60 --save "$T-lifecycle.complete--marker" >/dev/null
  vr electron text --testid goal-completion-marker --save "$T-lifecycle.complete--marker-text" >/dev/null
  vr electron text --testid thread-goal-banner-status --save "$T-lifecycle.complete--banner-status" >/dev/null
  vr electron aria --save "$T-lifecycle.complete--aria" >/dev/null
  vr snapshot --session "$S" --on electron --save "$T-lifecycle.complete--snap" >/dev/null
  vr snapshot --session "$S" --on electron --save "$T-lifecycle.auth-card--snap" >/dev/null
  # completion.md Electron：完成、验证时的授权卡片、最终回复与交付卡片、重载
  vr snapshot --session "$S" --on electron --save "$T-completion.complete--snap" >/dev/null
  vr snapshot --session "$S" --on electron --save "$T-completion.verify-auth-card--snap" >/dev/null
  vr electron count --testid goal-lifted-delivery-cards --save "$T-completion.final-reply--lifted-cards" >/dev/null
  vr electron aria --save "$T-completion.final-reply--aria" >/dev/null
  vr snapshot --session "$S" --on electron --save "$T-completion.final-reply--snap" >/dev/null
  vr electron reload --save "$T-completion.reload--reloaded" >/dev/null
  vr electron wait --role button --name "新建任务" --timeout 90 --save "$T-completion.reload--sidebar" >/dev/null
  if ! vr electron wait --testid goal-completion-marker --timeout 30 --save "$T-completion.reload--marker" >/dev/null; then
    # 没有回到该会话时，在侧栏点它的标题
    local title
    title=$(vr api GET $API/session/$S --on electron | jget "d['body']['session']['title']")
    vr electron click --text "$title" --save "$T-completion.reload--open-session" >/dev/null
    vr electron wait --testid goal-completion-marker --timeout 30 --save "$T-completion.reload--marker-2" >/dev/null
  fi
  vr electron text --testid thread-goal-banner-status --save "$T-completion.reload--banner-status" >/dev/null
  vr electron aria --save "$T-completion.reload--aria" >/dev/null
  vr snapshot --session "$S" --on electron --save "$T-completion.reload--snap" >/dev/null

  # 暂停、继续、编辑（替换确认）：新任务，始终授权
  vr electron click --role button --name "新建任务" >/dev/null
  set_permission 始终授权 "$T-lifecycle.pause--mode"
  send_goal "$OBJ_SLEEP30" "$T-lifecycle.pause"
  S2=$(latest_session); echo "$S2" >"$RUNDIR/session-pause"
  vr electron click --testid thread-goal-banner-pause --save "$T-lifecycle.pause--click" >/dev/null
  vr poll $API/session/$S2/goal --on electron --until goal.status=paused --show "$SHOW_RUN" --interval 1 --timeout 30 --save "$T-lifecycle.pause--paused" >/dev/null
  vr electron text --testid thread-goal-banner-status --save "$T-lifecycle.pause--status" >/dev/null
  vr snapshot --session "$S2" --on electron --save "$T-lifecycle.pause--snap" >/dev/null
  vr electron click --testid thread-goal-banner-resume --save "$T-lifecycle.resume--click" >/dev/null
  vr poll $API/session/$S2/goal --on electron --until goal.status=active --show "$SHOW_RUN" --interval 1 --timeout 30 --save "$T-lifecycle.resume--active" >/dev/null
  vr electron text --testid thread-goal-banner-status --save "$T-lifecycle.resume--status" >/dev/null
  vr snapshot --session "$S2" --on electron --save "$T-lifecycle.resume--snap" >/dev/null
  vr electron click --testid thread-goal-banner-pause --save "$T-lifecycle.edit-replace--pause" >/dev/null
  vr poll $API/session/$S2/goal --on electron --until goal.status=paused --show "$SHOW_RUN" --interval 1 --timeout 30 --save "$T-lifecycle.edit-replace--paused" >/dev/null
  vr electron click --testid thread-goal-banner-edit-button --save "$T-lifecycle.edit-replace--edit" >/dev/null
  rg1_type_checked "$OBJ_COUNT4" fill || rg1_input_abort
  vr electron click --testid send-button >/dev/null
  vr electron wait --testid goal-replace-confirm-modal --timeout 15 --save "$T-lifecycle.edit-replace--modal" >/dev/null
  vr electron click --role button --name 替换目标 --exact --save "$T-lifecycle.edit-replace--confirm" >/dev/null
  vr poll $API/session/$S2/goal --on electron --until 'goal.objective~1 to 4' --show "$SHOW_RUN" --interval 1 --timeout 30 --save "$T-lifecycle.edit-replace--objective" >/dev/null
  vr poll $API/session/$S2/goal --on electron --until "$GOAL_TERMINAL" --show "$SHOW_RUN" --interval 3 --timeout 420 --save "$T-lifecycle.edit-replace--run" >/dev/null
  vr snapshot --session "$S2" --on electron --save "$T-lifecycle.edit-replace--snap" >/dev/null

  # 清除：新任务里设 Goal 后点清除
  vr electron click --role button --name "新建任务" >/dev/null
  send_goal "$OBJ_SLEEP30" "$T-lifecycle.clear"
  S3=$(latest_session); echo "$S3" >"$RUNDIR/session-clear"
  vr electron click --testid thread-goal-banner-clear --save "$T-lifecycle.clear--click" >/dev/null
  vr electron click --selector '[data-testid="goal-clear-confirm-modal"] >> role=button[name="删除"]' --save "$T-lifecycle.clear--confirm" >/dev/null
  vr electron wait --testid thread-goal-banner --state hidden --timeout 30 --save "$T-lifecycle.clear--hidden" >/dev/null
  vr api GET $API/session/$S3/goal --on electron --save "$T-lifecycle.clear--get" >/dev/null
  vr snapshot --session "$S3" --on electron --save "$T-lifecycle.clear--snap" >/dev/null
  rg1_down electron electron
}

flow_continuation_bg() {
  rg1_up electron continuation-bg || return 1
  close_popups
  local S
  set_permission 始终授权 "$T-continuation.background--mode"
  send_goal "$OBJ_BG" "$T-continuation.background"
  S=$(latest_session); echo "$S" >"$RUNDIR/session"
  vr poll $API/session/$S/goal --on electron --until goal.execution.wait_reason=required_background --show "$SHOW_RUN" --interval 2 --timeout 150 --save "$T-continuation.background--waiting" >/dev/null
  vr electron text --testid thread-goal-banner-status --save "$T-continuation.background--ui-waiting" >/dev/null
  vr poll $API/session/$S/goal --on electron --until "$GOAL_TERMINAL" --show "$SHOW_RUN" --interval 3 --timeout 600 --save "$T-continuation.background--run" >/dev/null
  vr electron wait --testid goal-completion-marker --timeout 60 --save "$T-continuation.background--marker" >/dev/null
  vr snapshot --session "$S" --on electron --save "$T-continuation.background--snap" >/dev/null
  rg1_down electron electron
}

flow_attachments() {
  rg1_up electron attachments || return 1
  close_popups
  local S n
  set_permission 始终授权 "$T-attachments.kickoff--mode"
  # 首页（首轮附件）
  vr electron click --testid attach-button >/dev/null
  vr electron upload --text "添加文件或图片" --exact --files "$RG1_ROOT/_inputs/goal-brief.txt" --save "$T-attachments.kickoff--upload" >/dev/null
  vr electron text --testid attachment-bar --save "$T-attachments.kickoff--bar" >/dev/null
  send_goal "$OBJ_SECRET" "$T-attachments.kickoff"
  S=$(latest_session); echo "$S" >"$RUNDIR/session"
  vr api GET $API/session/$S/goal --on electron --save "$T-attachments.kickoff--goal" >/dev/null
  vr poll $API/session/$S/goal --on electron --until "$GOAL_TERMINAL" --show "$SHOW_RUN" --interval 3 --timeout 420 --save "$T-attachments.kickoff--run" >/dev/null
  vr snapshot --session "$S" --on electron --save "$T-attachments.kickoff--snap" >/dev/null
  # 会话内（目标资源）：上一个 Goal 已完成的会话里再选文件、发送
  vr electron click --testid attach-button >/dev/null
  vr electron upload --text "添加文件或图片" --exact --files "$RG1_ROOT/_inputs/goal-brief-2.txt" --save "$T-attachments.objective-resources--upload" >/dev/null
  vr electron text --testid attachment-bar --save "$T-attachments.objective-resources--bar" >/dev/null
  rg1_type_checked "/goal $OBJ_SECRET2" || rg1_input_abort
  vr electron click --testid send-button --save "$T-attachments.objective-resources--send" >/dev/null
  n=$(vr electron count --testid goal-replace-confirm-modal | jget "d.get('count')")
  if [ "${n:-0}" != 0 ]; then
    vr electron click --role button --name 替换目标 --exact --save "$T-attachments.objective-resources--replace-confirm" >/dev/null
  fi
  vr poll $API/session/$S/goal --on electron --until 'goal.objective~goal-brief-2.txt' --show "$SHOW_RUN" --interval 1 --timeout 60 --save "$T-attachments.objective-resources--created" >/dev/null
  vr api GET $API/session/$S/goal --on electron --save "$T-attachments.objective-resources--goal" >/dev/null
  vr poll $API/session/$S/goal --on electron --until "$GOAL_TERMINAL" --show "$SHOW_RUN" --interval 3 --timeout 420 --save "$T-attachments.objective-resources--run" >/dev/null
  vr snapshot --session "$S" --on electron --save "$T-attachments.objective-resources--snap" >/dev/null
  rg1_down electron electron
}

flow_questionnaire_manual() {
  rg1_up electron questionnaire-manual || return 1
  close_popups
  local S P="$API/agent/mavis/questionnaire/pending?session_id="
  set_permission 始终授权 "$T-questionnaire.manual--mode"
  # 手动回答
  send_goal "$OBJ_FRUIT" "$T-questionnaire.manual"
  S=$(latest_session); echo "$S" >"$RUNDIR/session-manual"
  vr electron wait --role radiogroup --name "Which fruit?" --timeout 150 --save "$T-questionnaire.manual--card" >/dev/null
  vr api GET "$P$S" --on electron --save "$T-questionnaire.manual--pending" >/dev/null
  vr electron aria --save "$T-questionnaire.manual--card-aria" >/dev/null
  vr electron click --role radio --name "Banana" --exact --save "$T-questionnaire.manual--answer" >/dev/null
  vr api GET "$P$S" --on electron --save "$T-questionnaire.manual--pending-after" >/dev/null
  vr poll $API/session/$S/goal --on electron --until "$GOAL_TERMINAL" --show "$SHOW_RUN" --interval 4 --timeout 420 --save "$T-questionnaire.manual--run" >/dev/null
  vr snapshot --session "$S" --on electron --save "$T-questionnaire.manual--snap" >/dev/null
  rg1_down electron electron
}

flow_questionnaire_auto() {
  rg1_up electron questionnaire-auto || return 1
  close_popups
  local S2 P="$API/agent/mavis/questionnaire/pending?session_id="
  set_permission 始终授权 "$T-questionnaire.auto-timeout--mode"
  # 超时自动回答：新任务，提问后不操作
  send_goal "$OBJ_FRUIT" "$T-questionnaire.auto-timeout"
  S2=$(latest_session); echo "$S2" >"$RUNDIR/session-auto"
  vr electron wait --role radiogroup --name "Which fruit?" --timeout 150 --save "$T-questionnaire.auto-timeout--card" >/dev/null
  vr api GET "$P$S2" --on electron --save "$T-questionnaire.auto-timeout--pending" >/dev/null
  vr poll $API/session/$S2/goal --on electron --until "$GOAL_TERMINAL" --show "$SHOW_RUN" --interval 10 --timeout 720 --save "$T-questionnaire.auto-timeout--run" >/dev/null
  vr electron count --role radiogroup --name "Which fruit?" --save "$T-questionnaire.auto-timeout--card-after" >/dev/null
  vr snapshot --session "$S2" --on electron --save "$T-questionnaire.auto-timeout--snap" >/dev/null
  rg1_down electron electron
}

rg1_inputs
for f in lifecycle continuation-bg attachments questionnaire-manual questionnaire-auto; do
  rg1_wants "$f" || continue
  ( "flow_${f//-/_}" )
  rg1_log "flow done rc=$?"
done
