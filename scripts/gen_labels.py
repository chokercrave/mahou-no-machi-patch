"""Genera le etichette italiane da work/trad/labels_it.tsv (indice -> testo, '\\n' = a capo)
usando work/img/labels/index.tsv (indice -> archivio, file PNG originale).
Output: work/img_it/_auto/<archivio>/<file>.png  +  foglio di controllo _anteprima.png
"""
import os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
from relabel import relabel

ROOT = os.path.join(os.path.dirname(__file__), '..')
IDX = os.path.join(ROOT, 'work', 'img', 'labels', 'index.tsv')
SRC = os.path.join(ROOT, 'work', 'img', 'ui')
OUT = os.path.join(ROOT, 'work', 'img_it', '_auto')


def main():
    import shutil
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    index = {}
    for line in open(IDX, encoding='utf-8'):
        n, d, f = line.rstrip('\n').split('\t')
        index[int(n)] = (d, f)
    trad = {}
    for line in open(os.path.join(ROOT, 'work', 'trad', 'labels_it.tsv'), encoding='utf-8-sig'):
        line = line.rstrip('\n')
        if '\t' in line:
            n, t = line.split('\t', 1)
            trad[int(n)] = t.replace('\\n', '\n')
    done = []
    import re, relabel as rl
    def group(d, f):
        # titoli e linguette: tutte le etichette dello stesso tipo hanno la stessa dimensione del testo
        # pulsanti: nel giapponese tutte le scritte dei pulsanti (una o due righe) hanno lo stesso corpo
        if re.search(r'__timg_button_(blue|gray|yel|green)_txt', f):
            return f'{d}:button_txt'
        if re.search(r'__timg_(back|front|okuru|retake|save|use)_button', f):
            return f'{d}:button'
        if re.search(r'__timg_safe_tab_[ou]_', f):
            return f'{d}:safe_tab'
        m = re.search(r'__timg_(title|tab_txt|keyboard_tab|warehouse_tab)_', f)
        return f'{d}:' + ('tab_txt' if m.group(1) in ('keyboard_tab', 'warehouse_tab') else m.group(1)) if m else None
    for pas in (1, 2):                       # passo 1: misura la dimensione adatta a ogni etichetta; passo 2: usa la minima del gruppo
        done = []
        for n, text in sorted(trad.items()):
            d, f = index[n]
            os.makedirs(os.path.join(OUT, d), exist_ok=True)
            dst = os.path.join(OUT, d, f)
            edges = text.startswith('@')
            rl.CUR_GROUP = group(d, f)
            relabel(os.path.join(SRC, d, f), text.lstrip('@'), dst, keep_edges=edges)
            done.append((n, os.path.join(SRC, d, f), dst))
        if pas == 1:
            rl.CAP.update({k: min(v) for k, v in rl.REC.items()})
    rl.CUR_GROUP = None
    # anteprima: originale | italiano
    rows = len(done)
    sheet = Image.new('RGBA', (2 * 300 + 60, 54 * ((rows + 1) // 2) + 10), (70, 70, 70, 255))
    dr = ImageDraw.Draw(sheet)
    for i, (n, a, b) in enumerate(done):
        x = (i % 2) * 330
        y = (i // 2) * 54
        ia, ib = Image.open(a).convert('RGBA'), Image.open(b).convert('RGBA')
        ia.thumbnail((150, 48)); ib.thumbnail((150, 48))
        dr.text((x, y), str(n), fill=(255, 255, 0, 255))
        sheet.alpha_composite(ia, (x + 24, y + 4)); sheet.alpha_composite(ib, (x + 176, y + 4))
    sheet.save(os.path.join(OUT, '_anteprima.png'))
    print(len(done), 'etichette generate')


if __name__ == '__main__':
    main()
