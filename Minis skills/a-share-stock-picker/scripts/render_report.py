#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

TITLE = {'short': '短线标的', 'medium': '中线标的', 'long': '长线标的'}
BASE = Path(__file__).resolve().parent.parent
NAMES_PATH = BASE / 'references' / 'ticker_names.json'
DEFAULT_BUCKET_COUNT = 5


STOP_TOKENS = (
    '主营业务', '所属地域', '综合判断', '短期趋势', '中期趋势', '长期趋势',
    '上市日期', '每股净资产', '每股收益', '净利润', '总股本', '流通股', '了解更多',
)


def load_json_map(path, key='ticker'):
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding='utf-8'))
    return {item[key]: item for item in data if item.get(key)}


def load_sector_strength(path):
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding='utf-8'))
    items = data.get('items') if isinstance(data, dict) else data
    if not isinstance(items, list):
        return {}
    return {item.get('ticker'): item for item in items if item.get('ticker')}


def load_names():
    if NAMES_PATH.exists():
        return json.loads(NAMES_PATH.read_text(encoding='utf-8'))
    return {}


def fmt(v):
    if v is None:
        return '待确认'
    if isinstance(v, float):
        return f'{v:.2f}'
    return str(v)


def clean_line(text):
    text = re.sub(r'\s+', ' ', str(text)).strip()
    text = re.sub(r'[^\u4e00-\u9fffA-Za-z0-9()（）+、，。：；_ /\-]+', '', text)
    return text


def compact_text(text):
    return re.sub(r'\s+', '', clean_line(text))


def truncate_at_noise(text):
    text = compact_text(text)
    for token in STOP_TOKENS:
        pos = text.find(token)
        if pos > 0:
            text = text[:pos]
    return text.strip('：:，,；;。 ')


def context_pool(cat, news):
    pool = []
    for obj in (cat, news):
        pool.extend(obj.get('sectionHighlights') or [])
        pool.extend(obj.get('titles') or [])
        if obj.get('summary'):
            pool.append(obj.get('summary'))
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
    labels_re = '|'.join(re.escape(label) for label in labels)
    m = re.search(r'(?:' + labels_re + r')[:：]\s*(.+)', text)
    if not m:
        return None
    value = cleanup_extracted_value(m.group(1))
    return value[:limit] if value else None


def extract_context_meta(base_meta, row, cat, news):
    meta = dict(base_meta or {})
    ticker = row.get('ticker')

    # 1) name: prefer explicit mapping, then fetched Tonghuashun title/context.
    if not meta.get('name'):
        for text in context_pool(cat, news):
            m = re.search(r'([\u4e00-\u9fffA-Za-z0-9]+)\(' + re.escape(str(ticker)) + r'\)', text)
            if m:
                meta['name'] = m.group(1)
                break
    if not meta.get('name'):
        meta['name'] = ticker

    # 2) sector/concepts: use hand mapping first, otherwise Tonghuashun 涉及概念.
    if not meta.get('sector') or meta.get('sector') == '待补充':
        concepts = None
        for text in context_pool(cat, news):
            concepts = extract_after_label(text, ('涉及概念', '所属概念', '概念'), limit=42)
            if concepts and concepts not in ('--', '待确认'):
                break
        if concepts:
            meta['sector'] = concepts
        else:
            meta['sector'] = '待补充'

    # 3) business/industry clue: Tonghuashun 主营业务 as industry proxy.
    business = None
    for text in context_pool(cat, news):
        business = extract_after_label(text, ('主营业务',), limit=42)
        if business and business not in ('--', '待确认'):
            break
    meta['business'] = business or meta.get('business') or '待确认'
    return meta


def recent_message_dates(cat, news):
    items = (cat.get('items') or news.get('items') or [])
    dates = []
    for item in items:
        dt = item.get('date')
        if dt and dt not in dates:
            dates.append(dt)
    dates.sort(reverse=True)
    return '、'.join(dates[:2]) if dates else '待确认'


