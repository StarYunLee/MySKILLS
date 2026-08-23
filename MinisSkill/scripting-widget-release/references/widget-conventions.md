# Widget 已验证约定

这些是真机或跨组件复验过的规则。官方文档冲突时：同机已工作组件优先，再补一次诊断，不要只引用文档改掉稳定行为。

## 刷新

- `Widget.present({ policy: "after" })` 只提交最早刷新时间，不是定时器。
- 不要把 1 / 5 分钟写成可兑现刷新周期。
- 用持久化 `lastRun` / `status` / `nextRequestedAt` 区分「WidgetKit 没唤醒」和「后台请求失败」。
- 手动刷新：已验证的 `reloadUserWidgets()` 优先，`reloadAll()` 兜底。不要只因公开文档只写了后者就删掉前者。
- 对易 429 的内部用量接口加最短实时请求间隔；失败回最近缓存。

## 时间文案

- `DateLabel(relative)` 不适合做“数据更新时间”：1 分钟内秒级跳动，且会把「2秒 / 前更新」拆成两行。
- 用静态绝对时间：当天 `更新 HH:mm` / `缓存 HH:mm`，跨天带日期。只在数据真正变化时更新。

## 布局与数据

- Usage 双布局：`overview | detail`。标题由用户所选 focus 决定，不依赖可空 API 窗口对象。
- 所选窗口缺失：该位置显示 `—`。不要回退到另一个额度。HTTP 200 且 JSON 合法时，即使全部窗口为 `null` 也要写入 live 空快照，不要回退旧缓存。只有响应不是合法 JSON、或 HTTP/网络失败，才算整次失败。
- Anthropic `/api/oauth/usage` 必须带 `User-Agent: claude-code/<version>`；缺这个头会被持续 429。Token 端点的 `User-Agent: anthropic` 不要复用到 usage。
- Codex / Grok / Claude 这类内部用量接口，缺官方客户端标识会进限流桶。改请求头前先对照同机已工作组件和社区一手证据，不要只抄 Token 端点。
- `remaining` 缺失不得显示成 `0%`。
- 进度条永远是已用比例，即使文案是“剩余”。
- 官方临时下线某个窗口（例如 Codex 五小时）：保留双额度布局位置，缺数据就显示 `—`，不要删布局、不要迁移掉用户设置。
- 只加布局时冻结 OAuth、账号迁移、Keychain/Storage、请求解析、缓存。视图层做窗口选择，不要改 API 层。

## 账号设置

- 全局默认 + 每账号覆盖。刷新频率保持全局。
- 切换账号读该账号覆盖；无覆盖则继承全局。
- 删除账号或取消未完成授权时清掉对应覆盖。
- Storage key 可以带版本后缀（如 `_v1`）；不要无故改名。
- Widget 参数：邮箱优先；空参数用默认账号；兼容旧 `profileId` / JSON。

## Mock

正式发布可以带只读 Mock，但必须同时满足：

- 不写真实账号注册表
- 不写真实 Keychain
- 不发起 OAuth / 网络请求
- 不能设为默认账号
- 不能删除
- 布局和已用/剩余可独立保存
- 用独立参数（如 `mock.pro20x@codex.local`）绑定小组件

旧规则「正式发布前必须删除 Mock」已废止。独立 Mock **工程**（如 `Claude Usage Account Mock`）默认不进发布仓。

## Surge Metrics

- 流量用接口原生累计 counter，引擎重启归零。不要用两次 Widget 采样差分冒充实时速率。
- Medium：累计上下行 + 内存 / 活跃 / DNS / 运行时长。
- Large：核心总览 + 累计最高的 3 个接口。不要再做策略 Top。
- API Key 只存在本机 Storage；日志脱敏。
- 设置页改字段后必须点保存 / 测试 / 刷新才写入。

## 安全

- Token / Refresh Token：脚本隔离 Keychain。
- 注册表、设置、缓存：Storage，组件间命名空间独立。
- OAuth：Authorization Code + PKCE；state/verifier 临时 Keychain，10 分钟过期；结束即删。
- 内部用量接口按不稳定 API 处理：401 刷新，403 / 429 / 缺字段 / 网络错误走缓存。
- 不要用 OAuth Token 到期时间冒充订阅到期。
- 辅助接口（重置权益等）失败不得阻断主用量。
