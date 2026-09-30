#!/usr/bin/env bash
# RG1 TUI 入口：功能地图索引“TUI”列的全部子功能，命令照抄各地图“TUI”一节。
# 每个流程起自己的 TUI 实例（tui up --config $RG1_CONFIG，staging/cn），跑完 tui snapshot、tui down、整理证据。
# 用法（agent-archon worktree 根目录）：
#   RG1_ROOT=<证据根> RG1_TAG=<前缀> [RG1_FLOWS="lifecycle continuation-bg ..."] bash <tools>/rg1-tui.sh
# 流程：lifecycle（含 completion 的 TUI 核对）continuation-bg limits attachments questionnaire-manual questionnaire-auto
set -u
source "$(dirname "${BASH_SOURCE[0]}")/rg1-lib.sh"

# 等轮次结束：状态栏 state 不是 run，并保持 3 秒
tui_idle() { vr tui wait --status "state=ready|done|fail|cancel|error" --hold 3 --timeout "${1:-180}" ${2:+--save "$2"}; }

flow_lifecycle() {
  rg1_up tui lifecycle || return 1
  # 创建
  vr tui type "/goal $OBJ_COUNT3" >/dev/null
  vr tui wait --text "◎ Goal · Active" --timeout 30 --save "$T-lifecycle.create--active" >/dev/null
  vr tui snapshot --save "$T-lifecycle.create--snap" >/dev/null
  # 暂停
  vr tui type "/goal pause" >/dev/null
  vr tui wait --text "◎ Goal · Paused" --timeout 30 --save "$T-lifecycle.pause--paused" >/dev/null
  tui_idle 60 "$T-lifecycle.pause--idle" >/dev/null
  vr tui snapshot --save "$T-lifecycle.pause--snap" >/dev/null
  # 查看摘要（空闲时）
  vr tui type "/goal" --no-submit >/dev/null
  vr tui keys escape >/dev/null
  vr tui keys enter >/dev/null
  vr tui wait --text "Objective:" --timeout 15 --save "$T-lifecycle.summary--summary" >/dev/null
  vr tui snapshot --save "$T-lifecycle.summary--snap" >/dev/null
  # 暂停时改目标
  vr tui type "/goal $OBJ_COUNT4" >/dev/null
  vr tui wait --text "Goal objective updated" --timeout 15 --save "$T-lifecycle.edit-paused--updated" >/dev/null
  vr tui wait --text "◎ Goal · Paused" --hold 8 --timeout 20 --save "$T-lifecycle.edit-paused--hold" >/dev/null
  vr tui snapshot --save "$T-lifecycle.edit-paused--snap" >/dev/null
  # 恢复并跑到完成
  vr tui type "/goal resume" >/dev/null
  vr tui wait --text "Goal resumed" --timeout 15 --save "$T-lifecycle.resume--resumed" >/dev/null
  vr tui snapshot --save "$T-lifecycle.resume--snap" >/dev/null
  vr tui wait --text "Goal complete" --timeout 420 --save "$T-lifecycle.complete--complete" >/dev/null
  tui_idle 120 "$T-lifecycle.complete--idle" >/dev/null
  vr tui snapshot --save "$T-lifecycle.complete--snap" >/dev/null
  # completion.md TUI：完成（验证横幅、✓ Goal complete）、最终回复（完成轮的错误行与状态栏）
  vr tui screen --save "$T-completion.complete--screen" >/dev/null
  vr tui snapshot --save "$T-completion.complete--snap" >/dev/null
  vr tui screen --all --save "$T-completion.final-reply--screen" >/dev/null
  vr tui snapshot --save "$T-completion.final-reply--snap" >/dev/null
  # 完成后替换
  vr tui type "/goal $OBJ_DONE" >/dev/null
  vr tui wait --text "◎ Goal · Active" --timeout 30 --save "$T-lifecycle.replace--active" >/dev/null
  vr tui snapshot --save "$T-lifecycle.replace--snap" >/dev/null
  # 清除
  vr tui type "/goal clear" >/dev/null
  vr tui wait --text "Goal cleared" --timeout 30 --save "$T-lifecycle.clear--cleared" >/dev/null
  tui_idle 120 "$T-lifecycle.clear--idle" >/dev/null
  vr tui snapshot --save "$T-lifecycle.clear--snap" >/dev/null
  rg1_down tui tui
}

flow_continuation_bg() {
  rg1_up tui continuation-bg || return 1
  vr tui type "/goal $OBJ_BG" >/dev/null
  vr tui wait --text "Waiting for background tasks" --timeout 150 --save "$T-continuation.background--waiting" >/dev/null
  vr tui wait --text "Goal complete" --timeout 600 --save "$T-continuation.background--complete" >/dev/null
  tui_idle 120 "$T-continuation.background--idle" >/dev/null
  vr tui snapshot --save "$T-continuation.background--snap" >/dev/null
  rg1_down tui tui
}

