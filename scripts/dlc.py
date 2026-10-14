"""DLC sempre attivi (14/10: niente menu Regali).

Contenuti scaricabili (oggetti dlitem_XXXX, negozi dlshop_NN) del server Konami, chiuso il 30/09/2020: pacchetto di
makemonge30 (GBAtemp, 10/01/2026, date di scadenza a +0x60 portate al 2100-12-31) in romfs/dlc/ della mod.
Il gioco li legge SOLO da extdata:/download/ con il bit di possesso in tc4_ext_sp.sav: qui il gioco stesso li
"scarica" dalla romfs come faceva col regalo pre_download (macchina 0x2837d0, stati 0x19-0x1c, docs/RE_atlas.md §9):
  lettore romfs FUN_001252c8/00125190/0012485c/00125270/0012533c, FUN_0020ebac(gestore, tipo, id, buf, dim, 0) mette in
  coda la scrittura (asincrona: gestore+4 == 9 o *(gestore+0x63748) != 0 = occupato), FUN_0010e880(possesso, tipo, id, 1)
  accende il bit (e aggiorna i contatori +0x14c), FUN_0020ee20(gestore, 1) salva tc4_ext_sp.sav.
  Negozi: come il distruttore dell'installatore FUN_00107758 -> FUN_0010d2f4(FUN_0010d228(), id) li registra nel centro
  commerciale (idempotente; al massimo 5 negozi DLC aperti insieme, gli altri in lista d'attesa e ruotano).
Dove: macchina di avvio 0x396ba0 (stato = obj+0x2d), dopo "Continua". Lo stato 0x36 chiude il riquadro "Controllo dei
dati ricevuti" (gestore libero, bitset gia' in RAM, centro popolato: GDB 14/10). Ganci:
  0x39817c (nop d'ingresso dello stato 0x36) -> dlc_36: se manca qualcosa -> stato 0x3a; altrimenti registra i negozi
           posseduti (se la partita non era stata salvata dopo l'installazione) e prosegue con l'originale (0x398180).
  0x396bac (stato >= 0x3a: "b 0x396cc0" = resta) -> dlc_ext:
    0x3a: un file per volta (a gestore libero): libera il buffer della scrittura finita (il worker, caso 7, non lo libera
          mai: worker+0x10134 azzerato all'ingresso), legge romfs dlc/..., accoda la scrittura, bit, negozio. Finiti (o
          file illeggibile) -> salva ext_sp -> 0x3b.
    0x3b: a gestore libero esegue il corpo originale dello stato 0x36 (che cambia stato da se').
Le partite con DLC veri (bit gia' accesi) non vengono toccate: si installa solo cio' che manca.
"""
import os, shutil, struct, sys
sys.path.insert(0, os.path.dirname(__file__))
import armasm

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, 'work', 'dlc_gbatemp', 'x', 'JKSV', 'ExtData', 'Tongariboshi To Maho no Machi',
                   'DLC items and shops', 'download')
FOLDER = 'dlc'
HOOK36, OLD36 = 0x39817C, 0xE320F000            # nop
HOOKX, OLDX = 0x396BAC, 0xEA000043              # b 0x396cc0
STAY, BODY36 = 0x396CC0, 0x398180
SYM = {'STAY': STAY, 'BODY36': BODY36, 'SPRINTF': 0x547044, 'RD_CTOR': 0x1252C8, 'RD_OPEN': 0x125190,
       'RD_READ': 0x12485C, 'RD_CLOSE': 0x125270, 'RD_DTOR': 0x12533C, 'ALLOC': 0x11717C, 'FREE': 0x13E88C,
       'WRITE': 0x20EBAC, 'SAVE': 0x20EE20, 'SETBIT': 0x10E880, 'TESTBIT': 0x132544, 'MALL': 0x10D228,
       'REG': 0x10D2F4}
MGR_PTR, OWN_OFF, BUSY_OFF = 0x5AFD3C, 0x619DC + 0x100, 0x63748
END = 0xFFFF
# Negozi ESCLUSI (solo contenuti completi): tutti i 24 dlshop del pacchetto usano come stanza
# l'oggetto 8707 (dlshop bin +0x710), mai recuperato -> pareti/pavimento "?" e il caricatore del modello FUN_003be75c
# riceve NULL da FUN_0011be60 e lo passa a FUN_00477cb8 (letture NULL in Azahar = crash su 3DS). Riattivare solo con
# una stanza sostitutiva provata.
SHOPS = False
# Disattivati dalla 1.9: i file DLC sono di Konami e l'xdelta li conterrebbe per intero (non sono nella ROM originale).
# Le partite che li hanno gia' installati li conservano (stanno in extdata:/download/, non nella romfs).
ENABLED = False


