"""Etichette delle pagine della rivista (menu_magpage_style_00..03): "<colore> per scegliere" (MG53/MG54) e stili di look (MG55/MG56),
nelle 4 varianti (t2n grande / co piccola). Si ridisegna tutta l'etichetta: parola grande con riempimento, contorno bianco interno e contorno
scuro esterno (come gli originali), coda piccola e tag "Risolto!". Uscita: work/img_it/_auto/menu_magpage_style_NN/<nome originale>.png
  python make_magpage_labels.py [--test]"""
import os, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(__file__), '..')
SRC = os.path.join(ROOT, 'work', 'img', 'ui')
OUT = os.path.join(ROOT, 'work', 'img_it', '_auto')
FONT = os.path.join(ROOT, 'tools', 'fonts', 'LilitaOne.ttf')
S = 4

COLORS = ['Grigio', 'Verde', 'Viola', 'Azzurro', 'Blu', 'Bianco', 'Nero', 'Marrone', 'Giallo', 'Arancione', 'Rosa', 'Rosso']
STYLES = ['Divisa', 'Magico', 'Elegante', 'Classico', 'Rock', 'Sportivo', 'Cool', 'Pop', 'Naturale', 'Carino']
FILL = {  # (alto, basso) del riempimento e contorno scuro, campionati dagli originali
    'Grigio': ((200, 200, 200), (140, 140, 140), (60, 70, 90)), 'Verde': ((90, 200, 40), (20, 130, 20), (20, 60, 40)),
    'Viola': ((200, 110, 255), (140, 40, 210), (50, 20, 90)), 'Azzurro': ((80, 230, 250), (0, 170, 220), (10, 70, 100)),
    'Blu': ((90, 150, 255), (20, 70, 230), (10, 30, 100)), 'Bianco': ((255, 255, 255), (235, 235, 245), (90, 90, 120)),
    'Nero': ((70, 70, 70), (0, 0, 0), (0, 0, 0)), 'Marrone': ((170, 100, 40), (100, 50, 10), (60, 20, 0)),
    'Giallo': ((255, 235, 60), (255, 170, 0), (120, 70, 0)), 'Arancione': ((255, 150, 30), (255, 90, 0), (110, 30, 0)),
    'Rosa': ((255, 130, 230), (255, 40, 190), (110, 0, 90)), 'Rosso': ((255, 80, 80), (220, 0, 0), (100, 0, 0)),
}
STYLE_FILL = ((140, 190, 255), (50, 100, 250), (15, 20, 110))


def font(px):
    return ImageFont.truetype(FONT, int(px * S))


def text_mask(txt, max_w, max_h, px_max=40):
    """maschera (supercampionata) del testo alla dimensione piu' grande che entra in max_w x max_h"""
    px = px_max
    while px > 5:
        f = font(px)
        l, t, r, b = f.getbbox(txt)
        if (r - l) <= max_w * S and (b - t) <= max_h * S:
            break
        px -= 0.5
    f = font(px)
    l, t, r, b = f.getbbox(txt)
    m = Image.new('L', (r - l + 4, b - t + 4), 0)
    ImageDraw.Draw(m).text((2 - l, 2 - t), txt, font=f, fill=255)
    return m


def layered(mask, top, bot, dark, ow=1.2, dw=1.3):
    """RGBA supercampionato: contorno scuro > contorno bianco > riempimento a sfumatura verticale + riflesso"""
    a = (np.asarray(mask) > 127).astype(np.uint8)
    pad = int((ow + dw + 2) * S)
    a = np.pad(a, pad)
    dist = cv2.distanceTransform(1 - a, cv2.DIST_L2, 5)
    h, w = a.shape
    out = np.zeros((h, w, 4), np.uint8)
    dk = dist <= (ow + dw) * S
    wh = dist <= ow * S
    out[dk] = (*dark, 255)
    out[wh] = (255, 255, 255, 255)
    ys = np.nonzero(a.any(1))[0]
    t = np.clip((np.arange(h) - ys.min()) / max(1, ys.max() - ys.min()), 0, 1)[:, None, None]
    grad = (np.array(top) * (1 - t) + np.array(bot) * t)
    gl = np.clip(1 - t / 0.5, 0, 1) * 0.28
    grad = grad * (1 - gl) + 255 * gl
    fill = np.broadcast_to(grad, (h, w, 3))
    out[a > 0, :3] = fill[a > 0].astype(np.uint8)
    out[a > 0, 3] = 255
    return Image.fromarray(out, 'RGBA')


