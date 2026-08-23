#!/usr/bin/env python3
"""Preflight shortcut request analyzer.

Given a natural-language request, classify route, family, likely recipes,
and what must be clarified before generation.
"""

from __future__ import annotations

import argparse
import json
from request_utils import analyze_prompt


QUESTION_BANK = {
    "trigger": {
        "question": "这个快捷指令从哪里启动？",
        "options": {"A": "手动运行", "B": "从分享菜单接收内容后运行", "C": "小组件、自动化或其他入口"},
    },
    "input": {
        "question": "主要输入方式是什么？",
        "options": {"A": "弹出输入框手动输入", "B": "读取剪贴板或当前已选内容", "C": "接收 URL、图片、文件等外部输入"},
    },
    "target": {
        "question": "目标要写入或输出到哪里？",
        "options": {"A": "系统原生应用", "B": "第三方应用", "C": "文件、URL 或分享面板", "D": "还没确定，需要你推荐"},
    },
    "write_mode": {
        "question": "目标内容要怎么处理？",
        "options": {"A": "新建一条或新建一个对象", "B": "写入固定对象", "C": "每次先选择对象再写入", "D": "先由你推荐最稳的方式"},
    },
    "completion": {
        "question": "完成后要停在哪一步？",
        "options": {"A": "完成后直接结束", "B": "完成后提示结果", "C": "完成后继续打开目标、跳转页面或执行下一步", "D": "完成后先停留在结果预览"},
    },
    "hybrid": {
        "question": "如果纯快捷指令不稳定，是否接受替代路径？",
        "options": {"A": "只接受纯快捷指令", "B": "接受快捷指令 + URL Scheme / 第三方动作", "C": "接受快捷指令 + Minis / 外部服务的混合方案"},
    },
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt")
    args = parser.parse_args()

    analysis = analyze_prompt(args.prompt)
    questions = []
    for key in analysis.missing_dimensions:
        entry = QUESTION_BANK.get(key)
        if entry:
            questions.append({"id": key, **entry})

    result = {
        "prompt": args.prompt,
        "task_family": analysis.task_family,
        "route_label": analysis.route_label,
        "recipes": analysis.recipes,
        "patterns": analysis.patterns,
        "missing_dimensions": analysis.missing_dimensions,
        "questions": questions,
        "reasons": analysis.reasons,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
