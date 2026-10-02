#!/usr/bin/env python3
"""Bounded Claude trace projection: UUID deduplication, no thinking/attachments.

Public conversation projections stay under ignored local/; committed timelines
contain shortened public messages/tool descriptions and raw source line IDs.
Usage is max-per-field across fragments of each message.id, not billed cost.
"""
import collections
import datetime as dt
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
TZ = dt.timezone(dt.timedelta(hours=8))
BASE = Path.home() / '.claude/projects'
SOURCES = {
    'definition': BASE / '-Users-minimax--claude-worktree-agent-archon-eager-leavitt-d0d8db/a6b48431-9771-482d-9b95-49964a4cee08.jsonl',
    'deliver': BASE / '-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5.jsonl',
}


def clean(s):
    s = str(s)
    s = re.sub(r'(?i)(bearer\s+)[\w.\-+/=]{12,}', r'\1[REDACTED]', s)
    s = re.sub(r'\b(?:sk-[A-Za-z0-9_-]{16,}|glpat-[A-Za-z0-9_-]+|gh[pousr]_[A-Za-z0-9_]{20,})\b', '[REDACTED]', s)
    s = re.sub(r'eyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]+', '[REDACTED_JWT]', s)
    return s


def stamp(s):
    return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).astimezone(TZ)


def short(s, n=260):
    s = re.sub(r'\s+', ' ', clean(s)).strip().replace('|', ' / ')
    return s if len(s) <= n else s[:n] + '…'


def extract(path, key):
    raw = path.read_bytes()
    seen = set()
    rows = []
    duplicate = 0
    errors = []
    for lineno, line in enumerate(raw.splitlines(), 1):
        try:
            row = json.loads(line)
        except (ValueError, UnicodeError):
            errors.append(lineno)
            continue
        uid = row.get('uuid')
        if uid and uid in seen:
            duplicate += 1
            continue
        if uid:
            seen.add(uid)
        rows.append((lineno, row))
    events = []
    usage = {}
    model_by_message = {}
    tool_ids = set()
    tools = collections.Counter()
    types = collections.Counter()
    for ln, r in rows:
        ty = r.get('type')
        types[ty] += 1
        timestamp = r.get('timestamp')
        if not timestamp:
            continue
        msg = r.get('message') or {}
        content = msg.get('content') or []
        ev = dict(source_line=ln, uuid=r.get('uuid'), timestamp=timestamp,
                  time_local=stamp(timestamp).isoformat(), record_type=ty)
        if ty == 'assistant':
            mid = msg.get('id')
            if mid:
                model_by_message[mid] = msg.get('model')
                u = usage.setdefault(mid, {})
                for k, v in (msg.get('usage') or {}).items():
                    if isinstance(v, int):
                        u[k] = max(u.get(k, 0), v)
            for part in content if isinstance(content, list) else []:
                if part.get('type') == 'text' and part.get('text'):
                    events.append(dict(ev, kind='assistant', text=clean(part['text'])))
                elif part.get('type') == 'tool_use' and part['id'] not in tool_ids:
                    tool_ids.add(part['id'])
                    name = part['name']
                    tools[name] += 1
                    inp = part.get('input') or {}
                    desc = inp.get('description') or inp.get('file_path') or inp.get('command') or inp.get('message') or inp.get('prompt') or json.dumps(inp, ensure_ascii=False)
                    events.append(dict(ev, kind='tool', name=name, tool_id=part['id'],
                                       text=clean(desc), input=clean(json.dumps(inp, ensure_ascii=False))))
        elif ty == 'user':
            if isinstance(content, str):
                content = [dict(type='text', text=content)]
            for part in content:
                if not isinstance(part, dict):
                    continue
                if part.get('type') == 'text':
                    origin = (r.get('origin') or {}).get('kind') or r.get('turnOrigin')
                    events.append(dict(ev, kind='user_text', origin=origin,
                                       is_meta=r.get('isMeta', False), text=clean(part.get('text', ''))))
                elif part.get('type') == 'tool_result':
                    c = part.get('content', '')
                    if isinstance(c, list):
                        c = '\n'.join(x.get('text', '') for x in c if isinstance(x, dict) and x.get('type') == 'text')
                    events.append(dict(ev, kind='tool_result', tool_id=part.get('tool_use_id'),
                                       is_error=part.get('is_error', False), text=clean(c)))
        elif ty == 'queue-operation' and r.get('content') and r.get('operation') != 'dequeue':
            events.append(dict(ev, kind='queue', operation=r.get('operation'), reason=r.get('reason'),
                               text=clean(r['content'])))
        elif ty == 'system' and r.get('subtype') in ('compact_boundary', 'api_error'):
            data = {k: r[k] for k in ('subtype', 'error') if k in r}
            if r.get('compactMetadata'):
                data['compactMetadata'] = {k: v for k, v in r['compactMetadata'].items()
                                           if k in ('trigger', 'preTokens', 'postTokens', 'durationMs', 'cumulativeDroppedTokens')}
            events.append(dict(ev, kind='system', text=clean(json.dumps(data, ensure_ascii=False))))
    events.sort(key=lambda x: (x['timestamp'], x['source_line']))
    sums = collections.Counter()
    for u in usage.values():
        sums.update(u)
    times = [x['timestamp'] for x in events]
    manifest = dict(key=key, path=str(path), sha256=hashlib.sha256(raw).hexdigest(),
                    bytes=len(raw), lines=len(raw.splitlines()), duplicate_uuid_rows=duplicate,
                    parse_error_lines=errors, first=min(times) if times else None,
                    last=max(times) if times else None, unique_model_message_ids=len(usage),
                    usage_max_per_message=dict(sums), tools=dict(tools), unique_record_types=dict(types))
    manifest['models_by_unique_message'] = dict(collections.Counter(model_by_message.values()))
    return events, manifest


