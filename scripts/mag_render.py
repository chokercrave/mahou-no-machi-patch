"""Rivista Spell & Spill: riscrive un'unita' di testo di uno sprite (blob di mag_blobs) con testo italiano nello stesso stile:
colori di riempimento/contorno campionati, rettangolo ruotato dell'originale, font a scelta."""
import os, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.join(os.path.dirname(__file__), '..')
FONTS = os.path.join(ROOT, 'tools', 'fonts')
S = 3   # supercampionamento


def font(name, px):
    return ImageFont.truetype(os.path.join(FONTS, name + '.ttf'), px)


def sample_style(arr, M):
    """arr RGBA (h,w,4), M maschera booleana dell'unita': (outline, top, bottom, thickness)"""
    m8 = M.astype(np.uint8)
    dist = cv2.distanceTransform(m8, cv2.DIST_L2, 3)
    rgb = arr[..., :3].astype(int)
    ring = rgb[(dist > 0) & (dist <= 1.6)]
    out = tuple(int(v) for v in np.median(ring, axis=0)) if len(ring) else (255, 255, 255)
    inner = (dist >= 3)
    if inner.sum() < 20:
        inner = (dist >= 1.5)
    far = inner & (np.abs(rgb - np.array(out)).sum(2) > 110)      # il riempimento non e' il colore del bordo (es. piastra nera)
    if far.sum() >= 0.12 * max(1, inner.sum()) and far.sum() >= 15:
        inner = far
    elif inner.sum():
        lum = sum(out) / 3
        w = (255, 255, 255) if lum < 140 else (30, 30, 40)
        return out, w, w, 2
    ys, xs = np.nonzero(inner)
    if not len(ys):
        return out, out, out, 2
    y0, y1 = ys.min(), ys.max()
    span = max(1, y1 - y0)
    top = rgb[inner & (np.arange(M.shape[0])[:, None] <= y0 + span * 0.35)]
    bot = rgb[inner & (np.arange(M.shape[0])[:, None] >= y1 - span * 0.35)]
    tc = tuple(int(v) for v in np.median(top, axis=0)) if len(top) else out
    bc = tuple(int(v) for v in np.median(bot, axis=0)) if len(bot) else tc
    # spessore del contorno: quanto in profondita' i pixel restano vicini al colore del bordo
    near = (np.abs(rgb - np.array(out)).sum(2) < 60) & M
    th = int(round(np.median(dist[near & (dist < 6)]) * 2)) if (near & (dist < 6)).sum() else 2
    return out, tc, bc, max(2, min(5, th))


def layout(text, W, H, fontname, th, maxlines=3):
    """migliore suddivisione in righe e corpo del carattere che entra in W x H (px reali). -> (size, [righe])"""
    words = text.split(' ')
    best = (0, [text])
    def fits(lines, size):
        f = font(fontname, size * S)
        w = max(f.getlength(l) for l in lines) / S + 2 * th
        asc, desc = f.getmetrics()
        h = (asc + desc) / S * len(lines) * 0.92 + 2 * th
        return w <= W and h <= H
    cands = [[text]]
    if len(words) > 1:
        for n in range(2, min(maxlines, len(words)) + 1):
            # suddivisioni bilanciate per lunghezza
            tot = len(text)
            lines, cur = [], ''
            for w in words:
                if cur and len((cur + ' ' + w)) > tot / n + 1 and len(lines) < n - 1:
                    lines.append(cur); cur = w
                else:
                    cur = (cur + ' ' + w).strip()
            lines.append(cur)
            cands.append(lines)
    for lines in cands:
        lo, hi = 6, 120
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if fits(lines, mid):
                lo = mid
            else:
                hi = mid - 1
        if lo > best[0]:
            best = (lo, lines)
    return best


