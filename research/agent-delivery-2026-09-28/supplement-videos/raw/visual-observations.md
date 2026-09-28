# 两段视频的关键画面观察

日期：2026-09-28；方法：Codex In-app Browser 公开 YouTube 播放页，按字幕时间跳转、暂停，再读截图。没有修改网页内容或操作 demo 本身。截图已在会话工具结果显示；本目录保存观察记录，不冒称保存了原始帧文件。下载失败原因见各视频 prepare.log/retry.log。

## Factory，暂停约 13:17

原地址：https://www.youtube.com/watch?v=ow1we5PzK-o&t=796s

画面标题 Breaking down a real mission，副标题 Building a clone of Slack。

- Total runtime：16.5h。
- Orchestration：0.38h / 2.3%；Implementation：9.98h / 60.5%；Validation：6.14h / 37.2%。
- Total tokens：778.5M；Input：30.3M；Cache read：744.9M；Output：3.4M。
- 按角色 tokens：Orchestration 29.2M、Implementation 485.5M、Validation 263.8M。
- Code：38.8k lines；52.5% tests；Source 18.5k、Tests 20.4k；Statement coverage 89.25%。
- 另有 185 total runs 和里程碑 waterfall；未根据柱形/颜色推算失败率或每个验证轮次。

只确认投影片展示这些读数，不独立审计后台运行数据。多个图表的小数/整数经过取整，不用其做精确费用计算。

## Pi 教程，暂停约 30:11

原地址：https://www.youtube.com/watch?v=y1TXjYlRjBU&t=1808s

画面为 3D 风格赛车场景，可见“海岸公路”、计时、车况、速度表和几何形车体；字幕显示作者说明车模型尚不完整。单帧确认作品画面存在，不能证明操控、全部三关、音乐或无 bug。作者 30:08–30:31 的保留意见应和成品演示一起保留。

## 非核心抽样

Factory 首次截图落在 16:01，显示工程师关注架构/产品问题、沉淀测试和 skills 的总结页。后续已回到 13:17 核对用户指定附近数据，未将 16:01 当作 13:53 的画面。
