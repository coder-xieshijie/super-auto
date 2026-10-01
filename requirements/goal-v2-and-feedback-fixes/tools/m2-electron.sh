#!/usr/bin/env bash
# M2 Electron 入口场景：verify.md S07、S03、S06、S32（同一实例，--fault）、S38（--fault，强制结束重启）、
# S10（defaultMainTurns=3、graceSteps=1 的配置注入）、S01（基线数据 + defaultMainTurns=10）、S41 的 Electron 一行。
# 用法（agent-archon worktree 根目录）：bash <tools>/m2-electron.sh <A|S38|S10|S01|S41> <尝试名> [from-data runId]
#   A：S07 → S03 → S06 → S32，证据分别写在 <M2_ROOT>/S07|S03|S06|S32/<尝试名>/ 下各自的动作名；实例级文件在 S07 目录
set -u
source "$(dirname "${BASH_SOURCE[0]}")/m2-lib.sh"
FLOW=$1
ATTEMPT=$2
FROM=${3:-}
E() { vr electron "$@"; }
etext() { E text --testid "$1" --timeout "${3:-10}" --save "$2" | jget "d.get('text')"; }
goal_e() { vr api GET $API/session/$1/goal --on electron --save "$2"; }
poll_e() { local s=$1; shift; vr poll $API/session/$s/goal --on electron "$@"; }
new_task() { E click --role button --name "新建任务" >/dev/null; sleep 1; }
open_session() { # open_session <标题>：关掉签到浮层，展开侧栏“未选项目”，点会话标题
  E click --role button --name "关闭签到" --exact --timeout 5 >/dev/null
  if ! E click --text "$1" --timeout 8 --save "open-$2" >/dev/null; then
    E click --role button --name "未选项目" --timeout 10 --save "open-$2-expand-project" >/dev/null
    if ! E click --text "$1" --timeout 10 --save "open-$2-retry" >/dev/null; then
      # 侧栏项目列表未加载时，用“搜索”对话框打开（S38 实测强制结束重启后侧栏一直 busy）
      E click --role button --name "搜索" --exact --save "open-$2-search" >/dev/null
      E fill --role textbox --name "搜索任务或运行命令" --value "$1" >/dev/null
      E click --selector "role=dialog >> role=button[name=\"$1\"]" --timeout 15 --save "open-$2-search-result" >/dev/null
    fi
  fi
}
turn_end() { E wait --testid stop-button --state hidden --timeout "${1:-120}" >/dev/null; }
send_msg() { # send_msg <文本>：普通发送（Enter 对应的发送按钮）
  E type --testid message-textarea --value "$1" >/dev/null
  E click --testid send-button >/dev/null
}

