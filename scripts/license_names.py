"""Patente da mago: nomi di bacchetta e cappello fino a 39 caratteri (nomi ufficiali DS interi).
Nell'oggetto della patente i due nomi stanno in campi da 16 caratteri senza posto per il terminatore
(+0x104 bacchetta, +0x124 cappello, subito dopo c'è un puntatore a +0x144): un nome da 16 si attaccava al
successivo. Misurato con GDB (stringhe in memoria: "Apprendista·····|Bacchetta stella|Capp. apprendist|...").
Soluzione: i due campi si spostano in una zona libera dopo la fine del bss (0x611f58..0x612000, mappata,
sempre a zero: verificato a runtime) e copia/ripiego/visualizzazione passano da piccoli stub nel
riempimento di .text (dopo la routine della targhetta, name_plate.py).
  python license_names.py     listato
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import armasm

BUF_W, BUF_H = 0x611F60, 0x611FB0          # 40 caratteri UTF-16 ciascuno (fino a 0x612000)
MAXCH = 39
FMT, STRCPY, SETTXT = 0x289334, 0x1315B4, 0x4679E4
# (indirizzo, istruzione originale attesa, etichetta dello stub, è un salto senza link)
SITES = [
    (0x3163C4, 'bl', FMT, 'fmt_w'),       # copia formattata del nome della bacchetta (max 16)
    (0x316438, 'bl', FMT, 'fmt_h'),       # idem cappello
    (0x3163F4, 'bl', STRCPY, 'cpy_w'),    # ripiego (testo di messaggio) bacchetta
    (0x316468, 'bl', STRCPY, 'cpy_h'),    # idem cappello
    (0x3164A8, 'bl', SETTXT, 'disp_w'),   # testo del pannello bacchetta
    (0x3164B8, 'b', SETTXT, 'disp_h'),    # testo del pannello cappello (salto finale)
    # altri aggiornamenti della patente (stessa sequenza titolo/bacchetta/cappello -> pannelli)
    (0x316524, 'bl', SETTXT, 'disp_w'), (0x316534, 'b', SETTXT, 'disp_h'),
    (0x316908, 'bl', SETTXT, 'disp_w'), (0x316914, 'bl', SETTXT, 'disp_h'),
    (0x316A38, 'bl', SETTXT, 'disp_w'), (0x316A44, 'bl', SETTXT, 'disp_h'),
    (0x316C04, 'bl', SETTXT, 'disp_w'), (0x316C10, 'bl', SETTXT, 'disp_h'),
    (0x316C48, 'bl', SETTXT, 'disp_w'), (0x316C54, 'bl', SETTXT, 'disp_h'),
]
SRC = f'''
fmt_w:
    ldr r2, =0x{BUF_W:x}
    mov r3, #{MAXCH}
    b fmt
fmt_h:
    ldr r2, =0x{BUF_H:x}
    mov r3, #{MAXCH}
    b fmt
cpy_w:
    ldr r0, =0x{BUF_W:x}
    b strcpy
cpy_h:
    ldr r0, =0x{BUF_H:x}
    b strcpy
disp_w:
    ldr r1, =0x{BUF_W:x}
    b settxt
disp_h:
    ldr r1, =0x{BUF_H:x}
    b settxt
    .pool
'''


def build(base):
    return armasm.asm(SRC, base, {'fmt': FMT, 'strcpy': STRCPY, 'settxt': SETTXT})


def branch(site, target, link):
    d = (target - site - 8) >> 2
    return (0xEB000000 if link else 0xEA000000) | (d & 0xFFFFFF)


if __name__ == '__main__':
    import name_plate
    code, _ = name_plate.build()
    base = (name_plate.CAVE + len(code) + 3) & ~3
    c, lab = build(base)
    print('\n'.join(armasm.listing(c, base)))
    print(f'{len(c)} byte a {base:#x}, fine {base + len(c):#x} (limite {name_plate.CAVE_END:#x})')
