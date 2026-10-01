# RG1 迁移前后逐条对照

基线 `evidence/rg1-baseline`（`d770f05f30`）对迁移 `evidence/rg1-migration`（`6d0823cc14`），同一批脚本。机械对照：`python3 tools/rg1-compare.py evidence/rg1-baseline evidence/rg1-migration`，输出 `compare.json`（每条含两边的最终状态、status_reason、文件与内容、goal 事件序列及 diff、地图检查的变化）。

## 结论

- 55 条的最终状态、status_reason 两边全部相同。
- 47 条在状态、原因、工作目录文件（含内容）、`goal.*` 事件类型序列四项上全部相同。
- 8 条有差异：3 条是预期差异（第 2 项）；5 条是模型随机性，均已重跑确认。没有迁移引入的行为变化。

## 有差异的 8 条

| 记录 | 差异 | 判断 |
| --- | --- | --- |
| 完成 · 最终回复的运行顺序 · 接口 | 基线：update_goal(complete) 后本轮即结束；迁移：同一 turn 再有一次模型请求并写出最终回复（历史 finish_reason=stop），之后 turn_settled → verification_dispatched。事件序列相同 | 预期差异（第 2 项） |
| 完成 · 最终回复 · TUI | 基线：× Error Runtime completed without a final assistant response.、state=fail、EMPTY_RESPONSE；迁移：没有该错误，state=done，tui-results 为 succeeded，update_goal 后同一 turn 有一次请求。事件序列相同 | 预期差异（第 2 项） |
| 完成 · 最终回复与交付卡片 · Electron | 迁移在 update_goal 之后同一 turn 有最终回复；goal-lifted-delivery-cards 两边都是 0。事件序列相同 | 预期差异（第 2 项） |
| 附件 · 首轮附件 · 接口 | secret.txt：基线 `PAPAYA-42`，迁移 `PAPAYA-42\n` | 模型随机：Inspector 中 write 的 content 原样如此；重跑一次仍带换行；两个提交发给模型的请求只差第 2 项的提示词句子 |
| 问卷 · 手动回答 · 接口 | fruit.txt：基线 `Banana`，迁移 `Banana\n` | 模型随机：write 参数原样；重跑一次仍带换行（同提交的其他条目两种都出现过） |
| 问卷 · 超时自动回答 · 接口 | fruit.txt：基线 `Apple\n`，迁移 `Apple`；事件多一条不跟 turn_bound 的 admission_decided{final_recheck,ready} | 模型随机：文件内容是 write 参数原样，重跑为 `Apple\n`，与基线相同；多出的事件紧跟回答后那一轮的 bash 结束出现（基线那一轮用 read），重跑仍用 bash、仍多一条 |
| 问卷 · 手动回答 · Electron | fruit.txt：基线 `Banana\n`，迁移 `Banana`；基线多 2 条不跟 turn_bound 的 admission_decided | 模型随机：基线那一轮调了 2 次 bash，每次结束后一条；迁移那一轮用 read。重跑模型用 2 次 bash，事件序列与基线逐条相同 |
| 问卷 · 超时自动回答 · Electron | fruit.txt：基线 `Apple`，迁移 `Apple\n` | 模型随机：write 参数原样；重跑为 `Apple`，与基线相同 |

“回答后那一轮里 bash 结束就触发一次 ready 的 admission_decided、后面没有 turn_bound”：基线（Electron 手动）和迁移（接口自动两次、Electron 手动与自动重跑）都有，出现与否只取决于模型在该轮是否用 bash。后台续跑三条在两边也有同样条数的这类事件（接口 2、Electron 2、TUI 4）。

## 两边相同的“与地图”结论

- 附件 · 粘贴图片 · TUI：两边都是第一次回车没有开始（`started-timeout`），补按一次后开始（`started-2`），color.txt 为 red。
- 附件 · 失败后恢复 · TUI：两边都走不通（首轮没有失败）。

## 其他观察（不作判定依据）

- Electron 授权卡片：执行阶段基线 1 张、迁移 2 张；验证阶段两边都是 2 张（模型相关）。
- 接口计时：运行中 time_used_seconds 为 12→16（基线）、12→17（迁移）；暂停后 10 秒不变。
- Electron 编辑替换后 goal_id 不变，turns_used 都是 3；重载后都直接回到原会话；会话内目标资源都没有弹替换确认。
- token 预算：两边都在第一轮后 budget_limited(token)，notes.md 都没写出。完成后不续跑：两边 turns_used 都保持 2，队列为空。
