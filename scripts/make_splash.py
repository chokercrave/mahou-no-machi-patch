"""Avviso anti-pirateria iniziale (ui/menu_logo.tarc, logo.arc: timg/logo_cesa) in italiano.
Output: work/img_it/menu_logo/logo_cesa.png (installato da build_images.py, gruppo menu_logo)
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(__file__), '..')
SRC = os.path.join(ROOT, 'work', 'img', 'ui', 'menu_logo', 'logo.arc__timg_logo_cesa.png')
OUT = os.path.join(ROOT, 'work', 'img_it', 'menu_logo', 'logo_cesa.png')
FONTS = r'C:\Windows\Fonts'
SRC_LP = os.path.join(ROOT, 'work', 'img', 'ui', 'menu_logo', 'logo.arc__timg_logo_lp.png')
OUT_LP = os.path.join(ROOT, 'work', 'img_it', 'menu_logo', 'logo_lp.png')
RED, BLACK, GREY = (230, 0, 18, 255), (40, 40, 40, 255), (140, 140, 140, 255)
# versione della patch: file VERSION nella radice del progetto (una riga, es. 0.9)
VERSION = open(os.path.join(ROOT, 'VERSION'), encoding='utf-8').read().strip()
CREDIT = f'Patch italiana di chokercrave - v{VERSION}'

TITLE = 'Non distribuire né scaricare copie illegali'
BODY = [
    [('Distribuire giochi su Internet senza il permesso', BLACK)],
    [('del titolare dei diritti, o scaricarli sapendo che', BLACK)],
    [('sono illegali, è ', BLACK), ('severamente vietato dalla legge.', RED)],
    [('Grazie per la comprensione e la collaborazione.', BLACK)],
]


def main():
    src = Image.open(SRC).convert('RGBA')
    w, h = src.size
    im = Image.new('RGBA', (w, h), (255, 255, 255, 255))
    dr = ImageDraw.Draw(im)
    ft = ImageFont.truetype(os.path.join(FONTS, 'arialbd.ttf'), 17)
    fb = ImageFont.truetype(os.path.join(FONTS, 'arial.ttf'), 13)
    fbb = ImageFont.truetype(os.path.join(FONTS, 'arialbd.ttf'), 13)
    cx = 258                                     # centro del testo nell'originale
    tw = dr.textlength(TITLE, font=ft)
    dr.text((cx - tw / 2, 62), TITLE, font=ft, fill=RED)
    dr.line((cx - tw / 2 - 4, 85, cx + tw / 2 + 4, 85), fill=RED, width=2)
    y = 100
    for parts in BODY:
        lw = sum(dr.textlength(t, font=fbb if c == RED else fb) for t, c in parts)
        x = cx - lw / 2
        for t, c in parts:
            f = fbb if c == RED else fb
            dr.text((x, y), t, font=f, fill=c)
            x += dr.textlength(t, font=f)
        y += 21
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    im.save(OUT)
    print('->', OUT, im.size)



def credit():
    """credito della traduzione sotto il logo LovePlus Production (schermo basso, texture 256x256 bianca),
    piccolo e grigio (la schermata anti-pirateria viene saltata: make_logo_skip.py cesa)"""
    im = Image.open(SRC_LP).convert('RGBA')
    dr = ImageDraw.Draw(im)
    fc = ImageFont.truetype(os.path.join(FONTS, 'arial.ttf'), 11)
    cw = dr.textlength(CREDIT, font=fc)
    dr.text((128 - cw / 2, 222), CREDIT, font=fc, fill=GREY)
    im.save(OUT_LP)
    print('->', OUT_LP)


def black_bg():
    """i loghi iniziali sono tolti (make_logo_skip.py all), ma il codice aspetta lo stesso il loro tempo con lo
    sfondo dei layout (timg/white 8x8): nero invece di bianco, cosi' l'attesa e' una dissolvenza al nero"""
    Image.new('RGBA', (8, 8), (0, 0, 0, 255)).save(os.path.join(ROOT, 'work', 'img_it', 'menu_logo', 'white.png'))
    print('-> white.png nero')


if __name__ == '__main__':
    main()
    black_bg()
