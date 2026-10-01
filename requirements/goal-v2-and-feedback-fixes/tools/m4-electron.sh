#!/usr/bin/env bash
# M4 Electron 场景（verify.md S22–S29b、S31、S33、S39）与 M4 之后的重跑（S03 补充消息、S16 两次真实快速点击）。
# 用法（agent-archon worktree 根目录，HEAD 为被测提交、已 prepare runtime tui electron）：
#   bash <tools>/m4-electron.sh <S03|S16|S22|S23|S24|S25|S26|S27|S28|S29|S31|S33|S39> <尝试名>
#   S16 另有 S16_MODE=hold（默认：屏障暂扣第一次恢复请求，期间两次点击都落到按钮上）或 nohold（只记录，两次点击并发发出）
#   S29 同一实例里依次跑 S29（会话 A）和 S29b（会话 B、C），证据都在 S29/<尝试名>/
# 证据：<M2_ROOT>/<场景>/<尝试名>/（M2_ROOT 默认 evidence/m3，跑 M4 时设为 evidence/m4）。每个场景起自己的 Electron 实例，结束 down。
# 启动经 m3_up 的共享锁串行、错开 M3_UP_GAP 秒。
set -u
source "$(dirname "${BASH_SOURCE[0]}")/m3-lib.sh"
SCN=$1
ATTEMPT=$2
E() { vr electron "$@"; }
etext() { E text --testid "$1" --timeout "${3:-10}" --save "$2" | jget "d.get('text')"; }
goal_e() { vr api GET $API/session/$1/goal --on electron --save "$2"; }
poll_e() { local s=$1; shift; vr poll $API/session/$s/goal --on electron "$@"; }
turn_end() { E wait --testid stop-button --state hidden --timeout "${1:-120}" >/dev/null; }
new_task() { E click --role button --name "新建任务" --exact --timeout 10 >/dev/null || E click --role button --name "新建任务" >/dev/null; sleep 1; }
REPLACE_BTN='[data-testid="goal-replace-confirm-modal"] >> role=button[name="替换目标"]'
CANCEL_BTN='[data-testid="goal-replace-confirm-modal"] >> role=button[name="取消"]'
CLEAR_BTN='[data-testid="goal-clear-confirm-modal"] >> role=button[name="删除"]'

# 输入框普通发送（点 send-button）。M4 起 active Goal 下不应弹“替换当前目标吗？”：弹出时记 <name>-replace-dialog-shown，
# 截图后取消（不替换目标），返回 1
send_plain() {
  type_checked "$1" || input_abort
  echo "$(now_ms)" >"$OUT/$2-sent-at-ms"
  E click --testid send-button --save "$2-send" >/dev/null
  sleep 1.5
  local n
  n=$(E count --testid goal-replace-confirm-modal --save "$2-replace-dialog" | jget "d.get('count')")
  if [ -n "$n" ] && [ "$n" != 0 ]; then
    E screenshot --save "$2-replace-dialog-shown" >/dev/null
    E click --selector "$CANCEL_BTN" --timeout 5 >/dev/null
    echo replace-dialog >"$OUT/$2-blocked"
    m2_log "replace-goal dialog appeared for a plain send ($2)"
    return 1
  fi
  return 0
}
# 清空输入框
clear_input() { E press --testid message-textarea --key "Meta+a" >/dev/null; E press --testid message-textarea --key Backspace >/dev/null; }
# toast 连读：toast 只停留约 4 秒，连读 n 次（间隔 0.4 秒），写 <name>.jsonl
toast_burst() {
  local name=$1 n=${2:-6} i
  for i in $(seq 1 "$n"); do
    node "$V" electron text --testid toast-container --timeout 1 --run "$RID" 2>/dev/null | python3 -c 'import json,sys,time
try: d=json.load(sys.stdin)
except Exception: d={}
print(json.dumps({"at":int(time.time()*1000),"ok":d.get("ok"),"text":d.get("text")},ensure_ascii=False))' >>"$OUT/$name.jsonl"
    sleep 0.4
  done
}
# 等屏障出现暂扣的请求（最多 <秒>），存证 <name>
wait_barrier_held() {
  local deadline=$(( $(date +%s) + ${2:-15} ))
  while [ "$(date +%s)" -lt "$deadline" ]; do
    if node "$V" electron barrier list --run "$RID" 2>/dev/null | python3 -c 'import json,sys
d=json.load(sys.stdin); sys.exit(0 if d.get("pending") else 1)'; then break; fi
    sleep 0.3
  done
  E barrier list --save "$1" >"$OUT/$1.json"
}
# Goal Turn 正在运行：stop-button 可见、Goal 为 active 且不在验证
wait_goal_turn_running() { # <session> <timeout 秒> <name>
  local deadline=$(( $(date +%s) + $2 )) c g
  while [ "$(date +%s)" -lt "$deadline" ]; do
    c=$(node "$V" electron count --testid stop-button --run "$RID" 2>/dev/null | jget "d.get('count')")
    g=$(goal_raw "$1" | jget "(d.get('status') or '')+'|'+((d.get('execution') or {}).get('wait_reason') or '')")
    printf '{"at":%s,"stopButton":"%s","goal":"%s"}\n' "$(now_ms)" "$c" "$g" >>"$OUT/$3-trajectory.jsonl"
    if [ "$c" = 1 ] && [ "$g" = "active|" ]; then return 0; fi
    case $g in complete*|blocked*|budget_limited*|usage_limited*) return 1 ;; esac
    sleep 0.5
  done
  return 1
}
# 该会话当前是否有未结算的 Goal Turn：只读实例的 runtime 事件文件，最新的 goal.turn_bound 没有对应的 goal.turn_settled。
# 打印 open:<turnId> 或 none
goal_turn_open() {
  python3 - "$HOME_VA/$RID/data/v2/observability/events" "$1" <<'PYEOF'
import json, os, sys
root, sid = sys.argv[1], sys.argv[2]
bound, settled = [], set()
for dp, _, fs in os.walk(root):
    for f in fs:
        if not f.endswith('.jsonl'):
            continue
        for line in open(os.path.join(dp, f), errors='replace'):
            if sid not in line:
                continue
            try:
                e = json.loads(line)
            except Exception:
                continue
            fl = e.get('fields') or {}
            p = fl.get('payload') or {}
            if fl.get('eventType') == 'goal.turn_bound':
                bound.append((e.get('tsMs') or 0, p.get('turnId')))
            elif fl.get('eventType') == 'goal.turn_settled':
                settled.add(p.get('turnId'))
bound.sort()
print('open:' + bound[-1][1] if bound and bound[-1][1] not in settled else 'none')
PYEOF
}
# 等一个正在运行的 Goal Turn：有未结算的 Goal Turn 且 stop-button 可见；<排除的 turnId> 可选
wait_open_goal_turn() { # <session> <timeout 秒> <name> [exclude turnId]
  local deadline=$(( $(date +%s) + $2 )) o c
  while [ "$(date +%s)" -lt "$deadline" ]; do
    o=$(goal_turn_open "$1")
    c=$(node "$V" electron count --testid stop-button --run "$RID" 2>/dev/null | jget "d.get('count')")
    printf '{"at":%s,"goalTurn":"%s","stopButton":"%s"}\n' "$(now_ms)" "$o" "$c" >>"$OUT/$3-trajectory.jsonl"
    if [ "${o#open:}" != "$o" ] && [ "${o#open:}" != "${4:-}" ] && [ "$c" = 1 ]; then echo "${o#open:}"; return 0; fi
    case $(goal_raw "$1" | jget "d.get('status') or ''") in complete|blocked|budget_limited|usage_limited) return 1 ;; esac
    sleep 0.4
  done
  return 1
}
# 采样 Goal（objective/status/updated_at）n 次，间隔 1 秒，写 <name>.jsonl
goal_samples() { # <session> <n> <name>
  local i
  for i in $(seq 1 "$2"); do
    goal_raw "$1" | python3 -c 'import json,sys,time
g=json.loads(sys.stdin.read() or "{}")
print(json.dumps({"at":int(time.time()*1000),"status":g.get("status"),"objective":g.get("objective"),"updated_at":g.get("updated_at"),"token_budget":g.get("token_budget")},ensure_ascii=False))' >>"$OUT/$3.jsonl"
    sleep 1
  done
}
session_title() { vr api GET $API/session/$1 --on electron | jget "d['body']['session']['title']"; }
open_session() { # open_session <标题> <name>：侧栏点标题；找不到时用“搜索”对话框
  E click --role button --name "关闭签到" --exact --timeout 3 >/dev/null
  if ! E click --text "$1" --exact --timeout 8 --save "open-$2" >/dev/null; then
    E click --role button --name "搜索" --exact --save "open-$2-search" >/dev/null
    E fill --role textbox --name "搜索任务或运行命令" --value "$1" >/dev/null
    E click --selector "role=dialog >> role=button[name=\"$1\"]" --timeout 15 --save "open-$2-search-result" >/dev/null
  fi
}
verifier_children() { # <snapshot 名>：从 snapshot 的 runtime 事件取 verifier 子会话 ID
  python3 - "$OUT" "$1" <<'EOF'
import glob,json,sys,os
fs=sorted(glob.glob(os.path.join(sys.argv[1],'[0-9][0-9][0-9]-'+sys.argv[2]+'-runtime-events.jsonl')))
seen=[]
for l in open(fs[-1]) if fs else []:
    e=json.loads(l); p=e.get('fields',{}).get('payload') or {}
    if e.get('fields',{}).get('eventType')=='goal.verification_child_started' and p.get('childSessionId') and p['childSessionId'] not in seen:
        seen.append(p['childSessionId'])
print(' '.join(seen))
EOF
}
end_scenario() { E screenshot --save final-ui >/dev/null; m2_down "$@"; }

