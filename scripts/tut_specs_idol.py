"""Lavagne idol_000..002 (spiegazione del karaoke al bar): menu 'Cosa fai?', lista canzoni imparate, etichetta del cursore.
idol_003..009 non hanno testo. Titoli delle canzoni come nella lista del gioco (m002: 265 Cottage, 88 Eroe stelle,
91 Hasta luego); キュートバルーン esiste solo qui -> "Cute Balloon" (stile dei titoli inglesi del gioco)."""
import os, sys
import cv2
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import tut_board as tb
import ui_font
from tut_specs_mydesign import put

ARCH = 'menu_tutorial_pics'
MENU = (60, 40, 20)            # voci del menu "Cosa fai?"
TITLE = (40, 56, 72)           # titoli nella lista delle canzoni


def put_clip(img, rect, y_clip, text, fill, px):
    """voce di menu tagliata dal bordo della lista: scrive il testo intero su una copia e ricopia solo le righe visibili"""
    tmp = img.copy()
    put(tmp, rect, text, fill, None, px, align='l')
    y0, y1 = y_clip
    img.paste(tmp.crop((rect[0] - 2, y0, rect[2], y1)), (rect[0] - 2, y0))


def erase(img, rect):
    """cancella il testo nel riquadro (differenza dal colore di fondo + inpaint), come put()"""
    x0, y0, x1, y1 = rect
    a = np.asarray(img.convert('RGB')).copy()
    reg = a[y0:y1, x0:x1].astype(int)
    bgc = np.median(reg.reshape(-1, 3), axis=0)
    mask = np.zeros(a.shape[:2], np.uint8)
    mask[y0:y1, x0:x1] = ((np.abs(reg - bgc).sum(2) > 60) * 255).astype(np.uint8)
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8))
    img.paste(Image.fromarray(cv2.inpaint(a, mask, 3, cv2.INPAINT_TELEA)).convert('RGBA'), (0, 0))


def tile_bg(img, x0, x1, y0, y1, src=212, per=40):
    """sfondo a rombi della lista canzoni (periodo 40 px): ricopia da [src, src+per) nella stessa riga, senza sfumature"""
    a = np.asarray(img).copy()
    for x in range(x0, x1):
        a[y0:y1, x] = a[y0:y1, src + (x - src) % per]
    img.paste(Image.fromarray(a), (0, 0))


def put_big(img, rect, text, fill, px_max, outline=(255, 255, 255), squeeze=1.0):
    """titolo con contorno (ui_font), centrato nel riquadro; squeeze < 1 stringe le lettere in orizzontale"""
    erase(img, rect)
    x0, y0, x1, y1 = rect
    im = ui_font.fit(text, fill, x1 - x0 + 6, y1 - y0 + 6, px_max=px_max, px_min=9, squeeze=squeeze,
                     outline=outline, ow=2.0, soft=0.8)
    img.alpha_composite(im, ((x0 + x1 - im.width) // 2, (y0 + y1 - im.height) // 2))


def main(only=None):
    def want(n):
        return not only or n in only

    if want('idol_000'):
        img = tb.load('idol_000')
        put(img, (196, 90, 258, 107), 'Cosa fai?', (255, 255, 255), None, 11)
        put(img, (206, 135, 262, 148), 'Canta', MENU, None, 11, align='l')
        put_clip(img, (206, 113, 262, 127), (116, 129), 'Fischietta', MENU, 11)    # voce in alto, tagliata
        put_clip(img, (206, 155, 262, 169), (154, 166), 'Esci', MENU, 11)          # voce in basso, tagliata
        tb.save(img, 'idol_000', ARCH)
        print('ok idol_000')
    if want('idol_001'):
        img = tb.load('idol_001')
        put_big(img, (100, 17, 220, 45), 'Canzoni imparate', (110, 25, 45), 24, squeeze=0.62)
        for (y0, y1), t in zip(((77, 91), (103, 117), (129, 143), (155, 169)),
                               ('Cottage', 'Eroe stelle', 'Hasta luego', 'Cute Balloon')):
            tile_bg(img, 94, 212, y0, y1)
            put(img, (94, y0, 214, y1), t, TITLE, None, 11, align='l')
        put(img, (100, 190, 174, 210), 'Canzoni imparate', (60, 40, 40), None, 10)
        tb.save(img, 'idol_001', ARCH)
        print('ok idol_001')
    if want('idol_002'):
        img = tb.load('idol_002')
        put_big(img, (112, 159, 206, 186), 'Cursore', (230, 40, 50), 22)
        tb.save(img, 'idol_002', ARCH)
        print('ok idol_002')


if __name__ == '__main__':
    main(sys.argv[1:] or None)
