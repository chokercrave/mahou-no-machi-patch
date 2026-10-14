"""Script evento EVSC3.00 (script.tarc: evscript/actscript .rdbt + .rndx) — disassemblatore (QoL 1.1).

.rndx : (u32 id, u32 offset, u32 size) per script dentro .rdbt
blocco: 'EVSC3.00', u32 0x1c, u32 size x3, poi token da 8 byte a partire da 0x18:
  u32 valore, u8 tipo, 3 byte 0xff (tipo 0/2/4/255: ruolo non ancora chiaro).
  albero PREFISSO: token < 0x00ff0000 = operatore (argc << 16 | opcode) seguito da argc sotto-espressioni;
  altrimenti numero float (anche gli id delle variabili). Salti: offset in byte da blocco+0x20.
  op016(cond, off) = se cond VERA salta a off; op014(off) = salta; op00b(a, b) = a != b; op00c(a, b) = a == b
  (dedotto dallo script 1021 del Prof. Olmo); op008/op009/op00a altri confronti; op08f(var) = valore variabile;
  op08e(var, val) = assegna; op061(npc, file, riga[, x]) = dialogo: gruppo file*1000 + riga//100, slot riga%100; op058(n) = attesa.
  python evsc.py dis <id> [max]      disassembla uno script
  python evsc.py find <float> [...]  script/istruzioni che usano quei numeri
"""
import os, struct, sys
sys.path.insert(0, os.path.dirname(__file__))
import tbaf

ROOT = os.path.join(os.path.dirname(__file__), '..')
TARC = os.path.join(ROOT, 'work', '3ds', 'romfs', 'script.tarc')


def load(kind='evscript'):
    ents = {e['name']: e for e in tbaf.parse(open(TARC, 'rb').read())}
    raw = lambda n: tbaf.decompress(ents[n]['data']) if ents[n]['comp'] else ents[n]['data']
    x, r = raw(kind + '.rndx'), raw(kind + '.rdbt')
    return {sid: r[off:off + sz] for sid, off, sz in (struct.unpack_from('<3I', x, i) for i in range(0, len(x), 12))}


def tokens(blk):
    for k in range(0x18, len(blk) - 7, 8):
        v, t = struct.unpack_from('<II', blk, k)
        yield k, v, t & 0xff


def is_op(v):
    """token operatore: valore < 0x00ff0000 e non nullo (i numeri sono float: 1.0 = 0x3f800000; lo 0 e' il numero 0)"""
    return 0 < v < 0x00ff0000 or v == 0xffff


def insns(blk):
    """albero prefisso: -> (offset, opcode, [figli]); figlio = (valore, tipo) oppure tupla (offset, opcode, [figli])"""
    toks = list(tokens(blk))
    pos = 0

    def node():
        nonlocal pos
        k, v, t = toks[pos]
        pos += 1
        if not is_op(v):
            return (v, t)
        args = []
        for _ in range(v >> 16 if v != 0xffff else 0):
            if pos >= len(toks):
                break
            args.append(node())
        return (k, v & 0xffff, args)

    while pos < len(toks):
        n = node()
        if len(n) == 3:
            yield n
        else:
            yield (toks[pos - 1][0], -1, [n])      # letterale isolato


def fmt(v, t):
    f = struct.unpack('<f', struct.pack('<I', v))[0]
    if t in (0, 2) and (v == 0 or 1e-4 < abs(f) < 1e8) and f == round(f, 3):
        return str(int(f)) if f == int(f) else f'{f:g}'
    return f'#{v:08x}' + ('' if t in (0, 2) else f'/{t}')


def expr(n):
    if len(n) == 2:
        return fmt(*n)
    k, op, args = n
    return f'op{op:03x}(' + ', '.join(expr(a) for a in args) + ')'


def dis(blk, n=10**9):
    out = []
    for node in insns(blk):
        out.append(f'{node[0]:05x}: ' + expr(node))
        if len(out) >= n:
            break
    return out


if __name__ == '__main__':
    S = load(os.environ.get('EVSC', 'evscript'))
    if sys.argv[1] == 'dis':
        print('\n'.join(dis(S[int(sys.argv[2])], int(sys.argv[3]) if len(sys.argv) > 3 else 10**9)))
    elif sys.argv[1] == 'find':
        want = {struct.unpack('<I', struct.pack('<f', float(a)))[0] for a in sys.argv[2:]}
        for sid, blk in S.items():
            for node in insns(blk):
                e = expr(node)
                if any(fmt(w, 0) in e for w in want):
                    print(sid, f'{node[0]:05x}', e)
