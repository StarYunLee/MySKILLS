---
name: icon-library-finder
description: 从一个或多个 Surge/Loon/QuanX 图标库 JSON 中按名称查找图标，并返回清洗后的可点击图片链接。适用于用户提到“查图标”“找图标”“搜图标”“图标库”“icon library”“icon json”“Surge 图标”“Loon 图标”“QuanX 图标”“添加图标库”等场景。支持多个图标库、重名图标全部返回、中文意图辅助匹配、后续追加新图标库链接。
---

在处理图标查找任务时：

1. 优先使用本 skill 的 `assets/sources.json` 作为默认图标库来源。
2. 用 `scripts/search_icons.py` 搜索图标名；支持大小写不敏感、去除多余转义斜杠、模糊匹配、返回全部同名/近似结果。
3. 当用户用中文描述图标时，不要机械按中文原词直查；先根据语义推断可能的英文名、拼音、常见缩写、品牌/应用英文名，再进行搜索。
4. 输出时优先给用户可点击 Markdown 链接，格式为：`[查看图片](https://...)`。
5. 如果存在 `名称`、`名称(1)`、`名称(2)` 等同名变体，全部列出，不要只返回一个。
6. 当用户要求“添加图标库”时，更新 `assets/sources.json`，把新链接持久化保存。
7. 若用户没有明确给出图标库，则默认查询全部已登记图标库。
8. 若图标库 JSON 拉取失败，明确指出失败的源，并继续查其他源。
9. 输出尽量简洁：图标名 + 来源库 + 可点击链接；必要时附少量候选项，方便用户点开确认。

建议调用方式：
- 查找：`python3 /var/minis/skills/icon-library-finder/scripts/search_icons.py search "关键词"`
- 简洁输出：`python3 /var/minis/skills/icon-library-finder/scripts/search_icons.py simple "关键词"`
- 添加源：先编辑 `assets/sources.json`
- 列出源：`python3 /var/minis/skills/icon-library-finder/scripts/search_icons.py sources`
