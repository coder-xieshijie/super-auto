#!/usr/bin/env python3
"""从 Claude Code 会话 JSONL 提取时间线与指标。

用法: extract_trace.py <session.jsonl> <输出.md> [--subagents <dir>]
只读原始记录；输出里的助手正文和工具输入做截断，不含 thinking 与签名。
"""
import json, sys, os, re, datetime, collections

TZ = datetime.timezone(datetime.timedelta(hours=8))

def ts(s):
    return datetime.datetime.fromisoformat(s.replace('Z', '+00:00')).astimezone(TZ)

def short(s, n):
    s = re.sub(r'\s+', ' ', s or '').strip()
    return s if len(s) <= n else s[:n] + '…'

def load(path):
    rows = []
    for line in open(path, encoding='utf-8'):
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows

def human_text(d):
    c = d['message']['content']
    if isinstance(c, str):
        return c
    parts = []
    for p in c:
        if p.get('type') == 'text':
            parts.append(p['text'])
    return '\n'.join(parts)

def is_human(d):
    if d.get('type') != 'user':
        return False
    if d.get('isMeta') or d.get('isSidechain'):
        return False
    o = d.get('origin') or {}
    if o.get('kind') == 'human' or d.get('turnOrigin') == 'human':
        c = d['message']['content']
        if isinstance(c, list) and any(p.get('type') == 'tool_result' for p in c):
            return False
        return True
    return False

def summarize(path, sub_dir=None):
    rows = load(path)
    ev = []  # (time, kind, text)
    usage = collections.Counter()
    tools = collections.Counter()
    seen_msg = set()
    first = last = None
    for d in rows:
        t = d.get('timestamp')
        if not t:
            continue
        tt = ts(t)
        first = first or tt
        last = tt
        if d.get('isSidechain'):
            continue
        if is_human(d):
            txt = human_text(d)
            kind = 'human'
            o = d.get('origin') or {}
            ev.append((tt, 'USER', txt))
        elif d.get('type') == 'user':
            c = d['message']['content']
            if isinstance(c, str) and 'cross-session' in c:
                ev.append((tt, 'XMSG', c))
            elif isinstance(c, list):
                for p in c:
                    if p.get('type') == 'text' and ('<cross-session-message' in p.get('text', '') or 'task-notification' in p.get('text', '')):
                        ev.append((tt, 'NOTIFY', p['text']))
        elif d.get('type') == 'assistant':
            m = d['message']
            mid = m.get('id')
            if mid and mid not in seen_msg:
                seen_msg.add(mid)
                u = m.get('usage') or {}
                for k in ('input_tokens', 'output_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens'):
                    usage[k] += u.get(k) or 0
                usage['api_calls'] += 1
            for p in m.get('content', []):
                if p.get('type') == 'text' and p.get('text', '').strip():
                    ev.append((tt, 'ASSISTANT', p['text']))
                elif p.get('type') == 'tool_use':
                    name = p['name']
                    tools[name] += 1
                    inp = p.get('input') or {}
                    desc = inp.get('description') or inp.get('command') or inp.get('file_path') or inp.get('prompt') or inp.get('message') or json.dumps(inp, ensure_ascii=False)
                    ev.append((tt, 'TOOL', f'{name}: {desc}'))
    # subagents
    subs = []
    if sub_dir and os.path.isdir(sub_dir):
        for fn in sorted(os.listdir(sub_dir)):
            if not fn.endswith('.jsonl'):
                continue
            meta = {}
            mp = os.path.join(sub_dir, fn.replace('.jsonl', '.meta.json'))
            if os.path.exists(mp):
                meta = json.load(open(mp))
            srows = load(os.path.join(sub_dir, fn))
            times = [ts(r['timestamp']) for r in srows if r.get('timestamp')]
            su = collections.Counter(); sids = set(); stools = collections.Counter()
            for r in srows:
                if r.get('type') == 'assistant':
                    m = r['message']
                    if m.get('id') not in sids:
                        sids.add(m.get('id'))
                        u = m.get('usage') or {}
                        for k in ('input_tokens', 'output_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens'):
                            su[k] += u.get(k) or 0
                    for p in m.get('content', []):
                        if p.get('type') == 'tool_use':
                            stools[p['name']] += 1
            model = next((r['message'].get('model') for r in srows if r.get('type') == 'assistant'), None)
            subs.append(dict(file=fn, meta=meta, start=min(times) if times else None, end=max(times) if times else None, usage=su, tools=stools, model=model))
    return dict(ev=ev, usage=usage, tools=tools, first=first, last=last, subs=subs)

