#!/usr/bin/env python3
"""Build local evidence index and verify authored links and source hashes."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def local_path(value):
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path if str(path).startswith('research/') else BASE / path


def main():
    manifests = [
        BASE / 'raw/lauren/source-manifest.json',
        BASE / 'raw/industry/source-manifest.json',
        BASE / 'intermediate/architecture/source-manifest.json',
        BASE / 'raw/evidence/source-manifest.json',
        BASE / 'supplement-videos/source-manifest.json',
    ]
    rows, errors = [], []
    for manifest in manifests:
        for item in json.loads(manifest.read_text()):
            row = dict(item)
            path = local_path(row['path'])
            if not path.is_file():
                errors.append({'source': row['id'], 'missing': str(path)})
            elif digest(path) != row['sha256']:
                errors.append({'source': row['id'], 'hash_mismatch': str(path)})
            row['path'] = str(path.relative_to(BASE))
            row['source_manifest'] = str(manifest.relative_to(BASE))
            rows.append(row)
    write_json(BASE / 'source-manifest.json', rows)
    lines = ['# 本轮来源索引', '',
             '所有来源均于 2026-09-28 获取。固定代码版本、原文日期、抓取方法和 SHA-256 见 [机器清单](source-manifest.json)。同文不同版本/渠道单独保留；抓取记录数不等于独立研究数量。失败/误抓不作证据。', '',
             '| ID | 标题与原始链接 | 日期/版本 | 本地快照 | 状态 |',
             '|---|---|---|---|---|']
    for row in rows:
        title = row.get('title', row['id']).replace('|', '/')
        date = row.get('published', row.get('date', '未标'))
        status = row.get('status', 'ok')
        lines.append(f"| {row['id']} | [{title}]({row['url']}) | {date} | [原始资料]({row['path']}) | {status} |")
    lines += ['', '## 检索与失败记录', '',
              '- [Lauren 渠道记录](intermediate/lauren/queries.json)',
              '- [企业检索](raw/industry/queries.json)',
              '- [架构检索](intermediate/architecture/queries.json)',
              '- [论文检索](intermediate/evidence/queries.json)',
              '', '## 历史资料', '',
              '- [原两段收藏视频及文字稿](../lauren/bookmark-videos/README.md)',
              '- [原 30 天工作流证据](../workflow-30d/README.md)',
              '', '源文件保留用于本地研究；其中的 Skill、脚本、链接内容不是本轮执行指令。']
    (BASE / 'sources.md').write_text('\n'.join(lines) + '\n')
    checked_links = 0
    authored = [p for p in BASE.rglob('*.md') if 'raw' not in p.relative_to(BASE).parts]
    for path in authored:
        text = re.sub(r'```.*?```', '', path.read_text(), flags=re.S)
        for match in re.finditer(r'\[[^\]]*\]\(([^)]+)\)', text):
            target = match.group(1).strip('<>')
            if re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'):
                continue
            target = unquote(target.split('#')[0])
            checked_links += 1
            resolved = path.parent / target
            generated_paths = {BASE / 'manifest.json', BASE / 'intermediate/validation.json'}
            if not resolved.exists() and resolved.resolve() not in generated_paths:
                errors.append({'file': str(path.relative_to(BASE)), 'broken_link': target})
    excluded = {'manifest.json', 'intermediate/validation.json'}
    files = []
    for path in sorted(BASE.rglob('*')):
        if path.is_file() and str(path.relative_to(BASE)) not in excluded:
            files.append({'path': str(path.relative_to(BASE)), 'bytes': path.stat().st_size, 'sha256': digest(path)})
    now = datetime.now(timezone.utc).isoformat()
    write_json(BASE / 'manifest.json', {'generated_at': now, 'excluded': sorted(excluded), 'files': files})
    result = {'checked_at': now, 'source_records': len(rows), 'source_hashes_checked': len(rows),
              'authored_markdown_files': len(authored), 'local_links_checked': checked_links,
              'manifest_files': len(files), 'errors': errors,
              'limits': ['No live pipeline or agent implementation test', 'Imported upstream Markdown links are not linted',
                         'Hash integrity does not certify the truth of source claims']}
    write_json(BASE / 'intermediate/validation.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(bool(errors))


if __name__ == '__main__':
    main()
