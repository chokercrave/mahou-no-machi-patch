"""Lavagne chime_000..006 (schermate della campanella): titolo della testata e nomi delle note sulla tastiera."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import tut_board as tb
import tut_specs_photo as ph

ARCH = 'menu_tutorial_pics'
KEYS = [(43, 'Do'), (75, 'Re'), (103, 'Mi'), (128, 'Fa'), (160, 'Sol'), (188, 'La'), (217, 'Si'), (244, 'Do'), (273, 'Re')]


def teal(a):
    return (a[..., 0] < 90) & (a[..., 1] < 150) & (a[..., 2] < 190)


def blue(a):
    return (a[..., 0] < 160) & (a[..., 2] > 190) & (a[..., 1] < 210)


def main(only=None):
    for k in range(7):
        name = f'chime_{k:03d}'
        if only and name not in only:
            continue
        img = tb.load(name)
        try:
            ph.swap(img, (132, 26, 190, 48), ['Campanella'], teal, (16, 96, 130), 14)
        except Exception as e:
            print(f'  ! {name} titolo: {e}')
        for cx, t in KEYS:
            try:
                ph.swap(img, (cx - 11, 222, cx + 11, 241), [t], blue, (60, 150, 220), 10, True)
            except Exception as e:
                print(f'  . {name} {t}@{cx}: {e}')
        tb.save(img, name, ARCH)
        print('ok', name)


if __name__ == '__main__':
    main(sys.argv[1:] or None)
