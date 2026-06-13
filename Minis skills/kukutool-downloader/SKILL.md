---
name: kukutool-downloader
description: 使用 KuKuTool/dy.kukutool.com 自动解析无水印资源并高效下载。触发场景：明确提到 KuKuTool、kukutool、dy.kukutool.com、酷酷工具、去水印、无水印解析、去水印下载、解析视频/图文链接、下载无水印视频/图片/Live图，或要求把抖音/快手/小红书/微博/B站/知乎/西瓜/贴吧/Instagram/TikTok/Facebook 等分享链接“去水印/解析/提取无水印资源”。不要仅因普通“下载抖音/微博/B站内容”触发，除非用户强调去水印、无水印、解析或指定 KuKuTool。
---

# KuKuTool Downloader

目标：把用户手动打开 KuKuTool、粘贴链接、解析、下载的流程，改为 Minis 自动完成。优先走“快路径”：少量浏览器调用 + 页面内 JS 等待结果 + Python 并发下载 + 默认返回 ZIP。

## 适用

- 用户给出社交平台分享链接并要求：去水印、无水印解析、解析下载、提取无水印视频/图片/Live 图。
- 用户明确指定：KuKuTool、kukutool、dy.kukutool.com、酷酷工具。
- 支持平台按网站能力处理：抖音、快手、小红书、微博、B站、知乎、好看视频、贴吧、西瓜、TikTok、Instagram、Facebook 等。

## 不适用

- 用户只是说“下载抖音/微博/B站/小红书”，但没有说去水印/无水印/解析/KuKuTool：优先使用更专用的下载或平台 Skill。
- 不绕过验证码、登录、积分、广告解锁、频率限制或风控。
- 不默认逆向 `/api/parse` 加密接口；正常使用网页前端。

## 性能原则

- 不要用多轮 `browser_use`：避免“打开 → 输入 → 点击 → 等待 → 再提取 → 再逐张下载”的慢流程。
- 优先用 `minis-browser-use` 写一个临时脚本：`navigate` 一次，`execute_js` 一次完成输入、点击、等待、提取。
- 下载不要逐个工具调用；用 Python `ThreadPoolExecutor` 并发下载到 `/var/minis/attachments/`。
- 默认返回每条内容的 ZIP 链接；只有用户要求“列出单图”时再返回全部单图链接。
- 不预览图片，不调用 `read_image`，除非用户要求检查图片内容。
- 多个 URL 时复用同一个 KuKuTool 页面，逐条解析；下载阶段统一并发。

## 快路径流程

1. 提取用户消息中的 URL 列表；没有 URL 才询问。
2. 用 `shell_execute` 运行一个短脚本，脚本内部调用 `minis-browser-use`：
   - `navigate --url https://dy.kukutool.com`
   - 对每个 URL 调用一次 `execute_js`，JS 内部：
     1. 找到输入框；用原生 setter 写入 URL。
     2. 点击文本包含“开始解析”的按钮。
     3. 每 300ms 轮询最多 20s，直到出现图片/视频结果或明确错误提示。
     4. 提取：页面正文、标题片段、所有结果图片 `document.images` 中的 `data.hellotik.app/v1/download/image` 链接、可能的视频/下载链接、按钮计数。
3. 将解析 JSON 写入 `/var/minis/workspace/kukutool_result_*.json`。
4. 用 Python 并发下载资源：
   - 图片文件名：`kuku_<platform_or_id>_<postid>_01.jpg`
   - 视频文件名：`kuku_<platform_or_id>_<postid>.mp4`
   - 每个原始 URL 单独打包：`kuku_<postid>_images.zip`
5. 最终回复：标题/数量/ZIP 链接；必要时附失败原因。

## 页面内 JS 提取要点

- 入口：`https://dy.kukutool.com`
- 输入框 placeholder 常见为：`粘贴带链接的文本`
- 主要按钮文本：`开始解析`、`清除内容`、`粘贴链接`
- 图片结果常见 URL：`https://data.hellotik.app/v1/download/image?...`
- 结果按钮文本常见：`批量下载图片ZIP`、`复制所有图片链接(n)`、`下载无水印图片`、`复制无水印链接`
- 成功判断优先级：
  1. 页面出现 `data.hellotik.app/v1/download/image` 图片链接；
  2. 页面出现下载按钮且正文包含“封面或图片列表”；
  3. 页面出现视频下载 URL/按钮。
- 错误判断：正文包含“解析错误”“请求过于频繁”“验证码”“登录”“积分”“服务器维护”等。

## 推荐临时实现模式

当需要实际执行时，创建一个临时 Python 脚本，不要在 shell 里写长命令。脚本职责：

- 调用 `subprocess.run(['minis-browser-use', ...])` 做浏览器自动化；
- 解析 `minis-browser-use execute_js` 返回的 JSON；
- `ThreadPoolExecutor(max_workers=6)` 并发下载；
- `zipfile.ZipFile` 打包；
- 打印结构化摘要。

下载请求头建议：

```text
User-Agent: Mozilla/5.0
Referer: https://dy.kukutool.com/
```

## 失败/限制处理

遇到以下情况直接反馈给用户，不尝试绕过：

- `请求过于频繁` / 429：稍后重试。
- `请提供有效的视频链接` / 无效链接：让用户确认复制完整分享链接。
- `签名验证失败`：刷新页面后重试。
- `验证码错误` / 需要验证码：请用户手动完成验证码。
- `每天无需登录解析次数已用完`：需要登录、换时间或使用 APP/小程序。
- `解析超限` / `积分不足`：网站限制，不能绕过。
- `服务器维护中`：稍后重试。

## 输出格式

默认精简输出：

```markdown
解析完成：

1. <来源 URL 或 post id>
   - 类型：图片
   - 数量：10 张
   - 打包：[kuku_xxx_images.zip](minis://attachments/kuku_xxx_images.zip)

如需单张链接，我可以展开列出。
```

失败：

```markdown
解析失败：<页面提示>
建议：<换链接/稍后重试/手动完成验证码/登录网站>
```

## 注意

- 只模拟用户正常网页操作，不规避网站访问控制。
- 尊重版权：提示用户仅下载自己有权保存或授权使用的内容。
