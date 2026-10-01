#!/usr/bin/env bash
# RG1b 迁移前后额度恢复一致（按 S17 原文的故障规则重跑）：接口入口的两个流程（verify.md“回归范围”RG1b）。
# 用 S17 的目标；故障规则照 S17 原文“该 Goal 的第 2 次主执行请求起返回 !7181 能识别为可信重置时间的额度错误
# （42212，重置时间为触发时刻 + 3 分钟），到重置时间后转发”，写法见 fault.md“场景写法”S17：
#   fault add --session $S --nth 2- --preset usage-limit-reset --reset-in $RESET_IN
# 会话在建 Goal 前新建、没有别的消息，所以该会话的 main 请求计数就是该 Goal 的请求计数。
# 预设：重置时间 = 第一次命中 + reset-in；之后同一规则的请求都带同一时刻；到点后规则自动不再命中，请求转发真实模型。
# 只看状态、goal.turn_bound 的时点与次数；不点恢复、不看文案。
# 用法（agent-archon worktree 根目录）：
#   bash <tools>/rg1b-api.sh <flow1|flow2> <证据目录>
# 环境变量：RG1B_CONFIG（默认 ~/.minimax/verify-goal-v2/config.yaml，含凭据，只传路径）、RG1B_RESET_IN（默认 180）
set -u
FLOW=$1
OUT=$2
V=.agents/skills/verify-archon/scripts/verify-archon.mjs
AUTHCHECK=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/authcheck.py
CONFIG=${RG1B_CONFIG:-$HOME/.minimax/verify-goal-v2/config.yaml}
RESET_IN=${RG1B_RESET_IN:-180}
API=/minimax-desktop/api/v1
OBJ="Create files e1.txt, e2.txt, e3.txt one at a time, each containing its own number, then stop."
TERMINAL="goal.status=complete|paused|blocked|budget_limited|usage_limited"
SHOW="goal.status,goal.status_reason,goal.execution.wait_reason,goal.turns_used"
[ -f "$V" ] || { echo "rg1b-s17: run from the agent-archon worktree root" >&2; exit 2; }
mkdir -p "$OUT"
OUT=$(cd "$OUT" && pwd)

