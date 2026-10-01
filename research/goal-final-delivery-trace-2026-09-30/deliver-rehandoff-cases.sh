#!/usr/bin/env bash
# Milestone records when the user changes spec/verify mid-delivery and hands off again.
set -u
S="$1"; CD="$S/check-delivery.mjs"
pass=0; failn=0
expect() { local want="$1" label="$2"; shift 2; out="$("$@" 2>&1)"; code=$?
  if [ "$code" = "$want" ]; then pass=$((pass+1)); echo "ok   [$code] $label"; else failn=$((failn+1)); echo "FAIL [$code want $want] $label"; echo "$out" | sed 's/^/     /'; fi; LAST="$out"; }
has() { if echo "$LAST" | grep -q -- "$1"; then pass=$((pass+1)); echo "ok   has: $1"; else failn=$((failn+1)); echo "FAIL missing: $1"; echo "$LAST" | sed 's/^/     /'; fi; }
T0=$(( $(date +%s) - 86400 ))
at() { date -r $((T0 + $1 * 60)) +%Y-%m-%dT%H:%M:%S%z; }
iso() { date -u -r $((T0 + $1 * 60)) +%Y-%m-%dT%H:%M:%SZ; }
ci() { GIT_AUTHOR_DATE="$(at $1)" GIT_COMMITTER_DATE="$(at $1)" git -C "$R" commit -q -F -; git -C "$R" rev-parse HEAD; }
put() { mkdir -p "$(dirname "$R/$2")"; printf '%s\n' "$3" > "$R/$2"; git -C "$R" add -A; printf '%s\n' "$2 $3" | ci "$1"; }
sha() { shasum -a 256 "$R/$1" | cut -d' ' -f1; }
handoff() { # handoff <minutes> <subject>: commit the staged spec/verify with both trailers
  printf '%s\n\nFrozen-Spec: specs/spec.md sha256=%s\nFrozen-Verify: specs/verify.md sha256=%s\n' "$2" "$(sha specs/spec.md)" "$(sha specs/verify.md)" | ci "$1"; }
