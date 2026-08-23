---
name: scripting-widget-release
description: >
  StarYunLee/Scripting 仓库的小组件发布、打包、展示图、上传前审查与 GitHub 发布门禁。
  当用户提到上传 GitHub、push Scripting、发布候选、打包 .scripting、展示图、预览图、
  代码审查清理、上传前检查、版本号更新、根 README、安装包验证，或处理 Codex Usage /
  Grok Usage / Claude Usage / Surge Metrics 的发布流程时使用。
  不替代 scripting-app-development（官方 API / 项目开发）。不自动 commit/push。
---

# Scripting Widget Release

用户自有仓库 `StarYunLee/Scripting` 的发布与工程约定。开发 Scripting API 仍走 `scripting-app-development`。

版本、路径、OAuth/数据源等易变事实：先读目标项目本地 `script.json` 与源码，再核对远程 `main`。不要背版本号或包哈希。PROJECTS 只记仓库/token/本地 Git 授权。

## 路由

| 用户在做什么 | 用哪个 skill |
|---|---|
| 写/改 Scripting API、页面、Widget、Intent | `scripting-app-development` |
| 审查、展示图、打包、发布候选、上传 GitHub | **本 skill** |
| 两边都有 | 先本 skill 的门禁，开发细节再加载官方 skill |

详细清单按需读取，不要一次全加载：

- 发布门禁与候选隔离 → `references/release-gate.md`
- 上传前检查 / 打包 / 远程回读 / Changelog 用户向文案 → `references/preflight.md`
- 展示图 → `references/preview-images.md`
- Usage / Metrics 已验证约定 → `references/widget-conventions.md`

## 硬规则

1. **禁止擅自 commit/push。** 当次对话必须有明确授权（「推到 Scripting」「上传 GitHub」「commit 并 push」）。准备候选可以做，暂存/提交/推送不行。
2. **唯一发布仓**：`https://github.com/StarYunLee/Scripting` 根目录。禁止再写入 `StarYunLee/Profiles/Scripting/`。
3. **认证**：`GITHUB_SCRIPTING_TOKEN`。不要用 `GITHUB_PROFILE_TOKEN` / `GITHUB_PROFILES_TOKEN`。
4. **一次只发一个项目**，禁止顺手改其他组件。必须同步更新仓库根 `README.md`。
5. **先同步最新 `main`**，在干净候选目录工作，不要直接在脏工作区打包。
6. **UI 未定型不要反复打包**；展示图未到位不要宣称“可上传”。
7. **只改 UI 时冻结** OAuth / Keychain / Storage / 请求 / 解析 / 缓存。发布前对这些文件做字节级对比。
8. **不要输出 Token、授权码、Cookie、完整 API 响应、HAR 明文。** 日志只保留状态码 / 类型 / 脱敏错误。
9. **真机宿主验证不能被 esbuild 或 Mock 替代。** 正式用量仍需有资格的真实账号。
10. **不要用 `Chart` / `AreaChart` / `LineChart`。** 真机会闪退，esbuild 查不出来。
11. Changelog 文案必须遵守 `references/preflight.md` 的用户向文案规范。
12. 版本号、SHA、提交哈希写日记忆即可，不要写进本 skill 或 GLOBAL。

## 发布流程（默认）

用户说「做上传前准备 / 审查 / 打包」但未授权 push 时，停在第 6 步。

1. 读 PROJECTS「Scripting」+ 目标项目 `script.json` / README / 入口文件。
2. `git fetch`，记录远程 `main` SHA。从该 SHA 建干净候选，再同步本次改动。
3. 需要改代码时：最小改动。布局扩展不要动稳定数据链路。
4. 需要展示图时：读 `references/preview-images.md`，等用户原始真机截图；不要用旧合成图二次放大。
5. 按 `references/preflight.md` 做构建、扫描、打包、三方一致校验。
6. 汇报：已完成、当前限制、是否可上传、**未** commit/push。等用户明确授权。
7. 授权后再 commit / push。消息格式：`feat|fix|chore: update <Name> to vX.Y.Z`。
8. 远程回读：源码版本、包内版本、ZIP、SHA、根 README。本地 HEAD 与 `origin/main` 一致后才算发布完成。

## 命名

| 类型 | 规则 | 例 |
|---|---|---|
| 源码目录 | 空格 | `Codex Usage/`、`Surge Metrics/` |
| 安装包 | 连字符 | `Codex-Usage.scripting`、`Surge-Metrics.scripting` |
| 作者 | `StarYunLee` | `author.homepage` = `https://github.com/StarYunLee`，禁止 `null` |
| 许可 | MIT | 项目与包内都要有 |

## 完成时只汇报

1. 改了哪些文件、版本是否变化；
2. 构建 / ZIP / 扫描证据；
3. 正式、候选、包是否一致；
4. staged / commit / push 状态（默认应为 0）；
5. 还缺什么（展示图、真机、用户授权）；
6. 不要把完整 SHA 当正文主角，需要时各留前 8 位。
