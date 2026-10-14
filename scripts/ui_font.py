"""Scritte UI nello stile della foto di riferimento (work/ref_font/menu_photo.jpg, menu del titolo 3DS):
lettere pixel SENZA sfumature, tratto scuro del colore del pulsante, contorno bianco spesso (effetto adesivo),
spaziatura un po' larga. Font: Grandstander (variabile, peso Regular), "B" nel confronto
work/ref_font/scelta_font.png. Regola: tutte le UI NUOVE usano questo; quelle già fatte si rifanno alla fine.

  python ui_font.py sample <out.png>                   prova (alfabeto, accenti, parole del menu)
Uso:  import ui_font;  img = ui_font.text('Continua', fill=(150, 40, 50), px=20)
      img = ui_font.fit('Riconoscimenti', (150, 40, 50), max_w=120, max_h=22)   # px più grande che ci sta
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.join(os.path.dirname(__file__), '..')
FONT = os.path.join(ROOT, 'tools', 'fonts', 'Grandstander.ttf')
SMOOTH = True               # glifi con bordo antialias (troppo pixelato fra lettera e contorno)
WEIGHT = 'Regular'          # tratto ~2 px a 18-22 px, come nella foto
S = 8                       # supercampionamento: i font variabili hanno contorni sovrapposti, senza AA
                            # FreeType li riempirebbe "a buchi"; si disegna a 8x e si riduce con soglia
_cache = {}


def _font(px, weight=None):
    key = (px, weight or WEIGHT)
    if key not in _cache:
        f = ImageFont.truetype(FONT, px * S)
        f.set_variation_by_name(weight or WEIGHT)
        _cache[key] = f
    return _cache[key]


SMALL = 14     # sotto questa altezza Grandstander diventa illeggibile: si usano i font pixel del 3DS
_BCF = {}


def _bcfnt(name):
    if name not in _BCF:
        import bcfnt
        p = os.path.join(ROOT, 'work', 'font', name)
        f = bcfnt.Bcfnt(open(p, 'rb').read())
        f._cache = [f.sheet_pixels(i) for i in range(f.nsheets)]
        _BCF[name] = f
    return _BCF[name]


def core_small(s, px, spacing=1):
    """testo piccolo coi font del gioco (già italianizzati): DF_kyougeki 13 px, LC 11 px; pixel netti"""
    f = _bcfnt('DF_kyougeki.bcfnt' if px >= 12 else 'LC.bcfnt')
    x, parts = 0, []
    for ch in s:
        g = f.cmap.get(ord(ch), f.alter_idx)
        l, gw, adv = f.widths[g][2] if g in f.widths else f.default_width
        cell = f.glyph_cell(g, f._cache)
        im = Image.new('L', (f.cell_w, f.cell_h))
        im.putdata([(v & 15) * 17 for row in cell for v in row])     # LA4: alfa nel nibble basso; antialias vero, come in gioco
        parts.append((x + l, im))
        x += adv + spacing
    out = Image.new('L', (max(1, x), f.cell_h), 0)
    for gx, im in parts:
        out.paste(255, (gx, 0), im)                  # (maschera in scala di grigi: bordi morbidi)
    bb = out.getbbox()
    return out.crop(bb) if bb else out


def core(s, px, spacing=2, threshold=110, weight=None, xs=1.0):
    """maschera L 0/255 del testo (pixel netti)"""
    if px < SMALL:
        return core_small(s, px, 1 if spacing >= 1 else 0)
    f = _font(px, weight)
    l, t, r, b = f.getbbox(s)
    m = Image.new('L', (r - l + 4 * S + spacing * S * len(s), b - t + 4 * S), 0)
    d = ImageDraw.Draw(m)
    x = S - l
    for ch in s:
        d.text((x, S - t), ch, font=f, fill=255)
        x += f.getlength(ch) + spacing * S
    small = m.resize((m.width // S, m.height // S), Image.BOX)
    if SMOOTH:       # bordo antialias (rampa 70..190): le lettere non hanno piu' gradini a contatto col contorno
        small = small.point(lambda v: 0 if v <= 70 else (255 if v >= 190 else int((v - 70) * 255 / 120)))
    else:
        small = small.point(lambda v: 255 if v >= threshold else 0)
    if xs != 1.0:                    # testo condensato (titoli lunghi): lettere piu' alte a parita' di larghezza
        small = small.resize((max(1, round(small.width * xs)), small.height), Image.BOX if xs < 1 else Image.BILINEAR)
    bb = small.getbbox()
    return small.crop(bb) if bb else small


def halo(mask, ow, soft=1.0):
    """contorno ROTONDO attorno alla maschera: distanza euclidea dai pixel delle lettere, bordo esterno
    sfumato su `soft` px (non a gradini come una dilatazione quadrata). Restituisce alfa L 0..255."""
    import numpy as np, cv2
    inside = (np.asarray(mask) > 100).astype(np.uint8)          # (i font piccoli hanno bordi antialias)
    dist = cv2.distanceTransform(1 - inside, cv2.DIST_L2, 5)          # px dal tratto più vicino
    a = np.clip((ow + 0.5 + soft / 2 - dist) / max(soft, 1e-3), 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8))


def text(s, fill=(40, 40, 120), px=20, outline=(255, 255, 255), ow=2.5, spacing=2, soft=1.5, weight=None, xs=1.0):
    """RGBA: tratto scuro `fill` (pixel netti) + contorno `outline` rotondo di `ow` px con bordo esterno
    sfumato di `soft` px (0 = netto); ritagliato al contenuto"""
    c = core(s, px, spacing, weight=weight, xs=xs)
    pad = int(ow + soft) + 2
    canvas = Image.new('L', (c.width + 2 * pad, c.height + 2 * pad), 0)
    canvas.paste(c, (pad, pad))
    out = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    if ow:
        out.paste(outline + (255,), (0, 0), halo(canvas, ow, soft))
    out.paste(fill + (255,), (0, 0), canvas)
    return out.crop(out.getbbox())


def lines(s, fill=(40, 40, 120), px=20, leading=-2, align='center', **kw):
    """più righe ('\\n'), centrate; leading = px tra una riga e l'altra (i contorni si sovrappongono)"""
    ims = [text(t, fill, px, **kw) for t in s.split('\n')]
    if len(ims) == 1:
        return ims[0]
    W = max(i.width for i in ims)
    H = sum(i.height for i in ims) + leading * (len(ims) - 1)
    out = Image.new('RGBA', (W, max(1, H)), (0, 0, 0, 0))
    y = 0
    for i in ims:
        x = (W - i.width) // 2 if align == 'center' else 0
        out.alpha_composite(i, (x, max(0, y)))
        y += i.height + leading
    return out


