#!/usr/bin/env bash
# 观察补充（不是 verify 检查点）：与 m23-obs-budget-steer.sh 相同，但走接口入口，普通消息以 Desktop 输入框 steer 的
# client_intent=composer-steer 发送（runtime 记为 producerId composer-steer，属于用户 steering）。用来区分
# TUI 的 steer（producerId mcode）与 Desktop 的 steer 在“工作请求用尽后不并入 Goal Turn”上的差别。
# 用法（agent-archon worktree 根目录）：bash <tools>/m23-obs-budget-steer-api.sh <尝试名>
# 证据：<M2_ROOT>/OBS-budget-steer-api/<尝试名>/
set -u
source "$(dirname "${BASH_SOURCE[0]}")/m3-lib.sh"
ATTEMPT=$1
m2_begin OBS-budget-steer-api "$ATTEMPT"
M2_UP_CONFIG=$(m2_config turns3 3 1) m3_up runtime --fault || exit 1
vr api GET /mavis/api/config --save obs-effective-config >/dev/null
S=$(m2_session "obs budget steer" obs-session); echo "$S" >"$OUT/session"
vr fault add --session "$S" --nth 3 --action hold --note "OBS-api: hold the tail of the Goal's 3rd main request" --save fault-rule >/dev/null
m2_goal_create "$S" "Create files d1.txt, d2.txt, d3.txt, d4.txt, d5.txt one at a time, each containing its own number. In each response make at most one tool call. Keep working in this turn until all five exist." obs-create >/dev/null
deadline=$(( $(date +%s) + 300 )); held=""
while [ "$(date +%s)" -lt "$deadline" ]; do
  held=$(vr fault pending | python3 -c 'import json,sys
d=json.load(sys.stdin); p=d.get("pending") or []
print(next((str(x["id"]) for x in p if x.get("kind")=="hold"),""))')
  [ -n "$held" ] && break
  sleep 1
done
echo "$held" >"$OUT/held-pending-id"
vr fault pending --save fault-pending >/dev/null
vr api GET $API/session/$S/goal --save obs-goal-held >/dev/null
echo "{\"at\":$(now_ms),\"cmd\":\"ordinary message\",\"heldPendingId\":\"$held\"}" >>"$OUT/commands.jsonl"
vr api POST $API/session/$S/message --data '{"content":"What is 5 + 6? Reply with only the number.","client_intent":"composer-steer"}' --save obs-send >/dev/null
sleep 2
echo "{\"at\":$(now_ms),\"cmd\":\"fault release\"}" >>"$OUT/commands.jsonl"
vr fault release --save fault-release >/dev/null
vr poll $API/session/$S/goal --until "$TERMINAL" --show "$SHOW" --interval 1 --timeout 300 --save obs-run >/dev/null
wait_reply "$S" "What is 5 + 6" 240 obs-history
vr poll $API/session/$S --until session.status.status_type=0 --hold 5 --show session.status.status_type --interval 1 --timeout 180 --save obs-idle >/dev/null
vr api GET $API/session/$S/goal --save obs-goal-final >/dev/null
vr snapshot --session "$S" --save obs >/dev/null
vr fault log --session "$S" --tail 500 --save fault-obs >/dev/null
m2_down
m2_log "done"
