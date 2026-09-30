#!/usr/bin/env python3
"""RG1 汇总：从证据树生成 summary.json 和 summary.md 的表格部分。

用法：rg1-summarize.py <证据根> [--tag rg1base] [--notes notes.json]

证据树由 rg1-api.sh / rg1-tui.sh / rg1-electron.sh 产生：<根>/<功能>/<子功能>/<入口>/。每条记录取该目录最后一个
snapshot：接口与 Electron 的 Goal 状态读 snapshot 里的 GET .../goal；TUI 没有接口，状态取屏幕最下方的
`◎ Goal · …` 横幅（没有横幅时看最后出现的 `✓ Goal complete` / `Goal cleared`），status_reason 取 runtime 事件里
同一 Goal 最近的原因。runtime 事件只取 goal.* 的类型和枚举字段，Goal 按出现顺序记为 g1、g2…；默认取本子功能的
窗口（与同一会话上一个 snapshot 的差集），完成类观察取整个会话。matches_map 由下面按功能地图写的检查得出。
--notes 指向人工补充的说明（{"<功能>/<子功能>/<入口>": ["…"]}），追加到 notes。
"""
import argparse
import glob
import json
import os
import re

ENUM_KEYS = ['phase', 'decision', 'reason', 'from', 'to', 'status', 'backend', 'source', 'verdict',
             'disposition', 'proposal', 'resultStatus', 'statusReason']
TERMINAL = {'complete', 'paused', 'blocked', 'budget_limited', 'usage_limited'}

# (功能, 子功能, 入口, 中文名, 事件范围)；范围 session = 整个会话到该 snapshot，window = 与上一个 snapshot 的差集
RECORDS = [
    ('lifecycle', 'create', 'api', '创建', 'window'),
    ('lifecycle', 'pause', 'api', '暂停', 'window'),
    ('lifecycle', 'edit-paused', 'api', '暂停时修改目标', 'window'),
    ('lifecycle', 'still-paused', 'api', '确认暂停期间不会自行继续', 'window'),
    ('lifecycle', 'resume', 'api', '恢复', 'window'),
    ('lifecycle', 'complete', 'api', '跑到终态', 'window'),
    ('lifecycle', 'replace', 'api', '替换已完成的 Goal', 'window'),
    ('lifecycle', 'clear', 'api', '清除', 'window'),
    ('lifecycle', 'create', 'tui', '创建', 'window'),
    ('lifecycle', 'pause', 'tui', '暂停', 'window'),
    ('lifecycle', 'summary', 'tui', '查看摘要', 'window'),
    ('lifecycle', 'edit-paused', 'tui', '暂停时改目标', 'window'),
    ('lifecycle', 'resume', 'tui', '恢复', 'window'),
    ('lifecycle', 'complete', 'tui', '完成', 'window'),
    ('lifecycle', 'replace', 'tui', '完成后替换', 'window'),
    ('lifecycle', 'clear', 'tui', '清除', 'window'),
    ('lifecycle', 'create', 'electron', '创建', 'window'),
    ('lifecycle', 'auth-card', 'electron', '授权卡片', 'session'),
    ('lifecycle', 'complete', 'electron', '完成', 'window'),
    ('lifecycle', 'pause', 'electron', '暂停', 'window'),
    ('lifecycle', 'resume', 'electron', '继续', 'window'),
    ('lifecycle', 'edit-replace', 'electron', '编辑（替换确认）', 'window'),
    ('lifecycle', 'clear', 'electron', '清除', 'window'),
    ('continuation', 'background', 'api', '后台续跑', 'window'),
    ('continuation', 'queue-while-waiting', 'api', '等待时插入用户消息', 'window'),
    ('continuation', 'background', 'tui', '后台续跑', 'window'),
    ('continuation', 'background', 'electron', '后台续跑', 'window'),
    ('completion', 'complete', 'api', '完成（验证通过、验证过程）', 'session'),
    ('completion', 'no-continuation', 'api', '完成后不续跑', 'window'),
    ('completion', 'replace', 'api', '完成后设定新 Goal', 'window'),
    ('completion', 'final-reply', 'api', '最终回复的运行顺序', 'session'),
    ('completion', 'complete', 'tui', '完成', 'session'),
    ('completion', 'final-reply', 'tui', '最终回复', 'session'),
    ('completion', 'complete', 'electron', '完成', 'session'),
    ('completion', 'verify-auth-card', 'electron', '验证时的授权卡片', 'session'),
    ('completion', 'final-reply', 'electron', '最终回复与交付卡片', 'session'),
    ('completion', 'reload', 'electron', '重载', 'window'),
    ('limits', 'token-budget', 'api', 'token 预算', 'window'),
    ('limits', 'resume-rejected', 'api', '恢复被拒', 'window'),
    ('limits', 'raise-reopen', 'api', '提高预算重开（含只改预算不恢复）', 'window'),
    ('limits', 'timer', 'api', '计时', 'window'),
    ('limits', 'token-budget', 'tui', 'token 预算', 'window'),
    ('limits', 'resume-rejected', 'tui', '恢复无效（地图步骤，索引未单列）', 'window'),
    ('limits', 'clear', 'tui', '清除', 'window'),
    ('attachments', 'kickoff', 'api', '首轮附件', 'window'),
    ('attachments', 'kickoff', 'tui', '粘贴图片作为首轮附件', 'window'),
    ('attachments', 'failure-resume', 'tui', '失败后恢复', 'window'),
    ('attachments', 'kickoff', 'electron', '首页首轮附件', 'window'),
    ('attachments', 'objective-resources', 'electron', '会话内目标资源', 'window'),
    ('questionnaire', 'manual', 'api', '手动回答', 'window'),
    ('questionnaire', 'auto-timeout', 'api', '超时自动回答', 'window'),
    ('questionnaire', 'manual', 'tui', '手动回答', 'window'),
    ('questionnaire', 'auto-timeout', 'tui', '超时自动回答', 'window'),
    ('questionnaire', 'manual', 'electron', '手动回答', 'window'),
    ('questionnaire', 'auto-timeout', 'electron', '超时自动回答', 'window'),
]
FEATURE_CN = {'lifecycle': 'Goal 生命周期', 'continuation': 'Goal 持续执行', 'completion': 'Goal 完成与独立验证',
              'limits': 'Goal 预算与限额', 'attachments': 'Goal 附件与注释', 'questionnaire': 'Goal 问卷'}
