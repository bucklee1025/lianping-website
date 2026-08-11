#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将真实照片优化为轻量封面图，输出到 assets/covers/。"""
import os, glob, sys
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIRS = [
    os.path.join(ROOT, 'assets', 'station-photos'),   # 用户给的实景照 21 张
]
# 现有真实素材（也偏大，一起优化）
EXTRA = [
    'yulin-led-1.jpg','yulin-led-2.jpg','yulin-led-3.jpg','yulin-led-4.jpg',
    'yulin-screen-1.jpg','yulin-screen-2.jpg','yulin-screen-3.jpg','yulin-screen-4.jpg','yulin-screen-5.jpg','yulin-screen-6.jpg',
    'yulin-lightbox-1.jpg','yulin-lightbox-2.jpg',
    'yulin-billboard-a.jpg','yulin-billboard-a6.jpg','yulin-billboard-b.jpg',
    'yulin-hall-ad.jpg','yulin-station-entrance.jpg','yulin-station-led.jpg',
    'hengzhou-station-platform.jpg','xingye-station-hall.jpg','xingye-station-platform.jpg',
    'airport-ad-example.jpg','airport-screen-ad.png',
    'yulin-station-entrance.jpg',
]
OUT = os.path.join(ROOT, 'assets', 'covers')
os.makedirs(OUT, exist_ok=True)

MAX_W = 1280
QUALITY = 82

def optimize(src, dst):
    try:
        im = Image.open(src).convert('RGB')
    except Exception as e:
        print('  SKIP', src, e); return False
    w, h = im.size
    if w > MAX_W:
        ratio = MAX_W / w
        im = im.resize((MAX_W, max(1, int(h * ratio))), Image.LANCZOS)
    # 再限制高度，避免竖图过大
    if im.size[1] > 1280:
        ratio = 1280 / im.size[1]
        im = im.resize((max(1, int(im.size[0] * ratio)), 1280), Image.LANCZOS)
    im.save(dst, 'JPEG', quality=QUALITY, optimize=True, progressive=True)
    return True

def human(n):
    return f"{n/1024:.0f}KB" if n < 1024*1024 else f"{n/1024/1024:.1f}MB"

count = 0
for d in SRC_DIRS:
    for f in sorted(glob.glob(os.path.join(d, '*.jpg'))):
        base = os.path.splitext(os.path.basename(f))[0] + '.jpg'
        dst = os.path.join(OUT, base)
        before = os.path.getsize(f)
        if optimize(f, dst):
            after = os.path.getsize(dst)
            print(f"  {base:28} {human(before):>8} -> {human(after):>8}")
            count += 1

for name in EXTRA:
    src = os.path.join(ROOT, 'assets', name)
    if not os.path.exists(src):
        continue
    base = os.path.splitext(os.path.basename(name))[0] + '.jpg'
    dst = os.path.join(OUT, base)
    before = os.path.getsize(src)
    if optimize(src, dst):
        after = os.path.getsize(dst)
        print(f"  {base:28} {human(before):>8} -> {human(after):>8}")
        count += 1

print(f"\n优化完成，共 {count} 张 -> {OUT}")
print("封面目录文件数:", len(glob.glob(os.path.join(OUT, '*.jpg'))))
