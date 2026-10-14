"""Controllo "da 3DS vera" sul log di Azahar dopo una sessione di test.
Azahar NON si ferma sugli accessi a memoria non mappata (es. puntatore NULL + offset): restituisce 0 e scrive
  HW.Memory <Error> ... unmapped Read32 @ 0x00000520 at PC 0x001FFD0C
mentre la 3DS vera va in data abort (crash Luma, DFSR 5/7). Ogni riga qui e' quindi un probabile crash su hardware.
Il log viene riscritto a ogni avvio di Azahar (il precedente diventa azahar_log.old.txt): controllare dopo ogni sessione.
  python emu_log_check.py [log ...]      (default: log attuale e .old)
Uscita 1 se trova accessi non mappati. Per capire il chiamante: python armfind.py dis <PC - 0x40> 24
"""
import os, re, sys
from collections import Counter

import paths
LOG = os.path.join(paths.AZAHAR_USER, 'log')
RX = re.compile(r'unmapped (Read|Write)(\d+) @ 0x([0-9A-Fa-f]+)(?: at PC 0x([0-9A-Fa-f]+))?')


def main(paths):
    bad = 0
    for p in paths:
        if not os.path.exists(p):
            continue
        hits = Counter()
        for line in open(p, encoding='utf-8', errors='replace'):
            m = RX.search(line)
            if m:
                hits[(m.group(1) + m.group(2), int(m.group(3), 16), int(m.group(4) or '0', 16))] += 1
        print(f'{os.path.basename(p)}: {sum(hits.values())} accessi non mappati')
        for (kind, addr, pc), n in sorted(hits.items(), key=lambda t: t[0][2]):
            tag = ' (NULL + offset)' if addr < 0x10000 else ''
            print(f'  {kind:8} @ {addr:#010x} da PC {pc:#010x}  x{n}{tag}')
        bad += len(hits)
    return 1 if bad else 0


if __name__ == '__main__':
    args = sys.argv[1:] or [os.path.join(LOG, 'azahar_log.txt'), os.path.join(LOG, 'azahar_log.old.txt')]
    sys.exit(main(args))
