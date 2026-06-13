# ENV_PROFILE

## 作用

记录会显著影响快捷指令生成路线的默认环境信息。生成时优先读取这些默认值；缺失且会改变路线时再最小澄清。

## 设计原则

- 只保留跨任务可复用的抽象字段
- 不把某个单一应用、单一笔记标题、单一文件名写成通用默认结构
- 示例配置只展示字段类型与层级，不固化具体业务实例
- 具体应用参数应在任务命中该应用时再补齐

## 建议结构

```json
{
  "system_targets": {
    "default_note_folder": "",
    "default_note_identifier": "",
    "default_reminder_list": ""
  },
  "external_targets": {
    "default_app": "",
    "default_target_identifier": "",
    "supports_uri_write": false,
    "supports_action_extension": false
  },
  "minis_integration": {
    "prefer_hybrid_when_available": true,
    "default_minis_output_mode": "clipboard",
    "allow_minis_browser": true,
    "allow_minis_model_calls": true
  },
  "permissions": {
    "allow_third_party_signing": true,
    "allow_network_requests": true,
    "allow_open_url_schemes": true
  },
  "delivery_mode": "full-delivery"
}
```

## 字段说明

- `system_targets.default_note_folder`：默认系统笔记文件夹
- `system_targets.default_note_identifier`：默认系统笔记对象标识，例如固定标题或其他稳定识别值
- `system_targets.default_reminder_list`：默认提醒事项列表名
- `external_targets.default_app`：默认第三方目标应用标识
- `external_targets.default_target_identifier`：第三方目标对象标识，例如目标页面、对象 ID、文件路径或其他可定位值
- `external_targets.supports_uri_write`：是否支持通过 URI/URL Scheme 写入
- `external_targets.supports_action_extension`：是否支持通过快捷指令动作或插件写入
- `minis_integration.prefer_hybrid_when_available`：当 Minis 命令可覆盖需求时，是否优先走 Hybrid 路线
- `minis_integration.default_minis_output_mode`：Minis 处理结果默认返回方式：`clipboard`（写剪贴板）、`file`（写文件）、`notification`（发通知）
- `minis_integration.allow_minis_browser`：是否允许快捷指令触发 Minis 浏览器操作
- `minis_integration.allow_minis_model_calls`：是否允许快捷指令触发 Minis AI 模型调用
- `permissions.allow_third_party_signing`：是否接受 HubSign
- `permissions.allow_network_requests`：是否允许联网请求类快捷指令
- `permissions.allow_open_url_schemes`：是否允许通过 URL Scheme 调起第三方应用
- `delivery_mode`：默认生成草稿、验证版还是成品

## 使用规则

- 有默认值时直接用
- 缺失但不影响路线时，可声明默认假设继续
- 缺失且会改变路线时，进入澄清
- 只有命中具体应用时，才把抽象字段映射成该应用所需参数
