#!/usr/bin/env bash
# M3 场景共用函数（verify.md S12–S21b、S30、S34–S36、S40）。在 m2-lib.sh 之上加：
#   - 启动互斥：所有入口的 up 经同一把锁串行，up 之后再等 M3_UP_GAP 秒才放锁（共享登录刷新会让先起的实例 401）
#   - 后台任务读数：只读打开实例的 runtime-state.sqlite，列出某会话的 local_runtime_background_tasks
#   - 端口探测、历史中找回复、等 Goal 离开某次状态
# 用法同 m2-lib.sh：在 agent-archon worktree 根目录 source。M2_ROOT 默认 ../evidence/m3。
M3_TOOLS=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
export M2_ROOT=${M2_ROOT:-$M3_TOOLS/../evidence/m3}
source "$M3_TOOLS/m2-lib.sh"
M3_UP_LOCK=${M3_UP_LOCK:-/tmp/gv2-m3-up.lock}
M3_UP_GAP=${M3_UP_GAP:-6}
HOME_VA=${VERIFY_ARCHON_HOME:-$(node -e "console.log(require('os').tmpdir())")/verify-archon}

m3_lock() {
  local waited=0
  until mkdir "$M3_UP_LOCK" 2>/dev/null; do
    sleep 1; waited=$((waited + 1))
    # 锁超过 15 分钟视为残留（持锁进程已死）
    if [ "$waited" -gt 900 ]; then rmdir "$M3_UP_LOCK" 2>/dev/null; waited=0; fi
  done
  echo "$$ ${SC:-?} $(date +%s)" >"$M3_UP_LOCK/owner"
}
m3_unlock() { rm -f "$M3_UP_LOCK/owner"; rmdir "$M3_UP_LOCK" 2>/dev/null; return 0; }

# m3_up <kind> [参数...]：持锁 up，成功后再等 M3_UP_GAP 秒放锁
m3_up() {
  local rc
  m3_lock
  m2_log "up lock acquired"
  M2_LOCK_HELD=1 m2_up "$@"; rc=$?
  sleep "$M3_UP_GAP"
  m3_unlock
  return $rc
}

m3_db() { echo "$HOME_VA/$RID/data/v2/sqlite/runtime-state.sqlite"; }

# bg_tasks <session> <name>：只读列出该会话的后台任务，写 <OUT>/<name>.json 并打印
bg_tasks() {
  python3 - "$(m3_db)" "$1" "$OUT/$2.json" <<'EOF'
import json, sqlite3, sys, time
db, sid, out = sys.argv[1:4]
rows = []
try:
    c = sqlite3.connect('file:' + db + '?mode=ro', uri=True, timeout=5)
    for task_id, kind, status, created, updated, ended, rec in c.execute(
            "SELECT task_id, kind, status, created_at_ms, updated_at_ms, ended_at_ms, record_json "
            "FROM local_runtime_background_tasks WHERE owner_session_id = ? ORDER BY created_at_ms", (sid,)):
        try:
            r = json.loads(rec)
        except Exception:
            r = {}
        meta = r.get('metadata') or {}
        desc = r.get('description') or r.get('title') or r.get('command') or (r.get('input') or {}).get('command') or ''
        rows.append({'taskId': task_id, 'kind': kind, 'status': status, 'createdAtMs': created, 'updatedAtMs': updated,
                     'endedAtMs': ended, 'parentTurnId': meta.get('parentTurnId'), 'description': str(desc)[:200]})
    err = None
except Exception as e:
    err = str(e)
d = {'at': int(time.time() * 1000), 'session': sid, 'tasks': rows, 'error': err}
json.dump(d, open(out, 'w'), indent=2, ensure_ascii=False)
print(json.dumps(d, ensure_ascii=False))
EOF
}

# port_probe <port> <name>：HTTP 探测 127.0.0.1:<port>，写 <OUT>/<name>.json
port_probe() {
  local code
  code=$(curl -s -o /dev/null -m 3 -w '%{http_code}' "http://127.0.0.1:$1/" 2>/dev/null)
  printf '{"at":%s,"port":%s,"httpCode":"%s"}\n' "$(now_ms)" "$1" "$code" | tee "$OUT/$2.json"
}

# goal_raw <session>：读 Goal（不记 steps），打印 goal 对象 JSON
goal_raw() { node "$V" api GET $API/session/$1/goal $(ON) --run "$RID" 2>/dev/null | jget "json.dumps(d['body'].get('goal') or {})"; }

