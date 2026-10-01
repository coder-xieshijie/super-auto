#!/usr/bin/env bash
# Electron 链：逐个场景串行；无效（前提/登录）重跑至上限，FAIL 重跑一次
source /tmp/gv2-m4/env.sh
LOG=/tmp/gv2-m4/chain-e.log
runone() { # runone <scenario> <attempt> : run + analyze, echo verdict
  local s=$1 a=$2 tool an
  case $s in
    S12|S12b|S15|S19|S20|S21) tool="bash $T/m3-electron.sh $s $a"; an="python3 $T/m3-analyze.py $s $a" ;;
    S14|S17) tool="bash $T/m3-electron.sh $s $a"; an="python3 $T/m4-analyze.py $s $a" ;;
    S10) tool="bash $T/m2-electron.sh S10 $a"; an="python3 $T/m2-analyze.py S10 $a" ;;
    S16) tool="bash $T/m4-electron.sh S16 $a"; an="python3 $T/m4-analyze.py S16 $a" ;;
    *) tool="bash $T/m4-electron.sh $s $a"; an="python3 $T/m4-analyze.py $s $a" ;;
  esac
  echo "$(date +%T) start $s $a" >>$LOG
  $tool > /tmp/gv2-m4/$s-$a.log 2>&1
  $an > /tmp/gv2-m4/$s-$a.analyze.json 2>&1
  local v
  v=$(python3 /tmp/gv2-m4/verdict.py $M2_ROOT/$s/$a/checks.json 2>/dev/null || echo NOCHECKS)
  echo "$(date +%T) done $s $a $v" >>$LOG
  echo "$v"
}
nextrun() { local s=$1 n=1; while [ -e "$M2_ROOT/$s/run$n" ]; do n=$((n+1)); done; echo run$n; }
scenario() { # scenario <S> [maxInvalid]：从下一个未用的 runN 开始
  local s=$1 max=${2:-3} i=1 fails=0 contam=0 v
  while [ $i -le $max ]; do
    v=$(runone $s $(nextrun $s))
    case $v in
      OK) return ;;
      FAIL) fails=$((fails+1)); [ $fails -ge 2 ] && return ;;
      CONTAM) contam=$((contam+1)); [ $contam -ge 2 ] && return ;;
      *) ;;
    esac
    i=$((i+1))
  done
}
for s in ${@:-S24 S26 S22 S23 S28 S39 S27 S29 S31 S33 S03 S14 S17 S12 S12b S15 S19 S20 S21}; do
  if [ "$s" = S16 ]; then
    export S16_MODE=hold; v=$(runone S16 run1)
    export S16_MODE=nohold; v2=$(runone S16 run2-nohold)
    if [ "$v" != OK ]; then export S16_MODE=hold; runone S16 run3 >/dev/null; fi
    unset S16_MODE
  elif [ "$s" = S10 ]; then
    scenario S10 6
  else
    scenario $s 3
  fi
done
echo "$(date +%T) chain finished" >>$LOG