log() { printf '%s [%s] %s\n' "$(date '+%H:%M:%S')" "$FLOW" "$*" >&2; }
jget() { python3 -c 'import json,sys
try: d=json.load(sys.stdin)
except Exception: print(""); sys.exit(0)
try: v=eval(sys.argv[1])
except Exception: v=""
print("" if v is None else v)' "$1"; }

# vr <参数...>：带 --run，记 steps.jsonl（命令、退出码、截断输出）
vr() {
  local out rc
  out=$(node "$V" "$@" --run "$RID" 2>>"$OUT/steps.stderr.log")
  rc=$?
  printf '%s' "$out" | python3 -c 'import json,sys,time
raw=sys.stdin.read()
try: parsed=json.loads(raw)
except Exception: parsed=raw
text=json.dumps(parsed, ensure_ascii=False)
if len(text)>20000: parsed={"truncated": text[:20000]}
print(json.dumps({"at":int(time.time()*1000),"rc":int(sys.argv[1]),"args":sys.argv[2:],"out":parsed}, ensure_ascii=False))' "$rc" "$@" >>"$OUT/steps.jsonl"
  printf '%s\n' "$out"
  return $rc
}

# 从 fault log 输出里取第一个 resetAtMs
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

# 设了 RG1_UP_LOCK / M2_UP_LOCK（目录路径）时，up 经这把共享启动锁串行，up 后再等 6 秒放锁（与 m2/m3/rg1/rg2 脚本相同；
# 2026-10-01 最终全量自验时补上，原脚本不持锁）
up_lock() { local l=${RG1_UP_LOCK:-${M2_UP_LOCK:-}} w=0; [ -n "$l" ] || return 0
  until mkdir "$l" 2>/dev/null; do sleep 1; w=$((w + 1)); [ "$w" -gt 900 ] && { rmdir "$l" 2>/dev/null; w=0; }; done
  echo "$$ rg1b-$FLOW $(date +%s)" >"$l/owner"; }
up_unlock() { local l=${RG1_UP_LOCK:-${M2_UP_LOCK:-}}; [ -n "$l" ] || return 0; sleep "${RG1_UP_GAP:-6}"; rm -f "$l/owner"; rmdir "$l" 2>/dev/null; return 0; }

up_lock
up_out=$(node "$V" up --config "$CONFIG" --fault --evidence-dir "$OUT" 2>>"$OUT/steps.stderr.log")
up_unlock
printf '%s\n' "$up_out" >"$OUT/up.json"
RID=$(printf '%s' "$up_out" | jget "d['runId'] if d.get('ok') else ''")
[ -n "$RID" ] || { log "up failed: $(printf '%s' "$up_out" | head -c 400)"; exit 1; }
echo "$RID" >"$OUT/runId"
git rev-parse HEAD >"$OUT/git-head"
git status --short >"$OUT/git-status"
log "up runId=$RID head=$(git rev-parse --short HEAD) fault=$(printf '%s' "$up_out" | jget "d.get('fault',{}).get('llmHost')")"
vr doctor >"$OUT/doctor.json"

# 冒烟（fault.md“就绪后先照常冒烟一次”）：单独的会话，不影响目标会话的请求计数
S0=$(vr api POST $API/agent/mavis/session --data '{"title":"rg1b-s17 smoke"}' --save rg1b-smoke-session | jget "d['body']['session_id']")
vr api POST $API/session/$S0/message --data '{"content":"Reply with exactly the word PONG and nothing else."}' --save rg1b-smoke-send >/dev/null
vr api GET $API/session/$S0/message --save rg1b-smoke-history >/dev/null
vr fault log --session "$S0" --role main --event attempt --save fault >/dev/null

# 目标会话与规则
S=$(vr api POST $API/agent/mavis/session --data "{\"title\":\"rg1b-s17 $FLOW\"}" --save rg1b-$FLOW-session | jget "d['body']['session_id']")
echo "$S" >"$OUT/session"
vr fault add --session "$S" --nth 2- --preset usage-limit-reset --reset-in "$RESET_IN" --note "RG1b-S17 $FLOW: from the 2nd main request of the goal session until the reset time" --save fault >/dev/null
vr api POST $API/session/$S/goal --data "$(python3 -c 'import json,sys; print(json.dumps({"objective":sys.argv[1]}))' "$OBJ")" --save rg1b-$FLOW-create >/dev/null
vr poll $API/session/$S/goal --until "$TERMINAL" --show "$SHOW" --interval 2 --timeout 180 --save rg1b-$FLOW-limited >/dev/null
vr api GET $API/session/$S/goal --save rg1b-$FLOW-goal-limited >"$OUT/goal-limited.json"
RESET_AT=$(vr fault log --session "$S" --event attempt-end --save fault | reset_at)
echo "$RESET_AT" >"$OUT/reset-at-ms"
GOAL_ID=$(jget "d['body']['goal']['goal_id']" <"$OUT/goal-limited.json")
echo "$GOAL_ID" >"$OUT/goal-id"
log "session=$S goal=$GOAL_ID status=$(jget "d['body']['goal']['status_reason']" <"$OUT/goal-limited.json") resetAtMs=$RESET_AT"
vr snapshot --session "$S" --save rg1b-$FLOW-limited-snap >/dev/null
[ "${RESET_AT:-0}" -gt 0 ] || { log "no resetAtMs in fault log"; }

now_ms() { python3 -c 'import time; print(int(time.time()*1000))'; }

if [ "$FLOW" = flow1 ]; then
  # 重置时间之前保持 usage_limited（到重置前 3 秒），之后等它离开 usage_limited，再等终态
  hold=$(( (RESET_AT - $(now_ms)) / 1000 - 3 ))
  [ "$hold" -gt 0 ] || hold=1
  vr poll $API/session/$S/goal --until goal.status=usage_limited --hold "$hold" --interval 2 --show "$SHOW" --save rg1b-$FLOW-hold-before-reset >/dev/null
  vr poll $API/session/$S/goal --until 'goal.status=active|complete|paused|blocked|budget_limited' --interval 1 --timeout 150 --show "$SHOW" --save rg1b-$FLOW-left-limited >/dev/null
  vr poll $API/session/$S/goal --until "$TERMINAL" --show "$SHOW" --interval 3 --timeout 600 --save rg1b-$FLOW-run >/dev/null
  vr api GET $API/session/$S/goal --save rg1b-$FLOW-goal-final >/dev/null
else
  # 重置时间之前清除，poll 到重置时间之后 90 秒：GET 一直为 {}
  vr api DELETE $API/session/$S/goal --save rg1b-$FLOW-delete >/dev/null
  vr api GET $API/session/$S/goal --save rg1b-$FLOW-get-after-delete >/dev/null
  log "deleted at $(now_ms), reset at $RESET_AT"
  hold=$(( (RESET_AT + 90000 - $(now_ms)) / 1000 ))
  [ "$hold" -gt 0 ] || hold=1
  vr poll $API/session/$S/goal --until goal.goal_id=undefined --hold "$hold" --interval 3 --show goal.goal_id,goal.status --save rg1b-$FLOW-hold-after-reset >/dev/null
  vr api GET $API/session/$S/goal --save rg1b-$FLOW-goal-final >/dev/null
fi
vr fault log --session "$S" --save fault >/dev/null
vr fault list --save fault >/dev/null
vr snapshot --session "$S" --save rg1b-$FLOW-final-snap >/dev/null
vr down >"$OUT/down.json"
log "down ok=$(jget "d.get('ok')" <"$OUT/down.json")"

# 登录失效核对（同 rg1_down）
home=${VERIFY_ARCHON_HOME:-$(node -e "console.log(require('os').tmpdir())")/verify-archon}
# verify-archon 的 down 已写 authCheck（含 http429、刷新次数）时用它；旧版没写时沿用原来的统计（authcheck.py）
log "auth-check $(python3 "$AUTHCHECK" "$home/$RID/server.log" "$OUT/auth-check.json" "$OUT" "$RID" --down "$OUT/down.json" --no-electron)"
