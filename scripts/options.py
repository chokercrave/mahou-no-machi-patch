"""Opzioni della patch dal Prof. Olmo (13/10): la voce "じかんわり" (Orario) del suo menu (32012.5 ->
32013.37 [$73'10'21'1] -> script 1021) diventa "Opzioni". Lo script 1021 sceglieva la fascia delle lezioni (var 3150105),
inutile con le lezioni a ogni ora: ora propone Viaggio rapido / Soldi infiniti / Legami stabili / Niente e inverte
l'opzione scelta.

Variabili nuove (docs/RE_atlas.md §1: id = tipo<<20 | banco<<12 | byte, tipo 0 = byte): banco 1, byte 253/254, mai usati
da script (evscript/actscript) ne' come costanti nel codice (scansione 13/10). 0 = comportamento predefinito, cosi' i
salvataggi esistenti partono con viaggio rapido acceso e soldi normali.
  4349 (0x10FD) = 1 -> viaggio rapido SPENTO (letto da fast_travel.py prima di avviare l'evento)
  4350 (0x10FE) = 1 -> soldi infiniti: il portafoglio non scende mai
  4351 (0x10FF) = 1 -> legami stabili: niente calo di amore/amicizia per i giorni senza vedersi
Soldi: portafoglio = FUN_001c58ac() -> [0] contanti (max 999999), [1] banca (max 9999999).
  FUN_001b222c(portafoglio, delta, ...) aggiunge/toglie (8 chiamanti: script op06c, negozi): delta < 0 -> 0
  FUN_001b266c(portafoglio, valore) imposta i contanti (negozi "soldi - prezzo", banca): mai sotto il valore attuale
Legami: al cambio di giorno FUN_001c65dc, per ognuno dei 13 abitanti non incontrati, toglie amore e amicizia (tabella *
giorni, non sotto una soglia) con FUN_001b592c(..., -punti, ...) a 0x1c69e4 (unica chiamata del calo; le altre sono le
interazioni). Con 4351 = 1 quella chiamata viene saltata.
Testi: build_text.SLOT_RAW (52000.59/64/65/66/67/73/74/77/78/79) e SLOT_TEXT (32012.5 "Opzioni").
"""
import os, struct, sys
sys.path.insert(0, os.path.dirname(__file__))
import armasm

SID = 1021
NPC = 2002                 # Prof. Olmo
# 14/10: le opzioni da tutti i prof, davanti all'aula e in sala professori. Uno script per prof
# (op061 fa parlare l'NPC indicato): id -> (npc, angolo finale come il loro "Lascia": 22140/22130/22120/22160).
# 1022-1024 sono id liberi; evscript.rndx e' ordinato (ricerca binaria in FUN_003406bc): si inseriscono in ordine.
TEACHERS = {1021: (2002, 0), 1022: (2001, 270), 1023: (2003, 0), 1024: (2023, 0)}
# battute delle risposte: (file, riga) per op061 -> gruppo file*1000 + riga//100, slot riga%100. I prof parlano in 52000.
LINES52 = {64: (52, 64), 66: (52, 66), 67: (52, 67), 73: (52, 73), 74: (52, 74), 78: (52, 78), 79: (52, 79),
           84: (52, 84), 94: (52, 94), 5: (52, 5)}
# 14/10: opzioni anche da Reginaldo (capo dormitorio, npc 2013, menu 32082.4), che non e' un gran mago
# e le chiede al Preside: battute proprie in 32082/32083 (slot vuoti fuori dagli intervalli casuali [$17'8205'8259] e
# [$17'8310'8349], nessun riferimento: scansione 14/10). Il suo "Lascia" non ha script: niente op038 finale (angolo None).
HELPERS = {1025: (2013, None, {64: (32, 8261), 66: (32, 8265), 67: (32, 8277), 73: (32, 8278), 74: (32, 8279),
                               78: (32, 8301), 79: (32, 8303), 84: (32, 8388), 94: (32, 8389), 5: (32, 8390)})}
