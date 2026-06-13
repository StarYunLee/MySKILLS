#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE_URL = os.environ.get('OUTLOOK_EMAIL_BASE_URL', '').strip().rstrip('/')
API_KEY = os.environ.get('OUTLOOK_EMAIL_API_KEY', '').strip()
EMAIL_RE = re.compile(r'^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$')
CODE_CONTEXT_RE = re.compile(r'(验证码|校验码|动态码|安全代码|安全码|verification|verify|code|security|otp|one[- ]?time|passcode)', re.I)
NUM_CODE_RE = re.compile(r'(?<!\d)(\d{4,8})(?!\d)')
MIXED_CODE_RE = re.compile(r'(?<![A-Za-z0-9])([A-Z0-9]{5,10})(?![A-Za-z0-9])')
URL_RE = re.compile(r'https?://[^\s"\'<>）)]+')

class OutlookEmailError(Exception):
    pass

def die(msg, code=1):
    print(msg, file=sys.stderr)
    sys.exit(code)

def require_env():
    if not BASE_URL:
        die('缺少环境变量 OUTLOOK_EMAIL_BASE_URL')
    if not API_KEY:
        die('缺少环境变量 OUTLOOK_EMAIL_API_KEY')

def api_get(path, params=None, timeout=30):
    require_env()
    url = BASE_URL + path
    if params:
        clean = {k: v for k, v in params.items() if v is not None and v != ''}
        if clean:
            url += '?' + urlencode(clean)
    req = Request(url, headers={
        'X-API-Key': API_KEY,
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    })
    try:
        with urlopen(req, timeout=timeout) as r:
            raw = r.read().decode('utf-8', 'replace')
    except HTTPError as e:
        body = e.read().decode('utf-8', 'replace')[:500]
        raise OutlookEmailError(f'HTTP {e.code}: {body}')
    except URLError as e:
        raise OutlookEmailError(f'网络错误: {e.reason}')
    try:
        data = json.loads(raw)
    except Exception:
        raise OutlookEmailError('响应不是 JSON: ' + raw[:300])
    if isinstance(data, dict) and data.get('success') is False:
        raise OutlookEmailError(str(data.get('error') or data.get('message') or data))
    return data

