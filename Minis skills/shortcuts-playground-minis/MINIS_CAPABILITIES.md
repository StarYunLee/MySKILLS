# MINIS_CAPABILITIES

## 作用

当构建快捷指令时，若任务涉及 iOS 系统能力、Minis 自身工具、或需要 Hybrid 执行，此文档提供**场景 → Minis 命令**的快速映射。

用于：
- 场景分析阶段：判断哪些 Minis 工具可覆盖用户需求
- Hybrid 路线设计：确定快捷指令入口 + Minis 后端执行的边界
- 命令参数确认：快速查阅命令用法，不用每次重新 `--help`

## 快速场景查找表

| 用户场景关键词 | 对应 Minis 工具 | 场景标签 |
|---|---|---|
| 闹钟、定时 | `apple-alarm` | 时间管理 |
| 提醒、待办、提醒事项 | `apple-reminders`、`apple-calendar remind` | 时间管理 |
| 日历、日程、会议 | `apple-calendar` | 时间管理 |
| 通知、推送提醒 | `apple-notification` | 系统交互 |
| 天气、温度、降雨 | `apple-weather` | 信息查询 |
| 位置、定位、附近、导航 | `apple-location`、`apple-maps` | 空间感知 |
| 地图、路线、通勤 | `apple-maps` | 空间感知 |
| 剪贴板、复制粘贴 | `apple-clipboard` | 输入输出 |
| 设备信息、电量、存储 | `apple-device` | 系统监控 |
| 健康、运动、步数、心率、睡眠 | `apple-healthkit` | 健康追踪 |
| 智能家居、灯、空调、场景 | `apple-homekit` | 智能家居 |
| 媒体、音乐、播放、音量 | `apple-media` | 媒体控制 |
| 播放器、视频、音频播放 | `apple-player` | 媒体控制 |
| 朗读、语音播报、TTS | `apple-speak` | 语音交互 |
| 语音识别、转文字、录音 | `apple-speech` | 语音交互 |
| NFC、读卡、写卡、银行卡 | `apple-nfc` | 物理交互 |
| 照片、相册、图片管理 | `apple-photos` | 媒体管理 |
| 视觉、OCR、扫码、人脸、图片分类 | `apple-vision` | AI 感知 |
| NLP、分词、情感、实体识别、嵌入 | `apple-nlp` | AI 感知 |
| 蓝牙、BLE 设备 | `apple-bluetooth` | 外设连接 |
| 浏览器、网页截图、网页抓取 | `minis-browser-use` | 网页交互 |
| Minis 对话、搜索历史、发消息 | `minis-sessions-cli` | Minis 自交互 |
| 调用 AI 模型、生成图片 | `minis-model-use` | AI 能力 |
| 应用设置、配置修改 | `minis-config` | 系统配置 |
| 打开文件、预览 URL | `minis-open`、`apple-open` | 通用入口 |

---

## 工具分类详解

### 1. 时间管理

| 工具 | 核心命令 | 典型场景 | Hybrid 适用 |
|---|---|---|---|
| `apple-alarm` | `set`、`timer`、`list`、`cancel` | 定时提醒、倒计时、闹钟管理 | ✅ |
| `apple-calendar` | `list`、`create`、`update`、`delete`、`remind`、`freebusy`、`calendars` | 日程查询、新建事件、空闲时段 | ✅ |
| `apple-reminders` | `list`、`create`、`update`、`complete`、`delete` | 待办管理、提醒创建 | ✅ |
| `apple-notification` | `schedule`、`pending`、`cancel`、`settings` | 本地推送、定时通知 | ✅ |

**场景匹配优先级**：
- 用户说"提醒我做X" → 先判断是系统提醒事项（`apple-reminders`）还是闹钟（`apple-alarm`）还是通知（`apple-notification`）
- 用户说"查看今天的日程" → `apple-calendar list --today`
- 用户说"下午2点叫我" → `apple-alarm set --time 14:00`

### 2. 信息查询