def main():
    (ROOT / 'local').mkdir(exist_ok=True)
    (ROOT / 'timelines').mkdir(exist_ok=True)
    manifests = []
    for key, path in SOURCES.items():
        events, manifest = extract(path, key)
        manifests.append(manifest)
        (ROOT / 'local' / f'{key}.jsonl').write_text(''.join(json.dumps(e, ensure_ascii=False) + '\n' for e in events))
        lines = [f'# {key} 全窗口时间线', '', f'原始来源：`{path}`。', '',
                 f'去重后 {len(events)} 个公开事件；以 UUID 去除 {manifest["duplicate_uuid_rows"]} 条重放记录。',
                 '下列工具描述与公开消息为截断导航；工具结果全文在本机 local 投影，不含 thinking、附件、签名。',
                 'L 为原始 JSONL 行号；同一行可含多个 content。时间均为 Asia/Shanghai。queue 保留投递/中途吸收，不等于新增人类决定；消息去重口径见 interventions.md。', '',
                 '| 时间 | 类型 | 原始行 / UUID | 内容 |', '|---|---|---|---|']
        for e in events:
            if e['kind'] == 'tool_result':
                continue
            if e.get('is_meta'):
                continue
            # Skill and task notifications are retained but are not human inputs.
            label = e['kind'] + (':' + e['name'] if e.get('name') else '')
            if e['kind'] == 'queue':
                label += ':' + str(e.get('operation')) + '/' + str(e.get('reason') or '')
            lines.append(f'| {stamp(e["timestamp"]):%m-%d %H:%M:%S} | {label} | L{e["source_line"]} / {e.get("uuid") or "—"} | {short(e["text"], 650 if e["kind"] == "assistant" else 280)} |')
        (ROOT / 'timelines' / f'{key}.md').write_text('\n'.join(lines) + '\n')
        for child in sorted(path.with_suffix('').joinpath('subagents').glob('*.jsonl')):
            ce, cm = extract(child, f'{key}/{child.stem}')
            meta = child.with_suffix('.meta.json')
            cm['description'] = json.loads(meta.read_text()).get('description') if meta.exists() else None
            manifests.append(cm)
            (ROOT / 'local' / f'{key}-{child.stem}.jsonl').write_text(''.join(json.dumps(e, ensure_ascii=False) + '\n' for e in ce))
    (ROOT / 'manifest.json').write_text(json.dumps(dict(captured_at=dt.datetime.now(TZ).isoformat(),
        scope='Two named main sessions and all their local subagents. No thinking or attachments.',
        metrics_note='Usage: maxima per unique message.id. Spans overlap and are not additive wall-clock costs.', files=manifests), ensure_ascii=False, indent=2) + '\n')
    lines = ['# 会话与子代理清单', '', '源文件 SHA-256、字节数、去重数据与用量详见 [manifest.json](manifest.json)。主会话不等于所有 Claude 活动；旁路会话见主报告。', '',
             '| 会话 | 任务 | 起止（北京时间） | 原始行数 | 去重行 | 唯一模型消息 | 工具调用 |', '|---|---|---|---|---|---|---|']
    for m in manifests:
        lines.append(f'| {m["key"]} | {short(m.get("description") or "主会话",100)} | {stamp(m["first"]):%m-%d %H:%M:%S}–{stamp(m["last"]):%m-%d %H:%M:%S} | {m["lines"]} | {m["duplicate_uuid_rows"]} | {m["unique_model_message_ids"]} | {sum(m["tools"].values())} |')
    (ROOT / 'sessions.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps(dict(files=len(manifests), main=[x for x in manifests if '/' not in x['key']]),ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
