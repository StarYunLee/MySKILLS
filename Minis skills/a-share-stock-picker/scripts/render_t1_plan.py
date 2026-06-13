#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
NAMES_PATH = BASE / "references" / "ticker_names.json"
TAIL_ENTRY_COUNT = 5
STOP_TOKENS = (
    "主营业务", "所属地域", "综合判断", "短期趋势", "中期趋势", "长期趋势",
    "上市日期", "每股净资产", "每股收益", "净利润", "总股本", "流通股", "了解更多",
)


def load_names():
    if NAMES_PATH.exists():
        return json.loads(NAMES_PATH.read_text(encoding="utf-8"))
    return {}


def load_json_map(path, key="ticker"):
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding="utf-8"))
    return {item[key]: item for item in data if item.get(key)}


def fmt(value):
    if value is None:
        return "待确认"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def clean_line(text):
    text = re.sub(r"\s+", " ", str(text)).strip()
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


def context_pool(cat, news):
    pool = []
    for obj in (cat, news):
        pool.extend(obj.get("sectionHighlights") or [])
        pool.extend(obj.get("titles") or [])
        if obj.get("summary"):
            pool.append(obj.get("summary"))
    return [clean_line(x) for x in pool if clean_line(x)]


def cleanup_extracted_value(value):
    value = truncate_at_noise(value)
    value = re.sub(r'^(经营分析|公司简介)', '', value)
    parts = re.split(r'[，、,；;]+', value)
    cleaned = []
    for part in parts:
        part = part.strip('：:，,；;。 ')
        if not part:
            continue
        if '(' in part and ')' not in part:
            part = part.split('(')[0]
        if '（' in part and '）' not in part:
            part = part.split('（')[0]
        part = part.strip('：:，,；;。 ')
        if len(part) <= 1:
            continue
        if part and part not in cleaned:
            cleaned.append(part)
    return '，'.join(cleaned) if cleaned else value


def extract_after_label(text, labels, limit=60):
    labels_re = "|".join(re.escape(label) for label in labels)
    m = re.search(r"(?:" + labels_re + r")[:：]\s*(.+)", text)
    if not m:
        return None
    value = cleanup_extracted_value(m.group(1))
    return value[:limit] if value else None


def extract_context_meta(base_meta, row, cat, news):
    meta = dict(base_meta or {})
    ticker = row.get("ticker")
    if not meta.get("name"):
        for text in context_pool(cat, news):
            m = re.search(r"([\u4e00-\u9fffA-Za-z0-9]+)\(" + re.escape(str(ticker)) + r"\)", text)
            if m:
                meta["name"] = m.group(1)
                break
    if not meta.get("name"):
        meta["name"] = ticker

    if not meta.get("sector") or meta.get("sector") == "待补充":
        concepts = None
        for text in context_pool(cat, news):
            concepts = extract_after_label(text, ("涉及概念", "所属概念", "概念"), limit=42)
            if concepts and concepts not in ("--", "待确认"):
                break
        meta["sector"] = concepts or "待补充"

    business = None
    for text in context_pool(cat, news):
        business = extract_after_label(text, ("主营业务",), limit=42)
        if business and business not in ("--", "待确认"):
            break
    meta["business"] = business or meta.get("business") or "待确认"
    return meta


def recent_message_dates(cat, news):
    items = (cat.get("items") or news.get("items") or [])
    dates = []
    for item in items:
        dt = item.get("date")
        if dt and dt not in dates:
            dates.append(dt)
    dates.sort(reverse=True)
    return "、".join(dates[:2]) if dates else "待确认"


def policy_clues(cat, news):
    pool = []
    pool.extend(cat.get("titles", []) or [])
    pool.extend(cat.get("sectionHighlights", []) or [])
    pool.extend(news.get("highlights", []) or [])
    summary = news.get("summary")
    if summary:
        pool.append(summary)
    keywords = ("政策", "国务院", "发改委", "工信部", "财政部", "证监会", "国资委", "能源局", "央行", "商务部", "住建部")
    hits = []
    for item in pool:
        text = clean_line(item)
        if text and any(keyword in text for keyword in keywords) and text not in hits:
            hits.append(text)
    return "；".join(hits[:2]) if hits else "暂无自动抓取到可信政策线索"


