#!/usr/bin/env node
// Read the Goal completion turn from a verify-archon snapshot and print the
// facts S01/S02/S03 check: the update_goal(complete) result, what follows it
// in the same turn, the Inspector request after it, and the event order.
//
//   node gfd-turn-facts.mjs <snapshot-prefix> [--tui]
//
// <snapshot-prefix> is the evidence path without suffix, e.g.
// .../evidence/m1-api/004-s03. With --tui the snapshot has no history API
// response, so the turn is read from the Inspector only.
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import path from 'node:path';

const prefix = process.argv[2];
const tui = process.argv.includes('--tui');
if (!prefix) {
  console.error('usage: gfd-turn-facts.mjs <snapshot-prefix> [--tui]');
  process.exit(2);
}

const readJsonl = (file) =>
  existsSync(file)
    ? readFileSync(file, 'utf8')
        .split('\n')
        .filter(Boolean)
        .map((line) => JSON.parse(line))
    : [];

const events = readJsonl(`${prefix}-runtime-events.jsonl`).map((e) => ({
  at: e.tsMs,
  type: e.fields?.eventType,
  payload: e.fields?.payload,
}));

// Inspector calls: requests in capture order.
const inspectorDir = `${prefix}-inspector`;
const calls = readJsonl(path.join(inspectorDir, 'events.jsonl'))
  .filter((e) => e.type === 'call.captured')
  .map((e) => {
    const file = path.join(inspectorDir, 'payloads', `${Buffer.from(e.callId).toString('base64')}.request.json`);
    const request = existsSync(file) ? JSON.parse(readFileSync(file, 'utf8')) : undefined;
    return { callId: e.callId, turnId: e.turnId, startedAtMs: e.startedAtMs, expectedTools: e.expectedTools ?? [], request };
  })
  .sort((a, b) => a.startedAtMs - b.startedAtMs);

function blocksOf(message) {
  return Array.isArray(message?.content) ? message.content : [{ type: 'text', text: String(message?.content ?? '') }];
}

// Find the accepted update_goal(complete) tool_result inside Inspector requests.
function acceptedCompletionIn(request) {
  for (const [index, message] of (request?.messages ?? []).entries()) {
    for (const block of blocksOf(message)) {
      if (block.type !== 'tool_result') continue;
      const text = Array.isArray(block.content)
        ? block.content.map((c) => c.text ?? '').join('')
        : String(block.content ?? '');
      if (/"proposal":\{"status":"complete"[^}]*"accepted":true/.test(text)) {
        return { index, toolUseId: block.tool_use_id };
      }
    }
  }
  return undefined;
}

const facts = { prefix, inspectorCalls: calls.length };
const completionCalls = calls
  .map((call) => ({ call, hit: acceptedCompletionIn(call.request) }))
  .filter((entry) => entry.hit);
