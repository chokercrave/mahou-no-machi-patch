"""Importa i lotti di riscrittura manuale (batches/mNNN.tsv: n, giapponese, ... / mNNN.it.tsv: n, italiano)
in work/trad/manual_pages.json (chiave = giapponese con segnaposto), con la stessa validazione di batch_import.
"""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from batch_import import normalize, fix_icons, check, font_chars

ROOT = os.path.join(os.path.dirname(__file__), '..')
B = os.path.join(ROOT, 'work', 'trad', 'batches')
OUT = os.path.join(ROOT, 'work', 'trad', 'manual_pages.json')


# limiti misurati (più larghi della stima "voce giapponese più lunga del gruppo" di short_lists.py)
OPTION_BATCHES = {'m102.tsv', 'm118.tsv', 'm119.tsv'}
LIMIT_OVERRIDE = {
    # nomi dei due libri parlanti: vanno nel buffer del nome della targhetta (obj+0x14c..0x188 = 29 car.)
    'さかなの しょ': 16, 'むしの しょ': 16,
    # opzione di dialogo (scelta, tagliata a 16 caratteri, non campo fisso da 10): si vuole "Spiegazioni"
    'せつめい<X1>': 16,
    # nome mappa (pannello da 150 px): termine ufficiale come nei dialoghi; da verificare in game che il buffer regga
    'こいびとみさき': 22,        # verificato in game (2026-10-09): 22 caratteri reggono, quindi anche i due seguenti (<= 22)
    'ゆうれいやしき': 22, 'ショッピングモール': 22,
    # titolo della ricetta = nome del piatto + suffisso: senza i due punti usciva "TortaCreiamo!"
    'をつくろう！': 10,
    # nomi UFFICIALI DS dei luoghi (lotto m120; mappa 99122 + elenchi luoghi 99124/99146), <= 22 come sopra
    **{k: 22 for k in ('きのこのもり', 'ハロゲンデパート', 'モン・パリ', 'スマイル・ビビ', 'フラワーデイジー', 'かめや',
                       'ライムライト', 'ゆうびんきょく', 'アパート', 'ひげまるラーメン', 'ヒゲマルラーメン',
                       'アンティーク＆キュリオス', 'ケット・シーひみつのおみせ', 'えっけんのま',
                       'のいえ', 'のおみせ', 'のアトリエ', 'のキッチン', 'のおへや')},
}


def main():
    import re
    man = {}
    chars = font_chars() | {' ', '§', '¤'}   # § = desinenza o/a, ¤ = plurale i/e (gender_tag 599/598)
    bad = 0
    rejected = []
    lp =os.path.join(ROOT, 'work', 'trad', 'short_limits.json')
    limits = json.load(open(lp, encoding='utf-8')) if os.path.exists(lp) else {}
    limits.update(LIMIT_OVERRIDE)
    for f in sorted(glob.glob(os.path.join(B, 'm???.tsv'))):
        src = {l.split('\t')[0]: l.rstrip('\n').split('\t')[1] for l in open(f, encoding='utf-8') if '\t' in l}
        it_path = f[:-4] + '.it.tsv'
        if not os.path.exists(it_path):
            continue
        for l in open(it_path, encoding='utf-8'):
            if '\t' not in l:
                continue
            n, it = l.rstrip('\n').split('\t', 1)
            if n not in src:
                continue
            jp = src[n]
            # suffissi attaccati a un nome dal gioco ("[nome]" + " abita qui"): lo spazio iniziale va tenuto
            lead = ' ' if it.startswith(' ') and jp.startswith('の') else ''
            it = lead + fix_icons(jp, normalize(it))
            # riparazione: <X> dimenticati (di solito codici di coda) in fondo; colori mancanti attorno a tutto
            for x in re.findall(r'<X\d+>', jp):
                if jp.count(x) > it.count(x):
                    it += x
            for c in re.findall(r'<c\d+>', jp):
                if c not in it:
                    it = c + it + '</c>'
            e = check(jp, it, chars, None, 3)
            vis = len(re.sub(r'</?c\d*>|<X\d+>|<P>', '', it))
            if not e and jp in limits and vis > limits[jp]:
                e = f'oltre il limite {limits[jp]} ({vis})'
            # lotti di opzioni di scelta (m102 con le frasi lunghe 41/49 escluse): il gioco taglia a 16 caratteri
            if not e and os.path.basename(f) in OPTION_BATCHES and vis > 15 and len(jp) < 20:
                e = f'opzione oltre 15 caratteri ({vis})'
            if e:
                bad += 1
                print('scartata', os.path.basename(f), n, e)
                rejected.append((jp, it, limits.get(jp, ''), e))
                continue
            man[jp] = it
    json.dump(man, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    with open(os.path.join(ROOT, 'work', 'trad', 'manual_rejected.tsv'), 'w', encoding='utf-8') as fo:
        for jp, it, lim, e in rejected:
            fo.write(f'{jp}\t{it}\t{lim}\t{e}\n')
    print(len(man), 'righe manuali;', bad, 'scartate')


if __name__ == '__main__':
    main()
