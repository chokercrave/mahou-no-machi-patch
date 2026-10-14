"""Rivista Spell & Spill: sprite dei titoli (work/img/ui/menu_magazine_tex0/1/MGnn_*_obj*.png, 512x256 RGBA).
Trova le "unita'" di testo (componenti dell'alfa dopo una dilatazione) e le numera per leggere/tradurre."""
import os, sys
import numpy as np, cv2
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(__file__), '..')
SRC = {0: os.path.join(ROOT, 'work', 'img', 'ui', 'menu_magazine_tex0'), 1: os.path.join(ROOT, 'work', 'img', 'ui', 'menu_magazine_tex1')}


PAGE = {'t2n': 'menu_magpage_03', 'co1': 'menu_magpage_04', 'co2': 'menu_magpage_05'}      # numeri 53-56: sprite nelle pagine rivista
PAGE_PREFIX = '000.bin__timg_'


def folder(name):
    """(cartella sorgente, nome file, cartella _auto di uscita) per lo sprite `name`"""
    n = int(name[2:4])
    if n >= 57:
        d = 'menu_magpage_06'
    elif n >= 53:
        d = PAGE[name[5:8]]
    else:
        d = 'menu_magazine_tex0' if n <= 28 else 'menu_magazine_tex1'
    pre = PAGE_PREFIX if n >= 53 else ''
    return os.path.join(ROOT, 'work', 'img', 'ui', d), pre + name + '.png', d


def path(name):
    d, f, _ = folder(name)
    return os.path.join(d, f)


def blobs(name, gap=4, minarea=25):  # gap fisso a 4: gli id dei testi in mag_texts.py dipendono da questo
    im = Image.open(path(name)).convert('RGBA')
    a = np.asarray(im)[..., 3]
    m = (a > 40).astype(np.uint8)
    d = cv2.dilate(m, np.ones((2 * gap + 1, 2 * gap + 1), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(d)
    out = []
    for i in range(1, n):
        x, y, w, h, ar = st[i]
        if (m[lab == i]).sum() >= minarea:
            out.append(dict(id=0, bbox=(int(x), int(y), int(x + w), int(y + h)), label=i))
    out.sort(key=lambda b: (b['bbox'][1] // 40, b['bbox'][0]))
    for k, b in enumerate(out):
        b['id'] = k + 1
    return im, lab, out


def sheet(names, out='work/tut/prev.png', gap=4, cols=2):
    rows = (len(names) + cols - 1) // cols
    W, Hh = 512 * cols, 256 * rows
    c = Image.new('RGB', (W, Hh), (110, 110, 118))
    for i, nme in enumerate(names):
        im, lab, bl = blobs(nme, gap)
        bg = Image.new('RGBA', im.size, (110, 110, 118, 255))
        bg.alpha_composite(im)
        d = ImageDraw.Draw(bg)
        for b in bl:
            x0, y0, x1, y1 = b['bbox']
            d.rectangle((x0, y0, x1 - 1, y1 - 1), outline=(0, 255, 0))
            d.text((x0 + 1, max(0, y0 - 10)), str(b['id']), fill=(255, 255, 0))
        d.text((2, 2), nme, fill=(255, 255, 255))
        c.paste(bg.convert('RGB'), ((i % cols) * 512, (i // cols) * 256))
    c.save(os.path.join(ROOT, out))


def issue(nn):
    if nn >= 53:
        names = []
        for d in set(PAGE.values()) | {'menu_magpage_06'}:
            dd = os.path.join(ROOT, 'work', 'img', 'ui', d)
            names += [f[len(PAGE_PREFIX):-4] for f in os.listdir(dd) if f.startswith(f'{PAGE_PREFIX}MG{nn:02d}_') and ('obj' in f)]
        return sorted(names)
    names = sorted(f[:-4] for d in SRC.values() for f in os.listdir(d) if f.startswith(f'MG{nn:02d}_') and 'obj' in f)
    return names


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1].isdigit():
        sheet(issue(int(sys.argv[1])))
    else:
        sheet(sys.argv[1:])
