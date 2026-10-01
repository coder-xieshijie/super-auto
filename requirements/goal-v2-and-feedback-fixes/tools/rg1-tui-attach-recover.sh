#!/usr/bin/env bash
# RG1 补跑：附件 · 失败后恢复 · TUI（attachments.md“坑”：首轮 504 → paused(infra_retryable)，/goal resume 后请求仍带图片，Goal 完成）。
# 用故障注入构造首轮失败：tui up --fault，规则让下一个新会话的第 1 次主执行请求返回一次 504：
#   fault add --on tui --session next --role main --nth 1 --times 1 --status 504 --body '{"status_msg":"请求处理超时"}'
# 不做 PONG 冒烟（TUI 的冒烟会落在同一会话，占掉 main 的 n=1）；注入的那次 attempt 本身证明流量经过代理。
# 用法（agent-archon worktree 根目录）：bash <tools>/rg1-tui-attach-recover.sh <证据目录>
# 环境变量：RG1_CONFIG（默认 ~/.minimax/verify-goal-v2/config.yaml，含凭据，只传路径）
set -u
OUT=$1
V=.agents/skills/verify-archon/scripts/verify-archon.mjs
CONFIG=${RG1_CONFIG:-$HOME/.minimax/verify-goal-v2/config.yaml}
TOOLS=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
IMG=$TOOLS/../evidence/rg1-baseline/_inputs/red-square.png
OBJ="Look at the attached image and write the color of the square (one lowercase word) into color.txt. "
T=rg1att
[ -f "$V" ] || { echo "rg1-tui-attach-recover: run from the agent-archon worktree root" >&2; exit 2; }
[ -f "$IMG" ] || { echo "missing $IMG" >&2; exit 2; }
mkdir -p "$OUT"
OUT=$(cd "$OUT" && pwd)
log() { printf '%s [tui-attach-recover] %s\n' "$(date '+%H:%M:%S')" "$*" >&2; }
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
tui_idle() { vr tui wait --status "state=ready|done|fail|cancel|error" --hold 3 --timeout "${1:-180}" ${2:+--save "$2"}; }

cp "$IMG" "$OUT/input-red-square.png"
up_out=$(node "$V" tui up --config "$CONFIG" --fault --evidence-dir "$OUT" 2>>"$OUT/steps.stderr.log")
printf '%s\n' "$up_out" >"$OUT/up.json"
RID=$(printf '%s' "$up_out" | jget "d['runId'] if d.get('ok') else ''")
[ -n "$RID" ] || { log "up failed: $(printf '%s' "$up_out" | head -c 400)"; exit 1; }
echo "$RID" >"$OUT/runId"
git rev-parse HEAD >"$OUT/git-head"
git status --short >"$OUT/git-status"
log "up runId=$RID head=$(git rev-parse --short HEAD) fault=$(printf '%s' "$up_out" | jget "d.get('fault',{}).get('llmHost')")"

vr fault add --on tui --session next --role main --nth 1 --times 1 --status 504 --body '{"status_msg":"请求处理超时"}' --note "RG1 attachments failure-resume: first main request of the next new session fails once with 504" --save fault >/dev/null
vr fault list --on tui --save fault >/dev/null

# 输入目标、粘贴图片、发送（同 rg1-tui.sh flow_attachments）
vr tui type "/goal $OBJ" --no-submit >/dev/null
vr tui paste "$IMG" >/dev/null
vr tui wait --text "[Image #1]" --timeout 15 --save "$T-pasted" >/dev/null
vr tui keys enter >/dev/null
if ! vr tui wait --text "Goal started" --timeout 10 --save "$T-started" >/dev/null; then
  vr tui keys enter >/dev/null
  vr tui wait --text "Goal started" --timeout 30 --save "$T-started-2" >/dev/null
fi
out=$(vr tui wait --text "Goal · Paused|Goal complete" --timeout 300 --save "$T-first-terminal")
tui_idle 60 "$T-first-idle" >/dev/null
vr tui screen --save "$T-paused-screen" >/dev/null
vr tui snapshot --save "$T-paused-snap" >/dev/null
vr fault log --on tui --save fault >/dev/null
vr fault list --on tui --save fault >/dev/null
if printf '%s' "$out" | grep -q 'Goal complete'; then
  log "first round did not fail (Goal complete without Paused)"
else
  # 恢复：/goal resume（attachments.md“坑”）
  vr tui type "/goal resume" >/dev/null
  vr tui wait --text "Goal resumed" --timeout 20 --save "$T-resumed" >/dev/null
  vr tui wait --text "Goal complete|Goal · Paused" --timeout 420 --save "$T-resume-terminal" >/dev/null
fi
tui_idle 120 "$T-final-idle" >/dev/null
vr tui screen --save "$T-final-screen" >/dev/null
vr tui snapshot --save "$T-final-snap" >/dev/null
vr fault log --on tui --save fault >/dev/null
vr fault list --on tui --save fault >/dev/null
vr tui down >"$OUT/down.json"
log "down ok=$(jget "d.get('ok')" <"$OUT/down.json")"

home=${VERIFY_ARCHON_HOME:-$(node -e "console.log(require('os').tmpdir())")/verify-archon}
python3 - "$home/$RID/server.log" "$OUT/auth-check.json" "$OUT" <<'PY'
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
PY
log "auth-check contentSafety401=$(jget "d.get('contentSafety401')" <"$OUT/auth-check.json")"
