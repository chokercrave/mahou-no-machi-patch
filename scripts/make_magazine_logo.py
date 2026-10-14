"""Logo della rivista: "Berry's" -> "Spell & Spill", stesso stile dell'originale
(ui/menu_magazine 000.bin timg/berry's_logo, 128x128): lettere tonde rosa acceso, contorno bianco spesso,
bordo rosa sottile, leggera ombra grigia, testo inclinato verso l'alto. Font: Lobster (scelto fra 8 opzioni,
work/ref_font/logo_opzioni.png).
Uscita: work/img_it/_auto/menu_magazine/000.bin__timg_berry's_logo.png (installato da build_images.py)
  python make_magazine_logo.py [anteprima.png]
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.join(os.path.dirname(__file__), '..')
SRC = os.path.join(ROOT, 'work', 'img', 'ui', 'menu_magazine', "000.bin__timg_berry's_logo.png")
OUT = os.path.join(ROOT, 'work', 'img_it', '_auto', 'menu_magazine', "000.bin__timg_berry's_logo.png")
FONT = os.path.join(ROOT, 'tools', 'fonts', 'Lobster.ttf')    # (opzione B)
LINES = ['Spell &', 'Spill']
PINK = (232, 40, 140)          # riempimento delle lettere (misurato sull'originale)
EDGE = (226, 34, 136)          # bordo esterno sottile
WHITE = (255, 255, 255)
SHADE = (208, 204, 216)        # ombra grigio-lilla tra lettere e contorno
ANGLE = 34                     # gradi, verso l'alto come "Berry's"
S = 8                          # supercampionamento


def disk(mask, r):
    """dilatazione rotonda di r px (in px supercampionati)"""
    import numpy as np, cv2
    a = (np.asarray(mask) > 127).astype(np.uint8)
    dist = cv2.distanceTransform(1 - a, cv2.DIST_L2, 5)
    return Image.fromarray(((dist <= r) * 255).astype(np.uint8))


def render(font=FONT, weight=None, sizes=(34, 44)):
    # righe centrate, la seconda un po' più grande (come le lettere irregolari dell'originale)
    lay = Image.new('L', (200 * S, 120 * S), 0)
    d = ImageDraw.Draw(lay)
    y = 4 * S
    for i, t in enumerate(LINES):
        fi = ImageFont.truetype(font, int(sizes[i] * S))
        if weight:
            try:
                fi.set_variation_by_name(weight)
            except Exception:
                pass
        l, tp, r, b = fi.getbbox(t)
        x = (lay.width - (r - l)) // 2 - l + (-10 * S if i == 0 else 10 * S)   # sfalsate come in diagonale
        d.text((x, y - tp), t, font=fi, fill=255)
        y += (b - tp) - 2 * S
    lay = lay.crop(lay.getbbox())
    pad = 12 * S
    m = Image.new('L', (lay.width + 2 * pad, lay.height + 2 * pad), 0)
    m.paste(lay, (pad, pad))
    m = m.rotate(ANGLE, resample=Image.BICUBIC, expand=True)
    m = m.crop(m.getbbox())
    p2 = 8 * S                                  # spazio per contorno e bordo dopo la rotazione
    big = Image.new('L', (m.width + 2 * p2, m.height + 2 * p2), 0); big.paste(m, (p2, p2)); m = big
    # strati: bordo rosa (più esterno) > bianco > ombra > lettere
    white = disk(m, 4.5 * S)
    edge = disk(m, 5.5 * S)
    shade = disk(m, 1.6 * S)
    W, H = m.size
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    canvas.paste(EDGE + (255,), (0, 0), edge)
    canvas.paste(WHITE + (255,), (0, 0), white)
    # ombra spostata in basso a destra, solo dentro il bianco
    sh = Image.new('L', (W, H), 0)
    sh.paste(shade, (int(1.2 * S), int(1.5 * S)))
    canvas.paste(SHADE + (255,), (0, 0), sh)
    canvas.paste(PINK + (255,), (0, 0), m)
    # riduzione a 128x128 mantenendo le proporzioni, centrata come l'originale
    k = min(122 / (W / S), 122 / (H / S)) / S
    small = canvas.resize((max(1, round(W * k)), max(1, round(H * k))), Image.LANCZOS)
    out = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
    out.alpha_composite(small, ((128 - small.width) // 2, (128 - small.height) // 2))
    return out


if __name__ == '__main__':
    out = render()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    out.save(OUT)
    if len(sys.argv) > 1:
        orig = Image.open(SRC).convert('RGBA')
        sheet = Image.new('RGBA', (128 * 2 + 8, 128), (120, 120, 120, 255))
        sheet.alpha_composite(orig, (0, 0)); sheet.alpha_composite(out, (136, 0))
        sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(sys.argv[1])
    print('->', OUT)
