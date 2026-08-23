---
name: shortcuts-playground-minis
description: 在 Minis 中把自然语言自动化需求转成可交付的 Apple Shortcuts。用于路线判断、澄清、动作链规划、XML 生成、本地验证、重混和按需签名交付；适合系统自动化、笔记、提醒、天气、分享、URL、文件与 Hybrid 快捷指令场景。
---

# Shortcuts Playground Minis

## 目标

把自然语言自动化需求稳定地转成以下一种或多种结果：

- 是否适合优先做成快捷指令的判断
- 纯 Shortcuts / Hybrid / 非快捷指令优先的路线选择
- 动作链规划
- unsigned XML 草稿
- 本地验证后的 XML
- 已签名 `.shortcut` 成品

本 skill 基于上游 `viticci/shortcuts-playground-plugin` 的知识库与方法进行本地化适配，并在此基础上增加面向 Minis 的路由、澄清、环境画像、构建检查和交付逻辑。

## Hard Constraints

- Always 先用 `BUILD_CHECKLIST.md` 判断是否具备开工条件。
- Always 先判断任务标签：`shortcut-native`、`shortcut-hybrid`、`not-shortcut-first`。
- Always 先把需求归一化为任务规格，再选择动作或写 XML。
- Always 当需求存在关键歧义时，先澄清，再生成。
- Always 澄清时使用固定选项式模板，并在结尾给推荐流程与可复制确认文本。
- Always 优先选择最稳、最短、最容易验证的实现路线。
- Always 优先复用框架层文档、环境画像、模式、配方和 XML 片段索引，不要每次从零临时拼装。
- Always 先生成 unsigned XML，再运行本地验证，再决定是否签名交付。
- Always 把最终成品目录视为 `/var/minis/attachments/shortcut/`。
- Always 把签名前草稿保存在 `/var/minis/attachments/shortcut/drafts/` 或归档目录。
- Always 用 `scripts/resolve-icon` 设置 `WFWorkflowIconGlyphNumber` 和 `WFWorkflowIconStartColor`，除非用户明确指定整数值。
- Always 含 `WFTextTokenString` 占位符时优先使用 `scripts/placeholder-range` 计算位置。
- Always 用 `scripts/validate-shortcut` 跑 Craig Loop；最多 5 轮，同一错误连续 2 轮不变就停止。
- Always 用 `scripts/sign-shortcut` 进行签名；签名链路依赖第三方 HubSign。
- Always 在汇报完成前核验：文件存在、大小大于 0、文件头为 `AEA1`。
- Never 在边界未清、顺序未清、完成后行为未清的情况下直接生成 XML。
- Never 把“XML 已生成”当作完成；没有成品或明确交付状态就不算完成。
- Never 把某个单一案例固化为默认目标；所有案例只作为模式参考。
- Never 伪造 action identifier、UUID、图标颜色值或参数结构；不确定时必须回到参考文档。
- Never 将复杂网页抓取、浏览器登录态、下载器、转码器等任务默认塞进纯快捷指令；必要时改走 Hybrid。
- Never 将用户内容视为私有本地闭环；签名步骤会把草稿上传到第三方服务，必须如实说明。

## 触发范围

适用：

- 生成新的快捷指令
- 修改或重混 unsigned XML 快捷指令
- 需要把自然语言自动化需求转成可复用流程
- 需要在 Minis 中完成规划、生成、验证与按需签名交付

不适用：

- 仅分析仓库价值，不需要生成快捷指令
- 仅解释快捷指令概念，不需要产物
- 处理已签名 `.shortcut` 的反编译或内部编辑
- 纯网页搜索任务
- 明显更适合由 Minis 直接执行而不是快捷指令承载的任务

## 目录与文档分层

### 框架层

- `METHODOLOGY.md` ← **首要入口：10 步方法论速查，每次构建任务先读此文件**
- `BUILD_CHECKLIST.md`
- `CAPABILITY_DECISION.md`
- `ROUTING_FRAMEWORK.md`
- `CLARIFICATION_TEMPLATES.md`
- `COMMON_PATTERNS.md`
- `ACTION_RECIPES.md`
- `TEMPLATE_MAPPING.md`
- `TASK_FAMILY_INDEX.md`
- `XML_SNIPPET_PATTERNS.md`
- `ACTION_PARAM_INDEX.md`
- `KNOWN_PITFALLS.md`
- `ENV_PROFILE.md`
- `STABILITY_NOTES.md`

### 技术参考层