| 工具 | 核心命令 | 典型场景 | Hybrid 适用 |
|---|---|---|---|
| `apple-weather` | `current`、`hourly`、`daily`、`alerts`、`report` | 天气播报、出行建议、穿搭推荐 | ✅（查询类） |
| `apple-location` | `current`、`geocode`、`forward` | 当前位置、地址解析、坐标转换 | ✅ |
| `apple-maps` | `search`、`route`、`eta` | 周边搜索、导航规划、通勤时间 | ✅ |

**组合模式**：
- "出门前天气 + 通勤时间" → `weather current` + `maps eta`
- "附近有什么" → `location current` → `maps search --lat ... --lon ...`

### 3. AI 感知

| 工具 | 核心命令 | 典型场景 | Hybrid 适用 |
|---|---|---|---|
| `apple-vision` | `ocr`、`barcode`、`classify`、`detect`、`faces`、`analyze`、`similarity`、`overlap` | 图片文字识别、扫码、图像分类、人脸检测、图片相似度、长图拼接 | ✅（强烈推荐） |
| `apple-nlp` | `language`、`tokenize`、`pos`、`ner`、`sentiment`、`embed`、`analyze` | 语言检测、分词、词性标注、实体识别、情感分析 | ✅ |
| `apple-speech` | `transcribe`、`languages`、`status` | 语音转文字、会议记录 | ✅ |
| `apple-speak` | `speak`、`voices`、`stop` | 文字朗读、通知播报 | ✅ |

**组合模式**：
- "拍照提取文字并朗读" → `vision ocr` → `speak`
- "语音备忘录转文字" → `speech transcribe --source file` → 保存文本
- "分析照片内容并描述" → `vision analyze` → `speak`

### 4. 媒体管理

| 工具 | 核心命令 | 典型场景 | Hybrid 适用 |
|---|---|---|---|
| `apple-photos` | `list`、`near`、`albums`、`album`、`stats`、`export`、`import`、`favorite`、`delete` | 照片搜索、相册管理、导入导出 | ✅ |
| `apple-media` | `now-playing`、`play`、`pause`、`toggle`、`next`、`prev`、`volume`、`search`、`play-search` | 音乐控制、媒体库搜索 | ✅ |
| `apple-player` | `play`、`pause`、`resume`、`seek`、`status`、`stop`、`list` | 音视频播放控制 | ✅ |

**组合模式**：
- "把最近照片导出到 Minis" → `photos list --days 1` → `export --id ...`
- "搜索并播放某首歌" → `media play-search --query ...`

### 5. 智能家居

| 工具 | 核心命令 | 典型场景 | Hybrid 适用 |
|---|---|---|---|
| `apple-homekit` | `list`、`search`、`get`、`set`、`scenes`、`trigger` | 设备控制、场景执行 | ✅ |
| `apple-bluetooth` | `status`、`scan`、`connect`、`read`、`write`、`notify` | BLE 设备交互 | ✅ |

**场景匹配**：
- "回家模式" → `homekit trigger --name "到家"`
- "把客厅灯调暗" → `homekit set --name "客厅灯" --characteristic brightness --value 30`
- "扫描附近的蓝牙设备" → `bluetooth scan --duration 10`

### 6. 健康追踪

| 工具 | 核心命令 | 典型场景 | Hybrid 适用 |
|---|---|---|---|
| `apple-healthkit` | `steps`、`heart-rate`、`sleep`、`workouts`、`weight`、`summary`、`batch`、`types`、`log`、`delete` | 健康数据查询、运动汇总、数据写入 | ✅ |

**高频场景**：
- "今日步数" → `healthkit steps --today`
- "本周运动汇总" → `healthkit summary --days 7`
- "睡眠分析" → `healthkit sleep --days 7`
- "批量导出健康数据" → `healthkit batch --types steps,heart-rate,sleep,active-energy --days 7`

### 7. 系统交互与设备

