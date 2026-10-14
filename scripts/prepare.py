"""Prepara la cartella work/ partendo dalla propria copia del gioco (da eseguire una volta, prima di build_all.py).

  python scripts/prepare.py <gioco.cci|.3ds> <aggiornamento_1.1.cia>

  <gioco>          dump decrittato della cartuccia giapponese Ver.1.0 (00040000000B4A00)
  <aggiornamento>  CIA decrittato dell'aggiornamento Ver.1.1 (v1056, 0004000E000B4A00)

Passaggi (ognuno si salta se il suo risultato c'e' gia'; --force li rifa' tutti):
  1. ROM -> work/3ds        con tools/3dstool: intestazioni, exheader, exefs (code.bin decompresso), romfs
  2. CIA -> work/v11        contenuto 0 (NCCH) -> exheader e exefs della Ver.1.1 (la 1.1 non ha romfs)
  3. impronte SHA1 di code.bin 1.0, code.bin 1.1 ed exheader 1.1: le patch del codice valgono solo per questi file
  4. work/3ds/romfs_x       archivi .tarc estratti (tbaf.py)
  5. work/img, work/tut     texture originali in PNG (extract_assets.py, tut_extract.py)
Il percorso della ROM resta in work/rom_path.txt: make_release.py la usa come sorgente della patch xdelta.
"""
import hashlib, os, shutil, struct, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, 'tools', '3dstool', '3dstool.exe')
W3, W11 = os.path.join(ROOT, 'work', '3ds'), os.path.join(ROOT, 'work', 'v11')
ROM_PATH = os.path.join(ROOT, 'work', 'rom_path.txt')
SHA1 = {os.path.join(W3, 'exefs', 'code.bin'): 'b12196a75b2f7b3cfa121f8ca9540ef878880be9',
        os.path.join(W11, 'exefs', 'code.bin'): 'e7132927854a932b36445a228ee143a3d849e5bd',
        os.path.join(W11, 'raw', 'exh.bin'): '04322014c2f15205abafabf1746fd3c584cb2985'}


def run(cwd, *args):
    r = subprocess.run([TOOL] + list(args), cwd=cwd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f'3dstool non riuscito ({" ".join(args)}):\n{r.stdout}\n{r.stderr}')


def sha1(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def extract_rom(rom):
    """stessi file e nomi che make_rom.py usa per ricostruire la ROM"""
    os.makedirs(W3, exist_ok=True)
    run(W3, '-xvt0f', 'cci', 'partition0.cxi', os.path.abspath(rom), '--header', 'ncsdheader.bin')
    run(W3, '-xvtf', 'cxi', 'partition0.cxi', '--header', 'ncchheader.bin', '--exh', 'exheader.bin',
        '--plain', 'plain.bin', '--exefs', 'exefs.bin', '--romfs', 'romfs.bin')
    run(W3, '-xvtfu', 'exefs', 'exefs.bin', '--header', 'exefsheader.bin', '--exefs-dir', 'exefs')
    run(W3, '-xvtf', 'romfs', 'romfs.bin', '--romfs-dir', 'romfs')


def extract_update(cia):
    """CIA: intestazione, catena di certificati, ticket, TMD e contenuti, ognuno allineato a 64 byte"""
    raw = os.path.join(W11, 'raw')
    os.makedirs(raw, exist_ok=True)
    with open(cia, 'rb') as f:
        hdr = f.read(0x20)
        hsize, _, _, cert, tik, tmd, meta, csize = struct.unpack('<IHHIIIIQ', hdr)
        al = lambda x: (x + 63) & ~63
        f.seek(al(hsize) + al(cert) + al(tik) + al(tmd))
        ncch = f.read(csize)
    if ncch[0x100:0x104] != b'NCCH':
        sys.exit('il CIA non contiene un NCCH leggibile: serve il CIA DECRITTATO dell\'aggiornamento')
    content = os.path.join(raw, 'content.0000.00000000')
    open(content, 'wb').write(ncch)
    run(raw, '-xvtf', 'cxi', 'content.0000.00000000', '--exh', 'exh.bin', '--exefs', 'exefs.bin')
    run(W11, '-xvtfu', 'exefs', os.path.join('raw', 'exefs.bin'), '--exefs-dir', 'exefs')


def main(argv):
    force = '--force' in argv
    args = [a for a in argv if a != '--force']
    if len(args) != 2:
        sys.exit(__doc__)
    rom, cia = args
    if not os.path.exists(TOOL):
        sys.exit(f'manca {TOOL} (vedi docs/building.md)')
    for p in (rom, cia):
        if not os.path.isfile(p):
            sys.exit(f'file non trovato: {p}')
    if force:
        for d in (W3, W11):
            if os.path.isdir(d):
                keep = os.path.join(W11, 'funcmap.tsv')               # tabella versionata, non si rigenera
                saved = open(keep, 'rb').read() if d == W11 and os.path.exists(keep) else None
                shutil.rmtree(d)
                if saved:
                    os.makedirs(d)
                    open(keep, 'wb').write(saved)
    os.makedirs(os.path.join(ROOT, 'work'), exist_ok=True)
    open(ROM_PATH, 'w', encoding='utf-8').write(os.path.abspath(rom))    # per make_release.py (sorgente della xdelta)
    print('1/5 ROM -> work/3ds')
    if not os.path.isdir(os.path.join(W3, 'romfs')):
        extract_rom(rom)
    print('2/5 aggiornamento 1.1 -> work/v11')
    if not os.path.exists(os.path.join(W11, 'exefs', 'code.bin')):
        extract_update(cia)
    print('3/5 controllo delle impronte')
    bad = [p for p, h in SHA1.items() if not os.path.exists(p) or sha1(p) != h]
    for p in bad:
        print('  DIVERSO:', os.path.relpath(p, ROOT))
    if bad:
        sys.exit('dump non riconosciuto: serve la cartuccia giapponese Ver.1.0 e l\'aggiornamento Ver.1.1 (v1056), '
                 'entrambi decrittati. Rifare con --force dopo aver cambiato file.')
    print('4/5 archivi .tarc -> work/3ds/romfs_x')
    if not os.path.isdir(os.path.join(W3, 'romfs_x')):
        subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'tbaf.py'), os.path.join(W3, 'romfs'),
                        os.path.join(W3, 'romfs_x')], check=True, stdout=subprocess.DEVNULL)
    print('5/5 texture originali -> work/img, work/tut')
    if not os.path.isdir(os.path.join(ROOT, 'work', 'img', 'ui')):
        import extract_assets
        extract_assets.main(os.path.join(ROOT, 'work', 'img'))
    if not os.path.isdir(os.path.join(ROOT, 'work', 'tut', 'png')):
        subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'tut_extract.py')], check=True,
                       stdout=subprocess.DEVNULL)
    print('pronto: ora python scripts/build_all.py')


if __name__ == '__main__':
    main(sys.argv[1:])
