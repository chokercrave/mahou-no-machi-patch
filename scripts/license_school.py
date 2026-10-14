"""Patente da mago: riga della scuola. Il gioco (0x3162a4) fa strcpy(buf, citta') + strcat(buf, "まほうがっこう"), quindi in
italiano veniva "Nome:Scuola" incollato. Si inverte l'ordine: strcpy(buf, prefisso) + strcat(buf, citta') e il prefisso
e' DINAMICO in base alla lunghezza del nome:
  citta' fino a 9 lettere  -> "Scuola di magia di <citta'>"
  citta' piu' lunga        -> "Scuola di magia <citta'>"   (il pannello Txt_school e' largo 176 px)
Nel riempimento di .text ci sono solo 112 byte per tutto: i 5 istruzioni originali 0x3162b4..0x3162c4 diventano
  mov r6,r1 / bl measure / add r0,r4,#0x34 / mov r1,r6 / bl strcat
e 'measure' (nel riempimento) misura la lunghezza, sceglie il prefisso (stringhe a distanza fissa) e fa strcpy.
  python license_school.py     listato
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import armasm

SITE = 0x3162B4                         # 5 istruzioni (fino a 0x3162c4 compreso)
STRCPY, STRCAT = 0x1315B4, 0x1D6F20
EXPECT = [0xE2840034, 0xEB000000 | 0, None, None, None]    # solo il primo e' controllato (add r0,r4,#0x34)
LONG, SHORT = 'Scuola di magia di ', 'Scuola di magia '
STRIDE = 40                            # byte tra le due stringhe (LONG = 20 caratteri con terminatore)
THRESH = 22                            # byte (2*lunghezza + 2): nome >= 10 lettere -> prefisso corto
N_INSN = 9


def _b(s, pad):
    return (s + chr(0)).encode('utf-16-le').ljust(pad, b'\0')


def build(base):
    """-> (codice+dati, indirizzo di measure)"""
    str_off = N_INSN * 4
    imm = str_off - 4 * 4 - 8              # add r1, pc, #imm e' la 5a istruzione (indice 4)
    src = f'''
l:
    ldrh r2, [r1], #2
    cmp r2, #0
    bne l
    sub r0, r1, r6
    add r1, pc, #{imm}
    cmp r0, #{THRESH}
    addhs r1, r1, #{STRIDE}
    add r0, r4, #0x34
    b strcpy
'''
    code, lab = armasm.asm(src, base, {'strcpy': STRCPY})
    assert len(code) == str_off, len(code)
    return code + _b(LONG, STRIDE) + _b(SHORT, 0), base


def patch_words(measure):
    """le 5 istruzioni che sostituiscono 0x3162b4..0x3162c4"""
    def bl(site, target):
        return 0xEB000000 | (((target - site - 8) >> 2) & 0xFFFFFF)
    return [0xE1A06001,                                     # mov r6, r1
            bl(SITE + 4, measure),                          # bl measure
            0xE2840034,                                     # add r0, r4, #0x34
            0xE1A01006,                                     # mov r1, r6
            bl(SITE + 16, STRCAT)]                          # bl strcat


if __name__ == '__main__':
    c, m = build(0x54AF90)
    print(len(c), 'byte, fine', hex(0x54AF90 + len(c)))
    print('\n'.join(armasm.listing(c[:N_INSN * 4], 0x54AF90)))
