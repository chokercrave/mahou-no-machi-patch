"""ROM 3DS gia' patchata (per chi non usa LayeredFS): romfs originale + file della mod sovrapposti, code.bin con
code.ips applicato. Usa la ROM estratta e decrittata in work/3ds e tools/3dstool.
  python make_rom.py            -> release/Tongari Boushi ITA v<VERSION>.3ds
La mod deve essere gia' costruita (build_all.py). I file temporanei stanno in release/_tmp (cancellati alla fine)."""
import os, shutil, subprocess, sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
SRC = os.path.join(ROOT, 'work', '3ds')
import paths
MOD = paths.MOD
TOOL = os.path.join(ROOT, 'tools', '3dstool', '3dstool.exe')
OUT = os.path.join(ROOT, 'release')
TMP = os.path.join(OUT, '_tmp')


def apply_ips(data, ips):
    """IPS standard: 'PATCH', record [off24 BE, size16 BE, dati] o RLE (size 0: len16 + byte), 'EOF'"""
    assert ips[:5] == b'PATCH'
    d = bytearray(data)
    p = 5
    while ips[p:p + 3] != b'EOF':
        off = int.from_bytes(ips[p:p + 3], 'big')
        n = int.from_bytes(ips[p + 3:p + 5], 'big')
        p += 5
        if n == 0:
            rl = int.from_bytes(ips[p:p + 2], 'big')
            chunk = ips[p + 2:p + 3] * rl
            p += 3
        else:
            chunk = ips[p:p + n]
            p += n
        if off + len(chunk) > len(d):
            d.extend(b'\0' * (off + len(chunk) - len(d)))
        d[off:off + len(chunk)] = chunk
    return bytes(d)


def run(*args):
    r = subprocess.run([TOOL] + list(args), cwd=TMP, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f'3dstool fallito: {args}\n{r.stdout}\n{r.stderr}')


def main(name=None):
    """name: nome del file .3ds (default 'Tongari Boushi ITA v<VERSION>.3ds'), es. per una build di prova"""
    ver = open(os.path.join(ROOT, 'VERSION'), encoding='utf-8').read().strip()
    if os.path.isdir(TMP):
        shutil.rmtree(TMP)
    os.makedirs(TMP)
    # romfs: originale + mod sovrapposta
    rdir = os.path.join(TMP, 'romfs')
    shutil.copytree(os.path.join(SRC, 'romfs'), rdir)
    n = 0
    for dp, _, fs in os.walk(os.path.join(MOD, 'romfs')):
        for f in fs:
            rel = os.path.relpath(os.path.join(dp, f), os.path.join(MOD, 'romfs'))
            dst = os.path.join(rdir, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(os.path.join(dp, f), dst)
            n += 1
    print('file della mod sovrapposti:', n)
    # exefs: code.bin decompresso, poi ricompresso da 3dstool (-z) come l'originale. Versione unica (build_code): codice
    # Ver.1.1 gia' patchato + exheader 1.1 (layout dei segmenti); altrimenti (build --target 10) code.bin 1.0 + code.ips
    edir = os.path.join(TMP, 'exefs')
    shutil.copytree(os.path.join(SRC, 'exefs'), edir)
    exh = os.path.join(SRC, 'exheader.bin')
    if os.path.exists(os.path.join(MOD, 'exefs', 'code.bin')):
        code = open(os.path.join(MOD, 'exefs', 'code.bin'), 'rb').read()
        # exheader ibrido: codeset (0x10-0x3f) e servizi (nim:aoc, am:app) della 1.1; della cartuccia 1.0 restano
        # flag (0xd: 1 = codice compresso, la 1.1 ha anche "app su SD"), remaster (0xe), jump id (0x1c8, nella 1.1
        # e' quello dell'aggiornamento 0004000E) e attributi (0x24f bit0 "Not use RomFS": la .3ds ha la sua romfs)
        e = bytearray(open(os.path.join(MOD, 'exheader.bin'), 'rb').read())
        e10 = open(exh, 'rb').read()
        for a, b in ((0xD, 0x10), (0x1C8, 0x1D0), (0x24F, 0x250)):
            e[a:b] = e10[a:b]
        exh = os.path.join(TMP, 'exheader.bin')
        open(exh, 'wb').write(e)
        print('codice: Ver.1.1 patchata (exheader ibrido 1.0/1.1)')
    else:
        code = open(os.path.join(edir, 'code.bin'), 'rb').read()
        code = apply_ips(code, open(os.path.join(MOD, 'exefs', 'code.ips'), 'rb').read())
    open(os.path.join(edir, 'code.bin'), 'wb').write(code)
    run('-cvtzf', 'exefs', 'exefs.bin', '--header', os.path.join(SRC, 'exefsheader.bin'), '--exefs-dir', 'exefs')
    run('-cvtf', 'romfs', 'romfs.bin', '--romfs-dir', 'romfs')
    run('-cvtf', 'cxi', '0.cxi', '--header', os.path.join(SRC, 'ncchheader.bin'), '--exh', exh,
        '--plain', os.path.join(SRC, 'plain.bin'), '--exefs', 'exefs.bin', '--romfs', 'romfs.bin', '--not-encrypt')
    name = name or f'Tongari Boushi ITA v{ver}.3ds'
    run('-cvt0f', 'cci', '0.cxi', os.path.join(OUT, name), '--header', os.path.join(SRC, 'ncsdheader.bin'))
    shutil.rmtree(TMP)
    print('->', os.path.join(OUT, name), os.path.getsize(os.path.join(OUT, name)) // (1024 * 1024), 'MB')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
