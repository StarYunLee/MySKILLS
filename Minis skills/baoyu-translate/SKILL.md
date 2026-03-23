---
name: baoyu-translate
description: 在 Minis 中进行文章与文档翻译的技能，支持 quick / normal / refined 三种模式。适用于用户提到“翻译”“精翻”“快翻”“翻译文章”“翻译成中文/英文”“本地化”“润色翻译”“继续润色”等场景，也适用于给出 URL、Markdown、文本文件后要求翻译。已适配 Minis 环境：优先使用 Node/npx 执行本地分块脚本；若运行环境缺少 bun，则不依赖 bun 直接用 Node 版本脚本处理分块。
---

# baoyu-translate for Minis

该 skill 来源于 `JimLiu/baoyu-skills` 的 `baoyu-translate`，已按 Minis 环境做兼容适配。

## Minis 适配结论

- 原版 **不能直接无缝使用**，因为原说明优先依赖 `bun` / `npx bun`，且包含 OpenClaw / AskUserQuestion / subagent 约定。
- 在 Minis 中可以**适配后使用**。
- 当前适配策略：
  1. 保留原参考文档与术语表；
  2. 将“分块”能力改为优先走 Node 版脚本；
  3. 翻译流程由 Minis 主代理执行，不依赖 OpenClaw 专属能力；
  4. 若用户未配置 EXTEND.md，可直接询问并按需创建。

## 推荐执行方式

### 1. 分块命令
优先使用：

```bash
node /var/minis/skills/baoyu-translate/scripts/main.mjs <file> [--max-words 5000] [--output-dir <dir>]
```

或：

```bash
node /var/minis/skills/baoyu-translate/scripts/main.mjs chunk <file> [--max-words 5000] [--output-dir <dir>]
```

### 2. 翻译工作流
在 Minis 中按以下逻辑执行：

1. 检查是否存在 EXTEND.md 偏好文件；
2. 若不存在，向用户一次性收集：目标语言、模式、受众、风格、保存位置；
3. 短文：直接翻译；
4. 长文：先用本地脚本分块，再逐块翻译并合并；
5. normal 模式：分析 → 翻译；
6. refined 模式：分析 → 翻译 → 审校 → 润色；
7. 保留 Markdown 结构、代码块、链接、图片引用；
8. 若用户说“继续润色”，在现有译稿基础上继续 refined 后半流程。

## 兼容性说明

- 原版依赖：`bun` / `npx -y bun`
- Minis 适配后：主要依赖 `node`
- 如后续安装了 `bun`，也可继续兼容原版脚本，但不是必须。

## 建议

- 若只是普通翻译请求，直接由 Minis 按此 skill 工作流执行即可；
- 若需要长文稳定分块，使用本地 `main.mjs`；
- 若需要持久化偏好，可创建：
  - `.baoyu-skills/baoyu-translate/EXTEND.md`
  - 或 `$HOME/.baoyu-skills/baoyu-translate/EXTEND.md`