m2_begin "$SCN" "$ATTEMPT"
case $SCN in
S03)
  m3_up electron || exit 1
  m2_close_popups
  m2_send_goal_electron "Create five files a1.txt to a5.txt one at a time, each containing its own number. After writing each file, run the shell command sleep 5 in the foreground. Do all five in this single turn. Then call get_goal once, then verify all five files exist." s03-create
  S=$(m2_latest_session); echo "$S" >"$OUT/session"; echo "$S" >"$OUT/s03-session"
  # 2
  poll_e "$S" --until "goal.requests_used=3|4|5|6|7|8|9|10|11|12|13|14|15" --show "$SHOW" --interval 1 --timeout 180 --save s03-three-requests >"$OUT/s03-three.json"
  # 3
  etext thread-goal-policy-summary s03-banner-before-reload >"$OUT/s03-banner-before-reload.txt"
  goal_e "$S" s03-api-before-reload >/dev/null
  E reload --save s03-reload >/dev/null
  E wait --role button --name "新建任务" --timeout 90 >/dev/null
  E wait --testid thread-goal-policy-summary --timeout 30 >/dev/null || open_session "$(session_title "$S")" s03
  etext thread-goal-policy-summary s03-banner-after-reload >"$OUT/s03-banner-after-reload.txt"
  goal_e "$S" s03-api-after-reload >/dev/null
  # 4 输入框默认（排队）发送补充消息
  E count --testid goal-mode-tag --save s03-goal-mode-tag-before-supplement >/dev/null
  send_plain "What is 2 + 2? Reply with only the number." s03-supplement || true
  E screenshot --save s03-supplement-sent >/dev/null
  vr api GET $API/session/$S/queue --on electron --save s03-queue-after-supplement >/dev/null
  # 5
  poll_e "$S" --until goal.execution.wait_reason=verification --show "$SHOW" --interval 1 --timeout 600 --save s03-verifying >/dev/null
  poll_e "$S" --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 600 --save s03-run >/dev/null
  turn_end 180
  wait_reply "$S" "What is 2 + 2" 120 s03-history
  goal_e "$S" s03-final-goal >/dev/null
  vr snapshot --session "$S" --on electron --save s03 >/dev/null
  CH=$(verifier_children s03); echo "$CH" >"$OUT/s03-verifier-children"
  for c in $CH; do vr snapshot --session "$c" --on electron --save "s03-verifier-$c" >/dev/null; done
  end_scenario
  ;;