def copy_text(text):
    try:
        subprocess.run(['apple-clipboard', 'set', text], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def load_accounts(limit=10000, group_id=None):
    params = {'limit': limit, 'offset': 0, 'sort_by': 'created_at', 'sort_order': 'desc'}
    if group_id is not None:
        params['group_id'] = group_id
    data = api_get('/api/external/accounts', params)
    return data.get('accounts') or [], data

def account_text(acc):
    parts = []
    for key in ['email', 'remark', 'group_name', 'status', 'provider', 'account_type']:
        v = acc.get(key)
        if v:
            parts.append(str(v))
    for a in acc.get('aliases') or []:
        parts.append(str(a))
    for t in acc.get('tags') or []:
        if isinstance(t, dict):
            parts.append(str(t.get('name') or ''))
        else:
            parts.append(str(t))
    return ' '.join(parts).lower()

def score_account(acc, terms):
    email = (acc.get('email') or '').lower()
    aliases = [str(x).lower() for x in (acc.get('aliases') or [])]
    text = account_text(acc)
    score = 0
    for term in terms:
        t = term.lower()
        if email == t:
            score += 100
        elif any(a == t for a in aliases):
            score += 95
        elif email.startswith(t):
            score += 70
        elif t in email:
            score += 50
        elif any(t in a for a in aliases):
            score += 45
        elif t in text:
            score += 20
        else:
            return -1
    if acc.get('status') == 'active':
        score += 3
    if acc.get('last_refresh_status') == 'success':
        score += 2
    return score

def search_accounts(query, limit=20, group_id=None):
    accounts, _ = load_accounts(group_id=group_id)
    terms = [x for x in re.split(r'\s+', query.strip()) if x]
    if not terms:
        return []
    hits = []
    for acc in accounts:
        sc = score_account(acc, terms)
        if sc >= 0:
            hits.append((sc, acc))
    hits.sort(key=lambda x: (x[0], str(x[1].get('created_at') or '')), reverse=True)
    return [a for _, a in hits[:limit]]

def fmt_account(acc, idx=None):
    p = '' if idx is None else f'{idx}. '
    tags = ','.join([str(t.get('name')) for t in (acc.get('tags') or []) if isinstance(t, dict) and t.get('name')])
    alias = ', '.join(acc.get('aliases') or [])
    extra = []
    if acc.get('group_name'): extra.append(f"分组:{acc.get('group_name')}")
    if acc.get('remark'): extra.append(f"备注:{acc.get('remark')}")
    if tags: extra.append(f"标签:{tags}")
    if acc.get('last_refresh_status'): extra.append(f"刷新:{acc.get('last_refresh_status')}")
    if alias: extra.append(f"别名:{alias}")
    return p + f"[{acc.get('id')}] {acc.get('email')}" + (" | " + ' | '.join(extra) if extra else '')

def resolve_email(value, allow_ambiguous=False):
    v = value.strip()
    if EMAIL_RE.match(v):
        return v, None, []
    hits = search_accounts(v, limit=10)
    if not hits:
        raise OutlookEmailError(f'未找到账号: {v}')
    if len(hits) > 1 and not allow_ambiguous:
        lines = ['匹配到多个账号，请换更精确关键词或直接传邮箱：']
        lines += [fmt_account(a, i+1) for i, a in enumerate(hits)]
        raise OutlookEmailError('\n'.join(lines))
    return hits[0].get('email'), hits[0], hits

def get_emails(email, folder='all', top=10, subject=None, from_contains=None, keyword=None):
    params = {'email': email, 'folder': folder, 'top': top}
    if subject: params['subject_contains'] = subject
    if from_contains: params['from_contains'] = from_contains
    if keyword: params['keyword'] = keyword
    data = api_get('/api/external/emails', params, timeout=45)
    return data.get('emails') or [], data

def email_key(m):
    return str(m.get('id') or '') + '|' + str(m.get('date') or '') + '|' + str(m.get('subject') or '')

def extract_code(text):
    if not text:
        return None
    # Prefer numbers close to code context
    for m in NUM_CODE_RE.finditer(text):
        s, e = m.span(1)
        window = text[max(0, s-50):min(len(text), e+50)]
        if CODE_CONTEXT_RE.search(window):
            return m.group(1)
    nums = NUM_CODE_RE.findall(text)
    if nums:
        # Prefer 6 digits, then other lengths
        nums.sort(key=lambda x: (len(x) != 6, len(x) != 4, -len(x)))
        return nums[0]
    for m in MIXED_CODE_RE.finditer(text.upper()):
        code = m.group(1)
        if any(c.isdigit() for c in code) and any(c.isalpha() for c in code):
            window = text[max(0, m.start(1)-50):min(len(text), m.end(1)+50)]
            if CODE_CONTEXT_RE.search(window):
                return code
    return None

def extract_link(text):
    urls = URL_RE.findall(text or '')
    if not urls:
        return None
    preferred = [u for u in urls if re.search(r'verify|verification|confirm|activate|auth|login|reset', u, re.I)]
    return (preferred or urls)[0]

def msg_text(m):
    return ' '.join(str(m.get(k) or '') for k in ['subject', 'from', 'body_preview'])

def parse_dt(s):
    if not s:
        return 0
    try:
        return datetime.fromisoformat(str(s).replace('Z', '+00:00')).timestamp()
    except Exception:
        return 0

def cmd_ping(args):
    accounts, data = load_accounts(limit=args.limit)
    print(f"连接成功。账号总数: {data.get('total', len(accounts))}；本次取回: {len(accounts)}")
    for i, acc in enumerate(accounts[:args.show], 1):
        print(fmt_account(acc, i))

def cmd_search(args):
    hits = search_accounts(args.query, limit=args.limit, group_id=args.group_id)
    print(f'匹配数量: {len(hits)}')
    for i, acc in enumerate(hits, 1):
        print(fmt_account(acc, i))

def cmd_copy_email(args):
    email, acc, hits = resolve_email(args.query, allow_ambiguous=args.first)
    ok = copy_text(email)
    if acc:
        print(fmt_account(acc))
    print(f"邮箱: {email}" + ('（已复制）' if ok else '（复制失败，请手动复制）'))

def cmd_emails(args):
    emails, data = get_emails(args.email, args.folder, args.top, args.subject, args.from_contains, args.keyword)
    print(f"邮箱: {data.get('resolved_email') or args.email}；邮件数: {len(emails)}")
    for i, m in enumerate(emails, 1):
        preview = str(m.get('body_preview') or '').replace('\n', ' ')[:120]
        print(f"{i}. [{m.get('folder')}] {m.get('date')} | {m.get('from')} | {m.get('subject')} | {preview}")

def cmd_wait_code(args):
    email, acc, _ = resolve_email(args.target, allow_ambiguous=args.first)
    copied_email = copy_text(email) if args.copy_email else False
    if acc:
        print(fmt_account(acc))
    print(f"已找到邮箱: {email}" + ('（已复制）' if copied_email else ''))
    print(f"开始等待验证码，超时 {args.timeout}s，间隔 {args.interval}s...")
    start = time.time()
    seen_initial = set()
    last_msgs = []
    try:
        initial, _ = get_emails(email, args.folder, args.top, args.subject, args.from_contains, args.keyword)
        if not args.include_existing:
            seen_initial = {email_key(m) for m in initial}
        last_msgs = initial[:3]
    except Exception as e:
        print(f'首次读取失败，将继续重试: {e}', file=sys.stderr)
    while time.time() - start <= args.timeout:
        try:
            messages, _ = get_emails(email, args.folder, args.top, args.subject, args.from_contains, args.keyword)
            messages.sort(key=lambda m: parse_dt(m.get('date')), reverse=True)
            if messages:
                last_msgs = messages[:3]
            for m in messages:
                if email_key(m) in seen_initial:
                    continue
                text = msg_text(m)
                code = extract_code(text)
                link = extract_link(text) if args.link else None
                if code or link:
                    value = code or link
                    copied = copy_text(value) if args.copy_code else False
                    print('收到邮件:')
                    print(f"From: {m.get('from')}")
                    print(f"Subject: {m.get('subject')}")
                    print(f"Date: {m.get('date')} Folder: {m.get('folder')}")
                    if code:
                        print(f"验证码: {code}" + ('（已复制）' if copied else ''))
                    if link:
                        print(f"链接: {link}" + ('（已复制）' if copied and not code else ''))
                    return
        except Exception as e:
            print(f'读取失败，继续重试: {e}', file=sys.stderr)
        time.sleep(args.interval)
    print('等待超时，未提取到验证码。')
    if last_msgs:
        print('最后看到的邮件:')
        for i, m in enumerate(last_msgs, 1):
            preview = str(m.get('body_preview') or '').replace('\n', ' ')[:100]
            print(f"{i}. [{m.get('folder')}] {m.get('date')} | {m.get('from')} | {m.get('subject')} | {preview}")
    sys.exit(2)

def build_parser():
    p = argparse.ArgumentParser(description='outlookEmail API Key CLI')
    sub = p.add_subparsers(dest='cmd', required=True)
    sp = sub.add_parser('ping')
    sp.add_argument('--limit', type=int, default=20)
    sp.add_argument('--show', type=int, default=5)
    sp.set_defaults(func=cmd_ping)
    sp = sub.add_parser('search')
    sp.add_argument('query')
    sp.add_argument('--limit', type=int, default=20)
    sp.add_argument('--group-id', type=int)
    sp.set_defaults(func=cmd_search)
    sp = sub.add_parser('copy-email')
    sp.add_argument('query')
    sp.add_argument('--first', action='store_true', help='多结果时使用第一个')
    sp.set_defaults(func=cmd_copy_email)
    sp = sub.add_parser('emails')
    sp.add_argument('email')
    sp.add_argument('--folder', default='all')
    sp.add_argument('--top', type=int, default=10)
    sp.add_argument('--subject')
    sp.add_argument('--from', dest='from_contains')
    sp.add_argument('--keyword')
    sp.set_defaults(func=cmd_emails)
    sp = sub.add_parser('wait-code')
    sp.add_argument('target', help='邮箱地址或搜索关键词')
    sp.add_argument('--timeout', type=int, default=120)
    sp.add_argument('--interval', type=int, default=5)
    sp.add_argument('--folder', default='all')
    sp.add_argument('--top', type=int, default=10)
    sp.add_argument('--subject')
    sp.add_argument('--from', dest='from_contains')
    sp.add_argument('--keyword')
    sp.add_argument('--first', action='store_true', help='多搜索结果时使用第一个')
    sp.add_argument('--include-existing', action='store_true', help='也从已有邮件中提取验证码')
    sp.add_argument('--no-copy-email', dest='copy_email', action='store_false', default=True)
    sp.add_argument('--no-copy-code', dest='copy_code', action='store_false', default=True)
    sp.add_argument('--link', action='store_true', help='未找到验证码时提取验证链接')
    sp.set_defaults(func=cmd_wait_code)
    return p

def main():
    args = build_parser().parse_args()
    try:
        args.func(args)
    except OutlookEmailError as e:
        die(str(e))
    except KeyboardInterrupt:
        die('已取消', 130)

if __name__ == '__main__':
    main()
