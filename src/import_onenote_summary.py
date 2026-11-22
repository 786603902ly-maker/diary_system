#!/usr/bin/env python3
"""把 OneNote 导出的「！总结--豆瓣所有书籍」(.mht) 转成 data/book-summaries.json。

用法（一次性导入；以后 OneNote 原页面有大改动时可重跑）：
    python3 -I src/import_onenote_summary.py <导出的.mht> [--keep-claude]

- 保留排版：文字颜色 / 高亮底色 / 加粗 / 斜体 / 下划线 / 缩进 / 有序无序列表（含 a,b,c 编号）/
  树状图里的连续空格 / 豆瓣链接 / 内嵌图片。字体统一由页面 CSS 给楷体，不逐字保留。
- 去掉：OneNote 的版面宽度、mso-* 私有样式、黑色字色（交给页面默认色）。
- OneNote 里的两个小图标换成同色字符：image001（橙色星，"重要"）→ ★，image002（蓝色星号，
  "参考资料"）→ ✳；其它图片以 data URI 内嵌。
- --keep-claude：保留现有 JSON 里 by=="claude" 的行（Claude 代写的总结），按原相对位置插回，
  这样重导 OneNote 原文不会冲掉代写内容。
"""
import base64
import email
import html
import json
import re
import sys
from email import policy
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "book-summaries.json"

KEEP_TAGS = {"p", "span", "b", "strong", "i", "em", "u", "br", "ul", "ol", "li", "a", "div", "img",
             "table", "tr", "td", "th", "tbody"}
VOID = {"br", "img"}
DROP_COLORS = {"black", "#000000", "#000", "windowtext"}
ICON_MAP = {
    "image001.png": '<span class="bs-ico bs-ico-star" title="重要">★</span>',
    "image002.png": '<span class="bs-ico bs-ico-ref" title="参考资料及链接">✳</span>',
}
BASE_PT = 11.0


def conv_len(v):
    """OneNote 用英寸做缩进，换算成 em（11pt 正文下 1in ≈ 6.55em）。"""
    m = re.fullmatch(r"(-?[\d.]+)in", v.strip())
    if not m:
        return None
    em = float(m.group(1)) * 72 / BASE_PT
    return None if abs(em) < 0.05 else f"{em:.2f}em"


def clean_style(style, tag):
    out = []
    for rule in style.split(";"):
        if ":" not in rule:
            continue
        prop, val = rule.split(":", 1)
        prop, val = prop.strip().lower(), val.strip()
        lv = val.lower()
        if prop == "color":
            if lv not in DROP_COLORS:
                out.append(f"color:{val}")
        elif prop in ("background", "background-color"):
            if lv not in ("white", "#ffffff", "transparent"):
                out.append(f"background:{val}")
        elif prop == "font-weight":
            if lv in ("bold", "700", "800", "900"):
                out.append("font-weight:700")
            elif lv == "normal":
                out.append("font-weight:400")
        elif prop == "font-style":
            if lv in ("italic", "normal"):
                out.append(f"font-style:{lv}")
        elif prop == "text-decoration":
            if lv in ("underline", "line-through", "none"):
                out.append(f"text-decoration:{lv}")
        elif prop == "margin-left" and tag in ("p", "div", "ul", "ol"):
            em = conv_len(val)
            if em:
                out.append(f"margin-left:{em}")
        elif prop == "font-size":
            m = re.fullmatch(r"([\d.]+)pt", lv)
            if m:
                ratio = float(m.group(1)) / BASE_PT
                if ratio >= 1.12 or ratio <= 0.93:
                    out.append(f"font-size:{ratio:.2f}em")
    return ";".join(out)


class Cleaner(HTMLParser):
    def __init__(self, images):
        super().__init__(convert_charrefs=True)
        self.images = images
        self.out = []
        self.spacerun = 0
        self.stack = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "img":
            name = (a.get("src") or "").split("/")[-1]
            if name in ICON_MAP:
                self.out.append(ICON_MAP[name])
            elif name in self.images:
                w = a.get("width") or ""
                size = f' style="width:{w}px"' if w.isdigit() else ""  # 保持 OneNote 里的显示尺寸
                self.out.append(f'<img class="bs-img"{size} alt="{html.escape(a.get("alt") or "")}" '
                                f'src="data:image/png;base64,{self.images[name]}">')
            return
        if tag not in KEEP_TAGS:
            self.stack.append(None)
            return
        style = a.get("style") or ""
        is_spacerun = "mso-spacerun" in style
        attrs_out = []
        cs = clean_style(style, tag)
        if cs:
            attrs_out.append(f'style="{cs}"')
        if tag in ("ol", "ul") and a.get("type"):
            attrs_out.append(f'type="{html.escape(a["type"])}"')
        if tag == "li" and a.get("value"):
            attrs_out.append(f'value="{html.escape(a["value"])}"')
        if tag == "a":
            href = a.get("href") or ""
            if re.match(r"https?://", href):
                attrs_out.append(f'href="{html.escape(href)}" target="_blank" rel="noopener"')
        if tag in VOID:
            self.out.append(f"<{tag}>")
            return
        self.stack.append((tag, is_spacerun))
        if is_spacerun:
            self.spacerun += 1
        self.out.append(f"<{tag}{(' ' + ' '.join(attrs_out)) if attrs_out else ''}>")

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            return
        top = self.stack.pop()
        if top is None:
            return
        t, sr = top
        if sr:
            self.spacerun -= 1
        self.out.append(f"</{t}>")

    def handle_data(self, data):
        if self.spacerun:
            data = data.replace(" ", " ")
        # OneNote 的 HTML 只在空白处折行；源码里的换行+缩进 = 一个空格
        data = re.sub(r"[ \t\r]*\n[ \t\r]*", " ", data)
        self.out.append(html.escape(data, quote=False))


