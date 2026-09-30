#!/usr/bin/env bash
# RG1 接口入口：功能地图索引“接口”列的全部子功能，命令照抄各地图“接口”一节。
# 每个流程起自己的接口实例（up --config $RG1_CONFIG），跑完 snapshot、down、整理证据。
# 用法（agent-archon worktree 根目录）：
#   RG1_ROOT=<证据根> RG1_TAG=<前缀> [RG1_FLOWS="lifecycle continuation-bg ..."] bash <tools>/rg1-api.sh
# 流程：lifecycle（含 completion 接口一节）continuation-bg continuation-queue limits attachments
#       questionnaire-manual questionnaire-auto
set -u
source "$(dirname "${BASH_SOURCE[0]}")/rg1-lib.sh"
API=/minimax-desktop/api/v1

new_session() { # new_session <title> <save>
  vr api POST $API/agent/mavis/session --data "{\"title\":\"$1\"}" --save "$2" | jget "d['body']['session_id']"
}
objective_json() { # objective_json <objective> <budget>
  python3 -c 'import json,sys; print(json.dumps({"objective":sys.argv[1],"token_budget":int(sys.argv[2])}))' "$1" "$2"
}

flow_lifecycle() {
  rg1_up runtime api-lifecycle || return 1
  local S
  S=$(new_session "goal lifecycle" "$T-lifecycle.create--session")
  echo "$S" >"$RUNDIR/session"
  # 创建
  vr api POST $API/session/$S/goal --data "$(objective_json "$OBJ_COUNT3" 80000)" --save "$T-lifecycle.create--create" >/dev/null
  vr snapshot --session "$S" --save "$T-lifecycle.create--snap" >/dev/null
  # 暂停
  vr api PATCH $API/session/$S/goal --data '{"status":"paused"}' --save "$T-lifecycle.pause--pause" >/dev/null
  vr snapshot --session "$S" --save "$T-lifecycle.pause--snap" >/dev/null
  # 暂停时修改目标
  vr api PATCH $API/session/$S/goal --data "{\"objective\":\"$OBJ_COUNT4\"}" --save "$T-lifecycle.edit-paused--edit" >/dev/null
  vr snapshot --session "$S" --save "$T-lifecycle.edit-paused--snap" >/dev/null
  # 确认暂停期间不会自行继续
  vr poll $API/session/$S/goal --until goal.status=paused --hold 8 --show goal.status,goal.turns_used --save "$T-lifecycle.still-paused--hold" >/dev/null
  vr snapshot --session "$S" --save "$T-lifecycle.still-paused--snap" >/dev/null
  # 恢复
  vr api PATCH $API/session/$S/goal --data '{"status":"active"}' --save "$T-lifecycle.resume--resume" >/dev/null
  vr snapshot --session "$S" --save "$T-lifecycle.resume--snap" >/dev/null
  # 跑到终态
  vr poll $API/session/$S/goal --until "$GOAL_TERMINAL" --show "$SHOW_RUN" --interval 4 --timeout 420 --save "$T-lifecycle.complete--run" >/dev/null
  vr snapshot --session "$S" --save "$T-lifecycle.complete--snap" >/dev/null
  # completion.md 接口：验证通过后完成、核对验证过程（snapshot --save completion）、最终回复的运行顺序
  vr api GET $API/session/$S/goal --save "$T-completion.complete--goal" >/dev/null
  vr snapshot --session "$S" --save "$T-completion.complete--snap" >/dev/null
  vr api GET $API/session/$S/message --save "$T-completion.final-reply--history" >/dev/null
  vr snapshot --session "$S" --save "$T-completion.final-reply--snap" >/dev/null
  # 完成后不续跑
  vr api POST $API/session/$S/message --data '{"content":"Reply with just OK."}' --timeout 180 --save "$T-completion.no-continuation--plain" >/dev/null
  vr poll $API/session/$S/goal --until goal.status=complete --hold 10 --show goal.status,goal.turns_used --save "$T-completion.no-continuation--hold" >/dev/null
  vr api GET $API/session/$S/queue --save "$T-completion.no-continuation--queue" >/dev/null
  vr snapshot --session "$S" --save "$T-completion.no-continuation--snap" >/dev/null
  # 完成后设定新 Goal（completion 替换；lifecycle 替换已完成的 Goal）
  vr api POST $API/session/$S/goal --data "$(objective_json "$OBJ_DONE" 40000)" --save "$T-completion.replace--create" >/dev/null
  vr snapshot --session "$S" --save "$T-completion.replace--snap" >/dev/null
  vr api GET $API/session/$S/goal --save "$T-lifecycle.replace--get" >/dev/null
  vr snapshot --session "$S" --save "$T-lifecycle.replace--snap" >/dev/null
  # 清除（确认后 DELETE）
  vr api DELETE $API/session/$S/goal --save "$T-lifecycle.clear--delete" >/dev/null
  vr api GET $API/session/$S/goal --save "$T-lifecycle.clear--get" >/dev/null
  vr snapshot --session "$S" --save "$T-lifecycle.clear--snap" >/dev/null
  rg1_down runtime api
}

