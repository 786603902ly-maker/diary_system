#!/usr/bin/env python3
"""构建 book-os.html：把 data/book-os.json 内联进模板，生成自包含单文件读书网页。
用法：python3 src/build_books.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "book-os.json"
TEMPLATE_FILE = ROOT / "src" / "book_template.html"
OUT_FILE = ROOT / "book-os.html"


def main():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    template = TEMPLATE_FILE.read_text(encoding="utf-8")

    json_str = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    json_str = json_str.replace("</script>", "<\\/script>")

    out = template.replace("__BOOK_OS_DATA__", json_str)
    OUT_FILE.write_text(out, encoding="utf-8")
    distilled = sum(1 for b in data["books"] if b.get("status") != "queued")
    print(f"built {OUT_FILE} ({len(out)/1024:.1f} KB), books={len(data['books'])} (distilled/in-progress={distilled}), universalTruths={len(data['universalTruths'])}")


if __name__ == "__main__":
    main()