FT_OFF, MONEY, BOND = 0x10FD, 0x10FE, 0x10FF
CHOICE = 8392              # indice dell'opzione scelta ([$55])
GET_VAR = 0x160AD0
ADD_MONEY, ADD_OLD = 0x1B222C, 0xE92D00F0      # push {r4, r5, r6, r7}
SET_MONEY, SET_OLD = 0x1B266C, 0xE59F200C      # ldr r2, [pc, #0xc]
CASH_MAX = 999999
DECAY_CALL, DECAY_OLD, POINTS = 0x1C69E4, 0xEBFFBBD0, 0x1B592C   # bl FUN_001b592c (calo giornaliero)
# Merce nuova (14/10): 4348 (0x10FC, banco 1 byte 252, libero: scansione script/codice 14/10) = 1 -> la
# macchina di preparazione dei negozi del caricamento (FUN_0019ebac, stato u8 in 0x5f2874; 0-2 carica il file 0x320,
# 6-7 rigenera con FUN_0019f564, 11 libera e restituisce 1) riparte dallo stato 0 e avanza di un passo a ogni chiamata
# del valutatore dei trigger orari (FUN_002a9664, solo sul campo); 4348 = 2 mentre gira, 0 alla fine.
# Con 4348 = 2 la lista dei negozi parte dall'indice 0 (mappa 51, Emporio: al caricamento normale escluso, mov r8,#1).
RESTOCK = 0x10FC
MACHINE, STATE = 0x19EBAC, 0x5F2874
VARMGR, VARFIND = 0x5BD9B0, 0x16D448          # come FUN_0016cfc4 (getvar): FUN_0016d448(mgr, id, &banco, &off, &tipo, &bit)
EVAL, EVAL_OLD = 0x2A9664, 0xE92D41F0          # push {r4, r5, r6, r7, r8, lr}
FIRST, FIRST_OLD = 0x19F058, 0xE3A08001        # mov r8, #1 (stato 6: primo negozio della lista)
# Riusa materiali (14/10): op06c(18, modo) (gestore 0x4835bc, tabella 0x591ab0; r0 = modo intero)
# svuota la mano del personaggio: modo 0 = rimette l'oggetto nella borsa (vt+0x164), 1 = lo distrugge (2/3 = stessa cosa
# per l'altro oggetto, vt+0x160). Gli incantesimi (SPELLS, messaggi di riuscita 99030/99031) chiamano op06c(18, 1) dopo
# il lancio: negli script il modo diventa 4 (stessa dimensione) e all'ingresso del gestore 4 -> 0 se 4331 = 1, altrimenti 1.
# 4331 (0x10EB, banco 1 byte 0xEB): mai usato (script op08e/f/090/091, letterali e mov+orr nel codice 1.0 e 1.1, 14/10).
# NON 4347 (0xFB): fa parte di 8 byte a 0xff (0xF4-0xFB, 4340 = base usata dal codice) -> 'accesa' in ogni salvataggio.
# Accesa solo se vale esattamente 1 (byte mai scritti possono valere 0xff). Regali, lezioni e look restano col modo 1.
SPELL_VAR = 0x10EB
HOLD, HOLD_OLD = 0x4835C0, 0xE1A05000          # mov r5, r0 (modo)
# Testo veloce tenendo B (14/10, QoL 1.x): macchina da scrivere dei dialoghi FUN_0033de74 stato 6: ogni [+0x17a]
# fotogrammi un carattere (contatore +0x180, totale +0x186); se premuti & 0x403 (A|B|X) o [+0x177] -> pagina intera.
# FUN_0010cc30(&pad) -> [sp] = tenuti, [sp+4] = premuti. 0x33e358 ldr r0,[sp,#4] -> bl fast_text: premuti | (tenuti & B),
# cosi' tenendo B ogni pagina compare subito (per andare avanti resta A). Senza chiamate ne' stack.
FAST, FAST_OLD = 0x33E358, 0xE59D0004          # ldr r0, [sp, #4]
SPELLS = (31001, 31101, 31201, 31601, 32001, 32101, 32201, 33001, 33201, 33401, 34401, 34501, 34601, 34901, 35001,
          35201, 35301, 35501, 35601, 35701, 35801, 35901, 36001, 36101, 133101, 133201, 133301, 133401, 133501,
          303025, 303026)     # 303100 NO: gatto dell'atelier (modifica oggetti), non un incantesimo

