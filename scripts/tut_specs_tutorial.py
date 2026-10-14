"""Lavagne Tutorial_* (menu_tutorial_pics3): coordinate = fogli di lettura work/tut/sheets/Tutorial_NN.png."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import tut_board as tb
from PIL import ImageDraw
import tut_edit
from tut_edit import retext, hdr, H

ARCH = 'menu_tutorial_pics3'
T = {   # lavagne con solo il titolo grande
    'Tutorial_01_1': ['La bacchetta'], 'Tutorial_02_1': ['Il negozio'], 'Tutorial_07_1': ['La comunicazione'],
    'Tutorial_10_1': ['Le lezioni'], 'Tutorial_11_1': ['La valutazione'],
    'Tutorial_12_1': ['Far comprare', 'i prodotti'], 'Tutorial_13_1': ['I consigliati'],
    'Tutorial_14_1': ['Come preparare', 'i prodotti'],
}


def run(name, img):
    r = lambda tile, rect, text, **k: retext(img, H(tile, rect), text, **k)
    h = lambda tile, rect, text, **k: hdr(img, H(tile, rect), text, **k)
    if name == 'Tutorial_01_2':
        t = (1, 0)
        r(t, (560, 104, 632, 128), 'Pennino', align='l')
        r(t, (560, 132, 612, 155), 'oppure', align='l')
        r(t, (562, 160, 622, 184), 'Tasto R', align='l')
    elif name == 'Tutorial_01_3':
        t = (0, 1)
        r(t, (86, 343, 160, 388), ['Mano libera', 'o bacchetta'], align='l')
        r(t, (86, 400, 140, 422), 'Paletta', align='l')
        r(t, (86, 451, 140, 473), 'Canna da pesca', align='l')
        r(t, (214, 343, 286, 368), 'Retino', align='l')
        r(t, (214, 400, 262, 422), 'Annaffiatoio', align='l')
    elif name == 'Tutorial_02_3':
        t = (0, 0)
        h(t, (80, 60, 245, 84), 'Come vendere gli oggetti')
        r(t, (66, 138, 106, 154), 'Oggetto', px=10, fit=36)
        r(t, (143, 114, 180, 130), 'Oggetto', px=10, fit=36)
        r(t, (222, 138, 262, 154), 'Oggetto', px=10, fit=36)
        r(t, (105, 191, 225, 211), 'Spostalo dalla borsa')
    elif name == 'Tutorial_04_2':
        t = (1, 0)
        h(t, (435, 58, 585, 84), 'Trasformazione')
        r(t, (425, 190, 575, 228), ['Pennino o croce direzionale:', 'gira in cerchio verso destra'], px=10)
    elif name == 'Tutorial_07_2':
        h((1, 1), (440, 342, 560, 368), 'Stanza di comunicazione')
    elif name == 'Tutorial_07_3':
        t = (0, 0)
        h(t, (125, 62, 215, 86), 'Cosa puoi fare')
        r(t, (184, 98, 240, 122), 'Studio estero', px=11)
        r(t, (168, 126, 256, 150), 'Vorrei far visita', px=11)
        r(t, (170, 154, 254, 178), 'Vieni a trovarmi!', px=11)
        r(t, (180, 182, 246, 206), 'Codice amico', px=11)
    elif name == 'Tutorial_09_2':
        t = (1, 0)
        h(t, (410, 60, 585, 86), 'Come imparare le canzoni')
        r(t, (503, 110, 612, 132), ['Ho imparato', 'il brano!'], px=11)
    elif name == 'Tutorial_09_4':
        h((0, 1), (95, 348, 240, 372), 'Come sapere il titolo?')
    elif name == 'Tutorial_10_2':
        t = (0, 0)
        h(t, (88, 50, 218, 72), 'Contenuto delle lezioni')
        R = lambda rect, text, **k: retext(img, rect, text, **k)
        R((104, 70, 162, 94), ['Parole', 'magiche'], px=10, dark=True)
        R((214, 70, 276, 94), ['Magia', 'bacchetta'], px=10, dark=True)
        R((104, 122, 166, 146), 'Incantesimi', px=10, dark=True)
        R((226, 122, 270, 146), 'Negozio', px=10, dark=True)
        R((170, 174, 236, 198), 'Moda', px=11, dark=True)
        R((50, 101, 124, 116), 'Prof. Vlad', px=10)
        R((152, 101, 232, 116), 'Prof. Olmo', px=10)
        R((46, 155, 136, 170), ['Prof.ssa', 'Corvetta'], px=10, gap=0, valign='t')
        R((158, 155, 236, 170), 'Prof.ssa Marisa', px=9)
        R((106, 207, 190, 224), ['Prof.ssa', 'Vicky'], px=10, gap=0, valign='t')
    elif name == 'Tutorial_11_2':
        h((0, 1), (105, 326, 250, 350), 'Patente di maga')
    elif name == 'Tutorial_11_3':
        h((1, 1), (435, 326, 560, 352), 'Rango Maestro')
    elif name == 'Tutorial_11_4':
        h((0, 0), (112, 52, 232, 76), 'Rango Designer')
    elif name == 'Tutorial_12_2':
        h((0, 1), (110, 336, 245, 360), 'Tipi di clientela')
    elif name == 'Tutorial_13_2':
        h((0, 0), (95, 58, 235, 84), 'Prodotti consigliati')
    elif name == 'Tutorial_13_3':
        h((1, 0), (428, 60, 560, 84), 'Pubblicità del negozio')
    elif name == 'Tutorial_14_2':
        h((1, 1), (432, 324, 568, 348), 'Inserisci gli oggetti')
        retext(img, (148, 158, 162, 172), 'e', px=13)
        tut_edit.clean(img, tut_edit.bright_bbox(img, (205, 155, 226, 175), 140))
        retext(img, (102, 114, 216, 127), 'Ricetta del forno', px=9, ink='dark', thr=205)
        retext(img, (84, 180, 240, 192), 'Mescola bene', align='l', px=11)
        retext(img, (84, 193, 240, 206), 'Prepara gli ingredienti', align='l', px=11, thr=100, alpha=0.5)
    elif name == 'Tutorial_14_3':
        h((0, 0), (80, 58, 245, 84), 'Ingredienti per la casella')
    else:
        return None
    return img


def main(only=None):
    for name in sorted(set(T) | {f[:-4] for f in os.listdir(os.path.join(tb.PNG)) if f.startswith('Tutorial_')}):
        if only and name not in only:
            continue
        img = tb.load(name)
        if name in T:
            img = tb.title(img, T[name])
        elif run(name, img) is None:
            continue
        tb.save(img, name, ARCH)
        print('ok', name)


if __name__ == '__main__':
    main(sys.argv[1:])
