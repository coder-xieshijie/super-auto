#!/usr/bin/env python3
"""M2 S02 前提安排：给 budget_limited(token) 会话写一条基线格式的预算总结队列项（尚未执行）。

基线在预算用尽后另排一个 `thread-goal-continuation`/`budget-limit` 的队列项；生成数据时它的请求被挂起、
实例被 SIGKILL，队列表里没有留下这一行（基线启动时靠 listRecoverableBudgetLimitSummaries 重新提交）。
这里按同一份数据里基线自己写的 `active` 续跑项（同格式）复制出一条 `budget-limit` 项，写入 queued 状态，
作为 verify S02“其队列里有预算总结项尚未执行”的前提。这是直接写存储安排的前提，不是产品路径。

用法：m2-s02-arrange-budget-item.py <runId 或数据目录> <budget 会话> <证据目录>
经 verify-archon 的 `db` 命令读写（只对已停止的实例数据）。
"""
import base64
import hashlib
import json
import subprocess
import sys
import uuid

V = '.agents/skills/verify-archon/scripts/verify-archon.mjs'
data, session, out = sys.argv[1], sys.argv[2], sys.argv[3]


def db(*args):
    res = subprocess.run(['node', V, 'db', '--data', data, *args], capture_output=True, text=True)
    if res.returncode != 0:
        sys.exit(f'db failed: {res.stdout[-400:]} {res.stderr[-400:]}')
    return json.loads(res.stdout)


goal = db('--query', f"SELECT goal_id, objective, status, status_reason, token_budget, tokens_used, time_used_seconds, updated_at_ms FROM local_runtime_thread_goals WHERE session_id = '{session}'")['rows'][0]
assert goal['status'] == 'budget_limited', goal['status']
template = db('--query', "SELECT session_id, source, routing_fingerprint, data_json FROM local_runtime_queue_items WHERE source = 'thread-goal' AND data_json LIKE '%\"kind\":\"active\"%' ORDER BY id LIMIT 1")['rows'][0]
item = json.loads(template['data_json'])

prompt = subprocess.run(['git', 'show', 'd770f05f30:packages/local-runtime-v2/assets/agents/workflow/goal/budget-limit.md'],
                        capture_output=True, text=True, check=True).stdout
for key, value in (('objective', goal['objective']), ('time_used_seconds', goal['time_used_seconds']),
                   ('tokens_used', goal['tokens_used']), ('token_budget', goal['token_budget'])):
    prompt = prompt.replace('{{' + key + '}}', str(value))

now = goal['updated_at_ms'] + 1
item_id = f'queue_{uuid.uuid4()}'
client_request_id = f"thread-goal-followup:budget-limit:{goal['goal_id']}:{goal['updated_at_ms']}"
item.update({
    'itemId': item_id,
    # 与 runtime 的 createUserMessageId 相同：sha256(sessionId \0 messageKey) 的 base64url
    'userMessageId': 'msg-user-v1-' + base64.urlsafe_b64encode(
        hashlib.sha256(session.encode() + b'\0' + item_id.encode()).digest()).decode().rstrip('='),
    'sessionId': session,
    'status': 'queued',
    'createdAt': now,
    'requestedTurnId': f'turn_{uuid.uuid4()}',
    'clientRequestId': client_request_id,
})
item['message'] = {
    **item['message'],
    'content': f'<archon_internal_context source="goal">\n{prompt}\n</archon_internal_context>',
    'origin': {
        'type': 'thread-goal-continuation',
        'goalId': goal['goal_id'],
        'goalUpdatedAt': goal['updated_at_ms'],
        'objectiveDigest': hashlib.sha256(goal['objective'].encode()).hexdigest(),
        'kind': 'budget-limit',
    },
}


def q(text):
    return "'" + str(text).replace("'", "''") + "'"


sql = (
    'INSERT INTO local_runtime_queue_items (session_id, item_id, status, created_at_ms, data_json, source, '
    'client_request_id, dedupe_key, expires_at_ms, claim_id, claim_lease_expires_at_ms, routing_fingerprint) VALUES ('
    f"{q(session)}, {q(item_id)}, 'queued', {now}, {q(json.dumps(item, ensure_ascii=False))}, 'thread-goal', "
    f"{q(client_request_id)}, NULL, NULL, NULL, NULL, {q(template['routing_fingerprint'])})"
)
res = db('--sql', f"DELETE FROM local_runtime_queue_items WHERE session_id = '{session}'; " + sql, '--save', 's02-arrange-budget-summary-item')
after = db('--query', f"SELECT id, session_id, item_id, status, client_request_id, json_extract(data_json, '$.message.origin') AS origin FROM local_runtime_queue_items WHERE session_id = '{session}'", '--save', 's02-arranged-budget-queue')
json.dump({'goal': {k: v for k, v in goal.items() if k != 'objective'}, 'insert': res, 'queueAfter': after['rows']},
          open(f'{out}/arrange-budget-summary-item.json', 'w'), indent=2, ensure_ascii=False)
print(json.dumps(after['rows'], ensure_ascii=False))