S16)
  MODE=${S16_MODE:-hold}; echo "$MODE" >"$OUT/s16-mode"
  m3_up electron || exit 1
  m2_close_popups
  # 1
  m2_send_goal_electron "Run the shell command sleep 20 in the foreground, then write step.txt containing 1, then stop." s16-create
  S=$(m2_latest_session); echo "$S" >"$OUT/session"
  E click --testid thread-goal-banner-pause --save s16-pause >/dev/null
  poll_e "$S" --until goal.status=paused --show "$SHOW" --interval 1 --timeout 30 --save s16-paused >/dev/null
  turn_end 60
  # 2 输入框普通发送（Goal 暂停中，M4 起按普通对话执行）
  send_plain "Start the shell command python3 -m http.server 8767 as a background task (bash tool with run_in_background: true) and end your turn right away." s16-bg || true
  sleep 3
  turn_end 180
  wait_reply "$S" "http.server 8767" 120 s16-bg-history
  bg_tasks "$S" s16-bg-tasks-step2 >/dev/null
  port_probe 8767 s16-port-step2 >/dev/null
  goal_e "$S" s16-goal-before-resume >/dev/null
  E count --testid thread-goal-banner-resume --save s16-resume-button-before >/dev/null
  # 3 连续两次快速点 thread-goal-banner-resume。屏障规则按添加顺序匹配：
  #   hold 模式：第一条暂扣下一个 PATCH .../goal（恢复请求），第二条只记录之后的 PATCH（第二次点击若再发请求就会记在这里）
  #   nohold 模式：只加记录规则
  E barrier clear >/dev/null
  if [ "$MODE" = hold ]; then
    E barrier add --method PATCH --path-contains /goal --times 1 --save s16-barrier-rule-hold >/dev/null
  fi
  E barrier add --method PATCH --path-contains /goal --record-only --times 20 --save s16-barrier-rule-record >/dev/null
  click_one() { # <k>：一次点击，记开始与结束时刻和结果
    local t0 t1 out
    t0=$(now_ms)
    out=$(node "$V" electron click --testid thread-goal-banner-resume --timeout 5 --run "$RID" 2>&1)
    t1=$(now_ms)
    printf '%s' "$out" | python3 -c 'import json,sys
raw=sys.stdin.read()
try: r=json.loads(raw)
except Exception: r={"raw":raw[:500]}
print(json.dumps({"click":int(sys.argv[1]),"startAt":int(sys.argv[2]),"endAt":int(sys.argv[3]),"result":r},ensure_ascii=False))' "$1" "$t0" "$t1" >"$OUT/s16-click-$1.json"
  }
  echo "$(now_ms)" >"$OUT/resume-click-at-ms"
  click_one 1 & C1=$!
  sleep 0.05
  click_one 2 & C2=$!
  wait "$C1" "$C2"
  echo "$(now_ms)" >"$OUT/resume-click-done-ms"
  E barrier list --save s16-barrier-after-clicks >"$OUT/s16-barrier-after-clicks.json"
  E count --testid thread-goal-banner-resume --save s16-resume-button-after-clicks >/dev/null
  E screenshot --save s16-after-clicks >/dev/null
  if [ "$MODE" = hold ]; then
    goal_e "$S" s16-goal-while-held >/dev/null
    sleep 1
    E barrier list --save s16-barrier-before-release >"$OUT/s16-barrier-before-release.json"
    echo "$(now_ms)" >"$OUT/resume-release-at-ms"
    E barrier release --save s16-barrier-release >/dev/null
  fi
  sleep 3
  E barrier list --save s16-barrier-after-release >"$OUT/s16-barrier-after-release.json"
  toast_burst s16-toasts 3
  # 4
  poll_e "$S" --until "$TERMINAL" --show "$SHOW" --interval 1 --timeout 420 --save s16-run >/dev/null
  turn_end 120
  goal_e "$S" s16-final >/dev/null
  vr snapshot --session "$S" --on electron --save s16 >/dev/null
  bg_tasks "$S" s16-bg-tasks-final >/dev/null
  E barrier list --save s16-barrier-final >/dev/null
  E barrier clear >/dev/null
  end_scenario
  port_closed_after_down 8767
  ;;
