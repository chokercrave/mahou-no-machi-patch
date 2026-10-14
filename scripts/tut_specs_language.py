"""Lavagne language_* (menu_tutorial_pics): tipi di parole magiche. Coordinate = fogli work/tut/sheets/language_NN.png."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import tut_board as tb
from tut_edit import retext, hdr, H, bright_bbox, clean
from magic_words import W

ARCH = 'menu_tutorial_pics'
T = {   # titoli grandi (1 o 2 righe)
    'language_01_1': ['Tipi di', 'parole magiche'], 'language_02_1': ['Parole magiche', 'aggiunte'], 'language_03_1': ['Salutiamoci'],
    'language_04_1': ['Esprimi i tuoi', 'sentimenti'], 'language_05_1': ['Esprimi i sentimenti', 'con più forza'],
    'language_06_1': ['Come chiedere'], 'language_07_1': ['Base'], 'language_08_1': ['Chi'], 'language_09_1': ['Azioni'],
    'language_10_1': ['Cose'], 'language_11_1': ['Dove'], 'language_12_1': ['Quando'], 'language_13_1': ['Incontro'],
    'language_14_1': ['Come invitare'], 'language_15_1': ['Promessa', 'di giocare'], 'language_16_1': ['Avanzato'],
}
# per lavagna: tile del foglio, titoletto, etichette [(cx, cy, testo)] in coordinate del foglio
S = {
    'language_01_2': ((1, 0), (460, 60, 545, 82), 'Tipi', [(432, 137, 'Base'), (493, 137, 'Chi'), (556, 137, 'Azioni'), (432, 200, 'Cose'), (493, 200, 'Dove'), (556, 200, 'Quando')]),
    'language_02_2': ((1, 1), (455, 338, 545, 360), 'Aggiunte', [(522, 466, 'Chi', 10)]),
    'language_03_2': ((1, 0), (455, 62, 540, 84), 'Saluto', [(426, 181, W('あなた')), (482, 181, W('だれ？')), (566, 181, W('あいさつ'))]),
    'language_04_2': ((1, 1), (435, 330, 548, 355), 'I tuoi sentimenti', [(468, 413, W('じぶん')), (517, 413, W('にっこり')), (468, 477, W('じぶん')), (517, 477, W('かなしみ'))]),
    'language_04_3': ((0, 0), (105, 55, 230, 80), 'I tuoi sentimenti', [(107, 136, W('あなた')), (164, 136, W('にっこり')), (107, 203, W('あなた')), (164, 203, W('いかり'))]),
    'language_05_2': ((0, 1), (75, 328, 255, 352), 'Esprimi meglio', [(135, 411, W('ともだち')), (110, 486, W('ほしい')), (164, 486, W('キノコ'))]),
    'language_06_2': ((0, 0), (110, 55, 225, 82), 'Come chiedere', [(83, 142, W('ほしい')), (128, 142, W('さかな')), (197, 142, W('ほしい')), (243, 142, W('キノコ')), (140, 211, W('ほしい')), (186, 211, W('ベリー'))]),
    'language_07_2': ((0, 1), (120, 336, 205, 360), 'Base', [(118, 413, W('ラブ')), (163, 413, W('はやい')), (208, 413, W('おおきい')), (118, 473, W('たくさん')), (163, 473, W('にっこり')), (208, 473, W('いかり'))]),
    'language_08_2': ((0, 0), (120, 56, 210, 80), 'Chi', [(117, 136, W('みんな')), (163, 136, W('ともだち')), (209, 136, W('こいびと')), (163, 197, W('こうちょう')), (209, 197, W('ビビ'))]),
    'language_09_2': ((0, 1), (118, 340, 215, 362), 'Azioni', [(94, 437, 'Vai'), (140, 437, 'Parla'), (186, 437, 'Suona'), (230, 437, 'Studia')]),
    'language_09_3': ((1, 1), None, None, [(443, 426, W('じかん')), (490, 426, W('ひる')), (488, 449, '"Ore 18"', 26, 110)]),
    'language_10_2': ((1, 0), (455, 62, 540, 85), 'Cose', [(423, 160, W('おかね')), (468, 160, W('さかな')), (516, 160, 'Annaff.'), (559, 160, W('くさ'))]),
    'language_11_2': ((1, 1), (455, 330, 540, 358), 'Dove', [(446, 414, W('いえ')), (492, 414, W('りょう')), (539, 414, W('どこ？')), (446, 473, W('もり')), (492, 473, W('うえ')), (539, 473, W('した'))]),
    'language_12_2': ((1, 0), (455, 62, 540, 88), 'Quando', [(423, 161, W('あさ')), (468, 161, W('いま')), (514, 161, W('あした')), (561, 161, W('げつようび'))]),
    'language_13_2': ((1, 1), (445, 334, 540, 358), 'Incontro', [(412, 418, W('まちあわせ')), (458, 418, W('よる')), (524, 418, W('まちあわせ')), (571, 418, W('どようび')), (468, 484, W('まちあわせ')), (515, 484, W('とう'))]),
    'language_14_2': ((1, 0), (445, 60, 545, 84), 'Come invitare', [(417, 134, W('いっしょ')), (462, 134, 'Canna'), (417, 200, 'Prendi'), (462, 200, W('くさ')), (527, 134, W('いっしょ')), (572, 134, W('えんそう')), (527, 200, 'Prendi'), (572, 200, W('キノコ'))]),
    'language_15_2': ((1, 1), (435, 336, 545, 360), 'Promessa di giocare', [(413, 417, W('あした')), (461, 417, W('あそぶ')), (524, 417, W('どようび')), (571, 417, W('あそぶ')), (468, 483, W('する')), (516, 483, W('あそぶ'))]),
    'language_16_2': ((1, 0), (425, 58, 575, 84), 'Altri usi 1', []),
    'language_16_3': ((0, 1), (95, 336, 235, 360), 'Altri usi 2', []),
    'language_16_4': ((1, 1), (420, 336, 570, 360), 'Altri usi 3', []),
}
FIT = 46


def render(name, img):
    tile, hint, title, labels = S[name]
    if hint:
        hdr(img, H(tile, hint), title)
    pend = []
    for lab in labels:                     # prima si misurano tutte le etichette originali, poi si riscrivono
        cx, cy, text = lab[:3]
        hw = lab[3] if len(lab) > 3 else 24
        thr = lab[4] if len(lab) > 4 else 165
        hint = H(tile, (cx - hw, cy - 9, cx + hw, cy + 7))
        bb = bright_bbox(img, hint, thr)
        if bb is None:
            print(f'  ! {name}: etichetta {text!r} in ({cx},{cy}) non trovata')
            continue
        pend.append((hint, text, hw, thr, bb))
    for hint, text, hw, thr, bb in pend:
        clean(img, bb)
    for hint, text, hw, thr, bb in pend:
        retext(img, hint, text, px=11, fit=FIT if hw == 24 else 2 * hw, thr=thr, bb=bb, keep=True)
    return img


def main(only=None):
    for name in sorted(set(T) | set(S)):
        if only and name not in only:
            continue
        img = tb.load(name)
        if name in T:
            img = tb.title(img, T[name])
        else:
            render(name, img)
        tb.save(img, name, ARCH)
        print('ok', name)


if __name__ == '__main__':
    main(sys.argv[1:])
