#!/usr/bin/env bash
# spec/verify changed after the first handoff: the user's confirmation line, the
# verifier's section, and run-verifier pointing the verifier at the first handoff.
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
put() { mkdir -p "$(dirname "$R/$2")"; printf '%s\n' "$3" > "$R/$2"; git -C "$R" add -A; printf '%s\n' "$2 $3" | ci "$1"; }
sha() { shasum -a 256 "$R/$1" | cut -d' ' -f1; }
handoff() { printf '%s\n\nFrozen-Spec: specs/spec.md sha256=%s\nFrozen-Verify: specs/verify.md sha256=%s\n' "$2" "$(sha specs/spec.md)" "$(sha specs/verify.md)" | ci "$1"; }
rec() { local body="report $1"; local s=$(printf '%s' "$body" | shasum -a 256 | cut -d' ' -f1)
  printf -- '---\nmilestone: %s\nround: 1\nrange: %s..%s\nrecorded_at: %s\nbody_sha256: %s\n---\n%s' "$1" "$2" "$3" "$(iso $4)" "$s" "$body" > "$P/evidence/milestone-$1-r1.md"; }

T="$(mktemp -d)/rf test"; R="$T/repo"; P="$T/req"; mkdir -p "$R" "$P/evidence" "$T/bin"
git -C "$R" init -q -b base; git -C "$R" config user.email t@t; git -C "$R" config user.name t; git -C "$R" config core.hooksPath /dev/null
echo base > "$R/README.md"; git -C "$R" add -A; B=$(echo base | ci 0); git -C "$R" checkout -q -b feat
mkdir -p "$R/specs"; echo '# spec' > "$R/specs/spec.md"; printf '# verify\nS01 S02\n' > "$R/specs/verify.md"; git -C "$R" add -A
H1=$(handoff 1 "docs: hand off")
C1=$(put 10 a.txt a); rec M1 $H1 $C1 30
printf '# verify\nS01 S02 (S02 checked another way)\n' > "$R/specs/verify.md"; git -C "$R" add -A; H2=$(handoff 40 "docs: change S02")
C2=$(put 60 b.txt b); rec M2 $H2 $C2 80
plan() { cat > "$P/plan.md" <<EOF
## 冻结输入
- spec: \`$R/specs/spec.md\` sha256=$(sha specs/spec.md)
- verify: \`$R/specs/verify.md\` sha256=$(sha specs/verify.md)
- 基线: base @ $B
- 交接: https://example/mr/1 feat @ ${H2}（t）
- owner: family=anthropic model=claude-opus-5-5
$1
## 里程碑
- **M1**（S01）
- **M2**（S02）
EOF
}
report() { # report <extra closing text>
  cat > "$P/evidence/v.md" <<EOF
head: $C2
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
  printf '{"valid":true,"head":"%s","report_sha256":"%s","session_id":"s","model":"gpt-6-astra","family":"openai","problems":[],"first_handoff":%s}\n' "$C2" "$rs" "${FH:-\"$H1\"}" > "$P/evidence/v.run.json"; }
full() { node "$CD" --plan "$P/plan.md" --report "$P/evidence/v.md" --head $C2; }

echo "== frozen-only"
plan ""
expect 1 "verify changed since the first handoff, no confirmation line" node "$CD" --plan "$P/plan.md" --frozen-only
has "verify is not the version of the first handoff"
has "verify changed since the first handoff"
plan "- 重新确认: verify sha256=0000000000000000000000000000000000000000000000000000000000000000 用户 10-01 同意"
expect 1 "a confirmation line for another hash does not count" node "$CD" --plan "$P/plan.md" --frozen-only
plan "- 重新确认: verify sha256=$(sha specs/verify.md)"
expect 1 "a confirmation line without the user's words does not count" node "$CD" --plan "$P/plan.md" --frozen-only
plan "- 重新确认: verify sha256=$(sha specs/verify.md) 用户 2026-10-01：按代理日志核对 S04"
expect 0 "with the user's confirmation" node "$CD" --plan "$P/plan.md" --frozen-only
has "git diff ${H1:0:12}"
hasnt "spec changed"

echo "== full gate"
report ""
expect 1 "the report has no 验收文档改动 section" full
has "no 验收文档改动 section"
report "验收文档改动：S02 的检查改为按代理日志核对，没有放宽。"
expect 0 "with the section" full
FH=null report "验收文档改动：S02 的检查改为按代理日志核对，没有放宽。"
expect 1 "the verifier was not pointed at the first handoff" full
has "pointed at no first handoff"

echo "== run-verifier names the first handoff"
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
git -C "$R" worktree add -q "$T/checkout" $C2
printf 'inputs\n' > "$T/inputs.md"; mkdir -p "$T/ev"
node "$RV" --cli codex --checkout "$T/checkout" --head $C2 --base base --inputs "$T/inputs.md" --verify "$R/specs/verify.md" --report "$T/ev/verification.md" --add-dir "$T/ev" >/dev/null 2>&1
if grep -q "第一次交接（检出目录里的提交 ${H1}）" "$T/args.txt" && grep -q "git show $H1:specs/verify.md" "$T/args.txt"; then pass=$((pass+1)); echo "ok   the call names the first handoff"; else failn=$((failn+1)); echo "FAIL the call does not name the first handoff"; cat "$T/args.txt" | tail -3; fi
if grep -q "\"first_handoff\": \"$H1\"" "$T/ev/verification.run.json"; then pass=$((pass+1)); echo "ok   the run record keeps it"; else failn=$((failn+1)); echo "FAIL run record"; grep first_handoff "$T/ev/verification.run.json"; fi
git -C "$R" worktree add -q "$T/checkout1" $C1
node "$RV" --cli codex --checkout "$T/checkout1" --head $C1 --base base --inputs "$T/inputs.md" --verify "$R/specs/verify.md" --report "$T/ev/verification1.md" --add-dir "$T/ev" >/dev/null 2>&1
if grep -q "第一次交接" "$T/args.txt"; then failn=$((failn+1)); echo "FAIL a single handoff is mentioned"; else pass=$((pass+1)); echo "ok   nothing is added before any change"; fi


echo "== the gate does not switch off"
plan "- 重新确认: verify sha256=$(sha specs/verify.md) 用户 2026-10-01 同意"
sed -i '' '/^- 交接:/d' "$P/plan.md"
expect 0 "without a 交接 line the change is still found" node "$CD" --plan "$P/plan.md" --frozen-only
has "verify changed since the first handoff"
sed -i '' '/^- 重新确认:/d' "$P/plan.md"
expect 1 "and still needs the confirmation" node "$CD" --plan "$P/plan.md" --frozen-only
plan "- 重新确认: verify sha256=$(sha specs/verify.md) 用户 2026-10-01 同意"
sed -i '' 's/^- 基线: base @/- 基线: nosuch @/' "$P/plan.md"
expect 1 "a base branch that is not fetched is an error" node "$CD" --plan "$P/plan.md" --frozen-only
has "base branch nosuch is not in"

# fresh repo helpers for the cases below
fresh() { T="$(mktemp -d)/rf2"; R="$T/repo"; P="$T/req"; mkdir -p "$R" "$P/evidence"
  git -C "$R" init -q -b base; git -C "$R" config user.email t@t; git -C "$R" config user.name t; git -C "$R" config core.hooksPath /dev/null
  echo base > "$R/README.md"; git -C "$R" add -A; B=$(echo base | ci 0); }
handoff2() { # handoff2 <minutes> <subject> <spec path> <verify path>
  printf '%s\n\nFrozen-Spec: %s sha256=%s\nFrozen-Verify: %s sha256=%s\n' "$2" "$3" "$(sha $3)" "$4" "$(sha $4)" | ci "$1"; }
plan2() { # plan2 <spec path> <verify path> <handoff>
  printf '## 冻结输入\n- spec: `%s` sha256=%s\n- verify: `%s` sha256=%s\n- 基线: base @ %s\n- 交接: https://example/mr/1 feat @ %s（t）\n- owner: family=anthropic model=claude-opus-5-5\n## 里程碑\n- **M1**（S01）\n' \
    "$R/$1" "$(sha $1)" "$R/$2" "$(sha $2)" "$B" "$3" > "$P/plan.md"; }
rv() { # rv <head> <verify path>: run the verifier through the fake CLI on a checkout of <head>
  rm -rf "$T/co"; git -C "$R" worktree add -q -f "$T/co" "$1"; mkdir -p "$T/ev2"; printf 'inputs\n' > "$T/in.md"; : > "$ARGS_OUT"
  node "$RV" --cli codex --checkout "$T/co" --head "$1" --base base --inputs "$T/in.md" --verify "$R/$2" --report "$T/ev2/v.md" --add-dir "$T/ev2" >/dev/null 2>&1; }
names() { if grep -q "第一次交接（检出目录里的提交 $2）" "$ARGS_OUT"; then pass=$((pass+1)); echo "ok   $1"; else failn=$((failn+1)); echo "FAIL $1"; grep -o '第一次交接（[^）]*）' "$ARGS_OUT"; fi; }
nothing() { if [ ! -s "$ARGS_OUT" ] || grep -q "第一次交接" "$ARGS_OUT"; then failn=$((failn+1)); echo "FAIL $1"; else pass=$((pass+1)); echo "ok   $1"; fi; }

echo "== only spec changed in the new handoff"
fresh; git -C "$R" checkout -q -b feat; mkdir -p "$R/s"; echo spec > "$R/s/spec.md"; printf 'S01\n' > "$R/s/verify.md"; git -C "$R" add -A
H1=$(handoff2 1 h1 s/spec.md s/verify.md); echo spec2 > "$R/s/spec.md"; git -C "$R" add -A; H2=$(handoff2 2 h2 s/spec.md s/verify.md)
rv $H2 s/verify.md; names "the verifier is told about the spec change" $H1

echo "== verify moved in the new handoff"
fresh; git -C "$R" checkout -q -b feat; mkdir -p "$R/s"; echo spec > "$R/s/spec.md"; printf 'S01\n' > "$R/s/verify.md"; git -C "$R" add -A
H1=$(handoff2 1 h1 s/spec.md s/verify.md); git -C "$R" mv s/verify.md s/checks.md; printf 'S01 looser\n' > "$R/s/checks.md"; git -C "$R" add -A
H2=$(handoff2 2 h2 s/spec.md s/checks.md)
rv $H2 s/checks.md; names "the verifier is told about the first version" $H1
plan2 s/spec.md s/checks.md $H2
expect 1 "the gate wants the confirmation" node "$CD" --plan "$P/plan.md" --frozen-only
has "verify is not the version of the first handoff"

echo "== an older requirement on the base branch uses the same paths"
fresh; mkdir -p "$R/s"; echo old > "$R/s/spec.md"; printf 'S01 old\n' > "$R/s/verify.md"; git -C "$R" add -A; handoff2 1 h0 s/spec.md s/verify.md >/dev/null
B=$(git -C "$R" rev-parse base)
git -C "$R" checkout -q -b feat; echo new > "$R/s/spec.md"; printf 'S01 new\n' > "$R/s/verify.md"; git -C "$R" add -A; H1=$(handoff2 2 h1 s/spec.md s/verify.md)
rv $H1 s/verify.md; nothing "nothing is added for an unchanged requirement"
plan2 s/spec.md s/verify.md $H1
expect 0 "the gate sees no change" node "$CD" --plan "$P/plan.md" --frozen-only

echo "== two requirements on one branch"
fresh; git -C "$R" checkout -q -b feat; mkdir -p "$R/a" "$R/b"; echo a > "$R/a/spec.md"; printf 'S01 a\n' > "$R/a/verify.md"; git -C "$R" add -A; handoff2 1 ha a/spec.md a/verify.md >/dev/null
echo b > "$R/b/spec.md"; printf 'S01 b\n' > "$R/b/verify.md"; git -C "$R" add -A; HB=$(handoff2 2 hb b/spec.md b/verify.md)
plan2 b/spec.md b/verify.md $HB
expect 0 "requirement B is compared with its own handoff" node "$CD" --plan "$P/plan.md" --frozen-only
hasnt "changed since the first handoff"

echo "== $pass passed, $failn failed"
