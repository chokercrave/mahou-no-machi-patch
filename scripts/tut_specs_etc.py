"""Lavagna etc_00_1 (come esporre i prodotti in negozio). Coordinate = foglio etc_00.png."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import tut_edit

ARCH = 'menu_tutorial_pics'
SPECS = {
    'etc_00_1': [('h', 'Esporre i prodotti', 56),
                 ('r', (62, 72, 155, 94), '\u25c6 Posa i prodotti', dict(align='l', px=11)),
                 ('r', (52, 104, 162, 138), ['Dalla borsa, posa il', 'prodotto dove vuoi'], dict(px=11)),
                 ('r', (56, 150, 118, 170), '\u25c6 Merce', dict(align='l', px=11)),
                 ('r', (122, 146, 154, 172), 'Spingi', dict(big=True, px=14)),
                 ('r', (174, 146, 210, 172), 'Tira', dict(big=True, px=14)),
                 ('r', (226, 146, 276, 172), 'Gira', dict(big=True, px=14)),
                 ('r', (48, 196, 116, 214), 'Tieni premuto', dict(px=8))],
}

if __name__ == '__main__':
    tut_edit.run_family(SPECS, ARCH, sys.argv[1:] or None)
