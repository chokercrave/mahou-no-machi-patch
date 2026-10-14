"""Ver.1.1 (aggiornamento ufficiale v1056, solo exefs: la romfs e' quella della cartuccia) -> mappa degli indirizzi 1.0 -> 1.1.

Segmenti (exheader): .text 0x100000 (1.0 0x44ac88 / 1.1 0x44b640), .rodata 0x54b000 -> 0x54c000, .data 0x588000 -> 0x589000.
Il codice 1.1 e' lo stesso compilato con poche funzioni cambiate: le funzioni seguenti scorrono. Confronto funzione per
funzione (lista Ghidra work/re/decomp/functions.tsv) su parole "normalizzate": salti b/bl senza offset, puntatori nel
programma ridotti a un segnaposto (cambiano solo per lo spostamento).
  python port11.py            -> work/v11/funcmap.tsv (indirizzo 1.0, indirizzo 1.1 o vuoto, dimensione, stato)
"""
import array, bisect, os, struct, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C10 = os.path.join(ROOT, 'work', '3ds', 'exefs', 'code.bin')
C11 = os.path.join(ROOT, 'work', 'v11', 'exefs', 'code.bin')
FUNCS = os.path.join(ROOT, 'work', 're', 'decomp', 'functions.tsv')
OUT = os.path.join(ROOT, 'work', 'v11', 'funcmap.tsv')
BASE = 0x100000
TEXT10, TEXT11 = 0x44AC88, 0x44B640


def norm(d, n):
    w = array.array('I', d[:n])
    out = array.array('I', w)
    for i, x in enumerate(w):
        if (x >> 25) & 7 == 5:
            out[i] = x & 0xFF000000
        elif BASE <= x < 0x700000:
            out[i] = 1
    return out


def build():
    a, b = open(C10, 'rb').read(), open(C11, 'rb').read()
    A, B = norm(a, TEXT10), norm(b, TEXT11)
    funcs = []
    for line in open(FUNCS, encoding='utf-8').read().splitlines()[1:]:
        f = line.split('\t')
        ad, sz = int(f[0], 16), int(f[1])
        if BASE <= ad < BASE + TEXT10 and sz >= 4:
            funcs.append((ad, sz))
    funcs.sort()
    d = 0
    rows = []
    for ad, sz in funcs:
        i, n = (ad - BASE) // 4, max(1, sz // 4)
        seg = A[i:i + n]

        def ok(dd):
            j = i + dd // 4
            return 0 <= j and j + n <= len(B) and B[j:j + n] == seg
        if ok(d):
            rows.append((ad, ad + d, sz, 'uguale'))
            continue
        hit = None
        for k in range(1, 0x1000):          # cerca il nuovo spostamento vicino a quello corrente (+-16 KB)
            for dd in (d + 4 * k, d - 4 * k):
                if ok(dd):
                    hit = dd
                    break
            if hit is not None:
                break
        if hit is None:
            rows.append((ad, None, sz, 'cambiata'))
        else:
            d = hit
            rows.append((ad, ad + d, sz, 'spostata'))
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('addr10\taddr11\tsize\tstato\n')
        for ad, a11, sz, st in rows:
            f.write(f'{ad:08x}\t{"" if a11 is None else f"{a11:08x}"}\t{sz}\t{st}\n')
    return rows


def load():
    rows = []
    for line in open(OUT, encoding='utf-8').read().splitlines()[1:]:
        a, b, s, st = line.split('\t')
        rows.append((int(a, 16), int(b, 16) if b else None, int(s), st))
    return rows


_rows = _starts = _A = _B = None
RODATA10, RODATA_INS, DATA10, PROG_END10 = 0x54B000, 0x5784B0, 0x588000, 0x588000 + 0x28000 + 0x62000
TABLES10, TABLES_DELTA = 0x587E00, 0xE00          # -> 0x588c00..0x588e00 nel .rodata libero 1.1 (0x588600-0x589000)


