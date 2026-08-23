---
name: scripting-app-development
description: "使用 Scripting App 的 TypeScript/TSX 与 scripting 包开发、修改、调试和验证 iOS 脚本项目。覆盖 index.tsx、widget.tsx、intent.tsx、app_intents.tsx、Live Activity、富通知、控制中心、Home Screen UI、Keyboard、Spotlight、Translation UI、Assistant Tools、Alarm Live Activity、Safari browser scripts，以及 desktop scripting-cli。当用户提到 Scripting App、Scripting 项目、TSX 小组件、灵动岛或相关入口文件时使用。API 以官方 llms.txt 为准。"
---

# Scripting App Development

帮助用户创建、修改、调试或验证 **Scripting App** 脚本项目。这是技术开发指南；不规定通用任务规划、规格文档或通用 coding-agent 流程。官方正文不规定 Git 流程；用户自有 App 的本地脚手架见下方。

基线：官方仓库 `https://github.com/ScriptingApp/scripting-app-development`，当前同步 `2991c41`（2026-08-04；2026-08-19 复核 HEAD 仍是该提交）。下方 Minis 段覆盖语言、文档索引、用户脚手架和发布分流；其余以官方正文为准。

## Minis / 用户偏好（覆盖本 skill 默认语言）

- **对用户回复使用简体中文**（代码、API 符号、文件名保持英文原样）。
- 先结论后细节；完成时按下方 Completion response 结构化汇报。
- 文档索引优先中文：`https://scriptingapp.github.io/zh/llms.txt`；中文索引缺页或需对照英文时再用 `https://scriptingapp.github.io/llms.txt`。
- Minis 环境通常没有内置 `scripting_reference` 工具；不要假装已查过 bundled docs。若当前会话确实提供了该工具，再优先用它。

## Scope and routing

适用于 Scripting 项目或下列文件/能力：

- `script.json`、`index.tsx`、共享 `.ts` / `.tsx` 模块、SwiftUI 风格 TSX 页面
- `widget.tsx`、`app_intents.tsx`、`live_activity.tsx`、`notification.tsx`、`intent.tsx`
- `browser.tsx` 或独立安装的 Safari `.user.js`
- Desktop 编辑器与 `scripting-cli` 实时同步/调试
- Scripting 提供的 iOS API（Notification、Calendar、Location、Photos、Storage、Speech、Device 等）
- 高级入口：Home Screen default UI、控制中心控件、自定义键盘、Spotlight、Translation UI、Assistant Tools、Alarm Live Activities

不要用本 skill 代替：独立 Apple 快捷指令、普通 Node/Python 自动化、或通用 Web App。

用户自有仓库的**打包、展示图、上传前审查、GitHub 发布**走配套 skill `scripting-widget-release`。本 skill 仍负责官方 API、项目结构和宿主验证；两边都涉及时先守发布门禁，再查本 skill 的文档与改码规则。版本以各项目 `script.json` 为准。

宿主限制（真机已确认，官方文档未必写）：

- `HttpServer` 需要 Scripting PRO；不要默认用它做 OAuth 本地收码，继续让用户粘贴回调。`Safari.present` / `Notification.schedule` 暂无 Pro 证据。
- `Navigation.present` 自带系统关闭槽，不能改成玻璃按钮；不要再叠 `cancellationAction` / `topBarLeading`，否则会出现两个 X。
- 快捷指令「运行意图脚本」只列出有 `intent.tsx` 的项目；`app_intents.tsx` 不会单独出现在搜索里。定时刷新要走 `intent.tsx`，不要只写 App Intent。
- `Widget.reloadAll()` 会重载 Scripting 里所有小组件，不是只刷新当前项目。界面文案不要写成「仅本应用」。
- 渲染期禁止同步调用 `GitHub.getAvailability()` / Keychain；首屏只渲染静态 UI，探测放到 `useEffect`。`toolbar` 必须是官方 `ToolBarProps` 对象（如 `{ topBarTrailing: ... }`），不能写成 JSX 节点，否则真机首屏空白。
- 不要把 `Fragment` + `Divider` 当作 List 行根节点：Scripting List 会把 Fragment 子节点拆成独立行，Divider 会变成空白玻璃行。每行单一 VStack 根。
- 不要在渲染期把可选 modifier 设成 `undefined`（如 `padding={undefined}`），真机可能整行不渲染。可选样式拆成两套明确 JSX。

