"""Targhetta dei nomi (oggetti dell'inventario, suggerimenti della tastiera magica, ...) DINAMICA.
La classe pop_up (layout common.arc: pop_up, pop_up_00, pop_up_01, pop_up_02) stima la larghezza del testo con regole
da giapponese (ASCII a mezza larghezza, ecc.): in italiano il testo finiva a sinistra con ~28 px vuoti a destra, e le
parole corte avevano comunque una targhetta larga (minimo di layout ~134 px).
Come per i nomi (name_plate.py): dopo la scrittura del testo (SET_STRING sull'holder dell'oggetto, 4 punti: uno per
variante) si misura il testo con le larghezze reali di LC.bcfnt (font 1 dei pannelli) e si riscrive:
  larghezza targhetta P = max(testo + 2*MARGIN, MINP); bordo sinistro fermo a -16 (capo sinistro x=16, w=64)
  Pic_pop_up_02 (capo destro)  x = P - 24         (come fa il gioco: sposta solo il capo destro)
  Pic_pop_up_01 (centro)       origine a SINISTRA (misurato dagli screenshot): x = 44, larghezza x02 - 48, scala 1.0 (il gioco la usa per allungare il centro:
                               sommata alla larghezza riscritta lo riduceva a una fessura)
  Pic_pop_up_03 (coda, solo varianti _01/_02) x = P/2 - 16 (al centro della targhetta)
  Txt_name_00 (testo)          x = (P - testo) / 2 - 14  (inizio del testo = x - 1.7, centrato nella targhetta)
Il gioco (0x256198, prima di SET_STRING) con testo stimato < minimo di layout (134 px) NASCONDE Pic_pop_up_01
(0x13aae4(holder, 0): bit 0 del byte +0xb7 del pannello) perche' la targhetta minima non ne ha bisogno: stringendo i capi
restava un buco sui nomi corti (Amanita, In uso, Farina...). Qui il centro viene sempre reso visibile, e su ogni pannello
spostato si azzerano i bit 4-5 di +0xb7 (matrice da ricalcolare), come fanno 0x14d624/0x4620c8.
Fratelli di Txt_name_00 in Nul_sheet_00 = solo Pic_pop_up_0x: basta confrontare la terza parola del nome ("up_0")
(spazio: il riempimento di .text finisce a 0x54b000).
Il codice sta nel riempimento di .text (dopo name_plate e license_names), la tabella delle larghezze in fondo a .rodata.
  python pop_plate.py          listato
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import armasm, bcfnt

ROOT = os.path.join(os.path.dirname(__file__), '..')
SET_STRING = 0x125150
# (indirizzo, 'bl'|'b'): chiamata a SET_STRING dei quattro metodi "imposta testo" della classe (r0 = holder, r1 = testo)
SITES = [(0x2565F0, 'bl'), (0x2563E0, 'bl'), (0x256660, 'b'), (0x256580, 'b')]
TABLE = 0x587F00           # 256 byte (larghezze LC.bcfnt), in .rodata libero
# varianti con la coda pop_up_01/_02 (nuvolette degli NPC nel campo, "E con questo?"): testo alto 14 in DF_kyougeki da 13 px
# con 2 px tra le lettere -> si misura con la tabella di name_plate (DF_kyougeki) + DF_SPACE per lettera
TABLE_DF = 0x587E00
DF_SPACE = 2
MARGIN = 8
MINP = 72                  # larghezza minima: centro (x02-48) >= 0 e capi che si toccano. Prima 96: il "buco" fra i capi
                           # era il pezzo centrale NASCOSTO dal gioco (vedi sotto), non un limite della grafica


def width_table():
    f = bcfnt.Bcfnt(open(os.path.join(ROOT, 'work', 'font', 'LC.bcfnt'), 'rb').read())
    t = []
    for c in range(256):
        if c < 0x20:
            t.append(0)
            continue
        g = f.cmap.get(c, f.alter_idx)
        adv = f.widths[g][2][2] if g in f.widths else f.default_width[2]
        t.append(min(adv, 255))
    return t


SRC = f'''
    push {{r4-r11, lr}}
    mov r4, r0
    mov r5, r1
    bl setstring
    mov r11, r0
    ldr r6, [r4, #0x14]
    cmp r6, #0
    beq done
    ldr r0, [r6, #0xb8]
    ldr r1, =0x5f747854
    cmp r0, r1
    bne done
    mov r7, #0
    ldr r9, =0x{TABLE:x}
    mov r2, #0
    mov r3, #11
    ldr r0, [r6, #0x4c]
    ldr r1, =0x41600000
    cmp r0, r1
    ldreq r9, =0x{TABLE_DF:x}
    moveq r2, #{DF_SPACE}
    moveq r3, #13
loop:
    ldrh r0, [r5], #2
    cmp r0, #0
    beq measured
    cmp r0, #0x20
    blo loop
    cmp r0, #0x100
    movhs r1, r3
    ldrblo r1, [r9, r0]
    add r7, r7, r1
    add r7, r7, r2
    b loop
measured:
    cmp r7, r2
    subhi r7, r7, r2
    add r8, r7, #{2 * MARGIN}
    cmp r8, #{MINP}
    movlt r8, #{MINP}
    sub r0, r8, r7
    mov r0, r0, lsr #1
    sub r0, r0, #14
    vmov s0, r0
    vcvt.f32.s32 s0, s0
    vstr s0, [r6, #0x28]
    ldrb r0, [r6, #0xb7]
    and r0, r0, #0xcf
    strb r0, [r6, #0xb7]
    sub r7, r8, #24
    add r9, r6, #4
    ldr r10, [r9]
sib:
    cmp r10, r9
    beq done
    sub r3, r10, #4
    ldr r0, [r3, #0xc0]
    ldr r1, =0x305f7075
    cmp r0, r1
    bne next
    ldrb r0, [r3, #0xc4]
    cmp r0, #0x31
    beq mid
    cmp r0, #0x32
    beq right
    cmp r0, #0x33
    beq tail
    b next
mid:
    mov r0, #44
    vmov s0, r0
    vcvt.f32.s32 s0, s0
    vstr s0, [r3, #0x28]
    sub r0, r7, #48
    vmov s0, r0
    vcvt.f32.s32 s0, s0
    vstr s0, [r3, #0x48]
    mov r0, #0x3f800000
    vmov s0, r0
    vstr s0, [r3, #0x40]
    ldrb r0, [r3, #0xb7]
    orr r0, r0, #1
    b dirty
right:
    vmov s0, r7
    vcvt.f32.s32 s0, s0
    vstr s0, [r3, #0x28]
    ldrb r0, [r3, #0xb7]
    b dirty
tail:
    mov r0, r8, lsr #1
    sub r0, r0, #16
    vmov s0, r0
    vcvt.f32.s32 s0, s0
    vstr s0, [r3, #0x28]
    ldrb r0, [r3, #0xb7]
dirty:
    and r0, r0, #0xcf
    strb r0, [r3, #0xb7]
next:
    ldr r10, [r10]
    b sib
done:
    mov r0, r11
    pop {{r4-r11, pc}}
    .pool
'''


def build(base):
    code, labels = armasm.asm(SRC, base, {'setstring': SET_STRING})
    return code, labels


def branch(site, target, link):
    d = (target - site - 8) >> 2
    return (0xEB000000 if link else 0xEA000000) | (d & 0xFFFFFF)


if __name__ == '__main__':
    import name_plate, license_names
    nc, _ = name_plate.build()
    b1 = (name_plate.CAVE + len(nc) + 3) & ~3
    lc, _ = license_names.build(b1)
    b2 = (b1 + len(lc) + 3) & ~3
    c, lab = build(b2)
    print('\n'.join(armasm.listing(c, b2)))
    print(f'{len(c)} byte a {b2:#x}, fine {b2 + len(c):#x} (limite {name_plate.CAVE_END:#x})')
