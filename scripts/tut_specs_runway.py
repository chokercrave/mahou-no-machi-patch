"""Lavagne npc_runway_00/01 e pc_runway_00/01 (512x256, due meta' come ucc_tuto)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import tut_board as tb, tut_edit
from tut_edit import retext, hdr
from tut_specs_ucc import save as save512

ARCH = 'menu_tutorial_pics2'
S = {
    'npc_runway_00': ('Illumina la modella!', ['Segui la modella con la luce', 'senza perderla di vista!'], (140, 172, 375, 224)),
    'npc_runway_01': ('Anima lo spettacolo!', ['Muovi liberamente il pennino', 'sul touch screen!'], (150, 196, 375, 224)),
    'pc_runway_00': ('Tocca le note!', ['Tocca tante note a tempo', 'con la musica!'], (135, 172, 375, 224)),
    'pc_runway_01': ('Rispondi al pubblico!', ["Tocca le voci del pubblico", "per attirare l'attenzione!!"], (135, 172, 365, 224)),
}

import numpy as np
import tut_specs_photo as ph

def white_mask(a):
    return (a.min(2) > 215)

def black_mask(a):
    return (a.max(2) < 90)

def bluebub(a):
    return (a[..., 0] < 110) & (a[..., 1] < 190) & (a[..., 2] > 170)

BUB = (30, 30, 30)
SHOTS = {
    'npc_runway_02': [((10, 10, 84, 32), ['Votazione'], white_mask, (255, 255, 255), 11)],
    'npc_runway_03': [((88, 22, 164, 64), ['Capo, dai le', 'istruzioni,', 'miao!'], black_mask, BUB, 11, True)],
    'npc_runway_04': [((88, 22, 164, 64), ['Capo, dai le', 'istruzioni,', 'miao!'], black_mask, BUB, 11, True)],
    'pc_runway_02': [((10, 10, 84, 32), ['Votazione'], white_mask, (255, 255, 255), 11)],
    'pc_runway_03': [((10, 10, 84, 32), ['Votazione'], white_mask, (255, 255, 255), 11)],
    'pc_runway_04': [((25, 12, 84, 32), ['Bersaglio'], white_mask, (255, 255, 255), 11),
                     ((20, 130, 92, 150), ['Vieni qui~'], bluebub, (0, 70, 200), 11),
                     ((118, 130, 200, 150), ['Splendida'], bluebub, (0, 70, 200), 11),
                     ((222, 130, 298, 150), ['Fantastica!'], bluebub, (0, 70, 200), 11)],
}


def shots(only=None):
    for name, ops in SHOTS.items():
        if only and name not in only:
            continue
        img = tb.load(name)
        for rect, lines, fn, ink, px, *w in ops:
            try:
                ph.swap(img, rect, lines, fn, ink, px, bool(w))
            except Exception as e:
                print(f'  ! {name} {rect}: {type(e).__name__} {e}')
        tb.save(img, name, ARCH)
        print('ok', name)


def main(only=None):
    tut_edit.PHOTO = False
    for name, (head, foot, rect) in S.items():
        if only and name not in only:
            continue
        img = tb.load(name)
        hdr(img, (140, 36, 375, 66), head)
        retext(img, rect, foot, align='l', px=12)
        d = os.path.join(tb.OUT, ARCH)
        os.makedirs(d, exist_ok=True)
        img.crop((0, 0, 256, 256)).save(os.path.join(d, name + '_l.png'))
        img.crop((256, 0, img.width, 256)).save(os.path.join(d, name + '_r.png'))
        print('ok', name)
    return


if __name__ == '__main__':
    main(sys.argv[1:] or None)
    shots(sys.argv[1:] or None)
