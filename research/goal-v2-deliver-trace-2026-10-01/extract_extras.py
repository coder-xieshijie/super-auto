#!/usr/bin/env python3
"""从 Claude Code 会话 JSONL 提取时间线以外的人工介入数据。

用法: extract_extras.py <session.jsonl> <输出.md> [--subagents <dir>]

输出五部分：
1. 进入会话的消息（用户输入、其他会话的消息、中途吸收的消息），取自 queue-operation 与 user 记录；
2. AskUserQuestion 的问题、选项与答复；
3. 被拒绝或被中断的工具调用；
4. 主会话超过 5 分钟没有任何记录的空档；
5. subagent 中等待超过 5 分钟的单次工具调用（多为审批或长命令），以及按说明归类的 subagent 用量。
只读原始记录；正文做截断，不含 thinking。
"""
import json, sys, os, datetime, collections

TZ = datetime.timezone(datetime.timedelta(hours=8))


def ts(s):
    return datetime.datetime.fromisoformat(s.replace('Z', '+00:00')).astimezone(TZ)


def load(path):
    rows = []
    for line in open(path, encoding='utf-8'):
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return ' '.join(x.get('text', '') for x in content if isinstance(x, dict))
    return str(content)


def one_line(s, n):
    s = ' '.join((s or '').split())
    return s if len(s) <= n else s[:n] + '…'


CATS = [
    ('里程碑检查', 'milestone check'), ('证据核对', 'evidence check'), ('代码审查', 'review '),
    ('场景运行', 'run m'), ('场景运行', 'rerun m'), ('场景运行', 'rg1'), ('场景运行', 'm1 smoke'),
    ('场景运行', 'm1 rerun'), ('探索', 'map '), ('探索', 'summarize'), ('探索', 'research'),
    ('实现', 'implement'), ('实现', 'build verify'), ('实现', 'desktop and tui'), ('实现', 'fix knip'),
    ('测试', 'port '), ('测试', 'fix v2'), ('测试', 'clean v1'), ('测试', 'update goal tests'),
    ('整合', 'integrate'), ('整合', 'split m2'), ('文档', 'draft m5'),
]


