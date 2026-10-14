"""Lavagne dei tutorial (menu_tutorial_pics*, ~457): compone le due metà _l/_r in una immagine sola e le raggruppa in fogli
di lettura (4 per foglio, con il nome sopra) per leggere il giapponese e scrivere le traduzioni.
  python tut_extract.py [prefisso]     -> work/tut/png/<nome>.png e work/tut/sheets/<prefisso>_NN.png
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import bclim
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(__file__), '..')
X = os.path.join(ROOT, 'work', '3ds', 'romfs_x', 'ui')
OUT = os.path.join(ROOT, 'work', 'tut')
DIRS = ['menu_tutorial_pics', 'menu_tutorial_pics2', 'menu_tutorial_pics3']


def boards():
    res = {}
    for d in DIRS:
        for f in sorted(os.listdir(os.path.join(X, d + '.tarc_x'))):
            m = re.match(r'(.+)_([lr])\.bclim$', f)
            if m:
                res.setdefault(m.group(1), {'dir': d})[m.group(2)] = f
    return res


def compose(name, b):
    ims = []
    for s in ('l', 'r'):
        if s in b:
            ims.append(bclim.decode(open(os.path.join(X, b['dir'] + '.tarc_x', b[s]), 'rb').read()))
    w = sum(i.width for i in ims)
    h = max(i.height for i in ims)
    c = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    x = 0
    for i in ims:
        c.paste(i, (x, 0))
        x += i.width
    return c


def main():
    pre = sys.argv[1] if len(sys.argv) > 1 else ''
    os.makedirs(os.path.join(OUT, 'png'), exist_ok=True)
    os.makedirs(os.path.join(OUT, 'sheets'), exist_ok=True)
    names = [n for n in boards() if n.startswith(pre)]
    bs = boards()
    tiles = []
    for n in names:
        im = compose(n, bs[n])
        im.save(os.path.join(OUT, 'png', n + '.png'))
        tiles.append((n, im))
    for k in range(0, len(tiles), 4):
        grp = tiles[k:k + 4]
        sheet = Image.new('RGB', (660, 2 * 276), (255, 255, 255))
        dr = ImageDraw.Draw(sheet)
        for j, (n, im) in enumerate(grp):
            x, y = (j % 2) * 330, (j // 2) * 276
            dr.text((x + 4, y + 2), n, fill=(255, 0, 0))
            bg = Image.new('RGB', im.size, (60, 60, 60))
            bg.paste(im, (0, 0), im)
            sheet.paste(bg, (x + 4, y + 14))
        sheet.save(os.path.join(OUT, 'sheets', f'{pre or "all"}_{k // 4:02d}.png'))
    print(len(tiles), 'lavagne,', (len(tiles) + 3) // 4, 'fogli')


if __name__ == '__main__':
    main()
