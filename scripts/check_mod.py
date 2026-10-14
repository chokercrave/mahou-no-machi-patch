"""Controllo di integrità della mod: per ogni .tarc installato confronta con l'originale
(stesse voci, stessi file nei DARC, stesse dimensioni/formati delle texture, BCLYT leggibili).
  python check_mod.py [filtro]
"""
import os, struct, sys
sys.path.insert(0, os.path.dirname(__file__))
import bclim, bclyt, darc, tbaf

ROOT = os.path.join(os.path.dirname(__file__), '..')
ORIG = os.path.join(ROOT, 'work', '3ds', 'romfs')
import paths
MOD = os.path.join(paths.MOD, 'romfs')


# texture ingrandite apposta (stesso formato): "Tocca lo schermo!" + credito della patch (make_title_credit.py)
RESIZED = {('timg/touch_icon_logo.bclim', (256, 256, 'RGBA4'))}

def files(path):
    data = open(path, 'rb').read()
    out = {}
    for e in tbaf.parse(data):
        out[e['name']] = (tbaf.decompress(e['data']) if e['comp'] else e['data'], e)
    return out, data


def luma_layeredfs():
    """Simula Luma (3DS vera): payload LayeredFS (0x118 B) a fine .text e percorso (39 B) a fine .rodata secondo le
    dimensioni dell'exheader; devono cadere su byte a zero che nessuna patch usa (build_code.luma_exheader)."""
    root = os.path.dirname(MOD)
    e = open(os.path.join(root, 'exheader.bin'), 'rb').read()
    d = open(os.path.join(root, 'exefs', 'code.bin'), 'rb').read()
    bad = 0
    for off, need, what in ((0x10, 0x118, 'payload'), (0x20, 39, 'percorso')):
        a, pages, size = struct.unpack_from('<III', e, off)
        s, t = a + size - 0x100000, a + pages * 0x1000 - 0x100000
        if t - s < need or any(d[s:s + need]):
            print(f'LUMA LAYEREDFS: il {what} a {a + size:#x} sovrascrive codice/dati della patch'); bad += 1
    return bad


def main(filt=''):
    bad = 0
    for root, _, fs in os.walk(MOD):
        for f in fs:
            if not f.endswith('.tarc') or filt not in f:
                continue
            p = os.path.join(root, f)
            rel = os.path.relpath(p, MOD)
            if rel.replace('\\', '/').startswith('dlc/'):
                # DLC sempre attivi (dlc.py): file nuovi senza originale -> solo struttura e dimensioni
                try:
                    b, braw = files(p)
                    assert struct.unpack_from('<I', braw, 4)[0] == len(braw), 'dimensione header'
                    assert all(len(blob) == e['raw'] for blob, e in b.values()), 'raw size'
                except Exception as ex:
                    print('ERRORE dlc', rel, ex); bad += 1
                continue
            try:
                a, araw = files(os.path.join(ORIG, rel))
                b, braw = files(p)
            except Exception as ex:
                print('ERRORE parse', rel, ex); bad += 1; continue
            if struct.unpack_from('<I', braw, 4)[0] != len(braw):
                print('  dimensione header errata', rel)
            if set(a) != set(b):
                print('voci diverse', rel, set(a) ^ set(b)); bad += 1
            for name, (blob, e) in b.items():
                if len(blob) != e['raw']:
                    print('  raw size errata', rel, name, len(blob), e['raw']); bad += 1
                ob = a.get(name, (b'',))[0]
                if blob[:4] == b'darc':
                    try:
                        fa, fb = darc.read_files(ob), darc.read_files(blob)
                    except Exception as ex:
                        print('ERRORE darc', rel, name, ex); bad += 1; continue
                    if set(fa) != set(fb):
                        print('file darc diversi', rel, name, set(fa) ^ set(fb)); bad += 1
                    for k, v in fb.items():
                        if k.endswith('.bclim'):
                            ia, ib = bclim.info(fa[k]), bclim.info(v)
                            if ia != ib and (k, ib) not in RESIZED:   # anche il formato: un ETC convertito in RGBA raddoppia la memoria
                                print('texture diversa', rel, name, k, ia, ib); bad += 1
                        elif k.endswith('.bclyt'):
                            try:
                                bclyt.texts(v)
                                # la 3DS vera (non l'emulatore) va in crash se una sezione non e' allineata a 4:
                                # il gioco legge i pannelli sul posto con ldm/vldr
                                mis = [(m, o, s) for m, o, s in bclyt.sections(v) if o % 4 or s % 4]
                                if mis:
                                    print('SEZIONE NON ALLINEATA', rel, name, k, mis[0]); bad += 1
                            except Exception as ex:
                                print('ERRORE bclyt', rel, name, k, ex); bad += 1
                    _, ffb = darc.parse(blob)
                    for f in ffb:
                        need = 0x80 if f['path'].endswith(('.bclim', '.bcfnt')) else 4
                        if f['off'] % need:
                            print('FILE DARC NON ALLINEATO', rel, name, f['path'], hex(f['off'])); bad += 1
    # codice 1.1 della build unica: ogni patch portata dalla 1.0 controllata parola per parola (port_audit.py)
    if not filt and os.path.exists(os.path.join(os.path.dirname(MOD), 'exefs', 'code.bin')):
        import port_audit
        bad += port_audit.main()
        bad += luma_layeredfs()
    print('problemi:', bad)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '')