S22)
  m3_up electron || exit 1
  m2_close_popups
  O1="Run the shell command sleep 60 in the foreground, then write v.txt containing one."
  O2="Run the shell command sleep 60 in the foreground, then write v.txt containing two."
  O3="Run the shell command sleep 60 in the foreground, then write v.txt containing three."
  m2_send_goal_electron "$O1" s22-create
  S=$(m2_latest_session); echo "$S" >"$OUT/session"
  goal_e "$S" s22-goal-v0 >/dev/null
  # 2 屏障：暂扣下一个修改 Goal 的请求；之后的 PATCH 只记录
  E barrier clear >/dev/null
  E barrier add --method PATCH --path-contains /goal --times 1 --save s22-barrier-rule-hold >/dev/null
  E barrier add --method PATCH --path-contains /goal --record-only --times 50 --save s22-barrier-rule-record >/dev/null
  # 3
  E click --testid thread-goal-banner-edit-button --save s22-edit >/dev/null
  sleep 0.5
  etext message-textarea s22-textarea-after-edit-click >/dev/null
  clear_input
  type_checked "$O2" || input_abort
  E click --testid send-button --save s22-send-two >/dev/null
  E wait --testid goal-replace-confirm-modal --timeout 10 >/dev/null
  E aria --selector '[data-testid="goal-replace-confirm-modal"]' --save s22-replace-modal >/dev/null
  E click --selector "$REPLACE_BTN" --timeout 5 --save s22-replace-confirm >/dev/null
  # 4
  wait_barrier_held s22-barrier-held 15
  goal_e "$S" s22-goal-while-held >/dev/null
  vr api PATCH $API/session/$S/goal --on electron --data "$(python3 -c 'import json,sys;print(json.dumps({"objective":sys.argv[1]}))' "$O3")" --save s22-api-patch-three >/dev/null
  echo "$(now_ms)" >"$OUT/s22-release-at-ms"
  E barrier release --save s22-barrier-release >/dev/null
  # 5
  toast_burst s22-toasts-step5 6
  E screenshot --save s22-step5 >/dev/null
  etext thread-goal-banner-objective s22-banner-objective-step5 >/dev/null
  etext message-textarea s22-textarea-step5 >/dev/null
  E aria --save s22-page-aria-step5 >/dev/null
  goal_e "$S" s22-goal-step5 >/dev/null
  # 5→6 之间不自动重试：采样 objective 6 次
  goal_samples "$S" 6 s22-objective-samples
  # 6
  E click --testid send-button --save s22-resend >/dev/null
  E wait --testid goal-replace-confirm-modal --timeout 10 >/dev/null
  E click --selector "$REPLACE_BTN" --timeout 5 --save s22-resend-confirm >/dev/null
  sleep 3
  goal_e "$S" s22-goal-step6 >/dev/null
  E count --testid goal-mode-tag --save s22-goal-mode-tag-step6 >/dev/null
  etext message-textarea s22-textarea-step6 >/dev/null
  # 7
  E barrier clear >/dev/null
  E barrier add --method PATCH --path-contains /goal --times 1 --save s22-barrier-rule-hold-budget >/dev/null
  E barrier add --method PATCH --path-contains /goal --record-only --times 50 >/dev/null
  clear_input
  type_checked "/goal budget=300K" || input_abort
  sleep 0.5
  E click --testid send-button --save s22-send-budget >/dev/null
  wait_barrier_held s22-barrier-held-budget 15
  vr api PATCH $API/session/$S/goal --on electron --data '{"token_budget":400000}' --save s22-api-patch-budget >/dev/null
  echo "$(now_ms)" >"$OUT/s22-release-budget-at-ms"
  E barrier release --save s22-barrier-release-budget >/dev/null
  toast_burst s22-toasts-step7 6
  E screenshot --save s22-step7 >/dev/null
  etext message-textarea s22-textarea-step7 >/dev/null
  E aria --save s22-page-aria-step7 >/dev/null
  goal_e "$S" s22-goal-step7 >/dev/null
  goal_samples "$S" 4 s22-budget-samples
  E barrier list --save s22-barrier-final >/dev/null
  E barrier clear >/dev/null
  vr snapshot --session "$S" --on electron --save s22 >/dev/null
  end_scenario
  ;;
S23)
  m3_up electron || exit 1
  m2_close_popups
  m2_send_goal_electron "Run the shell command sleep 60 in the foreground, then write w.txt containing ok." s23-create
  S=$(m2_latest_session); echo "$S" >"$OUT/session"
  # 1 暂停：只记录（不分方法）
  E barrier clear >/dev/null
  E barrier add --path-contains /goal --record-only --times 50 --save s23-barrier-rule-record-step1 >/dev/null
  E click --testid thread-goal-banner-pause --save s23-pause >/dev/null
  poll_e "$S" --until goal.status=paused --show "$SHOW" --interval 1 --timeout 30 --save s23-paused >/dev/null
  turn_end 60
  E barrier list --save s23-barrier-step1 >"$OUT/s23-barrier-step1.json"
  goal_e "$S" s23-goal-paused >/dev/null
  # 2 暂扣恢复请求；暂扣期间接口改预算；放行
  E barrier clear >/dev/null
  E barrier add --method PATCH --path-contains /goal --times 1 --save s23-barrier-rule-hold >/dev/null
  E barrier add --path-contains /goal --record-only --times 50 >/dev/null
  E click --testid thread-goal-banner-resume --save s23-resume-1 >/dev/null
  wait_barrier_held s23-barrier-held 15
  vr api PATCH $API/session/$S/goal --on electron --data '{"token_budget":500000}' --save s23-api-patch-budget >/dev/null
  echo "$(now_ms)" >"$OUT/s23-release-at-ms"
  E barrier release --save s23-barrier-release >/dev/null
  # 3
  toast_burst s23-toasts-step3 6
  E screenshot --save s23-step3 >/dev/null
  E aria --save s23-page-aria-step3 >/dev/null
  sleep 1
  goal_e "$S" s23-goal-step3 >/dev/null
  etext thread-goal-banner-status s23-banner-status-step3 >/dev/null
  # 4 再次恢复；进行中后清除
  E barrier clear >/dev/null
  E barrier add --path-contains /goal --record-only --times 50 --save s23-barrier-rule-record-step4 >/dev/null
  echo "$(now_ms)" >"$OUT/s23-resume2-at-ms"
  E click --testid thread-goal-banner-resume --save s23-resume-2 >/dev/null
  for _ in $(seq 1 20); do
    st=$(node "$V" electron text --testid thread-goal-banner-status --timeout 2 --run "$RID" 2>/dev/null | jget "d.get('text')")
    [ "$st" = 进行中 ] && break
    sleep 0.5
  done
  etext thread-goal-banner-status s23-banner-status-step4 >/dev/null
  goal_e "$S" s23-goal-step4-active >/dev/null
  sleep 8
  E click --testid thread-goal-banner-clear --save s23-clear >/dev/null
  E click --selector "$CLEAR_BTN" --timeout 5 --save s23-clear-confirm >/dev/null
  E wait --testid thread-goal-banner --state hidden --timeout 30 >/dev/null
  sleep 1
  E barrier list --save s23-barrier-step4 >"$OUT/s23-barrier-step4.json"
  goal_e "$S" s23-goal-after-clear >/dev/null
  E barrier clear >/dev/null
  E click --testid stop-button --timeout 5 >/dev/null
  vr snapshot --session "$S" --on electron --save s23 >/dev/null
  end_scenario
  ;;
