"""Lavagne/immagini varie: kanban (insegne), idol, chime, photo, runway, mydesign (schermate di gioco con poche scritte)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import tut_board as tb, tut_edit
from tut_edit import retext, hdr, H

tut_edit.PHOTO = True
ARCH = 'menu_tutorial_pics'
ARCH2 = 'menu_tutorial_pics2'


def kanban(name, img):
    if name == 'kanban_010':
        retext(img, (100, 16, 240, 46), 'La mia insegna!')
    elif name == 'kanban_012':
        retext(img, (100, 20, 240, 44), 'La mia insegna!')
        retext(img, (20, 228, 90, 250), 'Zoom', align='l')
    elif name == 'kanban_013':
        retext(img, (85, 100, 200, 125), 'Base insegna', dark=True, thr=190)
    else:
        return None
    return img


SPECS = [(kanban, ['kanban_010', 'kanban_012', 'kanban_013'], ARCH)]


def main(only=None):
    for fn, names, arch in SPECS:
        for n in names:
            if only and n not in only:
                continue
            img = tb.load(n)
            if fn(n, img) is None:
                continue
            tb.save(img, n, arch)
            print('ok', n)


if __name__ == '__main__':
    main(sys.argv[1:])
