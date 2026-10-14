"""Rigenera "etichette" di testo in italiano mantenendo lo stile dell'originale.
- etichetta trasparente: si conservano le decorazioni ai bordi (blocchi separati da colonne vuote
  nel primo/ultimo 28% della larghezza), si cancella il resto, si scrive il testo con i colori
  di riempimento e contorno rilevati.
- riquadro opaco: si ridipinge l'interno col colore di fondo prevalente e si scrive il testo.
"""
import collections
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT = r'C:\Windows\Fonts\seguibl.ttf'
FONT_PLAIN = r'C:\Windows\Fonts\segoeuib.ttf'


def _lum(c):
    return (c[0] * 3 + c[1] * 6 + c[2]) // 10


def _text_colors(pixels_with_edge):
    """(fill, outline): outline = colore prevalente dei pixel di bordo, fill = degli interni"""
    edge = collections.Counter(c[:3] for c, e in pixels_with_edge if e and c[3] > 200)
    inner = collections.Counter(c[:3] for c, e in pixels_with_edge if not e and c[3] > 200)
    out = edge.most_common(1)[0][0] if edge else (40, 40, 100)
    fill = None
    for c, _ in inner.most_common(10):
        if sum(abs(a - b) for a, b in zip(c, out)) > 120:
            fill = c; break
    if fill is None:
        # testo monocolore: stesso colore, nessun contorno
        return out, None
    return fill, out


_DR = ImageDraw.Draw(Image.new('L', (4, 4)))


def _fit_font(text, maxw, maxh, path=FONT):
    def load(sz):
        f = ImageFont.truetype(path, sz)
        if 'Grandstander' in path:
            f.set_variation_by_name('Bold')       # variabile: senza questo userebbe il peso più sottile
        return f
    size = max(8, int(maxh))
    while size > 7:
        f = load(size)
        l, t, r, b = _DR.multiline_textbbox((0, 0), text, font=f, spacing=0, align='center')
        if r - l <= maxw and b - t <= maxh:
            return f
        size -= 1
    return load(7)


CUR_GROUP, CAP, REC = None, {}, {}     # gruppi di etichette con dimensione uniforme (gen_labels)
STYLE = 'ui'         # font UI (ui_font: Grandstander / font pixel del gioco). 'segoe' = vecchio
BUTTON_PX = {'button_txt': 13, 'button': 13, 'safe_tab': 13}     # gruppi di pulsanti (gen_labels.group): DF_kyougeki 13 px
BUTTON_FILL = {'button': (39, 90, 124)}          # pulsanti mydesign: colore del testo giapponese (la stima per pulsante variava)


def _draw(canvas, text, box, fill, outline, ow):
    x0, y0, x1, y1 = box
    w, h = canvas.size
    if STYLE == 'ui':
        import ui_font
        o = outline if outline else (255, 255, 255)
        if CUR_GROUP and CUR_GROUP.endswith('tab_txt'):
            x0, y0, x1, y1 = 2, 1, w - 2, h - 1          # linguette: tutta la targhetta, font Grandstander anche a corpo piccolo
            if CUR_GROUP.startswith('menu_input_str:'):   # tastiera: il testo giapponese sta in alto (centro y~11 nelle basse, ~28 nelle alte)
                y0, y1 = (17, 39) if h >= 48 else (1, 21)
            ui_font.SMALL = 6                             # Grandstander antialias anche a corpo piccolo (il font pixel LC a 11 px risultava largo e poco leggibile)
        else:
            ui_font.SMALL = 14
        pxm = max(9, int((y1 - y0) * 1.1))
        if CUR_GROUP and CUR_GROUP.split(':')[1] in BUTTON_PX:
            # pulsanti: corpo FISSO come nel giapponese (font pixel del gioco) e tutta la larghezza del pulsante,
            # non quella dell'inchiostro giapponese (una parola corta come もどす rimpiccioliva "Rimetti")
            pxm = BUTTON_PX[CUR_GROUP.split(':')[1]]
            if _lum(fill) < 110 and fill[2] > fill[0] + 30:   # solo la variante normale (testo blu): rosa/grigio restano i loro
                fill = BUTTON_FILL.get(CUR_GROUP.split(':')[1], fill)
            if CUR_GROUP.endswith(('button_txt', 'safe_tab')):
                x0, x1, y0, y1 = 1, w - 1, 0, h
        elif CUR_GROUP:
            pxm = min(pxm, CAP.get(CUR_GROUP, pxm))      # stessa dimensione del testo per tutte le etichette del gruppo
        if CUR_GROUP and CUR_GROUP.split(':')[1] in BUTTON_PX:
            # contorno netto da 1 px come nel giapponese; se la parola non entra, lettere senza spazio
            # tra loro invece di scendere al font piccolo
            bow = 0 if CUR_GROUP.endswith(':button') else 1      # mydesign: testo senza contorno, come l'originale
            for sp in (1, 0):
                im = ui_font.fit(text, fill, x1 - x0, y1 - y0, px_max=pxm, px_min=pxm, outline=o, spacing=sp, ow=bow, soft=0)
                if im.width <= x1 - x0:
                    break
            else:
                im = ui_font.fit(text, fill, x1 - x0, y1 - y0, px_max=pxm, outline=o, spacing=1, ow=bow, soft=0)
        else:
            im = ui_font.fit(text, fill, x1 - x0, y1 - y0, px_max=pxm, outline=o, squeeze=0.78, spacing=1,
                             ow=1.5 if (y1 - y0) >= 12 else 1.0)
        if CUR_GROUP:
            REC.setdefault(CUR_GROUP, []).append(ui_font.LAST_PX)
        if im.width <= x1 - x0 and im.height <= y1 - y0 + 2:
            # linguette di menu_safe: il giapponese e' allineato a destra nella texture (finisce a x=64)
            xa = x1 - im.width if CUR_GROUP and CUR_GROUP.endswith('safe_tab') else int((x0 + x1 - im.width) / 2)
            canvas.alpha_composite(im, (xa, int((y0 + y1 - im.height) / 2)))
            return
        # spazio troppo piccolo per il font pixel: Grandstander con antialias (leggibile anche a 7-9 px)
        global FONT, FONT_PLAIN
        FONT = FONT_PLAIN = ui_font.FONT
        _draw_aa(canvas, text, box, fill, outline, ow)
        return
    _draw_aa(canvas, text, box, fill, outline, ow)


