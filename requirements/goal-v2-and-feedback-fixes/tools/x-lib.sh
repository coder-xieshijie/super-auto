#!/usr/bin/env bash
# X1、X2 补充验证（不是 verify 场景）共用函数，2026-10-02 第二轮自验 Electron C 线加。
# 在 m3-lib.sh（含 m2-lib 的启动锁、type_checked、读数函数）之上加：Goal Turn 读数（与 m4-electron.sh 相同的写法）、
# 只读读取实例 SQLite 的队列暂停与队列项、后台轨迹采样。在 agent-archon worktree 根目录 source。
source "$(dirname "${BASH_SOURCE[0]}")/m3-lib.sh"
E() { vr electron "$@"; }
etext() { E text --testid "$1" --timeout "${3:-10}" --save "$2" | jget "d.get('text')"; }
goal_e() { vr api GET $API/session/$1/goal --on electron --save "$2"; }
poll_e() { local s=$1; shift; vr poll $API/session/$s/goal --on electron "$@"; }
turn_end() { E wait --testid stop-button --state hidden --timeout "${1:-120}" >/dev/null; }
end_scenario() { E screenshot --save final-ui >/dev/null; m2_down "$@"; }
events_dir() { echo "$HOME_VA/$RID/data/v2/observability/events"; }

# goal_turn_open <session>：最新的 goal.turn_bound 没有对应的 goal.turn_settled 时打印 open:<turnId>，否则 none
goal_turn_open() {
  python3 - "$(events_dir)" "$1" <<'PYEOF'
import json, os, sys
root, sid = sys.argv[1], sys.argv[2]
bound, settled = [], set()
for dp, _, fs in os.walk(root):
    for f in fs:
        if not f.endswith('.jsonl'):
            continue
        for line in open(os.path.join(dp, f), errors='replace'):
            if sid not in line:
                continue
            try:
                e = json.loads(line)
            except Exception:
                continue
            fl = e.get('fields') or {}
            p = fl.get('payload') or {}
            if fl.get('eventType') == 'goal.turn_bound':
                bound.append((e.get('tsMs') or 0, p.get('turnId')))
            elif fl.get('eventType') == 'goal.turn_settled':
                settled.add(p.get('turnId'))
bound.sort()
print('open:' + bound[-1][1] if bound and bound[-1][1] not in settled else 'none')
PYEOF
}

# goal_events <session> [eventType...]：打印该会话的 goal 事件（tsMs eventType turnId 摘要），按时间排序
goal_events() {
  python3 - "$(events_dir)" "$@" <<'PYEOF'
import json, os, sys
root, sid, types = sys.argv[1], sys.argv[2], set(sys.argv[3:])
rows = []
for dp, _, fs in os.walk(root):
    for f in fs:
        if not f.endswith('.jsonl'):
            continue
        for line in open(os.path.join(dp, f), errors='replace'):
            if sid not in line:
                continue
            try:
                e = json.loads(line)
            except Exception:
                continue
            fl = e.get('fields') or {}
            et = fl.get('eventType')
            if not et or (types and et not in types):
                continue
            rows.append({'tsMs': e.get('tsMs'), 'eventType': et, 'payload': fl.get('payload') or {}})
rows.sort(key=lambda r: r['tsMs'] or 0)
for r in rows:
    print(json.dumps(r, ensure_ascii=False))
PYEOF
}

# wait_open_goal_turn <session> <timeout 秒> <name> [排除的 turnId]：有未结算的 Goal Turn 且 stop-button 可见
wait_open_goal_turn() {
  local deadline=$(( $(date +%s) + $2 )) o c
  while [ "$(date +%s)" -lt "$deadline" ]; do
    o=$(goal_turn_open "$1")
    c=$(node "$V" electron count --testid stop-button --run "$RID" 2>/dev/null | jget "d.get('count')")
    printf '{"at":%s,"goalTurn":"%s","stopButton":"%s"}\n' "$(now_ms)" "$o" "$c" >>"$OUT/$3-trajectory.jsonl"
    if [ "${o#open:}" != "$o" ] && [ "${o#open:}" != "${4:-}" ] && [ "$c" = 1 ]; then echo "${o#open:}"; return 0; fi
    case $(goal_raw "$1" | jget "d.get('status') or ''") in complete|blocked|budget_limited|usage_limited) return 1 ;; esac
    sleep 0.4
  done
  return 1
}