ENTRY_CN = {'api': '接口', 'tui': 'TUI', 'electron': 'Electron'}


def load(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def read_events(path):
    out = []
    if not path or not os.path.exists(path):
        return out
    for line in open(path, errors='replace'):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        fields = d.get('fields') or {}
        etype = fields.get('eventType') or ''
        payload = fields.get('payload')
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except ValueError:
                payload = {}
        out.append({'line': line, 'ts': d.get('tsMs') or 0, 'type': etype, 'payload': payload or {}})
    out.sort(key=lambda e: e['ts'])
    return out


class Rec:
    def __init__(self, root, tag, feature, sub, entry, label, scope):
        self.root, self.tag, self.feature, self.sub, self.entry = root, tag, feature, sub, entry
        self.label, self.scope = label, scope
        self.key = f'{feature}/{sub}/{entry}'
        self.dir = os.path.join(root, feature, sub, entry)
        self.names = sorted(os.listdir(self.dir)) if os.path.isdir(self.dir) else []
        self.prefix = f'{tag}-{feature}.{sub}--'

    def path(self, step, ext='.json'):
        pat = re.compile(r'^\d{3}-' + re.escape(self.prefix + step) + re.escape(ext) + '$')
        found = [n for n in self.names if pat.match(n)]
        return os.path.join(self.dir, found[-1]) if found else None

    def j(self, step):
        p = self.path(step)
        return load(p) if p else None

    def has(self, step):
        return self.path(step) is not None

    def body(self, step):
        d = self.j(step)
        return ((d or {}).get('response') or {}).get('body')

    def code(self, step):
        d = self.j(step)
        return ((d or {}).get('response') or {}).get('status')

    def goal(self, step):
        b = self.body(step)
        return (b or {}).get('goal') if isinstance(b, dict) else None

    def final_goal(self, step):
        d = self.j(step)
        f = (d or {}).get('final')
        return (f or {}).get('goal') if isinstance(f, dict) else None

    def traj(self, step):
        return (self.j(step) or {}).get('trajectory') or []

    def result(self, step):
        return (self.j(step) or {}).get('result') or {}

    def screen(self, step):
        return ((self.j(step) or {}).get('screen') or {}).get('lines') or []

    def screen_status(self, step):
        return ((self.j(step) or {}).get('screen') or {}).get('status') or {}

    def snaps(self):
        pat = re.compile(r'^\d{3}-' + re.escape(self.prefix) + r'(?:[a-z0-9-]*-)?snap\.json$')
        return [os.path.join(self.dir, n) for n in self.names if pat.match(n)]

    def run_dir(self):
        info = load(os.path.join(self.dir, 'run.json')) or {}
        runs = info.get('runs') or []
        return (os.path.join(self.root, runs[-1]['instanceEvidenceDir']), runs[-1]['runId']) if runs else (None, None)


class Snap:
    def __init__(self, path):
        self.path = path
        self.stem = path[:-len('.json')]
        self.data = load(path) or {}
        self.session = self.data.get('sessionId')
        self.at = self.data.get('capturedAt') or 0
        self.events = read_events(self.stem + '-runtime-events.jsonl')

    def goal_body(self):
        http = self.data.get('http')
        if not http:
            return None
        return (http.get('goal') or {}).get('body')

    def messages(self):
        http = self.data.get('http') or {}
        return ((http.get('messages') or {}).get('body') or {}).get('messages') or []

    def screen(self):
        return (self.data.get('screen') or {}).get('lines') or []

    def files(self):
        listing = load(self.stem + '-workspace.json') or []
        out = []
        for item in listing:
            entry = {'path': item['path'], 'bytes': item['bytes']}
            if item['bytes'] < 4096:
                try:
                    with open(os.path.join(self.stem + '-workspace', item['path']), errors='replace') as fh:
                        entry['content'] = fh.read()
                except OSError:
                    pass
            out.append(entry)
        return sorted(out, key=lambda f: f['path'])

    def file_text(self, name):
        for f in self.files():
            if f['path'] == name:
                return f.get('content')
        return None

    def inspector_text(self):
        text = ''
        for p in glob.glob(self.stem + '-inspector/payloads/*.request.json'):
            try:
                text += open(p, errors='replace').read()
            except OSError:
                pass
        return text


def describe_events(events, ordinals):
    out = []
    for e in events:
        if not e['type'].startswith('goal.'):
            continue
        p = e['payload']
        gid = p.get('goalId')
        if gid and gid not in ordinals:
            ordinals[gid] = f'g{len(ordinals) + 1}'
        fields = ','.join(f'{k}={p[k]}' for k in ENUM_KEYS if k in p and isinstance(p[k], (str, int, bool)))
        out.append(e['type'] + (f'{{{fields}}}' if fields else '') + (f'@{ordinals[gid]}' if gid else ''))
    return out


def event_status(events):
    """Goal status/reason from goal.* events of the last goal (TUI has no HTTP view)."""
    status, reason, last_goal = None, None, None
    for e in events:
        p = e['payload']
        gid = p.get('goalId')
        if e['type'] == 'goal.created':
            status, reason, last_goal = 'active', None, gid
        elif gid and gid != last_goal:
            continue
        elif e['type'] == 'goal.state_transitioned':
            status, reason = p.get('to'), p.get('reason')
        elif e['type'] == 'goal.worker_proposal_decided' and p.get('resultStatus'):
            status, reason = p.get('resultStatus'), p.get('statusReason')
    return status, reason


BANNER = re.compile(r'◎ Goal · ([A-Za-z][A-Za-z ]*?)(?: ·|\s*$)')
BANNER_STATUS = {'Active': 'active', 'Paused': 'paused', 'Budget limited': 'budget_limited',
                 'Blocked': 'blocked', 'Usage limited': 'usage_limited',
                 'Waiting for background tasks': 'active', 'Verifying the result': 'active',
                 'Waiting for your answer': 'active'}


def tui_status(lines):
    banner = None
    for line in lines:
        m = BANNER.search(line)
        if m:
            banner = m.group(1).strip()
    if banner:
        return BANNER_STATUS.get(banner, banner), f'横幅 ◎ Goal · {banner}'
    last, which = -1, None
    for i, line in enumerate(lines):
        if '✓ Goal complete' in line and i >= last:
            last, which = i, 'complete'
        if 'Goal cleared' in line and i >= last:
            last, which = i, 'none'
    return which, ('屏幕 ✓ Goal complete' if which == 'complete' else '屏幕 Goal cleared' if which == 'none' else '无横幅')


def lines_of(text):
    return [l.strip() for l in (text or '').strip().splitlines()]


# ---------- 检查（按功能地图） ----------

class Checks:
    def __init__(self):
        self.items = []

    def add(self, name, ok, detail=None):
        self.items.append({'check': name, 'ok': bool(ok), **({'detail': detail} if detail is not None else {})})

    def verdict(self):
        if not self.items:
            return '走不通'
        return '一致' if all(i['ok'] for i in self.items) else '不一致'


def subseq(seq, wanted):
    it = iter(seq)
    return all(any(w in s for s in it) for w in wanted)


def final_reply_after_update_goal(messages):
    idx = None
    for i, m in enumerate(messages):
        names = [t.get('tool_name') for t in (m.get('tool_calls') or [])]
        if 'update_goal' in names:
            idx = i
    if idx is None:
        return None
    turn = messages[idx].get('turn_id')
    return any(m.get('role') == 'assistant' and (m.get('msg_content') or '').strip() and m.get('turn_id') == turn
               for m in messages[idx + 1:])


def check(rec, recs, snap, ev_session, ev_window, c):
    k = rec.key
    g = rec.goal
    fg = rec.final_goal
    R = lambda key: recs.get(key)

    def snap_of(key):
        r = R(key)
        s = r.snaps() if r else []
        return Snap(s[-1]) if s else None

    def ok_step(step):  # 存在且不是 -timeout / -hold-broken
        return rec.has(step)

    def traj_has(step, field, value):
        return any(t.get(field) == value for t in rec.traj(step))

    def lines_has(lines, text):
        return any(text in l for l in lines)

    if k == 'lifecycle/create/api':
        gg = g('create') or {}
        c.add('POST 200', rec.code('create') == 200, rec.code('create'))
        c.add('status active', gg.get('status') == 'active', gg.get('status'))
        c.add('token_budget 80000', gg.get('token_budget') == 80000, gg.get('token_budget'))
    elif k == 'lifecycle/pause/api':
        c.add('paused(user_requested)', (g('pause') or {}).get('status_reason') == 'paused(user_requested)', (g('pause') or {}).get('status_reason'))
    elif k == 'lifecycle/edit-paused/api':
        gg = g('edit') or {}
        c.add('objective 已更新', '1 to 4' in (gg.get('objective') or ''))
        c.add('仍 paused(user_requested)', gg.get('status_reason') == 'paused(user_requested)', gg.get('status_reason'))
    elif k == 'lifecycle/still-paused/api':
        tr = rec.traj('hold')
        c.add('hold 8 秒成立', ok_step('hold'))
        c.add('turns_used 不变', len({t.get('goal.turns_used') for t in tr}) == 1, [t.get('goal.turns_used') for t in tr])
    elif k == 'lifecycle/resume/api':
        c.add('status active', (g('resume') or {}).get('status') == 'active', (g('resume') or {}).get('status'))
    elif k == 'lifecycle/complete/api':
        c.add('complete(verifier_met)', (fg('run') or {}).get('status_reason') == 'complete(verifier_met)', (fg('run') or {}).get('status_reason'))
        c.add('轨迹出现 verification', traj_has('run', 'goal.execution.wait_reason', 'verification'))
        c.add('count.txt 为 1–4', snap and lines_of(snap.file_text('count.txt')) == ['1', '2', '3', '4'], snap and snap.file_text('count.txt'))
    elif k == 'lifecycle/replace/api':
        old = snap_of('lifecycle/complete/api')
        old_id = ((old.goal_body() or {}).get('goal') or {}).get('goal_id') if old else None
        gg = g('get') or {}
        c.add('新 goal_id', gg.get('goal_id') and gg.get('goal_id') != old_id, [old_id, gg.get('goal_id')])
        c.add('status active', gg.get('status') == 'active', gg.get('status'))
    elif k == 'lifecycle/clear/api':
        c.add('DELETE 2xx', (rec.code('delete') or 0) < 300, rec.code('delete'))
        c.add('GET 返回 {}', rec.body('get') == {}, rec.body('get'))
    elif k == 'lifecycle/create/tui':
        c.add('◎ Goal · Active', ok_step('active'))
    elif k == 'lifecycle/pause/tui':
        c.add('◎ Goal · Paused', ok_step('paused'))
        c.add('状态栏 state=cancel', rec.screen_status('idle').get('state') == 'cancel', rec.screen_status('idle').get('state'))
        c.add('轮次显示 Interrupted', lines_has(rec.screen('idle'), 'Interrupted'))
    elif k == 'lifecycle/summary/tui':
        lines = rec.screen('summary')
        c.add('摘要出现 Objective:', ok_step('summary'))
        c.add('摘要含 Time used', lines_has(lines, 'Time used'))
    elif k == 'lifecycle/edit-paused/tui':
        c.add('Goal objective updated.', ok_step('updated'))
        c.add('Paused 保持 8 秒', ok_step('hold'))
    elif k == 'lifecycle/resume/tui':
        c.add('Goal resumed.', ok_step('resumed'))
    elif k == 'lifecycle/complete/tui':
        lines = rec.screen('complete')
        c.add('✓ Goal complete · … turns', ok_step('complete') and any(re.search(r'✓ Goal complete · .* turns', l) for l in lines))
        c.add('count.txt 为 1–4', snap and lines_of(snap.file_text('count.txt')) == ['1', '2', '3', '4'], snap and snap.file_text('count.txt'))
    elif k == 'lifecycle/replace/tui':
        c.add('新 Goal Active', ok_step('active'))
        c.add('出现第二个 goal.created', sum(1 for e in ev_session if e.startswith('goal.created')) >= 2)
    elif k == 'lifecycle/clear/tui':
        c.add('Goal cleared.', ok_step('cleared'))
    elif k == 'lifecycle/create/electron':
        c.add('横幅出现', ok_step('banner'))
        c.add('状态“进行中”', rec.result('status').get('text') == '进行中', rec.result('status').get('text'))
    elif k == 'lifecycle/auth-card/electron':
        cards = [n for n in rec.names if re.search(r'--card-\d+\.json$', n)]
        c.add('执行轮次出现“文件夹权限”卡片并点“仅本对话”', len(cards) >= 1, len(cards))
        c.add('之后跑到 complete', ((snap.goal_body() or {}).get('goal') or {}).get('status') == 'complete' if snap else False)
    elif k == 'lifecycle/complete/electron':
        c.add('complete(verifier_met)', (fg('run') or {}).get('status_reason') == 'complete(verifier_met)', (fg('run') or {}).get('status_reason'))
        c.add('完成标记“目标已完成 用时 …”', (rec.result('marker-text').get('text') or '').startswith('目标已完成 用时'), rec.result('marker-text').get('text'))
        c.add('横幅“已完成”', rec.result('banner-status').get('text') == '已完成', rec.result('banner-status').get('text'))
        c.add('count.txt 为 1–3', snap and lines_of(snap.file_text('count.txt')) == ['1', '2', '3'], snap and snap.file_text('count.txt'))
    elif k == 'lifecycle/pause/electron':
        c.add('paused(user_requested)', (fg('paused') or {}).get('status_reason') == 'paused(user_requested)', (fg('paused') or {}).get('status_reason'))
        c.add('状态“已停止”', rec.result('status').get('text') == '已停止', rec.result('status').get('text'))
    elif k == 'lifecycle/resume/electron':
        c.add('status active', (fg('active') or {}).get('status') == 'active')
        c.add('状态“进行中”', rec.result('status').get('text') == '进行中', rec.result('status').get('text'))
    elif k == 'lifecycle/edit-replace/electron':
        c.add('弹出“替换当前目标?”', ok_step('modal'))
        c.add('新目标生效', ok_step('objective'))
        c.add('complete(verifier_met)', (fg('run') or {}).get('status_reason') == 'complete(verifier_met)', (fg('run') or {}).get('status_reason'))
        c.add('count.txt 为新目标结果 1–4', snap and lines_of(snap.file_text('count.txt')) == ['1', '2', '3', '4'], snap and snap.file_text('count.txt'))
    elif k == 'lifecycle/clear/electron':
        c.add('横幅消失', ok_step('hidden'))
        c.add('GET 返回 {}', rec.body('get') == {}, rec.body('get'))
    elif k == 'continuation/background/api':
        c.add('进入 required_background 且 turns_used 1', (fg('waiting') or {}).get('turns_used') == 1 and ok_step('waiting'), (fg('waiting') or {}).get('turns_used'))
        tr = rec.traj('run')
        c.add('轨迹 required_background → verification', subseq([str(t.get('goal.execution.wait_reason')) for t in tr], ['required_background', 'verification']))
        c.add('complete(verifier_met)', (fg('run') or {}).get('status_reason') == 'complete(verifier_met)', (fg('run') or {}).get('status_reason'))
        c.add('bg.txt 为 bg-done', snap and (snap.file_text('bg.txt') or '').strip() == 'bg-done', snap and snap.file_text('bg.txt'))
        c.add('事件 turn_settled → deferred(required_background) → ready → 第二个 turn_bound',
              subseq(ev_session, ['goal.turn_settled', 'reason=deferred(required_background)', 'decision=ready', 'goal.turn_bound']))
    elif k == 'continuation/queue-while-waiting/api':
        b = rec.body('queue') or {}
        c.add('queue 200 queued position 2', rec.code('queue') == 200 and b.get('status') == 'queued' and b.get('position') == 2, {k2: b.get(k2) for k2 in ('status', 'position')})
        c.add('用户消息先执行（历史出现 42）', ok_step('history'))
        gg = g('goal-still-waiting') or {}
        c.add('Goal 仍 active、required_background、turns_used 1', gg.get('status') == 'active' and (gg.get('execution') or {}).get('wait_reason') == 'required_background' and gg.get('turns_used') == 1,
              [gg.get('status'), (gg.get('execution') or {}).get('wait_reason'), gg.get('turns_used')])
        c.add('complete(verifier_met)', (fg('run') or {}).get('status_reason') == 'complete(verifier_met)', (fg('run') or {}).get('status_reason'))
        c.add('late.txt 为 late-done', snap and (snap.file_text('late.txt') or '').strip() == 'late-done', snap and snap.file_text('late.txt'))
    elif k == 'continuation/background/tui':
        traj_lines = [h for t in rec.traj('waiting') + rec.traj('complete') for h in t.get('highlights', [])]
        c.add('◎ Goal · Waiting for background tasks', ok_step('waiting'))
        c.add('状态栏 background=1', any('background=1' in h for h in traj_lines))
        c.add('✓ Goal complete · … · 2 turns', any('✓ Goal complete' in l and '2 turns' in l for l in rec.screen('complete')))
        c.add('bg.txt 为 bg-done', snap and (snap.file_text('bg.txt') or '').strip() == 'bg-done', snap and snap.file_text('bg.txt'))
    elif k == 'continuation/background/electron':
        c.add('进入 required_background', ok_step('waiting'))
        c.add('横幅“等待后台任务完成”', rec.result('ui-waiting').get('text') == '等待后台任务完成', rec.result('ui-waiting').get('text'))
        tr = rec.traj('run')
        c.add('轨迹 → verification → complete', subseq([str(t.get('goal.execution.wait_reason')) for t in tr], ['verification']))
        c.add('complete(verifier_met)', (fg('run') or {}).get('status_reason') == 'complete(verifier_met)', (fg('run') or {}).get('status_reason'))
        c.add('完成标记', ok_step('marker'))
        c.add('bg.txt 为 bg-done', snap and (snap.file_text('bg.txt') or '').strip() == 'bg-done', snap and snap.file_text('bg.txt'))
    elif k in ('completion/complete/api', 'completion/complete/electron'):
        gg = (snap.goal_body() or {}).get('goal') or {} if snap else {}
        lv = gg.get('last_verification') or {}
        c.add('complete(verifier_met)', gg.get('status_reason') == 'complete(verifier_met)', gg.get('status_reason'))
        c.add('last_verification backend subagent、verdict met', lv.get('backend') == 'subagent' and lv.get('verdict') == 'met', {x: lv.get(x) for x in ('backend', 'verdict')})
        c.add('事件 dispatched → child_started → active→complete → decided(met,accepted) → proposal complete',
              subseq(ev_session, ['goal.verification_dispatched', 'goal.verification_child_started', 'to=complete',
                                  'goal.verification_decided', 'proposal=complete']))
        if rec.entry == 'electron':
            c.add('验证期间横幅“正在验证目标结果”', (rec.result('verifying').get('text') or '') == '正在验证目标结果', rec.result('verifying').get('text'))
    elif k == 'completion/no-continuation/api':
        msgs = snap.messages() if snap else []
        last = next((m for m in reversed(msgs) if m.get('role') == 'assistant'), {})
        c.add('助手回复 OK', (last.get('msg_content') or '').strip().rstrip('.') == 'OK', last.get('msg_content'))
        tr = rec.traj('hold')
        c.add('10 秒内一直 complete、turns_used 不变', ok_step('hold') and len({t.get('goal.turns_used') for t in tr}) == 1, [t.get('goal.turns_used') for t in tr])
        c.add('queue items 为空', ((rec.body('queue') or {}).get('items') or []) == [], rec.body('queue'))
    elif k == 'completion/replace/api':
        gg = g('create') or {}
        old = snap_of('completion/no-continuation/api')
        old_id = ((old.goal_body() or {}).get('goal') or {}).get('goal_id') if old else None
        c.add('返回新 goal_id', gg.get('goal_id') and gg.get('goal_id') != old_id, [old_id, gg.get('goal_id')])
        c.add('active、turns_used 0', gg.get('status') == 'active' and gg.get('turns_used') == 0, [gg.get('status'), gg.get('turns_used')])
    elif k in ('completion/final-reply/api', 'completion/final-reply/electron'):
        fr = final_reply_after_update_goal(snap.messages() if snap else [])
        c.add('update_goal 之后同一轮没有最终回复（基线；第 2 项之后会有）', fr is False, fr)
        c.add('本轮结算后才派发验证（turn_settled 在 verification_dispatched 之前）', subseq(ev_session, ['goal.turn_settled', 'goal.verification_dispatched']))
        if rec.entry == 'electron':
            n = rec.result('lifted-cards').get('count')
            c.add('基线界面没有 goal-lifted-delivery-cards', n == 0, n)
    elif k == 'completion/complete/tui':
        r = R('lifecycle/complete/tui')
        hl = [h for t in (r.traj('complete') if r else []) for h in t.get('highlights', [])]
        c.add('验证期间横幅 ◎ Goal · Verifying the result', any('Verifying the result' in h for h in hl))
        c.add('✓ Goal complete', any('✓ Goal complete' in l for l in rec.screen('screen')))
        ok_ev = subseq(ev_session, ['goal.verification_dispatched', 'goal.verification_child_started', 'to=complete', 'goal.verification_decided', 'proposal=complete'])
        c.add('验证事件顺序同接口', ok_ev)
    elif k == 'completion/final-reply/tui':
        lines = rec.screen('screen')
        st = rec.screen_status('screen').get('state')
        c.add('基线地图：完成轮显示 × Error Runtime completed without a final assistant response.', any('Runtime completed without a final assistant response' in l for l in lines))
        c.add('基线地图：状态栏 state=fail', st == 'fail', st)
        run_dir, _ = rec.run_dir()
        turn = rec.screen_status('screen').get('turn')
        res = None
        if run_dir and os.path.exists(os.path.join(run_dir, 'tui-results.jsonl')):
            for line in open(os.path.join(run_dir, 'tui-results.jsonl'), errors='replace'):
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if d.get('turnId') == turn:
                    res = {'status': d.get('status'), 'code': (d.get('error') or {}).get('code')}
        c.add('基线：tui-results.jsonl 完成轮 failed / EMPTY_RESPONSE', res == {'status': 'failed', 'code': 'EMPTY_RESPONSE'}, res)
    elif k == 'completion/verify-auth-card/electron':
        cards = [n for n in rec.names if re.search(r'--card-\d+\.json$', n)]
        c.add('验证子会话出现授权卡片并点“仅本对话”', len(cards) >= 1, len(cards))
    elif k == 'completion/reload/electron':
        c.add('重载后侧栏出现', ok_step('sidebar'))
        c.add('回到该会话、完成标记仍在', ok_step('marker') or ok_step('marker-2'))
        c.add('横幅仍“已完成”', rec.result('banner-status').get('text') == '已完成', rec.result('banner-status').get('text'))
        c.add('重载不产生新的 goal.* 事件', ev_window == [], ev_window)
    elif k == 'limits/token-budget/api':
        f = fg('run') or {}
        c.add('budget_limited(token)', f.get('status_reason') == 'budget_limited(token)', f.get('status_reason'))
        c.add('tokens_used 远大于 3000', (f.get('tokens_used') or 0) > 3000, f.get('tokens_used'))
    elif k == 'limits/resume-rejected/api':
        b = rec.body('resume') or {}
        c.add('409 GOAL_BUDGET_LIMITED', rec.code('resume') == 409 and 'GOAL_BUDGET_LIMITED' in json.dumps(b), [rec.code('resume'), b.get('code') if isinstance(b, dict) else b])
    elif k == 'limits/raise-reopen/api':
        gr = g('raise') or {}
        c.add('只改预算：200、token_budget 200000、仍 budget_limited(token)', rec.code('raise') == 200 and gr.get('token_budget') == 200000 and gr.get('status_reason') == 'budget_limited(token)',
              [rec.code('raise'), gr.get('token_budget'), gr.get('status_reason')])
        go = g('reopen') or {}
        c.add('提高预算并恢复：active', rec.code('reopen') == 200 and go.get('status') == 'active', [rec.code('reopen'), go.get('status')])
        c.add('DELETE 2xx', (rec.code('delete') or 0) < 300, rec.code('delete'))
    elif k == 'limits/timer/api':
        t1 = (g('get1') or {}).get('time_used_seconds')
        t2 = (g('get2') or {}).get('time_used_seconds')
        tp = (g('pause') or {}).get('time_used_seconds')
        t3 = (g('get3') or {}).get('time_used_seconds')
        c.add('运行中 time_used_seconds 递增', t1 is not None and t2 is not None and t2 > t1, [t1, t2])
        c.add('暂停后 10 秒不变', tp is not None and t3 == tp, [tp, t3])
    elif k == 'limits/token-budget/tui':
        lines = rec.screen('limited') + rec.screen('idle')
        c.add('◎ Goal · Budget limited', ok_step('limited'))
        c.add('提示 /goal clear, then /goal <objective> starts a new Goal', lines_has(lines, 'starts a new Goal'))
    elif k == 'limits/resume-rejected/tui':
        c.add('/goal resume 后仍 Budget limited', ok_step('still-limited'))
    elif k == 'limits/clear/tui':
        c.add('Goal cleared.', ok_step('cleared'))
    elif k == 'attachments/kickoff/api':
        gg = g('create') or {}
        c.add('POST 200、has_kickoff_attachments true', rec.code('create') == 200 and gg.get('has_kickoff_attachments') is True)
        c.add('complete(verifier_met)', (fg('run') or {}).get('status_reason') == 'complete(verifier_met)', (fg('run') or {}).get('status_reason'))
        c.add('secret.txt 为 PAPAYA-42', snap and (snap.file_text('secret.txt') or '').strip() == 'PAPAYA-42', snap and snap.file_text('secret.txt'))
        first_user = next((m for m in (snap.messages() if snap else []) if m.get('role') == 'user'), {})
        c.add('第一条用户消息 attachments 含 goal-brief.txt', 'goal-brief.txt' in json.dumps(first_user.get('attachments') or []))
        insp = snap.inspector_text() if snap else ''
        c.add('请求里 <attachment ... path> 指向 data/v2/assets/', bool(re.search(r'<attachment[^>]*goal-brief\.txt[^>]*v2/assets/', insp.replace('\\"', '"'))))
    elif k == 'attachments/kickoff/tui':
        pasted = rec.screen('pasted')
        all_lines = [l for n in rec.names if n.endswith('.txt') for l in open(os.path.join(rec.dir, n), errors='replace')]
        c.add('粘贴后输入框出现 [Image #1]', lines_has(pasted, '[Image #1]'))
        c.add('输入框上方出现 Goal · 1 attachment · Enter start', lines_has(all_lines, 'Goal · 1 attachment · Enter start'))
        started_lines = rec.screen('started') + rec.screen('started-2') + [h for t in rec.traj('terminal') for h in t.get('highlights', [])]
        c.add('一次回车即开始（Goal started.）', rec.has('started'))
        c.add('横幅 ◎ Goal · Active · … · Attachment', any('◎ Goal · Active' in l and 'Attachment' in l for l in started_lines))
        c.add('color.txt 为 red', snap and (snap.file_text('color.txt') or '').strip() == 'red', snap and snap.file_text('color.txt'))
        insp = snap.inspector_text() if snap else ''
        c.add('请求里有 <attachment name="red-square.png" mime="image/png"', 'red-square.png' in insp and 'image/png' in insp)
    elif k == 'attachments/kickoff/electron':
        up = rec.result('upload')
        c.add('upload mechanism native-dialog', up.get('mechanism') == 'native-dialog', up.get('mechanism'))
        c.add('attachment-bar 显示 goal-brief.txt', 'goal-brief.txt' in (rec.result('bar').get('text') or ''))
        gg = g('goal') or {}
        c.add('has_kickoff_attachments true、objective_resources 空', gg.get('has_kickoff_attachments') is True and not gg.get('objective_resources'))
        c.add('complete(verifier_met)', (fg('run') or {}).get('status_reason') == 'complete(verifier_met)', (fg('run') or {}).get('status_reason'))
        c.add('secret.txt 为 PAPAYA-42', snap and (snap.file_text('secret.txt') or '').strip() == 'PAPAYA-42', snap and snap.file_text('secret.txt'))
        insp = snap.inspector_text() if snap else ''
        c.add('请求里有 <attachment name="goal-brief.txt"', 'attachment name=\\"goal-brief.txt\\"' in insp or 'attachment name="goal-brief.txt"' in insp)
    elif k == 'attachments/objective-resources/electron':
        gg = g('goal') or {}
        res = gg.get('objective_resources') or []
        obj = gg.get('objective') or ''
        c.add('has_kickoff_attachments false', gg.get('has_kickoff_attachments') is False, gg.get('has_kickoff_attachments'))
        c.add('objective_resources 含该文件且有 local.asset_id', any('goal-brief-2.txt' in json.dumps(r) and (r.get('local') or {}).get('asset_id') for r in res))
        c.add('objective 追加 <user-provided-context>、## Goal resources、1. "goal-brief-2.txt"',
              '<user-provided-context>' in obj and '## Goal resources' in obj and '1. "goal-brief-2.txt"' in obj)
        c.add('complete(verifier_met)', (fg('run') or {}).get('status_reason') == 'complete(verifier_met)', (fg('run') or {}).get('status_reason'))
        c.add('secret2.txt 为 MANGO-7', snap and (snap.file_text('secret2.txt') or '').strip() == 'MANGO-7', snap and snap.file_text('secret2.txt'))
    elif k in ('questionnaire/manual/api', 'questionnaire/auto-timeout/api'):
        pend = (rec.j('pending') or {}).get('final') or {}
        req = pend.get('request') or {}
        opts = ((req.get('steps') or [{}])[0].get('options') or [])
        apple = next((o for o in opts if 'apple' in json.dumps(o).lower()), {})
        c.add('问卷 purpose 1、status 0、expires_at = created_at + 300000',
              req.get('purpose') == 1 and req.get('status') == 0 and (req.get('expires_at') or 0) - (req.get('created_at') or 0) == 300000,
              {x: req.get(x) for x in ('purpose', 'status')} | {'expiresMinusCreated': (req.get('expires_at') or 0) - (req.get('created_at') or 0)})
        c.add('Apple recommended', apple.get('recommended') is True)
        run_dir, _ = rec.run_dir()
        glob_types = []
        if run_dir and os.path.exists(os.path.join(run_dir, 'events.jsonl')):
            for line in open(os.path.join(run_dir, 'events.jsonl'), errors='replace'):
                try:
                    glob_types.append(json.loads(line).get('type'))
                except ValueError:
                    pass
        c.add('events.jsonl 有 questionnaire.ask、questionnaire.dismiss', 'questionnaire.ask' in glob_types and 'questionnaire.dismiss' in glob_types)
        f = fg('run') or {}
        c.add('complete(verifier_met)', f.get('status_reason') == 'complete(verifier_met)', f.get('status_reason'))
        if rec.sub == 'manual':
            b = rec.body('reply') or {}
            c.add('reply 200、ok true、answered_at', rec.code('reply') == 200 and b.get('ok') is True and bool(b.get('answered_at')))
            c.add('turns_used 2', f.get('turns_used') == 2, f.get('turns_used'))
            c.add('fruit.txt 为 Banana', snap and (snap.file_text('fruit.txt') or '').strip() == 'Banana', snap and snap.file_text('fruit.txt'))
        else:
            hist = json.dumps(snap.messages() if snap else [])
            c.add('fruit.txt 为 Apple', snap and (snap.file_text('fruit.txt') or '').strip() == 'Apple', snap and snap.file_text('fruit.txt'))
            c.add('历史含 automatic_timeout 与 explicitUserConfirmation false',
                  '<responseSource>automatic_timeout</responseSource>' in hist and '<explicitUserConfirmation>false</explicitUserConfirmation>' in hist)
    elif k in ('questionnaire/manual/tui', 'questionnaire/auto-timeout/tui'):
        ask = rec.screen('ask')
        c.add('Ask 面板：Auto-continue in 5:00、Apple (Recommended)', lines_has(ask, 'Auto-continue in') and lines_has(ask, 'Apple (Recommended)'))
        c.add('✓ Goal complete', any('✓ Goal complete' in l for l in rec.screen('terminal')))
        want = 'Banana' if rec.sub == 'manual' else 'Apple'
        c.add(f'fruit.txt 为 {want}', snap and (snap.file_text('fruit.txt') or '').strip() == want, snap and snap.file_text('fruit.txt'))
        src = 'user' if rec.sub == 'manual' else 'automatic_timeout'
        insp = snap.inspector_text() if snap else ''
        c.add(f'发给模型的回答 responseSource 为 {src}', f'<responseSource>{src}</responseSource>' in insp)
    elif k in ('questionnaire/manual/electron', 'questionnaire/auto-timeout/electron'):
        c.add('问卷卡片出现（radiogroup Which fruit?）', ok_step('card'))
        pend = ((rec.body('pending') or {}).get('request') or {})
        c.add('pending purpose 1、status 0', pend.get('purpose') == 1 and pend.get('status') == 0)
        f = fg('run') or {}
        c.add('complete(verifier_met)', f.get('status_reason') == 'complete(verifier_met)', f.get('status_reason'))
        hist = json.dumps(snap.messages() if snap else [])
        if rec.sub == 'manual':
            c.add('回答后 pending 为 {}', rec.body('pending-after') == {}, rec.body('pending-after'))
            c.add('fruit.txt 为 Banana', snap and (snap.file_text('fruit.txt') or '').strip() == 'Banana', snap and snap.file_text('fruit.txt'))
            c.add('历史 responseSource user、explicitUserConfirmation true', '<responseSource>user</responseSource>' in hist and '<explicitUserConfirmation>true</explicitUserConfirmation>' in hist)
        else:
            c.add('卡片消失', rec.result('card-after').get('count') == 0, rec.result('card-after').get('count'))
            c.add('fruit.txt 为 Apple', snap and (snap.file_text('fruit.txt') or '').strip() == 'Apple', snap and snap.file_text('fruit.txt'))
            c.add('历史含 automatic_timeout 与 explicitUserConfirmation false',
                  '<responseSource>automatic_timeout</responseSource>' in hist and '<explicitUserConfirmation>false</explicitUserConfirmation>' in hist)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root')
    ap.add_argument('--tag', default='rg1base')
    ap.add_argument('--notes')
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    notes_extra = load(args.notes) if args.notes else {}

    recs = {f'{f}/{s}/{e}': Rec(root, args.tag, f, s, e, label, scope) for f, s, e, label, scope in RECORDS}
    all_snaps = [Snap(p) for r in recs.values() for p in r.snaps()]

    out = []
    for f, s, e, label, scope in RECORDS:
        rec = recs[f'{f}/{s}/{e}']
        snaps = rec.snaps()
        snap = Snap(snaps[-1]) if snaps else None
        entry = {'feature': f, 'subfeature': s, 'entry': e, 'final_status': None, 'status_reason': None,
                 'files': None, 'goal_event_types': None, 'matches_map': '走不通', 'notes': []}
        entry['label'] = f'{FEATURE_CN[f]} · {label} · {ENTRY_CN[e]}'
        entry['evidence_dir'] = os.path.relpath(rec.dir, root) if rec.names else None
        run_dir, run_id = rec.run_dir()
        entry['run_id'] = run_id
        if not rec.names:
            entry['notes'].append('没有证据目录：该子功能未执行或流程没有走到。')
        else:
            ordinals = {}
            session_events = []
            window_events = []
            if snap:
                entry['session_id'] = snap.session
                earlier = [x for x in all_snaps if x.session == snap.session and x.at < snap.at]
                prev = max(earlier, key=lambda x: x.at) if earlier else None
                describe_events(snap.events, ordinals)  # 固定 g1、g2 的编号
                session_events = describe_events(snap.events, ordinals)
                if scope == 'session' or not prev:
                    window_events = session_events
                else:
                    seen = {ev['line'] for ev in prev.events}
                    window_events = describe_events([ev for ev in snap.events if ev['line'] not in seen], ordinals)
                entry['goal_event_types'] = window_events
                entry['event_scope'] = 'session' if (scope == 'session' or not prev) else 'window'
                entry['files'] = snap.files()
                gb = snap.goal_body()
                if gb is not None:
                    gg = gb.get('goal') if isinstance(gb, dict) else None
                    entry['final_status'] = gg.get('status') if gg else 'none'
                    entry['status_reason'] = gg.get('status_reason') if gg else None
                    entry['status_source'] = 'snapshot GET .../goal'
                else:
                    st, src = tui_status(snap.screen())
                    ev_st, ev_reason = event_status(snap.events)
                    entry['final_status'] = st
                    entry['status_reason'] = ev_reason if (st == ev_st and st not in (None, 'active', 'none')) else None
                    entry['status_source'] = f'{src}；原因取 runtime 事件'
            else:
                entry['notes'].append('该子功能目录没有 snapshot。')
            c = Checks()
            try:
                check(rec, recs, snap, session_events, window_events, c)
            except Exception as exc:  # noqa: BLE001 - 检查自身出错时记下，不中断汇总
                c.add('检查执行出错', False, repr(exc))
            entry['checks'] = c.items
            entry['matches_map'] = c.verdict() if snap or c.items else '走不通'
            for item in c.items:
                if not item['ok']:
                    entry['notes'].append(f"未满足：{item['check']}" + (f"（实际 {json.dumps(item.get('detail'), ensure_ascii=False)[:200]}）" if 'detail' in item else ''))
        entry['notes'] += (notes_extra or {}).get(f'{f}/{s}/{e}', [])
        out.append(entry)

    with open(os.path.join(root, 'summary.json'), 'w') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
        fh.write('\n')

    rows = ['| 功能 | 子功能 | 入口 | 最终状态 | status_reason | 工作目录文件 | goal 事件数 | 与地图 | 证据 |',
            '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for x in out:
        files = ', '.join(f['path'] for f in (x['files'] or [])) or '—'
        rows.append('| {} | {} | {} | {} | {} | {} | {} | {} | {} |'.format(
            FEATURE_CN[x['feature']], x['label'].split(' · ')[1], ENTRY_CN[x['entry']], x['final_status'] or '—',
            x['status_reason'] or '—', files, len(x['goal_event_types'] or []), x['matches_map'],
            f"`{x['evidence_dir']}`" if x['evidence_dir'] else '—'))
    with open(os.path.join(root, 'summary-table.md'), 'w') as fh:
        fh.write('\n'.join(rows) + '\n')
    counts = {}
    for x in out:
        counts[x['matches_map']] = counts.get(x['matches_map'], 0) + 1
    print(json.dumps({'records': len(out), 'counts': counts}, ensure_ascii=False))


if __name__ == '__main__':
    main()