flow_continuation_bg() {
  rg1_up runtime continuation-bg || return 1
  local S
  S=$(new_session "goal continuation" "$T-continuation.background--session")
  echo "$S" >"$RUNDIR/session"
  vr api POST $API/session/$S/goal --data "$(objective_json "$OBJ_BG" 120000)" --save "$T-continuation.background--create" >/dev/null
  vr poll $API/session/$S/goal --until goal.execution.wait_reason=required_background --show goal.status,goal.execution.wait_reason,goal.turns_used --interval 2 --timeout 120 --save "$T-continuation.background--waiting" >/dev/null
  vr poll $API/session/$S/goal --until "$GOAL_TERMINAL" --show "$SHOW_RUN" --interval 3 --timeout 600 --save "$T-continuation.background--run" >/dev/null
  vr snapshot --session "$S" --save "$T-continuation.background--snap" >/dev/null
  rg1_down runtime api
}

flow_continuation_queue() {
  rg1_up runtime continuation-queue || return 1
  local S
  S=$(new_session "goal continuation hol" "$T-continuation.queue-while-waiting--session")
  echo "$S" >"$RUNDIR/session"
  vr api POST $API/session/$S/goal --data "$(objective_json "$OBJ_LATE" 120000)" --save "$T-continuation.queue-while-waiting--create" >/dev/null
  vr poll $API/session/$S/goal --until goal.execution.wait_reason=required_background --show goal.status,goal.execution.wait_reason,goal.turns_used --interval 2 --timeout 120 --save "$T-continuation.queue-while-waiting--waiting" >/dev/null
  vr api POST $API/session/$S/queue --data '{"content":"Quick side question while the goal waits: what is 17 + 25? Answer with just the number.","client_request_id":"verify-hol-1"}' --save "$T-continuation.queue-while-waiting--queue" >/dev/null
  vr poll $API/session/$S/message --until 'messages.-1.msg_content~42' --show messages.-1.role,messages.-1.msg_content --interval 2 --timeout 120 --save "$T-continuation.queue-while-waiting--history" >/dev/null
  vr api GET $API/session/$S/goal --save "$T-continuation.queue-while-waiting--goal-still-waiting" >/dev/null
  vr poll $API/session/$S/goal --until "$GOAL_TERMINAL" --show "$SHOW_RUN" --interval 3 --timeout 600 --save "$T-continuation.queue-while-waiting--run" >/dev/null
  vr snapshot --session "$S" --save "$T-continuation.queue-while-waiting--snap" >/dev/null
  rg1_down runtime api
}

flow_limits() {
  rg1_up runtime limits || return 1
  local S
  S=$(new_session "goal limits" "$T-limits.token-budget--session")
  echo "$S" >"$RUNDIR/session"
  # 达到 token 预算
  vr api POST $API/session/$S/goal --data "$(objective_json "$OBJ_NOTES" 3000)" --save "$T-limits.token-budget--create" >/dev/null
  vr poll $API/session/$S/goal --until "$GOAL_TERMINAL" --show goal.status,goal.status_reason,goal.turns_used,goal.tokens_used --interval 3 --timeout 300 --save "$T-limits.token-budget--run" >/dev/null
  vr snapshot --session "$S" --save "$T-limits.token-budget--snap" >/dev/null
  # 普通恢复被拒绝（预期 409 GOAL_BUDGET_LIMITED）
  vr api PATCH $API/session/$S/goal --data '{"status":"active"}' --save "$T-limits.resume-rejected--resume" >/dev/null
  vr snapshot --session "$S" --save "$T-limits.resume-rejected--snap" >/dev/null
  # 只改预算不会恢复；提高预算并恢复；确认后 DELETE
  vr api PATCH $API/session/$S/goal --data '{"token_budget":200000}' --save "$T-limits.raise-reopen--raise" >/dev/null
  vr api PATCH $API/session/$S/goal --data '{"token_budget":250000,"status":"active"}' --save "$T-limits.raise-reopen--reopen" >/dev/null
  vr api DELETE $API/session/$S/goal --save "$T-limits.raise-reopen--delete" >/dev/null
  vr snapshot --session "$S" --save "$T-limits.raise-reopen--snap" >/dev/null
  # 耗时：约 12 秒后每隔 4 秒 GET 两次；暂停后 10 秒再 GET（用 poll --hold 代替固定 sleep）
  vr api POST $API/session/$S/goal --data "$(objective_json "$OBJ_TIMER" 80000)" --save "$T-limits.timer--create" >/dev/null
  vr poll $API/session/$S/goal --until goal.status=active --hold 12 --interval 4 --show goal.status,goal.time_used_seconds --save "$T-limits.timer--wait12" >/dev/null
  vr api GET $API/session/$S/goal --save "$T-limits.timer--get1" >/dev/null
  vr poll $API/session/$S/goal --until goal.status=active --hold 4 --interval 2 --show goal.status,goal.time_used_seconds --save "$T-limits.timer--wait4" >/dev/null
  vr api GET $API/session/$S/goal --save "$T-limits.timer--get2" >/dev/null
  vr api PATCH $API/session/$S/goal --data '{"status":"paused"}' --save "$T-limits.timer--pause" >/dev/null
  vr poll $API/session/$S/goal --until goal.status=paused --hold 10 --interval 2 --show goal.status,goal.time_used_seconds --save "$T-limits.timer--paused-hold" >/dev/null
  vr api GET $API/session/$S/goal --save "$T-limits.timer--get3" >/dev/null
  vr api DELETE $API/session/$S/goal --save "$T-limits.timer--delete" >/dev/null
  vr snapshot --session "$S" --save "$T-limits.timer--snap" >/dev/null
  rg1_down runtime api
}

