#!/usr/bin/env bash
# M2 场景共用函数（verify.md S01–S11、S32、S37、S38、S41）。各 m2-*.sh 用 source 引入。
# 在 agent-archon worktree 根目录运行。环境变量：
#   M2_ROOT    证据根，默认 ../evidence/m2
#   M2_CONFIG  验证配置，默认 ~/.minimax/verify-goal-v2/config.yaml（含凭据，只传路径，不读不打印）
#   M2_PROXY_FLAG  TUI、Electron 不带 --fault 时的代理选项，默认 --no-proxy
# 每次运行的证据放 <M2_ROOT>/<场景>/<尝试名>/，含 git-head、git-status、up.json、runId、steps.jsonl、
# auth-check.json，以及 verify-archon 写入的 NNN-*.json、events.jsonl、日志与截图。

V=.agents/skills/verify-archon/scripts/verify-archon.mjs
M2_TOOLS=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
M2_ROOT=${M2_ROOT:-$M2_TOOLS/../evidence/m2}
M2_CONFIG=${M2_CONFIG:-$HOME/.minimax/verify-goal-v2/config.yaml}
M2_PROXY_FLAG=${M2_PROXY_FLAG---no-proxy}
API=/minimax-desktop/api/v1
TERMINAL="goal.status=complete|paused|blocked|budget_limited|usage_limited"
SHOW="goal.status,goal.status_reason,goal.execution.wait_reason,goal.turns_used,goal.requests_used,goal.work_requests,goal.grace_requests,goal.legacy_turns,goal.unknown_requests,goal.tokens_used,goal.usage_incomplete"
[ -f "$V" ] || { echo "m2: run from the agent-archon worktree root" >&2; exit 2; }
[ -f "$M2_CONFIG" ] || { echo "m2: config not found: $M2_CONFIG" >&2; exit 2; }

m2_log() { printf '%s [%s] %s\n' "$(date '+%H:%M:%S')" "${SC:-m2}" "$*" >&2; }

jget() { python3 -c 'import json,sys
try: d=json.load(sys.stdin)
except Exception: print(""); sys.exit(0)
try: v=eval(sys.argv[1])
except Exception: v=""
print("" if v is None else v)' "$1"; }

now_ms() { python3 -c 'import time; print(int(time.time()*1000))'; }

# 派生配置：m2_config <名字> <defaultMainTurns> <graceSteps>。在原配置末尾追加 goal.budget，写到
# /tmp/gv2-cfg/<名字>.yaml（权限 600），不读出、不打印原配置内容。已有同名文件时直接用。
m2_config() {
  local name=$1 turns=$2 grace=$3 out=/tmp/gv2-cfg/$1.yaml
  mkdir -p /tmp/gv2-cfg
  if [ ! -f "$out" ]; then
    umask 077
    { cat "$M2_CONFIG"; printf '\ngoal:\n  budget:\n    defaultMainTurns: %s\n    graceSteps: %s\n' "$turns" "$grace"; } >"$out"
    chmod 600 "$out"
  fi
  printf '%s\n' "$out"
}

# m2_begin <场景> <尝试名>：建证据目录，记 git HEAD 与工作区状态
m2_begin() {
  SC=$1
  OUT="$M2_ROOT/$1/$2"
  mkdir -p "$OUT"
  OUT=$(cd "$OUT" && pwd)
  git rev-parse HEAD >"$OUT/git-head"
  git status --porcelain >"$OUT/git-status"
  m2_log "begin $OUT head=$(git rev-parse --short HEAD) dirty=$(wc -l <"$OUT/git-status" | tr -d ' ')"
}

# vr <verify-archon 参数...>：对本实例执行（自动加 --run），stdout 为其 JSON；命令与截断输出记到 steps.jsonl
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

# m2_up <runtime|tui|electron> [启动参数...]：--config 默认 $M2_CONFIG，可用 M2_UP_CONFIG 覆盖。
# 设了 M2_UP_LOCK（目录路径）时，up 经这把锁串行，up 后再等 M2_UP_GAP 秒（默认 6）放锁；与 m3-lib 的 M3_UP_LOCK
# 指向同一路径即可让 M2、M3 脚本共用一把启动锁（m3_up 已持锁时传 M2_LOCK_HELD=1，不重复加锁）
m2_up() {
  if [ -n "${M2_UP_LOCK:-}" ] && [ -z "${M2_LOCK_HELD:-}" ]; then
    local rc waited=0
    until mkdir "$M2_UP_LOCK" 2>/dev/null; do
      sleep 1; waited=$((waited + 1))
      if [ "$waited" -gt 900 ]; then rmdir "$M2_UP_LOCK" 2>/dev/null; waited=0; fi
    done
    echo "$$ ${SC:-?} $(date +%s)" >"$M2_UP_LOCK/owner"
    m2_log "up lock acquired"
    M2_LOCK_HELD=1 m2_up "$@"; rc=$?
    sleep "${M2_UP_GAP:-6}"
    rm -f "$M2_UP_LOCK/owner"; rmdir "$M2_UP_LOCK" 2>/dev/null
    return $rc
  fi
  local kind=$1; shift
  local cfg=${M2_UP_CONFIG:-$M2_CONFIG} out proxy=()
  case " $* " in *" --fault "*) ;; *) [ "$kind" = runtime ] || proxy=($M2_PROXY_FLAG) ;; esac
  case $kind in
    runtime) out=$(node "$V" up --config "$cfg" --evidence-dir "$OUT" "$@" 2>>"$OUT/steps.stderr.log") ;;
    tui) out=$(node "$V" tui up --config "$cfg" --evidence-dir "$OUT" ${proxy[@]+"${proxy[@]}"} "$@" 2>>"$OUT/steps.stderr.log") ;;
    electron) out=$(node "$V" electron up --config "$cfg" --evidence-dir "$OUT" ${proxy[@]+"${proxy[@]}"} "$@" 2>>"$OUT/steps.stderr.log") ;;
  esac
  printf '%s\n' "$out" >"$OUT/up.json"
  RID=$(printf '%s' "$out" | jget "d['runId'] if d.get('ok') else ''")
  if [ -z "$RID" ]; then m2_log "up $kind failed: $(printf '%s' "$out" | head -c 600)"; return 1; fi
  echo "$RID" >"$OUT/runId"
  KIND=$kind
  m2_log "up $kind runId=$RID"
  [ "$kind" = runtime ] && vr doctor >"$OUT/doctor.json"
  return 0
}

