---
name: surge-docs-helper
description: 优先从 Surge 官方知识库、官方手册与官方 community 中查找答案，处理 Surge 配置、模块、脚本、MitM、策略组、规则、DNS、面板、参数含义、功能说明、使用方法、报错排查等问题。适用于用户提到“Surge”“surge 配置”“surge 模块”“surge 脚本”“surge 手册”“surge 知识库”“surge community”“surge 怎么用”“surge 报错”“surge 参数”“surge 文档”等任意 Surge 相关场景。若官方来源没有答案，再回退到网络搜索。
---

处理 Surge 相关问题时：

1. 优先查询以下官方来源：
   - `https://kb.nssurge.com/surge-knowledge-base/`
   - `https://manual.nssurge.com/`
   - `https://community.nssurge.com/t/official`
2. 回答前，优先从官方知识库/手册提取相关内容；不要先凭印象作答。
3. 对于用户交流经验、排障案例、配置实战、边缘场景，可补充查询官方 community。
4. 官方页面正文提取优先使用 `web-content-extractor` 的链路（Defuddle / Jina Reader）或直接 `curl` 抓取页面，再做总结。
5. 如果用户问题偏“概念/参数/配置项/语法/模块能力/行为差异/官方限制”，优先查官方手册。
6. 如果用户问题偏“实战经验/常见问题/知识讲解/案例说明”，优先查官方知识库，再视情况查 community。
7. 如果官方来源查不到，或搜索结果明显不相关，再回退到联网搜索（优先官方域名结果，再看其他可信来源）。
8. 回答时尽量标注来源，至少给出引用到的官方页面链接。
9. 若问题涉及版本差异、不确定行为或近期变更，必须联网核验，不要猜测。
10. 输出优先简洁直接，先给结论，再给必要说明与来源。

推荐执行顺序：
- 先在官方站内搜索 / 页面检索
- 再读取命中的官方页面正文
- 再补充查 official community 讨论
- 最后必要时回退 `web-search` / `tavily-search`
