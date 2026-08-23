# License & Compliance Notes

## 结论

当前 `shortcuts-playground-minis` 可以在 **MIT 协议**下合规本地化、修改、使用、再分发，但必须保留：

1. 上游版权声明
2. MIT 许可文本
3. 来源归因
4. 本地化修改说明

只要做到这些，就不会因为本地化本身侵犯上游仓库的许可权益。

## 上游来源

- Upstream: `viticci/shortcuts-playground-plugin`
- URL: <https://github.com/viticci/shortcuts-playground-plugin>
- Author: Federico Viticci / MacStories
- License: MIT
- SPDX: `MIT`

## MIT 协议对本地化意味着什么

MIT 允许：

- 使用
- 复制
- 修改
- 合并
- 分发
- 再授权
- 商业使用

前提是：

- **所有副本或重要部分都要保留版权声明与许可文本**

这意味着本地 skill 可以：

- 复制上游知识库文件
- 改写 `SKILL.md`
- 新增脚本与包装层
- 修改输出目录、工作流与本地说明
- 在 Minis 场景下继续演进

但不能：

- 删除上游版权与 MIT 文本后再重新发布
- 把大量继承自上游的方法和资料表述为“完全原创”
- 在分享时隐去关键来源，造成来源误导

## 当前本地 skill 应保留的合规文件

以下文件应视为合规最小集合，不建议删除：

- `LICENSE`
- `UPSTREAM_ATTRIBUTION.md`
- `LICENSE_COMPLIANCE.md`（本文件）
- `README.md` 中对上游来源与本地化边界的说明
- `SKILL.md` 中对上游方法借鉴的说明

## 本地化修改的合规表达方式

推荐使用这种表述：

- “基于 `viticci/shortcuts-playground-plugin` 本地化适配”
- “借鉴上游知识库、方法与验证流程，并针对 Minis 进行了运行环境改造”
- “本目录为 Minis 场景下的适配层与扩展层，不是完全从零原创”

不推荐：

- “这是我独立原创的快捷指令生成框架”
- “与上游项目无关，只是参考了一点思路”

## 分发与共享时的最低要求

如果以后把这个 skill 分享给别人、迁移到别的设备、打包给其他用户，至少应满足：

1. 保留 `LICENSE`
2. 保留 `UPSTREAM_ATTRIBUTION.md`
3. 在 `README.md` 或说明文档里明确写出上游仓库地址
4. 说明哪些部分是本地化修改
5. 不删除原作者署名
6. 不把本地 skill 表述为上游官方版本、原作者授权版本或 MacStories 背书版本

## 哪些部分更像“上游继承”

以下内容明显属于上游方法或资料延续，应继续归因：

- Shortcuts 参考知识库主体
- Craig Loop 验证思路
- unsigned XML 作为 source of truth 的工作模式
- draft / archive / signed artifact 分离交付思路
- action / parameter / golden example 的整体知识体系

## 哪些部分更像“本地新增”

以下内容主要属于本地适配与扩展，可作为本地贡献明确写出：

- Minis 路径结构与结果目录约定
- HubSign 包装层
- 本地 self-test
- 通用路由框架、模式框架、能力决策框架、环境画像框架
- 固定澄清模板、推荐流程、可复制确认文本
- iPhone / iPad 场景下的交付与使用方式

## 实操建议

后续继续完善 skill 时，优先做这几件事以保持合规：

- 所有新增框架文件继续保留上游借鉴说明，不必每个文件都写一遍，但入口文件和归因文件必须明确
- 若将来删除或大幅改写上游文件，仍要保留 `LICENSE` 和 `UPSTREAM_ATTRIBUTION.md`
- 若新增 `NOTICE.md`，可把“上游 + 本地新增边界”压缩成一页摘要，便于分享
- 若以后形成独立公开仓库，README 首页第一屏就应明确“fork / adaptation / based on”关系

## 当前判断

当前本地化方向**可以合规继续推进**。

需要继续加强的不是许可证本身，而是：

- 更清楚地区分“上游继承内容”和“本地新增内容”
- 让 README / SKILL / 归因文件之间的说法更一致
- 避免在后续优化中无意把来源信息删掉