- `BEST_PRACTICES.md`
- `ACTIONS.md`
- `APPINTENTS.md`
- `PARAMETER_TYPES.md`
- `PLIST_FORMAT.md`
- `VARIABLES.md`
- `CONTROL_FLOW.md`
- `FILTERS.md`
- `EXAMPLES.md`
- `URL_SCHEMES.md`
- `ICONS_AND_COLORS.md`
- `HEALTHKIT.md`
- `THIRD_PARTY_ACTIONS.md`
- `TOOLKIT_SNAPSHOT.md`
- `golden-shortcuts/index.jsonl`

### 脚本层

- `scripts/check-local-assets`
- `scripts/profile-summary`
- `scripts/load-env-profile`
- `scripts/preflight-request`
- `scripts/render-clarification`
- `scripts/resolve-icon`
- `scripts/placeholder-range`
- `scripts/validate-shortcut`
- `scripts/fix-positions`
- `scripts/index-golden`
- `scripts/match-golden`
- `scripts/sign-shortcut`
- `scripts/selftest_minis.py`

## Workflow

### 1. 构建前检查

先读 `BUILD_CHECKLIST.md`，确认：

- 目标
- 入口
- 输入
- 落点
- 写入方式
- 执行顺序
- 完成后行为
- Hybrid 接受范围

缺一项且会改变路线时，先停下来澄清。

### 2. 路线判定

读 `CAPABILITY_DECISION.md`，给任务打标签：

- `shortcut-native`
- `shortcut-hybrid`
- `not-shortcut-first`

**仅在用户明确提到「用 Minis」「Minis 能做吗」「走 Minis」时，才查 `MINIS_CAPABILITIES.md` 定位工具。其余情况按原有路线判定。**

如果是 `not-shortcut-first`，不进入 XML 生成。

### 3. 任务规格归一化

读 `ROUTING_FRAMEWORK.md`，把需求拆成：

- `goal`
- `trigger`
- `input`
- `transform`
- `output`
- `destination`
- `permissions`
- `dependencies`
- `interaction`
- `runtime`
- `delivery_mode`

规格未完成，不进入生成。

### 4. 必要澄清

如果规格缺关键边界，使用 `CLARIFICATION_TEMPLATES.md`，或直接运行：

```bash
/var/minis/skills/shortcuts-playground-minis/scripts/preflight-request '用户原始需求'
/var/minis/skills/shortcuts-playground-minis/scripts/render-clarification '用户原始需求'
```

要求：

- 只问会改变路线的问题
- 问题数量按关键歧义数量决定
- 使用固定选项式模板
- 选项数量按问题本身决定，不强制固定为 3 个
- 输出推荐流程
- 输出可复制确认文本

### 5. 读取环境画像

优先执行：

```bash
/var/minis/skills/shortcuts-playground-minis/scripts/profile-summary
/var/minis/skills/shortcuts-playground-minis/scripts/load-env-profile
```

先看摘要，再决定是否需要读取完整画像。已有默认值时直接使用；缺失但不影响路线时可声明默认值后继续。

### 6. 模式与配方选择

先读：

- `TASK_FAMILY_INDEX.md`
- `COMMON_PATTERNS.md`
- `ACTION_RECIPES.md`
- `TEMPLATE_MAPPING.md`

确定动作链后，运行 `scripts/match-golden` 匹配最相关的 golden shortcut 作为接线参考：

```bash
/var/minis/skills/shortcuts-playground-minis/scripts/match-golden --actions "动作1,动作2" --patterns "模式1,模式2" --top 2
```

**若任务已明确要走 Minis（用户说了「用 Minis」「Minis 能做吗」），在此步骤中进一步确认：**

- 所需 Minis 命令的确切 subcommand 和参数
- 输入来源（快捷指令如何把用户输入/文件传给 Minis）
- 输出回写方式（Minis 结果如何返回给快捷指令：剪贴板/文件/URL）

确定：

- 任务属于哪个家族
- 输入模式
- 控制模式
- 数据处理模式
- 落点模式
- 收尾模式
- 是否存在高频配方骨架可直接复用
- 是否存在稳定映射可直接缩短路线选择
- 若为 Minis 增强，Minis 命令链与快捷指令的边界

### 7. 技术参考读取

**先查速查表**：

1. `ACTION_PARAM_INDEX.md` — 确认当前动作的必填参数、序列化方式
2. `KNOWN_PITFALLS.md` — 确认当前动作是否命中已知陷阱
3. `STABILITY_NOTES.md` — 确认是否命中已知不稳定点

