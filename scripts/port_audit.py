"""Controllo del porting 1.0 -> 1.1 (build unica): ogni parola cambiata dalle patch, confrontata fra la 1.0 patchata (rifatta
qui con code_patches) e il code.bin 1.1 della mod.
  python port_audit.py
Segnala:
  RAW-PTR   copiata tale e quale ma il valore sembra un indirizzo che nella 1.1 si sposta (puntatore non rilocato?)
  ASCII     rilocata ma il valore sembra testo (costante scambiata per puntatore: usare 'ldr rX, =#valore')
  B-TGT     salto la cui destinazione 1.1 non corrisponde alla destinazione 1.0 mappata
  PTR-DATA  puntatore rilocato ma i 16 byte puntati differiscono fra 1.0 patchata e 1.1 (escluse le parole rilocate)
Uscita 1 se c'e' qualcosa da guardare."""
import os, struct, sys
sys.path.insert(0, os.path.dirname(__file__))
import armasm, build_code, port11

B = 0x100000
CAVES = [(build_code.NGC_CAVE, build_code.NGC_CAVE_END), (build_code.GAME_NG_CAVE, build_code.GAME_NG_CAVE_END),
         (0x54AC90, 0x54B000)]                   # name_plate.CAVE..CAVE_END
import paths
MOD = os.path.join(paths.MOD, 'exefs', 'code.bin')


def main():
    o10 = open(build_code.CODE, 'rb').read()
    o11 = open(build_code.CODE11, 'rb').read()
    d11 = open(MOD, 'rb').read()
    e10 = bytearray(o10)
    armasm.RELOCS.clear(); armasm.CONSTS.clear()
    build_code.code_patches(e10)
    u = lambda d, a: struct.unpack_from('<I', d, a - B)[0] if 0 <= a - B <= len(d) - 4 else None
    asc = lambda v: all(32 <= c < 127 or c == 0 for c in v.to_bytes(4, 'little')) and \
        sum(32 <= c < 127 for c in v.to_bytes(4, 'little')) >= 2
    rel_b = {a for a, k, v in armasm.RELOCS if k == 'b'}
    rel_ptr = {a for a, k, v in armasm.RELOCS if k == 'ptr'}
    free10 = [x for x in range(build_code.FREE_START & ~3, port11.TABLES10, 4) if u(o10, x) != u(e10, x)]
    if free10:
        issues_free = f'FREE10   {len(free10)} parole scritte nel .rodata libero 1.0 sotto le tabelle (da {free10[0]:#x}): collidono con FREE11'
    else:
        issues_free = None
    changed = [x for x in range(B, B + len(o10) // 4 * 4, 4) if u(o10, x) != u(e10, x)]
    moved = {}
    issues = [issues_free] if issues_free else []
    n = {'raw': 0, 'b': 0, 'ptr': 0}
    for x in changed:
        new, y = u(e10, x), port11.map_addr(x)
        w = u(d11, y)
        if w == new and not (x in rel_b):
            n['raw'] += 1
            utf16 = all(32 <= (new >> k) & 0xFFFF < 0x100 for k in (0, 16))     # 2 caratteri UTF-16 (testo nelle cave)
            if B <= new < port11.PROG_END10 and x not in armasm.CONSTS and not utf16:
                m = port11.map_addr(new)
                if m is not None and m != new:
                    issues.append(f'RAW-PTR  {x:#x}->{y:#x}: {new:#010x} (nella 1.1 sarebbe {m:#x})')
            continue
        if port11.is_branch(new) and port11.is_branch(w):
            n['b'] += 1
            t10, t11 = port11.branch_target(x, new), port11.branch_target(y, w)
            if port11.map_addr(t10) != t11:
                issues.append(f'B-TGT    {x:#x}->{y:#x}: {t10:#x} -> {t11:#x} (atteso {port11.map_addr(t10)})')
            continue
        n['ptr'] += 1
        moved[x] = (new, w)
        in_cave = any(a <= new < b for a, b in CAVES)
        if asc(new) and x not in rel_ptr and not in_cave:   # rilocazioni esplicite e puntatori alle cave: voluti
            issues.append(f'ASCII    {x:#x}->{y:#x}: {new:#010x} {new.to_bytes(4, "little")!r} rilocato in {w:#010x}')
    for x, (new, w) in moved.items():
        if not (port11.RODATA10 <= new < port11.PROG_END10) or new >= 0x5A0000:
            continue                                     # testo: gia' verificato da port11 (contenuto normalizzato)
        a = [u(e10, new + k) for k in range(0, 16, 4)]
        b = [u(d11, w + k) for k in range(0, 16, 4)]
        if None in a or None in b:
            continue
        diff = [k for k in range(4) if a[k] != b[k] and not (new + 4 * k in moved or (a[k] and port11.map_addr(a[k]) == b[k]))]
        if diff:
            issues.append(f'PTR-DATA {x:#x}: {new:#x} -> {w:#x}: ' + ' '.join(f'{a[k]:#x}/{b[k]:#x}' for k in diff))
    print(f'parole cambiate {len(changed)}: {n}; costanti =# {len(armasm.CONSTS)}')
    for i in issues:
        print(' ', i)
    print('problemi:', len(issues))
    return 1 if issues else 0


if __name__ == '__main__':
    sys.exit(main())
