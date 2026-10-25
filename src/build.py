#!/usr/bin/env python3
"""构建 index.html：把 data/mind-os.json + data/book-os.json 一起内联进模板，
生成自包含单文件网页（日记 Mind OS 与读书 Book OS 合并在同一个页面/同一个 Artifact 里）。

同时生成 site/：GitHub Pages 用的可安装版本（PWA）——同一份页面内容，额外加上
<!doctype>/<head>、manifest、图标和 service worker。Artifact 版不加这些，因为 Artifact
跑在 claude.ai 的 iframe 里，浏览器只看顶层页面的 manifest，加了也没用。
用法：python3 src/build.py
"""
import json
import shutil
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIND_OS_FILE = ROOT / "data" / "mind-os.json"
BOOK_OS_FILE = ROOT / "data" / "book-os.json"
TEMPLATE_FILE = ROOT / "src" / "template.html"
PWA_DIR = ROOT / "src" / "pwa"
OUT_FILE = ROOT / "index.html"
SITE_DIR = ROOT / "site"

PWA_HEAD = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#2f6b57">
<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="知识宇宙">
<script>
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function(){ navigator.serviceWorker.register('sw.js').catch(function(){}); });
  }
</script>
"""


def inline_json(data):
    json_str = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    # 防止 </script> 提前结束内联脚本标签
    return json_str.replace("</script>", "<\\/script>")


def build_site(page):
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    # 图标是 src/pwa/make_icons.py 一次性生成后提交进仓库的 PNG，构建时只复制，不依赖 Pillow
    shutil.copytree(PWA_DIR / "icons", SITE_DIR / "icons")
    # 页面内容里的 <title>/<meta>/<style> 紧跟在 <head> 里，遇到第一个 <div> 时浏览器自动进入 <body>
    (SITE_DIR / "index.html").write_text(PWA_HEAD + page + "\n</html>\n", encoding="utf-8")
    shutil.copy(PWA_DIR / "manifest.webmanifest", SITE_DIR / "manifest.webmanifest")
    sw = (PWA_DIR / "sw.js").read_text(encoding="utf-8").replace("__BUILD_ID__", str(int(time.time())))
    (SITE_DIR / "sw.js").write_text(sw, encoding="utf-8")
    (SITE_DIR / ".nojekyll").write_text("", encoding="utf-8")


def main():
    mind_os = json.loads(MIND_OS_FILE.read_text(encoding="utf-8"))
    book_os = json.loads(BOOK_OS_FILE.read_text(encoding="utf-8"))
    template = TEMPLATE_FILE.read_text(encoding="utf-8")

    out = template.replace("__MIND_OS_DATA__", inline_json(mind_os))
    out = out.replace("__BOOK_OS_DATA__", inline_json(book_os))
    OUT_FILE.write_text(out, encoding="utf-8")
    build_site(out)

    distilled = sum(1 for b in book_os["books"] if b.get("status") != "queued")
    print(
        f"built {OUT_FILE} ({len(out)/1024:.1f} KB) + {SITE_DIR}/ (PWA) | "
        f"mind-os: principles={len(mind_os['principles'])}, lifeRecords={len(mind_os.get('lifeRecords', []))} | "
        f"book-os: books={len(book_os['books'])} (distilled/in-progress={distilled}), "
        f"universalTruths={len(book_os['universalTruths'])}"
    )


if __name__ == "__main__":
    main()
