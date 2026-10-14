"""Rendering delle lavagne dei tutorial (menu_tutorial_pics*): cancella il testo giapponese ripristinando la lavagna vuota
(Base_00), ridisegna titolo (a gesso), intestazione, riquadro grigio con le righe e le etichette sotto le icone.
Il testo piccolo usa i font del gioco già italianizzati (DF_kyougeki 13 px), quello grande Grandstander (ui_font).
Le due metà (_l 256 px, _r 64 px) vanno in work/img_it/_auto/<archivio>/<nome>_l|_r.png (build_images.py le ricodifica ETC1).
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
import ui_font

ROOT = os.path.join(os.path.dirname(__file__), '..')
PNG = os.path.join(ROOT, 'work', 'tut', 'png')
OUT = os.path.join(ROOT, 'work', 'img_it', '_auto')
_base = None
CHALK = (244, 244, 248)


def base():
    global _base
    if _base is None:
        _base = Image.open(os.path.join(PNG, 'Base_00.png')).convert('RGBA')
    return _base


def load(name):
    return Image.open(os.path.join(PNG, name + '.png')).convert('RGBA')


_wide = []


def erase(img, rect):
    """ripristina la lavagna vuota nel rettangolo (x0, y0, x1, y1); per le immagini più larghe di 320 px la texture è ripetuta"""
    if rect[2] > 320:
        if not _wide:
            w = Image.new('RGBA', (640, 256))
            b = base()
            w.paste(b, (0, 0))
            inner = b.crop((40, 0, 280, 256))                  # solo l'interno (senza la cornice) per riempire a destra
            for x in range(280, 640, 240):
                w.paste(inner, (x, 0))
            _wide.append(w)
        img.paste(_wide[0].crop(rect), rect[:2])
        return
    img.paste(base().crop(rect), rect[:2])


def sprite(img, win, thr=110):
    """ritaglia il disegno a gesso (pixel chiari) dentro `win` con alfa proporzionale alla luminosità"""
    c = img.crop(win).convert('RGB')
    a = np.asarray(c).astype(float).mean(2)
    m = a > thr
    import cv2
    n_, lab, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)))
    big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))             # solo il pezzo più grande (scarta frammenti di lettere)
    m = m & (lab == big)
    ys, xs = np.nonzero(m)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    sub = np.asarray(c)[max(0, y0 - 1):y1 + 1, max(0, x0 - 1):x1 + 1].astype(float)
    lum = sub.mean(2)
    alpha = np.clip((lum - 52) / (235 - 52), 0, 1)
    keep = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8))[max(0, y0 - 1):y1 + 1, max(0, x0 - 1):x1 + 1]
    alpha = alpha * keep
    out = np.zeros(sub.shape[:2] + (4,), np.uint8)
    out[..., :3] = 242
    out[..., 3] = (alpha * 255).astype(np.uint8)
    return Image.fromarray(out)


def chalk(s, px, weight='Medium', spacing=1, boost=1.25):
    """testo bianco a gesso con bordi morbidi (supercampionato 8x)"""
    S = ui_font.S
    f = ui_font._font(px, weight)
    l, t, r, b = f.getbbox(s)
    m = Image.new('L', (r - l + 4 * S + spacing * S * len(s), b - t + 4 * S), 0)
    d = ImageDraw.Draw(m)
    x = S - l
    for ch in s:
        d.text((x, S - t), ch, font=f, fill=255)
        x += f.getlength(ch) + spacing * S
    small = m.resize((m.width // S, m.height // S), Image.BOX)
    a = np.clip(np.asarray(small).astype(float) / 255 * boost, 0, 1)
    out = np.zeros(a.shape + (4,), np.uint8)
    out[..., :3] = CHALK
    out[..., 3] = (a * 255).astype(np.uint8)
    im = Image.fromarray(out)
    return im.crop(im.getbbox())


def pixel_text(s, px=13, spacing=1, dark=False):
    """testo piccolo coi font del gioco (maschera con bordi antialias), bianco"""
    m = ui_font.core_small(s, px, spacing)
    out = Image.new('RGBA', m.size, (30, 30, 40, 0) if dark else CHALK + (0,))
    out.putalpha(m)
    return out


def save(img, name, arch):
    d = os.path.join(OUT, arch)
    os.makedirs(d, exist_ok=True)
    img.crop((0, 0, 256, 256)).save(os.path.join(d, name + '_l.png'))
    img.crop((256, 0, 320, 256)).save(os.path.join(d, name + '_r.png'))


_orn = {}


def ornaments():
    """sprite dei due ornamenti del titolo grande (da Charm_09_1, titolo a una riga senza altro attorno)"""
    if not _orn:
        ref = load('Charm_09_1')
        _orn['L'] = sprite(ref, (34, 127, 71, 150))
        _orn['R'] = sprite(ref, (250, 127, 288, 150))
    return _orn['L'], _orn['R']


def title(img, lines, px=26, cx=160, cy=125):
    """titolo grande a gesso (1 o 2 righe) con i due ornamenti ai lati. Cancella la fascia centrale."""
    erase(img, (16, 92, 305, 168))
    while True:                                   # riduce il corpo finché titolo + ornamenti stanno in 270 px
        ims = [chalk(t, px) for t in lines]
        if max(i.width for i in ims) <= 220 or px <= 16:
            break
        px -= 2
    H = px + 1
    n = len(ims)
    total = H * n
    top = cy - total // 2 + (0 if n == 1 else 1)
    W = max(i.width for i in ims)
    for k, im in enumerate(ims):
        img.alpha_composite(im, (cx - im.width // 2, top + k * H + (H - im.height) // 2))
    lo, ro = ornaments()
    ocy = cy + 12 if n == 1 else cy + 2
    img.alpha_composite(lo, (cx - W // 2 - 3 - lo.width, ocy - lo.height // 2))
    img.alpha_composite(ro, (cx + W // 2 + 3, ocy - ro.height // 2))
    return img


BOX = (113, 113, 121)
_small = {}


def small_ornaments():
    """ornamenti piccoli = quelli grandi ridotti (i ritagli originali portavano frammenti di lettere)"""
    if not _small:
        L, R = ornaments()
        k = 0.8
        _small['L'] = L.resize((round(L.width * k), round(L.height * k)), Image.LANCZOS)
        _small['R'] = R.resize((round(R.width * k), round(R.height * k)), Image.LANCZOS)
    return _small['L'], _small['R']


def find_box(img):
    """rettangolo (x0, y0, x1, y1) del riquadro grigio (113,113,121) nella lavagna originale"""
    import cv2
    a = np.asarray(img.convert('RGB')).astype(int)
    m = ((np.abs(a - np.array(BOX)).max(2) <= 3)).astype(np.uint8)
    m[:, :14] = 0
    m[:, 306:] = 0
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    n_, lab, st, _ = cv2.connectedComponentsWithStats(m)
    if n_ < 2:
        return None
    i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    x, y, w, h, ar = st[i]
    return (int(x), int(y), int(x + w), int(y + h))


def find_boxes(img, minarea=1500):
    """tutti i riquadri grigi (x0, y0, x1, y1), dall'alto in basso"""
    import cv2
    a = np.asarray(img.convert('RGB')).astype(int)
    m = ((np.abs(a - np.array(BOX)).max(2) <= 3)).astype(np.uint8)
    m[:, :14] = 0
    m[:, 306:] = 0
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    n_, lab, st, _ = cv2.connectedComponentsWithStats(m)
    out = [(int(x), int(y), int(x + w), int(y + h)) for x, y, w, h, ar in st[1:] if ar >= minarea]
    return sorted(out, key=lambda b: b[1])


