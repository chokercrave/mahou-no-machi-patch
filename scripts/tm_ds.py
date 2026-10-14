"""Tier (a): riuso delle traduzioni ufficiali del prequel DS, pagina per pagina.

Per ogni pagina 3DS (testo tra [#0000]) la chiave è il testo giapponese senza codici/furigana/a capo.
Se il DS ha la stessa frase, si prende l'italiano DS e si rimpiazzano i suoi codici con quelli
del 3DS, nell'ordine. Codici "lasciabili" (desinenza [$511'N], pronome [$514'0]) possono mancare
nell'italiano, come nella localizzazione DS ufficiale.

Output: work/trad/ds_pages.json  {chiave_pagina: testo_it_con_codici_3ds}
"""
import json, os, re, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
import textdb

ROOT = textdb.ROOT
DSCODE = re.compile(r"\$(\d+)((?:'[^;']*)*);")
CODE3 = re.compile(r"\[\$(\d+)((?:'[^\]']*)*)\]")
DROP = re.compile(r"\[\$511'\d+\]|\[\$514'0\]")
FACE_DS = re.compile(r"^(?:\$02[234](?:'[^;']*)*;)+")
TRAIL = re.compile(r"(?:\[\$[^\]]*\])+$")


def ds_tm():
    tm = {}
    for line in open(os.path.join(ROOT, 'work', 'glossary', 'corpus_dialoghi.tsv'), encoding='utf-8'):
        c = line.rstrip('\n').split('\t')
        if len(c) != 6 or c[0] == 'file':
            continue
        jp = textdb.FURI.sub(r'\1', c[4])
        k = re.sub(r'[\s▼　]', '', DSCODE.sub('', jp))
        if k and textdb.JP.search(k):
            tm.setdefault(k, collections.Counter())[c[5]] += 1
    return {k: v.most_common(1)[0][0] for k, v in tm.items()}


def split_page(p):
    """pagina -> (codici iniziali, corpo, codici finali)"""
    m = textdb.LEAD.match(p)
    lead = m.group(0) if m else ''
    rest = p[len(lead):]
    t = TRAIL.search(rest)
    trail = t.group(0) if t else ''
    return lead, rest[:len(rest) - len(trail)], trail


def page_key(body):
    return re.sub(r'[\s▼　]', '', textdb.FURI.sub(r'\1', body))


TRAIL_DS = re.compile(r"(?:\$\d+(?:'[^;']*)*;)+$")
# codici che rappresentano testo (nomi, colori): se l'italiano li omette si possono perdere
TEXTUAL = {0, 500, 503, 507, 515, 530, 531, 532, 533, 535, 538, 540, 545, 550, 560, 561}


def ds_to_3ds(it_ds, body3):
    """Italiano DS -> corpo 3DS; None se i codici non tornano.
    I codici sono abbinati per numero (il traduttore può riordinare i nomi); i codici 3DS
    non usati dall'italiano: testuali -> omessi, effetti -> messi a inizio pagina."""
    it = TRAIL_DS.sub('', FACE_DS.sub('', it_ds)).replace('[', '[[')
    pool = collections.defaultdict(list)
    for m in CODE3.finditer(DROP.sub('', body3)):
        pool[int(m.group(1))].append(m.group(0))
    out, last = [], 0
    for m in DSCODE.finditer(it):
        n = int(m.group(1))
        if not pool[n]:
            return None
        out.append(it[last:m.start()]); out.append(pool[n].pop(0)); last = m.end()
    out.append(it[last:])
    res = ''.join(out)
    if res.count("[$0'") % 2:
        return None
    effects = [c for n, cs in pool.items() if n not in TEXTUAL for c in cs]
    return ''.join(effects) + res.replace('\\n', '▼')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    tm = ds_tm()
    res, miss_codes = {}, collections.Counter()
    for f, groups in textdb.load_all().items():
        for _, slot in textdb.iter_slots(groups):
            for p in textdb.split_pages(slot):
                lead, body, trail = split_page(p)
                if not textdb.JP.search(body):
                    continue
                k = page_key(body)
                n = textdb.norm(body)
                if k in res or n not in tm:
                    continue
                it = ds_to_3ds(tm[n], body)
                if it is None:
                    miss_codes[f] += 1
                    continue
                res[k] = it
    os.makedirs(os.path.join(ROOT, 'work', 'trad'), exist_ok=True)
    json.dump(res, open(os.path.join(ROOT, 'work', 'trad', 'ds_pages.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=0)
    chars = collections.Counter(ch for v in res.values() for ch in CODE3.sub('', v))
    print(f'pagine tradotte dal DS: {len(res)}; scartate per codici diversi: {dict(miss_codes)}')
    print('caratteri non ASCII usati:', ''.join(sorted(c for c in chars if ord(c) > 0x7E)))