def policy_clues(cat, news):
    pool = []
    pool.extend(cat.get('titles', []) or [])
    pool.extend(cat.get('sectionHighlights', []) or [])
    pool.extend(news.get('highlights', []) or [])
    summary = news.get('summary')
    if summary:
        pool.append(summary)
    keywords = ('政策', '国务院', '发改委', '工信部', '财政部', '证监会', '国资委', '能源局', '央行', '商务部', '住建部')
    hits = []
    for item in pool:
        text = clean_line(item)
        if text and any(keyword in text for keyword in keywords) and text not in hits:
            hits.append(text)
    return '；'.join(hits[:2]) if hits else '暂无自动抓取到可信政策线索'


def sector_strength(meta, row, ind, cat, news):
    sector = meta.get('sector', '待补充')
    proxy = 0
    if sector and sector != '待补充':
        proxy += 1
    chg = row.get('summary', {}).get('chg_1d')
    vr = ind.get('vol_ratio')
    text_pool = ' '.join(context_pool(cat, news))
    if chg is not None:
        if chg >= 2:
            proxy += 1
        elif chg < 0:
            proxy -= 1
    if isinstance(vr, (int, float)):
        if vr >= 1.5:
            proxy += 1
        elif vr < 0.8:
            proxy -= 1
    if any(keyword in text_pool for keyword in ('概念', '行业', '题材', '政策', '景气', '涨价', '预增', '芯片', '算力', '电力')):
        proxy += 1
    if proxy >= 3:
        return '较强(代理)'
    if proxy >= 1:
        return '中等(代理)'
    if proxy <= -1:
        return '偏弱(代理)'
    return '待验证'


def position_suggestion(bucket, row):
    score = row.get('scores', {}).get(bucket, 0)
    if bucket == 'short':
        if score >= 88:
            return '轻仓试错'
        if score >= 80:
            return '轻仓'
        return '观察仓'
    if bucket == 'medium':
        if score >= 88:
            return '分批半仓'
        if score >= 80:
            return '分批轻仓'
        return '观察仓'
    if score >= 88:
        return '分批建底仓'
    if score >= 80:
        return '底仓观察'
    return '观察仓'


def evidence_level(meta, cat, news, row):
    checks = 0
    if meta.get('sector') and meta.get('sector') != '待补充':
        checks += 1
    if meta.get('business') and meta.get('business') != '待确认':
        checks += 1
    if row.get('open') and row.get('close'):
        checks += 1
    if cat.get('titles') or cat.get('sectionHighlights'):
        checks += 1
    if news.get('summary'):
        checks += 1
    if isinstance(money_metrics(row).get('netInflow'), (int, float)):
        checks += 1
    if policy_clues(cat, news) != '暂无自动抓取到可信政策线索':
        checks += 1
    if checks >= 5:
        return '高'
    if checks >= 3:
        return '中'
    return '低'


def data_timestamp(row):
    anchor_date = row.get('anchorDate')
    return f'{anchor_date} 收盘锚点' if anchor_date else '待确认'


def money_metrics(row):
    return row.get('marketMetrics') or {}


def money_net_text(row):
    net = money_metrics(row).get('netInflow')
    if not isinstance(net, (int, float)):
        return '待确认'
    sign = '+' if net > 0 else ''
    if abs(net) >= 100000000:
        return f'{sign}{net / 100000000:.2f}亿'
    if abs(net) >= 10000:
        return f'{sign}{net / 10000:.0f}万'
    return f'{sign}{net:.0f}'


def money_flow_view(row):
    metrics = money_metrics(row)
    net = metrics.get('netInflow')
    amount = metrics.get('amount')
    turnover = metrics.get('turnoverPct')
    if not isinstance(net, (int, float)):
        return '待确认'
    verdict = '净流入' if net >= 0 else '净流出'
    strength = '一般'
    if abs(net) >= 500000000:
        strength = '较强'
    elif abs(net) >= 100000000:
        strength = '偏强'
    if isinstance(turnover, (int, float)) and turnover > 20:
        strength += '/高换手'
    elif isinstance(amount, (int, float)) and amount >= 3000000000:
        strength += '/高成交'
    return f'{verdict}{strength}'


