#!/usr/bin/env python3
"""Shared heuristics for shortcut request preflight tools."""

from __future__ import annotations

from dataclasses import dataclass

TASK_FAMILY_KEYWORDS = {
    "records": ["记录", "记", "备忘录", "提醒", "笔记", "note", "reminder", "capture", "写入"],
    "query": ["查询", "查看", "天气", "汇率", "日历", "calendar", "weather", "search", "query", "获取", "查"],
    "share": ["分享", "发送", "截图", "照片", "图片", "文件", "share", "send", "screenshot", "photo", "image"],
    "jump": ["打开", "跳转", "启动", "进入", "open", "launch", "scheme", "url"],
    "download": ["下载", "视频", "音频", "douyin", "抖音", "tiktok", "youtube", "bilibili", "video", "audio"],
}

HIGH_RISK_KEYWORDS = ["cookie", "登录", "登录态", "scrape", "crawl", "爬", "抓取", "反爬", "浏览器"]

KNOWN_FIELDS = {
    "trigger": ["分享菜单", "分享", "剪贴板", "手动", "自动化", "小组件", "siri"],
    "input": ["输入框", "输入", "剪贴板", "链接", "url", "图片", "文件", "分享"],
    "target": ["备忘录", "提醒", "笔记", "第三方应用", "文件", "url", "页面", "相册", "照片"],
    "write_mode": ["追加", "新建", "覆盖", "固定", "选择", "append", "create"],
    "completion": ["通知", "提示", "打开", "跳转", "结束", "分享", "完成后"],
    "hybrid": ["minis", "外部服务", "url scheme", "第三方", "hybrid"],
}

RECIPES_BY_FAMILY = {
    "records": ["collect_text_then_write", "collect_text_then_choose_destination", "task_then_followup"],
    "query": ["query_then_show"],
    "share": ["share_input_then_process"],
    "jump": ["construct_and_open_uri", "task_then_followup"],
    "download": ["hybrid_launcher"],
}

PATTERNS_BY_FAMILY = {
    "records": ["ask_text", "menu_select", "write_target", "show_notification"],
    "query": ["ask_text", "current_location", "json_request", "show_result"],
    "share": ["share_input", "transform", "share_output"],
    "jump": ["url_encode", "open_target"],
    "download": ["launcher_shortcut", "handoff_result"],
}


@dataclass
class Analysis:
    task_family: str
    route_label: str
    recipes: list[str]
    patterns: list[str]
    missing_dimensions: list[str]
    reasons: list[str]


def _contains_any(text: str, keywords: list[str]) -> bool:
    lower = text.lower()
    return any(k.lower() in lower for k in keywords)


def analyze_prompt(prompt: str) -> Analysis:
    scores = {family: 0 for family in TASK_FAMILY_KEYWORDS}
    for family, keywords in TASK_FAMILY_KEYWORDS.items():
        scores[family] = sum(1 for k in keywords if k.lower() in prompt.lower())

    task_family = max(scores, key=scores.get)
    if scores[task_family] == 0:
        task_family = "records"

    reasons: list[str] = []
    if task_family == "download":
        if _contains_any(prompt, HIGH_RISK_KEYWORDS):
            route_label = "not-shortcut-first"
            reasons.append("涉及下载平台且伴随登录态、Cookie、网页抓取或浏览器依赖")
        else:
            route_label = "shortcut-hybrid"
            reasons.append("涉及下载或媒体平台，更适合作为 Hybrid 启动器")
    elif task_family in {"records", "query"}:
        route_label = "shortcut-native"
        reasons.append("更接近系统原生动作可覆盖的前台短流程")
    elif task_family in {"share", "jump"}:
        route_label = "shortcut-hybrid" if _contains_any(prompt, ["第三方", "uri", "scheme"]) else "shortcut-native"
        reasons.append("可能需要分享输入、URL Scheme 或目标跳转")
    else:
        route_label = "shortcut-native"
        reasons.append("未命中特殊高风险信号，默认按原生优先")

    missing = [name for name, keys in KNOWN_FIELDS.items() if not _contains_any(prompt, keys)]
    if route_label == "shortcut-native" and "hybrid" in missing:
        missing.remove("hybrid")

    return Analysis(
        task_family=task_family,
        route_label=route_label,
        recipes=RECIPES_BY_FAMILY.get(task_family, ["collect_text_then_write"]),
        patterns=PATTERNS_BY_FAMILY.get(task_family, ["ask_text"]),
        missing_dimensions=missing,
        reasons=reasons,
    )
