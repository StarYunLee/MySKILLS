---
name: outlook-email-hub
description: 使用 outlookEmail 服务的 API Key 模式自动搜索邮箱账号、复制邮箱、轮询邮件、提取验证码/验证链接。触发词：outlookEmail、Outlook 邮箱、搜索邮箱、复制邮箱、收验证码、等验证码、验证码来了没、读取邮箱邮件、邮箱账号池。当前默认使用 OUTLOOK_EMAIL_BASE_URL 和 OUTLOOK_EMAIL_API_KEY，仅调用 /api/external/accounts 与 /api/external/emails；分组创建/移动等管理功能需要后续 Session 模式。
---

# Outlook Email Hub

用于对接 `assast/outlookEmail` 的外部 API，高频完成：搜索账号 → 复制邮箱 → 等验证码 → 提取并复制验证码。

## 环境变量

必须存在：

- `OUTLOOK_EMAIL_BASE_URL`：服务基础地址，例如 `https://mail.example.com`
- `OUTLOOK_EMAIL_API_KEY`：Web 设置里的对外 API Key

不要输出 API Key。检查是否设置只能用：

```sh
[ -n "$OUTLOOK_EMAIL_API_KEY" ] && echo set || echo missing
```

## 默认工具

优先使用本 Skill 附带 CLI：

```sh
python3 /var/minis/skills/outlook-email-hub/scripts/outlook_email_cli.py <command>
```

常用命令：

```sh
# 验证连接，显示账号总数与前几条脱敏摘要
python3 /var/minis/skills/outlook-email-hub/scripts/outlook_email_cli.py ping

# 搜索账号：匹配 email、aliases、remark、group_name、tags、provider、status
python3 /var/minis/skills/outlook-email-hub/scripts/outlook_email_cli.py search <关键词>

# 搜索并复制唯一/最佳邮箱到剪贴板
python3 /var/minis/skills/outlook-email-hub/scripts/outlook_email_cli.py copy-email <关键词>

# 直接读取某邮箱最近邮件
python3 /var/minis/skills/outlook-email-hub/scripts/outlook_email_cli.py emails <email> --top 10 --folder all

# 搜索账号或直接用邮箱，等待验证码；默认复制邮箱和验证码
python3 /var/minis/skills/outlook-email-hub/scripts/outlook_email_cli.py wait-code <邮箱或关键词> --timeout 120 --interval 5

# 加来源/关键词过滤，减少误判
python3 /var/minis/skills/outlook-email-hub/scripts/outlook_email_cli.py wait-code <邮箱或关键词> --from github --keyword verify
```

## 使用原则

1. 用户说“等验证码/收验证码”：先判断输入是否邮箱；不是邮箱就 `search`。
2. 搜索结果唯一时直接使用；多个候选时展示前 10 条让用户选择，不要猜错账号。
3. 等验证码时默认：`folder=all`、`top=10`、`timeout=120`、`interval=5`。
4. 找到邮箱后默认复制邮箱到剪贴板；找到验证码后默认复制验证码到剪贴板。
5. 验证码从 `subject + body_preview + from` 中提取。优先含 code/验证码/verification/security 等上下文的 4-8 位数字，再考虑字母数字混合码。
6. API Key 模式只读外部接口，不能创建分组、移动分组、删除账号、改标签；遇到这类请求，说明需要 Session + CSRF 模式后续扩展。

## 外部 API

- `GET /api/external/accounts`：账号列表。支持 `group_id, limit, offset, sort_by, sort_order, tag_ids, include_untagged`。
- `GET /api/external/emails`：邮件列表。参数：`email` 必填；`folder` 可用 `inbox/junkemail/deleteditems/all`；`top` 最大 50；可加 `subject_contains/from_contains/keyword`。

## 回复格式

收验证码成功时简洁返回：

```text
已找到邮箱：xxx@outlook.com（已复制）
收到验证码：123456（已复制）
来源：no-reply@example.com / 主题 xxx
```

如果超时：返回已检查的邮箱、过滤条件、最后看到的 3 封邮件摘要，建议用户放宽关键词或重试。
