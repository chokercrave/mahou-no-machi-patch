"""QoL 7 (1.2): relazioni con abitanti di qualsiasi sesso (script.tarc -> evscript.rdbt, script 128080).

128080 = evento del Bouquet d'invito (おさそいブーケ) regalato a un abitante (8080 = l'abitante). docs/RE_atlas.md §7.
Originale:
  0x498 var 1049260 = 0; op06c(342, 0) / op06c(342, 8080) = sesso giocatore / abitante; se uguali -> 1049260 = 1
  0x558 op063(3307) "Il tuo cuore e' pronto?" + scelta 3308 (Tutto a posto! / Non ancora) -> var 8392
  0x578 8392 == 0 -> avanti (0x5b8), altrimenti 0x8c0 (respiro e richiede: non si puo' annullare)
  0x840 1049260 == 0 -> 0x990 FIDANZATI (righe 270-272; 148 = fidanzati del giocatore < 1, sennò 284;
        189 = amore >= 80 -> 0xd18 successo op04e(8080, 0, 4) riga 273, sennò 0x16b8 riga 278 "no, grazie")
  0x880 1049260 == 1 -> 0xbd0 AMICI PER LA PELLE (269; 156 < 1 sennò 286; 151 = amicizia >= 80 -> 0x1fb8 riga 281)
  La riga 285 ("siamo tutti e due maschi... no, grazie") e' codice morto (0x19b8-0x1cb8, nessun salto ci arriva).
Patch (stessa lunghezza, nessun offset cambia):
  A 0x578: op091(8392, 1049260) x2 + op014(0x5b8): la SCELTA del giocatore (3308 diventa "Amore / Amicizia")
           sostituisce il flag "stesso sesso" -> 0 = fidanzati, 1 = amici per la pelle, per qualsiasi coppia.
  B 0xb50: amore < 80 -> 0x19b8 (codice morto riusato): se i sessi sono uguali e l'amicizia e' >= 80 la dichiarazione
           riesce (0xd18), altrimenti il rifiuto originale (0x16b8). Il gioco non e' mai arrivato li' con lo stesso sesso:
           se i punti amore crescessero solo tra sessi diversi, la scelta "Amore" non finirebbe mai in un vicolo cieco.
  python patch_relationships.py      verifica (modello di tutte le combinazioni) senza scrivere nulla
"""
import os, struct, sys
sys.path.insert(0, os.path.dirname(__file__))
import evsc

SID = 128080
F = lambda x: struct.unpack('<I', struct.pack('<f', float(x)))[0]
CHOICE, FLAG, PSEX, RES = 8392, 1049260, 1049262, 1056768
NPC = 8080


def op(n, code):
    return (n << 16) | code


def j(off):
    """destinazione di salto: offset dal blocco + 0x20"""
    return F(off - 0x20)


# token (valore, tipo) copiati dagli schemi gia' presenti nello script (tipo: come nelle istruzioni originali analoghe)
def i_copy(src, dst):            # op091(src, dst)            schema di 0x4c8
    return [(op(2, 0x91), 2), (F(src), 2), (F(dst), 0)]


def i_jump(off):                 # op014(off)                 schema di 0x530
    return [(op(1, 0x14), 2), (j(off), 0)]


def i_query(sub, who):           # op06c(sub, who) -> RES      schema di 0x4b0 / 0xb38
    return [(op(2, 0x6c), 2), (F(sub), 2), (F(who), 0)]


def i_if_ne_vars(a, b, off):     # op016(op00b(op08f(a), op08f(b)), off)   schema di 0x4f8 (op00c -> op00b)
    return [(op(2, 0x16), 0), (op(2, 0x0b), 0), (op(1, 0x8f), 2), (F(a), 0), (op(1, 0x8f), 2), (F(b), 2), (j(off), 0)]


def i_if_ge(var, val, off):      # op016(op007(op08f(var), val), off)      schema di 0xb90
    return [(op(2, 0x16), 0), (op(2, 0x07), 0), (op(1, 0x8f), 2), (F(var), 2), (F(val), 2), (j(off), 0)]


PATCH_A = (0x578, 0x5b8, i_copy(CHOICE, FLAG) + i_copy(CHOICE, FLAG) + i_jump(0x5b8))
TRAMP = 0x19b8
PATCH_B_TOKENS = (i_query(342, 0) + i_copy(RES, PSEX) + i_query(342, NPC) + i_if_ne_vars(PSEX, RES, 0x16b8)
                  + i_query(151, NPC) + i_if_ge(RES, 80, 0xd18) + i_jump(0x16b8))
