#!/usr/bin/env bash
# M3 接口场景：verify.md S21b（--fault，六种错误各一个会话）、S34（提高或清除预算重开 budget_limited(token)）；
# 以及 S35/S36 前提核对 Q（只读 quota show，不发任何设置请求）。
# 用法（agent-archon worktree 根目录）：bash <tools>/m3-api.sh <S21b|S34|Q> <尝试名>
set -u
source "$(dirname "${BASH_SOURCE[0]}")/m3-lib.sh"
SCN=$1
ATTEMPT=$2
OBJ17="Create files e1.txt, e2.txt, e3.txt one at a time, each containing its own number, then stop."
LIMITS_OBJ="Write a file notes.md with ten numbered one-line facts about the Rust programming language, then verify the file has exactly ten lines."

case $SCN in
Q)
  m2_begin S35 "$ATTEMPT"
  # 只读：quota show（先查询；账号不在测试台时报错退出）。不调用 set/restore。
  node "$V" quota show --evidence-dir "$OUT" --save quota-show >"$OUT/quota-show.out.json" 2>"$OUT/quota-show.stderr.log"
  echo "rc=$?" >"$OUT/quota-show.rc"
  m2_log "quota show rc=$(cat "$OUT/quota-show.rc"): $(head -c 400 "$OUT/quota-show.out.json")"
  ;;
S21b)
  m2_begin S21b "$ATTEMPT"
  m3_up runtime --fault || exit 1
  m2_smoke_api
  vr fault log --role main --event attempt --tail 5 --save fault-smoke >/dev/null
  PRESETS="rate-limit-429 rate-limit-50111 tpm-50150 unrecognized upstream-50113 retryable-500"
  : >"$OUT/sessions.txt"
  i=0
  for p in $PRESETS; do
    i=$((i + 1))
    S=$(m2_session "s21b $i $p" "s21b-$i-session")
    echo "$i $p $S" >>"$OUT/sessions.txt"
    vr fault add --session "$S" --nth 2- --preset "$p" --for 300 --note "S21b ($i) $p from the 2nd main request for 300s" --save "fault-rule-$i" >/dev/null
    m2_goal_create "$S" "$OBJ17" "s21b-$i-create" >/dev/null
  done
  # 各会话 poll 到离开 active，读 Goal，hold 180 秒（并行）
  while read -r i p S; do
    (
      vr poll $API/session/$S/goal --until "goal.status=complete|paused|blocked|budget_limited|usage_limited" --show "$SHOW,goal.usage_recovery_scheduled" --interval 2 --timeout 600 --save "s21b-$i-left-active" >/dev/null
      vr api GET $API/session/$S/goal --save "s21b-$i-goal" >/dev/null
      echo "$(now_ms)" >"$OUT/s21b-$i-hold-start-ms"
      st=$(goal_raw "$S" | jget "d.get('status','')")
      vr poll $API/session/$S/goal --until "goal.status=$st" --hold 180 --show "$SHOW,goal.usage_recovery_scheduled" --interval 3 --timeout 240 --save "s21b-$i-hold" >/dev/null
      echo "$(now_ms)" >"$OUT/s21b-$i-hold-end-ms"
      vr api GET $API/session/$S/goal --save "s21b-$i-goal-after-hold" >/dev/null
    ) &
  done <"$OUT/sessions.txt"
  wait
  while read -r i p S; do
    vr snapshot --session "$S" --save "s21b-$i" >/dev/null
    vr fault log --session "$S" --tail 500 --save "fault-s21b-$i" >/dev/null
  done <"$OUT/sessions.txt"
  vr fault list --save fault-list >/dev/null
  m2_down
  ;;
S34)
  m2_begin S34 "$ATTEMPT"
  m3_up runtime || exit 1
  run_one() { # run_one <A|B> <新 token_budget>
    local tag=$1 budget=$2 s
    s=$(m2_session "s34 $tag" "s34-$tag-session"); echo "$s" >"$OUT/session-$tag"
    # 1 limits.md“接口”一节
    vr api POST $API/session/$s/goal --data "{\"objective\":\"$LIMITS_OBJ\",\"token_budget\":3000}" --save "s34-$tag-create" >/dev/null
    vr poll $API/session/$s/goal --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 300 --save "s34-$tag-limited" >/dev/null
    vr poll $API/session/$s --until session.status.status_type=0 --hold 5 --show session.status.status_type --interval 1 --timeout 180 --save "s34-$tag-turn-ended" >/dev/null
    vr api GET $API/session/$s/goal --save "s34-$tag-goal-limited" >/dev/null
    # 2 / 3
    echo "$(now_ms)" >"$OUT/s34-$tag-patch-at-ms"
    vr api PATCH $API/session/$s/goal --data "{\"token_budget\":$budget,\"status\":\"active\"}" --save "s34-$tag-patch" >"$OUT/s34-$tag-patch.json"
    vr poll $API/session/$s/goal --until "goal.status=active" --hold 0 --show "$SHOW,goal.token_budget" --interval 1 --timeout 10 --save "s34-$tag-after-patch" >/dev/null
    vr poll $API/session/$s/goal --until "$TERMINAL" --show "$SHOW,goal.token_budget" --interval 2 --timeout 600 --save "s34-$tag-run" >/dev/null
    vr api GET $API/session/$s/goal --save "s34-$tag-final" >/dev/null
    vr snapshot --session "$s" --save "s34-$tag" >/dev/null
  }
  run_one A 250000 &
  sleep 20
  run_one B 0 &
  wait
  m2_down
  ;;
*) echo "unknown scenario $SCN" >&2; exit 2 ;;
esac
m2_log "scenario $SCN done"