S24)
  m3_up electron || exit 1
  m2_close_popups
  OBJ="Create a file named page.html containing a heading that says Hello."
  type_checked "/goal $OBJ" || input_abort
  E click --testid send-button --save s24-create-send >/dev/null
  E count --testid goal-mode-tag --save s24-goal-mode-tag-step1 >/dev/null
  E wait --testid thread-goal-banner --timeout 60 --save s24-create-banner >/dev/null
  E count --testid goal-mode-tag --save s24-goal-mode-tag-step1b >/dev/null
  S=$(m2_latest_session); echo "$S" >"$OUT/session"
  # 2 Goal Turn 运行中按 Enter 发送（默认排队）
  T2=$(wait_open_goal_turn "$S" 60 s24-step2-running) || m2_log "S24: goal turn not seen running before step 2"
  echo "${T2:-}" >"$OUT/s24-step2-goal-turn"
  E count --testid stop-button --save s24-stop-button-step2 >/dev/null
  type_checked "Also make the heading text bold." || input_abort
  echo "$(now_ms)" >"$OUT/s24-step2-at-ms"
  E press --testid message-textarea --key Enter --save s24-step2-enter >/dev/null
  sleep 1.2
  E count --testid goal-replace-confirm-modal --save s24-replace-dialog-step2 >/dev/null
  # 3
  vr api GET $API/session/$S/queue --on electron --save s24-queue-step3 >/dev/null
  E aria --save s24-page-aria-step3 >/dev/null
  E screenshot --save s24-step3 >/dev/null
  deadline=$(( $(date +%s) + 300 ))
  while [ "$(date +%s)" -lt "$deadline" ]; do
    q=$(node "$V" api GET $API/session/$S/queue --on electron --run "$RID" 2>/dev/null | jget "len((d.get('body') or {}).get('items') or [])")
    h=$(node "$V" api GET $API/session/$S/message --on electron --run "$RID" 2>/dev/null | python3 -c 'import json,sys
d=json.load(sys.stdin); ms=(d.get("body") or {}).get("messages") or []
print(1 if any(m.get("role")=="user" and "heading text bold" in str(m.get("msg_content","")) for m in ms) else 0)')
    printf '{"at":%s,"queueItems":"%s","inHistory":"%s"}\n' "$(now_ms)" "$q" "$h" >>"$OUT/s24-supplement-trajectory.jsonl"
    [ "$q" = 0 ] && [ "$h" = 1 ] && break
    sleep 1
  done
  echo "$(now_ms)" >"$OUT/s24-supplement-processed-at-ms"
  # 4 下一个 Goal Turn 运行中：先按 verify 写的 ⇧⌘⏎；输入框文字没有发出时，再按产品在默认（Enter 发送）设置下的
  #   “立即发送”快捷键 ⌘⏎（设置页“跟进消息行为”说明里显示的单次反转键），作为补充路径
  if T4=$(wait_open_goal_turn "$S" 240 s24-step4-running "${T2:-}"); then
    echo "$T4" >"$OUT/s24-step4-goal-turn"
    type_checked "Use a blue color for the heading." || input_abort
    echo "$(now_ms)" >"$OUT/s24-step4-at-ms"
    E press --testid message-textarea --key "Meta+Shift+Enter" --save s24-step4-send >/dev/null
    sleep 1
    left=$(E text --testid message-textarea --save s24-step4-textarea-after-shift-cmd-enter | jget "(d.get('text') or '').strip()")
    if [ -n "$left" ]; then
      echo "not-sent" >"$OUT/s24-step4-shift-cmd-enter"
      m2_log "S24: Meta+Shift+Enter did not send; using Meta+Enter"
      if [ "$(goal_turn_open "$S")" = "open:$T4" ]; then
        echo "$(now_ms)" >"$OUT/s24-step4-cmd-enter-at-ms"
        E press --testid message-textarea --key "Meta+Enter" --save s24-step4-cmd-enter >/dev/null
        sleep 1
        E text --testid message-textarea --save s24-step4-textarea-after-cmd-enter >/dev/null
      else
        echo "goal-turn-closed-before-cmd-enter" >"$OUT/s24-step4-cmd-enter-skipped"
      fi
    else
      echo "sent" >"$OUT/s24-step4-shift-cmd-enter"
    fi
    E count --testid goal-replace-confirm-modal --save s24-replace-dialog-step4 >/dev/null
    E aria --save s24-page-aria-step4 >/dev/null
  else
    echo "no-goal-turn-running" >"$OUT/s24-step4-skipped"
    m2_log "S24: no running Goal Turn for step 4"
  fi
  # 5
  poll_e "$S" --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 600 --save s24-run >/dev/null
  turn_end 180
  goal_e "$S" s24-final >/dev/null
  vr api GET $API/session/$S/message --on electron --save s24-history >/dev/null
  E aria --save s24-page-aria-final >/dev/null
  vr snapshot --session "$S" --on electron --save s24 >/dev/null
  end_scenario
  ;;
S25)
  m3_up electron || exit 1
  m2_close_popups
  m2_send_goal_electron "Run the shell command sleep 60 in the foreground, then write p.txt containing ok." s25-create
  S=$(m2_latest_session); echo "$S" >"$OUT/session"
  goal_e "$S" s25-goal-created >/dev/null
  E click --testid thread-goal-banner-pause --save s25-pause >/dev/null
  poll_e "$S" --until goal.status=paused --show "$SHOW" --interval 1 --timeout 30 --save s25-paused >/dev/null
  turn_end 60
  # 2
  send_plain "What is 3 + 4? Reply with only the number." s25-side || true
  wait_reply "$S" "3 + 4" 120 s25-side-history
  turn_end 60
  # 3
  goal_e "$S" s25-goal-step3 >/dev/null
  etext thread-goal-banner-status s25-banner-status-step3 >/dev/null
  E count --testid continue-button --save s25-continue-count-step3 >/dev/null
  E count --testid thread-goal-banner-resume --save s25-banner-resume-count-step3 >/dev/null
  E screenshot --save s25-step3 >/dev/null
  # 4
  E click --testid thread-goal-banner-resume --save s25-resume >/dev/null
  for _ in $(seq 1 20); do
    st=$(node "$V" electron text --testid thread-goal-banner-status --timeout 2 --run "$RID" 2>/dev/null | jget "d.get('text')")
    [ "$st" = 进行中 ] && break
    sleep 0.5
  done
  etext thread-goal-banner-status s25-banner-status-resumed >/dev/null
  type_checked "/goal" || input_abort
  E wait --testid slash-command-palette --timeout 5 --save s25-slash-palette >/dev/null
  E press --testid message-textarea --key Enter >/dev/null
  E wait --testid goal-mode-tag --timeout 5 --save s25-goal-mode-tag-shown >/dev/null
  E count --testid goal-mode-tag --save s25-goal-mode-tag-before-remove >/dev/null
  E aria --selector '[data-testid="goal-mode-tag"]' --save s25-goal-mode-tag-aria >/dev/null
  echo "$(now_ms)" >"$OUT/s25-tag-removed-at-ms"
  E click --testid goal-mode-tag --save s25-goal-mode-tag-remove >/dev/null
  E count --testid goal-mode-tag --save s25-goal-mode-tag-after-remove >/dev/null
  # 5
  poll_e "$S" --until goal.status=active --hold 10 --show "$SHOW" --interval 1 --timeout 20 --save s25-hold-active >/dev/null
  etext thread-goal-banner-status s25-banner-status-step5 >/dev/null
  goal_e "$S" s25-goal-step5 >/dev/null
  vr snapshot --session "$S" --on electron --save s25 >/dev/null
  end_scenario
  ;;
