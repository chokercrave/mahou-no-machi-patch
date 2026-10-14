"""Fumetto della tastiera magica DINAMICO (layout common.arc mes_win_09 / mes_win_15: "Magia", suggerimenti).
La classe della tastiera magica (0x207xxx-0x20axxx) crea due menu da questi layout (tabella 0x5967bc, slot 9) e scrive il
testo con SET_STRING(holder = obj+0x560+0x18*indice, testo) a 0x20abac. Il fumetto e' fisso: centro Pic_win_00 da 80/92 px
e due capi da 16 (Pic_win_01 a sinistra, Pic_win_02 a destra specchiato) -> "Magia" in un fumetto da ~110 px, testi lunghi fuori.
Tutti i pannelli hanno origine al CENTRO (4) e il testo e' centrato: dopo SET_STRING si misura il testo (larghezze LC.bcfnt,
stessa tabella di pop_plate) e si riscrive
  centro  M = max(testo + 2*PAD - 2*CAP, MINM), pari;  Pic_win_00: x = 0, larghezza M, scala 1
  capi    Pic_win_01 x = -(M/2 + CAP/2),  Pic_win_02 x = +(M/2 + CAP/2)
  testo   Txt_win larghezza = M + 2*CAP - 2*PAD + 8 (non va mai a capo)
Su ogni pannello toccato si azzerano i bit 4-5 di +0xb7 (matrice da ricalcolare), come in pop_plate.
Il codice sta nello spazio liberato dal filtro parolacce spento (blocco nn::ngc, vedi build_code.NGC_CAVE).
  python bubble_plate.py       listato
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import armasm

SET_STRING = 0x125150
SITES = [(0x20ABAC, 'bl'), (0x20AC04, 'b'),   # i due metodi "imposta testo" del fumetto attivo (holder obj+0x560+0x18*[obj+0x5a8])
         (0x2C9A2C, 'bl')]                    # fumetto sopra l'icona toccata (GDB 10/10): ogni frame, holder obj+0x440+0x18*(len>=9)
TABLE = 0x587F00            # larghezze LC.bcfnt (scritta da build_code per pop_plate)
CAP = 16
PAD = 10
MINM = 8

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
    ldr r0, [r6, #0xbc]
    ldr r1, =0x006e6977
    cmp r0, r1
    bne done
    mov r7, #0
    ldr r9, =0x{TABLE:x}
loop:
    ldrh r0, [r5], #2
    cmp r0, #0
    beq measured
    cmp r0, #0x20
    blo loop
    cmp r0, #0x100
    movhs r1, #11
    ldrblo r1, [r9, r0]
    add r7, r7, r1
    b loop
measured:
    add r8, r7, #{2 * PAD}
    subs r8, r8, #{2 * CAP}
    cmp r8, #{MINM}
    movlt r8, #{MINM}
    add r8, r8, #1
    bic r8, r8, #1
    add r0, r8, #{2 * CAP - 2 * PAD + 8}
    vmov s0, r0
    vcvt.f32.s32 s0, s0
    vstr s0, [r6, #0x48]
    ldrb r0, [r6, #0xb7]
    and r0, r0, #0xcf
    strb r0, [r6, #0xb7]
    mov r7, r8, lsr #1
    add r7, r7, #{CAP // 2}
    add r9, r6, #4
    ldr r10, [r9]
sib:
    cmp r10, r9
    beq done
    sub r3, r10, #4
    ldr r0, [r3, #0xb8]
    ldr r1, =0x5f636950
    cmp r0, r1
    bne next
    ldr r0, [r3, #0xbc]
    ldr r1, =0x5f6e6977
    cmp r0, r1
    bne next
    ldrb r0, [r3, #0xc1]
    cmp r0, #0x30
    beq mid
    cmp r0, #0x31
    beq left
    cmp r0, #0x32
    beq right
    b next
mid:
    mov r0, #0
    vmov s0, r0
    vstr s0, [r3, #0x28]
    vmov s0, r8
    vcvt.f32.s32 s0, s0
    vstr s0, [r3, #0x48]
    mov r0, #0x3f800000
    vmov s0, r0
    vstr s0, [r3, #0x40]
    b dirty
left:
    rsb r0, r7, #0
    vmov s0, r0
    vcvt.f32.s32 s0, s0
    vstr s0, [r3, #0x28]
    b dirty
right:
    vmov s0, r7
    vcvt.f32.s32 s0, s0
    vstr s0, [r3, #0x28]
dirty:
    ldrb r0, [r3, #0xb7]
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
    return armasm.asm(SRC, base, {'setstring': SET_STRING})


def branch(site, target, link):
    d = (target - site - 8) >> 2
    return (0xEB000000 if link else 0xEA000000) | (d & 0xFFFFFF)


if __name__ == '__main__':
    c, lab = build(0x3F644C)
    print('\n'.join(armasm.listing(c, 0x3F644C)))
    print(f'{len(c)} byte')
