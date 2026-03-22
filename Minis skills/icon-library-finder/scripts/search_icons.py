#!/usr/bin/env python3
import json
import sys
import re
import difflib
import urllib.request
from pathlib import Path

BASE = Path('/var/minis/skills/icon-library-finder')
SOURCES = BASE / 'assets' / 'sources.json'

ZH_HINTS = {
    '小火箭': ['shadowrocket'],
    '圈x': ['quantumultx', 'quantumult x', 'quanx'],
    'quantumultx': ['quanx', 'quantumult x'],
    'loon': ['loon'],
    'surge': ['surge'],
    'egern': ['egern'],
    '微信': ['wechat', 'weixin', 'wx'],
    '支付宝': ['alipay', 'zhifubao'],
    '哔哩哔哩': ['bilibili', 'bili'],
    '微博': ['weibo'],
    '抖音': ['douyin', 'tiktok'],
    '小红书': ['xiaohongshu', 'redbook', 'xhs'],
    'telegram': ['telegram', 'tg'],
    '电报': ['telegram', 'tg'],
    '推特': ['twitter', 'x'],
    '油管': ['youtube', 'yt'],
    '谷歌': ['google', 'chrome', 'gmail'],
    '网飞': ['netflix'],
    '奈飞': ['netflix'],
    '迪士尼': ['disney', 'disneyplus', 'disney plus'],
    '苹果': ['apple', 'icloud', 'appstore', 'apple music'],
    '微软': ['microsoft', 'ms', 'onedrive', 'outlook'],
    '夸克': ['quark'],
    '百度': ['baidu'],
    '高德': ['amap', 'gaode'],
    '地图': ['map', 'maps'],
    '机场': ['airport'],
    '代理': ['proxy'],
}


def load_sources():
    data = json.loads(SOURCES.read_text(encoding='utf-8'))
    return data.get('sources', [])


def clean_url(url):
    return url.replace('\\/', '/') if isinstance(url, str) else ''


def normalize(text):
    text = (text or '').lower().strip()
    text = text.replace('_', ' ').replace('-', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text


def simplify(text):
    return re.sub(r'[^a-z0-9]+', '', normalize(text))


def extract_candidates(data):
    results = []
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str) and value.startswith(('http://', 'https://')):
                results.append({'name': str(key), 'url': clean_url(value)})
            elif isinstance(value, dict):
                name = value.get('name') or value.get('title') or value.get('label') or key
                url = value.get('url') or value.get('icon') or value.get('img') or value.get('image')
                if isinstance(url, str) and url.startswith(('http://', 'https://')):
                    results.append({'name': str(name), 'url': clean_url(url)})
                else:
                    results.extend(extract_candidates(value))
            elif isinstance(value, list):
                results.extend(extract_candidates(value))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                name = item.get('name') or item.get('title') or item.get('label') or item.get('key')
                url = item.get('url') or item.get('icon') or item.get('img') or item.get('image')
                if isinstance(name, str) and isinstance(url, str) and url.startswith(('http://', 'https://')):
                    results.append({'name': name, 'url': clean_url(url)})
                else:
                    results.extend(extract_candidates(item))
    return results


def fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))


def expand_queries(keyword):
    q = normalize(keyword)
    qs = [q]
    joined = simplify(q)
    if joined and joined != q:
        qs.append(joined)
    for k, vals in ZH_HINTS.items():
        if k in q:
            qs.extend(vals)
    uniq = []
    seen = set()
    for item in qs:
        item = normalize(item)
        if item and item not in seen:
            seen.add(item)
            uniq.append(item)
    return uniq


def score_item(queries, name, url):
    n = normalize(name)
    u = normalize(url)
    ns = simplify(name)
    best = 0.0
    for q in queries:
        qs = simplify(q)
        if q == n or qs == ns:
            best = max(best, 1.0)
        elif q in n or q in u or (qs and qs in ns):
            best = max(best, 0.92)
        else:
            ratio = difflib.SequenceMatcher(None, qs or q, ns or n).ratio()
            if ratio >= 0.82:
                best = max(best, round(ratio, 4))
    return best


def search(keyword):
    queries = expand_queries(keyword)
    final = []
    errors = []
    global_seen = set()
    for source in load_sources():
        sname = source.get('name', 'unknown')
        surl = source.get('url', '')
        try:
            data = fetch_json(surl)
            candidates = extract_candidates(data)
            for item in candidates:
                name = str(item.get('name', '')).strip()
                url = clean_url(item.get('url', '')).strip()
                if not name or not url:
                    continue
                score = score_item(queries, name, url)
                if score <= 0:
                    continue
                key = (name, url, sname)
                if key in global_seen:
                    continue
                global_seen.add(key)
                final.append({'source': sname, 'name': name, 'url': url, 'score': score})
        except Exception as e:
            errors.append({'source': sname, 'url': surl, 'error': str(e)})
    final.sort(key=lambda x: (-x['score'], x['name'].lower(), x['source'].lower()))
    return final, errors, queries


def cmd_sources():
    print(json.dumps(load_sources(), ensure_ascii=False, indent=2))


def cmd_search(keyword):
    results, errors, queries = search(keyword)
    out = {'query': keyword, 'expanded_queries': queries, 'count': len(results), 'results': results, 'errors': errors}
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_simple(keyword):
    results, errors, queries = search(keyword)
    print(f'查询: {keyword}')
    print(f'实际匹配词: {", ".join(queries)}')
    if results:
        for i, item in enumerate(results, 1):
            print(f'{i}. {item["name"]} | {item["source"]} | [查看图片]({item["url"]})')
    else:
        print('未找到匹配图标')
    if errors:
        print('\n失败源:')
        for e in errors:
            print(f'- {e["source"]}: {e["error"]}')


def main():
    if len(sys.argv) < 2:
        print('usage: search_icons.py [sources|search <keyword>|simple <keyword>]')
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == 'sources':
        cmd_sources()
    elif cmd == 'search' and len(sys.argv) >= 3:
        cmd_search(sys.argv[2])
    elif cmd == 'simple' and len(sys.argv) >= 3:
        cmd_simple(sys.argv[2])
    else:
        print('usage: search_icons.py [sources|search <keyword>|simple <keyword>]')
        sys.exit(1)


if __name__ == '__main__':
    main()