def sector_strength(meta, row):
    proxy = 0
    if meta.get("sector") and meta.get("sector") != "待补充":
        proxy += 1
    change_1400 = row.get("changeFrom1400Pct")
    range_position = row.get("rangePosition")
    if change_1400 is not None:
        if change_1400 >= 0.8:
            proxy += 1
        elif change_1400 <= -0.5:
            proxy -= 1
    if range_position is not None:
        if range_position >= 0.8:
            proxy += 1
        elif range_position <= 0.35:
            proxy -= 1
    if proxy >= 2:
        return "较强(代理)"
    if proxy == 1:
        return "中等(代理)"
    if proxy <= -1:
        return "偏弱(代理)"
    return "待验证"


def position_suggestion(row):
    score = row.get("score", 0)
    if score >= 85:
        return "轻仓-半仓"
    if score >= 78:
        return "轻仓"
    return "观察仓"


def evidence_level(meta, cat, news, row):
    checks = 0
    if meta.get("sector") and meta.get("sector") != "待补充":
        checks += 1
    if meta.get("business") and meta.get("business") != "待确认":
        checks += 1
    if row.get("todayOpen") and row.get("todayClose"):
        checks += 1
    if cat.get("titles") or cat.get("sectionHighlights"):
        checks += 1
    if news.get("summary"):
        checks += 1
    if isinstance(money_metrics(row).get("netInflow"), (int, float)):
        checks += 1
    if policy_clues(cat, news) != "暂无自动抓取到可信政策线索":
        checks += 1
    if checks >= 5:
        return "高"
    if checks >= 3:
        return "中"
    return "低"


def data_timestamp(row):
    today = row.get("todayDate")
    minute = row.get("latestMinute")
    if today and minute:
        return f"{today} {minute}"
    if today:
        return str(today)
    return "待确认"


def money_metrics(row):
    return row.get("marketMetrics") or {}


def money_net_text(row):
    net = money_metrics(row).get("netInflow")
    if not isinstance(net, (int, float)):
        return "待确认"
    sign = "+" if net > 0 else ""
    if abs(net) >= 100000000:
        return f"{sign}{net / 100000000:.2f}亿"
    if abs(net) >= 10000:
        return f"{sign}{net / 10000:.0f}万"
    return f"{sign}{net:.0f}"


def money_flow_view(row):
    metrics = money_metrics(row)
    net = metrics.get("netInflow")
    amount = metrics.get("amount")
    turnover = metrics.get("turnoverPct")
    if not isinstance(net, (int, float)):
        return "待确认"
    verdict = "净流入" if net >= 0 else "净流出"
    strength = "一般"
    if abs(net) >= 500000000:
        strength = "较强"
    elif abs(net) >= 100000000:
        strength = "偏强"
    if isinstance(turnover, (int, float)) and turnover > 20:
        strength += "/高换手"
    elif isinstance(amount, (int, float)) and amount >= 3000000000:
        strength += "/高成交"
    return f"{verdict}{strength}"


def evidence_lines(row, meta, cat, news):
    titles = [clean_line(title) for title in cat.get("titles", []) if clean_line(title)]
    highlights = [clean_line(item) for item in (cat.get("sectionHighlights") or news.get("highlights") or []) if clean_line(item)]
    summary = clean_line(news.get("summary") or "暂无自动摘要")
    policy_text = policy_clues(cat, news)
    reasons = "；".join(row.get("scoreNotes", [])[:3]) or "尾盘模式分数较高"
    page_count = news.get("pageCount") or cat.get("pageCount")
    useful_count = news.get("usefulItemCount") or cat.get("usefulItemCount")
    page_text = f"；同花顺抓取页数 `{page_count}`" if page_count else ""
    useful_text = f"；有效线索 `{useful_count}`" if useful_count else ""
    metrics = money_metrics(row)
    amount = metrics.get("amount")
    turnover = metrics.get("turnoverPct")
    flow_in = metrics.get("flowIn")
    flow_out = metrics.get("flowOut")
    return [
        f"- **{meta.get('name', row['ticker'])} {row['ticker']}**：板块/概念 `{meta.get('sector', '待补充')}`；主营/行业线索 `{meta.get('business', '待确认')}`；尾盘评分 `{row.get('score')}`。",
        f"  - 入选原因：{reasons}",
        f"  - 价格结构：D日参考价 `{fmt(row.get('todayClose'))}`，14:00 后变化 `{fmt(row.get('changeFrom1400Pct'))}%`，尾盘量能占比 `{fmt((row.get('lateVolumeShare') or 0) * 100)}%`。",
        f"  - 资金面：净流入 `{money_net_text(row)}`，资金判断 `{money_flow_view(row)}`，流入/流出 `{fmt(flow_in)}/{fmt(flow_out)}`，成交额 `{fmt(amount)}`，换手 `{fmt(turnover)}%`。",
        f"  - 板块/行业：`{meta.get('sector', '待补充')}`；主营/行业代理：`{meta.get('business', '待确认')}`。代理分类来自同花顺文本解析，不等同于官方申万行业。",
        f"  - 新闻/公告：{'；'.join((titles + highlights)[:3]) if (titles or highlights) else '暂无额外页面线索'}",
        f"  - 政策/宏观：{policy_text}",
        f"  - 摘要与来源：{summary}{page_text}{useful_text}；未抓到的证据不做补写。",
    ]


