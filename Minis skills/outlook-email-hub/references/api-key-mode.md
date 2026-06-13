# outlookEmail API Key 模式速查

## 认证

```http
X-API-Key: <OUTLOOK_EMAIL_API_KEY>
```

也支持 `?api_key=`，但 Skill 默认使用 Header，避免 Key 出现在 URL 日志里。

## GET /api/external/accounts

获取普通邮箱账号列表，不包含密码、Refresh Token、IMAP 密码。

常用参数：

- `group_id`
- `limit` 最大 10000
- `offset`
- `sort_by`: `created_at` / `email` / `sort_order`
- `sort_order`: `asc` / `desc`
- `tag_ids`
- `include_untagged`

返回账号字段重点：

- `id`
- `email`
- `aliases`
- `group_id`, `group_name`, `group_color`
- `remark`
- `status`
- `account_type`, `provider`
- `forward_enabled`
- `last_refresh_at`, `last_refresh_status`, `last_refresh_error`
- `tags`

## GET /api/external/emails

参数：

- `email` 必填，主邮箱或别名邮箱
- `folder`: `inbox` / `junkemail` / `deleteditems` / `all`
- `skip`
- `top` 默认 1，最大 50；`folder=all` 时每个文件夹各取 top
- `subject_contains`
- `from_contains`
- `keyword`

返回邮件字段：

- `id`
- `subject`
- `from`
- `date`
- `is_read`
- `has_attachments`
- `body_preview`
- `folder`

`folder=all` 会同时抓取 inbox 与 junkemail 并按时间倒序合并。