## Mandatory official-documentation workflow

写或改**任何** Scripting 专用 API 之前：

1. 若当前环境有 bundled Scripting reference / API declarations（例如 `scripting_reference`），先查它。
2. Minis 默认没有该工具，改查公开 LLM 文档索引：
   - 中文：`https://scriptingapp.github.io/zh/llms.txt`
   - 英文对照（中文缺页时）：`https://scriptingapp.github.io/llms.txt`
3. 在索引中搜索精确 API、入口或能力关键词。
4. 拉取对应 Markdown 页面；相对链接解析到 `https://scriptingapp.github.io/`（路径含空格时 URL 编码）。读完整文档和精确 API 声明，不要只看搜索摘要。
5. 核对：import/全局模块、参数、返回类型、async 行为、iOS/版本可用性、权限、宿主约束、示例模式。
6. 只实现当前文档已确认的 API；禁止从 Swift、React、旧示例或模型记忆推断。
7. 若有已连接的 `scripting-cli` 工作区，用其同步的 `.d.ts` 核对本地 TypeScript 签名/imports；类型以 `.d.ts` 为准，行为/权限/宿主约束仍以官方文档为准。

只读下方必要 topic reference。本地 reference 与当前官方文档冲突时，**官方文档优先**。优先读非 `Changelog/` 规范页；仅在确认版本新增、迁移或兼容性时读 Changelog。

## Start work

### New project

1. Identify the requested host: finite script, in-app page, resident/resumable script, Widget, Live Activity, rich notification, Intent, Safari project script, or installed userscript.
2. 用户自有、长期维护的 App（会进 My Scripting）复制 `templates/user-app/`，再按官方生命周期选 `index.tsx`。一次性脚本 / 官方示例只用 `templates/script.json` + 对应 `index-*.tsx`。
3. Add capability entry files **only** when requested.
4. Read `references/project-and-lifecycle.md`, then the matching capability reference.

## 用户新项目脚手架

对齐 GitHub Star Lists / Icon Library / AI Usage 的工程骨架。不要默认复制三 Tab、玻璃目录或 Widget。

新建用户 App 时：

1. 目录建在 `/var/minis/mounts/Scripting scripts/<Name>/`，`Name` = `script.json.name`（可空格）。
2. 复制 `templates/user-app/`：`script.json`、`changelog.ts`、`.gitignore`、`tsconfig.json`。
3. 按官方生命周期选 `index.tsx`（App 页通常从 `templates/index-page.tsx` 起步），再按需加入口文件。
4. `script.json`：改 name / icon / color / description；App 默认 `runInApp: true`；作者保持 `StarYunLee` + `https://github.com/StarYunLee`；版本默认 `0.1.0`。
5. `changelog.ts` 只保留 `version` / `date` / `changes`，首条版本必须等于 `script.json.version`。不要用 OutlookEmail 那种 `phase` / `validation` / `limitations`。
6. `git init`，分支 `main`，不要擅自加 remote。本地 commit 按 PROJECTS（阶段收口再提交）；push / release 必须当次授权，走 `scripting-widget-release`。
7. LICENSE / 仓库 README / 打包到发布时再补。
8. 宿主同步出的 `types/device/` 已在 `.gitignore`，不要提交。设置或关于页要有更新日志入口，但页面结构按项目写，不进模板。

### Existing project

1. Read `script.json`, `index.tsx`, the requested entry file, and its direct dependencies before modifying code.
2. Preserve the existing project naming, metadata, entry points, lifecycle, and user configuration unless the requested change requires otherwise.
3. Make the narrowest compatible change. Do not add unused capabilities or refactor unrelated files.

