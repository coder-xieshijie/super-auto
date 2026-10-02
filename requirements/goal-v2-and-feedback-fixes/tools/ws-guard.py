#!/usr/bin/env python3
"""运行中的 workspace 越界守卫（第三轮最终自验 E3 线加，2026-10-02）。

只读轮询一个 verify-archon 实例的 LLM Context Inspector（data/v2/sessions/**/llm-context-inspector/，含 verifier 等子会话），检查每个模型响应里
文件类、shell 类工具调用的路径参数；发现指向 workspace 以外的路径时，在证据目录追加一条 ws-incident.jsonl：
只记工具名、turnId、callId、时间与类别（host / home-ref / parent-ref / tmp / instance-run-dir），不记命令或输出原文；
只有落在本实例临时目录内的路径记脱敏后的形状 instancePathShapes（实例根换成 <inst>、会话 id 换成 *），host、home 类不记路径。
kill 模式下立即 `electron down` 该实例（输出写 guard-down.json，并建 guard-killed 标记）。
kill-host 模式（2026-10-02 TA 线加，owner 定为各验证线统一口径）：越出本实例临时目录（host、home-ref、/tmp）或任何 workspace 外写入
（记录里 outsideWrite 为 true）时立即停实例；本实例临时目录内的只读读取只记录。down 命令按实例 state.json 的 kind 选
（electron down、tui down、down）；接口、TUI 实例另放行 <实例>/workspace。

用法：python3 ws-guard.py <实例目录 $HOME_VA/$RID> <runId> <证据目录> <kill|kill-host|record> [最长秒数，默认 3600]
kill-host（owner 2026-10-02 口径）：越出实例临时目录（host、home-ref、tmp、parent-escape）或 workspace 外的任何写入（outside_write）
立即停实例；实例目录内的只读读取（instance-run-dir、parent-ref）只记录。
在被测检出根目录运行（kill 用 .agents/skills/verify-archon/scripts/verify-archon.mjs）。证据目录出现 down.json、
guard-stop 或实例目录消失时退出。

允许：任意 data/sessions/mvs_*/workspace 之内（规范化后）；data/v2/assets/ 之内（附件）；/dev/null 等设备；
/usr/bin、/bin 等可执行文件目录。update_goal、get_goal、task、ask_user 等非文件工具的文本不检查（子会话自己的调用另有 Inspector）。
"""
import base64
import glob
import json
import os
import re
import subprocess
import sys
import time

V = '.agents/skills/verify-archon/scripts/verify-archon.mjs'
FILE_TOOLS = {'bash', 'read', 'write', 'edit', 'multiedit', 'glob', 'grep', 'ls', 'list', 'view', 'apply_patch', 'shell'}
PATH_KEYS = ('path', 'file_path', 'filePath', 'filepath', 'cwd', 'workdir', 'directory', 'dir', 'paths', 'pattern', 'include', 'target')
DEV_OK = {'/dev/null', '/dev/stdout', '/dev/stderr', '/dev/zero', '/dev/stdin', '/dev/tty'}
BIN_OK = ('/usr/bin/', '/bin/', '/usr/local/bin/', '/opt/homebrew/bin/', '/usr/sbin/', '/sbin/')


def norm(p):
    p = os.path.normpath(p)
    return p[len('/private'):] if p.startswith('/private/') else p


INST = WS_RE = ASSETS = None
KIND = 'electron'
# 2026-10-02 TA 线加：down 命令按实例类型选；kill-host 模式只在越出实例临时目录（host、home、/tmp）时停实例，
# 实例目录内（instance-run-dir、parent-ref）只记录。kill、record 两种模式的行为不变。
DOWN_CMD = {'electron': ['electron', 'down'], 'tui': ['tui', 'down'], 'runtime': ['down']}
HOST_CATS = {'host', 'home-ref', 'tmp', 'parent-escape'}
# 2026-10-02 E3 线补：连续 .. 足以越出实例目录（parent-escape：Electron 的 workspace 在 <实例>/data/sessions/<会话>/workspace，
# 5 级才越出；接口、TUI 在 <实例>/workspace，2 级）也立即停实例。workspace 外写入由下方 outside_write() 判断。
PARENT_RUN = re.compile(r'''(?:\.\./)*\.\.(?=$|[/\s"';|&)<>`])''')


def set_instance(inst):
    global INST, WS_RE, ASSETS
    INST = norm(os.path.realpath(inst))
    WS_RE = re.compile(re.escape(INST) + r'/data/sessions/mvs_[0-9a-f]+/workspace(?:/|$)')
    ASSETS = INST + '/data/v2/assets/'


