#!/usr/bin/env bash
# Milestone records across a rebase onto a newer base, and which check is timed.
set -u
S="$1"; CD="$S/check-delivery.mjs"
pass=0; failn=0
expect() { local want="$1" label="$2"; shift 2; out="$("$@" 2>&1)"; code=$?
  if [ "$code" = "$want" ]; then pass=$((pass+1)); echo "ok   [$code] $label"; else failn=$((failn+1)); echo "FAIL [$code want $want] $label"; echo "$out" | sed 's/^/     /'; fi; LAST="$out"; }
has() { if echo "$LAST" | grep -q -- "$1"; then pass=$((pass+1)); echo "ok   has: $1"; else failn=$((failn+1)); echo "FAIL missing: $1"; echo "$LAST" | sed 's/^/     /'; fi; }
T0=$(( $(date +%s) - 86400 ))
at() { date -r $((T0 + $1 * 60)) +%Y-%m-%dT%H:%M:%S%z; }
iso() { date -u -r $((T0 + $1 * 60)) +%Y-%m-%dT%H:%M:%SZ; }
ci() { GIT_AUTHOR_DATE="$(at $1)" GIT_COMMITTER_DATE="$(at $1)" git -C "$R" commit -qm "$2"; git -C "$R" rev-parse HEAD; }
put() { mkdir -p "$(dirname "$R/$2")"; printf '%s\n' "$3" > "$R/$2"; git -C "$R" add -A; ci "$1" "$2 $3"; }
setup() { # base: a.txt 1..10, x.js 1..30; handoff on feat
  T="$(mktemp -d)/rb test"; R="$T/repo"; P="$T/req"; mkdir -p "$R" "$P/evidence"
  git -C "$R" init -q -b base; git -C "$R" config user.email t@t; git -C "$R" config user.name t; git -C "$R" config core.hooksPath /dev/null
  seq 1 10 > "$R/a.txt"; seq 1 30 > "$R/x.js"; echo r0 > "$R/r.txt"; git -C "$R" add -A; B=$(ci 0 base)
  git -C "$R" checkout -q -b feat
  mkdir -p "$R/specs"; echo '# spec' > "$R/specs/spec.md"; echo '# verify S01 S02' > "$R/specs/verify.md"; git -C "$R" add -A; H=$(ci 1 handoff)
  plan "$H" ""
}
plan() { SS=$(shasum -a 256 "$R/specs/spec.md" | cut -d' ' -f1); VS=$(shasum -a 256 "$R/specs/verify.md" | cut -d' ' -f1)
  cat > "$P/plan.md" <<EOF
## 冻结输入
- spec: \`$R/specs/spec.md\` sha256=$SS
- verify: \`$R/specs/verify.md\` sha256=$VS
- 基线: base @ $B
- 交接: https://example/mr/1 feat @ $1（t）
- owner: family=anthropic model=claude-opus-5-5
$2
## 里程碑
- **M1**（S01）
- **M2**（S02）
EOF
}
rec() { local body="report $1 r$2"; local sha=$(printf '%s' "$body" | shasum -a 256 | cut -d' ' -f1)
  printf -- '---\nmilestone: %s\nround: %s\nrange: %s..%s\nrecorded_at: %s\nbody_sha256: %s\n---\n%s' "$1" "$2" "$3" "$4" "$(iso $5)" "$sha" "$body" > "$P/evidence/milestone-$1-r$2.md"; }
ms() { node "$CD" --plan "$P/plan.md" --milestones-only --head "$(git -C "$R" rev-parse HEAD)"; }
handoff() { git -C "$R" log --format=%H --grep='^handoff$' -1 HEAD; }

echo "== 1: clean rebase; the base now has one checked commit and changed lines near two others"
setup
C1=$(put 10 r.txt r1)                                            # item 2, also in its own MR
sed -i '' 's/^5$/five/' "$R/a.txt"; git -C "$R" add -A; C2=$(ci 20 "a.txt five")
git -C "$R" mv x.js y.js; sed -i '' 's/^25$/twenty-five/' "$R/y.js"; git -C "$R" add -A; C3=$(ci 25 "rename x.js and edit")
C4=$(put 60 b.txt b); C5=$(put 70 c.txt c)
rec M1 1 $H $C3 30; rec M2 1 $C3 $C5 80
expect 0 "before the rebase" ms
git -C "$R" checkout -q base
echo r1 > "$R/r.txt"; echo x > "$R/other.txt"; git -C "$R" add -A; ci 90 "item 2 squashed" >/dev/null
sed -i '' 's/^3$/three/' "$R/a.txt"; sed -i '' 's/^22$/twenty-two/' "$R/x.js"; git -C "$R" add -A; ci 95 "upstream edits" >/dev/null
git -C "$R" checkout -q feat; git -C "$R" rebase -q base >/dev/null 2>&1
expect 1 "old handoff SHA is not an ancestor" ms
has "not an ancestor"
plan "$(handoff)" ""
expect 0 "records still count after the handoff line is updated" ms
has "of its 3 commits, 1 no longer on the branch"
has "2 for M1, M2"
has "4 of 4 branch commits covered"

echo "== 2: a rebase conflict changed M1's last commit"
setup
C1=$(put 10 f1.txt f1); sed -i '' 's/^5$/five/' "$R/a.txt"; git -C "$R" add -A; C2=$(ci 20 "a.txt five")
C3=$(put 60 b.txt b); C4=$(put 70 c.txt c)
rec M1 1 $H $C2 30; rec M2 1 $C2 $C4 80
git -C "$R" checkout -q base; sed -i '' 's/^5$/FIVE/' "$R/a.txt"; git -C "$R" add -A; ci 90 "upstream FIVE" >/dev/null
git -C "$R" checkout -q feat; git -C "$R" rebase -q base >/dev/null 2>&1
sed -i '' -e '/^<<<<<<<\|^=======\|^>>>>>>>/d' "$R/a.txt"; sed -i '' -e '/^FIVE$/d' -e 's/^five$/five-FIVE/' "$R/a.txt"
git -C "$R" add a.txt; GIT_EDITOR=true git -C "$R" rebase --continue >/dev/null 2>&1
plan "$(handoff)" ""
expect 1 "the changed commit needs a new check" ms
has "a.txt five changed after milestone-M1-r1.md checked it"
N1=$(git -C "$R" log --format=%H --grep='^f1.txt' -1); N2=$(git -C "$R" log --format=%H --grep='^a.txt five' -1)
rec M1 2 $N1 $N2 200
expect 0 "round 2 over it, recorded long after, is not timed" ms

echo "== 3: a late first check hidden behind a later round over M2's commits"
setup
C1=$(put 10 f1.txt f1); C2=$(put 20 f2.txt f2); C3=$(put 60 b.txt b); C4=$(put 70 c.txt c)
rec M1 1 $H $C2 65; rec M1 2 $C2 $C4 66; rec M2 1 $C2 $C4 80
expect 1 "M1's first check is still late" ms
has "M1 round 1 was recorded"

echo "== 4: every commit of M1's first check changed; round 2 is the first that counts"
setup
C1=$(put 10 f1.txt f1); C2=$(put 20 f2.txt f2)
rec M1 1 $H $C2 30
git -C "$R" reset -q --hard $H; D1=$(put 10 f1.txt f1-v2); D2=$(put 20 f2.txt f2-v2); D3=$(put 60 b.txt b); D4=$(put 70 c.txt c)
rec M2 1 $D2 $D4 80; rec M1 2 $H $D2 90
expect 1 "its time is checked" ms
has "first check that still matches the branch"
has "milestone-M1-r1.md no longer matches the branch"
plan "$H" "- milestone-order: waived 用户 2026-09-30 同意"
expect 0 "the user can waive it" ms

echo "== 5: a later round over a fix is not timed"
setup
C1=$(put 10 f1.txt f1); C2=$(put 20 f2.txt f2); C3=$(put 60 b.txt b); C4=$(put 70 c.txt c)
C5=$(put 100 f1.txt f1-fix); C6=$(put 110 d.txt d)
rec M1 1 $H $C2 30; rec M2 1 $C2 $C4 80; rec M1 2 $C4 $C5 120
expect 0 "M1 round 2 recorded after the next commit" ms

echo "== 6: a whitespace change in an added line is a different change"
setup
C1=$(put 10 f1.txt "f1"); C2=$(put 60 b.txt b)
rec M1 1 $H $C1 30; rec M2 1 $C1 $C2 80
git -C "$R" reset -q --hard $H; E1=$(put 10 f1.txt "f1 "); E2=$(put 60 b.txt b)
expect 1 "the old record does not cover it" ms
has "f1.txt f1 changed after"


# raw <minutes> <message>: commit what is staged with the given time and message
raw() { ci "$1" "$2"; }

echo "== F1: a binary file whose checked content was replaced"
setup
printf '\x00\x01' > "$R/asset.bin"; git -C "$R" add -A; raw 5 "add asset" >/dev/null; H5=$(git -C "$R" rev-parse HEAD)
printf '\x00\x02' > "$R/asset.bin"; git -C "$R" add -A; A=$(raw 10 "update asset")
rec M1 1 $H5 $A 30
git -C "$R" reset -q --hard $H5; printf '\x00\x03' > "$R/asset.bin"; git -C "$R" add -A; A2=$(raw 10 "update asset"); Bm=$(put 60 b.txt b)
rec M2 1 $A2 $Bm 80
expect 1 "the new binary content needs a check" ms
has "update asset changed after milestone-M1-r1.md checked it"

echo "== F2: a later round cannot hide a late first check behind another milestone's changed commit"
setup
A=$(put 10 f1.txt f1); echo b > "$R/b.txt"; git -C "$R" add -A; B1=$(raw 20 "m2 work")
rec M1 1 $H $A 30; rec M2 1 $A $B1 40
git -C "$R" reset -q --hard $A; echo b2 > "$R/b.txt"; git -C "$R" add -A; B2=$(raw 20 "m2 work")
rec M1 2 $A $B2 50; rec M2 2 $A $B2 50
expect 1 "M1's first check is still late" ms
has "M1 round 1 was recorded"

echo "== F3: the same edit in two places, then a clean rebase"
setup
printf 'f() {\n  return false;\n}\n%s\ng() {\n  return false;\n}\n' "$(seq 1 15)" > "$R/two.js"; git -C "$R" add -A; H5=$(raw 5 "add two.js")
plan "$H5" ""
perl -0pi -e 's/return false;/return true;/' "$R/two.js"; git -C "$R" add -A; X1=$(raw 10 "f returns true")
perl -0pi -e 's/return false;/return true;/' "$R/two.js"; git -C "$R" add -A; X2=$(raw 20 "g returns true")
X3=$(put 60 b.txt b)
rec M1 1 $H5 $X2 30; rec M2 1 $X2 $X3 80
git -C "$R" checkout -q base; echo x > "$R/other.txt"; git -C "$R" add -A; ci 90 "upstream" >/dev/null
git -C "$R" checkout -q feat; git -C "$R" rebase -q base >/dev/null 2>&1
plan "$(git -C "$R" log --format=%H --grep='^add two.js$' -1)" ""
expect 0 "both checked commits map to their own rebased commits" ms
has "3 of 3 branch commits covered"

echo "== F5: an added line that looks like a file header, newline at the end changed"
setup
printf 'base\n' > "$R/h.txt"; git -C "$R" add -A; H5=$(raw 5 "add h.txt"); plan "$H5" ""
printf '++ payload' > "$R/h.txt"; git -C "$R" add -A; A=$(raw 10 "payload")
rec M1 1 $H5 $A 30
git -C "$R" reset -q --hard $H5; printf '++ payload\n' > "$R/h.txt"; git -C "$R" add -A; A2=$(raw 10 "payload")
expect 1 "the changed newline needs a check" ms
has "payload changed after"

echo "== F6: non-UTF-8 bytes"
setup
printf 'a\n' > "$R/l.txt"; git -C "$R" add -A; H5=$(raw 5 "add l.txt"); plan "$H5" ""
printf '\xe9\n' > "$R/l.txt"; git -C "$R" add -A; A=$(raw 10 "latin")
rec M1 1 $H5 $A 30
git -C "$R" reset -q --hard $H5; printf '\xf1\n' > "$R/l.txt"; git -C "$R" add -A; A2=$(raw 10 "latin")
expect 1 "different bytes are a different change" ms
has "latin changed after"

echo "== F7: the last commit of a check changed, nothing after it"
setup
A=$(put 10 f1.txt f1); echo b > "$R/b.txt"; git -C "$R" add -A; B1=$(raw 20 "m1 tail")
rec M1 1 $H $B1 30
git -C "$R" reset -q --hard $A; echo b2 > "$R/b.txt"; git -C "$R" add -A; B2=$(raw 20 "m1 tail")
expect 1 "the changed tail needs a check" ms
has "m1 tail changed after milestone-M1-r1.md checked it"
rec M1 2 $A $B2 200
plan "$H" ""
expect 1 "M2 still has no record" ms
has "M2 has no milestone check record"

echo "== $pass passed, $failn failed"
