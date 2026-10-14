"""Applica work/trad/tables/<nome>.json alle tabelle di stringhe di common.tarc e installa la mod."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import strtable, tbaf

ROOT = os.path.join(os.path.dirname(__file__), '..')
SRC = os.path.join(ROOT, 'work', '3ds', 'romfs_x', 'common.tarc_x')
import paths
MOD = os.path.join(paths.MOD, 'romfs', 'common.tarc')
TABLES = ['MenuString', 'ItemSlotWindowMessageData', 'GameCoinShop']


def main():
    repl = {}
    for t in TABLES:
        trad = {k: v for k, v in json.load(open(os.path.join(ROOT, 'work', 'trad', 'tables', t + '.json'), encoding='utf-8')).items() if v}
        data = strtable.build(open(os.path.join(SRC, t + '.bin'), 'rb').read(), trad)
        got = list(strtable.load(data)[2].values())
        assert all(s in trad.values() or s not in trad for s in got)
        repl[t + '.bin'] = data
        print(f'{t}: {len(trad)} stringhe tradotte')
    os.makedirs(os.path.dirname(MOD), exist_ok=True)
    tbaf.rebuild(os.path.join(ROOT, 'work', '3ds', 'romfs', 'common.tarc'), repl, MOD)
    print('mod common.tarc installata')


if __name__ == '__main__':
    main()
