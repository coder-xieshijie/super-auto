#!/usr/bin/env bash
# Acceptance deviations (口径偏差): plan.md entries handed to the verifier by
# run-verifier.mjs --plan, judged in the report, and checked by check-delivery.mjs.
# usage: deliver-deviation-cases.sh <deliver scripts dir>
set -u
S="$1"; CD="$S/check-delivery.mjs"; RV="$S/run-verifier.mjs"
pass=0; failn=0
expect() { local want="$1" label="$2"; shift 2; out="$("$@" 2>&1)"; code=$?
  if [ "$code" = "$want" ]; then pass=$((pass+1)); echo "ok   [$code] $label"; else failn=$((failn+1)); echo "FAIL [$code want $want] $label"; echo "$out" | sed 's/^/     /'; fi; LAST="$out"; }
has() { if echo "$LAST" | grep -q -- "$1"; then pass=$((pass+1)); echo "ok   has: $1"; else failn=$((failn+1)); echo "FAIL missing: $1"; echo "$LAST" | sed 's/^/     /'; fi; }
hasnt() { if echo "$LAST" | grep -q -- "$1"; then failn=$((failn+1)); echo "FAIL unexpected: $1"; echo "$LAST" | sed 's/^/     /'; else pass=$((pass+1)); echo "ok   hasn't: $1"; fi; }
T0=$(( $(date +%s) - 86400 ))
at() { date -r $((T0 + $1 * 60)) +%Y-%m-%dT%H:%M:%S%z; }
iso() { date -u -r $((T0 + $1 * 60)) +%Y-%m-%dT%H:%M:%SZ; }
ci() { GIT_AUTHOR_DATE="$(at $1)" GIT_COMMITTER_DATE="$(at $1)" git -C "$R" commit -q -F -; git -C "$R" rev-parse HEAD; }
sha() { shasum -a 256 "$R/$1" | cut -d' ' -f1; }

T="$(mktemp -d)/dev test"; R="$T/repo"; P="$T/req"; mkdir -p "$R" "$P/evidence" "$T/bin"
git -C "$R" init -q -b base; git -C "$R" config user.email t@t; git -C "$R" config user.name t; git -C "$R" config core.hooksPath /dev/null
echo base > "$R/README.md"; git -C "$R" add -A; B=$(echo base | ci 0); git -C "$R" checkout -q -b feat
mkdir -p "$R/specs"; echo '# spec' > "$R/specs/spec.md"; printf '# verify\nS01 S02\n' > "$R/specs/verify.md"; git -C "$R" add -A
H=$(printf 'docs: hand off\n\nFrozen-Spec: specs/spec.md sha256=%s\nFrozen-Verify: specs/verify.md sha256=%s\n' "$(sha specs/spec.md)" "$(sha specs/verify.md)" | ci 1)
echo a > "$R/a.txt"; git -C "$R" add -A; C=$(echo "feat: a" | ci 10)
body="report M1"; bs=$(printf '%s' "$body" | shasum -a 256 | cut -d' ' -f1)
printf -- '---\nmilestone: M1\nround: 1\nrange: %s..%s\nrecorded_at: %s\nbody_sha256: %s\n---\n%s' "$H" "$C" "$(iso 30)" "$bs" "$body" > "$P/evidence/milestone-M1-r1.md"

ENTRY='- D1 S02 检查点 3；同类：无
  - 字面：完成时请求数 = Inspector 条数
  - 不成立的原因：Inspector 只保存成功的调用（运行 r1：7 对 6）
  - 改用：请求数 = Inspector 条数 + 代理日志中被暂停取消的请求数
  - 推翻后重跑：S02'
D1="### 口径偏差（持续更新）

