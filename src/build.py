#!/usr/bin/env python3
"""构建 index.html：把 data/mind-os.json 内联进模板，生成自包含单文件网页。
用法：python3 src/build.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "mind-os.json"
TEMPLATE_FILE = ROOT / "src" / "template.html"
OUT_FILE = ROOT / "index.html"


def main():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    template = TEMPLATE_FILE.read_text(encoding="utf-8")

    json_str = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    # 防止 </script> 提前结束内联脚本标签
    json_str = json_str.replace("</script>", "<\\/script>")

    out = template.replace("__MIND_OS_DATA__", json_str)
    OUT_FILE.write_text(out, encoding="utf-8")
    print(f"built {OUT_FILE} ({len(out)/1024:.1f} KB), principles={len(data['principles'])}, lifeRecords={len(data.get('lifeRecords', []))}")


if __name__ == "__main__":
    main()
