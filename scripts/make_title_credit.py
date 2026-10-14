"""Credito della patch in fondo allo SCHERMO BASSO del titolo (va bene che lampeggi
insieme a "Tocca lo schermo!"). Il pannello Pic_touch_icon (title_touch_icon.bclyt, 128x64 al centro dello schermo
320x240) diventa 256x256 e la sua texture timg/touch_icon_logo.bclim (RGBA4) 256x256: l'icona resta al centro
(colonne 64-192, righe 96-160), il credito va nelle righe 234-246 (lo schermo finisce alla riga 248).
Testo NERO semitrasparente: sempre un po' piu' scuro dello sfondo verde.
Step di build_all DOPO build_images (modifica ui/menu_title_d.tarc gia' installato)."""
import os, struct, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import tbaf, darc, bclyt, bclim, ui_font

ROOT = os.path.join(os.path.dirname(__file__), '..')
import paths
MOD = os.path.join(paths.MOD, 'romfs', 'ui', 'menu_title_d.tarc')
ICON = os.path.join(ROOT, 'work', 'img_it', 'menu_title', 'touch_icon_logo.png')
PREVIEW = os.path.join(ROOT, 'work', 'img_it', 'menu_title', '_credito_anteprima.png')
SIZE = 256
ALPHA = 0.45


def compose():
    ver = open(os.path.join(ROOT, 'VERSION'), encoding='utf-8').read().strip()
    icon = Image.open(ICON).convert('RGBA')
    im = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    im.alpha_composite(icon, ((SIZE - icon.width) // 2, (SIZE - icon.height) // 2))
    t = ui_font.text(f'Patch italiana di chokercrave - v{ver}', (0, 0, 0), 8, ow=0, spacing=1)   # font pixel del gioco
    a = t.getchannel('A').point(lambda v: int(v * ALPHA))
    t.putalpha(a)
    im.alpha_composite(t, ((SIZE - t.width) // 2, 246 - t.height))
    return im


def fake_orig(w, h, d_orig):
    """piede CLIM dell'originale con nuove dimensioni (stesso formato): encode() usa queste misure"""
    foot = bytearray(d_orig[-0x28:])
    n = w * h * 2                                     # RGBA4 = 16 bit
    struct.pack_into('<HH', foot, 0x14 + 8, w, h)
    struct.pack_into('<I', foot, 0x14 + 0x10, n)
    struct.pack_into('<I', foot, 0x0C, n + 0x28)
    return bytes(n) + bytes(foot)


def main():
    im = compose()
    bg = Image.new('RGBA', im.size, (152, 204, 160, 255))
    bg.alpha_composite(im)
    bg.save(PREVIEW)
    ents = {e['name']: e for e in tbaf.parse(open(MOD, 'rb').read())}
    e = ents['title.arc']
    arc = tbaf.decompress(e['data']) if e['comp'] else e['data']
    fs = darc.read_files(arc)
    old = fs['timg/touch_icon_logo.bclim']
    assert bclim.info(old)[2] == 'RGBA4', bclim.info(old)
    tex = bclim.encode(im, fake_orig(SIZE, SIZE, old))
    lay = bytearray(fs['blyt/title_touch_icon.bclyt'])
    for m, o, sz in bclyt.sections(bytes(lay)):
        if m == b'pic1' and lay[o + 0xC:o + 0x1C].split(b'\0')[0] == b'Pic_touch_icon':
            struct.pack_into('<ff', lay, o + 0x44, float(SIZE), float(SIZE))
    arc2 = darc.rebuild(arc, {'timg/touch_icon_logo.bclim': tex, 'blyt/title_touch_icon.bclyt': bytes(lay)})
    tmp = MOD + '.tmp'
    tbaf.rebuild(MOD, {'title.arc': arc2}, tmp)
    os.replace(tmp, MOD)
    print('credito sullo schermo basso: texture', bclim.info(tex), '-> anteprima', PREVIEW)


if __name__ == '__main__':
    main()