def text_layer(lines, size, fontname, fill_top, fill_bot, outline, th, shadow=True):
    f = font(fontname, size * S)
    asc, desc = f.getmetrics()
    lh = int((asc + desc) * 0.92)
    w = int(max(f.getlength(l) for l in lines)) + 2 * (th + 3) * S
    h = lh * len(lines) + 2 * (th + 3) * S
    mask = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(mask)
    for k, l in enumerate(lines):
        lw = f.getlength(l)
        d.text(((w - lw) / 2, (th + 3) * S + k * lh), l, font=f, fill=255)
    # contorno: dilatazione della maschera
    ol = mask.filter(ImageFilter.MaxFilter(2 * th * S // 2 * 2 + 1)) if th * S > 1 else mask
    fillimg = Image.new('RGB', (w, h))
    px = fillimg.load()
    for y in range(h):
        t = y / max(1, h - 1)
        c = tuple(int(fill_top[i] * (1 - t) + fill_bot[i] * t) for i in range(3))
        for x in range(w):
            px[x, y] = c
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    if shadow:
        sh = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        sh.paste(Image.new('RGBA', (w, h), (0, 0, 0, 90)), (S, S), ol)
        layer.alpha_composite(sh)
    layer.paste(Image.new('RGBA', (w, h), tuple(outline) + (255,)), (0, 0), ol)
    layer.paste(fillimg.convert('RGBA'), (0, 0), mask)
    return layer.resize((w // S, h // S), Image.LANCZOS)


BG = None      # sfondo (RGB array 512x256) dello sprite in lavorazione: serve a garantire la leggibilita'


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def ensure_contrast(tc, bc, out, cx, cy, rw, rh):
    """se riempimento/contorno somigliano allo sfondo dietro l'etichetta, scurisce o schiarisce il riempimento e inverte il contorno
    (scritta scura con contorno bianco su sfondi chiari, chiara con contorno scuro su sfondi scuri): leggibile, stesso spirito dell'originale"""
    if BG is None:
        return tc, bc, out
    H, W = BG.shape[:2]
    x0, x1 = int(max(0, cx - rw / 2)), int(min(W, cx + rw / 2))
    y0, y1 = int(max(0, cy - rh / 2)), int(min(H, cy + rh / 2))
    if x1 <= x0 or y1 <= y0:
        return tc, bc, out
    reg = BG[y0:y1, x0:x1].reshape(-1, 3).astype(float)
    bl = _lum(reg.mean(0))
    spread = reg.std(0).mean()
    fl = (_lum(tc) + _lum(bc)) / 2
    ol = _lum(out)
    # il contorno e' cio' che separa la scritta dallo sfondo: deve contrastare con lo sfondo, il riempimento col contorno
    if abs(ol - bl) < 70 or abs(fl - ol) < 90 or spread > 60 and abs(ol - bl) < 110:
        if bl > 140:           # sfondo chiaro: contorno scuro, riempimento chiaro e saturo oppure bianco
            out = (40, 20, 70)
            if fl < 150:
                tc, bc = (255, 255, 255), (255, 244, 230)
        else:                  # sfondo scuro: contorno bianco-rosato, riempimento scuro saturo? meglio chiaro con contorno scuro
            out = (30, 10, 50)
            if fl < 170:
                tc, bc = (255, 255, 255), (255, 230, 120)
    return tc, bc, out


def restyle(im, lab, label, text, fontname='Chewy', angle_mode='auto', pad=0.0, fill=None, outline=None, maxlines=3):
    """sostituisce l'unita' `label` (immagine delle etichette lab) di `im` (RGBA 512x256) con `text`. Restituisce una nuova immagine."""
    arr = np.asarray(im).copy()
    M = (lab == label) & (arr[..., 3] > 40)
    reg = (lab == label)
    ys, xs = np.nonzero(M)
    pts = np.stack([xs, ys], 1).astype(np.float32)
    (cx, cy), (rw, rh), ang = cv2.minAreaRect(pts)
    # lato lungo orizzontale: angolo in (-90, 90]
    if rw < rh:
        rw, rh = rh, rw
        ang += 90
    if ang > 90:
        ang -= 180
    if ang > 45:
        ang -= 90; rw, rh = rh, rw      # ruota di 90: rettangolo in verticale
    if ang < -45:
        ang += 90; rw, rh = rh, rw
    if rh > rw * 1.5:                       # testo verticale (illeggibile): si scrive in orizzontale, leggermente inclinato, anche sopra il logo
        long_side = rh
        rw, rh = max(long_side * 1.5, 120.0), max(min(long_side * 0.5, 46.0), 34.0)
        ang = -6.0
    out, tc, bc, th = sample_style(arr, M)
    if fill:
        tc = bc = fill
    if outline:
        out = outline
    tc, bc, out = ensure_contrast(tc, bc, out, cx, cy, rw, rh)
    W, Hh = rw * (1 - pad), rh * (1 - pad)
    opts = []
    for rot, (a, b) in ((0, (W, Hh)),):
        size, lines = layout(text, a, b, fontname, th, maxlines)
        opts.append((size * (1.0 if rot == 0 else 0.85), size, lines, rot))
    _, size, lines, rot = max(opts, key=lambda o: o[0])
    layer = text_layer(lines, size, fontname, tc, bc, out, th)
    layer = layer.crop(layer.getbbox())      # centra sull'inchiostro (il font ha spazio per le discendenti)
    total = ang + (90 if rot == 90 else 0)
    while total >= 90:
        total -= 180
    while total < -90:
        total += 180
    layer = layer.rotate(-total, expand=True, resample=Image.BICUBIC)
    # cancella l'unita' originale e incolla la nuova
    clear = cv2.dilate(reg.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    arr[clear & (lab == label) | M] = 0
    base = Image.fromarray(arr)
    return place(base, layer, cx, cy)


AVOID = None   # rettangolo (x0, y0, x1, y1) del logo nello sfondo: il testo non deve coprirlo


def _hit(r, a):
    return r[0] < a[2] and r[2] > a[0] and r[1] < a[3] and r[3] > a[1]


def place(base, layer, cx, cy, margin=1):
    """incolla il livello centrato su (cx, cy); se esce dallo sprite lo rimpicciolisce; se toccherebbe il logo (AVOID) lo sposta nella posizione
    libera piu' vicina (sotto, sopra, a lato), rimpicciolendolo se serve"""
    W, H = base.size
    k = min(1.0, 2 * (min(cx, W - cx) - margin) / layer.width, 2 * (min(cy, H - cy) - margin) / layer.height)
    if k < 1.0:
        layer = layer.resize((max(1, int(layer.width * k)), max(1, int(layer.height * k))), Image.LANCZOS)
    if AVOID:
        ax0, ay0, ax1, ay1 = AVOID
        for _ in range(8):
            w, h = layer.size
            r = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
            if not _hit(r, AVOID):
                break
            cands = []
            for ncx, ncy in ((cx, ay1 + h / 2 + 2), (cx, ay0 - h / 2 - 2), (ax1 + w / 2 + 2, cy), (ax0 - w / 2 - 2, cy)):
                if w / 2 + margin <= ncx <= W - w / 2 - margin and h / 2 + margin <= ncy <= H - h / 2 - margin:
                    cands.append((abs(ncx - cx) + abs(ncy - cy), ncx, ncy))
            if cands:
                _, cx, cy = min(cands)
                break
            layer = layer.resize((max(1, int(w * 0.88)), max(1, int(h * 0.88))), Image.LANCZOS)
    base.alpha_composite(layer, (int(round(cx - layer.width / 2)), int(round(cy - layer.height / 2))))
    return base


def restyle_inner(im, lab, label, text, fontname='Chewy', maxlines=3):
    """testo dentro una forma (ovale, etichetta, bollino): toglie solo i pixel del testo (colore lontano dal riempimento della forma,
    lontano dal bordo), li ricostruisce col colore della forma e riscrive il testo con lo stesso colore d'inchiostro."""
    arr = np.asarray(im).copy()
    M = (lab == label) & (arr[..., 3] > 40)
    yy_, xx_ = np.nonzero(M)
    if len(yy_) and (yy_.max() - yy_.min()) > 1.6 * (xx_.max() - xx_.min() + 1):      # etichetta verticale: si cancella e si riscrive in orizzontale
        return restyle(im, lab, label, text, fontname, maxlines=maxlines)
    dist = cv2.distanceTransform(M.astype(np.uint8), cv2.DIST_L2, 3)
    rgb = arr[..., :3].astype(int)
    core = M & (dist >= 3)
    fillc = np.median(rgb[core], axis=0)
    txt = core & (np.abs(rgb - fillc).sum(2) > 150)
    if txt.sum() < 10:
        raise ValueError('nessun testo interno')
    txt = cv2.dilate(txt.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & core
    ink = tuple(int(v) for v in np.median(rgb[core & (np.abs(rgb - fillc).sum(2) > 150)], axis=0))
    ys, xs = np.nonzero(txt)
    pts = np.stack([xs, ys], 1).astype(np.float32)
    (cx, cy), (rw, rh), ang = cv2.minAreaRect(pts)
    if rw < rh:
        rw, rh = rh, rw; ang += 90
    if ang > 90: ang -= 180
    if ang > 45: ang -= 90; rw, rh = rh, rw
    if ang < -45: ang += 90; rw, rh = rh, rw
    mask = (txt * 255).astype(np.uint8)
    rec = cv2.inpaint(np.ascontiguousarray(arr[..., :3]), mask, 3, cv2.INPAINT_TELEA)
    arr[..., :3][txt] = rec[txt]
    W, Hh = rw, rh
    opts = []
    for rot, (a, b) in ((0, (W, Hh)), (90, (Hh, W))):
        size, lines = layout(text, a, b, fontname, 0, maxlines)
        opts.append((size * (1.0 if rot == 0 else 0.85), size, lines, rot))
    _, size, lines, rot = max(opts, key=lambda o: o[0])
    layer = text_layer(lines, size, fontname, ink, ink, ink, 0, shadow=False)
    layer = layer.crop(layer.getbbox())
    total = ang + (90 if rot == 90 else 0)
    while total >= 90: total -= 180
    while total < -90: total += 180
    layer = layer.rotate(-total, expand=True, resample=Image.BICUBIC)
    base = Image.fromarray(arr)
    return place(base, layer, cx, cy)
