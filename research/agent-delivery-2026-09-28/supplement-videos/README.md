# 用户补充的两段视频

先读 [综合借鉴分析](analysis.md)。

| 视频 | 元信息 | 原始字幕 | 中间分析 |
|---|---|---|---|
| Pi Agent / pi-herdr-agents 实战 | [metadata](raw/y1TXjYlRjBU/metadata.json)，2026-09-19，31:18 | [中文全文](raw/y1TXjYlRjBU/transcript/browser-export.txt) | [视频笔记](intermediate/pi-video-notes.md)、[作者示例源码核查](intermediate/pi-source-check.md) |
| Factory — The Multi-Agent Architecture That Actually Ships | [metadata](raw/ow1we5PzK-o/metadata.json)，2026-05-06，18:30 | [英文自动字幕全文](raw/ow1we5PzK-o/transcript/browser-export.txt) | [视频笔记](intermediate/factory-video-notes.md)、[官方整理原页](raw/ow1we5PzK-o/official-talk.html) |

- [关键画面观察](raw/visual-observations.md)：Factory 13:17 数据图、Pi 30:11 游戏画面；未保存本地完整视频或原始帧文件。
- [来源与 SHA-256](source-manifest.json)、[方法与采集状态](acquisition.json)。
- [独立审核](intermediate/review.md)。

YouTube 公开页面字幕导出成功；匿名完整视频下载在旧 extractor 失败后，用本机较新 yt-dlp 重试仍返回 HTTP 403。两次日志保留，未导出浏览器 cookies。原始字幕不改字，Factory 未逐字听校，Pi 字幕作者校订状态不明。

用户第二个链接从 13:53 开始；本轮分析全片，并对这附近的成本/验证图表作了重点核对。作者示例代码固定到 9 月 24 日提交，晚于首片发布时间；它是补充核查而非录制环境复原。本轮未安装或运行示例，没有修改用户的实际交付工具。