flow_attachments() {
  rg1_up runtime attachments || return 1
  local S
  S=$(new_session "goal attachments" "$T-attachments.kickoff--session")
  echo "$S" >"$RUNDIR/session"
  python3 - "$RG1_ROOT/_inputs/goal-brief.txt" "$OBJ_SECRET" >"$RUNDIR/goal-attach.json" <<'EOF'
import json, os, sys
path, objective = sys.argv[1], sys.argv[2]
print(json.dumps({"objective": objective, "token_budget": 80000, "attachments": [{"meta": {"attachment_type": "file", "file_name": "goal-brief.txt", "mime_type": "text/plain", "size_bytes": os.path.getsize(path)}, "local": {"file_path": path}}]}))
EOF
  vr api POST $API/session/$S/goal --data "@$RUNDIR/goal-attach.json" --save "$T-attachments.kickoff--create" >/dev/null
  vr poll $API/session/$S/goal --until "$GOAL_TERMINAL" --show "$SHOW_RUN" --interval 3 --timeout 420 --save "$T-attachments.kickoff--run" >/dev/null
  vr snapshot --session "$S" --save "$T-attachments.kickoff--snap" >/dev/null
  rg1_down runtime api
}

questionnaire_ask() { # questionnaire_ask <sub>；输出会话 ID
  local sub=$1 S
  S=$(new_session "goal questionnaire $sub" "$T-questionnaire.$sub--session")
  echo "$S" >"$RUNDIR/session"
  vr api POST $API/session/$S/goal --data "$(objective_json "$OBJ_FRUIT" 100000)" --save "$T-questionnaire.$sub--create" >/dev/null
  vr poll "$API/agent/mavis/questionnaire/pending?session_id=$S" --until request.status=0 --show request.id,request.expires_at --interval 2 --timeout 180 --save "$T-questionnaire.$sub--pending" >"$RUNDIR/pending-$sub.json"
  echo "$S"
}

flow_questionnaire_manual() {
  rg1_up runtime questionnaire-manual || return 1
  local S rid body
  S=$(questionnaire_ask manual)
  rid=$(jget "d['final']['request']['id']" <"$RUNDIR/pending-manual.json")
  body=$(python3 - "$RUNDIR/pending-manual.json" <<'EOF'
import json, sys
req = json.load(open(sys.argv[1]))['final']['request']
step = req['steps'][0]
banana = next(o for o in step['options'] if 'banana' in json.dumps(o, ensure_ascii=False).lower())
print(json.dumps({"schema_version": 2, "answers": [{"step_id": step['id'], "selected_option_ids": [banana['id']], "selected_other": False}]}))
EOF
)
  vr api POST "$API/agent/mavis/questionnaire/$rid/reply" --data "$body" --save "$T-questionnaire.manual--reply" >/dev/null
  vr poll $API/session/$S/goal --until "$GOAL_TERMINAL" --show "$SHOW_RUN" --interval 4 --timeout 420 --save "$T-questionnaire.manual--run" >/dev/null
  vr snapshot --session "$S" --save "$T-questionnaire.manual--snap" >/dev/null
  rg1_down runtime api
}

flow_questionnaire_auto() {
  rg1_up runtime questionnaire-auto || return 1
  local S
  S=$(questionnaire_ask auto-timeout)
  vr poll $API/session/$S/goal --until "$GOAL_TERMINAL" --show "$SHOW_RUN" --interval 10 --timeout 720 --save "$T-questionnaire.auto-timeout--run" >/dev/null
  vr snapshot --session "$S" --save "$T-questionnaire.auto-timeout--snap" >/dev/null
  rg1_down runtime api
}

rg1_inputs
for f in lifecycle continuation-bg continuation-queue limits attachments questionnaire-manual questionnaire-auto; do
  rg1_wants "$f" || continue
  "flow_${f//-/_}"
  rg1_log "flow done"
done
