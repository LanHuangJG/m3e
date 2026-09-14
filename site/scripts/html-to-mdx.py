#!/usr/bin/env python3
"""把 m3e 旧文档的 HTML 正文转成 Astro MDX（Element Plus 风格的 demo 块）。

用法:
    python3 html-to-mdx.py <src-docs-dir> <out-docs-dir> <demos-dir> <lang>

产物:
- <out-docs-dir>/{lang}/components/*.mdx
- <demos-dir>/{component}/{i}.html   预览片段（LiveDemo/Demo 注入）
- <demos-dir>/{component}/{i}.code   源码（复制 + 高亮）

只保留「是什么（intro）+ 用法」两段；密度/无障碍/国际化/样板/API 参考全部丢弃。
showcase 与其后紧邻的 example 配对为一个 demo（预览 + 源码）。
"""

from __future__ import annotations

import html
import re
import sys
import textwrap
from pathlib import Path

# 旧站用的是 @m3e/* 包名，这里统一改成本 fork 的包名
PKG_RENAME = [("@m3e/icons", "m3e-icons"), ("@m3e/react", "m3e-react"), ("@m3e/web", "m3e"), ("@m3e/", "m3e/")]


def rename_pkgs(s: str) -> str:
    for a, b in PKG_RENAME:
        s = s.replace(a, b)
    return s


ORDER = {
    "app-bar": 1, "autocomplete": 2, "avatar": 3, "badge": 4, "bottom-sheet": 5, "breadcrumb": 6,
    "button": 7, "button-group": 8, "calendar": 9, "card": 10, "checkbox": 11, "chips": 12,
    "content-pane": 13, "date-input": 14, "datepicker": 15, "dialog": 16, "divider": 17,
    "drawer-container": 18, "expansion-panel": 19, "fab": 20, "fab-menu": 21, "form-field": 22,
    "heading": 23, "icon": 24, "icon-button": 25, "list": 26, "loading-indicator": 27, "menu": 28,
    "nav-bar": 29, "nav-menu": 30, "nav-rail": 31, "paginator": 32, "progress-indicator": 33,
    "radio-group": 34, "search": 35, "segmented-button": 36, "select": 37, "shape": 38, "skeleton": 39,
    "slide-group": 40, "slider": 41, "snackbar": 42, "split-button": 43, "split-pane": 44,
    "stepper": 45, "switch": 46, "tabs": 47, "textarea-autosize": 48, "theme": 49, "timepicker": 50,
    "toc": 51, "toolbar": 52, "tooltip": 53, "tree": 54,
}

COMPONENTS = list(ORDER)

# 非组件页（章节 -> 页面 -> 排序）
NONCOMP = {
    "getting-started": {"overview": 1, "installation": 2, "browser-support": 3},
    "styles": {"color": 1, "density": 2, "motion": 3, "typography": 4},
    "frameworks": {"react": 1, "vue": 2, "angular": 3},
}
DROP_TITLES = {"原生模块支持", "Native module support", "API 参考", "API Reference"}


def drop_sections(body: str) -> str:
    """按 level-2 标题丢弃样板章节，其余保留。"""
    hs = list(re.finditer(r'<m3e-heading[^>]*level="2"[^>]*>(.*?)</m3e-heading>', body, re.S))
    if not hs:
        return body
    keep = [body[: hs[0].start()]]
    for i, h in enumerate(hs):
        end = hs[i + 1].start() if i + 1 < len(hs) else len(body)
        if strip_tags(h.group(1)) not in DROP_TITLES:
            keep.append(body[h.start() : end])
    return "".join(keep)

# 组件分类（对齐 Material 3 的五类 + 基础）
CATEGORY = {
    # 操作 Actions
    "button": "actions", "button-group": "actions", "fab": "actions", "fab-menu": "actions",
    "icon-button": "actions", "segmented-button": "actions", "split-button": "actions",
    "split-pane": "containment",
    # 通信 Communication
    "badge": "communication", "loading-indicator": "communication",
    "progress-indicator": "communication", "skeleton": "communication",
    "snackbar": "communication", "tooltip": "communication",
    # 容器 Containment
    "bottom-sheet": "containment", "card": "containment", "content-pane": "containment",
    "dialog": "containment", "divider": "containment", "expansion-panel": "containment",
    "list": "containment", "toolbar": "containment", "tree": "containment",
    # 导航 Navigation
    "app-bar": "navigation", "breadcrumb": "navigation", "drawer-container": "navigation",
    "menu": "navigation", "nav-bar": "navigation", "nav-menu": "navigation",
    "nav-rail": "navigation", "paginator": "navigation", "search": "navigation",
    "slide-group": "navigation", "stepper": "navigation", "tabs": "navigation", "toc": "navigation",
    # 选择 Selection（含表单控件）
    "autocomplete": "selection", "calendar": "selection", "checkbox": "selection",
    "chips": "selection", "date-input": "selection", "datepicker": "selection",
    "form-field": "selection", "radio-group": "selection", "select": "selection",
    "slider": "selection", "switch": "selection", "textarea-autosize": "selection",
    "timepicker": "selection",
    # 基础 Basics
    "avatar": "basics", "heading": "basics", "icon": "basics", "shape": "basics", "theme": "basics",
}


