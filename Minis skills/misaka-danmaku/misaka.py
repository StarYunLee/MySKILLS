#!/usr/bin/env python3
"""Misaka Danmaku 控制 API 客户端 CLI（纯标准库）。

环境变量：
  MISAKA_DANMAKU_BASE_URL  例如 https://danmu.630226.xyz （不带尾部 /）
  MISAKA_DANMAKU_API_KEY   API Key（用 X-API-KEY 请求头传递）

用法示例：
  ./misaka.py library                              # 列出媒体库
  ./misaka.py search-lib 主角                      # 库内按关键词搜
  ./misaka.py anime 118                            # 看作品详情
  ./misaka.py sources 118                          # 看作品的所有源
  ./misaka.py source-episodes 42                   # 看某个源的分集
  ./misaka.py danmaku 12345 -o out.json            # 下载弹幕(JSON)
  ./misaka.py danmaku 12345 --xml -o out.xml       # 转成 dandanplay XML
  ./misaka.py danmaku-batch 118                    # 批量下载某作品全部分集弹幕
  ./misaka.py refresh-ep 12345                     # 刷新单集
  ./misaka.py refresh-anime 118                    # 刷新整部作品（所有源所有分集）
  ./misaka.py import-auto -t keyword -q "斗破苍穹" -m tv_series -s 1 -e 1-5
  ./misaka.py import-auto -t tmdb -q 12345 -s 2
  ./misaka.py task <taskId>                        # 看任务状态
  ./misaka.py tasks                                # 后台任务列表
  ./misaka.py rate-limit                           # 流控状态
"""
from __future__ import annotations
import argparse, json, os, sys, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path

BASE_URL = (os.environ.get("MISAKA_DANMAKU_BASE_URL") or "").rstrip("/")
API_KEY = os.environ.get("MISAKA_DANMAKU_API_KEY") or ""

if not BASE_URL or not API_KEY:
    sys.exit("缺少 MISAKA_DANMAKU_BASE_URL 或 MISAKA_DANMAKU_API_KEY 环境变量")


