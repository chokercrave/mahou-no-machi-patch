"""Costruisce i font italiani e li installa nella mod LayeredFS (ui/menu_font.tarc).
- LC.bcfnt: glifi copiati da LC_full.bcfnt (stesse metriche, disegnati da Nintendo).
- DF_kyougeki / DF_shm_gothic: nessun donatore, accentate sintetizzate = vocale del font + accento.
"""
import os, sys, unicodedata
sys.path.insert(0, os.path.dirname(__file__))
import tbaf
from bcfnt import Bcfnt
from font_patch import from_donor, patch_and_verify, remap, ITA_CHARS

# simbolo della tastiera ABC -> vocale accentata che il font disegna al suo posto
KEY_REMAP = {'<': 'à', '>': 'è', '\\': 'é', '_': 'ì', '#': 'ò', '&': 'ù'}

ROOT = os.path.join(os.path.dirname(__file__), '..')
UI = os.path.join(ROOT, 'work', '3ds', 'romfs_x', 'ui')
OUT = os.path.join(ROOT, 'work', 'font')
import paths
MOD = os.path.join(paths.MOD, 'romfs', 'ui')
SYNTH_CHARS = 'àáèéìíòóùúÀÁÈÉÌÍÒÓÙÚ'
# accenti: X = inchiostro pieno, H = mezzo tono (solo per il font antialiasato)
ACCENTS = {
    'DF_kyougeki': {'grave': ['XH.', '.HX'], 'acute': ['.HX', 'XH.']},
    'DF_shm_gothic': {'grave': ['X.', '.X'], 'acute': ['.X', 'X.']},
}


def ink_rows(cell):
    return [j for j, r in enumerate(cell) if any(v & 0xF for v in r)]


def ink_cols(cell, rows):
    return [i for i in range(len(cell[0])) if any(cell[j][i] & 0xF for j in rows)]


def synth(font, name):
    cell_of = lambda c: [bytearray(r) for r in font.glyph_cell(font.cmap[ord(c)])]
    x_top = min(ink_rows(cell_of('u')))      # inizio altezza x
    glyphs = {}
    for ch in SYNTH_CHARS:
        base, mark = unicodedata.normalize('NFD', ch)
        kind = {'̀': 'grave', '́': 'acute'}[mark]
        cell = cell_of(base)
        if base == 'i':                       # toglie il puntino
            for j in range(x_top):
                cell[j][:] = bytes(len(cell[j]))
        rows = ink_rows(cell)
        full = max(v for r in cell for v in r)
        half = (full & 0xF0) | ((full & 0xF) // 2)
        pat = ACCENTS[name][kind]
        top = min(rows)
        bottom = top - 2 if base.islower() else max(len(pat) - 1, top - 2)
        cols = ink_cols(cell, rows)
        x0 = round((cols[0] + cols[-1] + 1) / 2 - len(pat[0]) / 2)
        for j, line in enumerate(pat):
            for i, p in enumerate(line):
                if p != '.':
                    cell[bottom - len(pat) + 1 + j][x0 + i] = full if p == 'X' else half
        glyphs[ch] = (cell, font.widths[font.cmap[ord(base)]][2])
    return glyphs


def proportional(path, space=4, gap=1):
    """Rende proporzionali i glifi latini di un font monospazio: larghezza = inchiostro + gap,
    con bearing sinistro negativo per allineare l'inchiostro all'origine."""
    import struct
    f = Bcfnt(open(path, 'rb').read())
    latin = [c for c in f.cmap if 0x21 <= c <= 0x7E or 0xA1 <= c <= 0x17F]
    cache = {}
    for c in latin:
        g = f.cmap[c]
        s = f.cell_origin(g)[0]
        if s not in cache:
            cache[s] = f.sheet_pixels(s)
        cell = f.glyph_cell(g, cache)
        cols = [i for i in range(f.cell_w) if any(r[i] & 0xF for r in cell)]
        if not cols:
            continue
        w = cols[-1] - cols[0] + 1
        struct.pack_into('<bBB', f.data, f.widths[g][1], -cols[0], cols[-1] + 1, w + gap)
    g = f.cmap[0x20]
    left, gw, _ = f.widths[g][2]
    struct.pack_into('<bBB', f.data, f.widths[g][1], left, gw, space)
    open(path, 'wb').write(f.data)


def main():
    os.makedirs(OUT, exist_ok=True)
    src = os.path.join(UI, 'menu_font.tarc_x')
    lc = Bcfnt(open(os.path.join(src, 'LC.bcfnt'), 'rb').read())
    full = Bcfnt(open(os.path.join(UI, 'menu_acceptable_use_policy.tarc_x', 'LC_full.bcfnt'), 'rb').read())
    patch_and_verify(lc, from_donor(lc, full, ITA_CHARS), os.path.join(OUT, 'LC.bcfnt'))
    proportional(os.path.join(OUT, 'LC.bcfnt'))
    for name in ACCENTS:
        f = Bcfnt(open(os.path.join(src, name + '.bcfnt'), 'rb').read())
        patch_and_verify(f, synth(f, name), os.path.join(OUT, name + '.bcfnt'))
    # tastiera: i simboli inutili della scheda ABC disegnano le vocali accentate (nomi con accenti)
    for n in ('LC.bcfnt', 'DF_kyougeki.bcfnt', 'DF_shm_gothic.bcfnt'):
        p = os.path.join(OUT, n)
        data = remap(open(p, 'rb').read(), KEY_REMAP)
        open(p, 'wb').write(data)
    repl = {n: open(os.path.join(OUT, n), 'rb').read() for n in ('LC.bcfnt', 'DF_kyougeki.bcfnt', 'DF_shm_gothic.bcfnt')}
    os.makedirs(MOD, exist_ok=True)
    out = os.path.join(MOD, 'menu_font.tarc')
    tbaf.rebuild(os.path.join(ROOT, 'work', '3ds', 'romfs', 'ui', 'menu_font.tarc'), repl, out)
    chk = {e['name']: tbaf.decompress(e['data']) if e['comp'] else e['data'] for e in tbaf.parse(open(out, 'rb').read())}
    assert all(chk[k] == v for k, v in repl.items())
    print('mod installata:', os.path.relpath(out, ROOT))


if __name__ == '__main__':
    main()
