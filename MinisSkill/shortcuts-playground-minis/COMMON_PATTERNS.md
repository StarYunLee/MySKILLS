# Common Patterns

## 作用

提供可组合的高频模式分类，用于快速把自然语言需求拆成动作链。

## 模式分类

| 类别 | 模式 | 用途 | 常见动作 |
|---|---|---|---|
| 输入 | `ask_text` | 手动输入文本 | Ask for Input |
| 输入 | `ask_number` | 手动输入数值 | Ask for Input |
| 输入 | `ask_date` | 日期或日期时间输入 | Ask for Input |
| 输入 | `share_input` | 接收分享输入 | Extension Input |
| 输入 | `clipboard_in` | 读取剪贴板 | Get Clipboard |
| 输入 | `external_input` | 接收 URL、图片、文件 | Share / Detect / File |
| 上下文 | `current_location` | 读取当前位置 | Get Current Location |
| 上下文 | `current_date` | 读取当前时间 | Current Date |
| 控制 | `menu_select` | 固定分支 | Choose from Menu |
| 控制 | `list_select` | 从列表选择 | Choose from List |
| 控制 | `if_guard` | 条件判断 | If |
| 控制 | `repeat_each` | 列表遍历 | Repeat with Each |
| 控制 | `dictionary_flow` | 字典构建与取值 | Dictionary / Get Dictionary Value |
| 数据 | `text_template` | 拼接结果文本 | Text |
| 数据 | `text_replace` | 文本替换 | Replace Text |
| 数据 | `regex_extract` | 规则提取 | Match Text |
| 数据 | `json_request` | 联网请求 | Get Contents of URL |
| 数据 | `json_parse` | 解析 JSON | Get Dictionary from Input |
| 数据 | `url_encode` | 编码 URL 参数 | URL Encode |
| 输出 | `show_result` | 展示结果 | Show Result |
| 输出 | `show_notification` | 提示完成 | Notification |
| 输出 | `share_output` | 分享结果 | Share |
| 输出 | `open_target` | 打开目标页面或应用 | Open URL / Open App |
| 落点 | `write_system_note` | 写入系统笔记 | Find Notes / Append to Note / Create Note |
| 落点 | `write_reminder` | 新建或编辑提醒事项 | Add New Reminder / Set Reminder |
| 落点 | `write_file` | 写入文件 | Save File / Append File |
| 落点 | `write_external_note_app` | 写入第三方笔记应用 | URI / 第三方动作 |
| Hybrid | `launcher_shortcut` | 快捷指令只做入口 | Ask / Share + Handoff |
| Hybrid | `handoff_result` | 把外部处理结果交给快捷指令 | Open File / Open URL / Share |
| Minis | `minis_query` | 通过 Minis 命令查询数据 | apple-healthkit / apple-weather / apple-location 等 |
| Minis | `minis_process` | 通过 Minis 命令处理输入 | apple-vision / apple-nlp / apple-speech 等 |
| Minis | `minis_hybrid_write` | Minis 处理后回写到系统 | Minis 命令 + apple-reminders / apple-calendar / apple-photos |

## 选择原则

### 1. 先选输入模式

先确定入口和输入，再决定后续路线。输入不清楚时，不进入生成。

### 2. 再选落点模式

先确定最终落点，再补控制和数据处理。不要先写中间动作再回头猜落点。

### 3. 控制模式只为解决分支和顺序问题

If、Menu、Repeat 都属于控制模式，只有在任务确实需要分支、条件或遍历时才引入。

### 4. 能用原生动作时不用外部模式

优先顺序：

1. 系统原生动作
2. 已文档化 AppIntent
3. 稳定 URI / URL Scheme
4. 第三方动作
5. Hybrid

## 组合规则

一个完整动作链通常按以下顺序组合：

1. 输入模式
2. 控制模式（可选）
3. 数据处理模式（可选）
4. 落点模式
5. 收尾输出模式

## 使用要求

- 模式用于加速规划，不替代边界澄清
- 模式名称应保持抽象，不绑定某个单一案例
- 如果同一模式在不同应用中复用，优先保留抽象名称，再在具体任务中绑定目标应用
- 对第三方应用，优先使用通用模式名，具体实现再映射到实际应用能力