def clean(fragment, images):
    c = Cleaner(images)
    c.feed(fragment)
    c.close()
    s = "".join(c.out)
    # 去掉空 span，压缩全空段落
    s = re.sub(r"<span>([^<]*)</span>", r"\1", s)
    return s.strip()


def inline_p_background(h):
    """OneNote 的段落高亮只覆盖文字宽度；<p style=background> 在网页里会铺满整行，改成内层 span。"""
    def fix(m):
        styles = [x for x in m.group(1).split(";") if x]
        bg = [x for x in styles if x.startswith("background:")]
        if not bg:
            return m.group(0)
        rest = [x for x in styles if not x.startswith("background:")]
        attr = f' style="{";".join(rest)}"' if rest else ""
        return f'<p{attr}><span style="{bg[0]}">{m.group(2)}</span></p>'
    return re.sub(r'<p style="([^"]*)">(.*?)</p>', fix, h, flags=re.S)


def text_of(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", h))).replace(" ", " ").strip()


def load_mht(path):
    msg = email.message_from_binary_file(open(path, "rb"), policy=policy.default)
    page, images = None, {}
    for part in msg.walk():
        if part.is_multipart():
            continue
        name = (part["Content-Location"] or "").split("/")[-1]
        data = part.get_payload(decode=True)
        if part.get_content_type() == "text/html":
            page = data.decode("utf-8")
        elif part.get_content_type().startswith("image/"):
            images[name] = base64.b64encode(data).decode()
    return page, images


def main():
    src = sys.argv[1]
    keep_claude = "--keep-claude" in sys.argv
    page, images = load_mht(src)
    body = page[page.index("<body"):page.index("</body>")]
    body = body[body.index(">") + 1:]
    tables = [m.start() for m in re.finditer(r"<table", body)]
    main_start = tables[2]
    main_end = body.index("</table>", main_start) + len("</table>")
    intro_html = clean(body[:main_start], images)
    # 去掉开头的页面标题/日期（页面上单独渲染），保留分类框架表 + 标注图例
    rows = []
    for tr in re.split(r"<tr[^>]*>", body[main_start:main_end])[1:]:
        tds = re.findall(r"<td([^>]*)>(.*?)</td>", tr, flags=re.S)
        if len(tds) < 2:
            continue
        (a0, c0), (_, c1) = tds[0], tds[1]
        bg = re.search(r"background-color:([^;']+)", a0)
        bg = bg.group(1).strip().lower() if bg else ""
        title_html, body_html = clean(c0, images), clean(c1, images)
        title = text_of(title_html).lstrip("★✳ ").strip()
        if not title and not text_of(body_html):
            continue
        kind = "l1" if bg == "#92d050" else "l2" if bg == "yellow" else "book"
        row = {"kind": kind, "title": title, "by": "user"}
        if kind == "book":
            row["titleHtml"] = title_html
            row["html"] = body_html
        rows.append(row)

    if keep_claude and OUT.exists():
        old = json.loads(OUT.read_text(encoding="utf-8"))["rows"]
        for i, r in enumerate(old):
            if r.get("by") != "claude":
                continue
            # 插回到原来前一行（按标题匹配）之后
            prev = next((old[j]["title"] for j in range(i - 1, -1, -1)), None)
            idx = next((k for k, x in enumerate(rows) if x["title"] == prev), len(rows) - 1)
            existing = next((k for k, x in enumerate(rows) if x["title"] == r["title"] and x["kind"] == "book"), None)
            if existing is not None:
                rows[existing] = r
            else:
                rows.insert(idx + 1, r)

    for r in rows:
        if r.get("html"):
            r["html"] = inline_p_background(r["html"])

    data = {
        "meta": {
            "title": "！总结--豆瓣所有书籍",
            "source": "OneNote「阅读与书评相关」分区",
            "created": "2023-12-11",
        },
        "introHtml": inline_p_background(intro_html),
        "rows": rows,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    books = [r for r in rows if r["kind"] == "book"]
    print(f"wrote {OUT}: {len(rows)} rows, {len(books)} books "
          f"({sum(1 for r in books if r['by'] == 'claude')} by claude)")


if __name__ == "__main__":
    main()
