# XML Snippet Patterns

## 作用

为高频动作提供最小结构索引，减少从长文档检索参数的成本。

## 使用顺序

1. 先确定动作链
2. 再选对应片段骨架
3. 再填变量与参数
4. 最后运行本地验证

## 高频片段索引

| 片段 | 动作标识符 | 必填键 | 输入接线要点 | 常见错误 |
|---|---|---|---|---|
| Ask / Text | `is.workflow.actions.ask` | `UUID`, `WFAskActionPrompt` | 文本输入时加 `WFInputType = Text` | 缺少 Prompt |
| Menu / Start | `is.workflow.actions.choosefrommenu` | `GroupingIdentifier`, `WFControlFlowMode=0`, `WFMenuItems` | 起始节点必须有菜单项 | 菜单项为空 |
| Menu / Case | `is.workflow.actions.choosefrommenu` | `GroupingIdentifier`, `WFControlFlowMode=1`, `WFMenuItemTitle` | 标题必须与菜单项对应 | 分支标题不匹配 |
| Menu / End | `is.workflow.actions.choosefrommenu` | `GroupingIdentifier`, `WFControlFlowMode=2` | 一组菜单必须闭合 | 缺少结束节点 |
| Find Notes | `is.workflow.actions.filter.notes` | `UUID`, `WFContentItemFilter` | `WFContentPredicateTableTemplate`；Name 用 `Operator=99` | 把 Name 写成 `Operator=4` |
| Append to Note | `is.workflow.actions.appendnote` | `IntentAppIdentifier`, `WFInput`, `WFNote` | 文本来自上一步输出；Note 来自 Find Notes 输出 | `WFNote` 未接线 |
| Add New Reminder | `is.workflow.actions.addnewreminder` | `UUID`, `WFCalendarItemTitle` | 最小稳定参数为标题；列表通常补 `WFCalendarItemCalendar` | 一开始就填过多可选参数 |
| URL Encode | `is.workflow.actions.urlencode` | `UUID` | 对即将嵌入 URI 的动态文本先编码 | 直接把原始文本拼进 URI |
| URL | `is.workflow.actions.url` | `UUID`, `WFURLActionURL` | 动态内容优先用 `WFTextTokenString` | 占位位置错误 |
| Open URL | `is.workflow.actions.openurl` | `WFInput` | 输入通常来自 URL 动作输出 | 缺少 `WFInput` |
| Notification | `is.workflow.actions.notification` | 无强制固定最小键 | 常用 `WFNotificationActionTitle`, `WFNotificationActionBody` | 标题或正文为空 |

## 重点规则

### 1. Find Notes

- `WFContentItemFilter` 必须是 `WFContentPredicateTableTemplate`
- 按标题查找时，`Name` 只能用 `Operator = 99`
- `Values.String` 使用 `WFTextTokenString`

### 2. Append to Note

- `WFInput` 是要追加的内容
- `WFNote` 是 Note 对象，不是标题字符串
- 典型前置动作是 `Find Notes`

### 3. Add New Reminder

- 最小可运行用法优先只填标题和列表
- 复杂提醒时间、位置、备注属于后续扩展，不应默认加入

### 4. URI 类动作

- 所有动态 URI 文本优先先编码
- 含 `￼` 的 `WFTextTokenString` 不手算位置
- 位置计算统一使用：

```bash
/var/minis/skills/shortcuts-playground-minis/scripts/placeholder-range 'text with ￼ placeholder'
```

## 片段选择规则

- 优先选最小可运行结构
- 先保证验证通过，再补可选参数
- 若某动作已有稳定前置动作组合，优先按常见组合使用，不单独孤立拼接