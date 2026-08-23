# 发布门禁与候选隔离

## 何时可以碰远程

仅当用户在**当次对话**明确说：推到 Scripting / 上传 GitHub / commit 并 push / 发布到仓库。

以下句子**不够**：

- 「做上传前准备」
- 「审查一下能不能上传」
- 「打包验证」
- 「更新展示图」
- 上一轮对话曾经授权过

准备阶段默认：`staged=0`，不 `git add`，不 `commit`，不 `push`。

## 候选目录

不要在脏的本地 clone 或挂载项目里直接当发布产物。

1. `git fetch origin`
2. 记录 `origin/main` SHA，确认没有别人未合并的提交
3. 以该 SHA 建干净候选，例如 `/var/minis/workspace/Scripting-<project>-release`
4. 只同步**当前项目**目录、对应 `.scripting` 包、以及仓库根 `README.md`
5. 打包与哈希都以候选为准，再回写正式挂载项目（如需要）

本地开发源：`/var/minis/mounts/Scripting scripts/<Name>/`  
发布仓工作副本：按当次任务新建或复用 workspace 候选，用完可留作核对，不要把它当成第二个长期源码仓。

## 认证

Push 使用环境变量 `GITHUB_SCRIPTING_TOKEN`。

- 检查是否存在：`[ -n "$GITHUB_SCRIPTING_TOKEN" ] && echo set || echo missing`
- 禁止 `echo` / `printenv` 输出值
- 非交互 push 可用临时 `GIT_ASKPASS`；用完删除助手脚本
- 不要把 token 写入 git config、remote URL 或候选目录

若变量未设置，给用户环境变量设置链接，不要改用 Profiles token。

## 一次一个项目

- diff 只应包含：目标源码目录、对应 `.scripting`、根 README
- 发现其他项目文件被改：停下来，不要一起提交
- 版本只升当前项目的 `script.json` / README；根 README 只改对应条目

## 版本

- 问用户或根据改动幅度建议：修缺陷 / 文案 → patch；布局或数据模型变化 → minor
- 源码 `script.json`、项目 README、包内 `script.json` 必须同一版本
- 客户端标识（如 Grok `x-grok-client-version`）与组件版本对齐
- 不要为了“看起来正式”跳大版本

## README

项目 README 固定结构：

功能 → 系统要求 → 安装 → OAuth/配置 → 多账号 → 显示与设置 → 数据来源 → 隐私安全 → 已知限制 → 项目结构 → 免责声明

根 README 每次发布都核对：简介、源码链接、直接安装、Raw 地址、Issue 标签、免责声明。
