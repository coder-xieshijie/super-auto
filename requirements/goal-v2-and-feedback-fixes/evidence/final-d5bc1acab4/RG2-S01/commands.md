# RG2 S01（第 2 项 verify 的 S01，Electron）命令

来源：`git -C /Users/minimax/code/mm/worktrees/agent-archon/gv2-tests show refs/remotes/origin/fix/goal-final-result-delivery:.harness/docs/specs/goal-final-result-delivery/verify.md` 的 S01。之前没有本需求的现成脚本；步骤照原文 1–8，读数选择器沿用第 2 项交付时的 `requirements/goal-final-result-delivery/tools/gfd-s01.sh`，启动、输入框读回核对、登录核对改用本需求的 `m2-lib.sh`/`m3-lib.sh`。

在被测检出根目录（gv2-tests，HEAD d5bc1acab4）执行：

```bash
source /tmp/gv2-final/env.sh            # REQ、T、M2_ROOT、共享启动锁 /tmp/gv2-final-up.lock、M23_HEAD
bash $T/rg2-s01-electron.sh <尝试名>     # 证据写到 $M2_ROOT/RG2-S01/<尝试名>/
python3 $T/rg2-s01-analyze.py <尝试名>   # 写 checks.json
```

`rg2-s01-electron.sh` 做的事（与原文步骤对应）：

| 原文 | 命令（均带本次 `--run <runId>`，`E` = `node $V electron`） | 保存名 |
| --- | --- | --- |
| 前提 | `electron up --config ~/.minimax/verify-goal-v2/config.yaml --evidence-dir <OUT> --no-proxy`（经共享锁，up 后等 6 秒放锁）；`E status`；`E config`（读回 effectiveGoal，确认没有 `goal.verification`=none/evaluator）；关首次弹窗；`E text --text 始终授权 --exact`（`--config` 设 bypassPermissions，输入框显示“始终授权”） | up.json、electron-status、electron-config、permission-mode |
| 1 | `type_checked "/goal Create a file named hello.html in the workspace. It should be a small web page whose main heading reads Hello Goal."`（读回不一致即中止）；`E click --testid send-button`；`E wait --testid thread-goal-banner` | s01-create-banner |
| 2 | 取最新会话；`poll .../goal --on electron --until goal.status=complete\|paused\|blocked\|budget_limited\|usage_limited --interval 3 --timeout 420` | e-run |
| 3 | `snapshot --session $S --on electron --save s01`；`E screenshot --save s01-complete` | s01、s01-complete |
| 4 | `E text --testid assistant-segment-active`；`E count` 正文内 / `goal-lifted-delivery-cards` 内 `deliver-assets-card:has-text("hello.html")`；`E text --testid goal-completion-marker`、`thread-goal-banner-status` | s01-body-text、s01-result-hello-cards-in-body、s01-lifted-area、s01-result-hello-cards-lifted、s01-marker、s01-banner |
| 5 | 点该卡片的 `file-display`；读选中标签标题与 `file-panel-browser-address-input` | s01-card-click、s01-preview-tab-title、s01-preview-address、s01-preview |
| 6 | `E click --testid turn-process-trigger`；数整条助手消息里 hello.html 卡片 | s01-process-expanded、s01-expanded-hello-cards |
| 7 | `E click --testid workspace-button`；`E text --testid workspace-panel`；数 `workspace-panel` 里 hello.html 按钮 | s01-workspace-panel、s01-workspace-hello-count |
| 8 | `E reload`；等“新建任务”与 `assistant-segment-active`；重复 4、6、7 | s01-reload-* |
| 收尾 | `api GET .../goal`；`electron down`（写 auth-check.json）；`python3 $T/rg2-sanitize-config.py <OUT>`（`electron config` 的输出含整份 config，密钥虽已遮盖也不留，只保留 Goal 字段）；`node $T/rg2-turn-facts.mjs <OUT>/NNN-s01` 从快照取完成那一轮的历史、Inspector 与事件顺序 | s01-goal-final、s01-turn-facts.json |

判定（`rg2-s01-analyze.py`）逐条对应原文检查点；“点击后预览内容包含 Hello Goal”在内嵌浏览器里读不到时按原文覆盖盲区 B6：预览地址为 hello.html，且 s01 快照中 `-workspace/hello.html` 的主标题为 Hello Goal。“独立判断”一项脚本只做机械部分（提到 hello.html 与位置、没有“已通过验证”类表述），结论由人读最终回复原文后写进 summary.md。
