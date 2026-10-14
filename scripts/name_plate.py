"""Targhetta del nome DINAMICA (mes_win_00: nomi NPC, fiori sulla mappa, elementi degli incantesimi).
Il gioco scrive il nome con 0x125150(holder=obj+0x2f0, nome UTF-16) in due punti (0x33e1c8, 0x33e2e4).
Li si devia su una routine nel riempimento in fondo a .text (0x54ac88-0x54b000, eseguibile, a zero) che:
  1. chiama la funzione originale;
  2. misura il nome: somma degli avanzamenti del font DF_kyougeki (tabella 0x00-0xFF, 13 per il resto)
     + 3 px tra una lettera e l'altra (charSpace del pannello Txt_mes_name);
  3. P = larghezza + 18 (margini originali: 110 px di testo in 128), centro M = P - 64 (min 8, pari);
  4. tra i fratelli del pannello di testo trova Pic_mes_name_01/_02 (nome a +0xB8) e scrive
     posizione x (+0x28) e larghezza (+0x48); il bordo sinistro resta a -162 come in originale.
Struttura di nw::lyt::Pane ricavata dal costruttore 0x42fbec: +4 nodo della lista dei fratelli,
+0x14 lista dei figli, +0x28 traslazione (x,y,z), +0x34 rotazione, +0x40 scala, +0x48 dimensioni (w,h),
+0xB8 nome (16 caratteri + 0).
  python name_plate.py         listato disassemblato (verifica)
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import armasm, bcfnt

ROOT = os.path.join(os.path.dirname(__file__), '..')
CAVE = 0x54ac90                     # dopo la fine di .text (0x54ac88), allineato
CAVE_END = 0x54b000
CALL_SITES = [0x33e1c8, 0x33e2e4]   # bl 0x125150 con r0 = obj+0x2f0, r1 = obj+0x14c (nome)
SET_STRING = 0x125150
CHAR_SPACE = 3
MARGIN = 18
MIN_MID = 8
LEFT = -162                         # bordo sinistro della targhetta (originale)
CAP = 32                            # larghezza dei due capi
TABLE = 0x587E00                    # tabella delle larghezze (256 byte) in .rodata libero (build_code la scrive)


def width_table():
    f = bcfnt.Bcfnt(open(os.path.join(ROOT, 'work', 'font', 'DF_kyougeki.bcfnt'), 'rb').read())
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
    mov r7, #0
    mov r8, #0
    ldr r9, =0x{TABLE:x}
loop:
    ldrh r0, [r5], #2
    cmp r0, #0
    beq measured
    cmp r0, #0x20
    blo loop
    cmp r0, #0x100
    movhs r1, #13
    ldrblo r1, [r9, r0]
    add r7, r7, r1
    add r8, r8, #1
    b loop
measured:
    subs r8, r8, #1
    addgt r7, r7, r8, lsl #1
    addgt r7, r7, r8
    add r7, r7, #{MARGIN}
    subs r7, r7, #{2 * CAP}
    cmp r7, #{MIN_MID}
    movlt r7, #{MIN_MID}
    add r7, r7, #1
    bic r7, r7, #1
    add r8, r6, #4
    ldr r9, [r8]
sib:
    cmp r9, r8
    beq settext
    sub r10, r9, #4
    ldr r0, [r10, #0xb8]
    ldr r1, =#0x5f636950
    cmp r0, r1
    bne next
    ldr r0, [r10, #0xc0]
    ldr r1, =#0x656d616e
    cmp r0, r1
    bne next
    ldr r0, [r10, #0xc4]
    ldr r1, =#0x0031305f
    cmp r0, r1
    beq mid
    ldr r1, =#0x0032305f
    cmp r0, r1
    beq right
    b next
mid:
    mov r0, r7, lsr #1
    sub r0, r0, #{-(LEFT + CAP)}
    vmov s0, r0
    vcvt.f32.s32 s0, s0
    vstr s0, [r10, #0x28]
    vmov s0, r7
    vcvt.f32.s32 s0, s0
    vstr s0, [r10, #0x48]
    b next
right:
    sub r0, r7, #{-(LEFT + CAP + CAP // 2)}
    vmov s0, r0
    vcvt.f32.s32 s0, s0
    vstr s0, [r10, #0x28]
next:
    ldr r9, [r9]
    b sib
settext:
    mov r0, r7, lsr #1
    sub r0, r0, #{-(LEFT + CAP)}
    vmov s0, r0
    vcvt.f32.s32 s0, s0
    vstr s0, [r6, #0x28]
    add r0, r7, #{2 * CAP}
    vmov s0, r0
    vcvt.f32.s32 s0, s0
    vstr s0, [r6, #0x48]
done:
    mov r0, r11
    pop {{r4-r11, pc}}
    .pool
'''


def build():
    code, labels = armasm.asm(SRC, CAVE, {'setstring': SET_STRING})
    assert CAVE + len(code) <= CAVE_END, f'routine troppo lunga: {len(code)} byte'
    return code, labels


def call_patch(site):
    """bl CAVE al posto di bl 0x125150"""
    d = (CAVE - site - 8) >> 2
    return 0xEB000000 | (d & 0xFFFFFF)


if __name__ == '__main__':
    code, labels = build()
    print('\n'.join(armasm.listing(code, CAVE)))
    print(f'routine {len(code)} byte (spazio {CAVE_END - CAVE}); tabella a {TABLE:#x}')
    for s in CALL_SITES:
        print(hex(s), armasm.listing(call_patch(s).to_bytes(4, 'little'), s))
