# Methodology

## 目标

提供快捷指令构建的 10 步方法论速查，作为每次构建任务的第一入口。

本文件是索引层，不负责记录单一应用的默认值，也不绑定具体案例。

---

## Step 1: 判断路线

**不要接到需求就写 XML。先判断任务是否适合做成快捷指令，以及该走哪条路线。**

决策输出三类标签：

| 标签 | 含义 |
|------|------|
| `shortcut-native` | 纯原生动作可完成 |
| `shortcut-hybrid` | 快捷指令做入口，复杂逻辑交给外部 |
| `not-shortcut-first` | 不适合做成快捷指令 |

判断依据：输入是否简单、输出是否落在系统应用、是否依赖登录态/网页/长时间后台。

详细决策树 → [`CAPABILITY_DECISION.md`](CAPABILITY_DECISION.md)

---

## Step 2: 归一化任务规格

把自然语言需求拆成标准字段：

- **input**：从哪来（分享、剪贴板、手动输入、无输入）
- **transform**：中间做什么（拼接、判断、请求、过滤）
- **output / destination**：结果落在哪（备忘录、提醒、通知、文件）
- **trigger**：怎么触发（分享菜单、手动运行、小组件、自动化）
- **interaction**：全自动还是需要用户交互

这组字段没理清之前，不进入动作选择。

完整字段列表 → [`ROUTING_FRAMEWORK.md`](ROUTING_FRAMEWORK.md)

---

## Step 3: 最小澄清

**边界不清的信息会改变实现路线时，必须先问；可用默认值推进的不问。**

规则：

- 使用固定选项式模板，不用开放式追问
- 问题数量按关键歧义数量决定，不人为限制为固定 1~3 个
- 每个问题的选项数量按问题本身决定，不强制固定为 3 个
- 提问后附一版推荐流程 + 可直接复制确认的文本
- 只覆盖会改变动作链结构的歧义，不把可默认的信息变成问答

典型必问场景：输入方式不明、写入方式不明（新建 / 追加 / 选择）、是否接受第三方服务。

澄清模板 → [`CLARIFICATION_TEMPLATES.md`](CLARIFICATION_TEMPLATES.md)

---

## Step 4: 搭动作链骨架

**先用自然语言列出动作序列，再进入 XML。骨架对了参数是填空题，骨架错了参数填得再精确也白搭。**

骨架需要明确：

- 需要哪些动作，先后顺序是什么
- 谁的输出喂给谁的输入（数据流）
- 有无分支（If）、循环（Repeat）、菜单（Menu）
- 哪些部分是 Shortcuts 内完成，哪些交给外部

输出格式示例：

```
share_input → detect_link → set_variable → if_exists → clipboard_fallback →
find_note → format_date → text_template → append_note → notification
```

---

## Step 5: 选配方与模式

**大多数快捷指令是几个原子模式的排列组合。优先从已有配方中选，不从零发明。**

常用原子模式：

| 类别 | 典型模式 |
|------|---------|
| 输入 | `clipboard_in`、`share_input`、`ask_text`、`choose_menu` |
| 控制 | `if_exists`、`if_string_match`、`menu_branch`、`repeat_each` |
| 处理 | `text_template_with_variables`、`replace_text`、`format_date`、`http_get` |
| 落点 | `append_note`、`find_note`、`create_reminder`、`save_file`、`notification` |

配方骨架 → [`ACTION_RECIPES.md`](ACTION_RECIPES.md)
原子模式目录 → [`COMMON_PATTERNS.md`](COMMON_PATTERNS.md)

确定动作链后，用 `scripts/match-golden` 匹配最相关的 golden shortcut 作为接线参考。

---

## Step 6: 按需读参考文档

**不要一次性读入全部参考文件。按动作链中涉及的动作类型，按需读取。**

读取顺序：

1. **先查速查表**：[`ACTION_PARAM_INDEX.md`](ACTION_PARAM_INDEX.md)（必填参数 + 序列化方式）+ [`KNOWN_PITFALLS.md`](KNOWN_PITFALLS.md)（已知陷阱）
2. 先读环境画像（`load-env-profile`）
3. 命中高频动作时，先从 [`XML_SNIPPET_PATTERNS.md`](XML_SNIPPET_PATTERNS.md) 取最小片段骨架
4. 遇到不确定的参数结构，再读 [`ACTIONS.md`](ACTIONS.md)、[`VARIABLES.md`](VARIABLES.md)、[`PARAMETER_TYPES.md`](PARAMETER_TYPES.md)
5. 涉及控制流时读 [`CONTROL_FLOW.md`](CONTROL_FLOW.md)
6. 涉及过滤器时读 [`FILTERS.md`](FILTERS.md)
7. 通用规则查 [`BEST_PRACTICES.md`](BEST_PRACTICES.md)

