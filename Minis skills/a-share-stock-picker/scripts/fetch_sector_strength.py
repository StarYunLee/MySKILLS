#!/usr/bin/env python3
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

UA = "Mozilla/5.0 (OpenClaw Skill a-share-stock-picker)"
TIMEOUT = 12

STOP_TOKENS = (
    "主营业务", "所属地域", "综合判断", "短期趋势", "中期趋势", "长期趋势",
    "上市日期", "每股净资产", "每股收益", "净利润", "总股本", "流通股", "了解更多",
)

KEYWORD_ALIASES = {
    "CPO": ["CPO", "共封装光学", "光模块", "光通信"],
    "共封装光学": ["共封装光学", "CPO", "光模块", "光通信"],
    "东数西算": ["东数西算", "算力", "数据中心"],
    "数据中心": ["数据中心", "东数西算", "算力"],
    "虚拟电厂": ["虚拟电厂", "电力", "智能电网"],
    "绿色电力": ["绿色电力", "电力", "绿电"],
    "光纤概念": ["光纤概念", "光通信", "光模块"],
    "芯片概念": ["芯片概念", "半导体", "集成电路"],
    "汽车芯片": ["汽车芯片", "芯片概念", "半导体"],
    "国产操作系统": ["国产操作系统", "国产软件", "信创"],
    "减肥药": ["减肥药", "创新药", "医药"],
}


def clean_line(text):
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    text = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9()（）+、，。：；_ /\-]+", "", text)
    return text


def compact_text(text):
    return re.sub(r"\s+", "", clean_line(text))


def truncate_at_noise(text):
    text = compact_text(text)
    for token in STOP_TOKENS:
        pos = text.find(token)
        if pos > 0:
            text = text[:pos]
    return text.strip("：:，,；;。 ")


def cleanup_value(value):
    value = truncate_at_noise(value)
    value = re.sub(r"^(经营分析|公司简介)", "", value)
    parts = re.split(r"[，、,；;]+", value)
    cleaned = []
    for part in parts:
        part = part.strip("：:，,；;。 ")
        if not part:
            continue
        if "(" in part and ")" not in part:
            part = part.split("(")[0]
        if "（" in part and "）" not in part:
            part = part.split("（")[0]
        part = part.strip("：:，,；;。 ")
        if len(part) <= 1:
            continue
        if part not in cleaned:
            cleaned.append(part)
    return cleaned


def extract_concepts(ctx_item):
    pool = []
    pool.extend(ctx_item.get("sectionHighlights") or [])
    pool.extend(ctx_item.get("summary") or []) if isinstance(ctx_item.get("summary"), list) else pool.append(ctx_item.get("summary") or "")
    concepts = []
    for text in pool:
        m = re.search(r"(?:涉及概念|所属概念|概念)[:：]\s*(.+)", clean_line(text))
        if not m:
            continue
        for val in cleanup_value(m.group(1)):
            if val and val not in concepts:
                concepts.append(val)
    return concepts[:8]


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8", errors="ignore"))


def fetch_board_rank(kind, pages=10, page_size=100):
    # Eastmoney board list: t:3 concept boards; t:2 industry boards on most installations.
    fs = "m:90+t:3" if kind == "concept" else "m:90+t:2"
    items = []
    errors = []
    for page in range(1, pages + 1):
        params = {
            "pn": page, "pz": page_size, "po": 1, "np": 1, "fltt": 2, "invt": 2,
            "fid": "f3", "fs": fs,
            "fields": "f12,f14,f3,f62,f128,f136,f152",
        }
        url = "https://push2.eastmoney.com/api/qt/clist/get?" + urllib.parse.urlencode(params)
        try:
            data = fetch_json(url)
            diff = (data.get("data") or {}).get("diff") or []
            if not diff:
                break
            for rank, row in enumerate(diff, start=1 + (page - 1) * page_size):
                items.append({
                    "kind": kind,
                    "code": row.get("f12"),
                    "name": row.get("f14"),
                    "changePct": row.get("f3"),
                    "netInflow": row.get("f62"),
                    "rank": rank,
                })
        except Exception as exc:
            errors.append(f"{kind}-page-{page}: {exc}")
            break
        time.sleep(0.15)
    return items, errors


def match_boards(concepts, boards):
    candidates = []
    for concept in concepts:
        keys = KEYWORD_ALIASES.get(concept, [concept])
        # Add useful fragments for long concept names.
        if len(concept) >= 4:
            keys.append(concept[:4])
        for board in boards:
            name = board.get("name") or ""
            if not name:
                continue
            matched_key = None
            for key in keys:
                if not key:
                    continue
                if key in name or name in key:
                    matched_key = key
                    break
            if matched_key:
                item = dict(board)
                item["sourceConcept"] = concept
                item["matchedKey"] = matched_key
                candidates.append(item)
    # Unique by board code/name, sorted by rank.
    out = []
    seen = set()
    for item in sorted(candidates, key=lambda x: (x.get("rank") or 9999)):
        marker = item.get("code") or item.get("name")
        if marker in seen:
            continue
        seen.add(marker)
        out.append(item)
    return out[:5]


def main():
    if len(sys.argv) < 2:
        print("Usage: fetch_sector_strength.py <ths_context.json> [ticker...]", file=sys.stderr)
        sys.exit(1)
    ctx_path = Path(sys.argv[1])
    tickers = set(t[-6:] for t in sys.argv[2:])
    ctx_data = json.loads(ctx_path.read_text(encoding="utf-8"))
    if tickers:
        ctx_data = [x for x in ctx_data if x.get("ticker") in tickers]

    concept_boards, concept_errors = fetch_board_rank("concept")
    industry_boards, industry_errors = fetch_board_rank("industry")
    boards = concept_boards + industry_boards

    out = []
    for item in ctx_data:
        concepts = extract_concepts(item)
        matches = match_boards(concepts, boards)
        best = matches[0] if matches else None
        out.append({
            "ticker": item.get("ticker"),
            "concepts": concepts,
            "bestBoard": best,
            "matchedBoards": matches,
            "source": "eastmoney_board_rank + ths_context_concepts",
        })
    print(json.dumps({
        "fetchedAt": int(time.time()),
        "conceptBoardCount": len(concept_boards),
        "industryBoardCount": len(industry_boards),
        "errors": concept_errors + industry_errors,
        "items": out,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