# ---------------- HTTP helpers ---------------- #
def request(method, path, *, params=None, json_body=None, raw=False, timeout=60):
    url = BASE_URL + path
    if params:
        # 过滤 None
        params = {k: v for k, v in params.items() if v is not None}
        if params:
            url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    headers = {
        "X-API-KEY": API_KEY,
        "Accept": "application/json",
        # 默认 Python-urllib UA 会被 Cloudflare 拦（Error 1010），换个常规 UA
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    }
    data = None
    if json_body is not None:
        data = json.dumps(json_body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            if raw:
                return resp.status, dict(resp.headers), body
            ct = resp.headers.get("Content-Type", "")
            if "application/json" in ct or body[:1] in (b"{", b"["):
                return resp.status, dict(resp.headers), json.loads(body.decode("utf-8")) if body else None
            return resp.status, dict(resp.headers), body.decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        sys.exit(f"HTTP {e.code} {method} {path}\n{body[:1000]}")
    except urllib.error.URLError as e:
        sys.exit(f"网络错误 {method} {path}: {e}")


def get(path, **kw):  return request("GET", path, **kw)
def post(path, **kw): return request("POST", path, **kw)
def put(path, **kw):  return request("PUT", path, **kw)
def delete(path, **kw): return request("DELETE", path, **kw)


# ---------------- pretty print ---------------- #
def pp(obj, *, max_lines=None):
    s = json.dumps(obj, ensure_ascii=False, indent=2)
    if max_lines:
        lines = s.splitlines()
        if len(lines) > max_lines:
            s = "\n".join(lines[:max_lines]) + f"\n... ({len(lines)-max_lines} more lines)"
    print(s)


# ---------------- danmaku format ---------------- #
def to_dandan_xml(payload):
    """payload: {count, comments:[{cid,p,m}]}  →  bilibili/dandanplay 兼容 XML"""
    from xml.sax.saxutils import escape
    out = ['<?xml version="1.0" encoding="UTF-8"?>']
    out.append('<i>')
    out.append(f"  <chatserver>misaka-danmaku</chatserver>")
    out.append(f"  <chatid>0</chatid>")
    out.append(f"  <mission>0</mission>")
    out.append(f"  <maxlimit>{payload.get('count', 0)}</maxlimit>")
    out.append(f"  <state>0</state>")
    out.append(f"  <real_name>0</real_name>")
    out.append(f"  <source>k-v</source>")
    for c in payload.get("comments", []):
        # p 字段格式: time,mode,color,source  → 转成 bilibili 标准 time,mode,fontsize,color,timestamp,pool,user,rowid
        parts = (c.get("p") or "").split(",")
        if len(parts) >= 4:
            t, mode, color, src = parts[0], parts[1], parts[2], parts[3]
        else:
            t = parts[0] if parts else "0"
            mode = parts[1] if len(parts) > 1 else "1"
            color = parts[2] if len(parts) > 2 else "16777215"
            src = parts[3] if len(parts) > 3 else "0"
        p_attr = f"{t},{mode},25,{color},0,0,{src},{c.get('cid','0')}"
        out.append(f'  <d p="{escape(p_attr, {chr(34): "&quot;"})}">{escape(c.get("m") or "")}</d>')
    out.append('</i>')
    return "\n".join(out)


def safe_filename(s, default="untitled"):
    s = (s or default).strip()
    bad = '/\\:*?"<>|\n\r\t'
    for ch in bad:
        s = s.replace(ch, "_")
    return s[:120] or default


# ---------------- commands ---------------- #
def cmd_library(args):
    _, _, data = get("/api/control/library")
    if args.json:
        pp(data); return
    print(f"共 {len(data)} 部作品\n")
    for it in data:
        print(f"  [{it['animeId']:>4}] {it['title']}  ({it.get('type')}, S{it.get('season')}, {it.get('year') or '?'})  分集:{it['episodeCount']}  源:{it['sourceCount']}")


def cmd_search_lib(args):
    _, _, data = get("/api/control/library/search", params={"keyword": args.keyword})
    if args.json:
        pp(data); return
    print(f"匹配 {len(data)} 条")
    for it in data:
        print(f"  [{it['animeId']:>4}] {it['title']}  S{it.get('season')} {it.get('year') or ''}  ep:{it['episodeCount']}")


def cmd_anime(args):
    _, _, data = get(f"/api/control/library/anime/{args.anime_id}")
    pp(data)


def cmd_sources(args):
    _, _, data = get(f"/api/control/library/anime/{args.anime_id}/sources")
    if args.json:
        pp(data); return
    print(f"{len(data)} 个源:")
    for s in data:
        flags = []
        if s.get("isFavorited"): flags.append("★精确")
        if s.get("isFinished"): flags.append("已完结")
        if s.get("incrementalRefreshEnabled"): flags.append("增量刷新")
        print(f"  sourceId={s['sourceId']:>4}  {s['providerName']:10s}  mediaId={s['mediaId']}  ep:{s['episodeCount']}  {' '.join(flags)}")


def cmd_source_episodes(args):
    _, _, data = get(f"/api/control/library/source/{args.source_id}/episodes")
    if args.json:
        pp(data); return
    print(f"{len(data)} 集:")
    for ep in data:
        print(f"  episodeId={ep['episodeId']:>5}  E{ep['episodeIndex']:>3}  弹幕:{ep['commentCount']:>5}  {ep['title']}")


def cmd_danmaku(args):
    _, _, data = get(f"/api/control/danmaku/{args.episode_id}")
    if args.xml:
        text = to_dandan_xml(data)
        if args.output:
            Path(args.output).write_text(text, encoding="utf-8")
            print(f"已保存 XML: {args.output} ({len(data.get('comments', []))} 条弹幕)")
        else:
            print(text)
    else:
        if args.output:
            Path(args.output).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"已保存 JSON: {args.output} ({data.get('count')} 条弹幕)")
        else:
            pp(data, max_lines=40)