# queue_db <session> <name>：只读打开实例 SQLite，读该会话的队列暂停（local_runtime_queue_pauses）与队列项
# （local_runtime_queue_items，data_json 只取 source、message.origin、内容前 120 字），写 <OUT>/<name>.json 并打印
queue_db() {
  python3 - "$(m3_db)" "$1" "$OUT/$2.json" <<'PYEOF'
import json, sqlite3, sys, time
db, sid, out = sys.argv[1:4]
d = {'at': int(time.time() * 1000), 'session': sid, 'pause': None, 'items': [], 'error': None}
try:
    c = sqlite3.connect('file:' + db + '?mode=ro', uri=True, timeout=5)
    c.row_factory = sqlite3.Row
    r = c.execute('SELECT * FROM local_runtime_queue_pauses WHERE session_id = ?', (sid,)).fetchone()
    d['pause'] = dict(r) if r else None
    for r in c.execute('SELECT * FROM local_runtime_queue_items WHERE session_id = ? ORDER BY id', (sid,)):
        row = dict(r)
        try:
            data = json.loads(row.pop('data_json') or '{}')
        except Exception:
            data = {}
        msg = data.get('message') or {}
        content = msg.get('content') if isinstance(msg.get('content'), str) else (data.get('content') if isinstance(data.get('content'), str) else '')
        row['source'] = data.get('source')
        row['origin'] = msg.get('origin')
        row['content'] = (content or '')[:120]
        row['dataKeys'] = sorted(data.keys())
        d['items'].append(row)
except Exception as e:
    d['error'] = str(e)
json.dump(d, open(out, 'w'), indent=2, ensure_ascii=False)
print(json.dumps(d, ensure_ascii=False))
PYEOF
}

# history_has <session> <python 表达式，变量 ms 为消息列表>：0/1
history_eval() {
  node "$V" api GET $API/session/$1/message --on electron --run "$RID" 2>/dev/null | python3 -c 'import json,sys
try: d=json.load(sys.stdin)
except Exception: d={}
ms=(d.get("body") or {}).get("messages") or []
try: print(1 if eval(sys.argv[1]) else 0)
except Exception: print(0)' "$2"
}

# traj_sampler <session> <file> &：约每秒一行：Goal 状态/原因/等待原因、未结算 Goal Turn、stop-button、队列暂停与项数
traj_sampler() {
  local g o c q
  while :; do
    g=$(goal_raw "$1")
    o=$(goal_turn_open "$1")
    c=$(node "$V" electron count --testid stop-button --run "$RID" 2>/dev/null | jget "d.get('count')")
    q=$(queue_db "$1" _sampler-queue 2>/dev/null)
    [ -n "$g" ] || g='{}'; [ -n "$q" ] || q='{}'
    python3 -c 'import json,sys,time
g=json.loads(sys.argv[1] or "{}"); q=json.loads(sys.argv[4] or "{}")
p=q.get("pause") or {}
print(json.dumps({"at":int(time.time()*1000),"status":g.get("status"),"status_reason":g.get("status_reason"),
 "wait":(g.get("execution") or {}).get("wait_reason"),"goalTurn":sys.argv[2],"stopButton":sys.argv[3],
 "pauseCause":p.get("cause"),"pauseTrigger":p.get("trigger_turn_id"),"queueItems":[(i.get("status"),i.get("source")) for i in q.get("items") or []]}))' \
      "$g" "$o" "$c" "$q" >>"$2" 2>/dev/null
    sleep 0.5
  done
}

