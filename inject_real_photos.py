#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将真实照片分配进 101 篇文章：替换封面 + 正文注入 2 张实景照 + 补 CSS。"""
import os, re, glob, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
NEWS = os.path.join(ROOT, 'news')
COV = 'assets/covers'          # 相对站点根；文章在 news/ 下引用为 ../assets/covers/xxx.jpg

# ---------- 主题分类 ----------
THEME_KW = {
    'yulin': ['玉林', '玉林北', 'yulin'],
    'hengzhou': ['横州', 'hengzhou'],
    'xingye': ['兴业', 'xingye'],
    'airport': ['机场', 'airport'],
    'hospital': ['医院', '医疗', 'hospital'],
}
def theme_of(title):
    t = title.lower()
    for th, kws in THEME_KW.items():
        if any(k.lower() in t for k in kws):
            return th
    if any(k in title for k in ['高铁', '南玉', '南珠', '高铁站']):
        return 'highspeed'
    if any(k in title for k in ['品牌', '案例', '投放', '广告', '营销', 'roi', '数据']):
        return 'brand'
    return 'default'

# ---------- 封面池(已优化到 assets/covers/) ----------
def cov(name): return f"../{COV}/{name}.jpg"

yulin_pool = [cov(n) for n in [
    'yulin-exit-passage-1','yulin-exit-passage-2','yulin-hall-empty-1','yulin-hall-people-1',
    'yulin-hall-seats-1','yulin-hall-wide-1','yulin-hall-wide-2','yulin-hall-wide-3',
    'yulin-hospital-live-1','yulin-hospital-live-2','yulin-passage-ad-1','yulin-wall-ad-1',
    'yulin-wall-ad-2','yulin-unsorted-01','yulin-unsorted-02','yulin-unsorted-03',
    'yulin-unsorted-04','yulin-unsorted-05',
    'yulin-led-1','yulin-led-2','yulin-led-3','yulin-led-4',
    'yulin-screen-1','yulin-screen-2','yulin-screen-3','yulin-screen-4','yulin-screen-5','yulin-screen-6',
    'yulin-lightbox-1','yulin-lightbox-2',
    'yulin-billboard-a','yulin-billboard-a6','yulin-billboard-b',
    'yulin-hall-ad','yulin-station-led',
]]
hengzhou_pool = [cov(n) for n in ['hengzhou-exterior-1','hengzhou-hall-1','hengzhou-station-platform']] + yulin_pool
xingye_pool   = [cov(n) for n in ['xingye-exterior-1','xingye-station-hall','xingye-station-platform']] + yulin_pool
airport_pool  = [cov(n) for n in ['airport-ad-example','airport-screen-ad']] + yulin_pool
hospital_pool = [cov(n) for n in ['yulin-hospital-live-1','yulin-hospital-live-2']] + yulin_pool
all_pool      = list(dict.fromkeys(yulin_pool + hengzhou_pool + xingye_pool + airport_pool))  # 去重保序

POOLS = {
    'yulin': yulin_pool, 'hengzhou': hengzhou_pool, 'xingye': xingye_pool,
    'airport': airport_pool, 'hospital': hospital_pool,
    'highspeed': all_pool, 'brand': all_pool, 'default': all_pool,
}

# ---------- 图注 ----------
def caption(path):
    name = os.path.basename(path)[:-4]
    rules = [
        ('yulin-hall-wide', '玉林北站候车厅全景'), ('yulin-hall-people', '玉林北站候车厅实况'),
        ('yulin-hall-seats', '玉林北站候车区座位'), ('yulin-hall-empty', '玉林北站空镜'),
        ('yulin-hall-ad', '玉林北站候车厅广告'), ('yulin-exit-passage', '玉林北站出站通道'),
        ('yulin-passage-ad', '玉林北站通道广告位'), ('yulin-wall-ad', '玉林北站墙面广告'),
        ('yulin-hospital', '玉林站医疗健康实景'), ('yulin-unsorted', '玉林北站现场实景'),
        ('yulin-led', '玉林北站LED大屏'), ('yulin-screen', '玉林北站刷屏机'),
        ('yulin-lightbox', '玉林北站灯箱'), ('yulin-billboard', '玉林北站广告牌'),
        ('yulin-station-entrance', '玉林北站进站口'), ('yulin-station-led', '玉林北站LED屏'),
        ('hengzhou-exterior', '横州站外景'), ('hengzhou-hall', '横州站站厅'),
        ('hengzhou-station-platform', '横州站站台'), ('xingye-exterior', '兴业南站外景'),
        ('xingye-station-hall', '兴业南站站厅'), ('xingye-station-platform', '兴业南站站台'),
        ('airport-ad-example', '南宁机场广告位示例'), ('airport-screen-ad', '南宁机场刷屏机'),
    ]
    for key, cap in rules:
        if key in name:
            return cap
    return '联屏传媒实景案例'

