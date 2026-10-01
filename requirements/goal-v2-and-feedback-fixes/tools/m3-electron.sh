#!/usr/bin/env bash
# M3 Electron 场景：verify.md S12、S12b、S14、S15、S16（不带故障注入），S17、S19、S20、S21（--fault）。
# 用法（agent-archon worktree 根目录，HEAD 为被测提交、已 prepare）：
#   bash <tools>/m3-electron.sh <场景> <尝试名>
# 证据：<M2_ROOT>/<场景>/<尝试名>/（M2_ROOT 默认 evidence/m3）。每个场景起自己的 Electron 实例，结束 down。
# 故障规则写法照 verify-archon references/fault.md“场景写法”。
set -u
source "$(dirname "${BASH_SOURCE[0]}")/m3-lib.sh"
SCN=$1
ATTEMPT=$2
LSC=$(echo "$SCN" | tr A-Z a-z)
E() { vr electron "$@"; }
etext() { E text --testid "$1" --timeout "${3:-10}" --save "$2" | jget "d.get('text')"; }
goal_e() { vr api GET $API/session/$1/goal --on electron --save "$2"; }
poll_e() { local s=$1; shift; vr poll $API/session/$s/goal --on electron "$@"; }
turn_end() { E wait --testid stop-button --state hidden --timeout "${1:-120}" >/dev/null; }
reset_at() { python3 -c 'import json,sys
def walk(o):
    if isinstance(o,dict):
        if isinstance(o.get("resetAtMs"),(int,float)): return int(o["resetAtMs"])
        for v in o.values():
            r=walk(v)
            if r: return r
    elif isinstance(o,list):
        for v in o:
            r=walk(v)
            if r: return r
    return 0
try: print(walk(json.load(sys.stdin)))
except Exception: print(0)'; }
# 普通发送；若弹出“替换当前目标？”（M4 之前 active Goal 让输入框处于目标模式），截图后取消并返回 1
send_plain() {
  type_checked "$1" || input_abort
  E click --testid send-button --save "$2-send" >/dev/null
  sleep 1.5
  local n
  n=$(E count --testid goal-replace-confirm-modal --save "$2-replace-dialog" | jget "d.get('count')")
  if [ "${n:-0}" != "0" ] && [ -n "$n" ]; then
    E screenshot --save "$2-replace-dialog-shown" >/dev/null
    E click --selector 'role=dialog >> role=button[name="取消"]' --timeout 5 --save "$2-replace-dialog-cancel" >/dev/null || E click --testid goal-replace-confirm-close --timeout 5 >/dev/null
    E press --testid message-textarea --key "Meta+a" >/dev/null; E press --testid message-textarea --key "Backspace" >/dev/null
    m2_log "replace-goal dialog appeared for plain send ($2); cancelled"
    echo replace-dialog >"$OUT/$2-blocked"
    return 1
  fi
  return 0
}
end_scenario() {
  E screenshot --save final-ui >/dev/null
  m2_down "$@"
}
fault_rule_id() { jget "(d.get('rule') or {}).get('id') or d.get('id') or d.get('ruleId')"; }
# 等 fault log 中出现第一个注入，读重置时刻
wait_injected() {
  local deadline=$(( $(date +%s) + ${2:-180} )) r=0
  while [ "$(date +%s)" -lt "$deadline" ]; do
    r=$(node "$V" fault log --on electron --session "$1" --event attempt-end --run "$RID" 2>/dev/null | reset_at)
    [ "${r:-0}" -gt 0 ] && break
    sleep 2
  done
  echo "${r:-0}"
}

# wait_port_free <端口>：等该端口空闲（最多 20 分钟），别的验证线的同号场景（如 TUI S13 用 8765）不并发占用。
# 2026-10-01 final 轮加：S12、S15 的 http.server 端口被占时，模型起的服务会失败，任务不再 running
wait_port_free() {
  local i
  for i in $(seq 1 400); do
    [ "$(curl -s -o /dev/null -m 2 -w '%{http_code}' "http://127.0.0.1:$1/" 2>/dev/null)" = "000" ] && return 0
    [ "$i" = 1 ] && m2_log "port $1 busy; waiting"
    sleep 3
  done
  m2_log "port $1 still busy"; return 1
}
m2_begin "$SCN" "$ATTEMPT"
case $SCN in
S12)
  wait_port_free 8765 || exit 1
  port_probe 8765 s12-port-before >/dev/null
  m3_up electron || exit 1
  m2_close_popups
  # 1
  send_plain "Start the shell command python3 -m http.server 8765 as a background task (bash tool with run_in_background: true) and end your turn right away." s12-bg || true
  sleep 3
  S=$(m2_latest_session); echo "$S" >"$OUT/session"
  turn_end 180
  bg_tasks "$S" s12-bg-tasks-step1 >/dev/null
  port_probe 8765 s12-port-step1 >/dev/null
  # 2
  m2_send_goal_electron "Write the numbers 1 to 3 into count.txt, one number per line, then stop." s12-goal1
  # 3
  banner_sampler thread-goal-banner-status "$OUT/s12-banner-status-samples.jsonl" & SAMPLER=$!
  poll_e "$S" --until "$TERMINAL" --show "$SHOW,goal.goal_id" --interval 3 --timeout 420 --save s12-goal1-run >/dev/null
  kill "$SAMPLER" 2>/dev/null; wait "$SAMPLER" 2>/dev/null
  turn_end 120
  goal_e "$S" s12-goal1-final >/dev/null
  vr snapshot --session "$S" --on electron --save s12-goal1 >/dev/null
  bg_tasks "$S" s12-bg-tasks-step3 >/dev/null
  # 4
  m2_send_goal_electron "Write hello into later.txt, then stop." s12-goal2
  E click --testid thread-goal-banner-pause --save s12-goal2-pause >/dev/null
  sleep 5
  turn_end 60
  # 5
  vr api GET $API/session/$S/message --on electron --save s12-history >/dev/null
  goal_e "$S" s12-goal2-after-pause >/dev/null
  bg_tasks "$S" s12-bg-tasks-step5 >/dev/null
  port_probe 8765 s12-port-step5 >/dev/null
  E screenshot --save s12-step5 >/dev/null
  vr snapshot --session "$S" --on electron --save s12 >/dev/null
  end_scenario
  port_closed_after_down 8765
  ;;
S12b)
  m3_up electron || exit 1
  m2_close_popups
  # 1
  send_plain "Start a background subagent task (task tool, run in background) that waits 120 seconds and then writes side.txt containing side. End your turn right away." s12b-bg || true
  sleep 3
  S=$(m2_latest_session); echo "$S" >"$OUT/session"
  turn_end 180
  bg_tasks "$S" s12b-bg-tasks-step1 >/dev/null
  # 2
  m2_send_goal_electron "Write the numbers 1 to 3 into count.txt, one number per line, then stop." s12b-goal
  # 3
  banner_sampler thread-goal-banner-status "$OUT/s12b-banner-status-samples.jsonl" & SAMPLER=$!
  poll_e "$S" --until "$TERMINAL" --show "$SHOW,goal.goal_id" --interval 3 --timeout 420 --save s12b-run >/dev/null
  kill "$SAMPLER" 2>/dev/null; wait "$SAMPLER" 2>/dev/null
  turn_end 120
  goal_e "$S" s12b-final >/dev/null
  bg_tasks "$S" s12b-bg-tasks-terminal >/dev/null
  vr snapshot --session "$S" --on electron --save s12b >/dev/null
  # 等 subagent 结束，取它的结束时刻（判定“在任务结束前就出现 turn_bound”）
  for _ in $(seq 1 30); do
    st=$(bg_tasks "$S" s12b-bg-tasks-wait | python3 -c 'import json,sys
d=json.load(sys.stdin); t=[x for x in d["tasks"] if x["kind"]=="subagent"]
print("done" if t and all(x["status"] not in ("queued","running","stopping") for x in t) else "running")')
    [ "$st" = done ] && break
    sleep 5
  done
  bg_tasks "$S" s12b-bg-tasks-end >/dev/null
  vr snapshot --session "$S" --on electron --save s12b-after-subagent >/dev/null
  end_scenario
  ;;
S14)
  m3_up electron || exit 1
  m2_close_popups
  # 1
  m2_send_goal_electron "Start a background subagent task (task tool, run in background) that waits 40 seconds and then writes sub.txt containing sub-done. End your turn right away without waiting. The goal is met only when sub.txt contains sub-done." s14-create
  S=$(m2_latest_session); echo "$S" >"$OUT/session"
  # 2
  poll_e "$S" --until goal.execution.wait_reason=required_background --show "$SHOW" --interval 1 --timeout 150 --save s14-waiting >"$OUT/s14-waiting.json"
  etext thread-goal-banner-status s14-banner-status-waiting >"$OUT/banner-status-waiting.txt"
  E count --testid continue-button --save s14-continue-count >"$OUT/continue-count.json"
  bg_tasks "$S" s14-bg-tasks-waiting >/dev/null
  # 3：输入框发送；M4 之前 active Goal 让输入框处于目标模式，会弹“替换当前目标？”。被挡时取消，
  #    并用接口（另一个客户端）发送同一条消息，只作为 runtime 侧的补充观察
  if ! send_plain "Quick side question: what is 17 + 25? Answer with just the number." s14-side; then
    api_send "$S" "Quick side question: what is 17 + 25? Answer with just the number." s14-side-via-api
  fi
  wait_reply "$S" "17 + 25" 120 s14-side-history
  goal_e "$S" s14-goal-after-side-reply >/dev/null
  bg_tasks "$S" s14-bg-tasks-after-side >/dev/null
  E screenshot --save s14-after-side >/dev/null
  # 4
  poll_e "$S" --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 600 --save s14-run >/dev/null
  turn_end 120
  goal_e "$S" s14-final >/dev/null
  bg_tasks "$S" s14-bg-tasks-final >/dev/null
  vr snapshot --session "$S" --on electron --save s14 >/dev/null
  end_scenario
  ;;