def available():
    """il pacchetto DLC non fa parte della patch (file Konami): se manca, la build salta installatore e copia"""
    return ENABLED and os.path.isdir(PKG)


def contents():
    """(tipo, id) dei file del pacchetto: negozi (1) prima degli oggetti (2). AEON (dlmall_00, tipo 0) escluso."""
    out = []
    for f in sorted(os.listdir(PKG)):
        n = int(f.split('_')[1].split('.')[0])
        if f.startswith('dlshop_') and SHOPS:
            out.append((1, n))
        elif f.startswith('dlitem_'):
            out.append((2, n))
    return sorted(out)


def fname(t, n):
    return ('dlmall_%02d', 'dlshop_%02d', 'dlitem_%04d')[t] % n + '.tarc'


SRC = '''
dlc_36:
    push {r4, r5, r6, lr}
    ldr r0, =MGR_PTR
    ldr r0, [r0]
    ldr r5, [r0, #8]
    cmp r5, #0
    beq d36_reg
    bl find
    cmp r0, #0
    beq d36_reg
    add r5, r5, #0x10000
    mov r0, #0
    str r0, [r5, #0x134]
    mov r0, #0x3a
    strb r0, [r4, #0x2d]
    pop {r4, r5, r6, lr}
    b STAY
d36_reg:
    bl regshops
    pop {r4, r5, r6, lr}
    b BODY36
dlc_ext:
    ldrb r0, [r4, #0x2d]
    cmp r0, #0x3a
    beq d3a
    cmp r0, #0x3b
    bne STAY
    bl busy
    cmp r0, #0
    bne STAY
    b BODY36
d3a:
    push {r4, r5, r6, r7, r8, r9, r10, r11, lr}
    sub sp, sp, #0x80
    bl busy
    cmp r0, #0
    bne a_stay
    ldr r6, =MGR_PTR
    ldr r6, [r6]
    ldr r6, [r6, #8]
    add r6, r6, #0x10000
    ldr r0, [r6, #0x134]
    cmp r0, #0
    beq a_next
    bl FREE
    mov r0, #0
    str r0, [r6, #0x134]
a_next:
    bl find
    cmp r0, #0
    beq a_save
    ldrh r8, [r0]
    mov r9, r8, lsr #14
    bic r10, r8, #0xc000
    ldr r1, =fmt_item
    cmp r9, #1
    ldreq r1, =fmt_shop
    cmp r9, #0
    ldreq r1, =fmt_mall
    add r0, sp, #0x40
    mov r2, r10
    bl SPRINTF
    mov r0, sp
    bl RD_CTOR
    mov r0, sp
    add r1, sp, #0x40
    bl RD_OPEN
    cmp r0, #0
    beq a_fail_dtor
    ldr r11, [sp, #0x28]
    mov r0, r11
    bl ALLOC
    cmp r0, #0
    beq a_fail_close
    mov r8, r0
    mov r0, sp
    mov r1, r8
    mov r2, r11
    bl RD_READ
    mov r6, r0
    mov r0, sp
    bl RD_CLOSE
    mov r0, sp
    bl RD_DTOR
    cmp r6, #0
    blt a_fail_free
    mov r0, #0
    str r11, [sp]
    str r0, [sp, #4]
    ldr r0, =MGR_PTR
    ldr r0, [r0]
    mov r1, r9
    mov r2, r10
    mov r3, r8
    bl WRITE
    cmp r0, #0
    beq a_retry
    ldr r0, =MGR_PTR
    ldr r0, [r0]
    ldr r1, =OWN_OFF
    add r0, r0, r1
    mov r1, r9
    mov r2, r10
    mov r3, #1
    bl SETBIT
    cmp r9, #1
    bne a_stay
    bl MALL
    mov r1, r10
    bl REG
    b a_stay
a_retry:
    mov r0, r8
    bl FREE
    b a_stay
a_fail_free:
    mov r0, r8
    bl FREE
    b a_save
a_fail_close:
    mov r0, sp
    bl RD_CLOSE
a_fail_dtor:
    mov r0, sp
    bl RD_DTOR
a_save:
    ldr r0, =MGR_PTR
    ldr r0, [r0]
    mov r1, #1
    bl SAVE
    mov r0, #0x3b
    strb r0, [r4, #0x2d]
a_stay:
    add sp, sp, #0x80
    pop {r4, r5, r6, r7, r8, r9, r10, r11, lr}
    b STAY
busy:
    ldr r0, =MGR_PTR
    ldr r0, [r0]
    ldrb r1, [r0, #4]
    cmp r1, #9
    beq busy_yes
    ldr r1, =BUSY_OFF
    ldr r0, [r0, r1]
    .word 0xe12fff1e
busy_yes:
    mov r0, #1
    .word 0xe12fff1e
find:
    push {r4, r5, r6, lr}
    ldr r4, =table
f_loop:
    ldrh r5, [r4]
    ldr r0, =END
    cmp r5, r0
    beq f_none
    ldr r0, =MGR_PTR
    ldr r0, [r0]
    ldr r1, =OWN_OFF
    add r0, r0, r1
    mov r1, r5, lsr #14
    bic r2, r5, #0xc000
    bl TESTBIT
    cmp r0, #0
    beq f_found
    add r4, r4, #2
    b f_loop
f_none:
    mov r0, #0
    pop {r4, r5, r6, pc}
f_found:
    mov r0, r4
    pop {r4, r5, r6, pc}
regshops:
    push {r4, r5, r6, lr}
    ldr r4, =table
r_loop:
    ldrh r5, [r4]
    ldr r0, =END
    cmp r5, r0
    beq r_end
    add r4, r4, #2
    mov r0, r5, lsr #14
    cmp r0, #1
    bne r_loop
    ldr r0, =MGR_PTR
    ldr r0, [r0]
    ldr r1, =OWN_OFF
    add r0, r0, r1
    mov r1, #1
    bic r2, r5, #0xc000
    bl TESTBIT
    cmp r0, #0
    beq r_loop
    bl MALL
    bic r1, r5, #0xc000
    bl REG
    b r_loop
r_end:
    pop {r4, r5, r6, pc}
    .pool
'''