ON() { case $KIND in electron) echo "--on electron" ;; *) echo "" ;; esac; }

# m2_down [--keep-data]：停本实例，做登录失效核对
m2_down() {
  case $KIND in
    runtime) vr down "$@" >"$OUT/down.json" ;;
    tui) vr tui down "$@" >"$OUT/down.json" ;;
    electron) vr electron down "$@" >"$OUT/down.json" ;;
  esac
  m2_log "down $KIND runId=$RID ok=$(jget "d.get('ok')" <"$OUT/down.json")"
  m2_authcheck
}

# 共享登录被别的进程刷新后，实例手里的旧 token 失效：内容审核 401、Electron 跳登录页。>0 时本次运行作废重跑。
m2_authcheck() {
  local home=${VERIFY_ARCHON_HOME:-$(node -e "console.log(require('os').tmpdir())")/verify-archon}
  python3 - "$home/$RID/server.log" "$OUT/auth-check.json" "$OUT" <<'EOF'
import glob, json, os, re, sys
log, out, rundir = sys.argv[1], sys.argv[2], sys.argv[3]
text = ''
for f in [log, os.path.join(rundir, 'electron-main.log')] + glob.glob(os.path.join(rundir, 'runtime-logs', '*')):
    try:
        text += open(f, errors='replace').read() + '\n'
    except OSError:
        pass
lines = [re.sub(r'\x1b\[[0-9;]*m', '', l) for l in text.splitlines() if 'content-safety' in l]
bad = [l for l in lines if '"statusCode":401' in l or 'failureKind":"auth' in l]
login = [l for l in text.splitlines() if 'navigateToLogin' in l or 'bearer is not synced' in l]
json.dump({'serverLog': log, 'contentSafetyLines': len(lines), 'contentSafety401': len(bad),
           'first401': bad[0][:300] if bad else None, 'electronAuthLost': len(login)}, open(out, 'w'), indent=2)
EOF
  m2_log "auth-check contentSafety401=$(jget "d.get('contentSafety401')" <"$OUT/auth-check.json") electronAuthLost=$(jget "d.get('electronAuthLost')" <"$OUT/auth-check.json")"
}

