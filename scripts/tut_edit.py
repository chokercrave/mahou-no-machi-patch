"""Operazioni generiche per rifare il testo delle lavagne (vedi tut_board.py per il disegno).
  retext(img, hint, testo|[righe], align='c', px=13, big=False)   trova il testo chiaro dentro `hint` (x0,y0,x1,y1), lo cancella
        (sfondo piatto se c'è, altrimenti texture della lavagna) e scrive il nuovo testo nello stesso ingombro
  Coordinate = quelle della lavagna 320x256 (nei fogli di lettura: x-4 (-330 per la colonna destra), y-14 (-276 seconda riga))."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image, ImageDraw
import tut_board as tb


PHOTO = False      # True per le immagini che non sono lavagne (schermate di gioco)


def bright_bbox(img, hint, thr=165, dark=False):
    full = np.asarray(img.convert('RGB')).astype(int)
    if dark:       # testo scuro su fondo chiaro: pixel scuri dentro una forma chiara (balloon, pulsante) senza i bordi
        import cv2
        bright = (full.min(2) > 150).astype(np.uint8)
        pad = cv2.copyMakeBorder(bright, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
        ff = (1 - pad).copy()
        mask = np.zeros((ff.shape[0] + 2, ff.shape[1] + 2), np.uint8)
        cv2.floodFill(ff, mask, (0, 0), 2)                   # sfondo esterno = 2; i buchi (testo) restano 1
        filled = (ff != 2).astype(np.uint8)[1:-1, 1:-1]
        inner = cv2.erode(filled, np.ones((7, 7), np.uint8))
        m_full = (full.max(2) < thr) & (inner > 0)
        m = m_full[hint[1]:hint[3], hint[0]:hint[2]]
    else:
        m = (full.min(2) > thr)[hint[1]:hint[3], hint[0]:hint[2]]
    ys, xs = np.nonzero(m)
    if not len(xs):
        return None
    return (hint[0] + xs.min(), hint[1] + ys.min(), hint[0] + xs.max() + 1, hint[1] + ys.max() + 1)


def clean(img, bb, pad=2, dark_mask=False):
    r = (max(0, bb[0] - pad), max(0, bb[1] - pad), min(img.width, bb[2] + pad), min(img.height, bb[3] + pad))
    a = np.asarray(img.convert('RGB')).astype(int)
    ring = np.concatenate([a[r[1] - 1, r[0]:r[2]], a[r[3], r[0]:r[2]], a[r[1]:r[3], r[0] - 1], a[r[1]:r[3], r[2]]])
    ring_all = ring
    ring = ring[ring.min(1) <= 200] if (ring.min(1) <= 200).any() else ring     # il bianco dei contorni non è sfondo
    cols, cnt = np.unique(ring, axis=0, return_counts=True)
    i = int(cnt.argmax())
    if cnt[i] >= 0.3 * len(ring_all):                      # sfondo piatto (balloon, pulsante, riquadro): lo si ridipinge a tinta unita
        col = tuple(int(v) for v in cols[i])
        ImageDraw.Draw(img).rectangle([r[0], r[1], r[2] - 1, r[3] - 1], fill=col + (255,))
    elif PHOTO or ring.mean() > 95:                    # sfondo non piatto e non lavagna: si ricostruisce con inpainting
        import cv2
        arr = np.asarray(img.convert('RGB')).copy()
        sub = arr[r[1]:r[3], r[0]:r[2]]
        mask = (sub.min(2) > 150).astype(np.uint8) * 255 if not dark_mask else (sub.max(2) < 100).astype(np.uint8) * 255
        mask = cv2.dilate(mask, np.ones((3, 3), np.uint8))
        out = cv2.inpaint(np.ascontiguousarray(sub), mask, 3, cv2.INPAINT_TELEA)
        img.paste(Image.fromarray(out).convert('RGBA'), (r[0], r[1]))
    else:
        tb.erase(img, r)
    return r


def retext(img, hint, text, align='c', px=13, big=False, gap=2, fit=None, thr=165, keep=False, at=None, alpha=1.0, dark=False, ink=None, valign='m', bb=None):
    """fit = larghezza massima: se il testo è più largo riduce il corpo; at=(x, y) forza la posizione dell'angolo/centro"""
    bb = bb or bright_bbox(img, hint, 100 if dark and thr == 165 else thr, dark)
    assert bb, f'nessun testo in {hint}'
    if not keep:
        clean(img, bb, dark_mask=dark)
    lines = [text] if isinstance(text, str) else text
    cx0 = (bb[0] + bb[2]) / 2
    W = img.width - 14
    maxw = fit or (W - bb[0] if align == 'l' else (bb[2] - 16 if align == 'r' else 2 * min(cx0 - 16, W - cx0)))
    sp = 1
    while True:
        ims = [(tb.chalk(t, px) if big else tb.pixel_text(t, px, spacing=sp, dark=dark or ink == 'dark')) for t in lines]
        if max(i.width for i in ims) <= maxw:
            break
        if px <= (16 if big else 9):
            if not big and sp == 1:
                sp = 0                                   # ultimo rimedio: lettere accostate
                continue
            break
        px -= 1
    lh = max(i.height for i in ims) + gap
    total = lh * len(ims) - gap
    cy = (bb[1] + bb[3]) / 2
    top = round(cy - total / 2) if valign == 'm' else bb[1]
    for k, im in enumerate(ims):
        if align == 'c':
            x = round((bb[0] + bb[2]) / 2 - im.width / 2)
        elif align == 'l':
            x = bb[0]
        else:
            x = bb[2] - im.width
        if at:
            x = at[0] if align == 'l' else at[0] - im.width // (2 if align == 'c' else 1)
        if alpha < 1:
            im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * alpha)))
        img.alpha_composite(im, (x, top + k * lh))
    return img


