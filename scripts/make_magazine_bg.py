"""Sfondi della rivista (MGnn_t2n_bg1): il logo "Berry's" e' dipinto nello sfondo, uno per numero, stesso disegno in colori diversi.
Si copre con una targa inclinata nei colori dell'originale (colore campionato dal logo) col testo "Spell & Spill" in due righe.
Uscita: work/img_it/_auto/menu_magazine_tex0|1/MGnn_t2n_bg1.png (dopo gen_labels, che svuota _auto).
  python make_magazine_bg.py [numeri]"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import colorsys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import mag_render as mr

ROOT = os.path.join(os.path.dirname(__file__), '..')
SRC = os.path.join(ROOT, 'work', 'img', 'ui')
OUT = os.path.join(ROOT, 'work', 'img_it', '_auto')

# riquadro del logo originale (x0, y0, x1, y1) in coordinate sprite 512x256, misurato a occhio sui fogli
BOX = {
    1: (60, 6, 304, 96), 2: (180, 14, 436, 120), 3: (72, 4, 326, 94), 4: (66, 2, 326, 92), 5: (186, 12, 444, 102),
    6: (60, 10, 318, 104), 7: (66, 4, 330, 106), 8: (64, 8, 326, 116), 9: (64, 8, 306, 100), 10: (66, 4, 326, 106),
    11: (64, 8, 326, 116), 12: (66, 6, 326, 104), 13: (186, 12, 446, 116), 14: (64, 8, 324, 114), 15: (62, 8, 328, 116),
    16: (60, 8, 328, 116), 17: (186, 10, 446, 106), 18: (200, 6, 438, 112), 19: (62, 10, 326, 116), 20: (74, 8, 328, 118),
    21: (62, 8, 326, 112), 22: (60, 8, 324, 128), 23: (62, 12, 324, 118), 24: (62, 8, 324, 126), 25: (58, 6, 310, 118),
    26: (200, 6, 438, 110), 27: (62, 8, 324, 124), 28: (60, 10, 322, 118), 29: (186, 10, 446, 122), 30: (64, 6, 324, 118),
    31: (60, 12, 320, 116), 32: (210, 8, 468, 116), 33: (60, 6, 306, 110), 34: (64, 6, 320, 114), 35: (200, 10, 446, 124),
    36: (60, 6, 324, 114), 37: (62, 8, 314, 114), 38: (64, 8, 324, 114), 39: (190, 8, 446, 122), 40: (64, 8, 324, 116),
    41: (62, 8, 308, 108), 42: (68, 4, 324, 108), 43: (62, 8, 314, 118), 44: (64, 8, 324, 122), 45: (62, 8, 314, 118),
    46: (198, 8, 444, 118), 47: (62, 8, 314, 116), 48: (192, 8, 448, 122), 49: (190, 8, 450, 120), 50: (58, 6, 316, 114),
    51: (100, 8, 350, 100), 52: (64, 8, 320, 114), 53: (60, 12, 320, 122),
}
SS = 4
KIND = {27: 'A'}      # correzione manuale del tipo (A = lettere bianche e contorno con la texture) dove la classificazione automatica sbaglia
KINDS = {}
EXTRA = {5: (14, 0, 6, 22), 9: (14, 0, 6, 22), 10: (14, 0, 6, 22), 20: (10, 0, 10, 14)}   # margini in piu' (sx, su, dx, giu') dove restano pezzi del vecchio logo


def dominant(img, box):
    """colore del logo: media dei pixel piu' saturi e non chiari/scuri nella parte centrale del riquadro"""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    reg = np.asarray(img.convert('RGB').crop((x0 + w // 5, y0 + h // 4, x1 - w // 5, y1 - h // 4))).reshape(-1, 3) / 255.0
    hsv = np.array([colorsys.rgb_to_hsv(*p) for p in reg[::3]])
    sel = hsv[(hsv[:, 1] > 0.35) & (hsv[:, 2] > 0.35)]
    if len(sel) < 20:
        sel = hsv
    sel = sel[np.argsort(-sel[:, 1])][:max(20, len(sel) // 3)]
    hh = np.arctan2(np.sin(sel[:, 0] * 6.2832).mean(), np.cos(sel[:, 0] * 6.2832).mean()) / 6.2832 % 1
    return hh, float(sel[:, 1].mean()), float(sel[:, 2].mean())


def rgb(h, s, v):
    return tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h % 1, max(0, min(1, s)), max(0, min(1, v))))


