"""Sfondi/pagine della rivista in menu_magazine_tex2 (168 BCLIM 512x256 ecc.): logo "Berry's" -> "Spell & Spill" (stessa resa degli sfondi
MGnn: make_magazine_bg.draw) e testi giapponesi riscritti. Uscita: work/img_it/_auto/menu_magazine_tex2/<nnn>.png (chiave build_images: '<nnn>.bclim').
  python make_magazine_pages.py [--test] [id ...]     --test scrive in work/tut/pages_test"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image
import make_magazine_bg as mbg

ROOT = os.path.join(os.path.dirname(__file__), '..')
SRC = os.path.join(ROOT, 'work', 'img', 'ui', 'menu_magazine_tex2')
OUT = os.path.join(ROOT, 'work', 'img_it', '_auto', 'menu_magazine_tex2')

# riquadro del vecchio logo (x0, y0, x1, y1), misurato a occhio sulle griglie
LOGO = {
    2: (200, 12, 448, 118), 5: (14, 10, 262, 104), 8: (64, 8, 326, 104),
    123: (208, 6, 420, 100), 124: (210, 6, 420, 98), 125: (210, 8, 418, 100), 126: (214, 10, 416, 88), 127: (212, 8, 418, 98),
    128: (210, 8, 418, 96), 129: (206, 8, 420, 100), 130: (210, 6, 418, 98), 131: (210, 8, 418, 96), 132: (210, 6, 420, 100),
    133: (214, 8, 422, 100), 134: (210, 8, 418, 94),
    158: (44, 10, 330, 104), 159: (150, 10, 436, 104), 160: (44, 10, 330, 104), 161: (72, 10, 330, 108), 162: (84, 8, 410, 104),
}


PREVIEW_Y1 = {134: 126}      # bordo basso della zona da cancellare (default 114; 134 = neon rosso piu' basso)
PREVIEW = range(123, 135)      # pagine "次号予告" (anteprima del prossimo numero): la scritta rossa sta sul cartoncino bianco sotto il logo


def logo_page(i, img):
    n = 1000 + i
    mbg.BOX[n] = LOGO[i]
    if i in PREVIEW:            # 次号予告 scende fino a y~110 anche dove il logo finisce prima: si cancella fin li'
        mbg.EXTRA[n] = (0, 0, 0, max(0, PREVIEW_Y1.get(i, 114) - LOGO[i][3] - 8))
    img = mbg.draw(n, img)
    if i in PREVIEW:
        # "Prossimo numero" al posto di 次号予告 (cancellato con il logo): rosso con bordo bianco, sotto il nuovo logo
        import mag_render as mr
        x0, y0, x1, y1 = LOGO[i]
        lay = mr.text_layer(['Prossimo numero'], 15, 'Chewy', (220, 44, 56), (170, 18, 34), (255, 255, 255), 2, shadow=False)
        lay = lay.crop(lay.getbbox())
        img.alpha_composite(lay, ((x0 + x1) // 2 + 6 - lay.width // 2, y1 - 6))
    return img


def main(test, only):
    od = os.path.join(ROOT, 'work', 'tut', 'pages_test') if test else OUT
    os.makedirs(od, exist_ok=True)
    done = 0
    for i in LOGO:
        if only and i not in only:
            continue
        img = Image.open(os.path.join(SRC, f'{i:03d}.png')).convert('RGBA')
        img = logo_page(i, img)
        img.save(os.path.join(od, f'{i:03d}.png'))
        done += 1
    print(f'{done} pagine della rivista (tex2) scritte in {os.path.relpath(od, ROOT)}')


if __name__ == '__main__':
    a = sys.argv[1:]
    main('--test' in a, [int(x) for x in a if x.isdigit()])