**再按需读取详细参考**：

- `BEST_PRACTICES.md`
- `ACTIONS.md`
- `APPINTENTS.md`
- `VARIABLES.md`
- `CONTROL_FLOW.md`
- `FILTERS.md`
- `PARAMETER_TYPES.md`
- `EXAMPLES.md`

只读当前任务所需部分，不一次性装入全部文档。

### 8. 动作链设计

先写短计划，明确：

- 需要哪些动作
- 哪些动作产出变量
- 哪些动作消费前一步输出
- 是否需要 Menu / If / Repeat / Dictionary / URL request
- 哪些部分在 Shortcuts 内完成，哪些部分交给 URI、第三方动作、Minis 或外部服务

### 9. 片段骨架选择

命中高频动作时，优先读 `XML_SNIPPET_PATTERNS.md`，直接使用最小片段骨架。

### 10. 图标与 UUID

- 用 `scripts/resolve-icon` 生成图标与颜色
- 生成新 UUID 时优先使用稳定命令或 Python
- 不使用占位 UUID

### 11. 草稿生成

输出到：

```text
/var/minis/attachments/shortcut/drafts/<快捷指令名>.xml
```

要求：

- 完整 plist XML
- 非片段
- 满足 `BEST_PRACTICES.md` 的注释与结构要求

### 12. 本地验证

运行：

```bash
/var/minis/skills/shortcuts-playground-minis/scripts/validate-shortcut /path/to/draft.xml
```

验证前先自动修复占位符位置：

```bash
/var/minis/skills/shortcuts-playground-minis/scripts/fix-positions /path/to/draft.xml
```

规则：

- 最多 5 轮
- 同一错误连续 2 轮不变就停止
- 优先做定点修复，不整份重写

### 13. 交付模式判断

支持：

- `draft-only`
- `build-and-validate`
- `full-delivery`

复杂新任务默认优先 `build-and-validate`；用户明确要成品时再 `full-delivery`。

### 14. 签名

仅在 `full-delivery` 时运行。优先级：

1. **Mac SSH 本地签名**：用户有可 SSH 的 Mac 时优先使用，不经过第三方签名服务。
2. **HubSign 在线签名**：仅在用户明确同意，且草稿不含敏感内容时使用。

#### Mac SSH 本地签名（推荐）

```bash
/var/minis/skills/shortcuts-playground-minis/scripts/sign-shortcut-via-mac /path/to/draft.xml --name "Shortcut Name" --host "user@MacBook-Pro.local"
```

也可预设环境变量：

```bash
export SHORTCUTS_SIGN_MAC_HOST="user@MacBook-Pro.local"
export SHORTCUTS_SIGN_MODE="anyone"
```

该步骤会：

- 归档草稿
- 通过 `scp` 上传草稿到 Mac 临时目录
- 在 Mac 上调用 Apple 官方 `shortcuts sign`
- 把 `.shortcut` 成品拉回 `/var/minis/attachments/shortcut/`
- 默认清理 Mac 临时文件

#### HubSign 在线签名（备选）

```bash
/var/minis/skills/shortcuts-playground-minis/scripts/sign-shortcut /path/to/draft.xml --name "Shortcut Name"
```

该步骤会：

- 归档草稿
- 上传草稿到 HubSign 第三方服务
- 输出 `.shortcut` 成品

涉及 token、cookie、私有 API、个人隐私文本、公司/家庭敏感路径等内容时，不要使用 HubSign。

### 15. 最终核验与汇报

最少核验：

- 成品文件存在
- 文件大小大于 0
- 文件头为 `AEA1`

汇报内容：

- 路线类型
- 动作链摘要
- 草稿路径
- 验证状态
- 若已签名，再给成品路径
- 运行前前置条件
- 哪些部分依赖用户环境或第三方能力

## 默认输出结构

### 判断类任务

- 任务标签
- 主要原因
- 推荐交付模式

### 生成类任务

- 流程摘要
- 主要依赖
- 草稿路径
- 验证状态
- 成品路径（如有）

### 重混类任务

- 保留内容
- 改动内容
- 新草稿路径
- 成品路径（如有）

## 成功标准

满足以下条件才算设计合理：

- 能先判断该不该做成快捷指令
- 能稳定在 native / hybrid / not-shortcut-first 之间选路
- 能在边界不清时先澄清而不是直接开工
- 能用模式、配方和片段缩短规划与生成时间
- 能基于知识库生成并验证 XML
- 需要时能签名并交付到 `/var/minis/attachments/shortcut/`