def _bytes(b):
    return '    .bytes ' + ','.join(str(x) for x in b) + '\n'


def build(base, items=None):
    items = contents() if items is None else items
    src = SRC
    for k, v in (('MGR_PTR', MGR_PTR), ('OWN_OFF', OWN_OFF), ('BUSY_OFF', BUSY_OFF), ('=END', END)):
        src = src.replace('=' + k.lstrip('='), '=' + str(v))
    data = ''
    for lab, fmt in (('fmt_mall', 'dlmall_%02d'), ('fmt_shop', 'dlshop_%02d'), ('fmt_item', 'dlitem_%04d')):
        data += f'{lab}:\n' + _bytes((f'{FOLDER}/{fmt}.tarc').encode() + b'\0') + '    .align\n'
    tab = b''.join(struct.pack('<H', (t << 14) | n) for t, n in items) + struct.pack('<H', END)
    data += 'table:\n' + _bytes(tab) + '    .align\n'
    return armasm.asm(src + data, base, SYM)


def branch(site, tgt):
    return 0xEA000000 | (((tgt - site - 8) >> 2) & 0xFFFFFF)


def install(d, base, BASE=0x100000):
    code, lab = build(base)
    d[base - BASE:base - BASE + len(code)] = code
    for site, old, tgt in ((HOOK36, OLD36, lab['dlc_36']), (HOOKX, OLDX, lab['dlc_ext'])):
        assert struct.unpack_from('<I', d, site - BASE)[0] == old, f'dlc: {site:#x} inatteso'
        struct.pack_into('<I', d, site - BASE, branch(site, tgt))
    return base + len(code)


def copy_files(mod_romfs):
    """file del pacchetto in romfs/dlc/ della mod (solo quelli in tabella)"""
    out = os.path.join(mod_romfs, FOLDER)
    if os.path.isdir(out):
        shutil.rmtree(out)
    if not available():
        return 0
    os.makedirs(out)
    for t, n in contents():
        shutil.copyfile(os.path.join(PKG, fname(t, n)), os.path.join(out, fname(t, n)))
    return len(contents())


if __name__ == '__main__':
    c, lab = build(0x3F6980)
    print(len(c), 'byte;', len(contents()), 'contenuti')
    print('\n'.join(armasm.listing(c, 0x3F6980)[:60]))