$ENTRY"
plan() { cat > "$P/plan.md" <<EOF
## 冻结输入
- spec: \`$R/specs/spec.md\` sha256=$(sha specs/spec.md)
- verify: \`$R/specs/verify.md\` sha256=$(sha specs/verify.md)
- 基线: base @ $B
- 交接: https://example/mr/1 feat @ ${H}（t）
- owner: family=anthropic model=claude-opus-5-5

### 决策日志

- 无

$1

## 里程碑
- **M1**（S01、S02）
EOF
}
# what run-verifier --plan would record for the current plan
seen() { node --input-type=module -e "import {parseDeviations} from '$S/deviations.mjs'; import {readFileSync} from 'node:fs'; const {entries}=parseDeviations(readFileSync(process.argv[1],'utf8')); console.log(JSON.stringify(entries.map(d=>({id:d.id,sha256:d.sha256}))))" "$P/plan.md"; }
report() { # report <closing text> <deviations json>
  cat > "$P/evidence/v.md" <<EOF
head: $C
base: $B
验证模型：Codex / gpt-6-astra
verdict: PASS
smoke-regression: PASS
code-issues: 0

| 项 | 结果 | 证据 | 说明 |
|---|---|---|---|
| S01 | PASS | e/1 | |
| S02 | PASS | e/2 | |

冒烟集与回归范围：PASS
代码问题：无
可选建议：无
$1
EOF
  local rs=$(shasum -a 256 "$P/evidence/v.md" | cut -d' ' -f1)
  printf '{"valid":true,"head":"%s","report_sha256":"%s","session_id":"s","model":"gpt-6-astra","family":"openai","problems":[],"first_handoff":null,"deviations":%s}\n' "$C" "$rs" "$2" > "$P/evidence/v.run.json"; }
full() { node "$CD" --plan "$P/plan.md" --report "$P/evidence/v.md" --head $C; }
OK1='口径偏差：
D1：成立；未放宽；代理日志能区分取消的请求'

echo "== no deviations: nothing changes"
plan ""
report "" null
expect 0 "no 口径偏差 section, a record from before --plan existed" full
report "" '[]'
expect 0 "no 口径偏差 section, verifier given the plan" full
hasnt "口径偏差"
plan '## 附：格式示例

```text
## 口径偏差
- D1 S02 检查点 3
```'
report "" null
expect 0 "an example in a code block is not an entry" full

echo "== the verifier must have seen the entries, as they are now"
plan "$D1"
report "$OK1" null
expect 1 "plan has D1, the verifier was given no plan" full
has "was given no plan"
report "$OK1" '[]'
expect 1 "D1 added after the verification" full
has "verifier was given none"
report "$OK1" "$(seen)"
expect 0 "D1 as the verifier saw it" full
has "口径偏差 D1: the verifier judged it valid"
SEEN="$(seen)"
plan "${D1/改用：请求数 = Inspector 条数 + 代理日志中被暂停取消的请求数/改用：请求数不少于 Inspector 条数的一半}"
report "$OK1" "$SEEN"
expect 1 "D1 reworded after the verification" full
has "or a different wording"
plan ""
report "" '[{"id":"D1","sha256":"x"}]'
expect 1 "D1 removed from the plan after the verification" full
has "plan.md records 口径偏差 none"

echo "== the report must judge every entry, in its 口径偏差 section"
plan "$D1"
report "" "$(seen)"
expect 1 "no 口径偏差 section" full
has "no 口径偏差 section"
report "口径偏差：无" "$(seen)"
expect 1 "section without a judgement for D1" full
has "does not judge D1"
report "代码问题之外：本次没有口径偏差
D1：成立；未放宽；x" "$(seen)"
expect 1 "a line that only mentions 口径偏差 is not the section" full
has "no 口径偏差 section"
report '口径偏差：无

```text
D1：成立；未放宽；示例
```' "$(seen)"
expect 1 "an example judgement in a code block does not count" full
has "does not judge D1"
report "口径偏差：
D1：成立；未放宽" "$(seen)"
expect 1 "a judgement without a reason" full
has "gives no reason"

echo "== judged looser"
report "口径偏差：
- D1：成立；放宽；不再检查暂停后没有新请求" "$(seen)"
expect 1 "looser is a stop for the user" full
has "judged 口径偏差 D1 to loosen acceptance (不再检查暂停后没有新请求)"
has "停下 case 1"
report "口径偏差：
D1：成立；放宽；删掉了检查
D1：成立；未放宽；示例" "$(seen)"
expect 1 "a later line does not clear looser" full
has "judged 口径偏差 D1 to loosen acceptance"
has "judges 口径偏差 D1 more than once"

echo "== judged not looser"
report "$OK1" "$(seen)"
expect 0 "valid and not looser" full
report "**口径偏差**：
- **D1**：不成立；未放宽；Inspector 也记录取消的请求，按字面判定" "$(seen)"
expect 0 "not valid, checked literally, bold label" full
has "not valid, so it checked the literal wording"

echo "== entries must be readable and in one section"
plan "## **口径偏差**

* **D1** S02 检查点 3
  - 字面：x
  - 不成立的原因：y
  - 改用：z
  - 推翻后重跑：S02"
report "$OK1" "$(seen)"
expect 0 "bold heading and * items are read" full
has "口径偏差 D1"
plan "### 口径偏差

- S02 检查点 3 按代理日志判定"
report "" '[]'
expect 1 "an entry without an ID" full
has "unrecognized line in the 口径偏差 section"
plan "### 决策日志补充

$ENTRY"
report "" '[]'
expect 1 "an entry outside the section" full
has "belong in the 口径偏差 section"
plan "### 口径偏差

### 其他

### 口径偏差

$ENTRY"
report "$OK1" '[]'
expect 1 "two 口径偏差 sections" full
has "more than one 口径偏差 section"
plan "$D1
- D1 S01 检查点 1
  - 字面：x
  - 不成立的原因：y
  - 改用：z
  - 推翻后重跑：S01"
report "$OK1" '[]'
expect 1 "an ID used twice" full
has "D1 appears twice"
plan "### 口径偏差

- D2 S02 检查点 3
  - 字面：x
  - 不成立的原因：y
  - 改用：
  - 说明：不改用任何方法
  - 推翻后重跑：S02"
report "" '[]'
expect 1 "an empty 改用" full
has "D2 has no non-empty 改用"
plan "### 口径偏差

- D3 检查点 3
  - 字面：x
  - 不成立的原因：y
  - 改用：z
  - 推翻后重跑：S02"
report "" '[]'
expect 1 "an entry that names no scenario" full
has "D3 names no scenario"

echo "== run-verifier hands the entries over in a file"
cat > "$T/bin/codex" <<'EOF'
#!/usr/bin/env bash
if [ "$1" = login ]; then echo "Logged in"; exit 0; fi
out=""; prev=""; for a in "$@"; do [ "$prev" = "-o" ] && out="$a"; prev="$a"; done
echo "model: gpt-6-astra" >&2; echo "session id: fake-$$" >&2
printf '%s\n' "$@" > "$ARGS_OUT"
[ -n "$out" ] && cat "$REPORT_SRC" > "$out"
exit 0
EOF
chmod +x "$T/bin/codex"
export PATH="$T/bin:$PATH" ARGS_OUT="$T/args.txt" REPORT_SRC="$P/evidence/v.md"
git -C "$R" worktree add -q "$T/checkout" $C
printf 'inputs\n' > "$T/inputs.md"; mkdir -p "$T/ev"
plan "$D1"
report "$OK1" '[]'
rv() { node "$RV" --cli codex --checkout "$T/checkout" --head $C --base base --inputs "$T/inputs.md" --verify "$R/specs/verify.md" --report "$T/ev/verification.md" --add-dir "$T/ev" "$@"; }
expect 0 "with --plan" rv --plan "$P/plan.md"
if grep -q "口径偏差（D1）" "$ARGS_OUT" && grep -q "verification.deviations.md" "$ARGS_OUT"; then pass=$((pass+1)); echo "ok   the call names D1 and the file"; else failn=$((failn+1)); echo "FAIL the call"; tail -5 "$ARGS_OUT"; fi
if grep -q "改用：请求数 = Inspector 条数 + 代理日志中被暂停取消的请求数" "$T/ev/verification.deviations.md"; then pass=$((pass+1)); echo "ok   the file quotes D1"; else failn=$((failn+1)); echo "FAIL the file"; fi
if grep -q "改用：请求数" "$ARGS_OUT"; then failn=$((failn+1)); echo "FAIL the entry is on the command line"; else pass=$((pass+1)); echo "ok   the entry is not on the command line"; fi
cp "$T/ev/verification.run.json" "$P/evidence/v.run.json"
python3 - "$P/evidence/v.run.json" "$P/evidence/v.md" <<'PY'
import json,sys,hashlib
r=json.load(open(sys.argv[1])); r['report_sha256']=hashlib.sha256(open(sys.argv[2],'rb').read()).hexdigest(); r['head']=r['head']
json.dump(r,open(sys.argv[1],'w'))
PY
expect 0 "the gate accepts the record run-verifier wrote" full
expect 0 "without --plan" rv
if grep -q "口径偏差" "$ARGS_OUT"; then failn=$((failn+1)); echo "FAIL the call mentions deviations without --plan"; else pass=$((pass+1)); echo "ok   nothing added without --plan"; fi
if grep -q '"deviations": null' "$T/ev/verification.run.json"; then pass=$((pass+1)); echo "ok   the run record says no plan"; else failn=$((failn+1)); echo "FAIL run record without --plan"; grep deviations "$T/ev/verification.run.json"; fi
long="$(head -c 400000 /dev/zero | tr '\0' 'x')"
plan "${D1/推翻后重跑：S02/推翻后重跑：S02
  - 证据摘录：$long}"
expect 0 "a long entry does not hit the argument limit" rv --plan "$P/plan.md"
plan "### 口径偏差

- D9 S02 检查点 3"
expect 2 "a malformed plan stops before the call" rv --plan "$P/plan.md"
has "D9 has no non-empty"

echo "== $pass passed, $failn failed"