def rr(trigger, stop, t1):
    try:
        if None in (trigger, stop, t1):
            return '条件计划'
        risk = abs(trigger - stop)
        reward = abs(t1 - trigger)
        if risk <= 0:
            return '条件计划'
        ratio = reward / risk
        return f'1:{min(max(ratio, 0.5), 5.0):.1f}'
    except Exception:
        return '条件计划'


def shape(row, bucket):
    s = row.get('summary', {})
    last_close, high20, low20 = s.get('last_close'), s.get('high_20'), s.get('low_20')
    if bucket == 'short':
        return '突破型' if last_close and high20 and last_close >= high20 * 0.98 else '趋势型'
    if bucket == 'medium':
        return '趋势型' if last_close and low20 and last_close > low20 * 1.08 else '回踩型'
    return '震荡低吸型' if last_close and high20 and last_close < high20 * 0.85 else '趋势型'


def buy_time(bucket):
    return {'short':'明日 9:35-10:30','medium':'未来 1-5 个交易日分批','long':'未来 5-20 个交易日分批'}[bucket]


def hold(bucket):
    return {'short':'1-5天','medium':'2-8周','long':'3-12个月'}[bucket]


def sell_time(bucket):
    return {'short':'冲高至第一目标减仓，跌破承接位离场','medium':'2-8 周内到目标位分批兑现','long':'季报/半年报后复核，分批处理'}[bucket]


def no_buy(row):
    flow = money_flow_view(row)
    if '净流出' in flow:
        return '高开过多、放量不续强、主力资金继续净流出、数据失真时不买'
    return '高开过多、放量不续强、数据失真时不买'


def levels(row, bucket, ind):
    s = row.get('summary', {})
    close = s.get('last_close')
    low5, high5, high20, low20 = s.get('low_5'), s.get('high_5'), s.get('high_20'), s.get('low_20')
    atr14 = ind.get('atr14')
    if close is None:
        return ('待确认','待确认','待确认',None,None,None,'条件计划',None)
    atr_buf = atr14 if isinstance(atr14, (int, float)) else close * 0.02
    if bucket == 'short':
        support = low5 or close - atr_buf
        resist = high5 or close + atr_buf
        trigger_num = round(close, 2)
        trigger_text = f'{trigger_num:.2f} 附近站稳再看'
        t1, t2 = resist, min(resist + atr_buf, resist * 1.05)
    elif bucket == 'medium':
        support = low20 or close - atr_buf * 2
        resist = high20 or close + atr_buf * 2
        trigger_num = round(close * 0.99, 2)
        trigger_text = f'{trigger_num:.2f}-{close:.2f} 回踩观察'
        t1, t2 = resist, min(resist + atr_buf * 1.5, resist * 1.10)
    else:
        support = low20 or close - atr_buf * 3
        resist = high20 or close + atr_buf * 2
        trigger_num = round(close * 0.98, 2)
        trigger_text = f'{trigger_num:.2f}-{round(close*1.01,2):.2f} 分批观察'
        t1, t2 = resist, min(resist + atr_buf * 1.5, resist * 1.12)
    stop = support * 0.99 if isinstance(support, (int, float)) else None
    return (support, resist, trigger_text, stop, t1, t2, rr(trigger_num, stop, t1), trigger_num)


def board_strength_text(row, meta, sector_item):
    if sector_item:
        best = sector_item.get('bestBoard')
        if best:
            chg = best.get('changePct')
            rank = best.get('rank')
            name = best.get('name')
            if isinstance(chg, (int, float)):
                if chg >= 3:
                    level = '强'
                elif chg >= 1:
                    level = '中强'
                elif chg >= 0:
                    level = '中性'
                else:
                    level = '弱'
                return f"{level}：{name} {chg:.2f}% 排名{rank}"
            return f"已匹配：{name} 排名{rank}"
        if sector_item.get('concepts'):
            return '待验证：' + '，'.join(sector_item.get('concepts')[:3])
    return sector_strength(meta, row, {}, {}, {})