def _local(x, win=6):
    """allineamento locale (funzioni cambiate, es. macchina di avvio 0x396990: +0x4c8 dopo il dispatcher): unico
    spostamento entro -1/+4 KB con 2*win parole normalizzate uguali attorno a x"""
    global _A, _B
    if _A is None:
        _A = norm(open(C10, 'rb').read(), TEXT10)
        _B = norm(open(C11, 'rb').read(), TEXT11)
    i = (x - BASE) // 4
    seg = _A[i - win:i + win]
    hits = [dd for dd in range(-0x400, 0x1000, 4) if _B[i + dd // 4 - win:i + dd // 4 + win] == seg]
    return x + hits[0] if len(hits) == 1 else None


def map_addr(x):
    """indirizzo 1.0 -> 1.1 (None se non determinabile con certezza)"""
    global _rows, _starts
    if TABLES10 <= x < DATA10:
        return x + TABLES_DELTA               # tabelle delle patch in fondo al .rodata 1.0 (larghezze dei font, 0x587e00 /
                                              # 0x587f00): con +0x1014 sconfinavano di 0x14 byte nel .data 1.1 (0x589000)
    if RODATA10 <= x < PROG_END10:
        if x >= DATA10:
            return x + 0x1000                   # .data/.bss: una pagina
        return x + (0x1014 if x >= RODATA_INS else 0x1000)   # .rodata: vtable nuova di 5 parole prima di 0x5784b0
    if not BASE <= x < RODATA10:
        return None
    if _rows is None:
        _rows = load()
        _starts = [r[0] for r in _rows]
    k = bisect.bisect_right(_starts, x) - 1
    if k < 0:
        return x                                # prima della prima funzione: identico
    ad, a11, sz, st = _rows[k]
    if a11 is not None and x < ad + max(sz, 4) + 0x400:
        return x - ad + a11
    return _local(x)


def is_branch(w):
    return (w >> 25) & 7 == 5 and (w >> 28) != 0xF


def branch_target(site, w):
    off = w & 0xFFFFFF
    off = off - (1 << 24) if off & 0x800000 else off
    return site + 8 + off * 4


def rebranch(site, w, tgt):
    return (w & 0xFF000000) | (((tgt - site - 8) >> 2) & 0xFFFFFF)


def port(o10, e10, o11, d11, relocs, caves, extra_ptrs=(), consts=()):
    """porta su d11 (copia di o11, eventualmente gia' con le stringhe) le parole cambiate tra o10 ed e10.
    Ogni parola: indirizzo mappato + verifica che il contenuto ORIGINALE coincida (normalizzato) tra 1.0 e 1.1.
    Contenuto nuovo: salti ritargettati, puntatori mappati, il resto copiato.
      relocs: armasm.RELOCS (indirizzo, 'b'|'ptr', valore) -- per le cave decide solo il registro
      caves: [(inizio, fine)] in indirizzi 1.0 (codice nostro: niente euristiche sui dati)
      extra_ptrs: indirizzi 1.0 di parole che sono puntatori anche se l'originale non lo era
      consts: indirizzi 1.0 di letterali '=#valore' (armasm.CONSTS): copiati tali e quali, mai rilocati"""
    rel = {}
    for at, kind, val in relocs:
        rel[at] = (kind, val)
    in_cave = lambda x: any(a <= x < b for a, b in caves)
    cave_ptr = lambda v: any(a <= v < b for a, b in caves)
    u32 = lambda d, x: struct.unpack_from('<I', d, x - BASE)[0]
    stats = {'b': 0, 'ptr': 0, 'raw': 0}
    for x in range(BASE, BASE + min(len(o10), len(e10)) // 4 * 4, 4):
        old, new = u32(o10, x), u32(e10, x)
        if old == new:
            continue
        y = map_addr(x)
        assert y is not None, f'{x:#x}: indirizzo 1.1 non determinabile'
        o11w = u32(o11, y)
        same = old == o11w or (is_branch(old) and is_branch(o11w) and (old >> 24) == (o11w >> 24)) or \
            (BASE <= old < 0x700000 and BASE <= o11w < 0x700000)
        assert same, f'{x:#x}->{y:#x}: contenuto originale diverso ({old:#010x} / {o11w:#010x})'
        kind = None
        if x in consts:
            stats['raw'] += 1
            struct.pack_into('<I', d11, y - BASE, new)
            continue
        if x in rel:
            k, v = rel[x]
            if k == 'b' and is_branch(new) and branch_target(x, new) == v:
                kind = 'b'
            elif k == 'ptr' and new == v and v < PROG_END10:
                kind = 'ptr'                                # (costanti oltre la .bss, es. 0x6e6977, restano tali)
        if kind is None and not in_cave(x):
            if RODATA10 > x and is_branch(new) and not (BASE <= old < 0x700000):
                kind = 'b'                                  # salto scritto da Python in un punto del codice originale
            elif x in extra_ptrs or (BASE <= old < 0x700000 and BASE <= new < 0x700000 and map_addr(old) == o11w) \
                    or cave_ptr(new):
                kind = 'ptr'
        if kind == 'b':
            t11 = map_addr(branch_target(x, new))
            assert t11 is not None, f'{x:#x}: destinazione {branch_target(x, new):#x} non mappabile'
            w = rebranch(y, new, t11)
        elif kind == 'ptr':
            w = map_addr(new)
            assert w is not None, f'{x:#x}: puntatore {new:#x} non mappabile'
        else:
            w = new
        stats[kind or 'raw'] += 1
        struct.pack_into('<I', d11, y - BASE, w)
    return stats


if __name__ == '__main__':
    rows = build()
    from collections import Counter
    print(Counter(r[3] for r in rows))
    ch = [r for r in rows if r[3] == 'cambiata']
    print('cambiate:', ' '.join(f'{r[0]:#x}({r[2]})' for r in ch[:60]))