# wait_new_turn_bound <session> <排除 turnId> <timeout 秒> <name>：等该会话出现新的 goal.turn_bound，打印 turnId tsMs
wait_new_turn_bound() {
  local deadline=$(( $(date +%s) + $3 )) r
  while [ "$(date +%s)" -lt "$deadline" ]; do
    r=$(goal_events "$1" goal.turn_bound | python3 -c 'import json,sys
ex=set(sys.argv[1].split(","))
rows=[json.loads(l) for l in sys.stdin if l.strip()]
rows=[r for r in rows if r["payload"].get("turnId") not in ex]
print(rows[0]["payload"]["turnId"]+" "+str(rows[0]["tsMs"]) if rows else "")' "$2")
    printf '{"at":%s,"found":"%s"}\n' "$(now_ms)" "$r" >>"$OUT/$4-trajectory.jsonl"
    if [ -n "$r" ]; then echo "$r"; return 0; fi
    sleep 0.3
  done
  return 1
}

write_commands() { # write_commands <行...>：写 commands.md
  { echo "# $SC $(basename "$OUT") 命令"; echo; echo '```bash'; printf '%s\n' "$@"; echo '```'; } >"$OUT/commands.md"
}

# supplement_tool_state <session> <排除 turnId>：读实例里该会话的 LLM Context Inspector（live，只读），
# 找排除 Turn 以外的 Turn 中 expectedTools 含 bash 的调用；打印 running:<turnId>:<开始 ms>（已开始未结束）、done:<turnId> 或 none
supplement_tool_state() {
  python3 - "$HOME_VA/$RID/data/v2/sessions" "$1" "$2" <<'PYEOF'
import base64, json, os, sys
root, sid, ex = sys.argv[1:4]
marker = 'session_' + base64.urlsafe_b64encode(sid.encode()).decode().rstrip('=')
path = None
for dp, ds, _ in os.walk(root):
    for d in ds:
        if d.endswith(marker):
            path = os.path.join(dp, d, 'llm-context-inspector', 'events.jsonl')
            break
    if path:
        break
calls, started, ended = {}, {}, set()
if path and os.path.exists(path):
    for line in open(path, errors='replace'):
        try:
            e = json.loads(line)
        except Exception:
            continue
        if e.get('type') == 'call.captured' and e.get('turnId') != ex:
            for t in e.get('expectedTools') or []:
                if t.get('toolName') == 'bash':
                    calls[t.get('toolCallId')] = e.get('turnId')
        elif e.get('type') == 'tool.execution_started':
            started[e.get('toolCallId')] = e.get('startedAtMs')
        elif e.get('type') == 'tool.execution_completed':
            ended.add(e.get('toolCallId'))
res = 'none'
for tc, turn in calls.items():
    if tc in started and tc not in ended:
        res = 'running:%s:%s' % (turn, started[tc]); break
    if tc in ended:
        res = 'done:%s' % turn
print(res)
PYEOF
}

# questionnaire_watch <session> <前缀> &：会话出现 pending 问卷时存证一次（问卷行摘要、Goal、截图、aria），15 秒后再存一次 Goal 与截图。
# 2026-10-02 X1 f3 发现 Goal Turn 调 ask_user 后 Goal 300 秒无等待原因，f4 起加。
questionnaire_watch() {
  local s=$1 p=$2 q n=0
  while :; do
    q=$(python3 - "$(m3_db)" "$s" <<'PYEOF'
import json, sqlite3, sys
try:
    c = sqlite3.connect('file:' + sys.argv[1] + '?mode=ro', uri=True, timeout=5)
    r = c.execute("SELECT request_id, status, created_at, json_extract(request_json,'$.purpose'), json_extract(request_json,'$.goalId'), json_extract(request_json,'$.expiresAt'), json_extract(request_json,'$.title') FROM questionnaire_requests WHERE session_id=? AND status='pending' ORDER BY created_at DESC LIMIT 1", (sys.argv[2],)).fetchone()
    print(json.dumps(dict(zip(['request_id','status','created_at','purpose','goalId','expiresAt','title'], r)), ensure_ascii=False) if r else '')
except Exception:
    print('')
PYEOF
)
    if [ -n "$q" ]; then
      n=$((n + 1))
      printf '%s\n' "$q" >"$OUT/$p-questionnaire-$n.json"
      vr api GET $API/session/$s/goal --on electron --save "$p-goal-during-questionnaire-$n" >/dev/null
      vr electron screenshot --save "$p-questionnaire-$n" >/dev/null
      vr electron aria --save "$p-page-aria-questionnaire-$n" >/dev/null
      [ "$n" -ge 2 ] && return 0
      sleep 15
    else
      sleep 2
    fi
  done
}
