# TASK_FAMILY_INDEX

## 作用

按任务家族组织高频需求，降低路由成本，减少每次重新判断“这类事情通常怎么做”。

## 任务家族

### 1. 记录类

典型目标：
- 备忘录
- 提醒事项
- 文件
- 第三方笔记应用

常见结构：
- `ask_text`
- `share_input`
- `menu_select`
- `write_target`
- `show_notification`

常见配方：
- `collect_text_then_write`
- `collect_text_then_choose_destination`
- `task_then_followup`

### 2. 查询类

典型目标：
- 天气
- 日历
- 汇率
- 简单 API
- 本地信息提取

常见结构：
- `ask_or_context`
- `request_or_native_query`
- `parse`
- `show_result`

常见配方：
- `query_then_show`

### 3. 分享类

典型目标：
- 分享文本
- 分享图片
- 分享文件
- 截图后发送

常见结构：
- `share_input`
- `transform`
- `share_output`

常见配方：
- `share_input_then_process`

### 4. 跳转类

典型目标：
- 打开 App
- 深链到页面
- 写入后继续打开目标
- 调起第三方动作

常见结构：
- `prepare_value`
- `url_encode`
- `open_url` / `open_app_scheme`

常见配方：
- `construct_and_open_uri`
- `task_then_followup`

### 5. Hybrid 类

典型目标：
- 启动复杂下载
- 启动网页处理
- 触发 Minis 或外部服务工作流
- 调用复杂脚本、签名、转换能力

常见结构：
- `collect_input`
- `handoff`
- `notify`

常见配方：
- `hybrid_launcher`

### 6. Minis 增强类

典型目标：
- 把 Minis CLI 工具的能力暴露为快捷指令
- 通过快捷指令触发 Minis 的 AI、感知、健康、家居等能力
- 快捷指令作入口 → Minis 执行 → 结果回写系统

使用条件：
- 任务核心能力在 `apple-*` 或 `minis-*` 命令中，而不在 Shortcuts 原生动作中
- 或任务需要组合多个 Minis 命令形成处理管道

常见入口：
- `share_input`（分享触发，传递文件/URL/文本给 Minis）
- `ask_text`（手动输入，作为 Minis 命令的参数）
- `clipboard_in`（读取剪贴板内容交给 Minis）

常见 Minis 后端能力（详见 `MINIS_CAPABILITIES.md`）：
- AI 感知：`apple-vision`（OCR/扫码/图片分类）、`apple-nlp`（实体识别/情感分析）、`apple-speech`（语音转文字）
- 健康追踪：`apple-healthkit`（步数/心率/睡眠/运动汇总）
- 智能家居：`apple-homekit`（设备控制/场景执行）
- 信息查询：`apple-weather`、`apple-location`、`apple-maps`
- 网页交互：`minis-browser-use`（截图/内容提取/表单填写）
- 媒体管理：`apple-photos`（导出/导入/搜索）、`apple-media`（音乐控制）
- 自交互：`minis-sessions-cli`（对话历史搜索/自动化对话）、`minis-model-use`（AI 模型调用）

常见配方：
- `hybrid_launcher`
- `minis_query_then_show`
- `minis_process_then_write`

## 使用顺序

1. 先识别任务属于哪个家族
2. 再选家族下的常见配方
3. 若用户明确提到 Minis，查 `MINIS_CAPABILITIES.md` 定位具体工具
4. 再查模式和片段
5. 最后进入 XML 生成
