"""QoL 1 (1.5): viaggio rapido dalla Mappa del villaggio, con il fumo dei fantasmi della casa infestata.
Sulla Mappa (menu 161, input FUN_0038b1f4) toccare un'icona la seleziona (nome del luogo); toccare di nuovo l'icona GIA'
selezionata oggi non fa nulla (0x38b3e8 beq -> return 0). Qui quel secondo tocco avvia l'evento GROUP*100 + icona
(FUN_001d6b48(gruppo, indice, 0xff), come gli altri avvii di eventi) e chiude la Mappa (return -1, come il tasto chiudi);
se il sistema eventi e' occupato resta il comportamento originale.

Eventi nuovi (evscript.rdbt/rndx, gruppo libero 1202): stessa scena del fantasma (script 5501, 13/10):
  op065(502, 127) suono + op040(0, 0, 0, 1, 35, 150) = effetto 35 (ef_035, nuvola di fumo) sul giocatore per 150 frame,
  op04c(0, 0) nasconde il giocatore, warp, e all'arrivo di nuovo fumo e op04c(0, 1) (fumo anche all'arrivo).
  Arrivo come lo script 8220: op06d(); op04c(0,0); op06c(79,1000); op06e(); op06c(17) (senza, il personaggio si vedeva
  prima del fumo).
Warp: gli script EVSC sono compilati in comandi a byte (op N -> comando N - 0x1e, tabella 0x554b94):
  op05e(mappa, x, y, z) -> '@' -> FUN_002d0570 (modo 1: mappa vera)
  op05f(255, x, y, z)   -> 'A' -> FUN_002d0548 (modo 0: campo del villaggio, come le uscite; usato da 100102, 103...)
(op05e(65535, ...) verso il campo = schermo nero: prima prova 13/10.)
Destinazioni prese giocando (tour_log.py 13/10: davanti a ogni luogo si e' toccata la sua icona): punti calpestabili.
  python fast_travel.py        listato del codice + script di un'icona
"""
import os, struct, sys
sys.path.insert(0, os.path.dirname(__file__))
import armasm

GROUP = 1202
SITE = 0x38B3E8           # beq 0x38b43c (icona toccata == icona selezionata)
SITE_OLD = 0x0A000013     # beq +0x4c
START_EVENT = 0x1D6B48
FIELD = 65535
SMOKE = [(0x65, 502, 127), (0x40, 0, 0, 0, 1, 35, 150)]

DEST = {
    0: (FIELD, 10.5, 0, 13.5),     # Foresta
    1: (FIELD, 10, 0, 42.25),      # Foresta dei Funghi
    2: (FIELD, 12, 0, 79),         # Rovine
    3: (FIELD, 28, 0, 12),         # Caverna
    4: (FIELD, 60, 0, 64),         # Parco
    5: (FIELD, 60.5, 0, 76.5),     # Cortile
    6: (67, 14, 0, 14.75),         # Isola
    7: (49, 6, 0, 9.75),           # Punta degli Innamorati
    8: (64, 5, 0, 13.5),           # Spiaggia
    9: (FIELD, 32.5, 0, 72.75),    # Torre
    10: (64, -0.5, 0, 9.75),       # Sala Eventi
    11: (FIELD, 77.25, 0, 42.75),  # Dormitorio
    12: (FIELD, 44, 0, 8),         # Casa infestata
    13: (FIELD, 38, 0, 50.25),     # case degli abitanti (lotti fissi, tabella 0x550858 + 1.75 in z)
    14: (FIELD, 6, 0, 66.25),
    15: (FIELD, 10, 0, 90.25),
    16: (FIELD, 22, 0, 82.25),
    17: (FIELD, 54, 0, 82.25),
    18: (FIELD, 62, 0, 42.25),
    19: (FIELD, 78, 0, 70.25),
    20: (FIELD, 78, 0, 86.25),
    21: (FIELD, 62, 0, 57),        # Posta
    22: (FIELD, 57, 0, 57),        # Banca
    23: (FIELD, 52.5, 0, 8),       # Appartamento
    24: (FIELD, 44, 0, 24),        # Scuola
    25: (182, 6, 0, 20),           # Castello
    26: (FIELD, 76, 0, 7.75),      # Centro commerciale
    27: (64, 4.375, 0, 0.25),      # Abracadabra (uscita del negozio 181)
}