S15)
  wait_port_free 8766 || exit 1
  port_probe 8766 s15-port-before >/dev/null
  m3_up electron || exit 1
  m2_close_popups
  # 1
  m2_send_goal_electron "Start the shell command python3 -m http.server 8766 as a background task (bash tool with run_in_background: true). Then write served.txt containing up and mark the goal complete. Do not stop the server." s15-create
  S=$(m2_latest_session); echo "$S" >"$OUT/session"
  # 2
  poll_e "$S" --until "$TERMINAL" --show "$SHOW" --interval 2 --timeout 420 --save s15-run >/dev/null
  bg_tasks "$S" s15-bg-tasks-at-terminal >/dev/null
  port_probe 8766 s15-port-at-terminal >/dev/null
  turn_end 120
  goal_e "$S" s15-final >/dev/null
  vr snapshot --session "$S" --on electron --save s15 >/dev/null
  end_scenario
  port_closed_after_down 8766
  ;;
S16)
  m3_up electron || exit 1
  m2_close_popups
  # 1
  m2_send_goal_electron "Run the shell command sleep 20 in the foreground, then write step.txt containing 1, then stop." s16-create
  S=$(m2_latest_session); echo "$S" >"$OUT/session"
  E click --testid thread-goal-banner-pause --save s16-pause >/dev/null
  poll_e "$S" --until goal.status=paused --show "$SHOW" --interval 1 --timeout 30 --save s16-paused >/dev/null
  turn_end 60
  # 2
  if ! send_plain "Start the shell command python3 -m http.server 8767 as a background task (bash tool with run_in_background: true) and end your turn right away." s16-bg; then
    api_send "$S" "Start the shell command python3 -m http.server 8767 as a background task (bash tool with run_in_background: true) and end your turn right away." s16-bg-via-api
  fi
  sleep 3
  turn_end 180
  wait_reply "$S" "http.server 8767" 120 s16-bg-history
  bg_tasks "$S" s16-bg-tasks-step2 >/dev/null
  port_probe 8767 s16-port-step2 >/dev/null
  goal_e "$S" s16-goal-before-resume >/dev/null
  # 3 连续两次快速点击（第二次在第一次发出约 0.2 秒后并发发出）
  echo "$(now_ms)" >"$OUT/resume-click-at-ms"
  ( node "$V" electron click --testid thread-goal-banner-resume --timeout 3 --run "$RID" >"$OUT/resume-click-2.json" 2>&1 ) &
  C2=$!
  sleep 0.2
  E click --testid thread-goal-banner-resume --timeout 5 --save s16-resume-click-1 >/dev/null
  wait "$C2"
  echo "$(now_ms)" >"$OUT/resume-click-done-ms"
  # 4
  poll_e "$S" --until "$TERMINAL" --show "$SHOW" --interval 1 --timeout 420 --save s16-run >/dev/null
  turn_end 120
  goal_e "$S" s16-final >/dev/null
  vr snapshot --session "$S" --on electron --save s16 >/dev/null
  bg_tasks "$S" s16-bg-tasks-final >/dev/null
  end_scenario
  port_closed_after_down 8767
  ;;
