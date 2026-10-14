"""Lavagne photo_00..02 (schermate di gioco con fumetti): testi blu nei fumetti e scritte rosa sul fondo grigio.
Maschera dei pixel del testo originale -> inpainting -> nuovo testo colorato (font del gioco)."""
import os, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
import tut_board as tb, ui_font

ARCH = 'menu_tutorial_pics2'
BLUE = (8, 137, 213)
PINK = (236, 64, 160)


def blue_mask(a):
    return (a[..., 0] < 110) & (a[..., 1] < 190) & (a[..., 2] > 170)


def pink_mask(a):
    return (a[..., 0] > 200) & (a[..., 1] < 130) & (a[..., 2] > 130)


def swap(img, rect, lines, mask_fn, ink, px, fn_white=False):
    a = np.asarray(img.convert('RGB')).astype(int)
    x0, y0, x1, y1 = rect
    m = mask_fn(a[y0:y1, x0:x1])
    ys, xs = np.nonzero(m)
    if not len(xs):
        raise AssertionError(f'nessun testo in {rect}')
    bx0, by0, bx1, by1 = x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1
    if fn_white:                          # fumetto: sfondo bianco piatto
        ImageDraw.Draw(img).rectangle([bx0 - 3, by0 - 3, bx1 + 2, by1 + 2], fill=(255, 255, 255, 255))
    mm = np.zeros(a.shape[:2], np.uint8)
    mm[y0:y1, x0:x1][m] = 255
    if fn_white:
        mm[:] = 0
    mm = cv2.dilate(mm, np.ones((5, 5), np.uint8))
    out = cv2.inpaint(np.asarray(img.convert('RGB')).copy(), mm, 4, cv2.INPAINT_TELEA)
    img.paste(Image.fromarray(out).convert('RGBA'), (0, 0))
    cx, cy = (bx0 + bx1) // 2, (by0 + by1) // 2
    ims = []
    for t in lines:
        mk = ui_font.core_small(t, px, 0)
        if ink == PINK:                      # scritta rosa con contorno bianco, come l'originale
            from PIL import ImageFilter
            big = Image.new('L', (mk.width + 4, mk.height + 4), 0)
            big.paste(mk, (2, 2))
            ol = Image.new('RGBA', big.size, (255, 255, 255, 0))
            ol.putalpha(big.filter(ImageFilter.MaxFilter(3)))
            fg = Image.new('RGBA', big.size, ink + (0,))
            fg.putalpha(big)
            ol.alpha_composite(fg)
            ims.append(ol)
            continue
        im = Image.new('RGBA', mk.size, ink + (0,))
        im.putalpha(mk)
        ims.append(im)
    lh = max(i.height for i in ims) + 1
    top = cy - lh * len(ims) // 2
    for k, im in enumerate(ims):
        img.alpha_composite(im, (cx - im.width // 2, top + k * lh))


SPECS = {
    'photo_00': [((34, 24, 286, 50), ['Scegli la direzione del corpo~'], blue_mask, BLUE, 15, True)],
    'photo_01': [((34, 24, 286, 50), ['Ora scegli dove mettere i piedi?'], blue_mask, BLUE, 15, True),
                 ((60, 130, 300, 168), ['Tocca per scegliere la posa dei piedi!'], pink_mask, PINK, 12)],
    'photo_02': [((18, 24, 302, 50), ['Alla fine, fai una posa a tempo!'], blue_mask, BLUE, 15, True),
                 ((30, 134, 296, 174), ['Scorri lo schermo a tempo!'], pink_mask, PINK, 12)],
}


def main(only=None):
    for name, ops in SPECS.items():
        if only and name not in only:
            continue
        img = tb.load(name)
        for rect, lines, fn, ink, px, *w in ops:
            try:
                swap(img, rect, lines, fn, ink, px, bool(w))
            except Exception as e:
                print(f'  ! {name} {rect}: {type(e).__name__} {e}')
        tb.save(img, name, ARCH)
        print('ok', name)


if __name__ == '__main__':
    main(sys.argv[1:] or None)