def core_logic(row, bucket, meta, ind, sector_item=None):
    sector = meta.get('sector', '待补充')
    board = board_strength_text(row, meta, sector_item)
    vr = ind.get('vol_ratio')
    ma20 = ind.get('ma20')
    flow = row.get('capitalFlowLabel') or money_flow_view(row)
    if bucket == 'short':
        return f'{sector}方向活跃度较高，板块强度 `{board}`，主力资金 `{flow}`，量比 {fmt(vr)}，看次日承接强弱'
    if bucket == 'medium':
        return f'{sector}方向 20 日结构更完整，板块强度 `{board}`，主力资金 `{flow}`，MA20={fmt(ma20)}，适合回踩跟踪'
    return f'{sector}方向更适合均衡型底仓，板块强度 `{board}`，主力资金 `{flow}`，分批观察更稳妥'


def evidence_lines(row, meta, cat, ind, news, sector_item=None):
    titles = [clean_line(t) for t in cat.get('titles', []) if clean_line(t)]
    highlights = [clean_line(t) for t in (cat.get('sectionHighlights') or news.get('highlights') or []) if clean_line(t)]
    title_text = '；'.join((titles + highlights)[:3]) if (titles or highlights) else '暂无自动抓取到有效线索'
    summary = clean_line(news.get('summary') or '暂无摘要')
    policy_text = policy_clues(cat, news)
    page_count = news.get('pageCount') or cat.get('pageCount')
    useful_count = news.get('usefulItemCount') or cat.get('usefulItemCount')
    page_text = f"；同花顺抓取页数 `{page_count}`" if page_count else ''
    useful_text = f"；有效线索 `{useful_count}`" if useful_count else ''
    s = row.get('summary', {})
    metrics = money_metrics(row)
    amount = metrics.get('amount')
    turnover = metrics.get('turnoverPct')
    flow_in = metrics.get('flowIn')
    flow_out = metrics.get('flowOut')
    return [
        f"- **{meta.get('name', row['ticker'])} {row['ticker']}**：板块/概念 `{meta.get('sector', '待补充')}`；主营/行业线索 `{meta.get('business', '待确认')}`；短/中/长评分 `{row['scores']['short']}/{row['scores']['medium']}/{row['scores']['long']}`。",
        f"  - 价格结构：近 1 日涨跌 `{fmt(s.get('chg_1d'))}%`，MA5/20/60 `{fmt(ind.get('ma5'))}/{fmt(ind.get('ma20'))}/{fmt(ind.get('ma60'))}`，ATR14 `{fmt(ind.get('atr14'))}`，量比 `{fmt(ind.get('vol_ratio'))}`。",
        f"  - 资金面：净流入 `{money_net_text(row)}`，资金判断 `{money_flow_view(row)}`，流入/流出 `{fmt(flow_in)}/{fmt(flow_out)}`，成交额 `{fmt(amount)}`，换手 `{fmt(turnover)}%`。",
        f"  - 板块/行业：`{meta.get('sector', '待补充')}`；主营/行业代理：`{meta.get('business', '待确认')}`；板块强度：`{board_strength_text(row, meta, sector_item)}`。若该字段来自同花顺文本解析，则为代理分类；若包含涨跌幅/排名，则来自外部板块排行匹配。",
        f"  - 新闻/公告：{title_text}",
        f"  - 政策/宏观：{policy_text}",
        f"  - 摘要与来源：{summary}{page_text}{useful_text}；未抓到的证据不做补写。",
    ]