def cmd_danmaku_batch(args):
    """批量下载某作品所有分集弹幕。目录结构：<out>/<title>/<provider>_S<source_id>/E<idx> - <title>.xml|json"""
    _, _, anime = get(f"/api/control/library/anime/{args.anime_id}")
    _, _, sources = get(f"/api/control/library/anime/{args.anime_id}/sources")
    title = safe_filename(anime.get("title"))
    base = Path(args.output_dir) / title
    base.mkdir(parents=True, exist_ok=True)
    fmt = "xml" if args.xml else "json"
    total_eps = 0
    total_danmu = 0
    for s in sources:
        if args.favorited_only and not s.get("isFavorited"):
            continue
        sub = base / f"{s['providerName']}_S{s['sourceId']}"
        sub.mkdir(parents=True, exist_ok=True)
        _, _, eps = get(f"/api/control/library/source/{s['sourceId']}/episodes")
        for ep in eps:
            fname = safe_filename(f"E{ep['episodeIndex']:02d} - {ep['title']}") + f".{fmt}"
            fp = sub / fname
            if fp.exists() and not args.force:
                print(f"  跳过(已存在) {fp.relative_to(base.parent)}")
                continue
            _, _, payload = get(f"/api/control/danmaku/{ep['episodeId']}")
            if args.xml:
                fp.write_text(to_dandan_xml(payload), encoding="utf-8")
            else:
                fp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            n = payload.get("count", 0)
            total_eps += 1
            total_danmu += n
            print(f"  ✔ {fp.relative_to(base.parent)}  ({n} 条)")
            time.sleep(args.sleep)
    print(f"\n完成：{total_eps} 集，{total_danmu} 条弹幕，目录 {base}")


def cmd_refresh_ep(args):
    _, _, data = post(f"/api/control/library/episode/{args.episode_id}/refresh")
    pp(data)
    if args.wait and isinstance(data, dict) and data.get("taskId"):
        wait_task(data["taskId"])


def cmd_refresh_anime(args):
    """对一部作品下所有(或指定)源的所有分集逐个刷新。"""
    _, _, sources = get(f"/api/control/library/anime/{args.anime_id}/sources")
    if args.source_id:
        sources = [s for s in sources if s["sourceId"] == args.source_id]
    task_ids = []
    for s in sources:
        if args.favorited_only and not s.get("isFavorited"):
            continue
        _, _, eps = get(f"/api/control/library/source/{s['sourceId']}/episodes")
        for ep in eps:
            _, _, data = post(f"/api/control/library/episode/{ep['episodeId']}/refresh")
            tid = data.get("taskId") if isinstance(data, dict) else None
            print(f"  refresh ep={ep['episodeId']} E{ep['episodeIndex']:02d} → task={tid}")
            if tid:
                task_ids.append(tid)
            time.sleep(args.sleep)
    print(f"已提交 {len(task_ids)} 个刷新任务")


def cmd_import_auto(args):
    params = {
        "searchType": args.search_type,
        "searchTerm": args.term,
        "season": args.season,
        "episode": args.episode,
        "mediaType": args.media_type,
    }
    _, _, data = post("/api/control/import/auto", params=params)
    pp(data)
    if args.wait and isinstance(data, dict) and data.get("taskId"):
        wait_task(data["taskId"])


def cmd_import_url(args):
    body = {"sourceId": args.source_id, "episode_index": args.episode_index, "url": args.url}
    if args.title:
        body["title"] = args.title
    _, _, data = post("/api/control/import/url", json_body=body)
    pp(data)
    if args.wait and isinstance(data, dict) and data.get("taskId"):
        wait_task(data["taskId"])


def cmd_import_xml(args):
    content = Path(args.file).read_text(encoding="utf-8")
    body = {"sourceId": args.source_id, "episode_index": args.episode_index, "content": content}
    if args.title:
        body["title"] = args.title
    _, _, data = post("/api/control/import/xml", json_body=body)
    pp(data)
    if args.wait and isinstance(data, dict) and data.get("taskId"):
        wait_task(data["taskId"])


def cmd_task(args):
    _, _, data = get(f"/api/control/tasks/{args.task_id}")
    pp(data)


def cmd_tasks(args):
    _, _, data = get("/api/control/tasks", params={"search": args.search, "status": args.status})
    if args.json:
        pp(data); return
    for t in data:
        print(f"  {t['status']:12s} {t.get('progress',0):>3}%  {t['taskId']}  {t['title']}")


def cmd_rate_limit(args):
    _, _, data = get("/api/control/rate-limit/status")
    pp(data)


