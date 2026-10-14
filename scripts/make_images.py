"""Genera le immagini italiane (PNG) da inserire nelle texture: work/img_it/<archivio>/<texture>.png
Stile: lettere colorate arrotondate con contorno blu scuro e alone bianco, come il logo originale.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(__file__))

ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'work', 'img_it')
NAVY = (36, 38, 120, 255)
WHITE = (255, 255, 255, 255)
PALETTE = [(236, 30, 121), (247, 148, 29), (237, 28, 36), (0, 166, 81), (0, 114, 188),
           (146, 39, 143), (255, 194, 14), (0, 174, 239)]
FONT = r'C:\Windows\Fonts\seguibl.ttf'


def colorful_text(text, size, outline=3, halo=2, colors=PALETTE, font=FONT, spacing=0):
    """Testo multicolore con contorno scuro e alone bianco; ritorna un'immagine RGBA ritagliata."""
    f = ImageFont.truetype(font, size)
    pad = outline + halo + 4
    w = int(sum(f.getlength(c) + spacing for c in text)) + 2 * pad
    h = int(size * 1.4) + 2 * pad
    fill = Image.new('RGBA', (w, h))
    mask = Image.new('L', (w, h))
    df, dm = ImageDraw.Draw(fill), ImageDraw.Draw(mask)
    x = pad
    ci = 0
    for c in text:
        col = colors[ci % len(colors)] + (255,) if c != ' ' else None
        if col:
            df.text((x, pad), c, font=f, fill=col)
            dm.text((x, pad), c, font=f, fill=255)
            ci += 1
        x += f.getlength(c) + spacing
    out_mask = mask.filter(ImageFilter.MaxFilter(outline * 2 + 1))
    halo_mask = out_mask.filter(ImageFilter.MaxFilter(halo * 2 + 1))
    img = Image.new('RGBA', (w, h))
    img.paste(Image.new('RGBA', (w, h), WHITE), (0, 0), halo_mask)
    img.paste(Image.new('RGBA', (w, h), NAVY), (0, 0), out_mask)
    img.alpha_composite(fill)
    return img.crop(img.getbbox())


def fit(img, maxw, maxh):
    r = min(maxw / img.width, maxh / img.height, 1.0)
    return img.resize((max(1, int(img.width * r)), max(1, int(img.height * r))), Image.LANCZOS)


# --- stile logo DS EU: lettere a colori, filetto bianco interno, contorno blu scuro, alone bianco esterno (supercampionato 4x) ---
DS_FONT = os.path.join(ROOT, 'tools', 'fonts', 'Fredoka.ttf')
DS_NAVY = (38, 40, 130)