## Project rules

- A project requires `script.json` and `index.tsx`.
- `script.json` must include `name`, `icon`, `color`, and `version`; `name` normally matches the directory name.
- Keep shared business logic in regular modules; entry files should adapt that logic to their host environment.
- Use `async` / `await`, handle expected failure paths, and give the user meaningful feedback.
- For standalone `scripting-ts run` execution, make sure finite paths call `Script.exit()`; otherwise the process may wait indefinitely.
- TSX modifier order affects layout and appearance. When debugging UI, inspect the order of `frame`, `padding`, `background`, `clipShape`, `buttonStyle`, `contentMargins`, and `widgetBackground` as well as their values.
- Avoid unbounded vertical layouts inside `Grid` / `ScrollView`; validate image-heavy layouts on an actual render.

## Lifecycle decision

| Need | Design |
|---|---|
| Finite work is done | Call `Script.exit()`. |
| One-time page | `await Navigation.present(...)`, then `Script.exit()` after dismissal. |
| Preserve runtime state or respond to notification/widget/URL re-triggers | Use `Script.minimize()` and `Script.onResume(...)`; do not unconditionally exit. |
| Return from `intent.tsx` | Return an appropriate Intent result with `Script.exit(value)`. |

Read `references/project-and-lifecycle.md` before choosing or changing this behavior.

## Capability references

| User need | Read |
|---|---|
| Project structure, entry files, lifecycle | `references/project-and-lifecycle.md` |
| Standard in-app page | `references/ios-pages.md` |
| Static or interactive Widget / App Intent | `references/widgets-and-app-intents.md` |
| Live Activity / Dynamic Island | `references/live-activities.md` |
| Rich notification | `references/notifications-and-intents.md` |
| Shortcuts / Share Sheet | `references/notifications-and-intents.md` |
| Desktop editor ↔ Scripting App sync/debugging | `references/desktop-cli.md` |
| Native iOS API | `references/native-apis.md` plus official API page |
| Safari browser script / userscript | `references/safari-browser-scripts.md` |
| Keyboard, Home Screen UI, Spotlight, Translation UI, Assistant Tool, Alarm Live Activity | `references/additional-entry-points.md` plus exact official docs/API declaration |

## Validation requirements

Read `references/validation-and-security.md` and use the relevant checklist, including `checklists/desktop-live-debug.md` when setting up `scripting-cli`.

- For desktop live synchronization/debugging, read `references/desktop-cli.md`; initialize and run `scripting-cli` only after checking Node.js and confirming any first-time package download/configuration effects. After App connection, consult its synced `.d.ts` files whenever exact local API typings or component props are needed.
- Run static diagnostics for changed TypeScript/TSX where available.
- Run finite `index.tsx` code with `scripting-ts project "<name>"` or an equivalent environment command when possible.
- Preview Widget/UI surfaces when possible; test all target Widget families if layout differs by family.
- Be explicit about host-only verification: Widget must be added to the Home Screen; Intents require Shortcuts/Share Sheet; rich notifications require a real notification; Live Activities require the Lock Screen/Dynamic Island; Safari scripts require a matching Safari page.
- Never describe compilation, preview, `Widget.present()`, or a mock Intent as full system-host verification.

## Safety boundary

Before expanding privileges or causing external side effects, describe the impact and get the user's confirmation. This includes sensitive system permissions, reads/writes of user data, cross-origin requests/Cookies/downloads, sending or uploading data, and deleting or bulk-modifying data.

Never hard-code or expose API keys, passwords, tokens, Cookies, private keys, or private user data in source, `script.json`, logs, screenshots, or sample files. Apply minimum permissions and minimum data access.

## Completion response

只汇报关键结果（对用户用中文）：

1. 改动的文件与行为；
2. 生命周期选择（如相关）；
3. 已核对的官方文档主题 / API 符号；
4. 诊断、运行或预览证据；
5. 仍需在真机宿主上完成的验证步骤；
6. 引入的权限或副作用。
