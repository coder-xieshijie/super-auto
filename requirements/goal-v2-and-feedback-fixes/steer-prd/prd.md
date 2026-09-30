<!--
source: https://vrfi1sk8a0.feishu.cn/wiki/SXcHwrz88ik3zJkb27hcotE3nLW（用户 2026-09-30 提供，此前无权限，16:25 起可读）
revision_id: 91
fetched_at: 2026-09-30 16:25 Asia/Shanghai（lark-cli docs +fetch --as user --doc-format markdown；图片用 docs +media-preview 取得，同目录 PNG 以 token 命名）
图片：O4HY…=“现在”（替换目标弹窗），QCm2…=“优化后”（普通发送作为消息气泡、Goal 继续），XPAw…=示意图（输入框默认“目标”标签），MEoK…=替换目标（二次 /goal 后发送弹确认）
-->

# goal模式下支持用户steer

<table><colgroup><col/><col/><col/><col/></colgroup><thead><tr><th vertical-align="top"><b>模块</b></th><th vertical-align="top">详细逻辑（状态、交互）</th><th vertical-align="top">示意图</th><th>checked</th></tr></thead><tbody><tr><td>正常goal模式下</td><td><ol><li seq="1">去掉默认配置的目标模式</li><li>正常发送的情况下，会直接替换goal<br/></li></ol><grid><column width-ratio="0.598700"><img name="Clipboard_Screenshot_1789977467.png" caption="现在&#xA;" mime="image/png" scale="0.414302" src="O4HYbfea8oNpWZxHaP0c0A0FnCe"/></column><column width-ratio="0.401300"><img name="Clipboard_Screenshot_1789977574.png" caption="优化后&#xA;" mime="image/png" scale="0.432977" src="QCm2bueQVotGPJxQhTdcombfn8G"/></column></grid></td><td><img name="Clipboard_Screenshot_1789977413.png" mime="image/png" scale="1.000000" src="XPAwbScSIobVT3xI1aPcvwyjnkf"/></td><td></td></tr><tr><td>替换目标</td><td><ol><li seq="1">需要用户二次 “/goal”</li><li>出现“目标”状态</li><li>用户点击发送，触发“替换目标”</li></ol></td><td><img name="Clipboard_Screenshot_1789977647.png" mime="image/png" scale="1.000000" src="MEoKb2sOco0RJPxOTIvcSj3mnkd"/></td><td></td></tr></tbody></table>