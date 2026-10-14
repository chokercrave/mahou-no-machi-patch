"""Intestazioni di "Patente da mago" e "Licenza di vendita" (ui/menu_make_profile.tarc -> makeprofile.arc:
timg_makeprofile_hedder / timg_shopprofile_hedder, 256x32). Originale: scritta oro sottile (243,227,53) senza contorno
fra due ricci. Si tengono i ricci (colonne SWIRLS), si cancella il resto e si scrive il testo italiano in oro con
Grandstander antialias leggero, centrato fra i ricci.
Output: work/img_it/menu_make_profile/ (gruppo in build_images.py)"""
import os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import ui_font

ROOT = os.path.join(os.path.dirname(__file__), '..')
SRC = os.path.join(ROOT, 'work', 'img', 'ui', 'menu_make_profile')
OUT = os.path.join(ROOT, 'work', 'img_it', 'menu_make_profile')
GOLD = (243, 227, 53)
# nome texture -> (testo, colonne dei due ricci)
JOBS = {'makeprofile_hedder': ('Patente da mago', (40, 64), (191, 215)),
        'shopprofile_hedder': ('Licenza di vendita', (48, 72), (183, 207))}
CY = 16        # centro verticale della scritta (originale: righe 5-27)


def main():
    os.makedirs(OUT, exist_ok=True)
    ui_font.SMALL = 6
    for name, (text, l, r) in JOBS.items():
        fn = f'makeprofile.arc__timg_{name}.png'
        im = Image.open(os.path.join(SRC, fn)).convert('RGBA')
        px = im.load()
        for x in range(im.width):
            if l[0] <= x <= l[1] or r[0] <= x <= r[1]:
                continue
            for y in range(im.height):
                px[x, y] = (0, 0, 0, 0)
        maxw = r[0] - l[1] - 4
        t = ui_font.fit(text, GOLD, maxw, 22, px_max=17, px_min=10, squeeze=0.85, ow=0, spacing=1, weight='Medium')
        sz = ui_font.LAST_PX
        cx = (l[1] + r[0]) // 2
        im.alpha_composite(t, (cx - t.width // 2, CY - t.height // 2))
        im.save(os.path.join(OUT, fn))
        print(name, text, 'px', sz, t.size)


if __name__ == '__main__':
    main()
