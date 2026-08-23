# 上传前检查与打包

在用户授权 push 之前跑完。UI 还在改像素时不要整套重跑打包。

## 1. 构建

Usage / Metrics 这类三入口项目：

```sh
npx --yes esbuild index.tsx widget.tsx app_intents.tsx \
  --bundle --platform=neutral --format=esm --external:scripting \
  --outdir=/tmp/scripting-build
```

少一个入口就少编一个。正式源码、候选、解包后的包内源码都要过。

## 2. 元数据

```sh
python3 -m json.tool script.json >/dev/null
```

核对：

- `name` 与目录名一致
- `version` 与 README / 包内一致
- `author.name` = `StarYunLee`
- `author.homepage` = `https://github.com/StarYunLee`（禁止 `null`）
- 无模板残留、无调试入口、无 `.learnings`

## 3. Changelog 用户向文案

`changelog.ts` 默认保持 `version / date / changes` 简单结构；除非产品展示明确需要，不额外引入技术分类字段。

- 每个版本写 1–4 条。
- 每条建议约 20–60 个汉字，以一个完整句子为宜；复杂事项可适当放宽，但通常不超过 80 个汉字。
- 顺序：新增功能 → 问题修复 → 体验优化。
- 描述用户可感知的结果，不描述代码实现过程。
- 不出现接口字段、Header、User-Agent、HTTP 状态码、客户端指纹或内部模块名。
- 保留必要的平台名、功能名、额度周期和小组件尺寸等用户可理解信息。
- 历史版本按当时实际功能描述，不用后续新增能力反写历史。

## 4. 扫描

至少查：

- Token / 授权码 / Cookie / 私钥字面量
- 完整 HAR、调试日志、本机路径、临时截图
- 未引用导出、死字段、过期文案（旧布局名、已删除指标）
- 「发布前删除 Mock」不再作为硬条件；若保留 Mock，必须只读且隔离（见 `widget-conventions.md`）

## 5. 打包

`.scripting` 是 ZIP，**文件在压缩包根目录**，不要套一层文件夹。

```sh
cd "<project-dir>"
zip -X -r "../<Name-With-Hyphens>.scripting" . \
  -x "*.DS_Store" -x "**/.git*" -x "**/.learnings/**" -x "**/node_modules/**"
unzip -t "../<Name-With-Hyphens>.scripting"
```

记录大小与 SHA-256，但回复里只报前 8 位，除非用户要完整值。

发布目录只留：源码、成品资源、README、LICENSE、安装包。源截图、合成中间图、诊断脚本不要进仓。

## 6. 三方一致

逐文件对比：

1. 正式挂载项目
2. 候选目录
3. 解包后的 `.scripting`

不一致就重打包，不要“先推再补”。

## 7. 远程回读（仅 push 后）

- 源码 `script.json` 版本
- 包内 `script.json` 版本
- Raw 安装包 HTTP 200，`unzip -t` 通过
- 远程与本地包 SHA 一致
- 根 README 对应条目已更新
- `git status` 干净，`HEAD == origin/main`

## 失败怎么报

已完成 / 当前限制 / 可能原因 / 下一步。不要假装已发布。