S26)
  m3_up electron || exit 1
  m2_close_popups
  m2_send_goal_electron "Run the shell command sleep 60 in the foreground, then write r.txt containing old." s26-create
  S=$(m2_latest_session); echo "$S" >"$OUT/session"
  goal_e "$S" s26-goal-old >/dev/null
  # 2
  type_checked "/goal" || input_abort
  E wait --testid slash-command-palette --timeout 5 --save s26-slash-palette >/dev/null
  E press --testid message-textarea --key Enter >/dev/null
  E wait --testid goal-mode-tag --timeout 5 --save s26-goal-mode-tag-shown >/dev/null
  type_checked "Write r.txt containing new, then stop." || input_abort
  E click --testid send-button --save s26-send-new >/dev/null
  # 3
  E wait --testid goal-replace-confirm-modal --timeout 10 >/dev/null
  E aria --selector '[data-testid="goal-replace-confirm-modal"]' --save s26-replace-modal >/dev/null
  E click --selector "$CANCEL_BTN" --timeout 5 --save s26-cancel >/dev/null
  sleep 1
  goal_e "$S" s26-goal-after-cancel >/dev/null
  # 4
  E click --testid send-button --save s26-send-new-again >/dev/null
  E wait --testid goal-replace-confirm-modal --timeout 10 >/dev/null
  E click --selector "$REPLACE_BTN" --timeout 5 --save s26-replace-confirm >/dev/null
  sleep 2
  E count --testid goal-mode-tag --save s26-goal-mode-tag-after-replace >/dev/null
  goal_e "$S" s26-goal-new >/dev/null
  E aria --save s26-page-aria-after-replace >/dev/null
  # 5
  E click --testid thread-goal-banner-pause --save s26-pause >/dev/null
  poll_e "$S" --until goal.status=paused --show "$SHOW" --interval 1 --timeout 30 --save s26-paused >/dev/null
  turn_end 60
  E click --testid thread-goal-banner-edit-button --save s26-edit >/dev/null
  sleep 0.5
  clear_input
  type_checked "Write r.txt containing final, then stop." || input_abort
  E click --testid send-button --save s26-send-final >/dev/null
  E wait --testid goal-replace-confirm-modal --timeout 10 >/dev/null
  echo "$(now_ms)" >"$OUT/s26-final-confirm-at-ms"
  E click --selector "$REPLACE_BTN" --timeout 5 --save s26-final-confirm >/dev/null
  poll_e "$S" --until goal.status=active --show "$SHOW" --interval 0.5 --timeout 10 --save s26-final-active >/dev/null
  # 6
  poll_e "$S" --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 420 --save s26-run >/dev/null
  turn_end 120
  goal_e "$S" s26-final >/dev/null
  vr api GET $API/agent/mavis/session --on electron --save s26-session-list >/dev/null
  E aria --save s26-page-aria-final >/dev/null
  vr snapshot --session "$S" --on electron --save s26 >/dev/null
  end_scenario
  ;;
S27)
  m3_up electron || exit 1
  m2_close_popups
  m2_send_goal_electron "Write the numbers 1 to 3 into count.txt, one number per line, then stop." s27-create
  S=$(m2_latest_session); echo "$S" >"$OUT/session"
  # 2
  poll_e "$S" --until goal.execution.wait_reason=verification --show "$SHOW" --interval 0.5 --timeout 300 --save s27-verifying >/dev/null
  E count --testid continue-button --save s27-continue-count >/dev/null
  # 3
  send_plain "Please also add a final line with the word end." s27-supplement || true
  # 4
  poll_e "$S" --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 600 --save s27-run >/dev/null
  turn_end 180
  goal_e "$S" s27-final >/dev/null
  vr snapshot --session "$S" --on electron --save s27 >/dev/null
  end_scenario
  ;;
