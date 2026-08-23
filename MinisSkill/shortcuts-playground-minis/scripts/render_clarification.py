#!/usr/bin/env python3
"""Render clarification questions + recommended flow from preflight analysis."""

from __future__ import annotations

import argparse
import json
from request_utils import analyze_prompt

QUESTION_BANK = {
    "trigger": ("这个快捷指令从哪里启动？", {"A": "手动运行", "B": "从分享菜单接收内容后运行", "C": "小组件、自动化或其他入口"}),
    "input": ("主要输入方式是什么？", {"A": "弹出输入框手动输入", "B": "读取剪贴板或当前已选内容", "C": "接收 URL、图片、文件等外部输入"}),
    "target": ("目标要写入或输出到哪里？", {"A": "系统原生应用", "B": "第三方应用", "C": "文件、URL 或分享面板", "D": "还没确定，需要你推荐"}),
    "write_mode": ("目标内容要怎么处理？", {"A": "新建一条或新建一个对象", "B": "写入固定对象", "C": "每次先选择对象再写入", "D": "先由你推荐最稳的方式"}),
    "completion": ("完成后要停在哪一步？", {"A": "完成后直接结束", "B": "完成后提示结果", "C": "完成后继续打开目标、跳转页面或执行下一步", "D": "完成后先停留在结果预览"}),
    "hybrid": ("如果纯快捷指令不稳定，是否接受替代路径？", {"A": "只接受纯快捷指令", "B": "接受快捷指令 + URL Scheme / 第三方动作", "C": "接受快捷指令 + Minis / 外部服务的混合方案"}),
}

ROUTE_TO_FLOW = {
    "shortcut-native": "先确认边界 → 规划动作链 → 生成 XML 草稿 → 本地验证 → 按需签名交付",
    "shortcut-hybrid": "先确认边界 → 规划快捷指令入口与交接点 → 生成 XML 草稿 → 本地验证 → 按需签名交付",
    "not-shortcut-first": "先确认是否改走 Minis 直接执行 → 如仍需快捷指令，再退化为 launcher 或 Hybrid 入口",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt")
    args = parser.parse_args()

    analysis = analyze_prompt(args.prompt)
    lines = []
    lines.append(f"我理解的流程：{ROUTE_TO_FLOW[analysis.route_label]}")
    lines.append("")

    qn = 1
    for key in analysis.missing_dimensions:
        if key not in QUESTION_BANK:
            continue
        question, options = QUESTION_BANK[key]
        lines.append(f"{qn}. {question}")
        for label, text in options.items():
            lines.append(f"• {label}：{text}")
        lines.append("")
        qn += 1

    lines.append(f"推荐流程：{ROUTE_TO_FLOW[analysis.route_label]}")
    lines.append("可直接复制确认：按推荐流程补齐上面问题的选项后执行。")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