SRC = '''
add:
    cmp r1, #0
    bge add_go
    push {r0, r1, r2, r3, ip, lr}
    mov r0, #0x1000
    orr r0, r0, #0xfe
    bl getvar
    cmp r0, #0
    pop {r0, r1, r2, r3, ip, lr}
    movne r1, #0
add_go:
    push {r4, r5, r6, r7}
    b add_back
decay:
    push {r0, r1, r2, r3, ip, lr}
    mov r0, #0x1000
    orr r0, r0, #0xff
    bl getvar
    cmp r0, #0
    pop {r0, r1, r2, r3, ip, lr}
    bne decay_skip
    b points
decay_skip:
    .word 0xe12fff1e
set:
    push {r0, r1, r2, r3, ip, lr}
    mov r0, #0x1000
    orr r0, r0, #0xfe
    bl getvar
    cmp r0, #0
    pop {r0, r1, r2, r3, ip, lr}
    beq set_go
    ldr r2, [r0]
    cmp r1, r2
    movlo r1, r2
set_go:
    ldr r2, =CASH_MAX
    cmp r1, r2
    movhi r1, r2
    str r1, [r0]
    .word 0xe12fff1e
restock:
    push {r0, r1, r2, r3, r4, r5, ip, lr}
    ldr r0, =#0x10fc
    bl getvar
    cmp r0, #0
    beq rs_out
    cmp r0, #1
    bne rs_step
    ldr r1, =0x5f2874
    mov r0, #0
    strb r0, [r1]
    mov r1, #2
    bl rs_set
rs_step:
    mov r0, #0
    bl machine
    cmp r0, #0
    beq rs_out
    mov r1, #0
    bl rs_set
rs_out:
    pop {r0, r1, r2, r3, r4, r5, ip, lr}
    push {r4, r5, r6, r7, r8, lr}
    b eval_back
rs_first:
    push {r0, r1, r2, r3, r4, r5, ip, lr}
    ldr r0, =#0x10fc
    bl getvar
    cmp r0, #2
    moveq r8, #0
    movne r8, #1
    pop {r0, r1, r2, r3, r4, r5, ip, lr}
    .word 0xe12fff1e
rs_set:
    push {r4, lr}
    sub sp, sp, #0x18
    mov r4, r1
    ldr r0, =0x5bd9b0
    ldr r1, =#0x10fc
    add r2, sp, #0x10
    add r3, sp, #0x14
    str r2, [sp]
    str r3, [sp, #4]
    add r2, sp, #8
    add r3, sp, #0xc
    bl varfind
    cmp r0, #0
    beq rs_set_out
    ldrb r0, [sp, #0x10]
    cmp r0, #0
    bne rs_set_out
    ldr r0, [sp, #8]
    ldr r1, [r0, #4]
    ldrh r0, [sp, #0xc]
    strb r4, [r1, r0]
rs_set_out:
    add sp, sp, #0x18
    pop {r4, pc}
fast_text:
    ldr r0, [sp, #4]
    ldr r1, [sp]
    and r1, r1, #2
    orr r0, r0, r1
    .word 0xe12fff1e
spell_mode:
    mov r5, r0
    cmp r5, #4
    bne sm_out
    push {r0, r1, r2, r3, r4, ip, lr}
    ldr r0, =#0x10eb
    bl getvar
    cmp r0, #1
    pop {r0, r1, r2, r3, r4, ip, lr}
    moveq r5, #0
    movne r5, #1
sm_out:
    .word 0xe12fff1e
    .pool
'''


def build(base):
    sym = {'getvar': GET_VAR, 'add_back': ADD_MONEY + 4, 'points': POINTS, 'machine': MACHINE, 'varfind': VARFIND,
           'eval_back': EVAL + 4}
    return armasm.asm(SRC.replace('CASH_MAX', str(CASH_MAX)), base, sym)