def wait_task(task_id, *, interval=2.0, timeout=600):
    print(f"\n等待任务 {task_id} 完成...")
    start = time.time()
    last = None
    while time.time() - start < timeout:
        _, _, t = get(f"/api/control/tasks/{task_id}")
        line = f"  [{t.get('status'):>12}] {t.get('progress', 0):>3}%  {t.get('description','')}"
        if line != last:
            print(line); last = line
        if t.get("status") in ("completed", "failed", "aborted"):
            return t
        time.sleep(interval)
    print("  (超时)")


# ---------------- argparse ---------------- #
def build_parser():
    ap = argparse.ArgumentParser(description="Misaka Danmaku 控制 API CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("library", help="列出媒体库"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_library)

    p = sub.add_parser("search-lib", help="按关键词搜库")
    p.add_argument("keyword"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_search_lib)

    p = sub.add_parser("anime", help="作品详情")
    p.add_argument("anime_id", type=int); p.set_defaults(func=cmd_anime)

    p = sub.add_parser("sources", help="作品的所有数据源")
    p.add_argument("anime_id", type=int); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_sources)

    p = sub.add_parser("source-episodes", help="某个源的分集列表")
    p.add_argument("source_id", type=int); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_source_episodes)

    p = sub.add_parser("danmaku", help="下载某分集弹幕")
    p.add_argument("episode_id", type=int)
    p.add_argument("-o", "--output"); p.add_argument("--xml", action="store_true", help="保存为 dandanplay XML")
    p.set_defaults(func=cmd_danmaku)

    p = sub.add_parser("danmaku-batch", help="批量下载某作品全部分集弹幕")
    p.add_argument("anime_id", type=int)
    p.add_argument("--output-dir", default="/var/minis/workspace/misaka-danmaku/downloads")
    p.add_argument("--xml", action="store_true")
    p.add_argument("--force", action="store_true", help="覆盖已存在文件")
    p.add_argument("--favorited-only", action="store_true", help="仅下载精确标记的源")
    p.add_argument("--sleep", type=float, default=0.3); p.set_defaults(func=cmd_danmaku_batch)

    p = sub.add_parser("refresh-ep", help="刷新单集弹幕")
    p.add_argument("episode_id", type=int); p.add_argument("--wait", action="store_true"); p.set_defaults(func=cmd_refresh_ep)

    p = sub.add_parser("refresh-anime", help="刷新一部作品所有源所有分集")
    p.add_argument("anime_id", type=int)
    p.add_argument("--source-id", type=int, help="只刷新指定 sourceId")
    p.add_argument("--favorited-only", action="store_true")
    p.add_argument("--sleep", type=float, default=0.5); p.set_defaults(func=cmd_refresh_anime)

    p = sub.add_parser("import-auto", help="全自动搜索并导入")
    p.add_argument("-t", "--search-type", required=True, choices=["keyword","tmdb","tvdb","douban","imdb","bangumi"])
    p.add_argument("-q", "--term", required=True, help="关键词或 ID")
    p.add_argument("-s", "--season", type=int)
    p.add_argument("-e", "--episode", help="集数 (如 1 / 1,3,5 / 1-5)")
    p.add_argument("-m", "--media-type", choices=["movie","tv_series"])
    p.add_argument("--wait", action="store_true"); p.set_defaults(func=cmd_import_auto)

    p = sub.add_parser("import-url", help="从 URL 给已存在源导入某集")
    p.add_argument("--source-id", type=int, required=True)
    p.add_argument("--episode-index", type=int, required=True)
    p.add_argument("--url", required=True)
    p.add_argument("--title")
    p.add_argument("--wait", action="store_true"); p.set_defaults(func=cmd_import_url)

    p = sub.add_parser("import-xml", help="从本地 XML 文件给已存在源导入某集")
    p.add_argument("--source-id", type=int, required=True)
    p.add_argument("--episode-index", type=int, required=True)
    p.add_argument("--file", required=True)
    p.add_argument("--title")
    p.add_argument("--wait", action="store_true"); p.set_defaults(func=cmd_import_xml)

    p = sub.add_parser("task", help="查看任务状态")
    p.add_argument("task_id"); p.set_defaults(func=cmd_task)

    p = sub.add_parser("tasks", help="任务列表")
    p.add_argument("--search"); p.add_argument("--status", default="all", choices=["all","in_progress","completed"])
    p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_tasks)

    p = sub.add_parser("rate-limit", help="流控状态"); p.set_defaults(func=cmd_rate_limit)

    return ap


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
