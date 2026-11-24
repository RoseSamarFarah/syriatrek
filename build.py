#!/usr/bin/env python3
"""Build the Syria Trek page for production.

Reads src/index.html + src/img/ and writes an optimised copy to
docs/ (served by GitHub Pages):
  * every <img> becomes responsive WebP (srcset at several widths) with
    content-hashed filenames, so a replaced photo always gets a new URL and
    can never be served stale from a browser or CDN cache
  * the hero image is preloaded
  * HTML, CSS and JS are minified into the single index.html
  * img/preview.jpg (the WhatsApp / iMessage link preview) is copied under
    its fixed name so existing link previews keep working
"""
import hashlib, io, os, re, shutil, sys
from PIL import Image
import minify_html

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs')
WIDTHS = [400, 800, 1200, 1800]
QUALITY = 88  # WebP quality; high enough that photos look identical to the originals

# rendered width of each image slot, used for the sizes attribute
SIZES = {
    'gate':    '(orientation:portrait) 100vh, 100vw',
    'hero':    '(max-width:700px) 100vw, 1160px',
    'bleed':   '(max-width:700px) 100vw, 1160px',
    'pair':    '(max-width:700px) 100vw, 580px',
    'gallery': '(max-width:700px) 76vw, 270px',
    'press':   '(max-width:700px) 100vw, 280px',
    'mini':    '76px',
    'card':    '(max-width:700px) 100vw, 820px',
}

def slot_for(html, pos, src):
    before = html[max(0, pos - 400):pos]
    if 'id="gate"' in before[-200:]: return 'gate'
    if 'bleed hero' in before[-200:]: return 'hero'
    if 'g-item' in before[-80:]: return 'gallery'
    if 'class="pf"' in before[-120:]: return 'pair'
    if 'class="mini' in before[-300:] or 'class="thumb' in before[-60:]: return 'mini'
    if 'press' in before and '<a href' in before[-250:]: return 'press'
    if 'bleed' in before[-120:]: return 'bleed'
    return 'card'

GATE_WIDTHS = [800, 1200, 1800, 2400, 3200]
GATE_QUALITY = 92

def build_image(rel, cache, widths_set=None, quality=None):
    widths_set = widths_set or WIDTHS
    quality = quality or QUALITY
    if rel in cache: return cache[rel]
    path = os.path.join(SRC, rel)
    im = Image.open(path).convert('RGB')
    W, H = im.size
    widths = [w for w in widths_set if w < W] + [W]
    digest = hashlib.sha1(open(path, 'rb').read() + f'{quality}{widths_set}'.encode()).hexdigest()[:10]
    stem = rel[len('img/'):].rsplit('.', 1)[0].replace('/', '-')
    out = []
    for w in widths:
        h = round(H * w / W)
        r = im if w == W else im.resize((w, h), Image.LANCZOS)
        name = f'img/{stem}.{digest}.{w}.webp'
        r.save(os.path.join(OUT, name), 'WEBP', quality=quality, method=6)
        out.append((name, w))
    cache[rel] = (out, W, H)
    return cache[rel]

def main():
    html = open(os.path.join(SRC, 'index.html'), encoding='utf-8').read()
    if os.path.isdir(OUT):
        for f in os.listdir(OUT):
            p = os.path.join(OUT, f)
            if f in ('.nojekyll', 'CNAME'): continue
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    os.makedirs(os.path.join(OUT, 'img'), exist_ok=True)
    open(os.path.join(OUT, '.nojekyll'), 'w').close()
    shutil.copy(os.path.join(SRC, 'img', 'preview.jpg'), os.path.join(OUT, 'img', 'preview.jpg'))

    cache, hero = {}, None
    def repl(m):
        nonlocal hero
        tag = m.group(0)
        src = re.search(r'src="(img/[^"]+)"', tag).group(1)
        slot = slot_for(html, m.start(), src)
        variants, W, H = build_image(src, cache, *( (GATE_WIDTHS, GATE_QUALITY) if slot == 'gate' else () ))
        srcset = ', '.join(f'{n} {w}w' for n, w in variants)
        default = next((n for n, w in variants if w >= 800), variants[-1][0])
        new = re.sub(r'src="[^"]+"', f'src="{default}" srcset="{srcset}" sizes="{SIZES[slot]}"', tag)
        if slot == 'hero':
            hero = (srcset, SIZES[slot])
            new = re.sub(r'\sloading="lazy"', '', new)
        return new
    html = re.sub(r'<img\b[^>]*\bsrc="img/[^"]+"[^>]*>', repl, html)

    if hero:
        html = html.replace('</title>', f'</title>\n<link rel="preload" as="image" imagesrcset="{hero[0]}" imagesizes="{hero[1]}" fetchpriority="high">', 1)

    html = minify_html.minify(html, minify_css=True, minify_js=True, keep_closing_tags=True, keep_html_and_head_opening_tags=True)
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(html)

    total = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(OUT) for f in fs)
    print(f'built {len(cache)} images, index.html {len(html)//1024} KB, total {total/1e6:.1f} MB')

if __name__ == '__main__':
    main()