def classify_abs(p):
    q = norm(p)
    if q in DEV_OK or q.startswith(BIN_OK) or q in ('/usr/bin', '/bin'):
        return None
    if WS_RE.match(q + '/') or q.startswith(ASSETS):
        return None
    if (q + '/').startswith(INST + '/'):
        return 'instance-run-dir'
    return 'tmp' if q == '/tmp' or q.startswith('/tmp/') else 'host'


# 绝对路径记号：前面是空白、引号、=、(、;、|、&、>、`（不含 <，避免把 HTML 结束标签 </h1> 当路径）
ABS_TOK = re.compile(r'''(?:^|(?<=[\s"'=(;|&>`]))(/[^\s"';|&<>()`]*)''')
# 单独的 /（根目录）只在常见读目录命令的参数位置算数，避免 echo "a / b" 之类误报
ROOT_ARG = re.compile(r'''(?:^|[\s;|&(`])(?:ls|find|cd|du|tree|stat|cat|grep|rg|fd|locate|mdfind)(?:\s+-\S+)*\s+/(?=$|[\s;|&)`])''')
PARENT_TOK = re.compile(r'''(?:^|(?<=[\s"'=(;|&<>`/]))\.\.(?=$|[/\s"';|&)<>`])''')
HOME_TOK = re.compile(r'''(?:^|(?<=[\s"'=(;|&<>`]))~(?=$|[/\s"';|&)<>`])|\$\{?HOME\b''')


SHAPES = []  # 本实例目录内（workspace 以外）的路径形状：实例根换成 <inst>、会话 id 换成 *；host、home 类不记任何路径


def shape(tok):
    q = norm(tok).replace(INST, '<inst>')
    q = re.sub(r'mvs_[0-9a-f]+', 'mvs_*', q)
    q = re.sub(r'session_[A-Za-z0-9_-]+', 'session_*', q)
    return q[:160]


def scan_text(s):
    cats = set()
    for m in ABS_TOK.finditer(s):
        tok = m.group(1)
        if tok.startswith('//') or tok == '/':
            continue
        c = classify_abs(tok)
        if c:
            cats.add(c)
            if c == 'instance-run-dir':
                SHAPES.append(shape(tok))
    if ROOT_ARG.search(s):
        cats.add('host')
    if PARENT_TOK.search(s.replace('../workspace', '')):
        cats.add('parent-ref')
        depth = 5 if KIND == 'electron' else 2
        if any(m.group(0).count('..') >= depth for m in PARENT_RUN.finditer(s)):
            cats.add('parent-escape')
    if HOME_TOK.search(s):
        cats.add('home-ref')
    return cats


def scan_tool(name, inp):
    n = (name or '').lower()
    if n not in FILE_TOOLS:
        return set()
    cats = set()
    if not isinstance(inp, dict):
        return cats
    if n in ('bash', 'shell'):
        for k in ('command', 'cmd', 'script'):
            if isinstance(inp.get(k), str):
                cats |= scan_text(inp[k])
    for k in PATH_KEYS:
        v = inp.get(k)
        vals = v if isinstance(v, list) else [v]
        for x in vals:
            if isinstance(x, str) and x:
                if x.startswith('/') or x.startswith('~') or x.startswith('..') or '$HOME' in x:
                    cats |= scan_text(x)
    if n == 'apply_patch':
        for k in ('patch', 'input', 'patchText'):
            if isinstance(inp.get(k), str):
                for m in re.finditer(r'^\*\*\* (?:Add|Update|Delete) File: (.+)$', inp[k], re.M):
                    x = m.group(1).strip()
                    if x.startswith('/') or x.startswith('~') or x.startswith('..'):
                        cats |= scan_text(x)
    return cats


# workspace 外写入（kill-host 模式下即使只在实例目录内也停实例，owner 2026-10-02 口径）：
# 写类工具（write、edit、multiedit、apply_patch）的路径在 workspace 外；或 bash 的某一段同时有写操作和 workspace 外的路径记号
# （重定向目标在外、rm/mv/cp/tee/touch/mkdir/ln/chmod/truncate/sed -i/dd of=、sqlite3 的写语句、python/node 写文件）。
WRITE_TOOLS = {'write', 'edit', 'multiedit', 'apply_patch'}
SEG_SPLIT = re.compile(r'\|\||&&|;|\||\n')
WRITE_VERB = re.compile(r'''(?:^|[\s(`])(?:rm|mv|cp|tee|touch|mkdir|ln|chmod|chown|truncate|install|rsync)\b|sed\s+(?:-\S*\s+)*-i|\bdd\b[^|;]*\bof=|'''
                        r'''\b(?:INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|REPLACE)\b|open\([^)]*,\s*['"][wa]|write_text|writeFileSync|appendFileSync''', re.I)