# wait_goal_relimited <session> <status> <prev_requests_used> <timeout 秒> <save>：
# 等 Goal 的请求数超过 prev 且 status 回到 <status>（恢复后再次受限/暂停），最后 vr 读一次存证
wait_goal_relimited() {
  local s=$1 want=$2 prev=$3 deadline=$(( $(date +%s) + $4 )) gj traj="$OUT/$5-trajectory.jsonl"
  while [ "$(date +%s)" -lt "$deadline" ]; do
    gj=$(goal_raw "$s")
    printf '%s\n' "$gj" | python3 -c 'import json,sys,time
g=json.loads(sys.stdin.read() or "{}")
print(json.dumps({"at":int(time.time()*1000),"status":g.get("status"),"status_reason":g.get("status_reason"),"requests_used":g.get("requests_used"),"wait":(g.get("execution") or {}).get("wait_reason"),"usage_recovery_scheduled":g.get("usage_recovery_scheduled")}))' >>"$traj"
    if printf '%s' "$gj" | python3 -c 'import json,sys
g=json.loads(sys.stdin.read() or "{}")
sys.exit(0 if g.get("status")==sys.argv[1] and (g.get("requests_used") or 0)>int(sys.argv[2]) else 1)' "$want" "$prev"; then
      break
    fi
    sleep 1
  done
  vr api GET $API/session/$s/goal $(ON) --save "$5" >/dev/null
}

# wait_reply <session> <问题片段> <timeout 秒> <save>：等历史中该用户消息之后出现助手消息，存历史
wait_reply() {
  local s=$1 q=$2 deadline=$(( $(date +%s) + $3 ))
  while [ "$(date +%s)" -lt "$deadline" ]; do
    if node "$V" api GET $API/session/$s/message $(ON) --run "$RID" 2>/dev/null | python3 -c 'import json,sys
d=json.load(sys.stdin); ms=(d.get("body") or {}).get("messages") or []
idx=[i for i,m in enumerate(ms) if m.get("role")=="user" and sys.argv[1] in str(m.get("msg_content",""))]
ok=bool(idx) and any(m.get("role")=="assistant" and str(m.get("msg_content","")).strip() for m in ms[idx[-1]+1:])
sys.exit(0 if ok else 1)' "$q"; then
      break
    fi
    sleep 2
  done
  vr api GET $API/session/$s/message $(ON) --save "$4" >/dev/null
}

# banner_sampler <testid> <file> &：每 3 秒读一次 Electron 文字，写 jsonl；用 kill 停
banner_sampler() {
  while :; do
    node "$V" electron text --testid "$1" --timeout 2 --run "$RID" 2>/dev/null | python3 -c 'import json,sys,time
try: d=json.load(sys.stdin)
except Exception: d={}
print(json.dumps({"at":int(time.time()*1000),"text":d.get("text"),"ok":d.get("ok")},ensure_ascii=False))' >>"$2"
    sleep 3
  done
}

# tui_status：当前状态栏 JSON
tui_status() { node "$V" tui screen --run "$RID" 2>/dev/null | jget "json.dumps(d.get('status') or {})"; }

# tui_wait_turn_after <seq> <timeout> <save>：等状态栏 seq 大于给定值且 state 不是 run/perm/ask
tui_wait_turn_after() {
  local prev=$1 deadline=$(( $(date +%s) + $2 )) st
  while [ "$(date +%s)" -lt "$deadline" ]; do
    st=$(tui_status)
    printf '%s\n' "$st" | python3 -c 'import json,sys,time
s=json.loads(sys.stdin.read() or "{}"); s["at"]=int(time.time()*1000); print(json.dumps(s))' >>"$OUT/$3-status-trajectory.jsonl"
    if printf '%s' "$st" | python3 -c 'import json,sys
s=json.loads(sys.stdin.read() or "{}")
sys.exit(0 if int(s.get("seq") or 0)>int(sys.argv[1]) and s.get("state") not in ("run","perm","ask","plan") else 1)' "$prev"; then
      break
    fi
    sleep 1
  done
  vr tui screen --all --save "$3" >/dev/null
}
tui_seq() { tui_status | jget "d.get('seq') or 0"; }

# 结束时核对：本实例启动的 http.server 端口不再监听
port_closed_after_down() {
  for p in "$@"; do port_probe "$p" "after-down-port-$p" >/dev/null; done
}

# api_send <session> <text> <save>：接口发普通消息；会话有排队项（409 local_session_has_queued_messages）时改用
# POST .../queue（verify-archon SKILL.md 的写法，Desktop 遇到 409 也排队）
api_send() {
  local body st
  body=$(python3 -c 'import json,sys; print(json.dumps({"content":sys.argv[1]}))' "$2")
  st=$(vr api POST $API/session/$1/message $(ON) --data "$body" --save "$3" | jget "d.get('status') or (d.get('response') or {}).get('status')")
  if [ "$st" = 409 ]; then
    body=$(python3 -c 'import json,sys,uuid; print(json.dumps({"content":sys.argv[1],"client_request_id":"m3-"+uuid.uuid4().hex[:12]}))' "$2")
    vr api POST $API/session/$1/queue $(ON) --data "$body" --save "$3-queue" >/dev/null
  fi
}