def main():
    if len(sys.argv) not in (2, 3, 4):
        print("Usage: render_t1_plan.py <tail_watchlist.json> [catalysts.json] [news_summary.json]", file=sys.stderr)
        sys.exit(1)
    watchlist = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    catalysts = load_json_map(sys.argv[2]) if len(sys.argv) >= 3 else {}
    news = load_json_map(sys.argv[3]) if len(sys.argv) >= 4 else {}
    names = load_names()
    rows = watchlist.get("tail_entry", [])[:TAIL_ENTRY_COUNT]

    parts = [
        "# A股T+1尾盘建仓计划",
        "说明：本模式用于 D 日尾盘建仓、D+1 日卖出，适配 A 股 T+1 规则。板块/行业字段优先来自内置映射；缺失时自动使用同花顺「涉及概念/主营业务」作为代理分类。",
        "",
        "## 今日尾盘建仓计划",
        "| 股票 | 优先级 | D日开盘价 | D日参考价 | 形态类型 | 板块强度 | 消息日期 | 资金净流入 | 资金面 | 尾盘支撑 | 尾盘阻力 | 核心逻辑 | 建仓时间 | 建仓价格区间 | 隔夜止损线 | 次日止盈一 | 次日止盈二 | 风险收益比 | 仓位建议 | 证据级别 | 数据时间戳 | 次日卖出时间 | 预计持有 | 放弃条件 |",
        "|---|---:|---:|---:|---|---|---|---:|---|---:|---:|---|---|---|---:|---:|---:|---|---|---|---|---|---|---|",
    ]

    for idx, row in enumerate(rows, start=1):
        cat = catalysts.get(row["ticker"], {})
        nw = news.get(row["ticker"], {})
        meta = extract_context_meta(names.get(row["ticker"], {}), row, cat, nw)
        display = f"{meta.get('name', row['ticker'])} {row['ticker']}"
        entry_zone = f"{fmt(row.get('entryLow'))}-{fmt(row.get('entryHigh'))}"
        core_logic = row.get("coreLogic") or f"{meta.get('sector', '待补充')}方向尾盘强度较好，观察次日承接"
        parts.append(
            f"| {display} | {idx} | {fmt(row.get('todayOpen'))} | {fmt(row.get('todayClose'))} | {row.get('setupType')} | {sector_strength(meta, row)} | {recent_message_dates(cat, nw)} | {money_net_text(row)} | {money_flow_view(row)} | {fmt(row.get('support'))} | {fmt(row.get('resistance'))} | {core_logic} | {row.get('buyWindow')} | {entry_zone} | {fmt(row.get('stop'))} | {fmt(row.get('target1'))} | {fmt(row.get('target2'))} | {row.get('riskReward')} | {position_suggestion(row)} | {evidence_level(meta, cat, nw, row)} | {data_timestamp(row)} | {row.get('sellWindow')} | {row.get('holdWindow')} | {row.get('skipCondition')} |"
        )

    parts.extend(["", "## 次日卖出原则"])
    for row in rows:
        cat = catalysts.get(row["ticker"], {})
        nw = news.get(row["ticker"], {})
        meta = extract_context_meta(names.get(row["ticker"], {}), row, cat, nw)
        parts.append(
            f"- `{meta.get('name', row['ticker'])} {row['ticker']}`：{row.get('nextDayPlan')} 若次日竞价明显高于 `第一目标`，优先兑现一部分；若低开并跌破 `隔夜止损线`，不恋战。"
        )

    parts.extend(["", "## 入选说明"])
    for row in rows:
        cat = catalysts.get(row["ticker"], {})
        nw = news.get(row["ticker"], {})
        meta = extract_context_meta(names.get(row["ticker"], {}), row, cat, nw)
        parts.extend(evidence_lines(row, meta, cat, nw))

    if watchlist.get("notes"):
        parts.extend(["", "## 调度备注"])
        for note in watchlist["notes"]:
            parts.append(f"- {note}")

    print("\n".join(parts))


if __name__ == "__main__":
    main()
