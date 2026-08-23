# Shortcuts Playground Minis

Minis 本地化 Apple Shortcuts 生成 skill。用途是把自然语言自动化需求转成可交付的快捷指令产物，包括：路线判断、动作链规划、unsigned XML 草稿、本地验证后的 XML，以及按需签名后的 `.shortcut` 成品。

本目录基于上游 `viticci/shortcuts-playground-plugin` 的知识库与方法进行本地化适配，不是与上游无关的全新原创项目。上游来源、许可与本地化边界见 [UPSTREAM_ATTRIBUTION.md](UPSTREAM_ATTRIBUTION.md)；合规使用与再分发要求见 [LICENSE_COMPLIANCE.md](LICENSE_COMPLIANCE.md)。

## 定位

本 skill 处理三类任务：

- **shortcut-native**：可主要依赖系统原生动作完成
- **shortcut-hybrid**：快捷指令负责入口，复杂部分交给 URI、第三方动作、Minis 或外部服务
- **not-shortcut-first**：不适合优先做成快捷指令，应先改走 Minis 直接执行或其他实现路径

本 skill 的目标不是围绕单个案例堆示例，而是提供一套可复用的构建框架。

## 文档使用顺序

1. [SKILL.md](SKILL.md) — 权威工作流与执行规则
2. [BUILD_CHECKLIST.md](BUILD_CHECKLIST.md) — 构建前检查
3. [CAPABILITY_DECISION.md](CAPABILITY_DECISION.md) — 路线判定
4. [ROUTING_FRAMEWORK.md](ROUTING_FRAMEWORK.md) — 任务规格与路由规则
5. [CLARIFICATION_TEMPLATES.md](CLARIFICATION_TEMPLATES.md) — 需求不清时的固定提问模板
6. [ENV_PROFILE.md](ENV_PROFILE.md) — 环境画像字段说明
7. [TASK_FAMILY_INDEX.md](TASK_FAMILY_INDEX.md) — 高层任务家族索引
8. [COMMON_PATTERNS.md](COMMON_PATTERNS.md) — 通用模式分类
9. [ACTION_RECIPES.md](ACTION_RECIPES.md) — 高频动作链骨架
10. [TEMPLATE_MAPPING.md](TEMPLATE_MAPPING.md) — 需求到模板的映射规则
11. [XML_SNIPPET_PATTERNS.md](XML_SNIPPET_PATTERNS.md) — 高频动作最小 XML 片段索引
12. [STABILITY_NOTES.md](STABILITY_NOTES.md) — 稳定性与可复现性注意事项
13. [BEST_PRACTICES.md](BEST_PRACTICES.md) 及技术参考文档 — 具体动作、参数、变量、过滤器和格式细节

## 核心命令

```bash
/var/minis/skills/shortcuts-playground-minis/scripts/check-local-assets
/var/minis/skills/shortcuts-playground-minis/scripts/profile-summary
/var/minis/skills/shortcuts-playground-minis/scripts/load-env-profile
/var/minis/skills/shortcuts-playground-minis/scripts/preflight-request '我要做一个快捷指令'
/var/minis/skills/shortcuts-playground-minis/scripts/render-clarification '我要做一个快捷指令'
/var/minis/skills/shortcuts-playground-minis/scripts/resolve-icon --prompt "Build a weather shortcut"
/var/minis/skills/shortcuts-playground-minis/scripts/placeholder-range 'text with ￼ placeholder'
/var/minis/skills/shortcuts-playground-minis/scripts/validate-shortcut /path/to/Shortcut.xml
/var/minis/skills/shortcuts-playground-minis/scripts/sign-shortcut-via-mac /path/to/Shortcut.xml --name "Shortcut Name" --host "user@MacBook-Pro.local"
/var/minis/skills/shortcuts-playground-minis/scripts/sign-shortcut /path/to/Shortcut.xml --name "Shortcut Name"
python3 /var/minis/skills/shortcuts-playground-minis/scripts/selftest_minis.py
```

## 输出目录

- 成品：`/var/minis/attachments/shortcut/`
- 草稿：`/var/minis/attachments/shortcut/drafts/`
- 归档：`/var/minis/attachments/shortcut/archive/YYYY-MM-DD/`

`scripts/sign-shortcut-via-mac` 通过 SSH/SCP 调用你自己 Mac 上的 Apple 官方 `shortcuts sign`，这是有 Mac 时的推荐签名方式；草稿不会上传到第三方签名服务。

`scripts/sign-shortcut` 调用 HubSign 在线签名服务；签名不是纯本地离线过程。仅在用户明确同意且草稿不含敏感内容时使用。

## 文件分组

### 框架层

- `SKILL.md`
- `BUILD_CHECKLIST.md`
- `CAPABILITY_DECISION.md`
- `ROUTING_FRAMEWORK.md`
- `CLARIFICATION_TEMPLATES.md`
- `COMMON_PATTERNS.md`
- `ACTION_RECIPES.md`
- `TEMPLATE_MAPPING.md`
- `TASK_FAMILY_INDEX.md`
- `XML_SNIPPET_PATTERNS.md`
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

- `scripts/select_shortcut_icon_color.py`
- `scripts/validate_shortcut.py`
- `scripts/sign_shortcut_via_mac.py`
- `scripts/sign_shortcut_via_hubsign.py`
- `scripts/placeholder_range.py`
- `scripts/load_env_profile.py`
- `scripts/check_local_assets.py`
- `scripts/selftest_minis.py`

### 合规层

- `LICENSE`
- `UPSTREAM_ATTRIBUTION.md`
- `LICENSE_COMPLIANCE.md`
- `NOTICE`
- `REDISTRIBUTION_CHECKLIST.md`

## 运行要求

- Python 3.10+
- Minis 运行环境
- 若执行签名，需可访问 HubSign

## 合规要求

MIT 允许本地使用、修改、迁移与再分发，但必须保留：

- 上游版权声明
- MIT 许可文本
- 来源归因
- 本地化修改边界说明

不要将本目录表述为上游官方版本，也不要暗示原作者或 MacStories 为本地版本背书。
