"""Rigenera tutte le lavagne dei tutorial (work/img_it/_auto/menu_tutorial_pics*): gen_labels svuota _auto a ogni build,
quindi questo passo va PRIMA di build_images. Ogni famiglia e' uno script tut_*.py; un errore in una famiglia non ferma le altre
ma lo stampa (exit 0: gli avvisi 'riquadro piu' alto' di Charm sono noti e innocui)."""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = [('tut_charm.py', []), ('tut_charm.py', ['special']), ('tut_specs_tutorial.py', []), ('tut_specs_language.py', []),
        ('tut_specs_magic.py', []), ('tut_specs_misc.py', []), ('tut_specs_coorde.py', []), ('tut_specs_ucc.py', []),
        ('tut_specs_shop.py', []), ('tut_specs_runway.py', []), ('tut_specs_photo.py', []), ('tut_specs_chime.py', []),
        ('tut_specs_idol.py', []), ('tut_specs_mydesign.py', []), ('tut_specs_etc.py', [])]


def main():
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    bad = 0
    for script, args in RUNS:
        r = subprocess.run([sys.executable, script] + args, cwd=HERE, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
        lines = r.stdout.splitlines()
        errs = [l for l in lines if l.lstrip().startswith('!')] + ([r.stderr.strip()[-300:]] if r.returncode else [])
        print(f'{script} {" ".join(args)}: {sum(l.startswith("ok") for l in lines)} ok, {len(errs)} errori')
        for e in errs:
            print('   ', e)
        bad += bool(errs)
    print('famiglie con avvisi:', bad)


if __name__ == '__main__':
    main()
