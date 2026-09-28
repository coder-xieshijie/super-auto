# MCode 分析入口

- [analysis.md](analysis.md)：13条主要任务链的证据、后续可见结果、边界和可改进项。
- [summary.json](summary.json)：全量覆盖统计与限制。
- [sessions.jsonl](sessions.jsonl)：758个有窗口消息的session，含profile、父子、cwd、消息计数和Agent Lord显式关联。
- [messages.jsonl](messages.jsonl)：38,995条去重可见消息，包含源path/line或SQLite rowid、时间、role、actor分类和tool evidence。
- [cases.json](cases.json)：13案例结构化引文与建议。
- [case-evidence/](case-evidence/)：13会话的可见文字材料，工具输出在messages.jsonl和raw快照中。
- [原始快照说明](../../raw/mcode/README.md)：源清单、gzip格式、覆盖方法和脱敏边界。

生成脚本顺序：`scripts/mcode_extract.py` → `scripts/mcode_postprocess.py`（需要orchestration/operations.jsonl）→ `scripts/mcode_cases.py` → `scripts/mcode_write_analysis.py`。原始源码只读，输出写入当前research目录。