DEAD_END = 0x1cb8                # fine del blocco morto della riga 285


def _put(blk, at, toks):
    for k, (v, t) in enumerate(toks):
        struct.pack_into('<II', blk, at + 8 * k, v, t | 0xffffff00)


def patch_block(blk):
    blk = bytearray(blk)
    toks = {k: (v, t) for k, v, t in evsc.tokens(bytes(blk))}
    # controlli sull'originale
    assert toks[0x578] == (op(2, 0x16), 0) and toks[0x590][0] == F(CHOICE), 'A: controllo della scelta non trovato'
    assert toks[0xb50] == (op(2, 0x16), 0) and toks[0xb58][0] == op(2, 0x0a) and toks[0xb70][0] == F(80) \
        and toks[0xb78][0] == j(0xb90), 'B: controllo amore >= 80 non trovato'
    assert toks[0x1a28] == (op(3, 0x61), 2) and toks[0x1a40][0] == F(285), 'riga 285 non nel blocco morto'
    a0, a1, ta = PATCH_A
    assert len(ta) * 8 == a1 - a0
    _put(blk, a0, ta)
    struct.pack_into('<I', blk, 0xb78, j(TRAMP))
    assert TRAMP + 8 * len(PATCH_B_TOKENS) <= DEAD_END
    _put(blk, TRAMP, PATCH_B_TOKENS)
    return bytes(blk)


# 105003 = reazioni ai regali. Torta / biscotto magico: op06c(342, 7027) = sesso dell'abitante, var 40 = sesso del giocatore;
# SOLO tra sessi diversi la reazione romantica (righe 200/204/205: +43 punti amore op04f(npc, 0, 43), poi appuntamento;
# righe 220/223: +24 e appuntamento), altrimenti quella generica (201 / 202). Patch C: il salto "stesso sesso" (op014 dopo
# op016(op00b(sesso, var40), romantico)) punta anche lui al ramo romantico -> il sesso non conta. L'evento del cuore (128060)
# ha gia' la variante per lo stesso sesso (riga 28).
GIFT_SID = 105003
GIFT_SITES = [(0x1a78, 0x1ab0), (0x21b8, 0x21f0)]     # (op016 test del sesso, op014 del ramo "stesso sesso")


def patch_gift(blk):
    blk = bytearray(blk)
    toks = {k: (v, t) for k, v, t in evsc.tokens(bytes(blk))}
    for test, jump in GIFT_SITES:
        assert toks[test][0] == op(2, 0x16) and toks[test + 8][0] == op(2, 0x0b) \
            and toks[test + 0x18][0] == F(RES) and toks[test + 0x28][0] == F(40), f'105003 {test:#x}: test del sesso non trovato'
        assert toks[jump][0] == op(1, 0x14), f'105003 {jump:#x}: salto non trovato'
        struct.pack_into('<I', blk, jump + 8, toks[test + 0x30][0])     # stessa destinazione del ramo "sessi diversi"
    return bytes(blk)


def patch(rdbt, rndx):
    """applica le patch ai blocchi 128080 e 105003 dentro evscript.rdbt (stessa dimensione)"""
    idx = {sid: (off, sz) for sid, off, sz in (struct.unpack_from('<3I', rndx, i) for i in range(0, len(rndx), 12))}
    for sid, fn in ((SID, patch_block), (GIFT_SID, patch_gift)):
        off, sz = idx[sid]
        new = fn(rdbt[off:off + sz])
        assert len(new) == sz
        rdbt = rdbt[:off] + new + rdbt[off + sz:]
    return rdbt


