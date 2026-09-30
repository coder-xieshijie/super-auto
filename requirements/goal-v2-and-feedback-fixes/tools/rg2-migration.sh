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

git rev-parse HEAD >"$OUT/git-head"
git status --short >"$OUT/git-status"

if [ "$SC" = S02 ]; then
  up_out=$(node "$V" tui up --config "$CONFIG" --evidence-dir "$OUT" --no-proxy 2>>"$OUT/steps.stderr.log")
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
  up_out=$(node "$V" up --config "$CONFIG" --evidence-dir "$OUT" 2>>"$OUT/steps.stderr.log")
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
python3 - "$home/$RID/server.log" "$OUT/auth-check.json" "$OUT" <<'EOF'
import glob, json, os, re, sys
log, out, rundir = sys.argv[1], sys.argv[2], sys.argv[3]
text = ''
for f in [log] + glob.glob(os.path.join(rundir, 'runtime-logs', '*')):
    try:
        text += open(f, errors='replace').read() + '\n'
    except OSError:
        pass
lines = [re.sub(r'\x1b\[[0-9;]*m', '', l) for l in text.splitlines() if 'content-safety' in l]
bad = [l for l in lines if '"statusCode":401' in l or 'failureKind":"auth' in l]
json.dump({'serverLog': log, 'contentSafetyLines': len(lines), 'contentSafety401': len(bad), 'first401': bad[0][:300] if bad else None,
           'electronAuthLost': 0}, open(out, 'w'), indent=2)
EOF
log "auth-check contentSafety401=$(jget "d.get('contentSafety401')" <"$OUT/auth-check.json")"
