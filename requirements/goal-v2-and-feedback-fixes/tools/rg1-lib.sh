#!/usr/bin/env bash
# RG1 共用函数：rg1-api.sh、rg1-tui.sh、rg1-electron.sh 通过 source 引入。
# 在 agent-archon worktree 根目录运行。环境变量：
#   RG1_ROOT    证据根目录，默认 ../evidence/rg1-baseline（迁移版本用 rg1-migrated 之类）
#   RG1_TAG     证据名前缀，默认 rg1base（迁移版本用 rg1mig 之类）
#   RG1_CONFIG  三个入口共用的 staging 配置，默认 ~/.minimax/verify-goal-v2/config.yaml（含凭据，只传路径）
#   RG1_FLOWS   只跑这些流程（空格分隔），默认全部
#   RG1_PROXY_FLAG  TUI、Electron 的代理选项，默认 --no-proxy
# 证据名统一为 <TAG>-<功能>.<子功能>--<步骤>；流程结束 down 之后由 rg1-organize.py 把它们移到
# <RG1_ROOT>/<功能>/<子功能>/<入口>/，实例级文件（up.json、events.jsonl、日志）留在 <RG1_ROOT>/_runs/<入口>-<流程>/。

V=.agents/skills/verify-archon/scripts/verify-archon.mjs
RG1_TOOLS=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
RG1_ROOT=${RG1_ROOT:-$RG1_TOOLS/../evidence/rg1-baseline}
RG1_TAG=${RG1_TAG:-rg1base}
RG1_CONFIG=${RG1_CONFIG:-$HOME/.minimax/verify-goal-v2/config.yaml}
RG1_PROXY_FLAG=${RG1_PROXY_FLAG---no-proxy}
[ -f "$V" ] || { echo "rg1: run from the agent-archon worktree root" >&2; exit 2; }
[ -f "$RG1_CONFIG" ] || { echo "rg1: config not found: $RG1_CONFIG" >&2; exit 2; }
mkdir -p "$RG1_ROOT/_runs" "$RG1_ROOT/_inputs"
RG1_ROOT=$(cd "$RG1_ROOT" && pwd)
T=$RG1_TAG

GOAL_TERMINAL="goal.status=complete|paused|blocked|budget_limited|usage_limited"
SHOW_RUN="goal.status,goal.status_reason,goal.execution.wait_reason,goal.turns_used"

# 各入口共用的目标文本（照抄功能地图）
OBJ_COUNT3="Write the numbers 1 to 3 into count.txt, one number per line, then stop."
OBJ_COUNT4="Write the numbers 1 to 4 into count.txt, one number per line, then stop."
OBJ_BG='Start the shell command `sleep 40 && echo bg-done > bg.txt` as a background task (bash tool with run_in_background: true) and end your turn right away without waiting or polling. After that background task has finished, read bg.txt and confirm it contains bg-done. The goal is met only when bg.txt contains bg-done.'
OBJ_LATE='Start the shell command `sleep 45 && echo late-done > late.txt` as a background task (bash tool with run_in_background: true) and end your turn right away without waiting or polling. After that background task has finished, read late.txt and confirm it contains late-done. The goal is met only when late.txt contains late-done.'
OBJ_NOTES="Write a file notes.md with ten numbered one-line facts about the Rust programming language, then verify the file has exactly ten lines."
OBJ_TIMER="Run the shell command sleep 20 in the foreground (not in the background), then write timer.txt containing done."
OBJ_SLEEP30="Run the shell command sleep 30 in the foreground, then write done.txt containing ok."
OBJ_FRUIT='First call the ask_user tool exactly once with one single-choice question "Which fruit?" and two options: "Apple" (recommended, listed first) and "Banana". Do not set requiresExplicitResponse. After you get the answer, write the chosen fruit name to fruit.txt (only the name).'
OBJ_SECRET="Read the attached file goal-brief.txt and write the secret word it contains into secret.txt (only the word)."
OBJ_SECRET2="Read the attached file goal-brief-2.txt and write the secret word it contains into secret2.txt (only the word)."
OBJ_COLOR="Look at the attached image and write the color of the square (one lowercase word) into color.txt. "
OBJ_DONE="Reply with the single word DONE."

rg1_wants() { [ -z "${RG1_FLOWS:-}" ] || [[ " $RG1_FLOWS " == *" $1 "* ]]; }

rg1_log() { printf '%s [%s] %s\n' "$(date '+%H:%M:%S')" "${FLOW:-rg1}" "$*" >&2; }