S17|S21)
  m3_up electron --fault || exit 1
  m2_close_popups
  RULE=$(vr fault add --on electron --session next --nth 2- --preset usage-limit-reset --reset-in 180 --note "$SCN: from the 2nd main request until the reset time" --save fault-rule | fault_rule_id)
  echo "$RULE" >"$OUT/rule-id"
  # 1
  m2_send_goal_electron "Create files e1.txt, e2.txt, e3.txt one at a time, each containing its own number, then stop." "$LSC-create"
  S=$(m2_latest_session); echo "$S" >"$OUT/session"
  # 2
  poll_e "$S" --until goal.status=usage_limited --show "$SHOW,goal.usage_recovery_scheduled" --interval 1 --timeout 180 --save "$LSC-limited" >/dev/null
  RESET_AT=$(wait_injected "$S" 30); echo "$RESET_AT" >"$OUT/reset-at-ms"
  goal_e "$S" "$LSC-goal-limited" >"$OUT/goal-limited.json"
  m2_log "usage_limited; resetAtMs=$RESET_AT"
  if [ "$SCN" = S17 ]; then
    turn_end 60
    # 3
    etext thread-goal-banner-status s17-banner-status >"$OUT/banner-status.txt"
    etext thread-goal-usage-guide s17-usage-guide >"$OUT/usage-guide.txt"
    E count --testid continue-button --save s17-continue-count >"$OUT/continue-count.json"
    E aria --selector '[data-testid="thread-goal-banner"]' --save s17-banner-aria >/dev/null
    # 补充消息也是该会话的 main 请求：发送前关规则、回复后开规则（fault.md“坑”），让规则只作用于 Goal
    vr fault disable "$RULE" --on electron --save fault-disable-for-side >/dev/null
    if ! send_plain "What is 8 + 1? Reply with only the number." s17-side; then
      api_send "$S" "What is 8 + 1? Reply with only the number." s17-side-via-api
    fi
    wait_reply "$S" "8 + 1" 120 s17-side-history
    turn_end 60
    vr fault enable "$RULE" --on electron --save fault-enable-after-side >/dev/null
    goal_e "$S" s17-goal-after-side >"$OUT/goal-after-side.json"
    etext thread-goal-banner-status s17-banner-status-after-side >"$OUT/banner-status-after-side.txt"
    # 4 重置之前点继续
    PREV=$(jget "d['body']['goal'].get('requests_used',0)" <"$OUT/goal-after-side.json")
    # M4 之前输入框三角沿用旧的 Turn 续跑判定：补充消息那一轮成功后三角消失（run1 实测）。此时记下数量，
    # 改点横幅“继续”（同一恢复接口，R53 横幅继续），三角入口本身记为依赖 M4
    CB=$(E count --testid continue-button --save s17-continue-count-before-click | jget "d.get('count')")
    echo "${CB:-0}" >"$OUT/continue-count-before-click"
    echo "$(now_ms)" >"$OUT/continue-click-at-ms"
    if [ "${CB:-0}" != 0 ]; then
      E click --testid continue-button --save s17-continue-click >/dev/null
    else
      echo banner-resume >"$OUT/step4-entry"
      E click --testid thread-goal-banner-resume --save s17-banner-resume-click >/dev/null
    fi
    # 失败提示（输入框上方的额度提醒）只停留几秒（S20 run2 实测）：点击后连续截图并读 aria
    for k in 1 2 3; do
      E screenshot --save "s17-after-click-$k" >/dev/null
      E aria --save "s17-page-aria-after-click-$k" >/dev/null
      sleep 1
    done
    wait_goal_relimited "$S" usage_limited "${PREV:-0}" 120 s17-goal-relimited
    turn_end 60
    sleep 2
    etext thread-goal-banner-status s17-banner-status-relimited >"$OUT/banner-status-relimited.txt"
    etext thread-goal-usage-guide s17-usage-guide-relimited >"$OUT/usage-guide-relimited.txt"
    E screenshot --save s17-relimited >/dev/null
    E aria --save s17-page-aria-relimited >/dev/null
    vr api GET $API/session/$S/message --on electron --save s17-history-relimited >/dev/null
    echo "$(now_ms)" >"$OUT/step4-done-at-ms"
    # 5 到重置时间之后：离开 usage_limited，再到终态
    wait_s=$(( (RESET_AT - $(now_ms)) / 1000 + 150 )); [ "$wait_s" -gt 30 ] || wait_s=150
    poll_e "$S" --until 'goal.status=active|complete|paused|blocked|budget_limited' --show "$SHOW,goal.usage_recovery_scheduled" --interval 1 --timeout "$wait_s" --save s17-left-limited >/dev/null
    poll_e "$S" --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 600 --save s17-run >/dev/null
    turn_end 120
    goal_e "$S" s17-final >/dev/null
    vr snapshot --session "$S" --on electron --save s17 >/dev/null
    vr fault log --on electron --session "$S" --tail 500 --save fault-s17 >/dev/null
    vr fault list --on electron --save fault-list >/dev/null
    end_scenario
  else
    # S21 步骤 2：保留数据关闭应用，等到重置时间之后再从这份数据启动
    vr snapshot --session "$S" --on electron --save s21-before-close >/dev/null
    vr fault log --on electron --session "$S" --tail 500 --save fault-s21-before-close >/dev/null
    TITLE=$(vr api GET $API/session/$S --on electron | jget "d['body']['session']['title']"); echo "$TITLE" >"$OUT/session-title"
    FIRST_RID=$RID; echo "$FIRST_RID" >"$OUT/first-runId"
    end_scenario --keep-data
    echo "$(now_ms)" >"$OUT/closed-at-ms"
    wait_s=$(( (RESET_AT - $(now_ms)) / 1000 + 10 ))
    [ "$wait_s" -gt 0 ] && { m2_log "waiting ${wait_s}s past the reset time"; sleep "$wait_s"; }
    # 3 重新启动（同一份数据），--fault 不加规则：只为记录请求
    mkdir -p "$OUT/after-restart"
    OUT0=$OUT; OUT=$OUT/after-restart
    git rev-parse HEAD >"$OUT/git-head"; git status --porcelain >"$OUT/git-status"
    echo "$(now_ms)" >"$OUT0/restart-up-at-ms"
    m3_up electron --fault --from-data "$FIRST_RID" || exit 1
    echo "$(now_ms)" >"$OUT0/restart-ready-at-ms"
    m2_close_popups
    goal_e "$S" s21-goal-after-restart >/dev/null
    E click --role button --name "关闭签到" --exact --timeout 5 >/dev/null
    E click --text "$TITLE" --timeout 10 --save s21-open-session >/dev/null || {
      E click --role button --name "搜索" --exact --save s21-open-search >/dev/null
      E fill --role textbox --name "搜索任务或运行命令" --value "$TITLE" >/dev/null
      E click --selector "role=dialog >> role=button[name=\"$TITLE\"]" --timeout 15 --save s21-open-search-result >/dev/null
    }
    poll_e "$S" --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 600 --save s21-run >/dev/null
    turn_end 120
    goal_e "$S" s21-final >/dev/null
    vr snapshot --session "$S" --on electron --save s21 >/dev/null
    vr fault log --on electron --session "$S" --tail 500 --save fault-s21-after-restart >/dev/null
    end_scenario
    OUT=$OUT0
    rm -rf "$HOME_VA/$FIRST_RID/data" "$HOME_VA/$FIRST_RID/workspace" "$HOME_VA/$FIRST_RID/userData"
  fi
  ;;