def main():
    path, out = sys.argv[1], sys.argv[2]
    sub_dir = sys.argv[sys.argv.index('--subagents') + 1] if '--subagents' in sys.argv else None
    rows = load(path)
    L = [f'# 人工介入与等待数据：{os.path.basename(path)}\n']

    # 1. 进入会话的消息
    L.append('## 1. 进入会话的消息\n')
    L.append('| 时间 | 操作 | 内容（截断） |')
    L.append('|---|---|---|')
    for d in rows:
        if d.get('type') != 'queue-operation':
            continue
        c = str(d.get('content', ''))
        if not c or 'task-notification' in c[:300] or d['operation'] == 'dequeue':
            continue
        op = d['operation'] + (f"（{d['reason']}）" if d.get('reason') else '')
        L.append(f"| {ts(d['timestamp']):%m-%d %H:%M:%S} | {op} | {one_line(c, 160).replace('|', '/')} |")

    # 2. AskUserQuestion
    L.append('\n## 2. AskUserQuestion\n')
    asks = {}
    for d in rows:
        if d.get('isSidechain'):
            continue
        if d.get('type') == 'assistant':
            for c in d['message'].get('content', []):
                if c.get('type') == 'tool_use' and c['name'] == 'AskUserQuestion':
                    asks[c['id']] = (d['timestamp'], c['input'])
        elif d.get('type') == 'user' and isinstance(d['message']['content'], list):
            for x in d['message']['content']:
                if x.get('type') == 'tool_result' and x.get('tool_use_id') in asks:
                    t0, inp = asks[x['tool_use_id']]
                    wait = (ts(d['timestamp']) - ts(t0)).total_seconds() / 60
                    L.append(f"### {ts(t0):%m-%d %H:%M:%S} → {ts(d['timestamp']):%H:%M:%S}（等待 {wait:.1f} 分钟）\n")
                    for q in inp.get('questions', []):
                        L.append(f"- 问：{q['question']}")
                        for o in q.get('options', []):
                            L.append(f"  - {o['label']}：{one_line(o.get('description', ''), 200)}")
                    L.append(f"- 答：{one_line(text_of(x.get('content')), 600)}\n")

    # 3. 被拒绝或被中断的工具调用
    L.append('## 3. 被拒绝或被中断的工具调用\n')
    for d in rows:
        if d.get('isSidechain') or d.get('type') != 'user' or not isinstance(d['message']['content'], list):
            continue
        for x in d['message']['content']:
            t = text_of(x.get('content')) if x.get('type') == 'tool_result' else x.get('text', '')
            if "doesn't want to proceed" in t or 'Request interrupted' in t:
                L.append(f"- {ts(d['timestamp']):%m-%d %H:%M:%S}：{one_line(t, 220)}")

    # 4. 主会话空档
    L.append('\n## 4. 主会话超过 5 分钟的空档\n')
    evs = sorted(ts(d['timestamp']) for d in rows
                 if d.get('timestamp') and not d.get('isSidechain') and d.get('type') in ('assistant', 'user', 'system'))
    total = 0
    for a, b in zip(evs, evs[1:]):
        g = (b - a).total_seconds()
        if g > 300:
            total += g
            L.append(f'- {a:%m-%d %H:%M:%S} → {b:%m-%d %H:%M:%S}（{g / 60:.1f} 分钟）')
    if evs:
        span = (evs[-1] - evs[0]).total_seconds()
        L.append(f'\n合计 {total / 3600:.2f} 小时；会话跨度 {span / 3600:.2f} 小时。')

    # 5. subagent
    if sub_dir and os.path.isdir(sub_dir):
        L.append('\n## 5. subagent\n')
        agg = collections.defaultdict(collections.Counter)
        waits = []
        spans = []
        for fn in sorted(os.listdir(sub_dir)):
            if not fn.endswith('.jsonl'):
                continue
            mp = os.path.join(sub_dir, fn.replace('.jsonl', '.meta.json'))
            desc = json.load(open(mp)).get('description', '') if os.path.exists(mp) else ''
            cat = next((c for c, k in CATS if k in desc.lower()), '其他')
            srows = load(os.path.join(sub_dir, fn))
            times = [ts(r['timestamp']) for r in srows if r.get('timestamp')]
            if not times:
                continue
            spans.append((min(times), max(times)))
            ids = set()
            pend = {}
            for r in srows:
                if r.get('type') == 'assistant':
                    m = r['message']
                    if m.get('id') not in ids:
                        ids.add(m.get('id'))
                        u = m.get('usage') or {}
                        agg[cat]['output'] += u.get('output_tokens') or 0
                        agg[cat]['cache_read'] += u.get('cache_read_input_tokens') or 0
                    for c in m.get('content', []):
                        if c.get('type') == 'tool_use':
                            inp = c.get('input') if isinstance(c.get('input'), dict) else {}
                            pend[c['id']] = (r['timestamp'], inp.get('command') or inp.get('description') or c['name'])
                elif r.get('type') == 'user' and isinstance(r['message']['content'], list):
                    for x in r['message']['content']:
                        if x.get('type') == 'tool_result' and x.get('tool_use_id') in pend:
                            t0, cmd = pend.pop(x['tool_use_id'])
                            g = (ts(r['timestamp']) - ts(t0)).total_seconds()
                            if g > 300:
                                waits.append((ts(t0), g, desc, cmd))
            agg[cat]['n'] += 1
            agg[cat]['sec'] += (max(times) - min(times)).total_seconds()
        L.append('| 类别 | 个数 | 时长合计（小时） | output token | cache read（百万） |')
        L.append('|---|---|---|---|---|')
        for c, v in sorted(agg.items(), key=lambda kv: -kv[1]['sec']):
            L.append(f"| {c} | {v['n']} | {v['sec'] / 3600:.2f} | {v['output']:,} | {v['cache_read'] / 1e6:.1f} |")
        ev = sorted([(a, 1) for a, _ in spans] + [(b, -1) for _, b in spans])
        cur = peak = 0
        for _, k in ev:
            cur += k
            peak = max(peak, cur)
        L.append(f'\n最多同时运行 {peak} 个。\n')
        L.append('单次工具调用等待超过 5 分钟（命令截断到 160 字）：\n')
        for t0, g, desc, cmd in sorted(waits):
            L.append(f'- {t0:%m-%d %H:%M:%S}，{g / 60:.1f} 分钟，{desc}：`{one_line(cmd, 160)}`')

    open(out, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print(out, len(L))


if __name__ == '__main__':
    main()
