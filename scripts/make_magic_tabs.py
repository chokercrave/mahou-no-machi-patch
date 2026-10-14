"""Linguette selezionate della schermata di composizione delle parole magiche
(ui/menu_input_magic2.tarc → 000.bin: timg/tab_06..11, 64x64): icona sopra, parola sotto (righe 44-53).
Si ridipinge la fascia del testo con il fondo della riga 42 e si scrive la parola italiana.
Output: work/img_it/menu_input_magic2/tab_NN.png (gruppo menu_input_magic2 in build_images.py)
"""
import collections, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from relabel import _lum
import ui_font

ROOT = os.path.join(os.path.dirname(__file__), '..')
SRC = os.path.join(ROOT, 'work', 'img', 'ui', 'menu_input_magic2')
OUT = os.path.join(ROOT, 'work', 'img_it', 'menu_input_magic2')
PAROLE = {'tab_06': 'Base', 'tab_07': 'Chi', 'tab_08': 'Azioni', 'tab_09': 'Cose', 'tab_10': 'Dove',
          'tab_11': 'Quando'}   # きほん だれ すること もの どこ いつ
Y0, Y1, X0, X1 = 44, 53, 16, 50


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, text in PAROLE.items():
        im = Image.open(os.path.join(SRC, f'000.bin__timg_{name}.png')).convert('RGBA')
        px = im.load()
        dark = [px[x, y][:3] for x in range(X0, X1) for y in range(Y0, Y1 + 1)
                if px[x, y][3] > 200 and _lum(px[x, y]) < 150]
        fill = collections.Counter(dark).most_common(1)[0][0]
        for y in range(Y0, Y1 + 1):
            for x in range(X0, X1):
                if px[x, y][3] > 200:
                    px[x, y] = px[x, 42 - (y - Y0) % 2]     # fondo a scacchi: si ripete il motivo
        # font pixel del gioco, stessa dimensione per tutte (prima: font generico di grandezza variabile)
        t = ui_font.text(text, fill, 11, outline=(0, 0, 0), ow=0, spacing=0)
        im.alpha_composite(t, ((64 - t.width) // 2, Y0 + (Y1 - Y0 + 1 - t.height) // 2))
        im.save(os.path.join(OUT, name + '.png'))
    print(len(PAROLE), 'linguette ->', OUT)


if __name__ == '__main__':
    main()