flow_limits() {
  rg1_up tui limits || return 1
  # 达到 token 预算（之后还有一个总结轮次，等它结束再继续）
  vr tui type "/goal $OBJ_NOTES budget=3K" >/dev/null
  vr tui wait --text "Goal · Budget limited" --timeout 300 --save "$T-limits.token-budget--limited" >/dev/null
  tui_idle 240 "$T-limits.token-budget--idle" >/dev/null
  vr tui snapshot --save "$T-limits.token-budget--snap" >/dev/null
  # 恢复无效：横幅仍为 Budget limited
  vr tui type "/goal resume" >/dev/null
  vr tui wait --text "Goal · Budget limited" --hold 8 --timeout 20 --save "$T-limits.resume-rejected--still-limited" >/dev/null
  vr tui snapshot --save "$T-limits.resume-rejected--snap" >/dev/null
  # 清除
  vr tui type "/goal clear" >/dev/null
  vr tui wait --text "Goal cleared" --timeout 30 --save "$T-limits.clear--cleared" >/dev/null
  vr tui snapshot --save "$T-limits.clear--snap" >/dev/null
  rg1_down tui tui
}

flow_attachments() {
  rg1_up tui attachments || return 1
  local img="$RG1_ROOT/_inputs/red-square.png" out
  vr tui type "/goal $OBJ_COLOR" --no-submit >/dev/null
  vr tui paste "$img" >/dev/null
  vr tui wait --text "[Image #1]" --timeout 15 --save "$T-attachments.kickoff--pasted" >/dev/null
  vr tui keys enter >/dev/null
  # 2026-09-30 基线实跑：粘贴后第一次回车没有提交（输入框仍是 [Image #1]），再按一次才 Goal started
  if ! vr tui wait --text "Goal started" --timeout 10 --save "$T-attachments.kickoff--started" >/dev/null; then
    vr tui keys enter >/dev/null
    vr tui wait --text "Goal started" --timeout 30 --save "$T-attachments.kickoff--started-2" >/dev/null
  fi
  out=$(vr tui wait --text "Goal complete|Goal · Paused" --timeout 420 --save "$T-attachments.kickoff--terminal")
  # 首轮失败后恢复（attachments.md 坑）：只在首轮自然失败、Goal 进入 Paused 时走这一段；不注入故障
  if ! printf '%s' "$out" | grep -q 'Goal complete'; then
    tui_idle 60 >/dev/null
    vr tui snapshot --save "$T-attachments.failure-resume--paused-snap" >/dev/null
    vr tui type "/goal resume" >/dev/null
    vr tui wait --text "Goal complete" --timeout 420 --save "$T-attachments.failure-resume--complete" >/dev/null
    tui_idle 120 >/dev/null
    vr tui snapshot --save "$T-attachments.failure-resume--snap" >/dev/null
  fi
  tui_idle 120 "$T-attachments.kickoff--idle" >/dev/null
  vr tui snapshot --save "$T-attachments.kickoff--snap" >/dev/null
  rg1_down tui tui
}

flow_questionnaire_manual() {
  rg1_up tui questionnaire-manual || return 1
  vr tui type "/goal $OBJ_FRUIT" >/dev/null
  vr tui wait --status state=ask --timeout 150 --save "$T-questionnaire.manual--ask" >/dev/null
  vr tui type "2" --no-submit >/dev/null
  vr tui wait --text "Goal complete|Goal · Paused" --timeout 420 --save "$T-questionnaire.manual--terminal" >/dev/null
  tui_idle 120 "$T-questionnaire.manual--idle" >/dev/null
  vr tui snapshot --save "$T-questionnaire.manual--snap" >/dev/null
  rg1_down tui tui
}

flow_questionnaire_auto() {
  rg1_up tui questionnaire-auto || return 1
  vr tui type "/goal $OBJ_FRUIT" >/dev/null
  vr tui wait --status state=ask --timeout 150 --save "$T-questionnaire.auto-timeout--ask" >/dev/null
  vr tui wait --text "Goal complete|Goal · Paused" --timeout 720 --interval 5 --save "$T-questionnaire.auto-timeout--terminal" >/dev/null
  tui_idle 120 "$T-questionnaire.auto-timeout--idle" >/dev/null
  vr tui snapshot --save "$T-questionnaire.auto-timeout--snap" >/dev/null
  rg1_down tui tui
}

rg1_inputs
for f in lifecycle continuation-bg limits attachments questionnaire-manual questionnaire-auto; do
  rg1_wants "$f" || continue
  "flow_${f//-/_}"
  rg1_log "flow done"
done