S19)
  m3_up electron --fault || exit 1
  m2_close_popups
  RULE=$(vr fault add --on electron --session next --nth 2- --preset usage-limit-reset --reset-in 180 --note "S19: first Goal only" --save fault-rule | fault_rule_id)
  echo "$RULE" >"$OUT/rule-id"
  # 1
  m2_send_goal_electron "Create files e1.txt, e2.txt, e3.txt one at a time, each containing its own number, then stop." s19-create
  S=$(m2_latest_session); echo "$S" >"$OUT/session"
  poll_e "$S" --until goal.status=usage_limited --show "$SHOW,goal.usage_recovery_scheduled" --interval 1 --timeout 180 --save s19-limited >/dev/null
  RESET_AT=$(wait_injected "$S" 30); echo "$RESET_AT" >"$OUT/reset-at-ms"
  goal_e "$S" s19-old-goal >"$OUT/old-goal.json"
  jget "d['body']['goal']['goal_id']" <"$OUT/old-goal.json" >"$OUT/old-goal-id"
  vr fault disable "$RULE" --on electron --save fault-disable >/dev/null
  turn_end 60
  # 2
  E click --testid thread-goal-banner-clear --save s19-clear >/dev/null
  E click --selector '[data-testid="goal-clear-confirm-modal"] >> role=button[name="删除"]' --save s19-clear-confirm >/dev/null
  E wait --testid thread-goal-banner --state hidden --timeout 30 >/dev/null
  goal_e "$S" s19-after-clear >/dev/null
  type_checked "/goal Reply with the single word DONE." || input_abort
  E click --testid send-button --save s19-new-send >/dev/null
  poll_e "$S" --until "goal.status=active|complete|paused|blocked|budget_limited|usage_limited" --show "goal.goal_id,goal.status" --interval 1 --timeout 60 --save s19-new-goal >/dev/null
  poll_e "$S" --until "$TERMINAL" --show "$SHOW,goal.goal_id" --interval 2 --timeout 420 --save s19-new-run >/dev/null
  turn_end 120
  goal_e "$S" s19-new-final >/dev/null
  # 3 重置时间过去之后 90 秒内保持终态
  hold=$(( (RESET_AT + 90000 - $(now_ms)) / 1000 )); [ "$hold" -gt 90 ] || hold=90
  echo "$hold" >"$OUT/hold-seconds"
  poll_e "$S" --until goal.status=complete --hold "$hold" --show "goal.goal_id,goal.status,goal.status_reason,goal.requests_used" --interval 3 --timeout $((hold + 60)) --save s19-hold >/dev/null
  goal_e "$S" s19-after-hold >/dev/null
  vr snapshot --session "$S" --on electron --save s19 >/dev/null
  vr fault log --on electron --session "$S" --tail 500 --save fault-s19 >/dev/null
  end_scenario
  ;;
