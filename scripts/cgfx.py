"""Texture dentro file CGFX (.bctex/.bcmdl dei modelli 3D) <-> PNG.
  python cgfx.py dump <cartella_tarc_x> <cartella_png>     estrae tutte le texture (TXOB) in PNG
Struttura TXOB (ImageTexture): 'TXOB' a +4 dall'inizio dell'oggetto; +0x18 altezza, +0x1C larghezza,
+0x34 formato PICA, +0x38 offset relativo alla descrizione immagine (altezza, larghezza, size, offset dati).
Formati PICA: 0 RGBA8, 1 RGB8, 2 RGBA5551, 3 RGB565, 4 RGBA4, 5 LA8, 6 HILO8, 7 L8, 8 A8, 9 LA4, 10 L4,
11 A4, 12 ETC1, 13 ETC1A4. I pixel sono codificati come nei BCLIM (tile Morton / blocchi ETC).
"""
import os, struct, sys
sys.path.insert(0, os.path.dirname(__file__))
import bclim

PICA = ['RGBA8', 'RGB8', 'RGBA5551', 'RGB565', 'RGBA4', 'LA8', 'HILO8', 'L8', 'A8', 'LA4', 'L4', 'A4',
        'ETC1', 'ETC1A4']
BCLIM_ID = {v: k for k, v in bclim.FMT.items()}


def textures(d):
    """[(nome, w, h, formato, offset_dati, size_dati)] per ogni TXOB del file"""
    out = []
    i = d.find(b'TXOB')
    while i >= 0:
        o = i - 4
        try:
            name_ptr = o + 0x0C + struct.unpack_from('<i', d, o + 0x0C)[0]
            name = d[name_ptr:d.index(b'\0', name_ptr)].decode('ascii', 'replace')
            h, w = struct.unpack_from('<II', d, o + 0x18)
            fmt = struct.unpack_from('<I', d, o + 0x34)[0]
            img = o + 0x38 + struct.unpack_from('<i', d, o + 0x38)[0]
            ih, iw, size = struct.unpack_from('<III', d, img)
            data = img + 0x0C + struct.unpack_from('<i', d, img + 0x0C)[0]
            if (ih, iw) == (h, w) and fmt < len(PICA) and 0 < size <= len(d):
                out.append((name, w, h, PICA[fmt], data, size))
        except (struct.error, ValueError):
            pass
        i = d.find(b'TXOB', i + 4)
    return out


def _as_bclim(raw, w, h, fmt):
    """dati grezzi + footer BCLIM finto, per riusare bclim.decode/encode"""
    footer = b'CLIM' + struct.pack('<HHIIHH', 0xFEFF, 0x14, 0x02020000, len(raw) + 0x28, 1, 0)
    footer += b'imag' + struct.pack('<IHHI', 0x10, w, h, BCLIM_ID[fmt]) + struct.pack('<I', len(raw))
    return raw + footer[:0x28]


def decode(d, tex):
    name, w, h, fmt, off, size = tex
    return bclim.decode(_as_bclim(d[off:off + size], w, h, fmt))


def encode(img, d, tex):
    """immagine -> stessi byte (stesso formato e dimensione) da riscrivere a d[off:off+size]"""
    name, w, h, fmt, off, size = tex
    fake = _as_bclim(d[off:off + size], w, h, fmt)
    new = bclim.encode_etc(img, fake) if fmt in ('ETC1', 'ETC1A4') else bclim.encode(img, fake)
    raw = new[:-0x28]
    assert len(raw) == size, (len(raw), size)
    return raw


if __name__ == '__main__':
    if sys.argv[1] == 'dump':
        src, dst = sys.argv[2], sys.argv[3]
        os.makedirs(dst, exist_ok=True)
        n = 0
        for f in sorted(os.listdir(src)):
            d = open(os.path.join(src, f), 'rb').read()
            for t in textures(d):
                decode(d, t).save(os.path.join(dst, f'{f}__{t[0]}.png'))
                n += 1
        print(n, 'texture estratte')