def strip_tags(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def dedent_code(code: str) -> str:
    return textwrap.dedent(html.unescape(code).strip("\n")).strip("\n")


def guess_lang(code: str) -> str:
    c = code.lstrip()
    if c.startswith(".") or c.startswith("{") or "--md-sys" in c or "/*" in c:
        return "css"
    if "document." in c or c.startswith("const ") or "=>" in c or "addEventListener" in c:
        return "js"
    return "html"


def fence(code: str, lang: str) -> str:
    body = dedent_code(code)
    return f"```{lang}\n{body}\n```" if body else ""


def extract_matching_div(s: str, start: int) -> str:
    depth = 0
    i = start
    while i < len(s):
        m = re.compile(r"<div\b|</div\s*>").search(s, i)
        if not m:
            break
        if m.group(0).startswith("</"):
            depth -= 1
            if depth == 0:
                return s[start : m.end()]
        else:
            depth += 1
        i = m.end()
    return s[start:]


def find_card_end(s: str, start: int) -> int:
    depth = 0
    i = start
    pat = re.compile(r"<m3e-card\b|</m3e-card\s*>")
    while i < len(s):
        m = pat.search(s, i)
        if not m:
            break
        if m.group(0).startswith("</"):
            depth -= 1
            if depth == 0:
                return m.end()
        else:
            depth += 1
        i = m.end()
    return len(s)


def normalize_tags(s: str) -> str:
    def fix(m: re.Match) -> str:
        tag = re.sub(r"\s+", " ", m.group(0))
        tag = re.sub(r"<\s+", "<", tag)
        return re.sub(r"\s+>", ">", tag)

    return re.sub(r"<[^<>]*>", fix, s, flags=re.S)


def escape_md(s: str) -> str:
    """转义标签外的 Markdown 特殊字符（* _ ~），避免被当成强调/删除线。"""
    parts = re.split(r"(<[^<>]*>)", s)
    for i in range(len(parts)):
        if i % 2 == 1:
            continue
        parts[i] = parts[i].replace("*", "&#42;").replace("_", "&#95;").replace("~", "&#126;")
    return "".join(parts)


def flatten_blocks(s: str) -> str:
    for tag in ("ul", "ol", "p", "li", "blockquote"):
        s = re.sub(
            rf"<{tag}\b[^>]*>.*?</{tag}>",
            lambda m: re.sub(r"\s+", " ", m.group(0)).strip(),
            s,
            flags=re.S,
        )
    return s


def extract_code(card: str) -> str:
    pre = re.search(r'<pre slot="content">(.*?)</pre\s*>', card, re.S)
    return pre.group(1) if pre else ""


def keep_intro_and_usage(body: str) -> str:
    hs = list(re.finditer(r'<m3e-heading[^>]*level="2"[^>]*>(.*?)</m3e-heading>', body, re.S))
    usage = next((i for i, h in enumerate(hs) if strip_tags(h.group(1)) in ("用法", "Usage")), None)
    if usage is None:
        return body
    intro = body[: hs[0].start()]
    end = hs[usage + 1].start() if usage + 1 < len(hs) else len(body)
    return intro + body[hs[usage].start() : end]


def convert(src: str, component: str, lang: str, section: str = "components", section_prefix: str = "components") -> tuple[str, str, str, list[dict]]:
    demos: list[dict] = []
    m = re.search(r'<m3e-content-pane id="body">(.*?)</m3e-content-pane>', src, re.S)
    body = m.group(1) if m else src

    h1 = re.search(r'<m3e-heading[^>]*level="1"[^>]*>(.*?)</m3e-heading>', body, re.S)
    title = re.sub(r"\s+", " ", strip_tags(h1.group(1))).strip() if h1 else component
    if h1:
        body = body[: h1.start()] + body[h1.end() :]

    body = keep_intro_and_usage(body) if section == "components" else drop_sections(body)

    pm = re.search(r"<p>(.*?)</p>", body, re.S)
    summary = re.sub(r"\s+", " ", strip_tags(pm.group(1))).strip() if pm else title

    # 扫描所有卡片，showcase 与紧随的 example 配对
    cards: list[tuple[str, str, int, int]] = []
    idx = 0
    pat = re.compile(r'<m3e-card\b[^>]*class="(showcase|example|install)"[^>]*>')
    while True:
        mm = pat.search(body, idx)
        if not mm:
            break
        end = find_card_end(body, mm.start())
        cards.append((mm.group(1), body[mm.start() : end], mm.start(), end))
        idx = end

    out: list[str] = []
    cursor = 0
    last_demo = -1
    last_demo_end = -1
    for kind, card, start, end in cards:
        # 保留卡片之间的原始内容（正文）
        if start > cursor:
            out.append(body[cursor:start])
        cursor = end

        if kind == "showcase":
            div = re.search(r'<div slot="content">', card)
            if not div:
                continue
            div_html = extract_matching_div(card, div.start())
            inner = re.sub(r'^<div slot="content">', "", div_html)
            inner = re.sub(r"</div>\s*$", "", inner).strip()
            demos.append({"html": inner, "code": "", "lang": "html"})
            last_demo = len(demos) - 1
            last_demo_end = end
            out.append(f'\n<Demo name="{lang}/{section_prefix}/{component}/{last_demo}" />\n')
        elif kind == "install":
            out.append("\n" + fence(extract_code(card), "js") + "\n")
            last_demo = -1
        else:  # example：若紧跟在 showcase 之后（中间只有空白）则配对为源码
            code = extract_code(card)
            adjacent = last_demo >= 0 and body[last_demo_end:start].strip() == ""
            if adjacent and demos[last_demo]["code"] == "":
                demos[last_demo]["code"] = dedent_code(code)
                demos[last_demo]["lang"] = guess_lang(html.unescape(code))
            else:
                out.append("\n" + fence(code, guess_lang(html.unescape(code))) + "\n")
            last_demo = -1
    out.append(body[cursor:])
    body = "".join(out)

    def heading_repl(level: int):
        def inner(m: re.Match) -> str:
            return "\n" + "#" * level + " " + strip_tags(m.group(1)) + "\n"

        return inner

    body = re.sub(r'<m3e-heading[^>]*level="2"[^>]*>(.*?)</m3e-heading>', heading_repl(2), body, flags=re.S)
    body = re.sub(r'<m3e-heading[^>]*level="3"[^>]*>(.*?)</m3e-heading>', heading_repl(3), body, flags=re.S)
    body = re.sub(r'<m3e-heading[^>]*level="4"[^>]*>(.*?)</m3e-heading>', heading_repl(4), body, flags=re.S)

    body = re.sub(r"<p>\s*本节提供该模块组件的用法示例与配置指引。\s*</p>", "", body)
    body = re.sub(r"<p>\s*This section (?:provides|details)[^<]*</p>", "", body)
    body = re.sub(r"<api-viewer\b.*?</api-viewer\s*>", "", body, flags=re.S)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    body = re.sub(r"[ \t]+\n", "\n", body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()

    parts = re.split(r"(```.*?```)", body, flags=re.S)
    prefix = "" if lang == "en" else "/zh"
    for i in range(0, len(parts), 2):
        seg = normalize_tags(parts[i])
        seg = re.sub(
            r'href="\.\./(getting-started|styles|frameworks|components)/([a-z0-9-]+)\.html(#[^"]*)?"',
            lambda m: f'href="{prefix}/{m.group(1)}/{m.group(2)}/{m.group(3) or ""}"',
            seg,
        )
        seg = flatten_blocks(seg)
        seg = "\n".join(line.lstrip() for line in seg.split("\n"))
        parts[i] = escape_md(seg.replace("{", "&#123;").replace("}", "&#125;"))
    body = "".join(parts)

    body = rename_pkgs(body)
    for demo in demos:
        demo["html"] = rename_pkgs(demo["html"])
        demo["code"] = rename_pkgs(demo["code"])
    return title, summary, body, demos


def main() -> int:
    src_dir = Path(sys.argv[1])
    out_root = Path(sys.argv[2])
    demos_root = Path(sys.argv[3])
    lang = sys.argv[4]
    out_dir = out_root / lang / "components"
    out_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    jobs = [("components", n, ORDER.get(n, 100)) for n in COMPONENTS]
    for sec, pages in NONCOMP.items():
        jobs += [(sec, n, o) for n, o in pages.items()]
    for section, name, order in jobs:
        f = src_dir / section / f"{name}.html"
        if not f.exists():
            print("MISS", f)
            continue
        title, summary, body, demos = convert(f.read_text(encoding="utf-8"), name, lang, section, section)
        d = demos_root / lang / section / name
        legacy = demos_root / name
        if legacy.exists():
            for old in legacy.glob("*"):
                old.unlink()
        if d.exists():
            for old in d.glob("*"):
                old.unlink()
        d.mkdir(parents=True, exist_ok=True)
        for i, demo in enumerate(demos):
            (d / f"{i}.html").write_text(demo["html"] + "\n", encoding="utf-8")
            (d / f"{i}.code").write_text(demo["code"] + "\n", encoding="utf-8")

        script = name if (src_dir / "components" / f"{name}.js").exists() else ""
        fm = (
            "---\n"
            f'title: "{title.replace(chr(34), chr(92) + chr(34))}"\n'
            f'description: "{summary.replace(chr(34), chr(92) + chr(34))}"\n'            f'summary: "{summary.replace(chr(34), chr(92) + chr(34))}"\n'
            f'script: "{script}"\n'
            f"section: {section}\n"
            + (f'category: "{CATEGORY.get(name, "basics")}"\n' if section == "components" else "")
            + f"order: {order}\n"
            "---\n\n"
        )
        dest = out_dir if section == "components" else (out_root / lang / section)
        dest.mkdir(parents=True, exist_ok=True)
        (dest / f"{name}.mdx").write_text(fm + body + "\n", encoding="utf-8")
        count += 1
    print(f"[{lang}] {count} MDX, {sum(1 for _ in demos_root.rglob('*.html'))} demos -> {demos_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
