#!/usr/bin/env bash
# Electron A 线（第二轮，被测 eb1b2af271）：串行跑 S01、S16(hold/nohold)、S17、S19、S20；同一时刻只有本线一个 Electron。
# 无效重跑上限 4 次；FAIL 重跑一次确认；输入污染最多重试 2 次。尝试名 f1、f2……
source /tmp/gv2-final2/env.sh
L=$M2_ROOT/_logs/lane-a
LOG=$L/chain.log
S01_FROM=20261001-233215-00aeb4
runone() { # runone <scenario> <attempt>
  local s=$1 a=$2 tool an
  case $s in
    S01) tool="bash $T/m2-electron.sh S01 $a $S01_FROM"; an="python3 $T/m2-analyze.py S01 $a" ;;
    S19|S20) tool="bash $T/m3-electron.sh $s $a"; an="python3 $T/m3-analyze.py $s $a" ;;
    S17) tool="bash $T/m3-electron.sh $s $a"; an="python3 $T/m4-analyze.py $s $a" ;;
    S16) tool="bash $T/m4-electron.sh S16 $a"; an="python3 $T/m4-analyze.py S16 $a" ;;
  esac
  echo "$(date +%T) start $s $a mode=${S16_MODE:-}" >>$LOG
  $tool > $L/$s-$a.log 2>&1
  echo "$(date +%T) tool rc=$? $s $a" >>$LOG
  $an > $L/$s-$a.analyze.json 2>&1
  echo "$(date +%T) analyze rc=$? $s $a" >>$LOG
  local v
  v=$(python3 $L/verdict.py $M2_ROOT/$s/$a/checks.json 2>/dev/null || echo NOCHECKS)
  echo "$(date +%T) done $s $a $v" >>$LOG
  echo "$v"
}
nextrun() { local s=$1 n=1; while [ -e "$M2_ROOT/$s/f$n" ]; do n=$((n+1)); done; echo f$n; }
scenario() {
  local s=$1 max=${2:-4} i=1 fails=0 contam=0 v
  while [ $i -le $((max + 2)) ]; do
    v=$(runone $s $(nextrun $s))
    case $v in
      OK) return ;;
      FAIL) fails=$((fails+1)); [ $fails -ge 2 ] && return ;;
      CONTAM) contam=$((contam+1)); [ $contam -gt 2 ] && return ;;
      *) i=$((i+1)); [ $i -gt $max ] && return ;;
    esac
  done
}
for s in "$@"; do
  if [ "$s" = S16 ]; then
    for m in hold nohold; do
      n=0; f=0; while :; do export S16_MODE=$m; v=$(runone S16 $(nextrun S16)); n=$((n+1)); case $v in OK) break;; FAIL) f=$((f+1)); [ $f -ge 2 ] && break;; *) [ $n -ge 4 ] && break;; esac; done
    done
    unset S16_MODE
  else
    scenario $s 4
  fi
done
echo "$(date +%T) chain finished: $*" >>$LOG
