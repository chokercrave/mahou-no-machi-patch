"""Blocchi RESO "isolati" dentro archivi TBAF senza nomi (nomi oggetti, prodotti UCC, parole magiche).
Ogni slot è diviso in campi da [#0000]; si traducono i campi con giapponese, mantenendo la struttura.
  python blob_texts.py export   -> work/trad/batches/iNNN.tsv (n, campo jp, '', limite) + blob_fields.json
  python blob_texts.py build    -> applica work/trad/blob_trad.json e installa i tarc nella mod
Limite per file = lunghezza del campo giapponese più lungo del file (i nomi finiscono in campi fissi).
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import reso, tbaf, textdb

ROOT = textdb.ROOT
X = os.path.join(ROOT, 'work', '3ds', 'romfs_x')
ORIG = os.path.join(ROOT, 'work', '3ds', 'romfs')
import paths
MOD = os.path.join(paths.MOD, 'romfs')
BLOBS = {  # tarc -> file RESO al suo interno
    'item/item_common.tarc': ['000.bin'],
    'ucc/ucc_common.tarc': ['000.bin', '001.bin', '002.bin', '003.bin', '004.bin'],
    'ui/menu_input_magic.tarc': ['001.bin'],
}
SKIP = re.compile(r'_{3,}\d+$|無効ID|ダミー')   # segnaposto per oggetti scaricabili/personalizzati


def fields(slot):
    return slot.split('[#0000]')


def load(tarc, f):
    return reso.parse_reso(open(os.path.join(X, tarc + '_x', f), 'rb').read())


def export():
    out, limits = [], {}
    seen = set()
    for tarc, files in BLOBS.items():
        for f in files:
            r = load(tarc, f)
            fl = [x for s in r['slots'] if s for x in fields(s) if textdb.JP.search(x) and not SKIP.search(x)]
            if not fl:
                continue
            lim = max(len(textdb.norm(x)) for x in fl)
            if tarc.startswith('item/'):
                lim = min(lim, 12)      # i nomi interni di sviluppo gonfiano il massimo: i nomi visibili sono <= 12
            for x in fl:
                if x not in seen:
                    seen.add(x)
                    out.append((x, lim))
                    limits[x] = min(limits.get(x, 99), lim)
    bdir = os.path.join(ROOT, 'work', 'trad', 'batches')
    size = 600
    for k in range(0, len(out), size):
        with open(os.path.join(bdir, f'i{k // size:03d}.tsv'), 'w', encoding='utf-8') as fo:
            for n, (x, lim) in enumerate(out[k:k + size]):
                fo.write(f'{k + n}\t{x}\t\t{limits[x]}\n')
    json.dump(limits, open(os.path.join(ROOT, 'work', 'trad', 'blob_limits.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print(len(out), 'campi unici;', (len(out) + size - 1) // size, 'lotti')


# Limiti alzati dopo prova in gioco (le parole magiche mostrano 14 caratteri senza problemi)
LIMIT_OVERRIDE = {'ライムライト': 10}     # "Bar Famosi" (nei dialoghi: Saranno Famosi)
ITEM_PX = 140  # pannelli dei nomi oggetto nelle schermate: ~120 px (10 caratteri giapponesi da 12 px)
# Limite per file più alto di quello calcolato dal giapponese: le parole magiche (limite calcolato 9) stanno in 14 caratteri
# (prova in gioco; dalla 1.1 il fumetto è dinamico e il buffer di mes_win_15 è di 20). Lotti i9xx tradotti con limite 14.
# Vestiti (ucc 001) e accessori (ucc 004): nomi interi fino a 18 caratteri e ITEM_PX (lotto i950, 1.1). Prova in gioco
# 10/10 con "Collana stellata": dialogo, borsa, prezzo, lista prodotti OK; la 1.0 ha gia' nomi DS da 18 ("Gonna stampa fiori").
# NON per ucc 000/003 e i piatti di 004 se cambiassero: sono pezzi che il gioco compone in nomi piu' lunghi.
FILE_LIMIT = {('ui/menu_input_magic.tarc', '001.bin'): 14,
              ('ucc/ucc_common.tarc', '001.bin'): 18, ('ucc/ucc_common.tarc', '004.bin'): 18}


def contexts():
    """(tarc, file) -> limite calcolato come in export(); testo jp -> [(tarc, file) in cui compare]"""
    lims, where = {}, {}
    for tarc, files in BLOBS.items():
        for f in files:
            r = load(tarc, f)
            fl = [x for s in r['slots'] if s for x in fields(s) if textdb.JP.search(x) and not SKIP.search(x)]
            if not fl:
                continue
            lim = max(len(textdb.norm(x)) for x in fl)
            if tarc.startswith('item/'):
                lim = min(lim, 12)
            lims[(tarc, f)] = max(lim, FILE_LIMIT.get((tarc, f), 0))
            for x in set(fl):
                where.setdefault(x, []).append((tarc, f))
    return lims, where


def name_px(s):
    """larghezza di un nome nei layout (font LC: CWDH + 1 px)"""
    import build_text
    return sum(build_text.char_px(c) - 1 for c in s)


def too_long(vis, lim):
    """limite 12 (nomi oggetto): conta la larghezza in pixel, non i caratteri (il gioco mostra almeno
    24 caratteri nel riquadro della borsa; i pannelli delle liste sono larghi ~120 px)"""
    if lim == 12:
        return name_px(vis) > ITEM_PX
    if lim == 18:                       # vestiti/accessori UCC: caratteri E pixel
        return len(vis) > lim or name_px(vis) > ITEM_PX
    return len(vis) > lim


def do_import():
    """batches/iNNN.it.tsv (n, italiano) -> blob_trad.json, con controllo lunghezza/caratteri"""
    import glob
    from batch_import import normalize, font_chars
    limits = json.load(open(os.path.join(ROOT, 'work', 'trad', 'blob_limits.json'), encoding='utf-8'))
    _, where = contexts()
    # blob_limits.json (export) ha il limite del PRIMO file in cui compare il testo (di solito item, 12 = controllo in px):
    # si tiene così (è quello provato in gioco). FILE_LIMIT alza solo i file elencati: un testo che compare solo lì prende
    # il limite alzato; uno che compare anche altrove resta col suo e ha una traduzione a parte per quel file (ctx).
    for jp, cs in where.items():
        if all(c in FILE_LIMIT for c in cs):
            limits[jp] = max(limits.get(jp, 0), max(FILE_LIMIT[c] for c in cs))
    limits.update(LIMIT_OVERRIDE)
    ctx_lim = lambda jp, c: LIMIT_OVERRIDE.get(jp, FILE_LIMIT.get(c, limits.get(jp, 99)))
    chars = font_chars() | {' '}
    trad, ctx, bad = {}, {}, 0   # ctx: 'tarc|file|jp' -> testo che entra solo in alcuni contesti (es. parola magica = nome UCC)
    bdir = os.path.join(ROOT, 'work', 'trad', 'batches')
    for f in sorted(glob.glob(os.path.join(bdir, 'i???.tsv'))):
        src = {l.split('\t')[0]: l.split('\t')[1] for l in open(f, encoding='utf-8') if '\t' in l}
        itp = f[:-4] + '.it.tsv'
        if not os.path.exists(itp):
            continue
        for l in open(itp, encoding='utf-8'):
            if '\t' not in l:
                continue
            n, it = l.rstrip('\n').split('\t', 1)
            jp = src.get(n)
            if jp is None:
                continue
            it2 = normalize(it)
            it3 = normalize(it, names=False)
            vis_ = lambda t: re.sub(r'\[[^\]]*\]', '', t)
            ok = lambda t, lim: t and not textdb.JP.search(vis_(t)) and not too_long(vis_(t), lim) \
                and all(c in chars for c in vis_(t))
            # se il nome ufficiale imposto da normalize non entra nel limite, si tiene quello del lotto
            # (es. ライムライト: "Limelight" nell'elenco da 9, "Saranno Famosi" nei dialoghi)
            good = next((t for t in (it2, it3) if ok(t, limits.get(jp, 99))), None)
            if good:
                trad[jp] = good
                for c in where.get(jp, []):           # un lotto successivo che entra ovunque vince sui contesti
                    ctx.pop(f'{c[0]}|{c[1]}|{jp}', None)
                continue
            hit = False
            for c in where.get(jp, []):               # entra almeno in qualche contesto (limite di quel file)?
                t = next((t for t in (it2, it3) if ok(t, ctx_lim(jp, c))), None)
                if t:
                    ctx[f'{c[0]}|{c[1]}|{jp}'] = t
                    hit = True
            if not hit:
                bad += 1
    json.dump(trad, open(os.path.join(ROOT, 'work', 'trad', 'blob_trad.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    json.dump(ctx, open(os.path.join(ROOT, 'work', 'trad', 'blob_trad_ctx.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(len(trad), 'campi importati;', len(ctx), 'solo in alcuni contesti;', bad, 'scartati')


def build():
    p = os.path.join(ROOT, 'work', 'trad', 'blob_trad.json')
    trad = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
    pc = os.path.join(ROOT, 'work', 'trad', 'blob_trad_ctx.json')
    ctx = json.load(open(pc, encoding='utf-8')) if os.path.exists(pc) else {}
    for tarc, files in BLOBS.items():
        repl, n = {}, 0
        for f in files:
            r = load(tarc, f)
            new = []
            for s in r['slots']:
                if s:
                    fs = fields(s)
                    fs2 = [ctx.get(f'{tarc}|{f}|{x}', trad.get(x, x)) for x in fs]
                    n += sum(1 for a, b in zip(fs, fs2) if a != b)
                    s = '[#0000]'.join(fs2)
                new.append(s)
            r['slots'] = new
            repl[f] = reso.build_reso(r)
        out = os.path.join(MOD, tarc)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        base = out if os.path.exists(out) else os.path.join(ORIG, tarc)   # dopo build_ui: parte dalla mod
        tmp = out + '.tmp'
        tbaf.rebuild(base, repl, tmp)
        os.replace(tmp, out)
        print(f'{tarc}: {n} campi tradotti')


if __name__ == '__main__':
    {'export': export, 'import': do_import, 'build': build}[sys.argv[1]]()