case $FLOW in
A)
  m2_begin S07 "$ATTEMPT"
  m2_up electron --fault || exit 1
  m2_close_popups
  E screenshot --save start >/dev/null
  # ---------------- S07 ----------------
  RULE=$(vr fault add --on electron --session next --nth 1 --action hold --note "S07 hold the first Goal's 1st main request tail" --save fault-rule-s07 | jget "d.get('rule',{}).get('id') or d.get('id') or d.get('ruleId')")
  echo "$RULE" >"$OUT/s07-rule-id"
  # 1
  m2_send_goal_electron "Write the numbers 1 to 3 into count.txt, one number per line, then stop." s07-create
  S=$(m2_latest_session); echo "$S" >"$OUT/s07-session"
  deadline=$(( $(date +%s) + 120 ))
  while [ "$(date +%s)" -lt "$deadline" ]; do
    held=$(vr fault pending --on electron | python3 -c 'import json,sys
d=json.load(sys.stdin); p=d.get("pending") or []
print(next((str(x["id"]) for x in p if x.get("kind")=="hold"),""))')
    [ -n "$held" ] && break
    sleep 1
  done
  echo "$held" >"$OUT/s07-held-pending-id"
  vr fault pending --on electron --save fault-s07-pending >/dev/null
  goal_e "$S" s07-old-goal >"$OUT/s07-old-goal.json"
  OLD=$(jget "d['body']['goal']['goal_id']" <"$OUT/s07-old-goal.json"); echo "$OLD" >"$OUT/s07-old-goal-id"
  m2_log "S07 held=$held old goal=$OLD"
  # 2
  E click --testid thread-goal-banner-clear --save s07-clear >/dev/null
  E click --selector '[data-testid="goal-clear-confirm-modal"] >> role=button[name="删除"]' --save s07-clear-confirm >/dev/null
  E wait --testid thread-goal-banner --state hidden --timeout 30 >/dev/null
  goal_e "$S" s07-after-clear >/dev/null
  # 3
  E type --testid message-textarea --value "/goal Reply with the single word DONE." >/dev/null
  E click --testid send-button --save s07-new-send >/dev/null
  poll_e "$S" --until "goal.status=active|complete|paused|blocked|budget_limited|usage_limited" --show "goal.goal_id,goal.status" --interval 1 --timeout 60 --save s07-new-goal >"$OUT/s07-new-goal.json"
  NEW=$(jget "d['final']['goal']['goal_id']" <"$OUT/s07-new-goal.json"); echo "$NEW" >"$OUT/s07-new-goal-id"
  # 4
  vr fault release --on electron --save fault-s07-release >/dev/null
  poll_e "$S" --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 420 --save s07-new-run >/dev/null
  turn_end 120
  goal_e "$S" s07-final-goal >/dev/null
  vr snapshot --session "$S" --on electron --save s07 >/dev/null
  vr fault log --on electron --session "$S" --tail 200 --save fault-s07 >/dev/null

  # ---------------- S03 ----------------
  new_task
  m2_send_goal_electron "Create five files a1.txt to a5.txt one at a time, each containing its own number. After writing each file, run the shell command sleep 5 in the foreground. Do all five in this single turn. Then call get_goal once, then verify all five files exist." s03-create
  S3=$(m2_latest_session); echo "$S3" >"$OUT/s03-session"
  # 2
  poll_e "$S3" --until "goal.requests_used=3|4|5|6|7|8|9|10|11|12|13|14|15" --show "$SHOW" --interval 1 --timeout 180 --save s03-three-requests >"$OUT/s03-three.json"
  # 3
  etext thread-goal-policy-summary s03-banner-before-reload >"$OUT/s03-banner-before-reload.txt"
  goal_e "$S3" s03-api-before-reload >/dev/null
  E reload --save s03-reload >/dev/null
  E wait --role button --name "新建任务" --timeout 90 >/dev/null
  E wait --testid thread-goal-policy-summary --timeout 30 >/dev/null || open_session "$(vr api GET $API/session/$S3 --on electron | jget "d['body']['session']['title']")" s03
  etext thread-goal-policy-summary s03-banner-after-reload >"$OUT/s03-banner-after-reload.txt"
  goal_e "$S3" s03-api-after-reload >/dev/null
  # 4 默认排队发送补充消息
  send_msg "What is 2 + 2? Reply with only the number."
  E screenshot --save s03-supplement-sent >/dev/null
  # 5
  poll_e "$S3" --until goal.execution.wait_reason=verification --show "$SHOW" --interval 1 --timeout 600 --save s03-verifying >/dev/null
  poll_e "$S3" --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 600 --save s03-run >/dev/null
  turn_end 180
  goal_e "$S3" s03-final-goal >/dev/null
  vr snapshot --session "$S3" --on electron --save s03 >/dev/null
  # verifier 子会话的 Inspector
  CHILD=$(python3 - "$OUT" <<'EOF'
import glob,json,sys,os
f=sorted(glob.glob(os.path.join(sys.argv[1],'*-s03-runtime-events.jsonl')))[-1]
for l in open(f):
    e=json.loads(l); p=e.get('fields',{}).get('payload') or {}
    if e.get('fields',{}).get('eventType')=='goal.verification_child_started' and p.get('childSessionId'):
        print(p['childSessionId'])
EOF
)
  echo "$CHILD" >"$OUT/s03-verifier-children"
  for c in $CHILD; do vr snapshot --session "$c" --on electron --save "s03-verifier-$c" >/dev/null; done
  E screenshot --save s03-final >/dev/null

  # ---------------- S06 ----------------
  new_task
  vr fault add --on electron --session next --nth 1 --action strip-usage --note "S06 strip usage of the 1st main request" --save fault-rule-s06 >/dev/null
  m2_send_goal_electron "Write the numbers 1 to 3 into count.txt, one number per line, then stop." s06-create
  S6=$(m2_latest_session); echo "$S6" >"$OUT/s06-session"
  poll_e "$S6" --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 420 --save s06-run >/dev/null
  turn_end 120
  etext thread-goal-tokens-used s06-tokens-text >"$OUT/s06-tokens-text.txt"
  E hover --testid thread-goal-tokens-used --save s06-tokens-hover >"$OUT/s06-tokens-hover.json"
  E aria --selector '[data-testid="thread-goal-banner"]' --save s06-banner-aria >/dev/null
  goal_e "$S6" s06-goal >/dev/null
  vr snapshot --session "$S6" --on electron --save s06 >/dev/null
  vr fault log --on electron --session "$S6" --tail 200 --save fault-s06 >/dev/null

  # ---------------- S32 ----------------
  # 前后读数：所有会话的 Goal（updated_at、status）
  vr api GET $API/agent/mavis/session --on electron --save s32-sessions >"$OUT/s32-sessions.json"
  SIDS=$(python3 -c 'import json,sys
d=json.load(open(sys.argv[1]))["body"]; items=d.get("sessions") or d.get("items") or []
print(" ".join(s["session_id"] for s in items))' "$OUT/s32-sessions.json")
  for s in $SIDS; do goal_e "$s" "s32-before-$s" >/dev/null; done
  echo "$SIDS" >"$OUT/s32-session-ids"
  m2_log "S32: sessions $SIDS"
  ;;
S38)
  m2_begin S38 "$ATTEMPT"
  m2_up electron --fault || exit 1
  m2_close_popups
  RULE=$(vr fault add --on electron --session next --nth 2 --action hang --note "S38 hang the 2nd main request" --save fault-rule-s38 | jget "d.get('rule',{}).get('id') or d.get('id') or d.get('ruleId')")
  echo "$RULE" >"$OUT/rule-id"
  # 1
  m2_send_goal_electron "Create files f1.txt, f2.txt, f3.txt one at a time, each containing its own number, then stop." s38-create
  S=$(m2_latest_session); echo "$S" >"$OUT/session"
  # 2
  deadline=$(( $(date +%s) + 180 ))
  while [ "$(date +%s)" -lt "$deadline" ]; do
    hung=$(vr fault pending --on electron | python3 -c 'import json,sys
d=json.load(sys.stdin); p=d.get("pending") or []
print(next((str(x["id"]) for x in p if x.get("kind")=="hang"),""))')
    [ -n "$hung" ] && break
    sleep 1
  done
  vr fault pending --on electron --save fault-s38-pending >/dev/null
  goal_e "$S" s38-before-kill >/dev/null
  E restart --force --save s38-force-restart >"$OUT/restart.json"
  vr fault disable "$RULE" --on electron --save fault-s38-disable >/dev/null
  m2_close_popups
  TITLE=$(vr api GET $API/session/$S --on electron | jget "d['body']['session']['title']")
  # 3
  goal_e "$S" s38-after-restart >/dev/null
  open_session "$TITLE" s38
  E wait --testid thread-goal-requests-used --timeout 30 >/dev/null
  etext thread-goal-policy-summary s38-banner-after-restart >"$OUT/banner-after-restart.txt"
  E hover --testid thread-goal-requests-used --save s38-requests-hover >"$OUT/requests-hover.json"
  poll_e "$S" --until "$TERMINAL" --show "$SHOW,goal.reserved_requests" --interval 3 --timeout 600 --save s38-run >/dev/null
  turn_end 120
  goal_e "$S" s38-final-goal >/dev/null
  etext thread-goal-policy-summary s38-banner-final >"$OUT/banner-final.txt"
  E hover --testid thread-goal-requests-used --save s38-requests-hover-final >"$OUT/requests-hover-final.json"
  vr snapshot --session "$S" --on electron --save s38 >/dev/null
  vr fault log --on electron --session "$S" --tail 300 --save fault-s38 >/dev/null
  m2_down
  ;;
S10)
  m2_begin S10 "$ATTEMPT"
  M2_UP_CONFIG=$(m2_config turns3 3 1) m2_up electron || exit 1
  E config --save s10-config >"$OUT/config.json"
  m2_close_popups
  # 1
  m2_send_goal_electron "Create files d1.txt, d2.txt, d3.txt, d4.txt, d5.txt one at a time, each containing its own number. In each response make at most one tool call. Keep working in this turn until all five exist." s10-create
  S=$(m2_latest_session); echo "$S" >"$OUT/session"
  # 2
  poll_e "$S" --until goal.status=budget_limited --show "$SHOW" --interval 2 --timeout 420 --save s10-budget >/dev/null
  turn_end 120
  vr snapshot --session "$S" --on electron --save s10 >/dev/null
  # 3
  etext thread-goal-policy-summary s10-policy-summary >"$OUT/policy-summary.txt"
  etext thread-goal-banner-budget-guide s10-budget-guide >"$OUT/budget-guide.txt"
  etext thread-goal-banner-status s10-banner-status >"$OUT/banner-status.txt"
  E hover --testid thread-goal-requests-used --save s10-requests-hover >"$OUT/requests-hover.json"
  E count --testid continue-button --save s10-continue-count >"$OUT/continue-count.json"
  E aria --selector '[data-testid="thread-goal-banner"]' --save s10-banner-aria >/dev/null
  # 4
  vr api GET $API/session/$S/queue --on electron --save s10-queue >/dev/null
  poll_e "$S" --until goal.status=budget_limited --hold 60 --show "$SHOW,goal.updated_at" --interval 2 --timeout 90 --save s10-hold >/dev/null
  vr snapshot --session "$S" --on electron --save s10-after-hold >/dev/null
  # 5
  send_msg "What is 5 + 6? Reply with only the number."
  vr poll $API/session/$S/message --on electron --until "messages.-1.role=assistant" --interval 2 --timeout 120 --save s10-reply-poll >/dev/null
  turn_end 120
  vr api GET $API/session/$S/message --on electron --save s10-history >/dev/null
  goal_e "$S" s10-goal-after-message >/dev/null
  etext thread-goal-banner-status s10-banner-status-after >"$OUT/banner-status-after.txt"
  E screenshot --save s10-final >/dev/null
  vr snapshot --session "$S" --on electron --save s10-final >/dev/null
  m2_down
  ;;
S01)
  m2_begin S01 "$ATTEMPT"
  M2_UP_CONFIG=$(m2_config turns10 10 1) m2_up electron --from-data "$FROM" || exit 1
  E config --save s01-config >"$OUT/config.json"
  m2_close_popups
  S=$(cat "$M2_ROOT/S01/baseline-data/session"); echo "$S" >"$OUT/session"
  # 1
  open_session "s01 legacy" s01
  E wait --testid thread-goal-policy-summary --timeout 30 >/dev/null
  etext thread-goal-policy-summary s01-policy-summary >"$OUT/policy-summary.txt"
  E hover --testid thread-goal-requests-used --save s01-requests-hover >"$OUT/requests-hover.json"
  # 2
  goal_e "$S" s01-goal-before >/dev/null
  vr snapshot --session "$S" --on electron --save s01-before >/dev/null
  # 3
  E click --testid thread-goal-banner-resume --save s01-resume >/dev/null
  poll_e "$S" --until "goal.status=complete|paused|blocked|budget_limited|usage_limited" --show "$SHOW" --interval 3 --timeout 600 --save s01-run >/dev/null
  turn_end 120
  # 4
  goal_e "$S" s01-goal-after >/dev/null
  vr snapshot --session "$S" --on electron --save s01 >/dev/null
  etext thread-goal-policy-summary s01-policy-summary-after >"$OUT/policy-summary-after.txt"
  E hover --testid thread-goal-requests-used --save s01-requests-hover-after >"$OUT/requests-hover-after.json"
  E screenshot --save s01-final >/dev/null
  m2_down
  ;;
S41)
  m2_begin S41 "electron-$ATTEMPT"
  m2_up electron --from-data "$FROM" || exit 1
  m2_close_popups
  S=$(cat "$M2_ROOT/S41/seed/session"); echo "$S" >"$OUT/session"
  open_session "s41 ledger sample" s41
  E wait --testid thread-goal-policy-summary --timeout 30 >/dev/null
  etext thread-goal-policy-summary s41-policy-summary >"$OUT/policy-summary.txt"
  etext thread-goal-tokens-used s41-tokens-text >"$OUT/tokens-text.txt"
  E hover --testid thread-goal-requests-used --save s41-requests-hover >"$OUT/requests-hover.json"
  E hover --testid thread-goal-tokens-used --save s41-tokens-hover >"$OUT/tokens-hover.json"
  goal_e "$S" s41-goal >/dev/null
  E screenshot --save s41-banner >/dev/null
  m2_down
  ;;
*) echo "unknown flow $FLOW" >&2; exit 2 ;;
esac
m2_log "flow $FLOW done"