S28)
  m3_up electron || exit 1
  m2_close_popups
  # 另一个会话（步骤 3 切换会话用）
  send_plain "Reply with exactly the word PONG and nothing else." s28-other || true
  sleep 3; turn_end 60
  O=$(m2_latest_session); echo "$O" >"$OUT/other-session"
  new_task
  # 1
  m2_send_goal_electron "Run the shell command sleep 30 in the foreground, then write t.txt containing ok, then stop." s28-create
  S=$(m2_latest_session); echo "$S" >"$OUT/session"
  wait_goal_turn_running "$S" 60 s28-step1-running || true
  E count --testid continue-button --save s28-continue-count-step1 >/dev/null
  # 2 输入框的停止按钮
  echo "$(now_ms)" >"$OUT/s28-stop-at-ms"
  E click --testid stop-button --save s28-stop >/dev/null
  for _ in $(seq 1 30); do
    st=$(node "$V" electron text --testid thread-goal-banner-status --timeout 2 --run "$RID" 2>/dev/null | jget "d.get('text')")
    [ "$st" = 已停止 ] && break
    sleep 0.5
  done
  turn_end 30
  etext thread-goal-banner-status s28-banner-status-step2 >/dev/null
  E count --testid continue-button --save s28-continue-count-step2 >/dev/null
  goal_e "$S" s28-goal-step2 >/dev/null
  # 3 重载后数；切到另一会话再切回后数
  E reload --save s28-reload >/dev/null
  E wait --role button --name "新建任务" --timeout 90 >/dev/null
  E wait --testid thread-goal-banner --timeout 20 >/dev/null || open_session "$(session_title "$S")" s28-after-reload
  E wait --testid thread-goal-banner --timeout 20 >/dev/null
  sleep 1
  E count --testid continue-button --save s28-continue-count-after-reload >/dev/null
  goal_e "$S" s28-goal-after-reload >/dev/null
  open_session "$(session_title "$O")" s28-other
  sleep 2
  E count --testid thread-goal-banner --save s28-banner-count-other-session >/dev/null
  open_session "$(session_title "$S")" s28-back
  E wait --testid thread-goal-banner --timeout 20 >/dev/null
  sleep 1
  E count --testid continue-button --save s28-continue-count-after-switch >/dev/null
  goal_e "$S" s28-goal-after-switch >/dev/null
  # 4
  echo "$(now_ms)" >"$OUT/s28-continue-click-at-ms"
  E click --testid continue-button --save s28-continue-click >/dev/null
  for _ in $(seq 1 20); do
    st=$(node "$V" electron text --testid thread-goal-banner-status --timeout 2 --run "$RID" 2>/dev/null | jget "d.get('text')")
    [ "$st" = 进行中 ] && break
    sleep 0.5
  done
  etext thread-goal-banner-status s28-banner-status-step4 >/dev/null
  E count --testid continue-button --save s28-continue-count-step4 >/dev/null
  poll_e "$S" --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 420 --save s28-run >/dev/null
  turn_end 120
  goal_e "$S" s28-final >/dev/null
  vr snapshot --session "$S" --on electron --save s28 >/dev/null
  end_scenario
  ;;
S29)
  m3_up electron || exit 1
  m2_close_popups
  E notifications --save s29-notifications-start >"$OUT/s29-notifications-start.json"
  # ---- S29 会话 A
  m2_send_goal_electron "Start a background subagent task (task tool, run in background) that waits 40 seconds and then writes sub.txt containing sub-done. End your turn right away without waiting. The goal is met only when sub.txt contains sub-done." s29-create
  A=$(m2_latest_session); echo "$A" >"$OUT/session-A"; echo "$A" >"$OUT/session"
  poll_e "$A" --until goal.execution.wait_reason=required_background --show "$SHOW" --interval 1 --timeout 150 --save s29-waiting >"$OUT/s29-waiting.json"
  bg_tasks "$A" s29-bg-tasks-waiting >/dev/null
  # 2 发补充消息后立即回首页
  send_plain "What is 17 + 25? Answer with just the number." s29-side || true
  new_task
  echo "$(now_ms)" >"$OUT/s29-home-at-ms"
  wait_reply "$A" "17 + 25" 120 s29-side-history
  bg_tasks "$A" s29-bg-tasks-after-side >/dev/null
  # 3
  poll_e "$A" --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 600 --save s29-run >/dev/null
  sleep 6
  vr api GET $API/session/$A --on electron --save s29-session-A >/dev/null
  # 4
  E notifications --save s29-notifications-step4 >"$OUT/s29-notifications-step4.json"
  E notifications click --body 目标已完成 --save s29-notification-click >"$OUT/s29-notification-click.json"
  sleep 2
  etext thread-goal-banner-objective s29-objective-after-click >/dev/null
  E screenshot --save s29-after-click >/dev/null
  goal_e "$A" s29-final >/dev/null
  vr snapshot --session "$A" --on electron --save s29 >/dev/null
  # ---- S29b 会话 B（问卷）
  new_task
  m2_send_goal_electron 'First call the ask_user tool exactly once with one single-choice question "Which fruit?" and two options: "Apple" (recommended, listed first) and "Banana". Do not set requiresExplicitResponse. After you get the answer, write the chosen fruit name to fruit.txt (only the name).' s29b-create
  B=$(m2_latest_session); echo "$B" >"$OUT/session-B"
  new_task
  echo "$(now_ms)" >"$OUT/s29b-home-at-ms"
  vr poll "$API/agent/mavis/questionnaire/pending?session_id=$B" --on electron --until request.status=0 --show request.id,request.expires_at --interval 2 --timeout 180 --save s29b-pending >/dev/null
  sleep 8
  E notifications --save s29b-notifications-step2 >"$OUT/s29b-notifications-step2.json"
  vr api GET $API/session/$B --on electron --save s29b-session-B >/dev/null
  # 3 回到会话 B 回答
  open_session "$(session_title "$B")" s29b-B
  E wait --role radiogroup --name "Which fruit?" --timeout 30 --save s29b-card >/dev/null
  E click --role radio --name "Banana" --exact --save s29b-answer >/dev/null
  poll_e "$B" --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 420 --save s29b-run >/dev/null
  goal_e "$B" s29b-final-B >/dev/null
  vr snapshot --session "$B" --on electron --save s29b-B >/dev/null
  # 4 会话 C：接口暂停（等同手机端暂停）
  new_task
  m2_send_goal_electron "Run the shell command sleep 60 in the foreground, then write q.txt containing ok." s29b-create-C
  C=$(m2_latest_session); echo "$C" >"$OUT/session-C"
  new_task
  sleep 3
  echo "$(now_ms)" >"$OUT/s29b-pause-C-at-ms"
  vr api PATCH $API/session/$C/goal --on electron --data '{"status":"paused"}' --save s29b-pause-C >/dev/null
  sleep 20
  E notifications --save s29b-notifications-step4 >"$OUT/s29b-notifications-step4.json"
  vr api GET $API/session/$C --on electron --save s29b-session-C >/dev/null
  goal_e "$C" s29b-goal-C >/dev/null
  vr snapshot --session "$C" --on electron --save s29b-C >/dev/null
  end_scenario
  ;;
