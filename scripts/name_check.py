"""Trova nelle traduzioni i nomi di personaggi traslitterati dal giapponese (es. "Tetsu") invece del
nome italiano del glossario (es. "Reginaldo") e li corregge.
  python name_check.py          -> elenco dei casi trovati (anteprima)
  python name_check.py apply    -> applica le sostituzioni a batch_pages.json e manual_pages.json
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))

ROOT = os.path.join(os.path.dirname(__file__), '..')
TRAD = os.path.join(ROOT, 'work', 'trad')

KANA = {}
_base = ('a i u e o ka ki ku ke ko sa shi su se so ta chi tsu te to na ni nu ne no ha hi fu he ho '
         'ma mi mu me mo ya yu yo ra ri ru re ro wa wo n ga gi gu ge go za ji zu ze zo da ji zu de do '
         'ba bi bu be bo pa pi pu pe po').split()
_hira = 'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんがぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ'
for h, r in zip(_hira, _base):
    KANA[h] = r
    KANA[chr(ord(h) + 0x60)] = r          # katakana
SMALL = {'ゃ': 'ya', 'ゅ': 'yu', 'ょ': 'yo', 'ャ': 'ya', 'ュ': 'yu', 'ョ': 'yo'}
VOW = {'ぁ': 'a', 'ぃ': 'i', 'ぅ': 'u', 'ぇ': 'e', 'ぉ': 'o', 'ァ': 'a', 'ィ': 'i', 'ゥ': 'u', 'ェ': 'e', 'ォ': 'o'}


def romaji(s):
    out = ''
    i = 0
    while i < len(s):
        c = s[i]
        nxt = s[i + 1] if i + 1 < len(s) else ''
        if c in 'っッ':
            r = KANA.get(nxt, '')
            out += r[:1] if r else ''
        elif c == 'ー':
            out += out[-1:] if out else ''
        elif nxt in SMALL and c in KANA:
            base = KANA[c]
            out += (base[:-1] if base.endswith('i') and len(base) > 1 else base) + SMALL[nxt][-1:] \
                if base in ('shi', 'chi', 'ji') else base[:-1] + SMALL[nxt]
            i += 1
        elif nxt in VOW and c in KANA:
            out += KANA[c][:-1] + VOW[nxt]
            i += 1
        else:
            out += KANA.get(c, '')
        i += 1
    return out


def names():
    m = {}
    for line in list(open(os.path.join(ROOT, 'work', 'glossary', 'npc_it.tsv'), encoding='utf-8'))[1:]:
        c = line.rstrip('\n').split('\t')
        jp, it = c[0], c[1]
        r = romaji(jp)
        if len(r) >= 3 and r.lower() != it.lower() and re.fullmatch(r'[a-z]+', r):
            m[r] = it
    return m


EXTRA = {  # luoghi/negozi traslitterati o inventati dai traduttori -> nome del glossario
    'smile vivian': 'Da Vivian', 'smile bibi': 'Da Vivian', 'kameya': 'Emporio', 'limelight': 'Saranno Famosi',
    'harrows': 'Freccia', 'harogen': 'Freccia', 'halogen': 'Freccia', 'higemaru': 'Charlie',
    'flower daisy': 'Fiori Viola', 'mon pari': 'Mon Paris',
}
_PAT = None


def fix_names(text):
    """sostituisce i nomi traslitterati con quelli italiani (solo fuori dai segnaposto)"""
    global _PAT, _MAP
    if _PAT is None:
        _MAP = {**names(), **EXTRA}
        _PAT = re.compile(r'\b(' + '|'.join(sorted(map(re.escape, _MAP), key=len, reverse=True)) + r')\b', re.I)
    return _PAT.sub(lambda mo: _MAP[mo.group(1).lower()], text)


def main(apply=False):
    m = names()
    pat = re.compile(r'\b(' + '|'.join(sorted(map(re.escape, m), key=len, reverse=True)) + r')\b', re.I)
    total = 0
    for fn in ('batch_pages.json', 'manual_pages.json'):
        p = os.path.join(TRAD, fn)
        d = json.load(open(p, encoding='utf-8'))
        hits = 0
        for k, v in d.items():
            new = pat.sub(lambda mo: m[mo.group(1).lower()], v)
            if new != v:
                hits += 1
                if not apply and hits <= 15:
                    print(f'{fn}: {v[:70]}  ->  {new[:70]}')
                d[k] = new
        total += hits
        if apply:
            json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        print(fn, hits, 'righe con nomi traslitterati')
    return total


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main(len(sys.argv) > 1 and sys.argv[1] == 'apply')
