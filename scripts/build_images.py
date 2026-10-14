"""Inserisce le immagini italiane nelle texture dei layout e installa i tarc nella mod.
Fonti:
- gruppi manuali: work/img_it/<gruppo>/<texture>.png  -> GRUPPI (tarc, arc)
- etichette automatiche: work/img_it/_auto/<archivio>/<arc>__timg_<texture>.png  oppure <texture>.png
  (texture direttamente nel tarc). L'archivio è il nome della cartella ui (es. menu_common).
Le texture ETC1/ETC1A4 vengono ricodificate in ETC (stesso formato e dimensione). Va eseguito DOPO build_ui.py: parte dai tarc
già presenti nella mod, se esistono.
"""
import collections, concurrent.futures, hashlib, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import bclim, darc, tbaf

ROOT = os.path.join(os.path.dirname(__file__), '..')
ORIG = os.path.join(ROOT, 'work', '3ds', 'romfs')
import paths
MOD = os.path.join(paths.MOD, 'romfs')
IMG = os.path.join(ROOT, 'work', 'img_it')
GRUPPI = {
    'menu_title': [('ui/menu_title_d.tarc', 'title.arc'), ('ui/menu_title_u.tarc', 'title.arc')],
    'menu_mainmenu': [('ui/menu_mainmenu.tarc', 'mainmenu.arc')],
    'menu_logo': [('ui/menu_logo.tarc', 'logo.arc')],          # make_splash.py
    'menu_status': [('ui/menu_status.tarc', 'status.arc')],    # make_status_plates.py
    'menu_input_magic2': [('ui/menu_input_magic2.tarc', '000.bin')],   # make_magic_tabs.py
    'menu_warehouse': [('ui/menu_warehouse.tarc', 'warehouse.arc')],   # make_warehouse_title.py
    'menu_sell': [('ui/menu_sell.tarc', 'sell_menu.arc')],             # make_warehouse_title.py ("Vendita")
    'menu_make_profile': [('ui/menu_make_profile.tarc', 'makeprofile.arc')],   # make_license_headers.py
}


def jobs():
    """{tarc: {(arc o None, chiave texture): png}}"""
    out = collections.defaultdict(dict)
    for group, targets in GRUPPI.items():
        for f in os.listdir(os.path.join(IMG, group)):
            if f.endswith('.png') and '_anteprima' not in f:
                for tarc, arc in targets:
                    out[tarc][(arc, f'timg/{f[:-4]}.bclim')] = os.path.join(IMG, group, f)
    auto = os.path.join(IMG, '_auto')
    if os.path.isdir(auto):
        for d in os.listdir(auto):
            if not os.path.isdir(os.path.join(auto, d)):
                continue
            tarc = f'ui/{d}.tarc'
            for f in os.listdir(os.path.join(auto, d)):
                if not f.endswith('.png'):
                    continue
                if '__' in f:
                    arc, rest = f.split('__', 1)
                    out[tarc][(arc, rest[:-4].replace('_', '/', 1) + '.bclim')] = os.path.join(auto, d, f)
                else:
                    out[tarc][(None, f[:-4] + '.bclim')] = os.path.join(auto, d, f)
    return out


CACHE = os.path.join(ROOT, 'work', 'cache_enc')
_POOL = None


def _encode(png, orig):
    im = Image.open(png)
    fmt = bclim.info(orig)[2]
    # ETC1/ETC1A4 si ricodificano nello stesso formato: convertirle in RGBA4 raddoppiava la texture e
    # l'archivio decompresso del menu Start (status.arc) superava il buffer del gioco -> UI invisibile
    return bclim.encode_etc(im, orig) if fmt.startswith('ETC') else bclim.encode(im, orig)


def _key(png, orig):
    h = hashlib.sha1(open(png, 'rb').read())
    h.update(orig[-0x28:] + len(orig).to_bytes(8, 'little'))   # l'encoder usa solo footer e lunghezza dell'originale
    h.update(open(bclim.__file__, 'rb').read())   # se cambia l'encoder la cache decade
    return h.hexdigest()


def encode_many(pairs):
    """{chiave: (png, orig)} -> {chiave: bytes}. Cache su disco per contenuto; i mancanti si codificano in parallelo
    (la codifica ETC e' Python puro: ~25 min in serie su tutto il gioco, pochi minuti con la cache e i processi)."""
    global _POOL
    os.makedirs(CACHE, exist_ok=True)
    keys = {k: _key(*v) for k, v in pairs.items()}
    out, todo = {}, []
    for k, h in keys.items():
        f = os.path.join(CACHE, h + '.bin')
        if os.path.exists(f):
            out[k] = open(f, 'rb').read()
        else:
            todo.append(k)
    if todo:
        if len(todo) > 3:
            _POOL = _POOL or concurrent.futures.ProcessPoolExecutor(max_workers=max(1, (os.cpu_count() or 2) - 2))
            res = list(_POOL.map(_encode, [pairs[k][0] for k in todo], [pairs[k][1] for k in todo], chunksize=2))
        else:
            res = [_encode(*pairs[k]) for k in todo]
        for k, data in zip(todo, res):
            out[k] = data
            tmp = os.path.join(CACHE, keys[k] + '.tmp')
            open(tmp, 'wb').write(data)
            os.replace(tmp, os.path.join(CACHE, keys[k] + '.bin'))
    print(f'  codifica: {len(pairs) - len(todo)} da cache, {len(todo)} nuove')
    return out


def main():
    for tarc, items in jobs().items():
        base = os.path.join(MOD, tarc) if os.path.exists(os.path.join(MOD, tarc)) else os.path.join(ORIG, tarc)
        entries = {e['name']: e for e in tbaf.parse(open(base, 'rb').read())}
        get = lambda n: tbaf.decompress(entries[n]['data']) if entries[n]['comp'] else entries[n]['data']
        repl, n = {}, 0
        by_arc = collections.defaultdict(dict)
        for (arc, key), png in items.items():
            by_arc[arc][key] = png
        for arc, texs in by_arc.items():
            if arc is None:
                # BCLIM sciolti nel tarc: alcuni archivi li chiamano <nnn>.bin (menu_magazine_tex2), non <nome>.bclim
                texs = {(k if k in entries else k[:-6] + '.bin'): p for k, p in texs.items()}
                enc = encode_many({key: (png, get(key)) for key, png in texs.items() if key in entries})
                repl.update(enc); n += len(enc)
                continue
            if arc not in entries:
                continue
            arc_data = get(arc)
            files = darc.read_files(arc_data)
            r = encode_many({k: (p, files[k]) for k, p in texs.items() if k in files})
            n += len(r)
            repl[arc] = darc.rebuild(arc_data, r)
        out = os.path.join(MOD, tarc)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        tmp = out + '.tmp'
        tbaf.rebuild(base, repl, tmp)
        os.replace(tmp, out)
        print(f'{tarc}: {n} texture sostituite')


if __name__ == '__main__':
    main()
    if _POOL:
        _POOL.shutdown()