def install(d, base, BASE=0x100000):
    """codice dei soldi a base + salti dalle due funzioni; restituisce la fine del codice"""
    code, lab = build(base)
    d[base - BASE:base - BASE + len(code)] = code
    for site, old, tgt in ((ADD_MONEY, ADD_OLD, lab['add']), (SET_MONEY, SET_OLD, lab['set'])):
        assert struct.unpack_from('<I', d, site - BASE)[0] == old, f'opzioni: {site:#x} inatteso'
        struct.pack_into('<I', d, site - BASE, 0xEA000000 | (((tgt - site - 8) >> 2) & 0xFFFFFF))
    # legami stabili: la bl del calo giornaliero passa dal controllo (stessi argomenti, anche quelli sullo stack)
    assert struct.unpack_from('<I', d, DECAY_CALL - BASE)[0] == DECAY_OLD, 'opzioni: chiamata del calo inattesa'
    struct.pack_into('<I', d, DECAY_CALL - BASE, 0xEB000000 | (((lab['decay'] - DECAY_CALL - 8) >> 2) & 0xFFFFFF))
    # merce nuova: valutatore dei trigger -> restock (b); primo negozio dello stato 6 -> rs_first (bl, r8 = 0 o 1)
    # riusa materiali: mov r5, r0 all'ingresso di op06c(18) -> bl spell_mode (r5 = modo, 4 tradotto)
    for site, old, tgt, op in ((EVAL, EVAL_OLD, lab['restock'], 0xEA000000), (FIRST, FIRST_OLD, lab['rs_first'], 0xEB000000),
                               (HOLD, HOLD_OLD, lab['spell_mode'], 0xEB000000),
                               (FAST, FAST_OLD, lab['fast_text'], 0xEB000000)):
        assert struct.unpack_from('<I', d, site - BASE)[0] == old, f'opzioni: {site:#x} inatteso'
        struct.pack_into('<I', d, site - BASE, op | (((tgt - site - 8) >> 2) & 0xFFFFFF))
    return base + len(code)


# --- script 1021 -------------------------------------------------------------------------------------------------
def _f(x):
    return struct.unpack('<I', struct.pack('<f', float(x)))[0]


def script(npc=NPC, angle=0, lines=LINES52, fade=False):
    """op016(cond, off) salta se cond vera (off = indirizzo - 0x20); op00b != , op00c == ; op08f leggi; op08e scrivi.
    Tipi dei token come negli originali (1021, 303100): istruzione piatta = intestazione 2 ... ultimo 0;
    op016(op00x(op08f(v), n), off) = 0, 0, 2, 2, 2, 0; op080() = 0; ultimo token del blocco 255."""
    prog = []          # (etichetta | None, [(valore, tipo)]) ; valori str = etichette da risolvere

    def flat(op, *args):
        t = [((len(args) << 16) | op, 2)] + [(a if isinstance(a, str) else _f(a), 2) for a in args]
        t[-1] = (t[-1][0], 0)
        return t

    def jump_if(cmp_op, var, val, lab):
        return [(0x20016, 0), (0x20000 | cmp_op, 0), (0x1008F, 2), (_f(var), 2), (_f(val), 2), (lab, 0)]

    def say(n):
        return flat(0x61, npc, *lines[n])

    def ins(t, label=None):
        prog.append((label, t))

    ins([(0x80, 0)])
    ins(say(64))                                    # domanda + scelta (65)
    if fade:
        # Reginaldo va a chiedere al Preside: breve nero tra "vado a chiederglielo!" e "Fatto!" (non con "Niente")
        # op024(0, 0|1, fotogrammi, colore) = dissolvenza e ritorno; colore 0 = nero (1 = bianco, come negli incantesimi)
        ins(jump_if(0x0C, CHOICE, 5, 'end'))
        ins(flat(0x24, 0, 0, 20, 0))
        ins(flat(0x58, 35))
        ins(flat(0x24, 0, 1, 20, 0))
        ins(flat(0x58, 20))
    ins(jump_if(0x0B, CHOICE, 0, 'money'))          # scelta != 0 -> soldi
    ins(jump_if(0x0C, FT_OFF, 0, 'ft_off'))         # acceso (0) -> spegni
    ins(flat(0x8E, FT_OFF, 0))
    ins(say(66))
    ins(flat(0x14, 'end'))
    ins(flat(0x8E, FT_OFF, 1), 'ft_off')
    ins(say(67))
    ins(flat(0x14, 'end'))
    ins(jump_if(0x0B, CHOICE, 1, 'bond'), 'money')  # scelta != 1 -> legami
    ins(jump_if(0x0C, MONEY, 0, 'm_on'))
    ins(flat(0x8E, MONEY, 0))
    ins(say(74))
    ins(flat(0x14, 'end'))
    ins(flat(0x8E, MONEY, 1), 'm_on')
    ins(say(73))
    ins(flat(0x14, 'end'))
    ins(jump_if(0x0B, CHOICE, 2, 'restock'), 'bond')
    ins(jump_if(0x0C, BOND, 0, 'b_on'))
    ins(flat(0x8E, BOND, 0))
    ins(say(79))
    ins(flat(0x14, 'end'))
    ins(flat(0x8E, BOND, 1), 'b_on')
    ins(say(78))
    ins(flat(0x14, 'end'))
    ins(jump_if(0x0B, CHOICE, 3, 'spell'), 'restock')
    ins(flat(0x8E, RESTOCK, 1))                     # merce nuova: il codice la prepara al prossimo passaggio sul campo
    ins(say(84))
    ins(flat(0x14, 'end'))
    ins(jump_if(0x0B, CHOICE, 4, 'end'), 'spell')   # "Niente" -> fine
    ins(jump_if(0x0B, SPELL_VAR, 1, 's_on'))         # accesa solo se == 1 (0xff = spenta)
    ins(flat(0x8E, SPELL_VAR, 0))
    ins(say(5))
    ins(flat(0x14, 'end'))
    ins(flat(0x8E, SPELL_VAR, 1), 's_on')
    ins(say(94))
    if angle is None:
        ins(flat(0x58, 1), 'end')                   # nessun orientamento da ripristinare: attesa di 1 fotogramma
    else:
        ins(flat(0x38, npc, angle), 'end')          # chiusura come il loro "Lascia": op038(npc, angolo)
    addr, labels = 0x18, {}
    for lab, t in prog:
        if lab:
            labels[lab] = addr
        addr += 8 * len(t)
    toks = [(_f(labels[v] - 0x20) if isinstance(v, str) else v, ty) for _, t in prog for v, ty in t]
    toks[-1] = (toks[-1][0], 255)
    body = b''.join(struct.pack('<I', v) + (b'\xff' * 4 if t == 255 else bytes([t]) + b'\xff' * 3) for v, t in toks)
    size = 0x18 + len(body) + 12
    return b'EVSC3.00' + struct.pack('<4I', 0x1C, size, size, size) + body + b'\xff' * 12