REDIR_SEG = re.compile(r'''(?<![0-9&<>-])>{1,2}\s*([^\s;|&<>()`]+)''')


def outside_write(name, inp):
    n = (name or '').lower()
    if not isinstance(inp, dict):
        return False
    if n in WRITE_TOOLS:
        return bool(scan_tool('write', inp))
    if n not in ('bash', 'shell'):
        return False
    cmd = next((inp[k] for k in ('command', 'cmd', 'script') if isinstance(inp.get(k), str)), '')
    for seg in SEG_SPLIT.split(cmd):
        for t in REDIR_SEG.findall(seg):
            if t in DEV_OK or t.startswith('&'):
                continue
            if (t.startswith('/') and classify_abs(t)) or t.startswith('~') or '$HOME' in t or t.startswith('..'):
                return True
        if WRITE_VERB.search(seg) and scan_text(seg):
            return True
    return False


def main():
    global KIND, WS_RE
    inst, rid, out, mode = sys.argv[1:5]
    max_s = int(sys.argv[5]) if len(sys.argv) > 5 else 3600
    set_instance(inst)
    try:
        KIND = json.load(open(os.path.join(inst, 'state.json'))).get('kind') or 'electron'
    except Exception:
        KIND = 'electron'
    if KIND in ('runtime', 'tui'):  # 接口、TUI 实例的工作目录是 <实例>/workspace
        WS_RE = re.compile(r'(?:' + WS_RE.pattern + r')|(?:' + re.escape(INST) + r'/workspace(?:/|$))')
    seen = set()
    started = time.time()
    killed = False
    inc_path = os.path.join(out, 'ws-incident.jsonl')
    while time.time() - started < max_s:
        if os.path.exists(os.path.join(out, 'down.json')) or os.path.exists(os.path.join(out, 'guard-stop')) or not os.path.isdir(inst):
            break
        for d in glob.glob(os.path.join(inst, 'data', 'v2', 'sessions', '**', 'llm-context-inspector'), recursive=True):
            ev = os.path.join(d, 'events.jsonl')
            if not os.path.exists(ev):
                continue
            try:
                lines = open(ev, errors='replace').read().splitlines()
            except Exception:
                continue
            for line in lines:
                try:
                    e = json.loads(line)
                except Exception:
                    continue
                if e.get('type') != 'call.captured' or e.get('callId') in seen:
                    continue
                cid = base64.b64encode(e['callId'].encode()).decode()
                rp = os.path.join(d, 'payloads', f'{cid}.response.json')
                if not os.path.exists(rp):
                    continue
                try:
                    resp = json.load(open(rp))
                except Exception:
                    continue  # 还没写完，下一轮再读
                seen.add(e['callId'])
                for b in resp.get('content') or []:
                    if b.get('type') != 'tool_use':
                        continue
                    del SHAPES[:]
                    cats = scan_tool(b.get('name'), b.get('input'))
                    if not cats:
                        continue
                    wr = outside_write(b.get('name'), b.get('input'))
                    rec = {'detectedAtMs': int(time.time() * 1000), 'runId': rid, 'callId': e['callId'], 'turnId': e.get('turnId'),
                           'callStartedAtMs': e.get('startedAtMs'), 'callDurationMs': e.get('durationMs'), 'tool': b.get('name'),
                           'categories': sorted(cats), 'outsideWrite': wr, 'sessionDir': os.path.basename(os.path.dirname(d))[-60:],
                           'instancePathShapes': sorted(set(SHAPES))[:8], 'rawTextIncluded': False, 'mode': mode}
                    with open(inc_path, 'a') as fh:
                        fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
                    print(json.dumps(rec, ensure_ascii=False), flush=True)
                    if (mode == 'kill' or (mode == 'kill-host' and (cats & HOST_CATS or wr))) and not killed:
                        killed = True
                        open(os.path.join(out, 'guard-killed'), 'w').write(str(int(time.time() * 1000)) + '\n')
                        r = subprocess.run(['node', V] + DOWN_CMD.get(KIND, ['electron', 'down']) + ['--run', rid], capture_output=True, text=True, timeout=180)
                        open(os.path.join(out, 'guard-down.json'), 'w').write(r.stdout)
                        with open(os.path.join(out, 'guard-killed'), 'a') as fh:
                            fh.write(f'down rc={r.returncode} at {int(time.time() * 1000)}\n')
        if killed:
            break
        time.sleep(0.3)


if __name__ == '__main__':
    main()