FIG_CSS = """
.article-figure{margin:30px 0;text-align:center}
.article-figure img{width:100%;max-width:760px;margin:0 auto;display:block;border-radius:12px;box-shadow:0 10px 34px rgba(0,0,0,.28)}
.article-figure figcaption{margin-top:10px;font-size:13px;color:#9aa3b2;letter-spacing:.02em}
"""

def make_figure(path, idx):
    alt = caption(path)
    return (f'\n        <figure class="article-figure">\n'
            f'          <img src="{path}" alt="{alt}" loading="lazy">\n'
            f'          <figcaption>{alt}</figcaption>\n'
            f'        </figure>')

def assign(pool, i):
    return pool[i % len(pool)]

def process(html, theme, idx):
    # 1) 替换封面
    html = re.sub(
        r"(<div class=\"article-cover\"[^>]*style=\"background-image:\s*url\(')[^']+('\))",
        lambda m: m.group(1) + assign(POOLS[theme], idx) + m.group(2),
        html, count=1)
    # 2) 注入 2 张正文图：在第 2、第 5 个 </p> 之后(位于 footer 之前)
    footer_pos = html.find('<footer')
    if footer_pos == -1:
        footer_pos = html.find('class="site-footer"')
    if footer_pos == -1:
        footer_pos = len(html)
    body_region = html[:footer_pos]
    # 找 article-body 之后、footer 之前的 </p>
    body_start = body_region.find('<div class="article-body">')
    if body_start == -1:
        body_start = 0
    sub = body_region[body_start:]
    poses = [m.end() for m in re.finditer(r'</p>', sub)]
    # 选两个注入点
    pts = []
    if len(poses) >= 2:
        pts.append(poses[1])
    if len(poses) >= 5:
        pts.append(poses[4])
    elif len(poses) >= 3:
        pts.append(poses[-1])
    # 去重并按位置从后往前插，避免偏移错位
    pts = sorted(set(pts), reverse=True)
    cover = assign(POOLS[theme], idx)
    used = {cover}
    offset = 5
    new_sub = sub
    for p in pts:
        # 选一张与已用不同的图
        pic = cover
        while pic in used:
            offset += 1
            pic = assign(POOLS[theme], idx + offset)
        used.add(pic)
        new_sub = new_sub[:p] + make_figure(pic, idx) + new_sub[p:]
    html = html[:body_start] + new_sub + html[body_start + len(sub):]
    # 3) 补 CSS
    if '.article-figure' not in html:
        html = html.replace('</style>', FIG_CSS + '</style>', 1)
    return html

def main():
    test = '--test' in sys.argv
    files = sorted(glob.glob(os.path.join(NEWS, 'article*.html')))
    if test:
        files = [os.path.join(NEWS, 'article5.html')]
    theme_idx = {}   # 主题内轮询计数，保证同主题封面不撞车
    changed = 0
    for f in files:
        html = open(f, encoding='utf-8').read()
        title_m = re.search(r'<title>([^<]+)</title>', html)
        title = title_m.group(1) if title_m else ''
        theme = theme_of(title)
        idx = theme_idx.get(theme, 0)
        theme_idx[theme] = idx + 1
        new = process(html, theme, idx)
        if new != html:
            if not test:
                open(f, 'w', encoding='utf-8').write(new)
            changed += 1
        if test:
            # 输出关键区域供检视
            print("=== article5 theme:", theme, "===")
            m = re.search(r"article-cover[^>]*style=\"background-image:\s*url\('([^']+)'\)", new)
            print("cover ->", m.group(1) if m else 'NONE')
            print("figure 数量:", new.count('class="article-figure"'))
            for mm in re.finditer(r'<figure class="article-figure">.*?</figure>', new, re.S):
                print("  ", re.search(r'src="([^"]+)"', mm.group(0)).group(1))
    if not test:
        print(f"处理完成，更新 {changed} 篇")

if __name__ == '__main__':
    main()