def plate(w, h, col):
    """targa inclinata col colore del logo: bordo bianco, corpo sfumato, riflesso in alto"""
    hh, s, v = col
    s = max(s, 0.45)
    top, bot, dark = rgb(hh, s * 0.7, 1.0), rgb(hh, s, max(0.55, v * 0.8)), rgb(hh, min(1, s + 0.2), 0.35)
    W, H = w * SS, h * SS
    pad = 8 * SS
    shape = Image.new('L', (W, H), 0)
    r = int(min(W, H) * 0.32)
    ImageDraw.Draw(shape).rounded_rectangle((pad, pad, W - pad, H - pad), r, fill=255)
    def shear(im):
        return im.transform(im.size, Image.AFFINE, (1, 0.14, -0.07 * H, 0, 1, 0), Image.BICUBIC)
    shape = shear(shape)
    white = shape.filter(ImageFilter.MaxFilter(2 * 3 * SS + 1))
    edge = white.filter(ImageFilter.MaxFilter(2 * 1 * SS + 1))
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    out.paste(Image.new('RGBA', (W, H), dark + (255,)), (0, 0), edge)
    out.paste(Image.new('RGBA', (W, H), (255, 255, 255, 255)), (0, 0), white)
    body = Image.new('RGBA', (W, H))
    px = np.zeros((H, W, 4), np.uint8)
    t = np.linspace(0, 1, H)[:, None, None]
    px[..., :3] = (np.array(top) * (1 - t) + np.array(bot) * t).astype(np.uint8)
    px[..., 3] = 255
    body = Image.fromarray(px)
    out.paste(body, (0, 0), shape)
    gloss = Image.new('L', (W, H), 0)
    ImageDraw.Draw(gloss).rounded_rectangle((pad + 6 * SS, pad + 4 * SS, W - pad - 6 * SS, H * 0.42), int(r * 0.7), fill=70)
    gloss = shear(gloss)
    out.paste(Image.new('RGBA', (W, H), (255, 255, 255, 255)), (0, 0), Image.fromarray(np.minimum(np.asarray(gloss), np.asarray(shape))))
    return out.resize((w, h), Image.LANCZOS), dark, bot


LOGO = os.path.join(OUT, 'menu_magazine', "000.bin__timg_berry's_logo.png")


def tinted_logo(col):
    """il logo Spell & Spill gia' fatto (rosa, contorno bianco) con la tinta del logo originale dello sfondo"""
    lg = Image.open(LOGO).convert('RGBA')
    lg = lg.crop(lg.getbbox())
    a = np.asarray(lg).astype(np.float32)
    hh, s, v = col
    hsv = np.array([colorsys.rgb_to_hsv(*(p / 255.0)) for p in a.reshape(-1, 4)[:, :3]]).reshape(a.shape[0], a.shape[1], 3)
    pink = (hsv[..., 1] > 0.35) & (hsv[..., 2] > 0.4)            # il riempimento rosa, non il contorno bianco/grigio
    if s > 0.3:
        hsv[..., 0] = np.where(pink, hh, hsv[..., 0])
    rgbn = np.array([colorsys.hsv_to_rgb(*p) for p in hsv.reshape(-1, 3)]).reshape(a.shape[0], a.shape[1], 3) * 255
    a[..., :3] = rgbn
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


ART = (36, 8, 476, 248)      # l'immagine occupa 440x240 al centro dello sprite 512x256 (il resto e' nero)


FONT = os.path.join(ROOT, 'tools', 'fonts', 'Lobster.ttf')       # lo stesso font del logo
S4 = 4


def soft_fill(img, hole):
    """riempie il buco con la media pesata dei pixel noti attorno (convoluzione normalizzata a scale crescenti): niente raggi/strisce come
    nell'inpainting, solo un colore morbido continuo coi dintorni"""
    import cv2
    f = img.astype(np.float32)
    known = (~hole).astype(np.float32)
    out = f.copy()
    left = hole.copy()
    for sig in (3, 6, 12, 24, 48):
        num = cv2.GaussianBlur(f * known[..., None], (0, 0), sig)
        den = cv2.GaussianBlur(known, (0, 0), sig)
        ok = left & (den > 0.12)
        out[ok] = num[ok] / den[ok][:, None]
        left &= ~ok
    return np.clip(out, 0, 255).astype(np.uint8)