def title_only(name, lines, arch):
    b = tb.load(name)
    tb.save(tb.title(b, lines), name, arch)


def H(tile, rect):
    """coordinate del foglio di lettura (tile = (colonna, riga)) -> coordinate della lavagna"""
    ox, oy = tile[0] * 330 + 4, tile[1] * 276 + 14
    return (rect[0] - ox, rect[1] - oy, rect[2] - ox, rect[3] - oy)


def hdr(img, hint, text, px=13, cx=None):
    """titoletto in alto: testo piccolo tra i due ornamenti (cancella e riscrive tutta la riga)"""
    hint = (24, hint[1], img.width - 24, hint[3])        # l'intera riga, ornamenti compresi
    bb = bright_bbox(img, hint)
    assert bb, f'nessun titoletto in {hint}'
    clean(img, bb, pad=3)
    cy = (bb[1] + bb[3]) // 2
    cx = cx if cx is not None else (bb[0] + bb[2]) // 2
    while True:
        t = tb.pixel_text(text, px)
        if t.width <= img.width - 90 or px <= 9:
            break
        px -= 1
    lo, ro = tb.small_ornaments()
    img.alpha_composite(t, (cx - t.width // 2, cy - t.height // 2))
    img.alpha_composite(lo, (cx - t.width // 2 - 5 - lo.width, cy - lo.height // 2 + 1))
    img.alpha_composite(ro, (cx + t.width // 2 + 5, cy - ro.height // 2 + 1))
    return img


def text_blobs(img, hint, thr=165, maxh=14, maxw=70, kx=5, ky=2):
    """gruppi di pixel chiari piccoli (etichette di testo) dentro `hint`, in ordine di lettura (righe da 12 px, poi x)"""
    import cv2
    full = np.asarray(img.convert('RGB')).astype(int)
    m = (full.min(2) > thr).astype(np.uint8)
    sub = m[hint[1]:hint[3], hint[0]:hint[2]]
    d = cv2.dilate(sub, np.ones((ky, kx), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(d)
    out = []
    for i in range(1, n):
        x, y, w, h, ar = st[i]
        if h <= maxh and w <= maxw and sub[y:y + h, x:x + w].sum() >= 4:
            out.append((hint[0] + int(x), hint[1] + int(y), hint[0] + int(x + w), hint[1] + int(y + h)))
    out.sort(key=lambda b: (b[1] // 12, b[0]))
    return out


def auto_labels(img, hint, texts, px=11, thr=165, **kw):
    """riscrive le etichette di testo trovate in `hint` con `texts` (stesso ordine di lettura); None salta un'etichetta"""
    blobs = text_blobs(img, hint, thr)
    if len(blobs) != len(texts):
        raise ValueError(f'etichette trovate {len(blobs)} != {len(texts)}: {blobs}')
    for bb in blobs:
        clean(img, bb)
    for bb, t in zip(blobs, texts):
        if t:
            retext(img, bb, t, px=px, keep=True, bb=bb, fit=kw.get('fit', 52), **{k: v for k, v in kw.items() if k != 'fit'})


_order = {}


def tile_of(name):
    """posizione (colonna, riga) della lavagna nel suo foglio di lettura (tut_extract: 4 per foglio, ordine di boards())"""
    import tut_extract
    for pre in ('Charm', 'Special', 'Tutorial', 'chime', 'coorde', 'etc', 'hyosho', 'idol', 'kanban', 'language', 'magic', 'mydesign',
                'npc_runway', 'pc_runway', 'photo', 'shop', 'ucc_tuto'):
        if name.startswith(pre):
            if pre not in _order:
                _order[pre] = [n for n in tut_extract.boards() if n.startswith(pre)]
            k = _order[pre].index(name)
            return (k % 2, (k // 2) % 2)
    raise KeyError(name)


def apply_ops(name, img, ops):
    """ops: ('T', righe) titolo grande | ('h', testo, y_foglio) titoletto | ('r', rect_foglio, testo|righe, opzioni) testo libero"""
    t = tile_of(name)
    for op in ops:
        if op[0] == 'T':
            tb.title(img, op[1])
        elif op[0] == 'h':
            y = op[2]
            hdr(img, H(t, (0, y - 11, 0, y + 11)), op[1])
        elif op[0] == 'r':
            retext(img, H(t, op[1]), op[2], **(op[3] if len(op) > 3 else {}))
        elif op[0] == 'L':                                  # etichette automatiche: ('L', rect_foglio, [testi], opzioni)
            auto_labels(img, H(t, op[1]), op[2], **(op[3] if len(op) > 3 else {}))
        elif op[0] == 'b':                                  # rettangolo in coordinate della lavagna
            retext(img, op[1], op[2], **(op[3] if len(op) > 3 else {}))
    return img


def run_family(specs, arch, only=None, photo=False):
    global PHOTO
    PHOTO = photo
    for name, ops in specs.items():
        if only and name not in only:
            continue
        img = tb.load(name)
        try:
            apply_ops(name, img, ops)
        except Exception as e:
            print(f'  ! {name}: {type(e).__name__} {e}')
            continue
        tb.save(img, name, arch)
        print('ok', name)
