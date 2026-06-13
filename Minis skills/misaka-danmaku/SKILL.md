---
name: misaka-danmaku
version: 1.0.0
description: >-
  Misaka Danmaku 弹幕系统外部控制 API 技能。通过 CLI 客户端操作弹幕库：搜索、导入、下载弹幕、刷新弹幕、管理 Token、任务控制、配置修改、剧集组、弹幕源设置、日志查看等。
  当用户提到"弹幕"、"danmaku"、"misaka"、"danmu.630226.xyz"、"弹幕系统"、"下载弹幕"、"刷新弹幕"、"导入弹幕"、"弹幕库"、"弹幕源"时触发。
---

# Misaka Danmaku 控制 API

## 环境变量（必需）

| 变量 | 说明 |
|---|---|
| `MISAKA_DANMAKU_BASE_URL` | API 地址，不带尾部 `/`，例 `https://danmu.630226.xyz` |
| `MISAKA_DANMAKU_API_KEY` | 通过 `X-API-KEY` 请求头传递 |

检查：`[ -n "$MISAKA_DANMAKU_BASE_URL" ] && [ -n "$MISAKA_DANMAKU_API_KEY" ] && echo ok || echo missing`

缺失时提供创建链接：
- [设置 MISAKA_DANMAKU_BASE_URL](minis://settings/environments?create_key=MISAKA_DANMAKU_BASE_URL&create_value=https%3A%2F%2Fdanmu.630226.xyz&create_note=Misaka%20Danmaku%20API%20Base%20URL)
- [设置 MISAKA_DANMAKU_API_KEY](minis://settings/environments?create_key=MISAKA_DANMAKU_API_KEY&create_value=&create_note=Misaka%20Danmaku%20%E5%A4%96%E9%83%A8%E6%8E%A7%E5%88%B6%20API%20Key)

## CLI 客户端

路径：`/var/minis/skills/misaka-danmaku/misaka.py`（纯标准库，python3 直接跑）

运行方式：
```sh
python3 /var/minis/skills/misaka-danmaku/misaka.py <子命令> [参数]
```

⚠️ Cloudflare 会拦 Python 默认 UA（Error 1010），脚本已内置浏览器 UA，无需额外处理。

## 子命令速查

### 媒体库
| 命令 | 说明 |
|---|---|
| `library` | 列出全部作品 |
| `search-lib <keyword>` | 库内搜索 |
| `anime <animeId>` | 作品详情 |
| `anime-update <animeId> --file <json>` | 编辑作品信息 |
| `anime-delete <animeId>` | 删除作品（后台任务） |
| `anime-create --file <json>` | 自定义创建条目 |
| `sources <animeId>` | 作品的所有数据源 |
| `source-add <animeId> --provider <name> --media-id <id>` | 为作品添加源 |
| `source-delete <sourceId>` | 删除数据源 |
| `source-favorite <sourceId>` | 切换精确标记 |
| `source-episodes <sourceId>` | 某个源的分集列表 |
| `episode-update <episodeId> --title <t> --index <n>` | 编辑分集 |
| `episode-delete <episodeId>` | 删除分集 |

### 弹幕
| 命令 | 说明 |
|---|---|
| `danmaku <episodeId> [-o file] [--xml]` | 下载弹幕（JSON 或 dandanplay XML） |
| `danmaku-batch <animeId> [--xml --favorited-only --force]` | 批量下载整部作品 |
| `danmaku-overwrite <episodeId> --file <json>` | 覆盖弹幕 |
| `refresh-ep <episodeId> [--wait]` | 刷新单集 |
| `refresh-anime <animeId> [--source-id N --favorited-only]` | 批量刷新整部 |

### 搜索 & 导入
| 命令 | 说明 |
|---|---|
| `search <keyword> [--season --episode]` | 搜索外部弹幕源 |
| `search-episodes --search-id <id> --index <n>` | 获取搜索结果分集列表 |
| `import-auto -t <type> -q <term> [-s -e -m] [--wait]` | 全自动导入 |
| `import-direct --search-id <id> --index <n> [--tmdb-id ...]` | 直接导入搜索结果 |
| `import-edited --search-id <id> --index <n> --file <json>` | 导入编辑后的分集 |
| `import-url --source-id --episode-index --url [--wait]` | URL 导入单集 |
| `import-xml --source-id --episode-index --file [--wait]` | XML 导入单集 |
| `metadata-search --provider <tmdb\|bangumi> [--keyword\|--id] [--media-type]` | 查元数据 |

### Token 管理
| 命令 | 说明 |
|---|---|
| `tokens` | 列出所有 Token |
| `token <tokenId>` | Token 详情 |
| `token-create --name <n> [--validity --daily-limit --custom-token]` | 创建 |
| `token-update <tokenId> --name <n> --daily-limit <n> [--validity]` | 更新 |
| `token-delete <tokenId>` | 删除 |
| `token-toggle <tokenId>` | 启用/禁用 |
| `token-reset <tokenId>` | 重置今日调用次数 |
| `token-logs <tokenId>` | 访问日志 |

### 任务控制
| 命令 | 说明 |
|---|---|
| `tasks [--search --status]` | 任务列表 |
| `task <taskId>` | 任务详情 |
| `task-delete <taskId> [--force]` | 删除任务 |
| `task-abort <taskId> [--force]` | 中止任务 |
| `task-pause <taskId>` | 暂停 |
| `task-resume <taskId>` | 恢复 |
| `task-execution <taskId>` | 查调度任务触发的执行任务 |

### 定时任务
| 命令 | 说明 |
|---|---|
| `scheduler-tasks` | 所有定时任务 |
| `scheduler-last <taskId>` | 最近一次运行结果 |

### 设置 & 配置
| 命令 | 说明 |
|---|---|
| `danmaku-output` | 弹幕输出设置 |
| `danmaku-output-update --limit <n> --merge <bool>` | 更新输出设置 |
| `config [--type help]` | 查看配置 |
| `config-update --key <k> --value <v>` | 更新配置项 |
| `rate-limit` | 流控状态 |

### 剧集组
| 命令 | 说明 |
|---|---|
| `episode-groups [--tmdb-tv-id]` | 列表 |
| `episode-group <groupId>` | 详情 |
| `episode-group-create --tmdb-tv-id <id> [--group-id --name] --file <json>` | 创建 |
| `episode-group-update <groupId> --file <json>` | 编辑 |
| `episode-group-delete <groupId>` | 删除 |
| `episode-group-associate <groupId> --anime-id <id>` | 关联条目 |
| `episode-group-disassociate <groupId> --anime-id <id>` | 解关联 |

### 弹幕源
| 命令 | 说明 |
|---|---|
| `scrapers` | 所有源配置 |
| `scraper-update <provider> [--use-proxy --blacklist --log-raw --timeout]` | 更新源配置 |

### 日志
| 命令 | 说明 |
|---|---|
| `logs` | 实时日志 |
| `log-files` | 历史日志文件列表 |
| `log-file <filename> [--tail 500]` | 读取指定日志文件 |

## 常见工作流

### 下载某部剧全部弹幕（XML 格式）
```sh
# 1. 搜库找到 animeId
python3 misaka.py search-lib "主角"
# 2. 批量下载
python3 misaka.py danmaku-batch 118 --xml --favorited-only
```

### 全自动导入新作品
```sh
# 按关键词
python3 misaka.py import-auto -t keyword -q "斗破苍穹" -m tv_series -s 5 --wait
# 按 TMDB ID
python3 misaka.py import-auto -t tmdb -q 12345 -s 1 --wait
```

### 刷新整部作品弹幕
```sh
python3 misaka.py refresh-anime 118 --favorited-only
```

### 查看流控余量
```sh
python3 misaka.py rate-limit
```

## 关键约束

- **全局流控**：100 次/小时，批量操作注意 `--sleep` 参数
- **任务异步**：导入/刷新/删除返回 taskId，用 `--wait` 自动轮询或手动 `task <id>` 查看
- **dandanplay XML**：`--xml` 输出兼容 dandanplay 格式，p 字段转换为 `time,mode,fontsize,color,timestamp,pool,user,rowid`
