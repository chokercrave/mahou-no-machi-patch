"""Ricostruisce l'intera mod italiana nell'ordine corretto.
  python build_all.py
"""
import os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
import paths
MOD = os.path.join(paths.MOD, 'romfs')
STEPS = ['build_fonts.py', 'batch_import.py', 'fix_slots.py', 'manual_import.py', 'gen_labels.py', 'build_text.py', 'blob_texts.py import', 'build_npc.py', 'build_tables.py',
         'build_ui.py', 'blob_texts.py build', 'make_recipe_list.py', 'make_splash.py', 'make_status_plates.py', 'make_magic_tabs.py', 'make_warehouse_title.py', 'make_license_headers.py', 'make_images.py',
         'make_magazine_logo.py',   # logo "Spell & Spill" (in _auto: dopo gen_labels, che svuota _auto)
         'make_signs.py',      # insegne 3D + immagini 2D (ui_specs): rigenera le schede cambiate, rimette le copie in _auto
         'make_magazine_bg.py',  # sfondi t2n: logo "Berry's" -> "Spell & Spill" con la texture del logo originale
         'make_magazine_pages.py',   # pagine tex2 (copertine, anteprime 次号予告 -> "Prossimo numero")
         'make_magazine.py',   # titoli della rivista Spell & Spill (_auto/menu_magazine_tex0|1), dopo gen_labels
         'make_credits.py',    # crediti (staff_name_NN) in _auto: titoli italiani, nomi in lettere latine
         'make_magpage_labels.py',  # etichette colore/stile delle pagine rivista (menu_magpage_style_NN)
         'make_tutorials.py',  # lavagne dei tutorial in _auto (gen_labels le cancella): PRIMA di build_images
         'build_images.py',    # DOPO make_signs: installa anche le immagini 2D che make_signs mette in _auto
         'make_title_credit.py',   # credito della patch in fondo allo schermo basso del titolo (dopo build_images)
         'make_logo_skip.py all',   # nessun logo all'avvio (anti-pirateria, Konami, LovePlus) nel menu_logo.tarc installato
         'patch_shop_hours.py',     # QoL 1.2: negozi/servizi 24/7 (soglie orarie EVSC) + relazioni di qualsiasi sesso (patch_relationships)
         'build_code.py']

# Cache dei generatori di immagini lenti (12/10: ~290 s su ~380). Dipendono solo dal loro codice (+ moduli importati, testi
# della rivista compresi in mag_texts.py), dai font e dagli originali estratti, non dalle traduzioni: se la chiave non cambia si
# ricopiano i file che lo step aveva creato/modificato (in _auto e nella mod) invece di rigenerarli.
# --nocache forza la rigenerazione.
CACHED = {'make_signs.py', 'make_magazine_bg.py', 'make_magazine_pages.py', 'make_magazine.py'}
CACHE = os.path.join(ROOT, 'work', 'cache_steps')
AUTO = os.path.join(ROOT, 'work', 'img_it', '_auto')
OUTS = (AUTO, os.path.join(ROOT, 'work', 'img_it', 'signs'), os.path.join(ROOT, 'work', 'tut', 'pages_test'))  # uscite dei generatori


def _deps(mod, seen):
    """moduli locali (scripts/*.py) importati da mod, anche indirettamente"""
    import ast
    p = os.path.join(HERE, mod + '.py')
    if mod in seen or not os.path.exists(p):
        return seen
    seen.add(mod)
    for n in ast.walk(ast.parse(open(p, encoding='utf-8').read())):
        if isinstance(n, ast.Import):
            for a in n.names:
                _deps(a.name.split('.')[0], seen)
        elif isinstance(n, ast.ImportFrom) and n.module:
            _deps(n.module.split('.')[0], seen)
    return seen


def _cache_key(step):
    """codice dello step + moduli locali che importa (non tutti gli script: gender_tag/build_code non c'entrano)"""
    import hashlib
    h = hashlib.sha1()
    for m in sorted(_deps(step[:-3], set())):
        h.update(m.encode()); h.update(open(os.path.join(HERE, m + '.py'), 'rb').read())
    # ingressi: solo i font (gli originali estratti in work/img e romfs_x non cambiano; img_it e tut sono USCITE di
    # questi step o di altri: includerli invalidava la cache a ogni nuova immagine non correlata, es. "Vendita")
    for d in (os.path.join(ROOT, 'tools', 'fonts'),):
        for r, ds, fs in os.walk(d):
            ds[:] = sorted(x for x in ds if os.path.join(r, x) not in OUTS)
            for f in sorted(fs):
                # contenuto, non data: altri step riscrivono ogni volta le loro immagini identiche in img_it
                h.update(os.path.relpath(os.path.join(r, f), ROOT).encode())
                h.update(open(os.path.join(r, f), 'rb').read())
    return h.hexdigest()


