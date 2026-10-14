"""Lavagne magic_NN_1 (titolo) e magic_NN_2 (parole magiche della bacchetta): 22 magie."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import tut_board as tb
from tut_edit import retext, hdr
from magic_words import W

ARCH = 'menu_tutorial_pics2'
G, I, S = 'おおきい', 'いたずら', 'ほし'
M = {
    1: ('Flatulenza', ['トイレ', 'えんそう']), 2: ('Catino', [G, I]), 3: ('Ragnatela', ['おそい', 'むし']),
    4: ('Sonno', ['ひる', 'ねむい']), 5: ('Magnetismo', ['ラブ', 'あつまる']), 6: ('Perspicacia', ['たんけん', 'こいびと']),
    7: ('Trasformazione', ['こうかん', 'だれ？']), 8: ('Party popper', ['はな', 'がっき']), 9: ('Amaca nuvole', ['そら', 'ねる']),
    10: ('Stelle filanti', ['あつまる', S]), 11: ('Caccia tesoro', ['ひみつ', 'さがす']), 12: ('Fulmine', [S, 'いかり']),
    13: ('Voce alta', ['はなす', 'うえ']), 14: ('Piroetta', ['うえ', 'みぎ', 'した', 'ひだり']), 15: ('Volantini scherzo', ['せんでん', 'あるく']),
    16: ('Catino grande', [G, G, I]), 17: ('Grande party popper', ['はな', 'たくさん', 'がっき']), 18: ('Palloncino', [G, 'うえ', I]),
    19: ('Danza del ventre', ['ようふく', 'にっこり', I]), 20: ('Amaca amore', ['そら', 'ねる', 'ラブ']),
    21: ('Super flatulenza', [G, 'トイレ', 'えんそう']), 22: ('Bolle di sapone', ['あそぶ', 'そら', 'たくさん']),
}
EXTRA = {'ひみつ': 'Segreto', 'せんでん': 'Pubblicità', 'たんけん': W('たんけん'), 'まほう': 'Magia'}
SENT = 'Trasformati e recitala!'


def word(jp):
    return EXTRA.get(jp) or W(jp)


def main(only=None):
    for n, (name, labs) in M.items():
        full = 'Magia ' + name
        n1, n2 = f'magic_{n:02d}_1', f'magic_{n:02d}_2'
        if not only or n1 in only:
            lines = [full] if tb.chalk(full, 22).width <= 220 else ['Magia', name]
            tb.save(tb.title(tb.load(n1), lines), n1, ARCH)
        if not only or n2 in only:
            b = tb.load(n2)
            hdr(b, (24, 58, 296, 96), full)
            retext(b, (30, 166, 300, 192), SENT, px=11)
            tb.menu_labels(b, [word('まほう')] + [word(j) for j in labs])
            tb.save(b, n2, ARCH)
        print('ok', n)


if __name__ == '__main__':
    main(sys.argv[1:])