def place(canvas, layer, cx, cy):
    lw, lh = max(1, round(layer.width / S)), max(1, round(layer.height / S))
    small = layer.resize((lw, lh), Image.LANCZOS)
    canvas.alpha_composite(small, (int(round(cx - lw / 2)), int(round(cy - lh / 2))))


def label(size, word, colors, box, tail=None, tag=None, look=None, style=False):
    """box = dict con centro e dimensioni massime di: word, tail, tag, look (x, y, w, h)"""
    cv = Image.new('RGBA', size, (0, 0, 0, 0))
    top, bot, dark = colors
    if 'tag' in box and tag:
        x, y, w, h = box['tag']
        place(cv, layered(text_mask(tag, w, h), (255, 230, 60), (255, 160, 0), (60, 30, 0), 0.9, 1.0), x, y)
    place(cv, layered(text_mask(word, box['word'][2], box['word'][3]), top, bot, dark), box['word'][0], box['word'][1])
    if tail and 'tail' in box:
        x, y, w, h = box['tail']
        place(cv, layered(text_mask(tail, w, h), (255, 255, 255), (230, 235, 255), (20, 50, 90), 0.8, 1.0), x, y)
    if look and 'look' in box:
        x, y, w, h = box['look']
        place(cv, layered(text_mask(look, w, h), (255, 255, 255), (225, 230, 255), (15, 20, 110), 0.8, 1.0), x, y)
    return cv


# layout (centro x, centro y, larghezza max, altezza max) per tipo di sprite
COLOR_BOX = {
    ('MG53', 't2n'): dict(word=(60, 50, 108, 28), tail=(86, 84, 84, 22)),
    ('MG53', 'co'): dict(word=(44, 20, 62, 18), tail=(58, 40, 56, 14)),
    ('MG54', 't2n'): dict(word=(63, 24, 116, 40)),
    ('MG54', 'co'): dict(word=(55, 22, 72, 26)),
}
STYLE_BOX = {
    ('MG55', 't2n'): dict(word=(108, 52, 92, 26), tag=(74, 30, 50, 16), look=(140, 74, 44, 15)),
    ('MG55', 'co'): dict(word=(62, 26, 84, 16), tag=(30, 9, 44, 10), look=(92, 43, 36, 10)),
    ('MG56', 't2n'): dict(word=(100, 29, 80, 44)),
    ('MG56', 'co'): dict(word=(56, 16, 74, 28)),
}


def sizes(d, name):
    return Image.open(os.path.join(SRC, d, name)).size


def main(test=False):
    done = 0
    out_root = os.path.join(ROOT, 'work', 'tut', 'magpage_test') if test else OUT
    for d in ('menu_magpage_style_00', 'menu_magpage_style_01', 'menu_magpage_style_02', 'menu_magpage_style_03'):
        os.makedirs(os.path.join(out_root, d), exist_ok=True)
        for f in sorted(os.listdir(os.path.join(SRC, d))):
            if not f.endswith('.png') or f.startswith('_') or '__timg_' not in f:
                continue
            base = f.split('__timg_')[1][:-4]                  # es. MG53_t2n_color_00
            mg, kind, what, nn = base.split('_')
            nn = int(nn)
            size = sizes(d, f)
            if what == 'color':
                word = COLORS[nn]
                colors = FILL[word]
                box = COLOR_BOX[(mg, kind)]
                im = label(size, word, colors, box, tail='Scegli!' if mg == 'MG53' else None)
            else:
                word = STYLES[nn]
                box = STYLE_BOX[(mg, kind)]
                im = label(size, word, STYLE_FILL, box, tag='Risolto!' if mg == 'MG55' else None, look='Look' if mg == 'MG55' else None, style=True)
            im.save(os.path.join(out_root, d, f))
            done += 1
    print(f'{done} etichette delle pagine rivista scritte in {os.path.relpath(out_root, ROOT)}')


if __name__ == '__main__':
    main('--test' in sys.argv)
