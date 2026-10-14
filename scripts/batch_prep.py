"""Prepara i lotti per la traduzione nuova (tier c) delle pagine non coperte dal DS.

Per ogni pagina: testo giapponese "pulito" per il traduttore + mappa dei segnaposto.
  [$500]            -> <P>            nome del giocatore
  [$0'N] ... [$0'1] -> <cN> ... </c>  parola evidenziata a colori
  [$511'N]          -> (tolto)        desinenza del personaggio (vuota in italiano)
  [$514'0]          -> 私             pronome "io" del personaggio
  altri codici      -> <X1>, <X2>...  nomi/oggetti inseriti dal gioco o effetti
Output: work/trad/units.json (tutte le unità) e work/trad/batches/bNNN.tsv (id<TAB>giapponese)
più glossario pertinente per ogni lotto in bNNN.gloss.tsv
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import textdb
from tm_ds import split_page, page_key

ROOT = textdb.ROOT
TRAD = os.path.join(ROOT, 'work', 'trad')
CODE = re.compile(r"\[\$[^\]]*\]")
BATCH_CHARS = 3500


def to_placeholders(body):
    """corpo 3DS -> (testo per traduttore, {segnaposto: codice})"""
    t = textdb.FURI.sub(r'\1', body)
    t = re.sub(r"\[\$511'\d+\]", '', t).replace("[$514'0]", '私')
    t = t.replace('▼', ' ').replace('　', ' ').replace('[[', '［')
    tags, n = {}, 0

    def sub(m):
        nonlocal n
        c = m.group(0)
        if c == '[$500]':
            tags['<P>'] = c; return '<P>'
        mm = re.fullmatch(r"\[\$0'(\d+)\]", c)
        if mm:
            if mm.group(1) == '1':
                tags['</c>'] = c; return '</c>'
            tags[f'<c{mm.group(1)}>'] = c; return f'<c{mm.group(1)}>'
        for k, v in tags.items():
            if v == c and k.startswith('<X'):
                return k
        n += 1
        tags[f'<X{n}>'] = c
        return f'<X{n}>'
    t = CODE.sub(sub, t)
    t = re.sub(r'\[#[0-9A-F]{4}\]', '', t)
    return re.sub(r' +', ' ', t).strip(), tags


def load_glossary():
    g = {}
    for line in list(open(os.path.join(ROOT, 'work', 'glossary', 'npc_ds.tsv'), encoding='utf-8'))[1:]:
        c = line.rstrip('\n').split('\t')
        if c[1] and c[2]:
            g.setdefault(c[1], c[2])
    for k, v in json.load(open(os.path.join(ROOT, 'work', 'glossary', 'glossario.json'), encoding='utf-8')).items():
        if len(k) >= 2:
            g.setdefault(k, v)
    for line in list(open(os.path.join(ROOT, 'work', 'glossary', 'glossario_3ds_manuale.tsv'), encoding='utf-8'))[1:]:
        c = line.rstrip('\n').split('\t')
        if len(c) >= 2:
            g[c[0]] = c[1] + (f' ({c[2]})' if len(c) > 2 and c[2] else '')
    return g


def main():
    done = set()
    for name in ('ds_pages.json', 'batch_pages.json', 'manual_pages.json'):
        p = os.path.join(TRAD, name)
        if os.path.exists(p):
            done |= set(json.load(open(p, encoding='utf-8')))
    units, seen = [], set()
    for f, groups in textdb.load_all().items():
        if f == 'npc':
            continue
        for skey, slot in textdb.iter_slots(groups):
            for p in textdb.split_pages(slot):
                lead, body, trail = split_page(p)
                if not textdb.JP.search(body) or page_key(body) in done:
                    continue
                jp, tags = to_placeholders(body + trail)
                if jp in done or jp in seen:
                    continue
                seen.add(jp)
                units.append(dict(id=len(units), file=f, slot=skey, jp=jp, tags=tags))
    gloss = load_glossary()
    terms = sorted((t for t in gloss if len(t) >= 3 or re.search(r'[一-鿿]', t)), key=len, reverse=True)
    bdir = os.path.join(TRAD, 'batches')
    os.makedirs(bdir, exist_ok=True)
    batches, cur, size = [], [], 0
    for u in units:
        cur.append(u); size += len(u['jp'])
        if size >= BATCH_CHARS:
            batches.append(cur); cur, size = [], 0
    if cur:
        batches.append(cur)
    for i, b in enumerate(batches):
        with open(os.path.join(bdir, f'b{i:03d}.tsv'), 'w', encoding='utf-8') as f:
            for u in b:
                f.write(f"{u['id']}\t{u['jp']}\n")
        text = '\n'.join(u['jp'] for u in b)
        hits = []
        for t in terms:
            # termine katakana: non deve far parte di una parola katakana più lunga
            pat = re.escape(t)
            if re.fullmatch(r'[ァ-ヺー・]+', t):
                pat = r'(?<![ァ-ヺー])' + pat + r'(?![ァ-ヺー])'
            if re.search(pat, text):
                hits.append(t)
                text = re.sub(pat, '', text)
        with open(os.path.join(bdir, f'b{i:03d}.gloss.tsv'), 'w', encoding='utf-8') as f:
            for t in hits:
                f.write(f'{t}\t{gloss[t]}\n')
    json.dump(units, open(os.path.join(TRAD, 'units.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'{len(units)} unità, {sum(len(u["jp"]) for u in units)} caratteri, {len(batches)} lotti')


if __name__ == '__main__':
    main()