S20)
  m3_up electron --fault || exit 1
  m2_close_popups
  RULE=$(vr fault add --on electron --session next --nth 2- --preset usage-limit --note "S20: no trusted reset time" --save fault-rule | fault_rule_id)
  echo "$RULE" >"$OUT/rule-id"
  # 1
  m2_send_goal_electron "Create files e1.txt, e2.txt, e3.txt one at a time, each containing its own number, then stop." s20-create
  S=$(m2_latest_session); echo "$S" >"$OUT/session"
  poll_e "$S" --until goal.status=usage_limited --show "$SHOW,goal.usage_recovery_scheduled" --interval 1 --timeout 180 --save s20-limited >/dev/null
  turn_end 60
  # 2
  etext thread-goal-usage-guide s20-usage-guide >"$OUT/usage-guide.txt"
  etext thread-goal-banner-status s20-banner-status >"$OUT/banner-status.txt"
  goal_e "$S" s20-goal-limited >"$OUT/goal-limited.json"
  poll_e "$S" --until goal.status=usage_limited --hold 180 --show "$SHOW,goal.usage_recovery_scheduled" --interval 3 --timeout 240 --save s20-hold >/dev/null
  vr snapshot --session "$S" --on electron --save s20-after-hold >/dev/null
  # 3
  PREV=$(goal_raw "$S" | jget "d.get('requests_used',0)")
  echo "$(now_ms)" >"$OUT/resume-click-at-ms"
  E click --testid thread-goal-banner-resume --save s20-resume-click >/dev/null
  # 失败提示可能一闪而过：点击后连续截图并读页面 aria（第 1、2、4 秒左右）
  for k in 1 2 3; do
    E screenshot --save "s20-after-click-$k" >/dev/null
    E aria --save "s20-page-aria-after-click-$k" >/dev/null
    sleep 1
  done
  wait_goal_relimited "$S" usage_limited "${PREV:-0}" 120 s20-goal-relimited
  turn_end 60
  sleep 2
  etext thread-goal-banner-status s20-banner-status-relimited >"$OUT/banner-status-relimited.txt"
  etext thread-goal-usage-guide s20-usage-guide-relimited >"$OUT/usage-guide-relimited.txt"
  E screenshot --save s20-relimited >/dev/null
  E aria --save s20-page-aria-relimited >/dev/null
  vr api GET $API/session/$S/message --on electron --save s20-history-relimited >/dev/null
  vr snapshot --session "$S" --on electron --save s20 >/dev/null
  vr fault disable "$RULE" --on electron --save fault-disable >/dev/null
  vr fault log --on electron --session "$S" --tail 500 --save fault-s20 >/dev/null
  end_scenario
  ;;
*) echo "unknown scenario $SCN" >&2; exit 2 ;;
esac
m2_log "scenario $SCN done"
