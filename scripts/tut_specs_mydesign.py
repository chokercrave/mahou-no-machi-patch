"""Lavagne mydesign_00..08 e mydesign_photo_00..02 (schermate dell'editor di disegni): pulsanti Fronte/Retro e testi.
Il rettangolo del testo originale si ricostruisce per inpainting dai bordi (sfondi lisci) e si scrive il testo col font del gioco."""
import os, sys
import numpy as np
import cv2
from PIL import Image, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
import tut_board as tb, ui_font

ARCH = 'menu_tutorial_pics2'
PINK, BLUE, WHITE = (240, 110, 175), (30, 70, 130), (255, 255, 255)


def put(img, rect, text, fill, outline=None, px=10, align='c', grow=1):
    x0, y0, x1, y1 = rect
    a = np.asarray(img.convert('RGB')).copy()
    reg = a[y0:y1, x0:x1].astype(int)
    bgc = np.median(reg.reshape(-1, 3), axis=0)
    mask = np.zeros(a.shape[:2], np.uint8)
    mask[y0:y1, x0:x1] = ((np.abs(reg - bgc).sum(2) > 60) * 255).astype(np.uint8)
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8))
    out = cv2.inpaint(a, mask, 3, cv2.INPAINT_TELEA)
    img.paste(Image.fromarray(out).convert('RGBA'), (0, 0))
    lines = text if isinstance(text, list) else [text]
    ims = []
    for t in lines:
        mk = ui_font.core_small(t, px, 0)
        big = Image.new('L', (mk.width + 4, mk.height + 4), 0)
        big.paste(mk, (2, 2))
        layer = Image.new('RGBA', big.size, (0, 0, 0, 0))
        if outline:
            ol = Image.new('RGBA', big.size, outline + (0,))
            ol.putalpha(big.filter(ImageFilter.MaxFilter(3)))
            layer.alpha_composite(ol)
        fg = Image.new('RGBA', big.size, fill + (0,))
        fg.putalpha(big)
        layer.alpha_composite(fg)
        ims.append(layer)
    lh = max(i.height for i in ims) - 2
    cy = (y0 + y1) // 2
    top = cy - (lh * len(ims) + 2) // 2
    for k, im in enumerate(ims):
        x = (x0 + x1) // 2 - im.width // 2 if align == 'c' else x0
        img.alpha_composite(im, (x, top + k * lh))


# posizioni di Fronte/Retro nelle schermate dell'editor (testo giapponese: rettangoli)
PILL = {(52, 226, 80, 240): 'Fronte', (104, 226, 142, 240): 'Retro'}


def pills(img, mae, ushiro):
    put(img, mae, 'Fronte', PINK, (255, 255, 255), 9)
    put(img, ushiro, 'Retro', BLUE, (210, 245, 255), 9)


def main(only=None):
    for k in range(9):
        name = f'mydesign_{k:02d}'
        if only and name not in only:
            continue
        img = tb.load(name)
        pills(img, (54, 227, 92, 240), (108, 227, 152, 240))
        tb.save(img, name, ARCH)
        print('ok', name)
    # photo_00: bottoni grandi e barra di testo
    name = 'mydesign_photo_00'
    if not only or name in only:
        img = tb.load(name)
        put(img, (35, 20, 78, 41), 'Foto', (255, 200, 230), (230, 90, 160), 13)
        put(img, (130, 18, 190, 38), 'Album', WHITE, (60, 80, 170), 13)
        put(img, (238, 17, 293, 38), 'Ritocca', WHITE, (60, 80, 170), 13)
        put(img, (131, 133, 189, 153), 'Fine', WHITE, (60, 80, 170), 13)
        put(img, (14, 100, 306, 117), "Scatta una foto da applicare all'abito", WHITE, None, 11)
        pills(img, (48, 227, 84, 240), (104, 227, 140, 240))
        tb.save(img, name, ARCH)
        print('ok', name)
    name = 'mydesign_photo_01'
    if not only or name in only:
        img = tb.load(name)
        put(img, (84, 81, 224, 113), ['Verr\u00e0 mostrata la foto', 'che hai scattato, miao!'], (110, 50, 40), None, 11)
        put(img, (47, 227, 106, 240), 'Usala', PINK, (255, 255, 255), 9)
        put(img, (138, 227, 182, 240), 'Salva', BLUE, (210, 245, 255), 9)
        put(img, (212, 227, 276, 240), 'Rifai', BLUE, (210, 245, 255), 9)
        tb.save(img, name, ARCH)
        print('ok', name)
    name = 'mydesign_photo_02'
    if not only or name in only:
        img = tb.load(name)
        put(img, (250, 21, 296, 39), 'Stampa', WHITE, (20, 110, 40), 11)
        pills(img, (56, 227, 92, 240), (112, 227, 152, 240))
        tb.save(img, name, ARCH)
        print('ok', name)


if __name__ == '__main__':
    main(sys.argv[1:] or None)
