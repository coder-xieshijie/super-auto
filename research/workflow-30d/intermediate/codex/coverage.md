# Codex 覆盖与计数口径

| 层级 | 数量 | 含义 |
|---|---:|---|
| 全部读取源文件 | 1903 | 每份扫描固定字节前缀，未按文件日期裁剪 |
| 读取源字节 | 7,102,491,417 | 约7.10GB，source manifest记录哈希 |
| 读取JSONL行 | 1,223,520 | 坏JSON 0 |
| 窗口内来源文件 | 783 | 已排除当前研究及其子agent |
| 不同session身份 | 749 | 不是独立任务数 |
| 保存的可见源事件 | 342,154 | 含工具、执行状态及用量元数据；不含私有reasoning |
| 规范消息行（含回放） | 116,188 | user、assistant、工具调用/输出 |
| 已识别回放行 | 1,038 | 保留并标记replay_of |
| 去回放规范行 | 115,150 | 不应称为用户交互轮数 |
| 工具调用/输出行 | 98,324 | 包含调用和输出两端 |
| assistant行 | 13,632 | commentary11251、final2303、语音78 |
| user角色行 | 3,194 | human_candidate2193、wrapper873、委派/继承128 |

来源角色口径：根来源545、子agent来源155、fork来源183，可重叠且不能相加推任务数；31个来源匹配Agent Lord endpoint，其user role被标为委派。31个session身份拥有多份窗口内源文件，因此去重还必须考虑同id不同来源的导入。

语音转写也纳入：141个transcript_segment（user63、assistant78）；realtime session事件不是一条用户消息。

回放识别优先稳定message ID；无ID时要求同根、同时间、同角色、同文本。未以“继续”等短句跨全局去重。这是保守识别，元数据已丢失的历史回放可能仍无法证明。

主题广召回见 quality-and-recall.json：只在非回放human_candidate上做词匹配，排除cwd/首条请求识别出的历史分析来源。词命中不是失败数、催办数或因果结论；例如“继续”可能是用户主动追加下一阶段。

质量检查：所有源读取字节等于固定扫描边界；已引用快照存在；规范消息无analysis/reasoning频道；未发现残余URL token模式；坏JSON 0。启发式脱敏不保证识别所有可能的敏感字符串，资料仅本地保存。

复现顺序：codex_extract.py → codex_finalize.py → codex_realtime.py（已包含时幂等）→ codex_quality.py；深读由codex_cases.py和codex_case_report.py生成。源文件可能继续增长，manifest中的字节范围与hash用于比较本次快照。