# JSON 取值：echo "$json" | jget "d['body']['session_id']"
jget() { python3 -c 'import json,sys
try: d=json.load(sys.stdin)
except Exception: print(""); sys.exit(0)
try: v=eval(sys.argv[1])
except Exception: v=""
print("" if v is None else v)' "$1"; }

# vr <verify-archon 参数...>：对本流程实例执行一条命令（自动加 --run），stdout 输出其 JSON；
# 命令、退出码和截断的输出追加到 $RUNDIR/steps.jsonl。
vr() {
  local out rc
  out=$(node "$V" "$@" --run "$RID" 2>>"$RUNDIR/steps.stderr.log")
  rc=$?
  printf '%s' "$out" | python3 -c 'import json,sys,time
raw=sys.stdin.read()
try: parsed=json.loads(raw)
except Exception: parsed=raw
text=json.dumps(parsed, ensure_ascii=False)
if len(text)>20000: parsed={"truncated": text[:20000]}
print(json.dumps({"at":int(time.time()*1000),"rc":int(sys.argv[1]),"args":sys.argv[2:],"out":parsed}, ensure_ascii=False))' "$rc" "$@" >>"$RUNDIR/steps.jsonl"
  printf '%s\n' "$out"
  return $rc
}

# 起实例：rg1_up <入口 runtime|tui|electron> <流程名>；设置 FLOW、RUNDIR、RID。
rg1_up() {
  local kind=$1
  FLOW=$2
  RUNDIR="$RG1_ROOT/_runs/$kind-$FLOW"
  mkdir -p "$RUNDIR"
  local out
  case $kind in
    runtime) out=$(node "$V" up --config "$RG1_CONFIG" --evidence-dir "$RUNDIR" 2>>"$RUNDIR/steps.stderr.log") ;;
    tui) out=$(node "$V" tui up --config "$RG1_CONFIG" --evidence-dir "$RUNDIR" $RG1_PROXY_FLAG 2>>"$RUNDIR/steps.stderr.log") ;;
    electron) out=$(node "$V" electron up --config "$RG1_CONFIG" --evidence-dir "$RUNDIR" $RG1_PROXY_FLAG 2>>"$RUNDIR/steps.stderr.log") ;;
  esac
  printf '%s\n' "$out" >"$RUNDIR/up.json"
  RID=$(printf '%s' "$out" | jget "d['runId'] if d.get('ok') else ''")
  if [ -z "$RID" ]; then rg1_log "up failed: $(printf '%s' "$out" | head -c 400)"; return 1; fi
  echo "$RID" >"$RUNDIR/runId"
  rg1_log "up $kind runId=$RID"
  if [ "$kind" = runtime ]; then vr doctor >"$RUNDIR/doctor.json"; fi
  return 0
}

# 停实例并整理证据：rg1_down <入口 runtime|tui|electron> <入口目录名 api|tui|electron>
rg1_down() {
  local kind=$1 entry=$2
  case $kind in
    runtime) vr down >"$RUNDIR/down.json" ;;
    tui) vr tui down >"$RUNDIR/down.json" ;;
    electron) vr electron down >"$RUNDIR/down.json" ;;
  esac
  rg1_log "down $kind runId=$RID ok=$(jget "d.get('ok')" <"$RUNDIR/down.json")"
  # 环境核对：共享登录被别的进程刷新后，已启动实例手里的旧 token 失效，内容审核返回 401、输出被撤回。
  # 这种运行不代表产品行为，auth-check.json 里 contentSafety401 > 0 时整段重跑。
  local home=${VERIFY_ARCHON_HOME:-$(node -e "console.log(require('os').tmpdir())")/verify-archon}
  # verify-archon 的 down 已写 authCheck（含 http429、刷新次数）时用它；旧版没写时沿用原来的统计（authcheck.py）
  rg1_log "auth-check $(python3 "$RG1_TOOLS/authcheck.py" "$home/$RID/server.log" "$RUNDIR/auth-check.json" "$RUNDIR" "$RID" --down "$RUNDIR/down.json")"
  python3 "$RG1_TOOLS/rg1-organize.py" "$RUNDIR" "$RG1_ROOT" "$RG1_TAG" "$entry" "$RID" >&2
}

# 输入文件（工作目录之外）。三个入口脚本可能并行，先写临时文件再改名，不会读到半个文件。
rg1_inputs() {
  local d="$RG1_ROOT/_inputs"
  printf 'The secret word is PAPAYA-42.\n' >"$d/.goal-brief.txt.$$" && mv -f "$d/.goal-brief.txt.$$" "$d/goal-brief.txt"
  printf 'The second secret word is MANGO-7.\n' >"$d/.goal-brief-2.txt.$$" && mv -f "$d/.goal-brief-2.txt.$$" "$d/goal-brief-2.txt"
  python3 - "$d/.red-square.png.$$" <<'EOF'
import struct, sys, zlib
w = h = 64
raw = b''.join(b'\x00' + b'\xff\x00\x00' * w for _ in range(h))
def chunk(tag, data):
    return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')
open(sys.argv[1], 'wb').write(png)
EOF
  mv -f "$d/.red-square.png.$$" "$d/red-square.png"
}