def render_bucket(bucket, rows, names, catalysts, indicators, news, sector_strengths=None):
    out = [f"## {TITLE[bucket]}", "| 股票 | 优先级 | 上个交易日开盘价 | 上个交易日收盘价 | 形态类型 | 板块强度 | 消息日期 | 资金净流入 | 资金面 | 关键支撑 | 关键阻力 | 核心逻辑 | 买入时间 | 触发买价 | 止损价 | 第一目标 | 第二目标 | 风险收益比 | 仓位建议 | 证据级别 | 数据时间戳 | 卖出时间 | 持有周期 | 不买条件 |", "|---|---:|---:|---:|---|---|---|---:|---|---:|---:|---|---|---|---:|---:|---:|---|---|---|---|---|---|---|"]
    for idx, row in enumerate(rows[:DEFAULT_BUCKET_COUNT], start=1):
        ind = indicators.get(row['ticker'], {})
        cat = catalysts.get(row['ticker'], {})
        nw = news.get(row['ticker'], {})
        meta = extract_context_meta(names.get(row['ticker'], {}), row, cat, nw)
        sector_item = (sector_strengths or {}).get(row['ticker'])
        display = f"{meta.get('name', row['ticker'])} {row['ticker']}"
        support, resist, trigger, stop, t1, t2, ratio, _ = levels(row, bucket, ind)
        out.append(f"| {display} | {idx} | {fmt(row.get('open'))} | {fmt(row.get('close'))} | {shape(row, bucket)} | {board_strength_text(row, meta, sector_item)} | {recent_message_dates(cat, nw)} | {money_net_text(row)} | {money_flow_view(row)} | {fmt(support)} | {fmt(resist)} | {core_logic(row, bucket, meta, ind, sector_item)} | {buy_time(bucket)} | {trigger} | {fmt(stop)} | {fmt(t1)} | {fmt(t2)} | {ratio} | {position_suggestion(bucket, row)} | {evidence_level(meta, cat, nw, row)} | {data_timestamp(row)} | {sell_time(bucket)} | {hold(bucket)} | {no_buy(row)} |")
    out.append('')
    out.append(f"### {TITLE[bucket]}说明")
    for row in rows[:DEFAULT_BUCKET_COUNT]:
        cat = catalysts.get(row['ticker'], {})
        ind = indicators.get(row['ticker'], {})
        nw = news.get(row['ticker'], {})
        meta = extract_context_meta(names.get(row['ticker'], {}), row, cat, nw)
        sector_item = (sector_strengths or {}).get(row['ticker'])
        out.extend(evidence_lines(row, meta, cat, ind, nw, sector_item))
    out.append('')
    return '\n'.join(out)


def main():
    if len(sys.argv) not in (2, 3, 4, 5, 6):
        print('Usage: render_report.py <watchlist.json> [catalysts.json] [indicators.json] [news_summary.json] [sector_strength.json]', file=sys.stderr)
        sys.exit(1)
    data = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    names = load_names()
    catalysts = load_json_map(sys.argv[2]) if len(sys.argv) >= 3 else {}
    indicators = load_json_map(sys.argv[3]) if len(sys.argv) >= 4 else {}
    news = load_json_map(sys.argv[4]) if len(sys.argv) >= 5 else {}
    sector_strengths = load_sector_strength(sys.argv[5]) if len(sys.argv) >= 6 else {}
    parts = ['# A股盘前选股战报', '说明：以下内容为盘前观察池 / 条件交易计划，不构成无条件买入建议。板块/行业字段优先来自内置映射；缺失时自动使用同花顺「涉及概念/主营业务」作为代理分类。若提供 sector_strength.json，则板块强度优先使用外部板块排行匹配。', '']
    for bucket in ('short','medium','long'):
        parts.append(render_bucket(bucket, data.get(bucket, []), names, catalysts, indicators, news, sector_strengths))
    if data.get('notes'):
        parts.append('## 补充备注')
        for n in data['notes']:
            parts.append(f'- {n}')
    print('\n'.join(parts))


if __name__ == '__main__':
    main()
