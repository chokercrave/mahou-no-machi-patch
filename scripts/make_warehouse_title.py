"""Titolo "Magazzino" della schermata del magazzino del negozio (ui/menu_warehouse.tarc -> warehouse.arc:
timg/title_font_00 64x16 + title_font_01 16x16 affiancate: scritta marrone senza contorno su fondo trasparente,
stesso tratto dei titoli italiani delle altre schermate (Grandstander antialias).
Output: work/img_it/menu_warehouse/title_font_00.png, title_font_01.png (gruppo menu_warehouse in build_images.py)
Stessa struttura per il titolo "もちものをうる" del menu Vendi (ui/menu_sell.tarc -> sell_menu.arc, testo blu 0,89,130,
originale colonne 3..77 -> centro 40): work/img_it/menu_sell/ (gruppo menu_sell)."""
import os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import ui_font

ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'work', 'img_it', 'menu_warehouse')
TEXT, BROWN = 'Magazzino', (107, 58, 0)
TOTAL_W, H = 80, 16


# warehouse_bg.bclyt: targa coi ricciolini simmetrica attorno a x=56 (Pic_title_00/01/02), le due texture del
# titolo coprono x 18..98 (Pic_font_00 centro 50, Pic_font_01 centro 90) -> il centro della targa e' la colonna 38
CENTER_X = 38
MAX_W = 70           # spazio libero tra i ricciolini (il giapponese era largo 74 ma con gli spazi tra i kana)


TITLES = [(OUT, TEXT, BROWN, CENTER_X, MAX_W),
          (os.path.join(ROOT, 'work', 'img_it', 'menu_sell'), 'Vendita', (0, 89, 130), 40, 74)]


def main():
    for out, text, color, cx, mw in TITLES:
        title(out, text, color, cx, mw)


def title(OUT, TEXT, BROWN, CENTER_X, MAX_W):
    os.makedirs(OUT, exist_ok=True)
    # stesso font dei titoli delle altre schermate ("Ricette di cucina"): font pixel del gioco sotto i 14 px
    ui_font.SMALL = 14
    t = ui_font.fit(TEXT, BROWN, MAX_W, 15, px_max=13, ow=0, spacing=1)
    px = ui_font.LAST_PX
    canvas = Image.new('RGBA', (TOTAL_W, H), (0, 0, 0, 0))
    canvas.alpha_composite(t, (CENTER_X - t.width // 2, 8 - t.height // 2))     # centro verticale ~ riga 8 (originale righe 3-13)
    canvas.crop((0, 0, 64, 16)).save(os.path.join(OUT, 'title_font_00.png'))
    canvas.crop((64, 0, 80, 16)).save(os.path.join(OUT, 'title_font_01.png'))
    print('titolo:', TEXT, 'px', px, t.size)


if __name__ == '__main__':
    main()