| 工具 | 核心命令 | 典型场景 | Hybrid 适用 |
|---|---|---|---|
| `apple-clipboard` | `get`、`set`、`clear`、`status` | 剪贴板读写、文本中转 | ✅ |
| `apple-device` | `info`、`battery`、`storage` | 设备监控、电量查询 | ✅ |
| `apple-open` | `<url>`、`settings[://page]` | 打开 App/URL/设置 | ✅ |
| `minis-open` | `<url-or-path>` | Minis 内预览文件/URL | — |
| `minis-config` | `get`、`set`、`list-topics`、`audit-list` | 修改 Minis 设置 | —（慎用） |

**典型用途**：
- 快捷指令处理完文本后复制到剪贴板 → `clipboard set --text "..."`
- 快捷指令完成后打开某个 App → `apple-open "app-scheme://"`

### 8. NFC 与物理交互

| 工具 | 核心命令 | 典型场景 | Hybrid 适用 |
|---|---|---|---|
| `apple-nfc` | `scan`、`write`、`tag-info`、`read-emv`、`apdu`、`felica`、`search` | NFC 标签读写、银行卡读取、交通卡查询 | ✅ |

**典型用途**：
- "扫描 NFC 标签获取内容" → `nfc scan`
- "读取公交卡余额" → `nfc felica` 或 `nfc apdu`

### 9. 网页交互（Minis 特有）

| 工具 | 核心命令 | 典型场景 | Hybrid 适用 |
|---|---|---|---|
| `minis-browser-use` | `navigate`、`screenshot`、`click`、`type`、`get_text`、`get_readable`、`fetch`、`scroll_and_collect`、`execute_js` | 网页截图、内容提取、表单填写、文件下载 | ✅（核心） |

**典型用途**：
- "截取这个网页" → `browser-use navigate` → `screenshot --full-page`
- "提取文章正文" → `browser-use navigate` → `get_readable`
- "从网页下载文件" → `browser-use navigate` → `fetch --url ...`

### 10. Minis 自交互

| 工具 | 核心命令 | 典型场景 | Hybrid 适用 |
|---|---|---|---|
| `minis-sessions-cli` | `list`、`search`、`messages`、`send`、`retry`、`status`、`open` | 对话历史搜索、自动化对话、跨会话查询 | ✅ |
| `minis-model-use` | `list`、`search`、`run` | 调用 AI 模型、生成图片、文本/音频/视频生成 | ✅ |

**典型用途**：
- "搜索之前的对话" → `sessions-cli search --keywords "..."`
- "让 AI 生成图片" → `model-use run --model ... --prompt "..."`

---

## Hybrid 路线中的 Minis 命令使用模式

### 模式 A：快捷指令作入口 + Minis 作后端

```
快捷指令: Ask for Input → URL (minis-sessions-cli send) → Open URL
Minis:    接收输入 → 执行命令链 → 返回结果
```

**适用场景**：
- 快捷指令本身不支持的能力（NFC 读写、蓝牙交互、HealthKit 查询等）
- 需要 AI 处理的复杂任务

### 模式 B：快捷指令采集 + Minis 处理 + 回写系统

```
快捷指令: Share Sheet → Get File → Save File (到 /var/minis/)
Minis:    监听文件 → 处理（OCR/分析/转换）→ apple- 命令回写
```

### 模式 C：Minis 命令直接嵌入快捷指令

通过 `apple-open` 配合 URL Scheme 或 `shortcuts://run-shortcut` 实现：
- 快捷指令内调用 `apple-open "shortcuts://run-shortcut?name=..."` 链式触发

---

## 使用规则

1. **场景分析阶段**：先查"快速场景查找表"，定位相关工具
2. **路线判定**：如果任务核心能力在 Minis 工具而不在 Shortcuts 原生动作 → 标记为 `shortcut-hybrid`
3. **命令确认**：确定工具后查阅本文档的命令分类详情，确认参数
4. **不确定参数时**：在 shell 中运行 `<tool> --help` 获取最新帮助
5. **不在此文档中的命令**：直接运行 `ls /usr/local/bin/apple-* /usr/local/bin/minis-*` 查看完整列表

## 维护原则

- 新增 Minis 命令时同步更新本文档
- 场景关键词可按需扩展，但要保持一个关键词对应一个明确的工具
- 不重复 `--help` 的全部细节，只保留构造快捷指令时最常用的参数组合
