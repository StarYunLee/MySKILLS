# Template Mapping

## 作用

把高频需求映射到：

- 任务标签
- 适用配方
- 优先动作模式
- 常用 XML 片段
- 默认交付模式

用于缩短从自然语言到 XML 的规划时间。

## 映射表

| 需求类型 | 任务标签 | 优先配方 | 关键模式 | 常用片段 | 默认交付 |
|---|---|---|---|---|---|
| 快速记录文本到单一目标 | `shortcut-native` | `collect_text_then_write` | `ask_text`, `write_target`, `show_notification` | Ask, Append/Create Note, Add Reminder, Notification | `build-and-validate` |
| 同一输入写入多个目标 | `shortcut-native` / `shortcut-hybrid` | `collect_text_then_choose_destination` | `ask_text`, `menu_select`, `branch_write` | Ask, Menu, destination snippets | `build-and-validate` |
| 分享输入后处理 | `shortcut-native` / `shortcut-hybrid` | `share_input_then_process` | `share_input`, `transform`, `output` | Share input related snippets | `build-and-validate` |
| 查询并展示结果 | `shortcut-native` | `query_then_show` | `ask_or_context`, `request_or_native_query`, `show_result` | Ask, URL/HTTP, Text, Show Result | `build-and-validate` |
| 构造 URI 并打开目标 | `shortcut-native` / `shortcut-hybrid` | `construct_and_open_uri` | `url_encode`, `url`, `open_url` | URL Encode, URL, Open URL | `build-and-validate` |
| 完成后继续打开目标 | `shortcut-native` / `shortcut-hybrid` | `task_then_followup` | `core_task`, `followup_action` | destination + Open URL/App | `build-and-validate` |
| 快捷指令仅做入口 | `shortcut-hybrid` | `hybrid_launcher` | `collect_input`, `handoff`, `notify` | Ask/Share + handoff | `draft-only` / `build-and-validate` |

## 使用规则

1. 先做路线判定
2. 再在本表中找最接近的需求类型
3. 确定配方后，再落到 `COMMON_PATTERNS.md` 与 `XML_SNIPPET_PATTERNS.md`
4. 若需求命中多个类型，优先按“入口 → 落点 → 后续行为”的顺序选择主配方

## 不要这样用

- 不要跳过路线判定直接套配方
- 不要把映射表当成案例库
- 不要在边界未澄清时直接按表生成 XML