setup() {
  T="$(mktemp -d)/rh test"; R="$T/repo"; P="$T/req"; mkdir -p "$R" "$P/evidence"
  git -C "$R" init -q -b base; git -C "$R" config user.email t@t; git -C "$R" config user.name t; git -C "$R" config core.hooksPath /dev/null
  echo base > "$R/README.md"; git -C "$R" add -A; B=$(echo base | ci 0)
  git -C "$R" checkout -q -b feat
  mkdir -p "$R/specs"; echo '# spec' > "$R/specs/spec.md"; echo '# verify S01 S02' > "$R/specs/verify.md"; git -C "$R" add -A
  H1=$(handoff 1 "docs: hand off")
}
plan() { # plan <handoff sha> [extra frozen-input line]
  cat > "$P/plan.md" <<EOF
## 冻结输入
- spec: \`$R/specs/spec.md\` sha256=$(sha specs/spec.md)
- verify: \`$R/specs/verify.md\` sha256=$(sha specs/verify.md)
- 基线: base @ $B
- 交接: https://example/mr/1 feat @ $1（t）
- owner: family=anthropic model=claude-opus-5-5
${2:-}
## 里程碑
- **M1**（S01）
- **M2**（S02）
EOF
}
rec() { local body="report $1 r$2"; local s=$(printf '%s' "$body" | shasum -a 256 | cut -d' ' -f1)
  printf -- '---\nmilestone: %s\nround: %s\nrange: %s..%s\nrecorded_at: %s\nbody_sha256: %s\n---\n%s' "$1" "$2" "$3" "$4" "$(iso $5)" "$s" "$body" > "$P/evidence/milestone-$1-r$2.md"; }
ms() { node "$CD" --plan "$P/plan.md" --milestones-only --head "$(git -C "$R" rev-parse HEAD)"; }

echo "== 1: the user changes verify after M1 and hands off again"
setup
C1=$(put 10 a.txt a); C2=$(put 20 b.txt b)
rec M1 1 $H1 $C2 30
echo '# verify S01 S02 (S02 changed)' > "$R/specs/verify.md"; git -C "$R" add -A; H2=$(handoff 40 "docs: change S02")
C3=$(put 60 c.txt c); C4=$(put 70 d.txt d)
rec M2 1 $H2 $C4 80
plan $H2
expect 0 "M1's record still counts" ms
has "counting the owner's commits from the first handoff"
has "2 for M1, M2"
has "4 of 4 branch commits covered"
plan $H1
expect 0 "with the old 交接 line the result is the same" ms

echo "== 2: the new handoff was committed before M1's record was saved"
setup
C1=$(put 10 a.txt a); C2=$(put 20 b.txt b)
echo '# verify changed' > "$R/specs/verify.md"; git -C "$R" add -A; H2=$(handoff 25 "docs: change verify")
rec M1 1 $H1 $C2 30
C3=$(put 60 c.txt c); rec M2 1 $H2 $C3 80
plan $H2
expect 0 "the handoff commit is not M1's next commit" ms

echo "== 3: a handoff commit that also changes code needs a check"
setup
C1=$(put 10 a.txt a); rec M1 1 $H1 $C1 30
echo '# verify changed' > "$R/specs/verify.md"; echo tool > "$R/tool.sh"; git -C "$R" add -A; H2=$(handoff 40 "docs: change verify and add a tool")
C3=$(put 60 c.txt c); rec M2 1 $H2 $C3 80
plan $H2
expect 1 "its code change is not covered" ms
has "change verify and add a tool lies between checked ranges"

echo "== 4: a record whose range spans the new handoff commit"
setup
C1=$(put 10 a.txt a); rec M1 1 $H1 $C1 30
echo '# verify changed' > "$R/specs/verify.md"; git -C "$R" add -A; H2=$(handoff 40 "docs: change verify")
C3=$(put 60 c.txt c); rec M2 1 $C1 $C3 80
plan $H2
expect 0 "the handoff commit inside the range is skipped quietly" ms
if echo "$LAST" | grep -q "no longer on the branch"; then failn=$((failn+1)); echo "FAIL the handoff commit was reported as gone"; else pass=$((pass+1)); echo "ok   no note about a missing commit"; fi

echo "== 5: no 交接 line, only 基线: unchanged behaviour"
setup
C1=$(put 10 a.txt a); rec M1 1 $B $C1 30; C2=$(put 60 c.txt c); rec M2 1 $C1 $C2 80
plan $H1; sed -i '' '/^- 交接:/d' "$P/plan.md"
expect 0 "a baseline-only plan still passes" ms
has "3 of 3 branch commits covered"


echo "== R1: a merge handoff that also brings in code"
setup
A=$(put 10 a.txt a); rec M1 1 $H1 $A 30
git -C "$R" checkout -q -b side
echo '# verify changed' > "$R/specs/verify.md"; echo x > "$R/unreviewed.js"; git -C "$R" add -A; echo side | ci 20 >/dev/null
git -C "$R" checkout -q feat
GIT_AUTHOR_DATE="$(at 25)" GIT_COMMITTER_DATE="$(at 25)" git -C "$R" merge -q --no-ff side -m "$(printf 'merge handoff\n\nFrozen-Spec: specs/spec.md sha256=%s\nFrozen-Verify: specs/verify.md sha256=%s' "$(sha specs/spec.md)" "$(sha specs/verify.md)")"
H2=$(git -C "$R" rev-parse HEAD); Bc=$(put 60 b.txt b); rec M2 1 $H2 $Bc 80
plan $H2
expect 1 "the merge is not skipped" ms
has "merge handoff lies between checked ranges"

echo "== R2: trailers written with ./ paths"
setup
A=$(put 10 a.txt a)
echo '# verify changed' > "$R/specs/verify.md"; git -C "$R" add -A
H2=$(printf 'docs: change verify\n\nFrozen-Spec: ./specs/spec.md sha256=%s\nFrozen-Verify: ./specs/verify.md sha256=%s\n' "$(sha specs/spec.md)" "$(sha specs/verify.md)" | ci 25)
rec M1 1 $H1 $A 30; Bc=$(put 60 b.txt b); rec M2 1 $H2 $Bc 80
plan $H2
expect 0 "the ./ handoff is skipped like the plain one" ms

echo "== R3: a folded trailer that read-handoff rejects is not a handoff"
T="$(mktemp -d)/rh test"; R="$T/repo"; P="$T/req"; mkdir -p "$R" "$P/evidence"
git -C "$R" init -q -b base; git -C "$R" config user.email t@t; git -C "$R" config user.name t; git -C "$R" config core.hooksPath /dev/null
echo base > "$R/README.md"; git -C "$R" add -A; B=$(echo base | ci 0); git -C "$R" checkout -q -b feat
mkdir -p "$R/specs"; echo '# spec' > "$R/specs/spec.md"; echo '# verify S01 S02' > "$R/specs/verify.md"; git -C "$R" add -A
printf 'draft\n\nFrozen-Spec: specs/\n spec.md sha256=%s\nFrozen-Verify: specs/verify.md sha256=%s\n' "$(sha specs/spec.md)" "$(sha specs/verify.md)" | ci 1 >/dev/null
echo prep > "$R/prep.txt"; git -C "$R" add -A; echo prep | ci 2 >/dev/null
echo '# verify S01 S02 final' > "$R/specs/verify.md"; git -C "$R" add -A; H=$(handoff 3 "docs: hand off")
A=$(put 10 a.txt a); rec M1 1 $H $A 30; Bc=$(put 60 b.txt b); rec M2 1 $A $Bc 80
plan $H
expect 0 "counting starts at the real handoff" ms

echo "== $pass passed, $failn failed"