def fmt_dur(sec):
    sec = int(sec)
    h, r = divmod(sec, 3600); m, s = divmod(r, 60)
    return f'{h}h{m:02d}m' if h else f'{m}m{s:02d}s'

def main():
    path, out = sys.argv[1], sys.argv[2]
    sub_dir = None
    if '--subagents' in sys.argv:
        sub_dir = sys.argv[sys.argv.index('--subagents') + 1]
    r = summarize(path, sub_dir)
    ev = r['ev']
    # user wait: gap between last assistant/tool event before a USER event and the USER event
    waits = []
    prev = None
    for t, k, x in ev:
        if k == 'USER' and prev is not None:
            waits.append((prev, t, (t - prev).total_seconds()))
        prev = t
    lines = []
    lines.append(f'# 时间线：{os.path.basename(path)}\n')
    lines.append(f'- 起止（Asia/Shanghai）：{r["first"]:%Y-%m-%d %H:%M:%S} – {r["last"]:%H:%M:%S}，跨度 {fmt_dur((r["last"]-r["first"]).total_seconds())}')
    nuser = sum(1 for e in ev if e[1] == 'USER')
    lines.append(f'- 用户输入 {nuser} 次；API 调用 {r["usage"]["api_calls"]} 次')
    u = r['usage']
    lines.append(f'- token：input {u["input_tokens"]:,}，cache_creation {u["cache_creation_input_tokens"]:,}，cache_read {u["cache_read_input_tokens"]:,}，output {u["output_tokens"]:,}')
    lines.append('- 工具调用：' + '，'.join(f'{k} {v}' for k, v in r['tools'].most_common()))
    tw = sum(w for _, _, w in waits[1:])
    lines.append(f'- 用户输入前的空档合计（不含首条）：{fmt_dur(tw)}；超过 2 分钟的空档：')
    for a, b, w in waits[1:]:
        if w > 120:
            lines.append(f'  - {a:%H:%M:%S} → {b:%H:%M:%S}（{fmt_dur(w)}）')
    if r['subs']:
        lines.append('\n## subagent\n')
        lines.append('| 文件 | 说明 | 模型 | 起止 | 时长 | output tokens | 工具调用 |')
        lines.append('|---|---|---|---|---|---|---|')
        for s in r['subs']:
            desc = s['meta'].get('description') or s['meta'].get('agentType') or ''
            dur = fmt_dur((s['end'] - s['start']).total_seconds()) if s['start'] else ''
            lines.append(f'| {s["file"]} | {short(desc, 60)} | {s["model"]} | {s["start"]:%H:%M:%S}–{s["end"]:%H:%M:%S} | {dur} | {s["usage"]["output_tokens"]:,} | {sum(s["tools"].values())} |')
    lines.append('\n## 事件\n')
    lines.append('USER 与 NOTIFY 全文；ASSISTANT 截断到 1500 字；TOOL 截断到 220 字。\n')
    for t, k, x in ev:
        if k == 'USER':
            body = x.strip()
            lines.append(f'\n### {t:%H:%M:%S} USER\n')
            lines.append('\n'.join('> ' + l for l in body.splitlines()))
            lines.append('')
        elif k == 'NOTIFY' or k == 'XMSG':
            lines.append(f'\n**{t:%H:%M:%S} {k}**：{short(x, 1500)}\n')
        elif k == 'ASSISTANT':
            lines.append(f'\n**{t:%H:%M:%S} ASSISTANT**：{short(x, 1500)}\n')
        else:
            lines.append(f'- {t:%H:%M:%S} {short(x, 220)}')
    open(out, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print(out, len(lines))

if __name__ == '__main__':
    main()
