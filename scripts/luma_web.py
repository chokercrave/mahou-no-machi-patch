"""Dati per creare la cartella Luma3DS nel browser (pagina 3DS del sito), senza file del gioco.

    python scripts/luma_web.py <ROM italiana .3ds>   -> stampa il JSON (campo "luma" della release in patches_3ds.json)

Il browser applica la xdelta, poi da quella ROM estrae i file della mod (stesso lavoro del .bat con 3dstool):
- "files": [percorso, crc32, dimensione] di ogni file della cartella luma/titles/<TID>/: romfs della mod, code.bin
  (il .code dell'ExeFS decompresso), exheader.bin, code.ips. Il browser rifiuta lo zip se un CRC non torna.
- "exheaderPatch": [offset, byte]: l'exheader della ROM (0x800 byte dall'NCCH+0x200) diventa quello della mod.
- "codeIps": contenuto di code.ips (vuoto: sovrascrive quello di versioni precedenti).
"""
import json, os, struct, sys, zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

CODE_IPS = b'PATCHEOF'


def rom_exheader(rom):
    with open(rom, 'rb') as f:
        head = f.read(0x200)
        assert head[0x100:0x104] == b'NCSD', 'non e\' una ROM .3ds/.cci'
        ncch = struct.unpack_from('<I', head, 0x120)[0] * 0x200
        f.seek(ncch + 0x100)
        assert f.read(4) == b'NCCH'
        f.seek(ncch + 0x200)
        return f.read(0x800)


def entry(path, data):
    return [path, zlib.crc32(data), len(data)]


def info(rom, mod=paths.MOD):
    romfs = os.path.join(mod, 'romfs')
    files = []
    for rel in sorted(os.path.relpath(os.path.join(dp, f), romfs) for dp, _, fs in os.walk(romfs) for f in fs):
        files.append(entry('romfs/' + rel.replace(os.sep, '/'), open(os.path.join(romfs, rel), 'rb').read()))
    exh = open(os.path.join(mod, 'exheader.bin'), 'rb').read()
    files.append(entry('code.bin', open(os.path.join(mod, 'exefs', 'code.bin'), 'rb').read()))
    files.append(entry('exheader.bin', exh))
    files.append(entry('code.ips', CODE_IPS))
    src = rom_exheader(rom)
    assert len(exh) == len(src) == 0x800
    return {
        'titleId': paths.TITLE,
        'files': files,
        'exheaderPatch': [[i, exh[i]] for i in range(len(exh)) if exh[i] != src[i]],
        'codeIps': CODE_IPS.decode(),
    }


if __name__ == '__main__':
    print(json.dumps(info(sys.argv[1]), separators=(',', ':')))