m2_session() { # m2_session <title> <save>：接口新建会话，输出 session_id
  vr api POST $API/agent/mavis/session $(ON) --data "{\"title\":\"$1\"}" --save "$2" | jget "d['body']['session_id']"
}

m2_goal_create() { # m2_goal_create <session> <objective> <save> [token_budget]
  local body
  body=$(python3 -c 'import json,sys
d={"objective":sys.argv[1]}
if len(sys.argv)>2 and sys.argv[2]: d["token_budget"]=int(sys.argv[2])
print(json.dumps(d))' "$2" "${4:-}")
  vr api POST $API/session/$1/goal $(ON) --data "$body" --save "$3"
}

m2_smoke_api() { # 冒烟：单独会话 PONG（fault 实例上兼作流量核对）
  local s0
  s0=$(m2_session "m2 smoke" smoke-session)
  vr api POST $API/session/$s0/message --data '{"content":"Reply with exactly the word PONG and nothing else."}' --save smoke-send >/dev/null
  vr api GET $API/session/$s0/message --save smoke-history | python3 -c 'import json,sys
d=json.load(sys.stdin); ms=(d.get("body") or {}).get("messages") or []
ok=any(m.get("role")=="assistant" and str(m.get("msg_content","")).strip()=="PONG" for m in ms)
print("smoke PONG", ok)' >&2
}

# Electron 首次启动的弹窗
m2_close_popups() {
  vr electron click --selector 'role=dialog >> role=button[name="关闭"]' --timeout 8 >/dev/null
  vr electron click --role button --name "关闭签到" --exact --timeout 5 >/dev/null
  return 0
}

m2_latest_session() { # Electron：按 created_at 取最新的顶层会话
  vr api GET $API/agent/mavis/session --on electron | python3 -c 'import json,sys
d=json.load(sys.stdin).get("body") or {}
items=d.get("sessions") or d.get("items") or d.get("list") or []
items=[s for s in items if not s.get("parent_session_id")]
items.sort(key=lambda s: s.get("created_at") or 0)
print(items[-1]["session_id"] if items else "")'
}

# 输入框写入并核对（2026-10-01 S03 事故后加）：测试窗口在屏幕上时，真实键盘输入可能混进输入框。
# 写入前输入框非空先清空；写入后读回，必须与预期逐字一致才返回 0；不一致清空重写一次，仍不一致返回 1。
# 不一致时只记长度和哈希（input-mismatch.jsonl），不记录混入的原文。
type_checked() {
  local want=$1 got i
  for i in 1 2; do
    got=$(node "$V" electron text --testid message-textarea --timeout 5 --run "$RID" 2>/dev/null | jget "(d.get('text') or '').strip()")
    if [ -n "$got" ]; then
      vr electron press --testid message-textarea --key "Meta+a" >/dev/null
      vr electron press --testid message-textarea --key Backspace >/dev/null
    fi
    vr electron type --testid message-textarea --value "$want" >/dev/null
    got=$(node "$V" electron text --testid message-textarea --timeout 5 --run "$RID" 2>/dev/null | jget "(d.get('text') or '').strip()")
    [ "$got" = "$want" ] && return 0
    python3 -c 'import hashlib,json,sys,time
w,g=sys.argv[1],sys.argv[2]
print(json.dumps({"at":int(time.time()*1000),"try":int(sys.argv[3]),"wantLen":len(w),"gotLen":len(g),"gotSha1":hashlib.sha1(g.encode()).hexdigest()[:12],"gotEndsWithWant":g.endswith(w)}))' "$want" "$got" "$i" >>"$OUT/input-mismatch.jsonl"
    m2_log "message-textarea content mismatch (try $i)"
  done
  return 1
}
# 输入被污染：清空输入框、截图、down，作废本次运行（退出码 3）
input_abort() {
  vr electron press --testid message-textarea --key "Meta+a" >/dev/null
  vr electron press --testid message-textarea --key Backspace >/dev/null
  echo input-contaminated >"$OUT/input-contaminated"
  m2_log "input contaminated: aborting run"
  vr electron screenshot --save input-contaminated >/dev/null
  m2_down
  exit 3
}

m2_send_goal_electron() { # m2_send_goal_electron <objective> <save 前缀>
  type_checked "/goal $1" || input_abort
  vr electron click --testid send-button >/dev/null
  vr electron wait --testid thread-goal-banner --timeout 60 --save "$2-banner" >/dev/null
}
