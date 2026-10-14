"""Toglie i loghi iniziali CESA / Konami (schermo alto) da ui/menu_logo.tarc -> logo_upper.dmst.
Formato DMST: 'DMST', u32 inizio pool stringhe, u32 0, poi GRUPPI: [u16 0, u16 0, u16 offset nome pannello, u16 0]
seguito da N voci da 10 byte [01 02 'n' 00 idx16 's' 00 offset_anim16]. Gli offset sono relativi al pool stringhe.
Qui si cancellano i gruppi `drop` (per nome) e si sposta l'inizio del pool di conseguenza.
  python make_logo_skip.py [cesa|konami|both]    (default both; modifica la mod gia' costruita)"""
import os, struct, sys
sys.path.insert(0, os.path.dirname(__file__))
import tbaf

ROOT = os.path.join(os.path.dirname(__file__), '..')
import paths
MOD = os.path.join(paths.MOD, 'romfs', 'ui', 'menu_logo.tarc')


def strip(d, drop):
    base = struct.unpack_from('<I', d, 4)[0]
    pos, groups = 8, []
    while pos < base:
        nm_off = struct.unpack_from('<H', d, pos + 4)[0]
        # le voci seguono finche' non compare un altro gruppo (primi 4 byte nulli) o la fine
        e = pos + 8
        while e + 10 <= base and d[e] == 1 and d[e + 1] == 2:
            e += 10
        end = d.index(b'\0', base + nm_off)
        groups.append((d[base + nm_off:end].decode(), d[pos:e]))
        pos = e
    keep = [g for n, g in groups if not any(x in n for x in drop)]
    body = b''.join(keep)
    return d[:4] + struct.pack('<I', 8 + len(body)) + body + d[base:], [n for n, _ in groups]


def main():
    # all = nessun logo all'avvio: anti-pirateria e Konami (schermo alto)
    # + LovePlus Production (schermo basso, logo_under.dmst); il credito della patch e' sul titolo (make_images)
    # NON togliere i gruppi dal DMST (strip): il codice (0x1ffc48..0x1ffd30) chiede le parti 0/1 dei menu 0x8f/0x90
    # e senza gruppo riceve NULL -> 0x21d590(NULL) legge 0x520: su Azahar passa (legge 0), sulla 3DS vera crash
    # (dump 2026-10-10, DFSR 5, pc 0x13aae4). Si lasciano i DMST originali e si azzerano le texture dei loghi:
    # RGB565 a zero = nero, su sfondo gia' nero (blacken) -> stessa attesa nera, parti tutte presenti.
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    tex = {'cesa': ['logo_cesa'], 'konami': ['logo_konami'], 'both': ['logo_cesa', 'logo_konami'],
           'all': ['logo_cesa', 'logo_konami', 'logo_lp']}[which]
    ents = {e['name']: e for e in tbaf.parse(open(MOD, 'rb').read())}
    # DMST sempre quelli originali (la mod poteva contenere quelli tagliati dalle versioni <= 0.9.3)
    orig = os.path.join(ROOT, 'work', '3ds', 'romfs_x', 'ui', 'menu_logo.tarc_x')
    repl = {fn: open(os.path.join(orig, fn), 'rb').read() for fn in ('logo_upper.dmst', 'logo_under.dmst')}
    arc = ents['logo.arc']
    raw = tbaf.decompress(arc['data']) if arc['comp'] else arc['data']
    repl['logo.arc'] = blacken(raw, tex)
    tmp = MOD + '.tmp'
    tbaf.rebuild(MOD, repl, tmp)
    os.replace(tmp, MOD)


BLACK = b'\x00\x00\x00\xff'


def blacken(arc, tex=()):
    """sfondi dei layout dei loghi (pannelli Pic_white: colori dei vertici + colori del materiale) da bianco a nero:
    il codice mostra comunque i layout per il loro tempo, cosi' l'attesa resta tutta nera.
    Le texture in `tex` (timg/<nome>.bclim) vengono azzerate (dati immagine; intestazione CLIM finale intatta)."""
    import darc, bclyt
    fs = darc.read_files(arc)
    out = {}
    for t in tex:
        v = fs[f'timg/{t}.bclim']
        out[f'timg/{t}.bclim'] = bytes(len(v) - 0x28) + v[-0x28:]
        print('logo vuoto:', t)
    for k, v in fs.items():
        if not k.endswith('.bclyt'):
            continue
        v = bytearray(v)
        n = 0
        for m, o, sz in bclyt.sections(bytes(v)):
            if m == b'pic1' and v[o + 0xC:o + 0x1C].split(b'\0')[0] == b'Pic_white':
                for i in range(4):                          # 4 colori dei vertici (+0x4C)
                    v[o + 0x4C + 4 * i:o + 0x50 + 4 * i] = BLACK
                n += 1
            elif m == b'mat1':
                cnt = struct.unpack_from('<I', v, o + 8)[0]
                for i in range(cnt):
                    mo = o + struct.unpack_from('<I', v, o + 0xC + 4 * i)[0]
                    if v[mo:mo + 20].split(b'\0')[0] == b'Pic_white':
                        for j in range(6):                  # colori del materiale (+0x14, 6 x RGBA)
                            v[mo + 0x14 + 4 * j:mo + 0x18 + 4 * j] = BLACK
                        n += 1
        if n:
            out[k] = bytes(v)
            print('nero:', k, n)
    import darc as _d
    return _d.rebuild(arc, out)


if __name__ == '__main__':
    main()
