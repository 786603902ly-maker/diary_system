#!/usr/bin/env python3
"""构建 index.html：把 data/mind-os.json + data/book-os.json 一起内联进模板，
生成自包含单文件网页（日记 Mind OS 与读书 Book OS 合并在同一个页面/同一个 Artifact 里）。
用法：python3 src/build.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIND_OS_FILE = ROOT / "data" / "mind-os.json"
BOOK_OS_FILE = ROOT / "data" / "book-os.json"
TEMPLATE_FILE = ROOT / "src" / "template.html"
OUT_FILE = ROOT / "index.html"


def inline_json(data):
    json_str = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    # 防止 </script> 提前结束内联脚本标签
    return json_str.replace("</script>", "<\\/script>")


def main():
    mind_os = json.loads(MIND_OS_FILE.read_text(encoding="utf-8"))
    book_os = json.loads(BOOK_OS_FILE.read_text(encoding="utf-8"))
    template = TEMPLATE_FILE.read_text(encoding="utf-8")

    out = template.replace("__MIND_OS_DATA__", inline_json(mind_os))
    out = out.replace("__BOOK_OS_DATA__", inline_json(book_os))
    OUT_FILE.write_text(out, encoding="utf-8")

    distilled = sum(1 for b in book_os["books"] if b.get("status") != "queued")
    print(
        f"built {OUT_FILE} ({len(out)/1024:.1f} KB) | "
        f"mind-os: principles={len(mind_os['principles'])}, lifeRecords={len(mind_os.get('lifeRecords', []))} | "
        f"book-os: books={len(book_os['books'])} (distilled/in-progress={distilled}), "
        f"universalTruths={len(book_os['universalTruths'])}"
    )


if __name__ == "__main__":
    main()
