# Action Recipes

## 作用

提供高频动作链骨架，用于快速选择实现路线。配方描述的是结构，不是具体案例。

## 配方目录

| 配方 | 适用场景 | 标准动作链 |
|---|---|---|
| `collect_text_then_write` | 获取一段文本后写入单一目标 | `ask_text → write_target → notify` |
| `collect_text_then_choose_destination` | 同一输入可写入多个目标 | `ask_text → choose_menu → branch_write → notify` |
| `share_input_then_process` | 从分享菜单接收外部内容后处理 | `share_input → transform → output` |
| `query_then_show` | 输入参数后查询并展示结果 | `ask_or_context → request_or_native_query → format → show` |
| `construct_and_open_uri` | 构造深链并打开 | `prepare_value → urlencode → url → open_url` |
| `task_then_followup` | 完成核心任务后继续执行后续动作 | `core_task → followup_action` |
| `hybrid_launcher` | 快捷指令作为入口，复杂处理交给外部能力 | `collect_input → handoff → optional_notify` |

## 配方说明

### `collect_text_then_write`

适用：

- 记录到系统笔记
- 新建提醒事项
- 写入固定文件
- 写入第三方笔记应用

关键点：

- 输入方式通常为 `ask_text`
- 目标写入方式必须先确定：新建、固定对象、先选对象
- 完成后是否提示、是否跳转要单独确认

### `collect_text_then_choose_destination`

适用：

- 同一输入可能落到多个目标
- 目标之间动作链不同，但输入相同

关键点：

- 先确定目标集合是否固定
- 分支数量应与菜单项一一对应
- 每个分支都应独立完成写入与收尾

### `share_input_then_process`

适用：

- 分享网页、图片、文件、文本后再处理

关键点：

- 先确认分享输入类型
- 再确认处理方式是提取、转换、保存还是转发

### `query_then_show`

适用：

- 天气、汇率、日历、基础 API 查询

关键点：

- 优先原生查询动作，其次简单双向 HTTP
- 展示结果时优先生成最终可读文本，再显示或通知

### `construct_and_open_uri`

适用：

- 目标应用通过 URI / URL Scheme 提供写入、打开或跳转能力

关键点：

- 动态参数优先经过 `url_encode`
- `WFTextTokenString` 的变量位置不得手算
- 需要打开目标时，用 `open_url` 作为最后一步之一

### `task_then_followup`

适用：

- 记录后自动打开目标
- 保存后继续分享
- 完成后继续跳转下一步

关键点：

- 必须先确认“完成后是否继续动作”
- Follow-up 不是默认行为，只有用户明确需要时才加入

### `hybrid_launcher`

适用：

- 快捷指令本身不适合承载全部逻辑
- 需要网页处理、下载器、外部脚本、签名或复杂数据处理

关键点：

- 快捷指令负责入口、参数采集、结果回显
- 复杂执行交给 Minis 或外部服务
- 若用户只接受纯快捷指令，不应默认套此配方

## 配方选择顺序

1. 先看输入类型
2. 再看目标落点
3. 再看是否存在分支
4. 再看是否需要执行后续动作
5. 最后判断是否改走 Hybrid

## 使用限制

- 配方不能替代必要澄清
- 配方不能覆盖目标应用的具体参数校验
- 同一配方可绑定不同目标，不应被某个单一应用命名绑死