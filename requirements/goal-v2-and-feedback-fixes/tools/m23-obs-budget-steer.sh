#!/usr/bin/env bash
# 观察（不是 verify 检查点）：0af5e8a219 的“工作请求用尽后普通消息不并入 Goal Turn”。
# TUI，配置 defaultMainTurns=3、graceSteps=1（同 S09/S10），故障注入只暂扣第 3 次主执行请求的结尾（hold），
# 在它在途时用 Enter 发一条普通消息（TUI 运行中 Enter 为 steer），再放行。
# 期望：Goal 以 budget_limited(main_turn) 结束（不是 paused(infra_retryable)）；普通消息在 Goal Turn 关闭后
# 自己的一轮里回答，不在 Goal Turn 里。
# 用法（agent-archon worktree 根目录）：bash <tools>/m23-obs-budget-steer.sh <尝试名>
# 证据：<M2_ROOT>/OBS-budget-steer/<尝试名>/
set -u
source "$(dirname "${BASH_SOURCE[0]}")/m3-lib.sh"
ATTEMPT=$1
T() { vr tui "$@"; }
m2_begin OBS-budget-steer "$ATTEMPT"
M2_UP_CONFIG=$(m2_config turns3 3 1) m3_up tui --fault || exit 1
RULE=$(vr fault add --on tui --session next --nth 3 --action hold --note "OBS: hold the tail of the Goal's 3rd main request" --save fault-rule | jget "(d.get('rule') or {}).get('id') or d.get('id') or d.get('ruleId')")
echo "$RULE" >"$OUT/rule-id"
# 1 S09 的目标
T type "/goal Create files d1.txt, d2.txt, d3.txt, d4.txt, d5.txt one at a time, each containing its own number. In each response make at most one tool call. Keep working in this turn until all five exist." >/dev/null
# 2 等第 3 次主执行请求被暂扣（在途）
deadline=$(( $(date +%s) + 300 )); held=""
while [ "$(date +%s)" -lt "$deadline" ]; do
  held=$(vr fault pending --on tui | python3 -c 'import json,sys
d=json.load(sys.stdin); p=d.get("pending") or []
print(next((str(x["id"]) for x in p if x.get("kind")=="hold"),""))')
  [ -n "$held" ] && break
  sleep 1
done
echo "$held" >"$OUT/held-pending-id"
vr fault pending --on tui --save fault-pending >/dev/null
T screen --all --save obs-held-screen >/dev/null
S=$(tui_status | jget "d.get('session') or ''"); echo "$S" >"$OUT/session"
m2_log "held=$held session=$S"
# 3 第 3 次请求在途时发普通消息
echo "{\"at\":$(now_ms),\"cmd\":\"ordinary message\",\"heldPendingId\":\"$held\"}" >>"$OUT/commands.jsonl"
T type "What is 5 + 6? Reply with only the number." >/dev/null
sleep 2
T screen --all --save obs-after-send-screen >/dev/null
# 4 放行
echo "{\"at\":$(now_ms),\"cmd\":\"fault release\"}" >>"$OUT/commands.jsonl"
vr fault release --on tui --save fault-release >/dev/null
T wait --text "Budget limited" --timeout 300 --save obs-budget >/dev/null
# 等普通消息那一轮结束：空闲，且屏幕上该消息之后出现只有 11 的一行（最多 300 秒），再多等 5 秒确认没有新一轮
deadline=$(( $(date +%s) + 300 ))
while [ "$(date +%s)" -lt "$deadline" ]; do
  if node "$V" tui screen --all --run "$RID" 2>/dev/null | python3 -c 'import json,sys
d=json.load(sys.stdin); sc=d.get("screen") or d; L=sc.get("lines") or []; st=sc.get("status") or {}
idx=[i for i,l in enumerate(L) if "What is 5 + 6" in l]
ok=bool(idx) and any(l.strip().lstrip("●").strip()=="11" for l in L[idx[-1]+1:]) and st.get("state") not in ("run","perm","ask","plan")
sys.exit(0 if ok else 1)'; then break; fi
  sleep 2
done
sleep 5
T wait --status "state=ready|done|fail|cancel|error" --timeout 120 --save obs-idle >/dev/null
T screen --all --save obs-final-screen >/dev/null
T snapshot --save obs >/dev/null
vr fault log --on tui --tail 500 --save fault-obs >/dev/null
T screen --all --save final-screen >/dev/null
m2_down
m2_log "done"
