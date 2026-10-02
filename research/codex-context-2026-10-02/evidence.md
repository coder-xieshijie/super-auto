# Codex 上下文窗口：2026-10-02 证据快照

- 采集日期：2026-10-02，Asia/Shanghai。
- 范围：当前 Codex 桌面 App、本机模型目录、当前会话 token 事件、已有 Codex 源码和 OpenAI 官方文档。
- 方法：只读核对；没有改配置、启动测试会话或发送扩窗请求。
- 数字不能推广成所有用户、所有客户端的统一限制；目录、客户端版本和账号可用性可能变化。

## 1. 本机模型目录

来源：[models_cache.json](/Users/minimax/.codex/models_cache.json)。
目录 fetched_at = `2026-10-02T02:15:54.185461Z`（本地 10:15:54），client_version = `0.159.2`。
只记录模型与窗口字段，不复制账号标识、指令模板或其他无关字段。

| 可见模型 slug | context_window | max_context_window | effective_context_window_percent |
|---|---:|---:|---:|
| gpt-6.1-sol | 272000 | 872000 | 95 |
| gpt-6-astra | 272000 | 872000 | 95 |
| gpt-6-sol | 272000 | 872000 | 95 |
| gpt-6-luna | 272000 | 872000 | 95 |
| gpt-5.6-sol | 272000 | 872000 | 95 |
| gpt-5.6-terra | 272000 | 872000 | 95 |
| gpt-5.6-luna | 272000 | 872000 | 95 |
| gpt-5.5 | 272000 | 272000 | 95 |

`supports_experimental_context` 不能用作上述手动窗口配置的开关判据。已有源码里它控制实验性的 history notes 扩展，窗口覆盖函数没有用它作为条件。本轮不启用该扩展。

## 2. 当前会话直接读回

来源：[本轮 JSONL](/Users/minimax/.codex/sessions/2026/10/02/rollout-2026-10-02T10-15-33-01a0fa65-3cd1-7093-8368-4e3914940205.jsonl)，仅提取 `turn_context` 的模型字段和最新 `event_msg/token_count/info/model_context_window`。

- model = `gpt-6.1-sol`
- effort = `xhigh`
- model_context_window = `258400`
- 全局配置中未设置 `model_context_window` 或 `model_auto_compact_token_limit`。
- 算式：`272000 × 95 / 100 = 258400`。
- 如果配置窗口为 872000，按目录中的预留比例预计可用 `872000 × 95 / 100 = 828400`；这是计算和源码推导，不是扩窗后的请求实测。

桌面 App 的 `app.asar` 中，`/webview/assets/app-primary-705e2d4f1e56.js`：
- `uU(e)` 读取 `e?.modelContextWindow`。
- tooltip 用 `Math.round(n.contextWindow/1e3)` 展示千 token。
- 当前桌面构建不是按 1024 换算该 tooltip。因此没有把用户提到的 252K 强行解释成二进制单位；它来自哪个界面、版本或其他计算方式，本轮没有证据确定。

## 3. 已有本地源码核对

仓库：[Codex source](/Users/minimax/code/github/code-agent/codex)。
固定 HEAD = `5c5308fc9a9ee789049d646ef11e5400384b9c6f`，commit 时间 `2026-09-20T03:02:48Z`。
这个源码快照不是当前已安装二进制的逐字版本证明；本轮将它与当前模型目录、运行事件分别保留。

[窗口覆盖函数](/Users/minimax/code/github/code-agent/codex/codex-rs/models-manager/src/model_info.rs:19) 的核心行为：

```rust
if let Some(context_window) = config.model_context_window {
    model.context_window = Some(
        model.max_context_window.map_or(context_window, |max_context_window| {
            context_window.min(max_context_window)
        }),
    );
}
if let Some(auto_compact_token_limit) = config.model_auto_compact_token_limit {
    model.auto_compact_token_limit = Some(auto_compact_token_limit);
}
```

[可用窗口和自动压缩上限](/Users/minimax/code/github/code-agent/codex/codex-rs/protocol/src/openai_models.rs:514)：
- `resolved_context_window()` 优先取 `context_window`，没有时取 `max_context_window`。
- `usable_context_window()` 将解析后的窗口乘以 `effective_context_window_percent / 100`。
- `auto_compact_token_limit()` 取配置阈值与窗口 90% 的较小值；没有配置时用窗口的 90%。
- 872000 的 90% 为 784800，因此示例阈值 780000 处于该上限内。
- 填写 1000000 或更大数字，在有当前 `max_context_window=872000` 的目录下会被钳制。
- [源码测试](/Users/minimax/code/github/code-agent/codex/codex-rs/models-manager/src/model_info_tests.rs:249) 已包含配置超过最大值时钳制的断言；本轮只读该测试，没有重新运行整个项目测试。

## 4. 官方文档

使用 OpenAI Docs 连接器搜索后，实际 fetch 以下页面；没有以搜索摘要替代页面正文。

### 配置项