---

## Step 7: 生成 XML 草稿

**UUID 必须用工具生成，占位符位置必须用脚本计算，两者都不能手工推算。**

核心约束：

- UUID：`python3 -c "import uuid; print(str(uuid.uuid4()).upper())"` 生成，不得复用或伪造
- 占位符位置：`scripts/placeholder-range` 计算 `{position, 1}`，不手数
- 图标与颜色：`scripts/resolve-icon --prompt "..."` 生成
- 输出路径：`/var/minis/attachments/shortcut/drafts/<名称>.xml`
- 必须是完整 plist XML，不是片段

变量引用要点：

- 显示参数（通知 body、Alert message、Show Result）→ 必须用 `WFTextTokenString`
- 数据流参数（WFInput、WFDate）→ 可用 `WFTextTokenAttachment`
- If 条件的 `WFInput` → 必须用 `Type=Variable` 包装器

详细规则 → [`VARIABLES.md`](VARIABLES.md)、[`BEST_PRACTICES.md`](BEST_PRACTICES.md)

---

## Step 8: 验证与定点修复

**写完必须跑验证。"写完了"和"验过了"是两回事。**

验证前先自动修复占位符位置：

```bash
scripts/fix-positions "/path/to/draft.xml"
scripts/validate-shortcut "/path/to/draft.xml"
```

Craig Loop 规则：

- 最多 5 轮修 → 验循环
- 每轮只做**定点修复**，不整份重写——重写容易引入新问题
- 同一错误连续 2 轮不变 → 停止，换思路或报告用户
- 没有做出实际修改时不重跑验证

---

## Step 9: 签名与硬核验收

**签名前说明会上传到第三方服务。签名后必须做文件级验收。**

签名：

```bash
scripts/sign-shortcut "/path/to/draft.xml" --name "快捷指令名"
```

验收三项缺一不可：

| 检查项 | 标准 |
|--------|------|
| 文件存在 | 成品路径下 `.shortcut` 文件存在 |
| 文件大小 | > 0 字节 |
| 文件头 | 前 4 字节为 `AEA1` |

任一项不通过，不得宣称完成。

---

## Step 10: 交付与前置条件

**交付成品时必须同时说清运行前提，不能只给文件。**

交付清单：

- 成品 `.shortcut` 文件路径（可点击安装）
- 草稿 `.xml` 文件路径（可回溯修改）
- 路线类型（native / hybrid）
- 前置条件：用户需要提前准备什么（如"先建一个叫 X 的备忘录"）
- 触发方式：手动运行 / 分享菜单 / 两者兼容
- 第三方服务声明：是否经过 HubSign 等外部服务签名

---

## 速查流程图

```
需求 → Step 1 判断路线
         ↓
     Step 2 归一化规格
         ↓
     Step 3 最小澄清（可跳过）
         ↓
     Step 4 搭骨架
         ↓
     Step 5 选配方模式
         ↓
     Step 6 按需读参考
         ↓
     Step 7 生成 XML
         ↓
     Step 8 验证修复（≤5 轮）
         ↓
     Step 9 签名验收
         ↓
     Step 10 交付 + 前置条件
```

## 与现有文档的关系

本文件是**方法论索引层**，不包含动作参数细节、XML 结构规范或验证器规则。

| 需要什么 | 去哪里找 |
|----------|---------|
| 任务是否适合做快捷指令 | `CAPABILITY_DECISION.md` |
| 任务规格字段与路线优先级 | `ROUTING_FRAMEWORK.md` |
| 澄清问题模板 | `CLARIFICATION_TEMPLATES.md` |
| 配方骨架 | `ACTION_RECIPES.md` |
| 原子模式目录 | `COMMON_PATTERNS.md` |
| 最小 XML 片段 | `XML_SNIPPET_PATTERNS.md` |
| **高频动作参数速查** | **`ACTION_PARAM_INDEX.md`** |
| **已知动作陷阱** | **`KNOWN_PITFALLS.md`** |
| **匹配最相关 golden shortcut** | **`scripts/match-golden`** |
| **自动修复占位符位置** | **`scripts/fix-positions`** |
| 动作标识符与参数 | `ACTIONS.md`、`PARAMETER_TYPES.md` |
| 变量引用与占位符 | `VARIABLES.md` |
| 控制流结构 | `CONTROL_FLOW.md` |
| 过滤器结构 | `FILTERS.md` |
| 通用硬规则 | `BEST_PRACTICES.md` |
| 构建前检查清单 | `BUILD_CHECKLIST.md` |
