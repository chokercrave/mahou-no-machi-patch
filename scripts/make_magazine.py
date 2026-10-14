"""Rivista Spell & Spill: riscrive gli sprite dei titoli (mag_texts.ISSUES) in work/img_it/_auto/menu_magazine_tex0|1/<sprite>.png
(build_images.py li installa nei tarc ui/menu_magazine_tex0|1.tarc). gen_labels svuota _auto: questo passo va dopo di lui."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image
import mag_blobs as mb, mag_render as mr, mag_texts

ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'work', 'img_it', '_auto')
FONT = {1: 'Shojumaru', 2: 'CherryBombOne', 3: 'Shrikhand', 4: 'Bangers', 5: 'Pacifico', 6: 'Knewave', 7: 'Lemon',
        8: 'CinzelDecorative', 9: 'Gorditas', 10: 'LuckiestGuy', 11: 'Satisfy', 12: 'BubblegumSans', 13: 'Lobster', 14: 'Knewave',
        15: 'Boogaloo', 16: 'ChelaOne', 17: 'MochiyPopOne', 18: 'Gorditas', 19: 'CinzelDecorative', 20: 'SedgwickAveDisplay',
        21: 'Fascinate', 22: 'Knewave', 23: 'Shrikhand', 24: 'KaushanScript', 25: 'DelaGothicOne', 26: 'BubblegumSans', 27: 'GochiHand',
        28: 'Boogaloo', 29: 'RampartOne', 30: 'Modak', 31: 'SedgwickAveDisplay', 32: 'Satisfy', 33: 'PottaOne', 34: 'Bangers',
        35: 'CherryBombOne', 36: 'Fascinate', 37: 'AbrilFatface', 38: 'Lemon', 39: 'ChelaOne', 40: 'Gorditas',
        41: 'Courgette', 42: 'CinzelDecorative', 43: 'Shrikhand', 44: 'Shojumaru', 45: 'Knewave', 46: 'Lobster', 47: 'LuckiestGuy',
        48: 'AbrilFatface', 49: 'Pacifico', 50: 'BubblegumSans', 51: 'Gorditas', 52: 'Shrikhand'}   # un carattere per numero, scelto sul tema (fantasia ma leggibile)


def load_bg(name):
    """sfondo dello sprite titolo (coi nuovi loghi se gia' scritto), per il controllo di contrasto"""
    iss = min(int(name[2:4]), 53); d = 'menu_magazine_tex0' if iss <= 28 else 'menu_magazine_tex1'
    bgn = name.rsplit('_', 1)[0] + '_bg1.png'
    for p in (os.path.join(OUT, d, bgn), os.path.join(ROOT, 'work', 'img', 'ui', d, bgn)):
        if os.path.exists(p):
            return np.asarray(Image.open(p).convert('RGB'))
    return None


def build(name, texts, fontname='Chewy'):
    mr.BG = load_bg(name)
    mr.AVOID = None
    if '_t2n_' in name and int(name[2:4]) <= 53:                       # solo gli sfondi t2n hanno il logo: il testo non lo deve coprire
        import make_magazine_bg as mbg
        b = mbg.BOX[int(name[2:4])]
        mr.AVOID = (b[0] - 4, b[1] - 4, b[2] + 6, b[3] + 8)
    im, lab, bl = mb.blobs(name)
    if im.size != (512, 256):                 # sprite piccoli: nessun controllo di sfondo/logo
        mr.BG = None
        mr.AVOID = None
    lab = lab.copy()
    ids = {b['id']: b['label'] for b in bl}
    for i, items in texts.items():
        if items is None:
            continue
        if i not in ids:
            print(f'  ! {name}: unita {i} inesistente ({len(ids)} trovate)')
            ERRORS.append(name)
            continue
        label = ids[i]
        for t in (items if isinstance(items, list) else [items]):
            if isinstance(t, mag_texts.Z):
                arr = np.asarray(im).copy()
                arr[lab == label] = 0
                im = Image.fromarray(arr)
                continue
            if isinstance(t, mag_texts.E):
                x0, y0, x1, y1 = t.rect
                arr = np.asarray(im).copy()
                m = (lab == label); m[:y0] = False; m[y1:] = False; m[:, :x0] = False; m[:, x1:] = False
                arr[m] = 0
                im = Image.fromarray(arr)
                continue
            rect = None
            if isinstance(t, tuple):
                t, rect = t
            try:
                sub = lab
                if rect:
                    x0, y0, x1, y1 = rect
                    keep = np.zeros(lab.shape, bool); keep[y0:y1, x0:x1] = True
                    sub = np.where((lab == label) & ~keep, 0, lab)
                if isinstance(t, mag_texts.I):
                    im = mr.restyle_inner(im, sub, label, str(t), fontname)
                else:
                    im = mr.restyle(im, sub, label, t, fontname)
                if rect:
                    lab = np.where((lab == label) & keep, 0, lab)
            except Exception as e:
                print(f'  ! {name} #{i}: {type(e).__name__} {e}')
                ERRORS.append(name)
    return im


ERRORS = []


def main(only=None):
    n = 0
    for iss, sprites in sorted(mag_texts.ISSUES.items()):
        if only and iss not in only:
            continue
        for name, texts in sprites.items():
            im = build(name, texts, FONT.get(iss, 'Chewy'))
            _, fname, d = mb.folder(name)
            od = os.path.join(OUT, d)
            os.makedirs(od, exist_ok=True)
            im.save(os.path.join(od, fname))
            n += 1
    print(f'{n} sprite della rivista scritti')
    if ERRORS:              # es. un font mancante in tools/fonts: la rivista resterebbe in parte in giapponese
        sys.exit(f'{len(ERRORS)} errori in {len(set(ERRORS))} sprite')


if __name__ == '__main__':
    main([int(a) for a in sys.argv[1:]] or None)