S31)
  m3_up electron --fault || exit 1
  m2_close_popups
  RULE=$(vr fault add --on electron --session next --role verifier --preset upstream-50113 --note "S31: verifier child requests return 50113" --save fault-rule | jget "(d.get('rule') or {}).get('id') or d.get('id')")
  echo "$RULE" >"$OUT/rule-id"
  m2_send_goal_electron "Write the numbers 1 to 3 into count.txt, one number per line, then stop." s31-create
  S=$(m2_latest_session); echo "$S" >"$OUT/session"
  # 2
  poll_e "$S" --until "goal.status=paused|complete|blocked|budget_limited|usage_limited" --show "$SHOW" --interval 2 --timeout 420 --save s31-paused >/dev/null
  turn_end 60
  goal_e "$S" s31-goal-paused >/dev/null
  vr snapshot --session "$S" --on electron --save s31-paused-snap >/dev/null
  # 3 打开右侧 Subagents 的 “Goal verification”
  E aria --save s31-parent-aria-before >/dev/null
  E click --role button --name "Goal verification" --exact --timeout 10 --save s31-open-child >/dev/null || {
    E click --role button --name "Subagents" --exact --timeout 5 >/dev/null
    E click --role button --name "Goal verification" --timeout 10 --save s31-open-child-retry >/dev/null
  }
  sleep 2
  E aria --save s31-child-aria >/dev/null
  E count --testid goal-verifier-managed-notice --save s31-child-notice-count >/dev/null
  E count --role button --name "重试" --exact --save s31-child-retry-count >/dev/null
  E count --testid continue-button --save s31-child-continue-count >/dev/null
  E count --testid thread-goal-banner --save s31-child-banner-count >/dev/null
  E screenshot --save s31-child >/dev/null
  E click --role button --name "打开父目标会话" --exact --timeout 10 --save s31-open-parent >/dev/null
  sleep 2
  etext thread-goal-banner-objective s31-objective-after-open-parent >/dev/null
  etext thread-goal-banner-status s31-banner-status-after-open-parent >/dev/null
  # 4
  vr fault disable "$RULE" --on electron --save fault-disable >/dev/null
  echo "$(now_ms)" >"$OUT/s31-resume-at-ms"
  E click --testid thread-goal-banner-resume --save s31-resume >/dev/null
  # 5
  poll_e "$S" --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 600 --save s31-run >/dev/null
  turn_end 120
  goal_e "$S" s31-final >/dev/null
  vr snapshot --session "$S" --on electron --save s31 >/dev/null
  vr fault log --on electron --session "$S" --tail 500 --save fault-s31 >/dev/null
  end_scenario
  ;;
S33)
  m3_up electron || exit 1
  m2_close_popups
  m2_send_goal_electron 'First call the ask_user tool exactly once with one single-choice question "Which fruit?" and two options: "Apple" (recommended, listed first) and "Banana". Do not set requiresExplicitResponse. After you get the answer, write the chosen fruit name to fruit.txt (only the name).' s33-create
  S=$(m2_latest_session); echo "$S" >"$OUT/session"
  E wait --role radiogroup --name "Which fruit?" --timeout 150 --save s33-card >/dev/null
  vr api GET "$API/agent/mavis/questionnaire/pending?session_id=$S" --on electron --save s33-pending-step1 >/dev/null
  goal_e "$S" s33-goal-step1 >/dev/null
  # 2
  E click --testid thread-goal-banner-pause --save s33-pause >/dev/null
  poll_e "$S" --until goal.status=paused --show "$SHOW" --interval 1 --timeout 30 --save s33-paused >/dev/null
  echo "$(now_ms)" >"$OUT/s33-paused-at-ms"
  # 3 等 6 分钟
  sleep 360
  vr api GET "$API/agent/mavis/questionnaire/pending?session_id=$S" --on electron --save s33-pending-step3 >/dev/null
  goal_e "$S" s33-goal-step3 >/dev/null
  vr api GET $API/session/$S/message --on electron --save s33-history-step3 >/dev/null
  E screenshot --save s33-step3 >/dev/null
  # 4
  E click --role radio --name "Banana" --exact --save s33-answer >/dev/null
  sleep 2
  vr api GET "$API/agent/mavis/questionnaire/pending?session_id=$S" --on electron --save s33-pending-after-answer >/dev/null
  echo "$(now_ms)" >"$OUT/s33-resume-at-ms"
  E click --testid thread-goal-banner-resume --save s33-resume >/dev/null
  poll_e "$S" --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 420 --save s33-run >/dev/null
  turn_end 120
  goal_e "$S" s33-final >/dev/null
  vr snapshot --session "$S" --on electron --save s33 >/dev/null
  end_scenario
  ;;
S39)
  m3_up electron || exit 1
  m2_close_popups
  m2_send_goal_electron "This goal cannot be done yet because the input file is missing. Call update_goal with status blocked and a short reason, then stop." s39-create
  S=$(m2_latest_session); echo "$S" >"$OUT/session"
  # 2
  poll_e "$S" --until "goal.status=blocked|complete|paused|budget_limited|usage_limited" --show "$SHOW" --interval 2 --timeout 300 --save s39-blocked >/dev/null
  turn_end 120
  sleep 1
  goal_e "$S" s39-goal-blocked >/dev/null
  E count --testid continue-button --save s39-continue-count-step2 >/dev/null
  etext thread-goal-banner-status s39-banner-status-step2 >/dev/null
  # 3
  send_plain "What is 6 + 7? Reply with only the number." s39-side || true
  wait_reply "$S" "6 + 7" 120 s39-side-history
  turn_end 60
  sleep 1
  goal_e "$S" s39-goal-step3 >/dev/null
  etext thread-goal-banner-status s39-banner-status-step3 >/dev/null
  E count --testid continue-button --save s39-continue-count-step3 >/dev/null
  # 4
  echo "$(now_ms)" >"$OUT/s39-continue-click-at-ms"
  E click --testid continue-button --save s39-continue-click >/dev/null
  sleep 12
  goal_e "$S" s39-goal-after-click >/dev/null
  etext thread-goal-banner-status s39-banner-status-after-click >/dev/null
  poll_e "$S" --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 300 --save s39-run >/dev/null
  turn_end 120
  goal_e "$S" s39-final >/dev/null
  vr snapshot --session "$S" --on electron --save s39 >/dev/null
  end_scenario
  ;;
*) echo "unknown scenario $SCN" >&2; exit 2 ;;
esac
m2_log "scenario $SCN done"
