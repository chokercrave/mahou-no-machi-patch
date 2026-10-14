"""Tag [$599]: desinenza "o"/"a" secondo il sesso del personaggio giocante (QoL 10, dialoghi al femminile).
Nei testi italiani si scrive "§" al posto della desinenza ("brav§" -> "bravo"/"brava"); build_text lo sostituisce con
[$599] (o con "o" se GENDER_TAG e' spento) e lo misura come una "o".

Il dispatcher dei tag 500-599 (0x133924) prende il gestore da una tabella di 100 puntatori (0x597dac, voce nulla =
tag ignorato) e lo chiama con r0 = stato del testo; il gestore di [$500] (0x360b1c) copia il nome con
0x145ad4(stato, 2) + 0x1a0bec([stato+0xc], stringa, [stato+0x10]) e restituisce 1. Qui si fa lo stesso con "o" o "a".
Sesso: id del personaggio giocante = variabile 0x101282 (0x160ad0) = 0x1774 + slot (0..3); 0x185bb4(slot) = indirizzo del NOME
nel profilo (0 se slot >= 4; e' anche cio' che restituisce 0x2d3754 per il giocatore); sesso = byte nome+0x48
(W = 1 femmina, 0 maschio; verificato in RAM 12/10). Qualsiasi valore inatteso -> "o" (comportamento attuale).
Solo ldrb e puntatori controllati: niente letture disallineate o da NULL (3DS vera).
  python gender_tag.py       listato
"""
import os, struct, sys
sys.path.insert(0, os.path.dirname(__file__))
import armasm

TAG = 599
TABLE = 0x597DAC            # gestori [$500..599]
FLAGS = 0x597D48            # flag per tag (0 come [$500])
GETVAR, NAME, PROFILE, COPY = 0x160AD0, 0x2D3754, 0x185BB4, 0x1A0BEC

SRC = '''
    push {r4, r5, r6, r7, lr}
    mov r4, r0
    mov r6, #0
    ldr r0, [r4, #0x34]
    cmp r0, #0
    beq out
    ldr r0, =#0x101282
    bl getvar
    ldr r2, =0xffff
    and r1, r0, r2
    cmp r1, r2
    moveq r1, #0
    ldr r0, [r4, #0x34]
    ldrh r2, [r4, #0x14]
    bl name
    movs r5, r0
    beq out
    mov r7, #0
loop:
    mov r0, r7
    bl profile
    cmp r0, #0
    beq next
    cmp r0, r5
    beq found
next:
    add r7, r7, #1
    cmp r7, #4
    blt loop
    b out
found:
    ldrb r6, [r5, #0x48]
out:
    cmp r6, #1
    ldreq r1, =str_a
    ldrne r1, =str_o
    ldr r0, [r4, #0xc]
    ldr r2, [r4, #0x10]
    bl copy
    mov r0, #1
    pop {r4, r5, r6, r7, pc}
    .pool
str_o:
    .bytes MASC,0,0,0
str_a:
    .bytes FEMM,0,0,0
'''
# [$598] (QoL 7, relazioni di qualsiasi sesso): stesso gestore, desinenza PLURALE "i"/"e" ("fidanzat¤", "amic¤" -> h
# aggiunta nel testo dove serve); nei testi italiani si scrive "¤".
TAGS = {599: ('o', 'a'), 598: ('i', 'e')}


def build(base, tag=TAG):
    m, f = TAGS[tag]
    src = SRC.replace('MASC', hex(ord(m))).replace('FEMM', hex(ord(f)))
    return armasm.asm(src, base, {'getvar': GETVAR, 'name': NAME, 'profile': PROFILE, 'copy': COPY})


def install(d, base, BASE=0x100000, tag=TAG):
    """scrive il codice a base e il puntatore nella tabella; restituisce la fine del codice"""
    code, _ = build(base, tag)
    d[base - BASE:base - BASE + len(code)] = code
    slot = TABLE + (tag - 500) * 4
    assert struct.unpack_from('<I', d, slot - BASE)[0] == 0, f'[${tag}] gia\' usato'
    struct.pack_into('<I', d, slot - BASE, base)
    assert d[FLAGS + tag - 500 - BASE] == 0
    return base + len(code)


if __name__ == '__main__':
    c, _ = build(0x3F6758)
    print('\n'.join(armasm.listing(c, 0x3F6758)))
