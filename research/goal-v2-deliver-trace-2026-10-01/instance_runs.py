#!/usr/bin/env python3
"""统计 verify-archon 实例的启动、结束时间，以及每轮场景里实例实际在跑的时间。

用法: instance_runs.py <verify-archon 实例根目录> <输出.md> [--day 20261001] [--round 名称=HH:MM-HH:MM ...]

实例根目录一般是 `$(node -e "console.log(require('os').tmpdir())")/verify-archon`。
开始时间取 runId 前缀，结束时间取目录内文件的最晚修改时间（近似值；实例停止后不再写文件）。
种类取 state.json 的 kind（runtime=接口实例，tui，electron）。
"""
import os, sys, json, datetime


def load_runs(root, day):
    runs = []
    for r in sorted(os.listdir(root)):
        p = os.path.join(root, r)
        if not os.path.isdir(p) or not r.startswith(day):
            continue
        kind = '?'
        try:
            kind = json.load(open(os.path.join(p, 'state.json'))).get('kind', '?')
        except Exception:
            pass
        ts = []
        for rr, _, fs in os.walk(p):
            for f in fs:
                try:
                    ts.append(os.path.getmtime(os.path.join(rr, f)))
                except OSError:
                    pass
        start = datetime.datetime.strptime(r[:15], '%Y%m%d-%H%M%S')
        end = datetime.datetime.fromtimestamp(max(ts)) if ts else start
        runs.append((start, end, kind, r))
    return runs


def union_seconds(intervals):
    total, cur = 0, None
    for a, b in sorted(intervals):
        if cur is None or a > cur[1]:
            if cur:
                total += (cur[1] - cur[0]).total_seconds()
            cur = [a, b]
        else:
            cur[1] = max(cur[1], b)
    if cur:
        total += (cur[1] - cur[0]).total_seconds()
    return total


def main():
    root, out = sys.argv[1], sys.argv[2]
    day = sys.argv[sys.argv.index('--day') + 1] if '--day' in sys.argv else '20261001'
    rounds = []
    if '--round' in sys.argv:
        for spec in sys.argv[sys.argv.index('--round') + 1:]:
            if spec.startswith('--'):
                break
            name, rng = spec.split('=')
            a, b = rng.split('-')
            d = datetime.datetime.strptime(day, '%Y%m%d')
            s = d.replace(hour=int(a[:2]), minute=int(a[3:]))
            e = d.replace(hour=int(b[:2]), minute=int(b[3:]))
            rounds.append((name, s, e))
    runs = load_runs(root, day)
    L = [f'# verify-archon 实例运行（{day}）\n', f'共 {len(runs)} 次实例运行。结束时间是目录内文件的最晚修改时间，为近似值。\n']
    if rounds:
        L.append('## 每轮场景\n')
        L.append('| 轮次 | 墙钟（分） | 实例次数 | 实例在跑（并集，分） | 实例时长合计（分） | Electron 次数 | Electron 合计（分） | 单次最长（分） |')
        L.append('|---|---|---|---|---|---|---|---|')
        for name, s, e in rounds:
            rs = [x for x in runs if s <= x[0] < e]
            if not rs:
                continue
            el = [(b - a).total_seconds() for a, b, k, _ in rs if k == 'electron']
            L.append(f"| {name} | {(e - s).total_seconds() / 60:.0f} | {len(rs)} | "
                     f"{union_seconds([(a, b) for a, b, _, _ in rs]) / 60:.0f} | "
                     f"{sum((b - a).total_seconds() for a, b, _, _ in rs) / 60:.0f} | {len(el)} | {sum(el) / 60:.0f} | "
                     f"{max((b - a).total_seconds() for a, b, _, _ in rs) / 60:.1f} |")
    L.append('\n## 全部实例\n')
    L.append('| 开始 | 结束 | 分钟 | 种类 |')
    L.append('|---|---|---|---|')
    for a, b, k, _ in runs:
        L.append(f'| {a:%H:%M:%S} | {b:%H:%M:%S} | {(b - a).total_seconds() / 60:.1f} | {k} |')
    open(out, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print(out, len(runs))


if __name__ == '__main__':
    main()