OFF_VAR = 0x10FD         # variabile 4349 (banco 1, byte 253, libero): 1 = viaggio rapido spento dal Prof. Olmo (options.py)
GET_VAR = 0x160AD0

SRC = '''
    mov r0, #0x1000
    orr r0, r0, #0xfd
    bl getvar
    cmp r0, #0
    bne off
    mov r0, #GRP_HI
    orr r0, r0, #GRP_LO
    mov r1, r5
    mov r2, #0xff
    bl start
    cmp r0, #0
    moveq r0, #0
    mvnne r0, #0
    pop {r4, r5, r6, pc}
off:
    mov r0, #0
    pop {r4, r5, r6, pc}
'''


def build(base):
    src = SRC.replace('GRP_HI', hex(GROUP & 0xff00)).replace('GRP_LO', hex(GROUP & 0xff))
    assert OFF_VAR == 0x1000 | 0xfd
    return armasm.asm(src, base, {'start': START_EVENT, 'getvar': GET_VAR})


def install(d, base, BASE=0x100000):
    """codice a base + salto dal punto d'aggancio; restituisce la fine del codice"""
    code, _ = build(base)
    d[base - BASE:base - BASE + len(code)] = code
    so = SITE - BASE
    assert struct.unpack_from('<I', d, so)[0] == SITE_OLD, "viaggio rapido: punto d'aggancio inatteso"
    struct.pack_into('<I', d, so, 0x0A000000 | (((base - SITE - 8) >> 2) & 0xFFFFFF))
    return base + len(code)


def _f(x):
    return struct.unpack('<I', struct.pack('<f', float(x)))[0]


def script(dest):
    """blocco EVSC3.00: token (u32 valore, u8 tipo, ff ff ff); tipo 0 = ultimo token dell'istruzione, 2 = gli altri,
    255 = ultimo token del blocco; poi 4 byte ff (come gli originali)"""
    m, x, y, z = dest
    warp = (0x5F, 255, x, y, z) if m == FIELD else (0x5E, m, x, y, z)
    prog = [(0x80,)] + SMOKE + [(0x58, 30), (0x4C, 0, 0), (0x58, 30), warp,
                                (0x6D,), (0x4C, 0, 0), (0x6C, 79, 1000), (0x6E,), (0x6C, 17)] + SMOKE + [(0x58, 20), (0x4C, 0, 1)]
    toks = []
    for op, *args in prog:
        ins = [((len(args) << 16) | op, 2)] + [(_f(a), 2) for a in args]
        ins[-1] = (ins[-1][0], 0)
        toks += ins
    toks[-1] = (toks[-1][0], 255)
    body = b''.join(struct.pack('<I', v) + (b'\xff' * 4 if t == 255 else bytes([t]) + b'\xff' * 3) for v, t in toks)
    size = 0x18 + len(body) + 4
    return b'EVSC3.00' + struct.pack('<4I', 0x1C, size, size, size) + body + b'\xff' * 4


def add_scripts(rdbt, rndx):
    """aggiunge gli eventi GROUP*100+icona in fondo a evscript.rdbt e nell'indice (ordinato per id)"""
    ix = [struct.unpack_from('<3I', rndx, i) for i in range(0, len(rndx), 12)]
    used = {sid for sid, _, _ in ix}
    assert len(rdbt) % 4 == 0
    out = bytearray(rdbt)
    for icon, dest in sorted(DEST.items()):
        sid = GROUP * 100 + icon
        assert sid not in used, f"id {sid} gia' usato"
        blk = script(dest)
        ix.append((sid, len(out), len(blk)))
        out += blk
    ix.sort()
    return bytes(out), b''.join(struct.pack('<3I', *e) for e in ix)


if __name__ == '__main__':
    import evsc
    c, _ = build(0x3F68B0)
    print('\n'.join(armasm.listing(c, 0x3F68B0)))
    print('\n'.join(evsc.dis(script(DEST[21]))))