# ---------- modello: percorre lo script come la VM (solo controllo di flusso + le query usate) ----------
def simulate(blk, env):
    """env: psex, nsex, choice, q206, q188, q148, q156, love(189), friend(151). -> (righe op061, stato op04e)"""
    ins = {n[0]: n for n in evsc.insns(blk)}
    order = sorted(ins)
    var = {}
    lines, status = [], None
    val = lambda x: x[0] if isinstance(x, tuple) and len(x) == 2 and not isinstance(x[0], tuple) and x[0] > 0xffffff \
        else x
    fl = lambda v: struct.unpack('<f', struct.pack('<I', v))[0]

    def ev(node):
        if isinstance(node, tuple) and len(node) == 2:          # numero
            return fl(node[0]) if node[0] > 0xffffff else 0.0
        _, code, kids = node
        c = code & 0xffff
        a = [ev(k) for k in kids]
        if c == 0x8f: return var.get(int(a[0]), 0)
        if c == 0x0b: return a[0] != a[1]
        if c == 0x0c: return a[0] == a[1]
        if c == 0x0a: return a[0] < a[1]
        if c == 0x07: return a[0] >= a[1]
        if c == 0x01a: return a[0] and a[1]
        raise ValueError(hex(c))

    pc, steps = 0x18, 0
    while steps < 5000:
        steps += 1
        _, code, kids = ins[pc]
        c = code & 0xffff
        nxt = order[order.index(pc) + 1] if order.index(pc) + 1 < len(order) else None
        if c == 0x16:
            if ev(kids[0]):
                nxt = int(fl(kids[1][0])) + 0x20
        elif c == 0x14:
            nxt = int(fl(kids[0][0])) + 0x20
        elif c == 0x8e:
            var[int(ev(kids[0]))] = ev(kids[1])
        elif c == 0x91:
            var[int(ev(kids[1]))] = var.get(int(ev(kids[0])), 0)
        elif c == 0x6c and kids:
            sub = int(ev(kids[0])); who = int(ev(kids[1])) if len(kids) > 1 else None
            r = {342: env['psex'] if who == 0 else env['nsex'], 206: env['q206'], 188: env['q188'], 148: env['q148'],
                 156: env['q156'], 189: env['love'], 151: env['friend'], 11: NPC}.get(sub)
            if r is not None:
                var[RES] = r
        elif c == 0x63 and int(ev(kids[0])) == 3307:
            var[CHOICE] = env['choice']
        elif c == 0x61:
            lines.append(int(ev(kids[2])))
        elif c == 0x4e:
            status = int(ev(kids[2]))
        elif c in (0x5f,) or code == 0xffffffff:
            break
        if nxt is None or nxt == 0x39c8:
            break
        pc = nxt
    return lines, status


def expected(env):
    """risultato voluto: la scelta decide il tipo per qualsiasi coppia; i controlli originali restano"""
    if env['q206'] != 0:
        return 292, None
    if env['q188'] in (3, 4):
        return 288, None
    same = env['psex'] == env['nsex']
    if env['choice'] == 0:                                 # Amore
        if env['q148'] >= 1:
            return 284, None
        ok = env['love'] >= 80 or (same and env['friend'] >= 80)
        return (273, 4) if ok else (278, None)
    if env['q156'] >= 1:                                   # Amicizia
        return 286, None
    return (281, 3) if env['friend'] >= 80 else (279, None)


def prove(blk):
    import itertools
    # il blocco deve ancora disassemblarsi e ogni salto deve cadere su un'istruzione
    nodes = {n[0]: n for n in evsc.insns(blk)}
    for k, n in nodes.items():
        if n[1] & 0xffff in (0x14, 0x16):
            tgt = int(struct.unpack('<f', struct.pack('<I', n[2][-1][0]))[0]) + 0x20
            assert tgt in nodes, (hex(k), hex(tgt))
    n = 0
    for ps, ns, ch, q206, q188, q148, q156, love, fr in itertools.product(
            (0, 1), (0, 1), (0, 1), (0, 1), (0, 2, 3, 4), (0, 1), (0, 1), (10, 90), (10, 90)):
        env = dict(psex=ps, nsex=ns, choice=ch, q206=q206, q188=q188, q148=q148, q156=q156, love=love, friend=fr)
        lines, st = simulate(blk, env)
        want_line, want_st = expected(env)
        assert want_line in lines and st == want_st and 285 not in lines, (env, lines, st)
        n += 1
    return n


def main():
    blk = evsc.load('evscript')[SID]
    new = patch_block(blk)
    diff = [i for i in range(0, len(blk), 4) if blk[i:i + 4] != new[i:i + 4]]
    print(f'128080: {len(diff)} parole cambiate, {prove(new)} combinazioni del modello OK '
          f'(M/M F/F M/F F/M x Amore/Amicizia x controlli originali)')


if __name__ == '__main__':
    main()