[Configuration Reference](https://learn.chatgpt.com/docs/config-file/config-reference)：
- 用户配置位于 `~/.codex/config.toml`。
- `model_context_window`：当前模型可用的上下文 token 数配置。
- `model_auto_compact_token_limit`：触发自动历史压缩的阈值，未配置时使用模型默认值。
- `model_auto_compact_token_limit_scope`：默认 `total`，按完整活动上下文计算；本轮不改 scope。

### API 模型规格

[GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol) 与
[GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) 的当前正文都列出：
- Context window: 1,050,000 tokens
- Max input: 922,000 tokens
- Max output: 128,000 tokens

API 规格与 Codex 桌面目录的 `max_context_window=872000` 是不同证据来源，不能拿 API 数字直接承诺桌面 App 生效值。

`https://learn.chatgpt.com/docs/changelog` 的正文 fetch 返回 404；搜索能读到旧 GPT-5.4 的 1M 实验说明，但本轮没有把该摘要作为当前模型支持的证明。
`https://learn.chatgpt.com/docs/config-file/config-basics` 的正文 fetch 也返回 404；已成功读取的配置参考足以说明配置项。

## 5. 配置建议与验证边界

针对当前桌面 App，在 [config.toml](/Users/minimax/.codex/config.toml) 顶层设置：

```toml
model_context_window = 872000
model_auto_compact_token_limit = 780000
```

需要新会话核对实际 `model_context_window`。本轮没有实施该修改，也没有验证已安装二进制接受覆盖后的新值或服务端接受超过默认窗口的请求。

本机 `/Users/minimax/.local/bin/codex` 包装器单独设置 `CODEX_HOME=/Users/minimax/.codex-cli`，因此终端 CLI 不应假定读取桌面的上述配置路径。本轮范围是用户正在使用的桌面 App。

只提高压缩阈值，不会扩大模型窗口；压缩将长对话整理成摘要，也不能让原始内容全部同时进入模型窗口。

## 6. 同日追问的来源与计费补充

### 数字的证据等级

新一次目录读回：`fetched_at=2026-10-02T02:29:26.726793Z`，`client_version=0.159.2`；
`gpt-6.1-sol` 仍为 `context_window=272000`、`max_context_window=872000`、有效比例 95%。

配置 `model_provider=openai`；`openai_base_url`、`chatgpt_base_url`、
`model_catalog_json`、`model_catalog_url` 未设置。当前 shell 的 `OPENAI_BASE_URL`
和 `CHATGPT_BASE_URL` 也未设置。本轮没有读取或保存认证凭据。

固定源码的
[fetch_and_update_models](/Users/minimax/code/github/code-agent/codex/codex-rs/models-manager/src/manager.rs:519)
读取 `endpoint_client.list_models` 返回的模型、etag 和 identity，生成 ModelsCacheEntry 并写入缓存。
[ModelsClient](/Users/minimax/code/github/code-agent/codex/codex-rs/codex-api/src/endpoint/models.rs:34)
使用 models 路径和 client_version 查询参数，解码 ModelsResponse。

因此，872000 的直接来源是官方客户端保存的运行时目录字段。
这比无来源的估算具体，但仍区别于公开文档承诺；本轮没有独立向服务端重抓该目录。
前一条“最大可配置窗口”在本次讨论中澄清为“当前本机目录声明的最大值”。

### 官方建议的边界

[高级配置](https://learn.chatgpt.com/docs/config-file/config-advanced)
列出 `model_context_window`，示例值为 128000；它说明配置能力，并未推荐 872000 或全局最大窗口。

[Best practices](https://learn.chatgpt.com/guides/best-practices)
HTML 正文的 Organize long-running chats 节说明：
- 按一个连贯工作单元组织会话。
- 长会话可以使用 compact，Codex 也会自动压缩。
- 将整个项目都放在一个会话会导致上下文膨胀，并影响结果。

[定价页](https://learn.chatgpt.com/docs/pricing)
节约额度建议包括减少无关上下文和限制源材料。
本轮查到的这些指南没有给出“所有任务应一律调到最大窗口”的建议；
不能把这一有限查证表述成已证明官方任何页面都没有此建议。
前一条 872000 / 780000 是助手的示例，不是官方推荐组合。

### 当前计费正文

[Codex 定价](https://learn.chatgpt.com/docs/pricing) 明确：
- API token 价格与订阅用量独立，不能用 API 价格估算订阅包含的任务数。
- 模型、上下文、推理、工具、检索和缓存都会影响用量；保留更多上下文的长会话会显著增加每条消息的额度消耗。
- credits 按输入、缓存输入和输出 token 计价；Codex credits 没有单独的 cache-write 费用。
- GPT-6.1 Sol 的 Standard credits 表为每百万输入 50 credits、缓存输入 2.5 credits、输出 250 credits。
- credits 单价也不能直接推算订阅额度的消耗速度。
- 本轮读取的当前定价正文没有列出 GPT-6.1 Sol 超过 272K 时的 Codex 订阅固定倍率。因此不据此承诺订阅扩窗“无附加倍率”，也不宣称“一律 2 倍”。

[GPT-6.1 Sol API 模型页](https://developers.openai.com/api/docs/models/gpt-6.1-sol#pricing-notes)
当前 Pricing notes 明确：单次 prompt 超过 272K input tokens 后，整次请求的输入和缓存费率为基础费率 2 倍，输出费率为 1.5 倍。
这一触发条件是实际输入长度；修改可用窗口上限本身不是一次已发生的长输入请求。
不将 GPT-6.1 Sol 的规则无证据地推广到所有模型或 Codex 订阅。

### 获取失败与恢复

- OpenAI Docs 连接器读取 `https://learn.chatgpt.com/guides/best-practices.md` 返回 404，
  随后 Web 工具成功打开对应官方 HTML，并读取长会话管理正文。
- 上一轮 changelog Markdown 404 后，本轮成功打开官方 HTML。GPT-5.4 的旧发布说明提到实验性 1M 支持；没有用该旧模型说明证明当前 GPT-6.1 Sol 的窗口或计费。
- 对定价和 changelog HTML 查找精确字符串 `272K` 没有匹配；这是页面内查询结果，不是全网不存在的证明。
- 本轮未检查账户认证方式、具体套餐账单或扩窗后的实际扣量。
