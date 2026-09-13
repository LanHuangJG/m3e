#!/usr/bin/env python3
"""M3E 文档站样板段批量中译。

文档站每个组件页底部都有几段几乎逐字重复的固定文本（原生模块支持 /
import map / API 参考）。这些段落的英文只差空格换行，正文却完全一致，
适合用一张正则映射表统一替换；每页独有的正文仍由人工翻译。

用法:
    python3 scripts/localize-boilerplate.py            # 干跑，只报数量
    python3 scripts/localize-boilerplate.py --apply    # 写回文件

仅在命中时才改动，重复运行幂等（译后文本不再匹配英文模式）。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

MODULES_URL = "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules#module_specifiers"
IMPORTMAP_URL = "https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/script/type/importmap"
CEM_URL = "https://github.com/webcomponents/custom-elements-manifest"

# 每条: (名称, 正则, 替换文本)。正则里用 \s* 容忍标签间的换行与缩进。
RULES: list[tuple[str, re.Pattern[str], str]] = [
    (
        "原生模块支持-标准",
        re.compile(
            r"The\s*<code>@m3e/web</code>\s*package uses\s*"
            r'<a\s+href="' + re.escape(MODULES_URL) + r'"\s+target="_blank"\s*>'
            r"JavaScript Modules</a\s*>\s*\.\s*"
            r"To use it directly in a browser without a bundler,\s*"
            r"use a module script similar to the following\."
        ),
        f'<code>@m3e/web</code> 包使用 <a href="{MODULES_URL}" target="_blank">JavaScript Modules</a>。'
        f"要在不借助构建工具的情况下直接在浏览器中使用,请使用类似下面的 module 脚本。",
    ),
    (
        "原生模块支持-安装页",
        re.compile(
            r"Each package uses\s*"
            r'<a\s+href="' + re.escape(MODULES_URL) + r'"\s+target="_blank"\s*>'
            r"JavaScript Modules</a\s*>\s*"
            r"and documents their native module support\.\s*"
            r"To use a module directly in a browser without a bundler,\s*"
            r"use a\s+module script similar to the following\."
        ),
        f'每个包都使用 <a href="{MODULES_URL}" target="_blank">JavaScript Modules</a>,'
        f"并说明了各自对原生模块的支持。要在不借助构建工具的情况下直接在浏览器中使用某个模块,"
        f"请使用类似下面的 module 脚本。",
    ),
    (
        "import map-安装页",
        re.compile(
            r"In addition,\s*you must also use an\s*"
            r'<a\s+href="' + re.escape(IMPORTMAP_URL) + r'"\s+target="_blank"\s*>'
            r"import map</a\s*>\s*"
            r"to include dependencies\.\s*"
            r"The following is an example import map that imports all entry points for\s*"
            r"<code>@m3e/web/core</code>\."
        ),
        f'此外,你还必须使用一个 <a href="{IMPORTMAP_URL}" target="_blank">import map</a> 来引入依赖。'
        f"下面是一个示例 import map,它导入了 <code>@m3e/web/core</code> 的所有入口。",
    ),
    (
        "import map-标准",
        re.compile(
            r"In addition,\s*you must (?:also\s+)?use an\s*"
            r'<a\s+href="' + re.escape(IMPORTMAP_URL) + r'"\s+target="_blank"\s*>'
            r"import map</a\s*>\s*"
            r"to include (?:additional\s+)?dependencies\."
        ),
        f'此外,你还必须使用一个 <a href="{IMPORTMAP_URL}" target="_blank">import map</a> 来引入依赖。',
    ),
    (
        "依赖项 module 脚本",
        re.compile(
            r"You also need a module script for\s*"
            r"((?:<code>[^<]*</code>(?:\s*and\s*)?)+)\s*"
            r"due to (?:it )?being a dependency\."
        ),
        r"由于 \1 是依赖项,你还需要为它引入一个 module 脚本。",
    ),
    (
        "API 参考-Custom Elements Manifest",
        re.compile(
            r"The\s*<code>@m3e/web</code>\s*package includes a\s*"
            r'<a\s+href="' + re.escape(CEM_URL) + r'"\s+target="_blank"\s*>'
            r"Custom Elements Manifest</a\s*>\s*"
            r"\(<code>custom-elements\.json</code>\),\s*"
            r"which documents the properties, attributes, slots, events and CSS custom\s+properties of each component\."
        ),
        f'<code>@m3e/web</code> 包附带 <a href="{CEM_URL}" target="_blank">Custom Elements Manifest</a> '
        f"(<code>custom-elements.json</code>),其中记录了每个组件的属性、特性、插槽、事件与 CSS 自定义属性。",
    ),
    (
        "编辑器集成-Custom Elements Manifest",
        re.compile(
            r"The\s*<code>@m3e/web</code>\s*package includes a\s*"
            r'<a\s+href="' + re.escape(CEM_URL) + r'"\s+target="_blank"\s*>'
            r"Custom Elements Manifest</a\s*>\s*"
            r"to support enhanced editor tooling and developer experience\."
        ),
        f'<code>@m3e/web</code> 包附带一份 <a href="{CEM_URL}" target="_blank">Custom Elements Manifest</a>,'
        f"以支持增强的编辑器工具与开发体验。",
    ),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="写回文件（默认只统计）")
    args = ap.parse_args()

    files = sorted(DOCS.rglob("*.html"))
    total = 0
    touched: set[Path] = set()
    per_rule: dict[str, int] = {}

    for path in files:
        src = path.read_text(encoding="utf-8")
        out = src
        for name, pattern, repl in RULES:
            out, n = pattern.subn(lambda m: m.expand(repl), out)
            if n:
                per_rule[name] = per_rule.get(name, 0) + n
                total += n
        if out != src:
            touched.add(path)
            if args.apply:
                path.write_text(out, encoding="utf-8")

    print(f"{'[apply] ' if args.apply else '[dry-run] '}命中 {total} 处，涉及 {len(touched)} 个文件")
    for name, n in per_rule.items():
        print(f"  {n:>3}  {name}")

    # 干跑时列出未命中任何规则、仍含样板英文的文件，便于人工兜底。
    leftovers = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        if "package uses" in text or "package includes a" in text or "You also need a module script" in text:
            leftovers.append(path.relative_to(ROOT))
    if leftovers:
        print("\n仍含样板英文的文件（需人工确认）:")
        for p in leftovers:
            print("  ", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
