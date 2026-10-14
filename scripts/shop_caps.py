"""Didascalie sotto le icone (ingredienti, prodotti) delle lavagne del negozio: trova le icone colorate e il testo chiaro sotto ciascuna."""
import numpy as np, cv2
import tut_board as tb, tut_edit


def icons(img, region=(8, 60, 312, 214), minsz=11, maxsz=36):
    a = np.asarray(img.convert('RGB'))
    hsv = cv2.cvtColor(a, cv2.COLOR_RGB2HSV)
    m = ((hsv[..., 1] > 90) & (hsv[..., 2] > 120)).astype(np.uint8)
    x0, y0, x1, y1 = region
    sub = np.zeros_like(m); sub[y0:y1, x0:x1] = m[y0:y1, x0:x1]
    sub = cv2.dilate(sub, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(sub)
    res = []
    for i in range(1, n):
        x, y, w, h, ar = st[i]
        if minsz <= w <= maxsz and minsz <= h <= maxsz:
            res.append((int(x), int(y), int(x + w), int(y + h)))
    res.sort(key=lambda b: ((b[1] + b[3]) // 2 // 24, b[0]))
    return res


def find_caps(img, ics, thr=150, depth=22, half=24):
    out = []
    for (x0, y0, x1, y1) in ics:
        cx = (x0 + x1) // 2
        r = (max(0, cx - half), y1 + 1, min(img.width, cx + half), min(img.height, y1 + depth))
        out.append(tut_edit.bright_bbox(img, r, thr))
    return out


def captions(img, texts, region=(8, 60, 312, 214), px=8, thr=150, depth=22, half=24, strict=True, add=()):
    ics = icons(img, region) + [tuple(a) for a in add]
    ics.sort(key=lambda b: ((b[1] + b[3]) // 2 // 24, b[0]))
    if strict and len(ics) != len(texts):
        raise ValueError(f'icone {len(ics)} != testi {len(texts)}: {ics}')
    caps = find_caps(img, ics, thr, depth, half)
    for bb in caps:
        if bb:
            tut_edit.clean(img, bb)
    for ic, bb, t in zip(ics, caps, texts):
        if not t:
            continue
        cx = (ic[0] + ic[2]) // 2
        if bb is None:
            bb = (cx - 14, ic[3] + 2, cx + 14, ic[3] + 11)
        lines = t if isinstance(t, list) else [t]
        # il testo si centra sull'icona; larghezza massima ~ 2*half
        rect = (cx - 20, bb[1] - 1, cx + 20, bb[1] + 10 * len(lines) + 2)
        tut_edit.retext(img, rect, lines, px=px, keep=True, bb=rect, fit=40)
    return ics
