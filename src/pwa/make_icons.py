#!/usr/bin/env python3
"""生成 PWA 图标（PNG，Chrome 安装要求）：深松石绿底 + 四象限四个色点，与页面配色一致。
一次性运行、产物提交到 src/pwa/icons/（构建只复制，不依赖 Pillow）：
    python3 src/pwa/make_icons.py src/pwa/icons
maskable 版本内容收在中心 60% 安全区内，Android 自适应图标裁成圆形/圆角也不会切到。"""
from pathlib import Path
from PIL import Image, ImageDraw

BG = (47, 107, 87)          # --accent #2f6b57
QUADS = [(217, 154, 78), (127, 191, 163), (167, 155, 222), (214, 135, 135)]  # 深色主题下的四象限色，在深底上更亮
RING = (241, 243, 241)


def draw(size, safe):
    img = Image.new("RGBA", (size, size), BG + (255,))
    d = ImageDraw.Draw(img)
    c = size / 2
    span = size * safe            # 内容占用的边长
    gap = span * 0.08
    cell = (span - gap) / 2
    r = cell * 0.42
    x0 = c - span / 2
    for i, col in enumerate(QUADS):
        cx = x0 + (i % 2) * (cell + gap) + cell / 2
        cy = x0 + (i // 2) * (cell + gap) + cell / 2
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (255,))
    d.ellipse([c - span * 0.09, c - span * 0.09, c + span * 0.09, c + span * 0.09], fill=RING + (255,))
    return img


def main(out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for s in (192, 512):
        draw(s, 0.72).save(out / f"icon-{s}.png")
        draw(s, 0.56).save(out / f"icon-maskable-{s}.png")
    draw(180, 0.72).save(out / "apple-touch-icon.png")


if __name__ == "__main__":
    import sys
    main(sys.argv[1])