def spell_scripts(rdbt, rndx):
    """negli incantesimi op06c(18, 1) -> op06c(18, 4) (solo il token del modo, stessa dimensione)"""
    import evsc
    idx = {sid: (off, sz) for sid, off, sz in (struct.unpack_from('<3I', rndx, i) for i in range(0, len(rndx), 12))}
    out, n = bytearray(rdbt), 0
    for sid in SPELLS:
        off, size = idx[sid]
        toks = list(evsc.tokens(bytes(rdbt[off:off + size])))
        hit = [toks[i + 2][0] for i in range(len(toks) - 2)
               if toks[i][1] == 0x2006C and toks[i + 1][1] == _f(18) and toks[i + 2][1] == _f(1)]
        assert hit, f'incantesimo {sid}: op06c(18, 1) non trovato'
        for k in hit:
            struct.pack_into('<I', out, off + k, _f(4))
        n += len(hit)
    return bytes(out), n


def replace_script(rdbt, rndx):
    """script delle opzioni in fondo a evscript.rdbt: 1021 ripuntato (il blocco vecchio resta, non referenziato),
    1022-1024 aggiunti all'indice in ordine di id"""
    ix = [list(struct.unpack_from('<3I', rndx, i)) for i in range(0, len(rndx), 12)]
    assert [e[0] for e in ix] == sorted(e[0] for e in ix), 'evscript.rndx non ordinato'
    out = bytearray(rdbt)
    every = {sid: (npc, angle, LINES52) for sid, (npc, angle) in TEACHERS.items()} | HELPERS
    for sid, (npc, angle, lines) in every.items():
        fade = sid in HELPERS                       # chi chiede al Preside: dissolvenza al nero dopo la scelta
        assert len(out) % 4 == 0
        blk = script(npc, angle, lines, fade)
        e = next((e for e in ix if e[0] == sid), None)
        assert (e is not None) == (sid == SID), f'script {sid}: id gia usato'
        if e is None:
            e = [sid, 0, 0]
            ix.append(e)
        e[1], e[2] = len(out), len(blk)
        out += blk
    ix.sort(key=lambda e: e[0])
    return bytes(out), b''.join(struct.pack('<3I', *x) for x in ix)


if __name__ == '__main__':
    import evsc
    c, _ = build(0x3F6C00)
    print('\n'.join(armasm.listing(c, 0x3F6C00)))
    print('\n'.join(evsc.dis(script())))
