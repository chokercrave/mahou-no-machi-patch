"""Importa i lotti tradotti (batches/bNNN.it.tsv) in work/trad/batch_pages.json, validando ogni riga.
Errori -> work/trad/batch_errors.tsv (id, motivo, giapponese, italiano) per la ritraduzione.
  python batch_import.py            importa tutti i lotti presenti
"""
import collections, glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from build_text import layout, render_batch, TAG
from bcfnt import Bcfnt

ROOT = os.path.join(os.path.dirname(__file__), '..')
TRAD = os.path.join(ROOT, 'work', 'trad')
JP = re.compile(r'[぀-ヿ一-鿿＀-￯]')
MAX_LINES = 3


def font_chars():
    f = Bcfnt(open(os.path.join(ROOT, 'work', 'font', 'LC.bcfnt'), 'rb').read())
    return {chr(c) for c in f.cmap}


def normalize(s, names=True):
    s = s.strip().replace('　', ' ').replace('「', '"').replace('」', '"')
    s = s.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
    s = s.replace('！', '!').replace('？', '?').replace('～', '~')
    s = re.sub(r'</c\d+>', '</c>', s)
    if names:   # nomi ufficiali (name_check); names=False per gli elenchi corti dove non entrano
        from name_check import fix_names
        s = fix_names(s)
    s = s.translate(str.maketrans('ōūāīēŌŪ', 'ouaieOU'))
    # questi simboli nel font disegnano vocali accentate (tastiera): non usarli nel testo
    parts = re.split(r'(</?c\d*>|<P>|<X\d+>)', s)
    s = ''.join(p if i % 2 else p.replace('#', 'n.').replace('&', 'e').replace('<', '«').replace('>', '»')
                .replace('\\', '/').replace('_', ' ') for i, p in enumerate(parts))
    return re.sub(r' {2,}', ' ', s)


ICONS = '葱蕪蓬蓮韮'   # nel font del gioco: cuore, arrabbiato, sorriso, zampa, triste


def fix_icons(jp, it):
    """il traduttore a volte rende il cuore 葱 con ♪: lo ripristina"""
    n = jp.count('葱')
    if n and it.count('葱') < n and '♪' in it and '♪' not in jp:
        it = it.replace('♪', '葱', n - it.count('葱'))
    return it


SCUOLA = re.compile(r'(scuola di magia)(</c>)?', re.I)


def fix_town(tags, it):
    """[$504] = nome della città: in giapponese precede まほう学校 ("<città>のまほう学校"), i traduttori
    lo mettevano a inizio frase. Lo sposta dopo "scuola di magia" -> "scuola di magia di <città>"."""
    for k, v in (tags or {}).items():
        if v == '[$504]' and k in it:
            m = SCUOLA.search(it.replace(k, ''))
            if m and f'di {k}' not in it:
                it = it.replace(k, '')
                m = SCUOLA.search(it)
                it = re.sub(r' +', ' ', (it[:m.end()] + f' di {k}' + it[m.end():]).strip())
    return it


def check(jp, it, chars, tags=None, max_pages=3):
    if not it:
        return 'vuota'
    it = ''.join(c for c in it if c not in ICONS)
    a, b = collections.Counter(TAG.findall(jp)), collections.Counter(TAG.findall(it))
    # <P> (nome del giocatore) usato come "tu" in giapponese: in italiano può sparire
    if b['<P>'] <= a['<P>']:
        a['<P>'] = b['<P>']
    a['</c>'] = b['</c>'] = 0   # chiusure colore: alcune mancano già nel giapponese
    if +a != +b:
        return f'segnaposto {sorted(TAG.findall(jp))} != {sorted(TAG.findall(it))}'
    if JP.search(TAG.sub('', it)):
        return 'giapponese residuo'
    bad = {c for c in TAG.sub('', it) if c not in chars}
    if bad:
        return 'caratteri fuori font ' + ''.join(sorted(bad))
    n = len(layout(render_batch(it, tags or {})))
    if n > max_pages:
        return f'troppo lunga ({n} pagine)'
    return None


def main():
    units = {u['id']: u for u in json.load(open(os.path.join(TRAD, 'units.json'), encoding='utf-8'))}
    path = os.path.join(TRAD, 'batch_pages.json')
    bt = {}   # ricostruito da zero: le correzioni manuali stanno in manual_pages.json
    chars = font_chars() | {' ', '§'}   # § = desinenza o/a (gender_tag)
    errs, ok, nfiles = [], 0, 0
    # prima i lotti (b), poi le correzioni (r) che sovrascrivono
    for f in sorted(glob.glob(os.path.join(TRAD, 'batches', '[br]*.it.tsv'))):
        nfiles += 1
        for line in open(f, encoding='utf-8'):
            line = line.rstrip('\n')
            if '\t' not in line:
                continue
            sid, it = line.split('\t', 1)
            if not sid.strip().isdigit() or int(sid) not in units:
                continue
            u = units[int(sid)]
            it = fix_town(u['tags'], fix_icons(u['jp'], normalize(it)))
            e = check(u['jp'], it, chars, u['tags'], 1 if u['file'] == 'onemsg' else 3)
            if e:
                errs.append((u['id'], e, u['jp'], it))
            else:
                bt[u['jp']] = it; ok += 1
    json.dump(bt, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    with open(os.path.join(TRAD, 'batch_errors.tsv'), 'w', encoding='utf-8') as f:
        for e in errs:
            f.write('\t'.join(map(str, e)) + '\n')
    kinds = collections.Counter(e[1].split(' ')[0] for e in errs)
    print(f'{nfiles} lotti: {ok} righe valide, {len(errs)} errori {dict(kinds)}; totale batch_pages {len(bt)}/{len(units)}')


if __name__ == '__main__':
    main()
