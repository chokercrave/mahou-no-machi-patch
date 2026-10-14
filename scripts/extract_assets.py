"""Estrae dal gioco le texture 2D originali usate come base dai generatori di immagini (make_*.py, gen_labels.py).
Da eseguire una volta dopo aver estratto la ROM in work/3ds (vedi README, "Compilare la patch dai sorgenti").
  python extract_assets.py [cartella_uscita]     (default work/img)
Per ogni ui/<archivio>.tarc della romfs:
  texture direttamente nel tarc            -> <uscita>/ui/<archivio>/<nome>.png
  texture dentro un DARC interno (<arc>)   -> <uscita>/ui/<archivio>/<arc>__timg_<nome>.png
Copie usate da make_images.py: ui/menu_mainmenu -> mainmenu, ui/menu_title_d -> title_d."""
import os, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
import bclim, darc, tbaf

ROOT = os.path.join(os.path.dirname(__file__), '..')
UI = os.path.join(ROOT, 'work', '3ds', 'romfs', 'ui')


def entries(path):
    for e in tbaf.parse(open(path, 'rb').read()):
        yield e['name'], (tbaf.decompress(e['data']) if e['comp'] else e['data'])


def save(data, path):
    try:
        im = bclim.decode(data)
    except Exception as ex:                      # formati non gestiti: si segnalano e si saltano
        print('  salto', os.path.basename(path), ex)
        return 0
    im.save(path)
    return 1


def main(out):
    n = 0
    for f in sorted(os.listdir(UI)):
        if not f.endswith('.tarc'):
            continue
        dst = os.path.join(out, 'ui', f[:-5])
        os.makedirs(dst, exist_ok=True)
        for name, data in entries(os.path.join(UI, f)):
            if data[:4] != b'darc' and (name.endswith('.bclim') or data[-0x28:-0x24] == b'CLIM'):   # anche .bin
                n += save(data, os.path.join(dst, os.path.splitext(name)[0].replace('/', '_') + '.png'))
            elif data[:4] == b'darc':
                for path, sub in darc.read_files(data).items():
                    p = path.lstrip('/')
                    if p.endswith('.bclim'):
                        n += save(sub, os.path.join(dst, f'{name}__{p[:-6].replace("/", "_", 1)}.png'))
    for src, name in (('menu_mainmenu', 'mainmenu'), ('menu_title_d', 'title_d')):
        d = os.path.join(out, name)
        if os.path.isdir(d):
            shutil.rmtree(d)
        shutil.copytree(os.path.join(out, 'ui', src), d)
    print(f'{n} texture estratte in {out}')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'work', 'img'))
