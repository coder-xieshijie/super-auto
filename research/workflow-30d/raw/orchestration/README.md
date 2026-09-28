# Agent Lord 操作元数据快照

`source-manifest.jsonl` 列出 562 个原 operation JSON 的路径、大小、SHA256 与是否纳入窗口。`operation-metadata.jsonl` 保留创建或完成时间落在窗口内的 490 次操作，使用允许字段白名单；不复制 prompt、配置或凭据。

保留 task/operation/provider/endpoint、caller 身份、时间、状态、工作区、交付要求和错误分类等，用于与原生会话交叉关联。状态是采集时磁盘上可见值，可能晚于窗口内操作创建时间；不是严格的历史时点快照。

214 个 task ID 不等于 214 项用户需求。operation succeeded 不等于代码检查、MR 交付或合并。取消（例如返回码 130）单列；没有把它归因于 provider 健康。相邻 failed→succeeded 只描述同 task 的操作序列，不证明原任务全部成功。

可重放脚本：`../../scripts/orchestration_extract.py`。规范化操作和归并：`../../intermediate/orchestration/`。