def header(img, box_top, title_text, sub_text, cx=160):
    """intestazione piccola: riga 1 = nome dell'incantesimo tra due ornamenti, riga 2 = sottotitolo"""
    erase(img, (30, box_top - 52, 292, box_top - 2))
    t = pixel_text(title_text, 13)
    s = pixel_text(sub_text, 13)
    c1 = box_top - 32
    c2 = box_top - 13
    img.alpha_composite(t, (cx - t.width // 2, c1 - t.height // 2))
    img.alpha_composite(s, (cx - s.width // 2, c2 - s.height // 2))
    lo, ro = small_ornaments()
    oc = c1 + 7
    img.alpha_composite(lo, (cx - t.width // 2 - 3 - lo.width, oc - lo.height // 2))
    img.alpha_composite(ro, (cx + t.width // 2 + 3, oc - ro.height // 2))


def rounded(img, rect, fill=BOX, r=5):
    ImageDraw.Draw(img).rounded_rectangle([rect[0], rect[1], rect[2] - 1, rect[3] - 1], radius=r, fill=fill + (255,))


def box_rows(img, top, rows, cx=160, row_h=17, pad=(10, 7), max_w=282, px=13):
    """riquadro grigio con righe (etichetta, valore); le etichette sono allineate in colonna, il valore va a capo se serve.
    Restituisce il rettangolo disegnato."""
    labs = [pixel_text(l, px) for l, _ in rows]
    lw = max(i.width for i in labs)
    vx = lw + 7
    avail = max_w - 2 * pad[0] - vx
    lines = []                              # (indice riga, immagine valore, 1 = prima riga del valore)
    for k, (_, v) in enumerate(rows):
        words = v.split(' ')
        cur = ''
        parts = []
        for w in words:
            trial = (cur + ' ' + w).strip()
            if pixel_text(trial, px).width <= avail or not cur:
                cur = trial
            else:
                parts.append(cur)
                cur = w
        parts.append(cur)
        for j, p in enumerate(parts):
            lines.append((k, pixel_text(p, px), j == 0))
    w = vx + max(i.width for _, i, _ in lines) + 2 * pad[0]
    h = len(lines) * row_h + 2 * pad[1] - 3
    x0 = cx - w // 2
    rect = (x0, top, x0 + w, top + h)
    rounded(img, rect)
    for n, (k, im, first) in enumerate(lines):
        y = top + pad[1] + n * row_h + 1
        if first:
            img.alpha_composite(labs[k], (x0 + pad[0], y + (px - labs[k].height) // 2 + 1))
        img.alpha_composite(im, (x0 + pad[0] + vx, y + (px - im.height) // 2 + 1))
    return rect


def icon_centers(img, box):
    """centri x delle icone (quadrati colorati) dentro il riquadro grigio di una lavagna-menu"""
    a = np.asarray(img.convert('RGB')).astype(int)
    band = a[box[1] + 8:box[1] + 34, box[0] + 4:box[2] - 4]
    diff = (np.abs(band - np.array(BOX)).max(2) > 40).sum(0) > 10
    runs, start = [], None
    for x, v in enumerate(list(diff) + [False]):
        if v and start is None:
            start = x
        elif not v and start is not None:
            runs.append((start, x - 1))
            start = None
    return [round((s + e) / 2) + box[0] + 4 for s, e in runs if e - s >= 20]


def menu_labels(img, labels, note=None, centers=None):
    """lavagna-menu: sostituisce le etichette sotto le icone (e la nota in basso, se c'è).
    labels = lista di etichette (un riquadro) oppure lista di liste (un elenco per riquadro, dall'alto)"""
    boxes = find_boxes(img)
    sets = labels if labels and isinstance(labels[0], list) else [labels]
    assert len(sets) <= len(boxes), (boxes, sets)
    boxes = boxes[:len(sets)] if len(sets) < len(boxes) else boxes
    d = ImageDraw.Draw(img)
    for box, lab in zip(boxes, sets):
        cs = centers if centers else icon_centers(img, box)
        assert len(cs) == len(lab), (cs, lab)
        ly0 = box[1] + 41
        d.rectangle([box[0] + 3, ly0, box[2] - 4, box[3] - 3], fill=BOX + (255,))
        pitch = min(b - a for a, b in zip(cs, cs[1:])) if len(cs) > 1 else 60
        for c, t in zip(cs, lab):
            px = 11
            while True:
                im = pixel_text(t, px)
                if im.width <= pitch or px <= 11:
                    break
                px -= 1
            img.alpha_composite(im, (c - im.width // 2, ly0 + (box[3] - 3 - ly0 - im.height) // 2))
    if note:
        box = boxes[-1]
        erase(img, (30, box[3] + 15, 300, 215))
        for k, line in enumerate(note):
            im = pixel_text(line, 13)
            img.alpha_composite(im, (96, box[3] + 24 + k * 15))
    return img