def ds_text(text, size, colors, wd=700, ow=2.2, stroke=1.0, halo=1.6, spacing=0.0):
    """RGBA ritagliato: testo DS (colori ciclici sulle lettere)."""
    import numpy as np, cv2
    S = 4
    f = ImageFont.truetype(DS_FONT, int(size * S))
    try:
        f.set_variation_by_axes([wd])
    except Exception:
        pass
    pad = int((ow + stroke + halo + 3) * S)
    w = int(sum(f.getlength(c) + spacing * S for c in text)) + 2 * pad
    h = int(size * S * 1.5) + 2 * pad
    mask = Image.new('L', (w, h)); colr = Image.new('RGB', (w, h))
    dm, dc = ImageDraw.Draw(mask), ImageDraw.Draw(colr)
    x, ci = pad, 0
    for c in text:
        if c != ' ':
            dm.text((x, pad), c, font=f, fill=255)
            dc.text((x, pad), c, font=f, fill=colors[ci % len(colors)])
            ci += 1
        x += f.getlength(c) + spacing * S
    a = (np.asarray(mask) > 127).astype(np.uint8)
    dist = cv2.distanceTransform(1 - a, cv2.DIST_L2, 5)
    out = np.zeros((h, w, 4), np.uint8)
    out[dist <= (stroke + ow + halo) * S] = (255, 255, 255, 255)
    out[dist <= (stroke + ow) * S] = (*DS_NAVY, 255)
    out[dist <= stroke * S] = (255, 255, 255, 255)
    col = np.asarray(colr)
    # riempimento: sfumatura leggera verso il basso + riflesso in alto
    ys = np.nonzero(a.any(1))[0]
    t = np.clip((np.arange(h) - ys.min()) / max(1, ys.max() - ys.min()), 0, 1)[:, None, None]
    shade = 1.0 - 0.18 * t + 0.20 * np.clip(1 - t / 0.35, 0, 1)
    fill = np.clip(col * shade, 0, 255).astype(np.uint8)
    # il filetto bianco sta fuori dalle lettere: fill solo dove a=1
    out[a > 0, :3] = fill[a > 0]
    out[a > 0, 3] = 255
    im = Image.fromarray(out, 'RGBA')
    im = im.crop(im.getbbox())
    return im.resize((max(1, im.width // S), max(1, im.height // S)), Image.LANCZOS)


DS_RED = [(228, 38, 48), (240, 120, 24), (30, 120, 210), (24, 160, 80), (150, 60, 160)]
# colori delle parole nel logo DS EU (dalla foto del gioco)
C_RED, C_YEL, C_BLU, C_SKY, C_GRN = (236, 96, 100), (250, 200, 40), (70, 120, 215), (60, 170, 235), (60, 185, 80)


def ds_word(text, size, color, rot=2.6, bounce=0.07, cap=1.14, ow=2.8, halo=1.8, seed=0, spacing=-0.02):
    """Parola 'disegnata a mano' nello stile del logo DS EU: lettere che rimbalzano e si inclinano, maiuscola piu' grande,
    riempimento a sfumatura con riflesso, contorno blu scuro spesso e alone bianco (supercampionato 6x)."""
    import numpy as np, cv2, math, random
    S = 6
    rnd = random.Random(seed + len(text))
    base = ImageFont.truetype(DS_FONT, int(size * S))
    try:
        base.set_variation_by_axes([760])
    except Exception:
        pass
    W = int(size * S * (len(text) * 0.75 + 2)); H = int(size * S * 2.2)
    mask = Image.new('L', (W, H), 0)
    x = size * S * 0.5
    for k, c in enumerate(text):
        if c == ' ':
            x += size * S * 0.28; continue
        sc = cap if k == 0 or text[k - 1] == ' ' else 1.0
        f = ImageFont.truetype(DS_FONT, int(size * S * sc))
        try:
            f.set_variation_by_axes([760])
        except Exception:
            pass
        l, t, r, b = f.getbbox(c)
        tile = Image.new('L', (r - l + 40, b - t + 40), 0)
        ImageDraw.Draw(tile).text((20 - l, 20 - t), c, font=f, fill=255)
        ang = rnd.uniform(-rot, rot) + (1.2 if k % 2 else -1.2)
        tile = tile.rotate(ang, resample=Image.BICUBIC, expand=True)
        dy = math.sin(k * 1.35 + seed) * bounce * size * S
        y = H * 0.5 - (b - t) * 0.5 + dy - (size * S * (sc - 1) * 0.0)
        mask.paste(255, (int(x - 20), int(y - 20)), tile)
        x += (r - l) + size * S * spacing
    a = (np.asarray(mask) > 127).astype(np.uint8)
    bb = np.argwhere(a)
    y0, x0 = bb.min(0); y1, x1 = bb.max(0)
    pad = int((ow + halo + 3) * S)
    a = np.pad(a[y0:y1 + 1, x0:x1 + 1], pad)
    h, w = a.shape
    dist = cv2.distanceTransform(1 - a, cv2.DIST_L2, 5)
    out = np.zeros((h, w, 4), np.uint8)
    out[dist <= (ow + halo) * S] = (255, 255, 255, 255)
    out[dist <= ow * S] = (*DS_NAVY, 255)
    ys = np.nonzero(a.any(1))[0]
    t = np.clip((np.arange(h) - ys.min()) / max(1, ys.max() - ys.min()), 0, 1)[:, None, None]
    col = np.array(color, np.float32)[None, None, :]
    shade = 1.0 + 0.30 * np.clip(1 - t / 0.5, 0, 1) - 0.22 * np.clip((t - 0.55) / 0.45, 0, 1)
    fill = np.clip(col * shade + 255 * 0.0, 0, 255)
    # filetto chiaro interno (lungo il bordo alto-sinistra) per l'effetto "gonfio"
    inner = cv2.distanceTransform(a, cv2.DIST_L2, 5)
    rim = np.clip(1 - np.abs(inner - 1.6 * S) / (1.0 * S), 0, 1)[:, :, None] * 0.35
    fill = np.clip(fill * (1 - rim) + 255 * rim, 0, 255)
    out[a > 0, :3] = np.broadcast_to(fill, (h, w, 3))[a > 0].astype(np.uint8)
    out[a > 0, 3] = 255
    im = Image.fromarray(out, 'RGBA')
    return im.resize((max(1, im.width // S), max(1, im.height // S)), Image.LANCZOS)


def ds_words(items, gap=3, ow=2.0, baseline=True, **kw):
    """items = [(testo, corpo, colore)]: parole di colore/corpo diverso sulla stessa riga (baseline in basso)"""
    ims = [ds_word(t, sz, col, ow=ow, seed=n, **kw) for n, (t, sz, col) in enumerate(items)]
    W = sum(i.width for i in ims) + gap * (len(ims) - 1)
    H = max(i.height for i in ims)
    out = Image.new('RGBA', (W, H))
    x = 0
    for im in ims:
        out.alpha_composite(im, (x, H - im.height if baseline else (H - im.height) // 2))
        x += im.width + gap
    return out


def witch_hat(h):
    """cappellino da strega azzurro (come nel logo DS EU), altezza h"""
    S = 6
    w = int(h * 1.15)
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(0.30, 0.02), (0.58, 0.40), (0.52, 0.62), (0.18, 0.62)]
    d.polygon([(x * w * S, y * h * S) for x, y in pts], fill=C_SKY + (255,))
    d.ellipse((0.02 * w * S, 0.58 * h * S, 0.98 * w * S, 0.98 * h * S), fill=C_SKY + (255,))
    d.polygon([(0.22 * w * S, 0.45 * h * S), (0.52 * w * S, 0.45 * h * S), (0.53 * w * S, 0.58 * h * S), (0.2 * w * S, 0.58 * h * S)], fill=(40, 110, 190, 255))
    import numpy as np, cv2
    a = (np.asarray(im)[:, :, 3] > 127).astype(np.uint8)
    dist = cv2.distanceTransform(1 - a, cv2.DIST_L2, 5)
    out = np.zeros((a.shape[0] + 0, a.shape[1], 4), np.uint8)
    out[dist <= 3.6 * S] = (255, 255, 255, 255)
    out[dist <= 2.0 * S] = (*DS_NAVY, 255)
    arr = np.asarray(im)
    out[a > 0] = arr[a > 0]
    r = Image.fromarray(out, 'RGBA').rotate(14, resample=Image.BICUBIC, expand=True)
    r = r.crop(r.getbbox())
    return r.resize((max(1, r.width // S), max(1, r.height // S)), Image.LANCZOS)


JP_FONT = os.path.join(ROOT, 'tools', 'fonts', 'CherrySwash.ttf')
# colori delle lettere del logo giapponese: piatti, caldi in alto, verdi/blu/viola in basso
WARM = [(236, 36, 122), (247, 136, 20), (226, 30, 44), (240, 60, 150), (247, 136, 20), (236, 36, 122), (226, 30, 44), (247, 136, 20)]
COOL = [(24, 148, 70), (96, 188, 60), (70, 130, 225), (110, 70, 175), (24, 148, 70), (96, 188, 60), (70, 130, 225), (110, 70, 175)]


def jp_letters(text, size, colors, rot=7.0, bounce=0.05, seed=1, bold=2.6, spacing=0.0):
    """lettere piatte colorate (una tinta per lettera), leggermente inclinate/rimbalzanti come nel logo giapponese.
    Ritorna (RGB, maschera L) supercampionati S=4 insieme a S."""
    import math, random
    S = 4
    rnd = random.Random(seed)
    f = ImageFont.truetype(JP_FONT, int(size * S))
    W = int(sum(f.getlength(c) for c in text) + size * S * 2); H = int(size * S * 2.0)
    rgb = Image.new('RGB', (W, H), (0, 0, 0)); mask = Image.new('L', (W, H), 0)
    x, k = size * S * 0.5, 0
    for c in text:
        l, t, r, b = f.getbbox(c)
        if c != ' ':
            tile = Image.new('L', (r - l + 60, b - t + 60), 0)
            ImageDraw.Draw(tile).text((30 - l, 30 - t), c, font=f, fill=255)
            if bold:
                import cv2, numpy as np
                tile = Image.fromarray(cv2.dilate(np.asarray(tile), np.ones((int(bold * S) | 1,) * 2, np.uint8)))
            tile = tile.rotate(rnd.uniform(-rot, rot), resample=Image.BICUBIC, expand=True)
            y = H * 0.35 + math.sin(k * 1.6 + seed) * bounce * size * S
            mask.paste(255, (int(x - 30), int(y - 30)), tile)
            col = Image.new('RGB', tile.size, colors[k % len(colors)])
            rgb.paste(col, (int(x - 30), int(y - 30)), tile)
            k += 1
        x += f.getlength(c) + size * S * spacing
    return rgb, mask, S


CREDIT_ALPHA = 0.50     # scritta nera trasparente: sempre "un po' piu' scura" dello sfondo (la citta' cambia con l'ora)


def credit_line(logo):
    """credito della patch in fondo allo schermo alto del titolo, sotto la riga del copyright (Pic_license, righe
    222-238 della texture): righe 239-248 = ultimi 9 px dello schermo (texture logo 288 colonne, colonna 144 = centro).
    Testo NERO semitrasparente invece di un colore fisso: scurisce leggermente qualunque sfondo (giorno/sera/notte)."""
    import numpy as np
    sys.path.insert(0, os.path.dirname(__file__))
    import ui_font
    root = os.path.join(os.path.dirname(__file__), '..')
    ver = open(os.path.join(root, 'VERSION'), encoding='utf-8').read().strip()
    text = f'Patch italiana di chokercrave - v{ver}'
    t = ui_font.text(text, (0, 0, 0), 8, ow=0, spacing=1)       # < ui_font.SMALL: font pixel del gioco, nitido
    a = np.asarray(t.getchannel('A')).astype(float) * CREDIT_ALPHA
    t.putalpha(Image.fromarray(a.astype(np.uint8), 'L'))
    logo.alpha_composite(t, (144 - t.width // 2, 247 - t.height))    # ultima riga del testo = 246 (lo schermo finisce a 248)


def title_logo(src0, src1, dst0, dst1):
    """Logo 288x256 (texture 256 + 32) nello stile del logo giapponese: lettere piatte e colorate, una grande targa bianca
    unica con bordo blu scuro, stemma del castello sopra, cappello azzurro. Titolo inglese (filone DS EU)."""
    import numpy as np, cv2
    a = Image.open(src0).convert('RGBA'); b = Image.open(src1).convert('RGBA')
    full = Image.new('RGBA', (a.width + b.width, a.height))
    full.paste(a, (0, 0)); full.paste(b, (a.width, 0))
    W, H = full.size
    S = 4
    cvs_rgb = Image.new('RGB', (W * S, H * S), (0, 0, 0)); cvs_mask = Image.new('L', (W * S, H * S), 0)

    def put(rgb, mask, cx, y, scale=1.0):
        bb = mask.getbbox()
        rgb, mask = rgb.crop(bb), mask.crop(bb)
        k = scale * W * S / max(W * S, 1)
        if scale != 1.0:
            rgb = rgb.resize((int(rgb.width * scale), int(rgb.height * scale)), Image.LANCZOS)
            mask = mask.resize(rgb.size, Image.LANCZOS)
        cvs_rgb.paste(rgb, (int(cx * S - rgb.width / 2), int(y * S)), mask)
        cvs_mask.paste(255, (int(cx * S - rgb.width / 2), int(y * S)), mask)
        return rgb.width / S, rgb.height / S

    def fitw(rgb, mask, maxw):
        bb = mask.getbbox(); w = (bb[2] - bb[0]) / S
        return min(1.0, maxw / w)

    r1 = jp_letters('Enchanted', 62, WARM, seed=3)
    r2a = jp_letters('and the', 30, [(60, 60, 150)], seed=5, rot=4)
    r2b = jp_letters('Folk', 62, WARM[3:] + WARM[:3], seed=7)
    r3a = jp_letters('Magic', 64, COOL, seed=9)
    r3b = jp_letters('Town', 64, COOL[2:] + COOL[:2], seed=11)
    y = 93
    hy = y
    w, h = put(r1[0], r1[1], W / 2 - 30, y, fitw(r1[0], r1[1], 204)); y += h - 6
    # riga 2: "and the" piccolo + "Folk" + cappello
    sc = fitw(r2b[0], r2b[1], 130)
    wb, hb = put(r2b[0], r2b[1], W / 2 + 34, y, sc)
    put(r2a[0], r2a[1], W / 2 - 70, y + hb * 0.45, 0.9)
    # cappello da strega azzurro (come nel logo giapponese), in alto a destra, inclinato
    hs = Image.new('L', (60 * S, 60 * S), 0); hd = ImageDraw.Draw(hs)
    hd.polygon([(14 * S, 40 * S), (26 * S, 8 * S), (34 * S, 6 * S), (30 * S, 18 * S), (44 * S, 38 * S)], fill=255)   # cono con punta piegata
    hd.ellipse((4 * S, 34 * S, 56 * S, 52 * S), fill=255)                                                           # tesa
    hs = hs.rotate(-16, resample=Image.BICUBIC, expand=True)
    hs = hs.resize((int(hs.width * 0.8), int(hs.height * 0.8)), Image.LANCZOS).point(lambda v: 255 if v > 110 else 0)
    hcol = Image.new('RGB', hs.size, (146, 194, 244))
    hpx, hpy = W * S - hs.width - 6 * S, int((hy - 8) * S)
    cvs_rgb.paste(hcol, (hpx, hpy), hs); cvs_mask.paste(255, (hpx, hpy), hs)
    y += hb - 10
    w1, h1 = r3a[1].getbbox()[2] - r3a[1].getbbox()[0], 0
    tot = (r3a[1].getbbox()[2] - r3a[1].getbbox()[0] + r3b[1].getbbox()[2] - r3b[1].getbbox()[0]) / S + 10
    sc3 = min(1.0, 262 / tot)
    wa, ha = put(r3a[0], r3a[1], W / 2 - tot * sc3 / 2 + (r3a[1].getbbox()[2] - r3a[1].getbbox()[0]) / S * sc3 / 2, y, sc3)
    put(r3b[0], r3b[1], W / 2 + tot * sc3 / 2 - (r3b[1].getbbox()[2] - r3b[1].getbbox()[0]) / S * sc3 / 2, y + 2, sc3)
    # targa bianca unica + bordo blu scuro attorno a tutto il testo
    m = (np.asarray(cvs_mask) > 127).astype(np.uint8)
    dist = cv2.distanceTransform(1 - m, cv2.DIST_L2, 5)
    out = np.zeros((H * S, W * S, 4), np.uint8)
    out[dist <= 10.0 * S] = (*DS_NAVY, 255)
    out[dist <= 5.2 * S] = (255, 255, 255, 255)
    rgb = np.asarray(cvs_rgb)
    out[m > 0, :3] = rgb[m > 0]; out[m > 0, 3] = 255
    big = Image.fromarray(out, 'RGBA').resize((W, H), Image.LANCZOS)
    logo = Image.new('RGBA', (W, H))
    crest = full.crop((0, 0, W, 87))
    import numpy as np
    ca = np.asarray(crest).copy()                               # niente sfumatura: sotto il taglio la base si prolunga in blu navy fino alla targa
    ca[68:87, 219:, 3] = 0                                      # collina destra (resto della vecchia targa): via, il cappello occupa quel lato
    base = ca[78:87, :, 3].max(axis=0)
    ext = np.zeros((14, W, 4), np.uint8)
    ext[:, :, 0], ext[:, :, 1], ext[:, :, 2] = 17, 34, 136
    ext[:, :, 3] = base * (np.asarray(big.getchannel('A'))[100, :] > 200)[None, :]   # solo sopra la targa vera (niente lastra fuori)
    crest = Image.fromarray(np.vstack([ca, ext]), 'RGBA')
    logo.alpha_composite(crest, (0, 0))                          # stemma del castello (sagoma blu scuro) dietro la targa
    logo.alpha_composite(big)
    bb = logo.getchannel('A').getbbox()                          # logo un po' piu' piccolo e centrato come l'originale (centro 144,128)
    tgt_w = 250.0
    sc = tgt_w / (bb[2] - bb[0])
    part = logo.crop(bb)
    part = part.resize((round(part.width * sc), round(part.height * sc)), Image.LANCZOS)
    logo = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    logo.alpha_composite(part, (W // 2 - part.width // 2, 128 - part.height // 2))
    # credit_line(logo)   # credito spostato sullo schermo basso (make_title_credit.py)
    logo.crop((0, 0, a.width, H)).save(dst0)
    logo.crop((a.width, 0, W, H)).save(dst1)
    logo.save(dst0.replace('.png', '_anteprima.png'))


STAR_C = (64, 32)     # centro del gruppo di stelline (simmetriche: x 12/116, y 9-55)
# stelline (cx, cy, raggio): tre per lato, simmetriche rispetto a x=64; quella in alto a destra e' disegnata
# sopra la scritta, altrimenti il bordo del fiocchetto la coprirebbe
STARS_UNDER = ((12, 31, 9), (116, 33, 9), (21, 9, 4), (20, 54, 5), (108, 55, 4))
STARS_OVER = ((107, 9, 4),)
BOW_AT = (102, 12)    # centro del fiocchetto: angolo in alto a destra della "o" di "lo"
BOW_SCALE = 0.55


def _bow(orig):
    """il fiocchetto rosa del logo giapponese (riquadro 71-98 x 9-34, solo i pixel rosa: niente を giallo ne' ん),
    ridotto di BOW_SCALE; senza contorno: lo prende dal contorno comune della scritta (come nell'originale)"""
    import numpy as np, cv2
    a = np.asarray(orig.crop((71, 9, 98, 34)).convert('RGBA')).astype(int)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    pink = (al > 128) & (r > 200) & (b > 70) & (g < 190) & (r - g > 60)
    n, lab, st, _ = cv2.connectedComponentsWithStats(pink.astype(np.uint8), connectivity=8)
    keep = np.zeros_like(pink)
    if n > 1:
        big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        for i in range(1, n):          # il fiocco e' il pezzo piu' grande + i pezzi vicini (ali staccate)
            if i == big or st[i, cv2.CC_STAT_AREA] >= 6:
                keep |= lab == i
    # prima si riduce il fiocco, poi si disegna il contorno alla dimensione finale (resta netto)
    ys, xs = np.nonzero(keep)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgba = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
    rgba[..., :3] = a[y0:y1, x0:x1, :3]
    rgba[..., 3] = keep[y0:y1, x0:x1] * 255
    pim = Image.fromarray(rgba, 'RGBA')
    pim = pim.resize((max(1, round(pim.width * BOW_SCALE)), max(1, round(pim.height * BOW_SCALE))), Image.LANCZOS)
    return pim


def touch_icon(src_png, dst):
    """'がめんをタッチ!!' -> 'Tocca lo schermo!' nello stile del logo giapponese (lettere piatte, targa bianca, bordo blu);
    le stelline ai lati sono quelle dell'originale."""
    import numpy as np, cv2
    orig = Image.open(src_png).convert('RGBA')
    w, h = orig.size
    S = 4
    cvs_rgb = Image.new('RGB', (w * S, h * S), (0, 0, 0)); cvs_mask = Image.new('L', (w * S, h * S), 0)

    def put(rgb, mask, cx, y, maxw, maxh):
        bb = mask.getbbox()
        rgb, mask = rgb.crop(bb), mask.crop(bb)
        sc = min(1.0, maxw * S / rgb.width, maxh * S / rgb.height)
        if sc != 1.0:
            rgb = rgb.resize((int(rgb.width * sc), int(rgb.height * sc)), Image.LANCZOS)
            mask = mask.resize(rgb.size, Image.LANCZOS)
        x0 = int(cx * S - rgb.width / 2)
        cvs_rgb.paste(rgb, (x0, int(y * S)), mask); cvs_mask.paste(255, (x0, int(y * S)), mask)
        return rgb.height / S

    a = jp_letters('Tocca lo', 30, [(236, 36, 122), (247, 136, 20), (24, 148, 70), (70, 130, 225)], seed=21, bold=2.0)
    b = jp_letters('schermo!', 30, [(70, 130, 225), (110, 70, 175), (24, 148, 70), (236, 36, 122), (247, 136, 20)], seed=23, bold=2.0)
    ha = put(a[0], a[1], w / 2, 9, 80, 27)          # un po' piu' grande
    put(b[0], b[1], w / 2, 9 + ha - 1, 86, 28)
    # scritta centrata (orizzontale e verticale) sul centro del gruppo di stelline (STAR_C)
    bb = cvs_mask.getbbox()
    dx = round(STAR_C[0] * S - (bb[0] + bb[2]) / 2)
    dy = round(STAR_C[1] * S - (bb[1] + bb[3]) / 2)
    r2 = Image.new('RGB', cvs_rgb.size, (0, 0, 0)); m2 = Image.new('L', cvs_mask.size, 0)
    r2.paste(cvs_rgb, (dx, dy)); m2.paste(cvs_mask, (dx, dy))
    cvs_rgb, cvs_mask = r2, m2
    # fiocchetto rosa dell'originale sull'angolo in alto a destra della "o" di "lo": entra nella maschera comune,
    # quindi niente bordo blu fra fiocco e lettere (solo fuori), e un filo bianco lo separa dalla lettera
    bow = _bow(orig)
    bow = bow.resize((bow.width * S, bow.height * S), Image.LANCZOS)
    bm = bow.getchannel('A').point(lambda v: 255 if v > 110 else 0)
    bx, by = BOW_AT[0] * S - bow.width // 2, BOW_AT[1] * S - bow.height // 2
    mt = (np.asarray(cvs_mask) > 127).astype(np.uint8)            # solo lettere
    halo_w = bm.filter(ImageFilter.MaxFilter(S + 1))                 # filo bianco sottile fra fiocco e lettera
    cvs_rgb.paste((255, 255, 255), (bx, by), halo_w)
    cvs_rgb.paste(bow.convert('RGB'), (bx, by), bm)
    fb = Image.new('L', cvs_mask.size, 0)
    fb.paste(255, (bx, by), halo_w)
    mb = (np.asarray(fb) > 127).astype(np.uint8)                       # fiocco (+ filo)
    m = mt | mb
    dt = cv2.distanceTransform(1 - mt, cv2.DIST_L2, 5)
    db = cv2.distanceTransform(1 - mb, cv2.DIST_L2, 5)
    out = np.zeros((h * S, w * S, 4), np.uint8)
    # contorno comune (niente blu fra fiocco e lettere); sul fiocco il bianco e' piu' stretto (1.5 px invece di 3)
    out[(dt <= 5.5 * S) | (db <= 3.5 * S)] = (*DS_NAVY, 255)
    out[(dt <= 3.0 * S) | (db <= 1.5 * S)] = (255, 255, 255, 255)
    rgb = np.asarray(cvs_rgb)
    out[m > 0, :3] = rgb[m > 0]; out[m > 0, 3] = 255
    canvas = Image.fromarray(out, 'RGBA').resize((w, h), Image.LANCZOS)
    # stelline a quattro punte (blu scuro con bordo bianco) ai lati, come nell'originale
    import math

    def stars(lst):
        SS = 8
        st = Image.new('L', (w * SS, h * SS), 0); sd = ImageDraw.Draw(st)
        for cx, cy, r in lst:
            pts = []
            for k in range(8):
                ang = math.pi / 4 * k - math.pi / 2
                rr = r if k % 2 == 0 else r * 0.32
                pts.append(((cx + rr * math.cos(ang)) * SS, (cy + rr * math.sin(ang)) * SS))
            sd.polygon(pts, fill=255)
        sa = np.asarray(st) > 127
        sdist = cv2.distanceTransform((~sa).astype(np.uint8), cv2.DIST_L2, 5)
        so = np.zeros((h * SS, w * SS, 4), np.uint8)
        so[sdist <= 1.6 * SS] = (255, 255, 255, 255)
        so[sa] = (*DS_NAVY, 255)
        return Image.fromarray(so, 'RGBA').resize((w, h), Image.LANCZOS)

    final = Image.new('RGBA', (w, h))
    final.alpha_composite(stars(STARS_UNDER))
    final.alpha_composite(canvas)
    final.alpha_composite(stars(STARS_OVER))     # quella in alto a destra sta sopra al bordo del fiocco
    final.save(dst)


MAIN_BUTTONS = ['Continua', 'Iscriviti', 'Altro', 'Cancella dati', 'Cambia scritte', 'Dati',
                'Trasferisciti', 'Cancella scuola', 'Cancella giocatore', 'Invia', 'Accogli',
                'Esporta dati', 'Regali', 'SpotPass', 'Riconoscimenti', None, 'Esci', 'Torna',
                'Vai a Zona Tongari']
# pulsanti col testo giapponese troppo lungo: lo sfondo si ricostruisce da un pulsante "pulito"
# della stessa forma (indice del modello), ricolorato con i toni del pulsante di destinazione
TEMPLATE = {26: 4, 27: 5, 36: 4, 37: 5, 34: 32, 35: 33}


def _two_tones(im, box):
    """i due colori più frequenti (toni del motivo a rombi) dentro box"""
    from collections import Counter
    px = im.load()
    c = Counter(px[x, y][:3] for x in range(box[0], box[2]) for y in range(box[1], box[3]))
    (a, _), (b, _) = c.most_common(2)
    return (a, b) if sum(a) < sum(b) else (b, a)


def recolor_from_template(target_png, template_clean, dst_tmp):
    """Copia la fascia centrale del modello pulito sostituendo i due toni con quelli del target."""
    t = Image.open(target_png).convert('RGBA')
    m = Image.open(template_clean).convert('RGBA')
    w, h = t.size
    tp = t.load()
    opaque = [x for x in range(w) if tp[x, h // 2][3] > 200]
    bx0, bx1 = opaque[0], opaque[-1]
    bw = bx1 - bx0
    rows = [y for y in range(h) if tp[(bx0 + bx1) // 2, y][3] > 200]
    m0 = max(6, bw // 11)
    box = (bx0 + bw // 4, rows[0] + 3, bx1 - bw // 4, rows[-1] - 3)
    (ta, tb), (ma, mb) = _two_tones(t, (bx0 + m0, rows[0] + 3, bx0 + m0 + 14, rows[-1] - 3)), _two_tones(m, box)
    out = t.copy()
    op, mp = out.load(), m.load()
    for x in range(bx0 + m0 + 6, bx1 - m0 - 5):
        for y in range(rows[0] + 1, rows[-1]):
            r, g, b, a = mp[x, y]
            # interpolazione lineare sulla luminosità tra i due toni del modello
            lm = lambda c: c[0] + c[1] + c[2]
            k = (lm((r, g, b)) - lm(ma)) / max(1, lm(mb) - lm(ma))
            k = min(1.2, max(-0.2, k))
            op[x, y] = tuple(int(min(255, max(0, ta[i] + k * (tb[i] - ta[i])))) for i in range(3)) + (a,)
    out.save(dst_tmp)


def _period(row):
    """periodo orizzontale del motivo di sfondo (autocorrelazione su una riga pulita)"""
    best, bp = None, 16
    for p in range(8, 40):
        err = sum(sum(abs(a - b) for a, b in zip(row[i], row[i + p])) for i in range(len(row) - p))
        err /= (len(row) - p)
        if best is None or err < best:
            best, bp = err, p
    return bp


def plain_button(src, text, dst, font_size=19, clean_bg=None):
    im = Image.open(src).convert('RGBA')
    text_src = im
    if clean_bg:
        im = Image.open(clean_bg).convert('RGBA')
    w, h = im.size
    px = im.load()
    # zona del testo: colonne con pixel molto scuri o molto chiari (testo e bordo) al centro
    opaque = [x for x in range(w) if px[x, h // 2][3] > 200]
    bx0, bx1 = opaque[0], opaque[-1]
    bw = bx1 - bx0
    lum = lambda c: (c[0] * 3 + c[1] * 6 + c[2]) // 10
    rows = [y for y in range(h) if px[(bx0 + bx1) // 2, y][3] > 200]
    iy0, iy1 = rows[0] + 3, rows[-1] - 3
    # sfondo atteso: motivo periodico preso dalla zona subito dopo la spirale sinistra
    r0 = bx0 + max(8, bw // 9)
    ref = [px[x, (iy0 + iy1) // 2] for x in range(r0, r0 + 44)]
    P = _period(ref)
    tpx = text_src.load()
    tref = [tpx[x, (iy0 + iy1) // 2] for x in range(r0, r0 + 44)]
    tP = _period(tref)
    diff = []
    for x in range(r0 + 44, bx1 - max(8, bw // 9)):
        for y in range(iy0, iy1 + 1):
            a = tpx[x, y]; b = tpx[r0 + (x - r0) % tP, y]
            if sum(abs(a[i] - b[i]) for i in range(3)) > 90:
                diff.append((x, y))
    # si ridipinge tutta la fascia tra le spirali, righe comprese tra i bordi del pulsante
    tx0, tx1 = r0 + P, bx1 - (r0 - bx0)
    ty0, ty1 = rows[0], rows[-1]
    # colore del testo: il più saturo/scuro tra i pixel diversi dallo sfondo (escluso il bordo crema)
    cand = [tpx[x, y] for x, y in diff if lum(tpx[x, y]) < 200]
    fill_col = sorted(cand, key=lum)[len(cand) // 4] if cand else (60, 60, 120, 255)
    clean = im.copy()
    cp = clean.load()
    if not clean_bg:
        for x in range(tx0, tx1 + 1):
            sx = r0 + (x - r0) % P
            for y in range(ty0, ty1 + 1):
                cp[x, y] = px[sx, y]
    # testo italiano nel font UI scelto (Grandstander, stile foto): tratto scuro del colore del pulsante + contorno crema
    import ui_font
    maxw = bw - 2 * max(10, bw // 7)
    cap = SIZE_CAP.get(bw, 24)                          # stessa dimensione per tutti i pulsanti della stessa larghezza
    timg = ui_font.fit(text, tuple(fill_col[:3]), maxw, (iy1 - iy0) + 2, px_max=cap, px_min=9, squeeze=0.8,
                       outline=(255, 251, 225), ow=2.0)
    SIZE_REC.setdefault(bw, []).append(ui_font.LAST_PX)
    layer = Image.new('RGBA', (w, h))
    cx, cy = (bx0 + bx1) / 2, (ty0 + ty1) / 2
    layer.alpha_composite(timg, (int(round(cx - timg.width / 2)), int(round(cy - timg.height / 2))))
    clean.alpha_composite(layer)
    clean.save(dst)


SIZE_CAP, SIZE_REC = {}, {}


def main_menu(src_dir, out_dir):
    main_menu_pass(src_dir, out_dir)                              # passo 1: misura
    SIZE_CAP.update({k: min(v) for k, v in SIZE_REC.items()})
    main_menu_pass(src_dir, out_dir)                              # passo 2: dimensione uniforme per larghezza


def main_menu_pass(src_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for i, text in enumerate(MAIN_BUTTONS):
        if not text:
            continue
        for v in (0, 1):
            k = 2 * i + v
            n = f'main_btn_{k:02d}'
            src = os.path.join(src_dir, f'mainmenu.arc__timg_{n}.png')
            bg = None
            if k in TEMPLATE:
                tmp = os.path.join(out_dir, '_tmp')
                os.makedirs(tmp, exist_ok=True)
                tpl = os.path.join(src_dir, f'mainmenu.arc__timg_main_btn_{TEMPLATE[k]:02d}.png')
                plain_button(tpl, '', os.path.join(tmp, 'tpl.png'))
                bg = os.path.join(tmp, f'bg_{k}.png')
                recolor_from_template(src, os.path.join(tmp, 'tpl.png'), bg)
            plain_button(src, text, os.path.join(out_dir, n + '.png'), clean_bg=bg)


if __name__ == '__main__':
    main_menu(os.path.join(ROOT, 'work', 'img', 'mainmenu'), os.path.join(OUT, 'menu_mainmenu'))
    src = os.path.join(ROOT, 'work', 'img', 'title_d')
    out = os.path.join(OUT, 'menu_title')
    os.makedirs(out, exist_ok=True)
    touch_icon(os.path.join(src, 'title.arc__timg_touch_icon_logo.png'), os.path.join(out, 'touch_icon_logo.png'))
    title_logo(os.path.join(src, 'title.arc__timg_title_logo_00.png'), os.path.join(src, 'title.arc__timg_title_logo_01.png'),
               os.path.join(out, 'title_logo_00.png'), os.path.join(out, 'title_logo_01.png'))
    print('ok')