def _draw_aa(canvas, text, box, fill, outline, ow):
    x0, y0, x1, y1 = box
    w, h = canvas.size
    f = _fit_font(text, x1 - x0 - 2 * ow, (y1 - y0) - 2 * ow, FONT if ow else FONT_PLAIN)
    mask = Image.new('L', (w, h))
    ImageDraw.Draw(mask).multiline_text(((x0 + x1) / 2, (y0 + y1) / 2), text, font=f, fill=255,
                                        anchor='mm', spacing=0, align='center')
    layer = Image.new('RGBA', (w, h))
    if ow:
        halo = mask.filter(ImageFilter.MaxFilter(2 * ow + 1))
        layer.paste(Image.new('RGBA', (w, h), outline + (255,)), (0, 0), halo)
    layer.paste(Image.new('RGBA', (w, h), fill + (255,)), (0, 0), mask)
    canvas.alpha_composite(layer)


def relabel(src, text, dst, keep_deco=True, keep_edges=False):
    """keep_edges: conserva sempre il primo e l'ultimo blocco (icone ai lati del testo)"""
    im = Image.open(src).convert('RGBA')
    w, h = im.size
    px = im.load()
    a = im.getchannel('A')
    bbox = a.getbbox()
    if not bbox:
        im.save(dst); return
    bx0, by0, bx1, by1 = bbox
    opaque_ratio = sum(1 for x in range(bx0, bx1) for y in range(by0, by1) if px[x, y][3] > 200) / max(1, (bx1 - bx0) * (by1 - by0))
    out = im.copy()
    op = out.load()
    if opaque_ratio > 0.85:
        # riquadro opaco: fondo = colore prevalente al centro
        bh = by1 - by0
        cnt = collections.Counter(px[x, y][:3] for x in range(bx0 + 3, bx1 - 3)
                                  for y in range(by0 + bh // 3, by1 - bh // 3))
        bg = cnt.most_common(1)[0][0]
        ix0, iy0, ix1, iy1 = bx0 + 3, by0 + 2, bx1 - 3, by1 - 2
        textpx = [(x, y) for x in range(ix0, ix1) for y in range(iy0, iy1)
                  if sum(abs(px[x, y][i] - bg[i]) for i in range(3)) > 80]
        if textpx:
            tx0 = min(x for x, _ in textpx); tx1 = max(x for x, _ in textpx)
            ty0 = min(y for _, y in textpx); ty1 = max(y for _, y in textpx)
        else:
            tx0, ty0, tx1, ty1 = ix0, iy0, ix1, iy1
        cols = collections.Counter(px[x, y][:3] for x, y in textpx)
        cand = [c for c, n in cols.most_common(12) if n >= 3 and sum(abs(c[i] - bg[i]) for i in range(3)) > 120]
        if cand:
            # il più contrastato rispetto al fondo
            fill = max(cand[:6], key=lambda c: abs(_lum(c) - _lum(bg)))
        else:
            fill = (30, 30, 30) if _lum(bg) > 128 else (255, 255, 255)
        # interno del riquadro riga per riga (dal primo all'ultimo pixel del colore di fondo): i pulsanti con
        # un anello colorato dentro il bordo (mydesign: giallo dentro un anello azzurro) non perdono l'anello
        rows = {}
        for y in range(by0, by1):
            xs = [x for x in range(bx0, bx1) if sum(abs(px[x, y][i] - bg[i]) for i in range(3)) < 60]
            if xs:
                rows[y] = (min(xs), max(xs))
        ring = len(rows) and min(r[0] for r in rows.values()) > bx0 + 2      # anello colorato dentro il bordo
        for x in range(max(ix0, tx0 - 1), min(ix1, tx1 + 2)):
            for y in range(max(iy0, ty0 - 1), min(iy1, ty1 + 2)):
                if y in rows and rows[y][0] <= x <= rows[y][1]:
                    op[x, y] = bg + (255,)
        if ring:
            # con l'anello si ripulisce tutto l'interno: accenti e puntini del giapponese possono stare
            # fuori dalle righe dell'inchiostro misurato
            for y, (a, b) in rows.items():
                for x in range(a, b + 1):
                    op[x, y] = bg + (255,)
            # il testo giapponese sconfina anche sulle righe dell'anello sopra e sotto: lì i pixel scuri
            # (solo nella fascia centrale, non gli angoli del bordo) prendono il colore dell'anello
            y0r, y1r = min(rows), max(rows)
            a, b = rows[y0r][0] + 2, rows[y0r][1] - 2
            for y in (y0r - 2, y0r - 1, y1r + 1, y1r + 2):
                if not by0 < y < by1 - 1:
                    continue
                light = collections.Counter(px[x, y][:3] for x in range(a, b) if _lum(px[x, y]) >= 120)
                if not light:
                    continue
                rc = light.most_common(1)[0][0]
                for x in range(a, b):
                    if sum(abs(px[x, y][i] - rc[i]) for i in range(3)) > 90:     # anche l'antialias del testo
                        op[x, y] = rc + (255,)
        mid = rows.get((by0 + by1) // 2)
        if mid:
            ix0, ix1 = max(ix0, mid[0] + 1), min(ix1, mid[1])
        box = (ix0, iy0, ix1, iy1)
        if textpx and ty1 - ty0 < 0.5 * (iy1 - iy0):
            # testo in una fascia di un riquadro alto (es. linguetta tastiera 64x64): resta in quella fascia
            box = (ix0, max(iy0, ty0 - 2), ix1, min(iy1, ty1 + 3))
        _draw(out, text, box, fill, None, 0)
        out.save(dst); return
    # etichetta trasparente: colonne piene/vuote per trovare decorazioni ai bordi
    colfull = [any(px[x, y][3] > 40 for y in range(h)) for x in range(w)]
    segs, x = [], 0
    while x < w:
        if colfull[x]:
            s = x
            while x < w and colfull[x]:
                x += 1
            segs.append((s, x))
        x += 1
    lim = 0.28 * (bx1 - bx0)
    th = by1 - by0
    keep = []
    # decorazione = blocco ai bordi molto più largo di un carattere (spirale con coda)
    if keep_deco and len(segs) >= 3:
        need = 0 if keep_edges else 1.4 * th
        a, b = segs[0], segs[-1]
        ok_a = a[1] - bx0 < lim and a[1] - a[0] > need
        ok_b = bx1 - b[0] < lim and b[1] - b[0] > need
        # le decorazioni vere sono simmetriche: si tengono solo se lo sono entrambi i lati
        if ok_a and ok_b and (keep_edges or abs((a[1] - a[0]) - (b[1] - b[0])) <= 0.35 * max(a[1] - a[0], b[1] - b[0])):
            keep = [a, b]
    tx0 = max([s[1] for s in keep if s[0] == bx0] + [bx0])
    tx1 = min([s[0] for s in keep if s[1] == bx1] + [bx1])
    # colori del testo originale
    pe = []
    for x in range(tx0, tx1):
        for y in range(h):
            c = px[x, y]
            if c[3] > 200:
                edge = any(px[min(w - 1, max(0, x + dx)), min(h - 1, max(0, y + dy))][3] < 100
                           for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                pe.append((c, edge))
    fill, outline = _text_colors(pe)
    for x in range(tx0, tx1):
        for y in range(h):
            op[x, y] = (0, 0, 0, 0)
    ow = (2 if h >= 20 else 1) if outline else 0
    _draw(out, text, (tx0 + 1, max(0, by0 - 1), tx1 - 1, min(h, by1 + 1)), fill, outline, ow)
    out.save(dst)
