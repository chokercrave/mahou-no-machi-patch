"""Targhette dei titoli del libretto (menu Start, ui/menu_status.tarc → status.arc: timg/status_plate01..05):
icona a sinistra, testo, ricciolo a destra. Si ridipinge solo la fascia del testo col colore di fondo
e si scrive il titolo italiano col colore del testo originale.
Output: work/img_it/menu_status/status_plateNN.png (installati da build_images.py, gruppo menu_status)
"""
import collections, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from relabel import _draw, _lum

ROOT = os.path.join(os.path.dirname(__file__), '..')
SRC = os.path.join(ROOT, 'work', 'img', 'ui', 'menu_status')
OUT = os.path.join(ROOT, 'work', 'img_it', 'menu_status')
TITOLI = {
    'status_plate01': 'Profilo',        # じぶんのこと
    'status_plate02': 'Magie',          # まほう
    'status_plate03': 'Incanti',        # おまじない
    'status_plate04': 'Messaggi',       # でんぽう
    'status_plate05': 'Amici',          # おともだち
}


CX, CY = 131, 22                  # centro comune del testo (originale: x 130-131, righe 13-30)
MAXW, MAXH = 74, 16


def main():
    import ui_font
    os.makedirs(OUT, exist_ok=True)
    ui_font.SMALL = 9
    # passo 1: dimensione UNICA per tutte le targhette (la piu' grande che entra in tutte)
    px_all = min(next(px for px in range(20, 8, -1)
                      if ui_font.text(t, (0, 0, 0), px, ow=0, spacing=1).size[0] <= MAXW
                      and ui_font.text(t, (0, 0, 0), px, ow=0, spacing=1).size[1] <= MAXH) for t in TITOLI.values())
    for name, text in TITOLI.items():
        im = Image.open(os.path.join(SRC, f'status.arc__timg_{name}.png')).convert('RGBA')
        px = im.load()
        w, h = im.size
        x0, x1 = 92, 172
        rows = [y for y in range(h) if px[x0 + 2, y][3] > 200 and _lum(px[x0 + 2, y]) > 200]
        y0, y1 = min(rows), max(rows)
        bg = collections.Counter(px[x, y][:3] for x in range(x0, x1) for y in range(y0, y1 + 1)
                                 if px[x, y][3] > 200 and _lum(px[x, y]) > 200).most_common(1)[0][0]
        dark = [(x, y) for x in range(x0, x1) for y in range(y0, y1 + 1)
                if px[x, y][3] > 200 and _lum(px[x, y]) < _lum(bg) - 80]
        fill = collections.Counter(px[x, y][:3] for x, y in dark).most_common(1)[0][0]
        ty0 = min(y for _, y in dark); ty1 = max(y for _, y in dark)
        for y in range(12, 33):             # righe comuni: cancella anche il filetto che il testo giapponese lascia sopra
            row_bg = px[x0 + 1, y]          # il fondo ha un gradiente verticale: colore per riga
            for x in range(x0, x1 + 1):
                if px[x, y][3] > 200:
                    px[x, y] = row_bg
        t = ui_font.text(text, fill, px_all, ow=0, spacing=1)
        im.alpha_composite(t, (CX - t.width // 2, CY - t.height // 2))
        im.save(os.path.join(OUT, name + '.png'))
    print(len(TITOLI), 'targhette (px', px_all, ') ->', OUT)


if __name__ == '__main__':
    main()
