# 查漏试运行（2026-09-29）

检验 core-verify 第 6 步的查漏说明能否用另一家模型跑通，以及能查出什么。结论见[讨论记录](../../../../discussions/2026-09-29-zero-based-delivery.md)的“需求文档位置；补全 spec、verify 并新建 deliver”一节。

| 文件 | 内容 |
|---|---|
| [spec.md](spec.md) | 由 dev-skills core-spec 示例的 spec 正文拼成（已补目的、非目标、交付与授权） |
| [verify.md](verify.md) | 由 core-verify 示例的 verify 片段拼成。这是修正前的版本：S02 还是原来的写法 |
| [codex-report.md](codex-report.md) | Codex 的查漏报告原文 |
| [codex-run-header.txt](codex-run-header.txt) | 运行头信息：codex-cli 0.158.0-alpha.2.1、`gpt-5.6-sol`、xhigh、`read-only` 沙箱 |

调用命令：

```bash
codex exec -C /tmp/gapcheck-test -s read-only -o /tmp/gapcheck-test/report.md "按 <dev-skills>/skills/core-verify/references/gap-check.md 查漏。spec：/tmp/gapcheck-test/req/spec.md；verify：/tmp/gapcheck-test/req/verify.md；仓库：/tmp/gapcheck-test（示例仓库，只有这两份文件，没有应用代码）。"
```

用时约 1 分钟，约 4.1 万 token。报告报出 10 条问题：

- 3 条来自示例仓库本身（没有应用代码、没有 `main` 分支，S03–S05 被省略），在预期之内。
- 2 条是示例的真实缺陷，已在 dev-skills#12 中修正：
  - S02 的任务本来只请求一次，完全不检查额度的实现也能通过；
  - 非目标没有对应的要求。
- 5 条指出示例为了简短省掉的定义。

运行后示例仓库里只多了 CLI 写出的报告和日志，模型没有写入任何文件。
