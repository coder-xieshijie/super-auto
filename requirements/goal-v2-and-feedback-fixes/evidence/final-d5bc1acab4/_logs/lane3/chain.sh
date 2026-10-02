#!/usr/bin/env bash
# Electron 第 3 线：S25 S26 S27 S28 S29(+S29b) S31 S33 S39 串行；无效重跑（共 ≤4 次）、FAIL 重跑一次、输入污染 ≤2 次重试
source /tmp/gv2-final/env.sh
L=$M2_ROOT/_logs/lane3; mkdir -p $L
LOG=$L/chain.log
verdict() { python3 /tmp/gv2-final/lane3/verdict.py "$1" 2>/dev/null || echo NOCHECKS; }
runone() {
  local s=$1 a=$2 v v2
  echo "$(date +%T) start $s $a" >>$LOG
  bash $T/m4-electron.sh $s $a >$L/$s-$a.log 2>&1
  echo "$(date +%T) tool rc=$? $s $a" >>$LOG
  python3 $T/m4-analyze.py $s $a >$L/$s-$a.analyze.json 2>&1
  v=$(verdict $M2_ROOT/$s/$a/checks.json)
  if [ "$s" = S29 ]; then
    v2=$(verdict $M2_ROOT/S29b/$a/checks.json)
    echo "$(date +%T) S29b $a $v2" >>$LOG
    case "$v|$v2" in *CONTAM*) v=CONTAM ;; *INVALID*|*NOCHECKS*) v=INVALID ;; *FAIL*) v=FAIL ;; esac
  fi
  echo "$(date +%T) done $s $a $v" >>$LOG
  echo "$v"
}
scenario() {
  local s=$1 n=0 inv=0 fails=0 contam=0 v
  while [ $n -lt 8 ]; do
    n=$((n+1))
    v=$(runone $s f$n)
    case $v in
      OK) return ;;
      FAIL) fails=$((fails+1)); [ $fails -ge 2 ] && return ;;
      CONTAM) contam=$((contam+1)); [ $contam -gt 2 ] && return ;;
      *) inv=$((inv+1)); [ $inv -ge 4 ] && return ;;
    esac
    [ $fails -ge 1 ] && [ "$v" = FAIL ] && continue
  done
}
for s in ${@:-S25 S26 S27 S28 S29 S31 S33 S39}; do scenario $s; done
echo "$(date +%T) chain finished" >>$LOG
