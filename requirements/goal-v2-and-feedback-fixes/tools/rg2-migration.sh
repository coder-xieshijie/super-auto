#!/usr/bin/env bash
# RG2：第 2 项 verify（origin/fix/goal-final-result-delivery 的 .harness/docs/specs/goal-final-result-delivery/verify.md）
# 的 S02（TUI）与 S03（接口），命令照抄原文步骤；另加的只有：S02 在第 2 步之后等本轮结束（状态栏 state 不是 run），
# 用来留下“该轮结束时状态栏”的证据；两个场景结束时 down。
# 用法（agent-archon worktree 根目录）：bash <tools>/rg2-migration.sh <S02|S03> <证据目录>
# 环境变量：RG2_CONFIG（默认 ~/.minimax/verify-goal-v2/config.yaml，含凭据，只传路径）
set -u
SC=$1
OUT=$2
V=.agents/skills/verify-archon/scripts/verify-archon.mjs
AUTHCHECK=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/authcheck.py
CONFIG=${RG2_CONFIG:-$HOME/.minimax/verify-goal-v2/config.yaml}
API=/minimax-desktop/api/v1
OBJ="Create a file named hello.html in the workspace. It should be a small web page whose main heading reads Hello Goal."
[ -f "$V" ] || { echo "rg2: run from the agent-archon worktree root" >&2; exit 2; }
mkdir -p "$OUT"
OUT=$(cd "$OUT" && pwd)

log() { printf '%s [%s] %s\n' "$(date '+%H:%M:%S')" "$SC" "$*" >&2; }
jget() { python3 -c 'import json,sys
try: d=json.load(sys.stdin)
except Exception: print(""); sys.exit(0)
try: v=eval(sys.argv[1])
except Exception: v=""
print("" if v is None else v)' "$1"; }
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

# 设了 RG1_UP_LOCK / M2_UP_LOCK（目录路径）时，up 经这把共享启动锁串行，up 后再等 6 秒放锁（与 m2/m3/rg1 脚本相同）
up_lock() { local l=${RG1_UP_LOCK:-${M2_UP_LOCK:-}} w=0; [ -n "$l" ] || return 0
  until mkdir "$l" 2>/dev/null; do sleep 1; w=$((w + 1)); [ "$w" -gt 900 ] && { rmdir "$l" 2>/dev/null; w=0; }; done
  echo "$$ ${UP_LOCK_TAG:-tool} $(date +%s)" >"$l/owner"; }
up_unlock() { local l=${RG1_UP_LOCK:-${M2_UP_LOCK:-}}; [ -n "$l" ] || return 0; sleep "${RG1_UP_GAP:-6}"; rm -f "$l/owner"; rmdir "$l" 2>/dev/null; return 0; }

git rev-parse HEAD >"$OUT/git-head"
git status --short >"$OUT/git-status"

if [ "$SC" = S02 ]; then
  up_lock
  up_out=$(node "$V" tui up --config "$CONFIG" --evidence-dir "$OUT" --no-proxy 2>>"$OUT/steps.stderr.log")
  up_unlock
  printf '%s\n' "$up_out" >"$OUT/up.json"
  RID=$(printf '%s' "$up_out" | jget "d['runId'] if d.get('ok') else ''")
  [ -n "$RID" ] || { log "tui up failed: $(printf '%s' "$up_out" | head -c 400)"; exit 1; }
  echo "$RID" >"$OUT/runId"
  log "tui up runId=$RID state=$(printf '%s' "$up_out" | jget "d.get('status',{}).get('state')") head=$(git rev-parse --short HEAD)"
  # 1
  vr tui type "/goal $OBJ" >/dev/null
  # 2
  vr tui wait --text "Goal complete" --timeout 420 --save tui-s02 >/dev/null
  # 附加：等本轮结束，记录状态栏
  vr tui wait --status "state=ready|done|fail|cancel|error" --hold 3 --timeout 180 --save tui-s02-idle >/dev/null
  # 3
  vr tui screen --all --save tui-s02-screen >/dev/null
  vr tui snapshot --save s02 >/dev/null
  vr tui down >"$OUT/down.json"
else
  up_lock
  up_out=$(node "$V" up --config "$CONFIG" --evidence-dir "$OUT" 2>>"$OUT/steps.stderr.log")
  up_unlock
  printf '%s\n' "$up_out" >"$OUT/up.json"
  RID=$(printf '%s' "$up_out" | jget "d['runId'] if d.get('ok') else ''")
  [ -n "$RID" ] || { log "up failed: $(printf '%s' "$up_out" | head -c 400)"; exit 1; }
  echo "$RID" >"$OUT/runId"
  log "up runId=$RID head=$(git rev-parse --short HEAD)"
  vr doctor >"$OUT/doctor.json"
  S=$(vr api POST $API/agent/mavis/session --data '{"title":"rg2 s03"}' --save s03-session | jget "d['body']['session_id']")
  echo "$S" >"$OUT/session"
  # 1
  vr api POST $API/session/$S/goal --data "$(python3 -c 'import json,sys; print(json.dumps({"objective":sys.argv[1]}))' "$OBJ")" --save s03-create >/dev/null
  # 2
  vr poll $API/session/$S/goal --until 'goal.status=complete|paused|blocked|budget_limited|usage_limited' --show goal.status,goal.status_reason --interval 4 --timeout 420 --save s03-run >/dev/null
  # 3
  vr snapshot --session "$S" --save s03 >/dev/null
  # 4
  vr api POST $API/session/$S/message --data '{"content":"Create a file named after.txt in the workspace containing the word ok."}' --save s03-after >/dev/null
  # 5
  vr snapshot --session "$S" --save s03-after >/dev/null
  vr down >"$OUT/down.json"
fi
log "down ok=$(jget "d.get('ok')" <"$OUT/down.json")"
home=${VERIFY_ARCHON_HOME:-$(node -e "console.log(require('os').tmpdir())")/verify-archon}
# verify-archon 的 down 已写 authCheck（含 http429、刷新次数）时用它；旧版没写时沿用原来的统计（authcheck.py）
log "auth-check $(python3 "$AUTHCHECK" "$home/$RID/server.log" "$OUT/auth-check.json" "$OUT" "$RID" --down "$OUT/down.json" --no-electron)"