const firstAfter = completionCalls[0];
if (firstAfter) {
  const { call, hit } = firstAfter;
  const turnCalls = calls.filter((c) => c.turnId === call.turnId);
  const afterCalls = turnCalls.filter((c) => c.startedAtMs >= call.startedAtMs);
  facts.completionTurnId = call.turnId;
  facts.requestAfterCompletion = {
    callId: call.callId,
    startedAtMs: call.startedAtMs,
    sameTurn: true,
    completionResultIsLastMessage: hit.index === call.request.messages.length - 1,
  };
  const responseFile = path.join(inspectorDir, 'payloads', `${Buffer.from(call.callId).toString('base64')}.response.json`);
  const response = existsSync(responseFile) ? JSON.parse(readFileSync(responseFile, 'utf8')) : undefined;
  const responseText = (response?.content ?? [])
    .filter((block) => block.type === 'text')
    .map((block) => block.text)
    .join('');
  // Delivery markup only counts outside fenced and inline code.
  const outsideCode = responseText.replace(/```[\s\S]*?```/g, '').replace(/`[^`\n]*`/g, '');
  facts.responseAfterCompletion = {
    text: responseText,
    toolUse: (response?.content ?? []).filter((block) => block.type === 'tool_use').map((b) => b.name),
    deliveryMarkupForHelloHtml:
      /<deliver-assets>[\s\S]*<media[^>]*src="[^"]*hello\.html"[\s\S]*<\/deliver-assets>/.test(outsideCode),
    pathInText: /hello\.html/.test(outsideCode.replace(/<deliver-assets>[\s\S]*?<\/deliver-assets>/g, '')) || /hello\.html/.test(responseText.replace(/<deliver-assets>[\s\S]*?<\/deliver-assets>/g, '')),
  };
  facts.requestsAfterCompletionInTurn = afterCalls.length;
  facts.toolsRequestedAfterCompletion = afterCalls.flatMap((c) => c.expectedTools.map((t) => t.toolName));
} else {
  facts.requestAfterCompletion = null;
}

if (!tui) {
  const snapshot = JSON.parse(readFileSync(`${prefix}.json`, 'utf8'));
  const messages = snapshot.http?.messages?.body?.messages ?? [];
  const goal = snapshot.http?.goal?.body?.goal;
  facts.goal = goal && {
    status: goal.status,
    status_reason: goal.status_reason,
    backend: goal.last_verification?.backend,
    verdict: goal.last_verification?.verdict,
  };
  const completeIndex = messages.findIndex((m) =>
    (m.tool_calls ?? []).some((t) => t.tool_name === 'update_goal' && /"accepted":true/.test(t.tool_call_result_data ?? '') && /\\"status\\":\\"complete\\"/.test(t.tool_call_result_data ?? '')),
  );
  if (completeIndex >= 0) {
    const turnId = messages[completeIndex].turn_id;
    const inTurn = messages.slice(completeIndex).filter((m) => m.turn_id === turnId);
    const before = messages.slice(0, completeIndex + 1).filter((m) => m.turn_id === turnId);
    const completeMessage = messages[completeIndex];
    const updateGoalCall = completeMessage.tool_calls.find((t) => t.tool_name === 'update_goal');
    const after = inTurn.slice(1);
    const finalReply = [...after].reverse().find((m) => m.role === 'assistant' && (m.msg_content ?? '').trim());
    const toolCallsAfter = [
      ...completeMessage.tool_calls.slice(completeMessage.tool_calls.indexOf(updateGoalCall) + 1),
      ...after.flatMap((m) => m.tool_calls ?? []),
    ];
    facts.history = {
      turnId,
      updateGoalArgs: JSON.parse(updateGoalCall.tool_call_args ?? '{}'),
      toolsBeforeCompletion: before.flatMap((m) => (m.tool_calls ?? []).map((t) => `${t.tool_name}:${t.tool_call_status}`)),
      messagesAfterCompletion: after.map((m) => ({ role: m.role, timestamp: m.timestamp, text: (m.msg_content ?? '').slice(0, 80) })),
      toolCallsAfterCompletion: toolCallsAfter.map((t) => ({ name: t.tool_name, status: t.tool_call_status, result: String(t.tool_call_result_data ?? '').slice(0, 200) })),
      finalReply: finalReply ? { timestamp: finalReply.timestamp, text: finalReply.msg_content } : null,
    };
    const dispatched = events.find((e) => e.type === 'goal.verification_dispatched');
    facts.order = {
      finalReplyAt: finalReply?.timestamp ?? null,
      turnSettledAt: events.find((e) => e.type === 'goal.turn_settled')?.at ?? null,
      verificationDispatchedAt: dispatched?.at ?? null,
      finalReplyBeforeDispatch: Boolean(finalReply && dispatched && finalReply.timestamp < dispatched.at),
    };
  } else {
    facts.history = null;
  }
}
facts.events = events.map((e) => `${e.at} ${e.type}${e.payload?.verdict ? ` verdict=${e.payload.verdict}` : ''}${e.payload?.to ? ` to=${e.payload.to}` : ''}${e.payload?.reason ? ` reason=${e.payload.reason}` : ''}`);
console.log(JSON.stringify(facts, null, 2));