def silhouette(arr, box):
    """sagoma del vecchio logo: il contorno bianco spesso e il riempimento che racchiude (chiusura + riempimento dei buchi).
    Restituisce (sagoma, sagoma dilatata per la cancellazione)"""
    import cv2
    x0, y0, x1, y1 = box
    ax0, ay0, ax1, ay1 = ART
    sub = arr[y0:y1, x0:x1].astype(int)
    white = (sub.min(2) > 215).astype(np.uint8) * 255
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13))
    cl = cv2.morphologyEx(white, cv2.MORPH_CLOSE, k)
    cnts, _ = cv2.findContours(cl, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = np.zeros_like(cl)
    for c in cnts:
        if cv2.contourArea(c) > 400:
            cv2.drawContours(out, [c], -1, 255, -1)
    m = np.zeros(arr.shape[:2], np.uint8)
    m[y0:y1, x0:x1] = out
    m[:ay0] = 0; m[ay1:] = 0; m[:, :ax0] = 0; m[:, ax1:] = 0
    if m.sum() / 255 < 0.35 * (x1 - x0) * (y1 - y0):        # contorno colorato: si cancella l'ellisse del riquadro
        m[:] = 0
        cv2.ellipse(m, ((x0 + x1) // 2, (y0 + y1) // 2), ((x1 - x0) // 2 - 4, (y1 - y0) // 2 - 3), 0, 0, 360, 255, -1)
        m[:ay0] = 0; m[ay1:] = 0; m[:, :ax0] = 0; m[:, ax1:] = 0
    d = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    d[:ay0] = 0; d[ay1:] = 0; d[:, :ax0] = 0; d[:, ax1:] = 0
    return m, d


def texture(arr, sil, region, col):
    """texture del riempimento del vecchio logo (glitter, jeans, pois, sfumature...): i pixel di riempimento (dentro la sagoma, lontani
    dal contorno bianco) vengono estesi a tutta la regione per inpainting"""
    import cv2
    rx0, ry0, rx1, ry1 = region
    crop = np.ascontiguousarray(arr[ry0:ry1, rx0:rx1])
    m = sil[ry0:ry1, rx0:rx1]
    er = cv2.erode(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
    fill = (er > 0) & (crop.min(2) < 228)
    if fill.sum() < 300:
        hh, s, v = col
        flat = np.array(rgb(hh, max(s, 0.5), max(v, 0.7)), np.uint8)
        return np.broadcast_to(flat, crop.shape).copy()
    # il disegno della texture (fiori, glitter, pois) si conserva: si ritaglia il riquadro del riempimento originale, si ripara solo fra le lettere
    # e lo si estende a specchio (simmetrico) fin dove serve: niente sbavature da inpainting su grandi aree
    ys, xs = np.nonzero(fill)
    by0, by1, bx0, bx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    tile = np.ascontiguousarray(crop[by0:by1, bx0:bx1])
    hole = (~fill[by0:by1, bx0:bx1]).astype(np.uint8) * 255
    tile = cv2.inpaint(tile, hole, 5, cv2.INPAINT_TELEA)
    rh, rw = crop.shape[:2]
    return np.pad(tile, ((by0, rh - by1), (bx0, rw - bx1), (0, 0)), mode='symmetric')


def logo_layer(bw, bh, kind, angle=8):
    """"Spell &" / "Spill" sfalsate in diagonale (come l'originale), col font del logo scelto.
    kind 'B': lettere con la texture, bordo sottile, banda bianca, bordo esterno colorato;
    kind 'A': lettere bianche, contorno spesso con la texture, bordo bianco sottile, filo scuro.
    Restituisce la maschera delle lettere e la mappa delle distanze (px) dalle lettere."""
    import cv2
    rout = 8.5 if kind == 'B' else 11.5
    f1, f2 = 64 * S4, 72 * S4
    lay = Image.new('L', (640 * S4, 300 * S4), 0)
    d = ImageDraw.Draw(lay)
    y = 10 * S4
    x2 = None
    for i, (t, fs) in enumerate((('Spell &', f1), ('Spill', f2))):
        ft = ImageFont.truetype(FONT, fs)
        l, tp, r, bt = ft.getbbox(t)
        if i == 0:
            x = 14 * S4 - l
            x2 = 14 * S4 + int((r - l) * 0.86)          # la seconda riga parte oltre meta' della prima: diagonale larga come l'originale
        else:
            x = x2 - l
        d.text((x, y - tp), t, font=ft, fill=255)
        y += (bt - tp) - 18 * S4
    lay = lay.crop(lay.getbbox())
    lay = lay.rotate(angle, resample=Image.BICUBIC, expand=True)
    lay = lay.crop(lay.getbbox())
    k = min((bw - 2 * rout) / (lay.width / S4), (bh - 2 * rout) / (lay.height / S4))
    m = lay.resize((max(1, round(lay.width / S4 * k)), max(1, round(lay.height / S4 * k))), Image.LANCZOS)
    pad = 20
    M = Image.new('L', (m.width + 2 * pad, m.height + 2 * pad), 0)
    M.paste(m, (pad, pad))
    ink = np.asarray(M) > 127
    dist = cv2.distanceTransform((~ink).astype(np.uint8), cv2.DIST_L2, 5)
    return ink, dist


def classify(arr, sil):
    """'A' se il cuore del vecchio logo e' bianco (lettere bianche, texture nel contorno), 'B' se e' colorato"""
    import cv2
    if sil.sum() < 2000 * 255:
        return 'B'
    dist = cv2.distanceTransform((sil > 0).astype(np.uint8), cv2.DIST_L2, 5)
    deep = dist >= 9
    if deep.sum() < 200:
        return 'B'
    white = arr[deep].min(1) > 222
    return 'A' if white.mean() > 0.5 else 'B'


def draw(n, img):
    import cv2
    box = BOX[n]
    col = dominant(img, box)
    ax0, ay0, ax1, ay1 = ART
    big = (max(ax0, box[0] - 12), max(ay0, box[1] - 12), min(ax1, box[2] + 14), min(ay1, box[3] + 14))
    arr = np.asarray(img.convert('RGB')).copy()
    sil, sil_d = silhouette(arr, big)
    bw, bh = box[2] - box[0], box[3] - box[1]
    cx, cy = (box[0] + box[2]) // 2, (box[1] + box[3]) // 2
    ys_, xs_ = np.nonzero(sil)
    if len(xs_) > 0.35 * bw * bh:                      # la sagoma misurata e' piu' precisa del riquadro a occhio
        sx0, sx1, sy0, sy1 = xs_.min(), xs_.max(), ys_.min(), ys_.max()
        bw, bh = int(sx1 - sx0 + 1), int(sy1 - sy0 + 1)
        cx, cy = int((sx0 + sx1) // 2), int((sy0 + sy1) // 2)
        bw, bh = min(bw, int((box[2] - box[0]) * 1.12)), min(bh, int((box[3] - box[1]) * 1.15))
    kind = KIND.get(n) or classify(arr, sil)
    KINDS[n] = kind
    ink, dist = logo_layer(bw * 1.04, bh * 1.04, kind)
    H, W = ink.shape
    ox, oy = cx - W // 2, max(ay0 + 1, cy - H // 2)
    # texture del vecchio logo, estesa a tutta l'area del nuovo
    region = (max(ax0, min(box[0], ox) - 4), max(ay0, min(box[1], oy) - 4), min(ax1, max(box[2], ox + W) + 4), min(ay1, max(box[3], oy + H) + 4))
    tex = texture(arr, sil, region, col)
    Hs, Ws = arr.shape[:2]
    dist_f = np.full((Hs, Ws), 999, np.float32)
    y0, x0 = max(oy, 0), max(ox, 0)
    y1, x1 = min(oy + H, Hs), min(ox + W, Ws)
    dist_f[y0:y1, x0:x1] = dist[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
    ink_f = dist_f <= 0

    def smooth(m, close=21, sig=2.2):
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close, close)))
        return cv2.GaussianBlur(m.astype(np.float32), (0, 0), sig) > 0.5

    def grow(m, r):
        return cv2.dilate(m.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))) > 0

    band = smooth(dist_f <= (6.5 if kind == 'B' else 7.5))
    outer = grow(band, 2) if kind == 'B' else grow(grow(band, 2), 1)
    clip = np.zeros((Hs, Ws), bool); clip[ay0:ay1, ax0:ax1] = True
    band &= clip; outer &= clip
    # sfondo sotto il vecchio logo: ricostruito con LaMa come per le insegne (make_signs.lama_inpaint); maschera = sagoma misurata + riquadro
    old = np.zeros((Hs, Ws), bool)
    ex = EXTRA.get(n, (0, 0, 0, 0))
    old[max(ay0, box[1] - 4 - ex[1]):box[3] + 8 + ex[3], max(ax0, box[0] - 8 - ex[0]):box[2] + 6 + ex[2]] = True
    old = (old | (sil_d > 0)) & clip
    import make_signs
    art = Image.fromarray(np.ascontiguousarray(arr[ay0:ay1, ax0:ax1])).convert('RGBA')
    res = np.asarray(make_signs.lama_inpaint(art, old[ay0:ay1, ax0:ax1]))
    arr[ay0:ay1, ax0:ax1] = res[..., :3]
    out = np.asarray(Image.fromarray(arr).convert('RGBA')).copy()
    # texture a pieno sprite
    full_tex = np.zeros((Hs, Ws, 3), np.uint8)
    rx0, ry0, rx1, ry1 = region
    tp = np.pad(tex, ((Hs, Hs), (Ws, Ws), (0, 0)), mode='edge')
    full_tex[:] = tp[Hs - ry0:2 * Hs - ry0, Ws - rx0:2 * Ws - rx0]
    mean = full_tex[band].reshape(-1, 3).mean(0) if band.any() else np.array([200., 60., 140.])
    hh, ss, vv = colorsys.rgb_to_hsv(*(mean / 255.0))
    sat_edge = np.array(rgb(hh, min(1.0, ss + 0.15), max(0.75, vv)), np.uint8)       # bordo colorato in tinta con la texture
    dark = (mean * 0.5).astype(np.uint8)
    # ombra morbida sullo sfondo (come negli originali il logo "sta" sulla scena, non incollato)
    shm = cv2.GaussianBlur(np.roll(np.roll(outer.astype(np.float32), 3, 0), 2, 1), (0, 0), 2.6) * 0.42
    out[..., :3] = (out[..., :3].astype(np.float32) * (1 - shm[..., None])).astype(np.uint8)
    # ogni strato e' composto con alfa morbida (bordi antialias, niente scalette)
    def sm(m, sig=0.85):
        f = cv2.GaussianBlur(m.astype(np.float32), (0, 0), sig)
        return np.clip((f - 0.25) / 0.5, 0, 1)

    def paint(alpha, color):
        al = alpha[..., None]
        out[..., :3] = (out[..., :3].astype(np.float32) * (1 - al) + np.asarray(color, np.float32) * al).astype(np.uint8)

    inner = ink_f | (dist_f <= 1.3)
    if kind == 'B':
        paint(sm(outer), sat_edge)                       # bordo esterno sottile, colore della texture
        paint(sm(band), (255, 255, 255))                 # banda bianca
        paint(sm(np.roll(np.roll(dist_f <= 2.4, 2, 0), 1, 1) & band), (206, 202, 214))
        paint(sm(inner), dark)                           # filo scuro attorno alle lettere (stessa tinta)
        letters = ink_f
        fillc = full_tex
    else:
        paint(sm(outer), dark)                           # filo scuro esterno
        paint(sm(grow(band, 2) & clip), (255, 255, 255)) # bordo bianco sottile
        paint(sm(band), full_tex)                        # contorno spesso con la texture
        paint(sm(inner), dark)                           # filo tra lettere bianche e texture
        letters = ink_f
        fillc = np.full_like(full_tex, 255)
    ink_b = sm(letters, 0.7)[..., None]
    out[..., :3] = (out[..., :3] * (1 - ink_b) + fillc * ink_b).astype(np.uint8)
    out[..., 3] = 255
    # effetti degli originali: rilievo, riflesso vetroso, luce di bordo e scintille a 4 punte
    ys, xs = np.nonzero(letters)
    if len(ys):
        rgbf = out[..., :3].astype(np.float32)
        lt = sm(letters, 0.7)
        # 1) rilievo: luce da in alto a sinistra sul bordo interno delle lettere
        bl = cv2.GaussianBlur(lt, (0, 0), 1.3)
        gy, gx = np.gradient(bl)
        lit = np.clip(-(gx + gy) * 2.2, -1, 1)
        rgbf += (np.where(lit > 0, lit * 120, lit * 90))[..., None] * lt[..., None]
        # 2) riflesso a vetro: meta' alta piu' chiara con bordo inferiore ondulato, banda di luce riflessa in basso
        top = np.full(Ws, ys.min(), np.float32); bot = np.full(Ws, ys.max(), np.float32)
        for x in range(xs.min(), xs.max() + 1):
            c = np.nonzero(letters[:, x])[0]
            if len(c):
                top[x], bot[x] = c.min(), c.max()
        yy = np.arange(Hs, dtype=np.float32)[:, None]
        xx = np.arange(Ws, dtype=np.float32)[None, :]
        t = np.clip((yy - top[None, :]) / np.maximum(bot - top, 1)[None, :], 0, 1)
        edge_t = 0.50 + 0.06 * np.sin(xx / 8.0)
        up = np.clip((edge_t - t) / 0.06, 0, 1) * (0.62 - 0.30 * t / 0.5)
        low = np.clip(1 - np.abs(t - 0.84) / 0.07, 0, 1) * 0.22
        deep = np.clip((t - edge_t) / 0.5, 0, 1) * 0.16
        gl = (np.clip(up + low, 0, 1) * lt)[..., None]
        rgbf = rgbf * (1 - gl) + 255 * gl
        rgbf *= (1 - (deep * lt)[..., None])
        # 3) luce sul bordo alto della banda bianca e alone colorato esterno (neon morbido come in alcuni originali)
        if kind == 'B':
            glow = cv2.GaussianBlur(sm(outer).astype(np.float32), (0, 0), 3.0) * 0.30 * (1 - sm(outer))
            rgbf = rgbf * (1 - glow[..., None]) + sat_edge.astype(np.float32) * glow[..., None]
        # 4) scintille a 4 punte
        def glint(cx, cy, r):
            dx, dy = xx - cx, yy - cy
            h = np.exp(-(dy ** 2) / 1.6) * np.clip(1 - np.abs(dx) / r, 0, 1)
            v = np.exp(-(dx ** 2) / 1.6) * np.clip(1 - np.abs(dy) / r, 0, 1)
            c = np.exp(-(dx ** 2 + dy ** 2) / (r * 0.5))
            return np.clip(h + v + c, 0, 1)[..., None]
        W0, W1 = xs.min(), xs.max()
        for gx_, gy_, r in ((W0 + 12, top[W0 + 12] + 3, 9), (W1 - 24, top[max(W1 - 24, 0)] + 6, 7), (W0 + (W1 - W0) * 0.42, top[int(W0 + (W1 - W0) * 0.42)] + 2, 6)):
            g = glint(gx_, gy_, r) * 0.95
            rgbf = rgbf * (1 - g) + 255 * g
        out[..., :3] = np.clip(rgbf, 0, 255).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def bubble_fix(n, img):
    """n.2: balloncino "自然体がステキ" accanto al logo"""
    if n != 2:
        return img
    img = img.convert('RGBA')
    d = ImageDraw.Draw(img)
    d.ellipse((356, 104, 442, 154), fill=(255, 255, 255, 255), outline=(40, 120, 220, 255), width=2)
    mr_font = mr.font('Chewy', 11 * mr.S)
    for k, t in enumerate(('Naturale', 'e carina!')):
        lay = mr.text_layer([t], 11, 'Chewy', (40, 120, 220), (40, 120, 220), (40, 120, 220), 0, shadow=False)
        lay = lay.crop(lay.getbbox())
        img.alpha_composite(lay, (399 - lay.width // 2, 118 + k * 15))
    return img


def main(only=None):
    done = 0
    kinds = {}
    for n in BOX:
        if only and n not in only:
            continue
        d = 'tex0' if n <= 28 else 'tex1'
        src = os.path.join(SRC, f'menu_magazine_{d}', f'MG{n:02d}_t2n_bg1.png')
        img = Image.open(src).convert('RGBA')
        img = bubble_fix(n, draw(n, img))
        od = os.path.join(OUT, f'menu_magazine_{d}')
        os.makedirs(od, exist_ok=True)
        img.save(os.path.join(od, f'MG{n:02d}_t2n_bg1.png'))
        done += 1
        kinds[n] = KINDS.get(n)
    print(f'{done} sfondi della rivista scritti', ''.join(f'{n}{k} ' for n, k in kinds.items()))


if __name__ == '__main__':
    main([int(a) for a in sys.argv[1:]] or None)