def _snap():
    out = {}
    for base in OUTS + (MOD,):
        for r, ds, fs in os.walk(base):
            for f in fs:
                p = os.path.join(r, f)
                st = os.stat(p)
                out[p] = (st.st_size, st.st_mtime_ns)
    return out


def _cache_restore(step, key):
    d = os.path.join(CACHE, step)
    try:
        if open(os.path.join(d, 'KEY')).read() != key:
            return False
    except OSError:
        return False
    files = os.path.join(d, 'files')
    for r, ds, fs in os.walk(files):
        for f in fs:
            src = os.path.join(r, f)
            dst = os.path.join(ROOT, os.path.relpath(src, files))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
    return True


def _cache_store(step, key, before):
    d = os.path.join(CACHE, step)
    shutil.rmtree(d, ignore_errors=True)
    after = _snap()
    for p, v in after.items():
        if before.get(p) != v:
            dst = os.path.join(d, 'files', os.path.relpath(p, ROOT))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(p, dst)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'KEY'), 'w').write(key)


def _select(argv):
    """--from X: parte dallo step X (senza svuotare la mod); --only a,b: solo quegli step; --skip a,b: tutti tranne.
    I nomi sono prefissi del nome dello step (es. 'gen_labels'). Senza opzioni: build completa da mod vuota."""
    names = [x.split()[0] for x in STEPS]
    def find(p):
        m = [i for i, n in enumerate(names) if n.startswith(p)]
        if not m:
            sys.exit(f'step sconosciuto: {p}')
        return m[0]
    idx = list(range(len(STEPS)))
    partial = False
    for k, a in enumerate(argv):
        if a == '--from':
            idx = [i for i in idx if i >= find(argv[k + 1])]
            partial = True
        elif a == '--only':
            idx = [find(p) for p in argv[k + 1].split(',')]
            partial = True
        elif a == '--skip':
            drop = {find(p) for p in argv[k + 1].split(',')}
            idx = [i for i in idx if i not in drop]
            partial = True
    # Guardia: gli step che riscrivono interi tarc installati (build_ui dagli originali, build_images) cancellano le
    # correzioni fatte DOPO sugli archivi installati (credito del titolo, niente avviso legale/loghi all'avvio):
    # una build parziale che li tocca si porta dietro tutti gli step successivi a quello piu' a monte che li riscrive.
    # (10/10: --only build_images aveva rimesso l'avviso anti-pirateria e il titolo originale)
    rewrites = [i for i in idx if names[i] in ('build_ui.py', 'build_images.py')]
    if rewrites:
        idx = sorted(set(idx) | set(range(min(rewrites), len(STEPS))))
    return sorted(set(idx)), partial


if __name__ == '__main__':
    import time
    idx, partial = _select(sys.argv[1:])
    # build completa: si riparte da una mod vuota, cosi' non restano file di prove precedenti
    if not partial:
        if os.path.isdir(MOD):
            shutil.rmtree(MOD)
        os.makedirs(MOD)
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    times, t00 = [], time.time()
    for i in idx:
        s = STEPS[i]
        print(f'== {s}', flush=True)
        parts = s.split()
        t0 = time.time()
        cached = parts[0] in CACHED and '--nocache' not in sys.argv
        if cached:
            key = _cache_key(parts[0])
            if _cache_restore(parts[0], key):
                print('   (dalla cache)', flush=True)
                times.append((time.time() - t0, s + ' [cache]'))
                continue
            before = _snap()
        r = subprocess.run([sys.executable, os.path.join(HERE, parts[0])] + parts[1:], env=env)
        if cached and not r.returncode:
            _cache_store(parts[0], key, before)
        times.append((time.time() - t0, s))
        if r.returncode:
            sys.exit(f'errore in {s}')
    print('-- tempi per step (s):')
    for t, s in sorted(times, reverse=True):
        print(f'  {t:6.1f}  {s}')
    print(f'  {time.time() - t00:6.1f}  TOTALE')
    print('mod completa in', os.path.relpath(MOD, ROOT))