def fit(s, fill, max_w, max_h, px_max=24, px_min=9, squeeze=1.0, **kw):
    """come text()/lines(), alla dimensione più grande che entra in max_w x max_h.
    squeeze < 1: puo' stringere le lettere in orizzontale fino a quel fattore (titoli lunghi)"""
    global LAST_PX
    for px in range(px_max, px_min - 1, -1):
        im = lines(s, fill, px, **kw)
        if im.width <= max_w and im.height <= max_h:
            LAST_PX = px
            return im
        if squeeze < 1.0 and im.height <= max_h and chr(10) not in s and im.width * squeeze <= max_w:
            LAST_PX = px
            return lines(s, fill, px, xs=max(squeeze, (max_w - 6) / im.width), **kw)
    LAST_PX = px_min
    return lines(s, fill, px_min, **kw)


LAST_PX = 0


if __name__ == '__main__' and len(sys.argv) > 2 and sys.argv[1] == 'sample':
    lines = [('ABCDEFGHIJKLMNOPQRSTUVWXYZ', (40, 40, 120)), ('abcdefghijklmnopqrstuvwxyz', (150, 40, 50)),
             ('àèéìòù ÀÈÉÌÒÙ 0123456789 !?.,:;\'"-()«»', (10, 80, 70)),
             ('Continua  Iscriviti  Dati  Altro  Esci', (70, 40, 170))]
    ims = [text(t, c, 20) for t, c in lines]
    sheet = Image.new('RGBA', (max(i.width for i in ims) + 16, sum(i.height + 6 for i in ims) + 10), (232, 208, 176, 255))
    y = 6
    for i in ims:
        sheet.alpha_composite(i, (8, y)); y += i.height + 6
    sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(sys.argv[2])
