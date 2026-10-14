"""BCLIM (texture layout 3DS) <-> PNG.
Footer (ultimi 0x28 byte): 'CLIM' header 0x14 + 'imag' 0x14: u16 w, u16 h, u32 formato, u32 dim dati.
Dati a tile 8x8 Morton; ETC1/ETC1A4 a blocchi 4x4 dentro tile 8x8. Righe dall'alto.
  python bclim.py topng in.bclim out.png
  python bclim.py frompng in.bclim(originale) in.png out.bclim
"""
import struct, sys
from PIL import Image

FMT = {0: 'L8', 1: 'A8', 2: 'LA4', 3: 'LA8', 4: 'HILO8', 5: 'RGB565', 6: 'RGB8', 7: 'RGBA5551',
       8: 'RGBA4', 9: 'RGBA8', 10: 'ETC1', 11: 'ETC1A4', 12: 'L4', 13: 'A4'}
BPP = {'L8': 8, 'A8': 8, 'LA4': 8, 'LA8': 16, 'HILO8': 16, 'RGB565': 16, 'RGB8': 24, 'RGBA5551': 16,
       'RGBA4': 16, 'RGBA8': 32, 'ETC1': 4, 'ETC1A4': 8, 'L4': 4, 'A4': 4}


def info(d):
    f = d[-0x28:]
    assert f[:4] == b'CLIM', f[:4]
    w, h, fmt = struct.unpack_from('<HHI', f, 0x14 + 8)
    return w, h, FMT[fmt]


def _pot(n):
    p = 8
    while p < n:
        p *= 2
    return p


def _morton(i):
    x = (i & 1) | ((i >> 1) & 2) | ((i >> 2) & 4)
    y = ((i >> 1) & 1) | ((i >> 2) & 2) | ((i >> 3) & 4)
    return x, y


MORTON = [_morton(i) for i in range(64)]
ETC_MOD = [[2, 8, -2, -8], [5, 17, -5, -17], [9, 29, -9, -29], [13, 42, -13, -42],
           [18, 60, -18, -60], [24, 80, -24, -80], [33, 106, -33, -106], [47, 183, -47, -183]]


def _clamp(v):
    return 0 if v < 0 else 255 if v > 255 else v


def _etc1_block(blk):
    """8 byte (u64 little endian) -> 16 pixel RGB, indice [x][y]"""
    v = struct.unpack('<Q', blk)[0]
    hi = v >> 32
    lo = v & 0xFFFFFFFF
    diff = (hi >> 1) & 1
    flip = hi & 1
    if diff:
        def c5(sh):
            return (hi >> sh) & 0x1F

        def d3(sh):
            t = (hi >> sh) & 7
            return t - 8 if t >= 4 else t
        r1, g1, b1 = c5(27), c5(19), c5(11)
        r2, g2, b2 = r1 + d3(24), g1 + d3(16), b1 + d3(8)
        ext = lambda c: (c << 3) | (c >> 2)
        base = [(ext(r1), ext(g1), ext(b1)), (ext(r2 & 31), ext(g2 & 31), ext(b2 & 31))]
    else:
        e4 = lambda c: (c << 4) | c
        base = [(e4((hi >> 28) & 15), e4((hi >> 20) & 15), e4((hi >> 12) & 15)),
                (e4((hi >> 24) & 15), e4((hi >> 16) & 15), e4((hi >> 8) & 15))]
    tables = [(hi >> 5) & 7, (hi >> 2) & 7]
    px = {}
    for x in range(4):
        for y in range(4):
            i = x * 4 + y
            sub = (y >= 2) if flip else (x >= 2)
            idx = ((lo >> i) & 1) | (((lo >> (i + 16)) & 1) << 1)
            m = ETC_MOD[tables[sub]][idx]
            r, g, b = base[sub]
            px[(x, y)] = (_clamp(r + m), _clamp(g + m), _clamp(b + m))
    return px


def decode(d):
    w, h, fmt = info(d)
    pw, ph = _pot(w), _pot(h)
    img = Image.new('RGBA', (pw, ph))
    put = img.load()
    pos = 0
    for ty in range(0, ph, 8):
        for tx in range(0, pw, 8):
            if fmt in ('ETC1', 'ETC1A4'):
                for by in (0, 4):
                    for bx in (0, 4):
                        alpha = None
                        if fmt == 'ETC1A4':
                            alpha = struct.unpack('<Q', d[pos:pos + 8])[0]; pos += 8
                        px = _etc1_block(d[pos:pos + 8]); pos += 8
                        for (x, y), (r, g, b) in px.items():
                            a = 255
                            if alpha is not None:
                                a = ((alpha >> ((x * 4 + y) * 4)) & 0xF) * 17
                            put[tx + bx + x, ty + by + y] = (r, g, b, a)
                continue
            for i in range(64):
                x, y = MORTON[i]
                if fmt == 'RGBA8':
                    a, b, g, r = d[pos:pos + 4]; pos += 4
                elif fmt == 'RGB8':
                    b, g, r = d[pos:pos + 3]; a = 255; pos += 3
                elif fmt == 'RGBA5551':
                    v = struct.unpack_from('<H', d, pos)[0]; pos += 2
                    r, g, b = ((v >> 11) & 31) * 255 // 31, ((v >> 6) & 31) * 255 // 31, ((v >> 1) & 31) * 255 // 31
                    a = 255 if v & 1 else 0
                elif fmt == 'RGB565':
                    v = struct.unpack_from('<H', d, pos)[0]; pos += 2
                    r, g, b, a = ((v >> 11) & 31) * 255 // 31, ((v >> 5) & 63) * 255 // 63, (v & 31) * 255 // 31, 255
                elif fmt == 'RGBA4':
                    v = struct.unpack_from('<H', d, pos)[0]; pos += 2
                    r, g, b, a = ((v >> 12) & 15) * 17, ((v >> 8) & 15) * 17, ((v >> 4) & 15) * 17, (v & 15) * 17
                elif fmt == 'LA8':
                    a, l = d[pos:pos + 2]; r = g = b = l; pos += 2
                elif fmt == 'HILO8':
                    g, r = d[pos:pos + 2]; b = 0; a = 255; pos += 2
                elif fmt == 'L8':
                    r = g = b = d[pos]; a = 255; pos += 1
                elif fmt == 'A8':
                    r = g = b = 255; a = d[pos]; pos += 1
                elif fmt == 'LA4':
                    v = d[pos]; pos += 1; r = g = b = (v >> 4) * 17; a = (v & 15) * 17
                elif fmt in ('L4', 'A4'):
                    v = d[pos + i // 2]
                    n = (v >> 4) if i & 1 else (v & 15)
                    if fmt == 'L4':
                        r = g = b = n * 17; a = 255
                    else:
                        r = g = b = 255; a = n * 17
                    if i == 63:
                        pos += 32
                put[tx + x, ty + y] = (r, g, b, a)
    return img.crop((0, 0, w, h))


def encode_as(img, d_orig, fmt='RGBA8'):
    """Ricodifica con le dimensioni dell'originale ma nel formato indicato (es. per sostituire un ETC1)."""
    w, h, _ = info(d_orig)
    code = {v: k for k, v in FMT.items()}[fmt]
    pw, ph = _pot(w), _pot(h)
    data_len = pw * ph * BPP[fmt] // 8
    foot = bytearray(d_orig[-0x28:])
    struct.pack_into('<I', foot, 0x14 + 0x0C, code)
    struct.pack_into('<I', foot, 0x14 + 0x10, data_len)
    struct.pack_into('<I', foot, 0x0C, data_len + 0x28)
    fake = bytes(data_len) + bytes(foot)
    return encode(img, fake)


def encode(img, d_orig):
    """Ricodifica con formato e dimensioni dell'originale (formati non ETC)."""
    w, h, fmt = info(d_orig)
    assert fmt not in ('ETC1', 'ETC1A4'), 'ETC non supportato in scrittura: usa encode_as(..., "RGBA8")'
    pw, ph = _pot(w), _pot(h)
    src = Image.new('RGBA', (pw, ph))
    src.paste(img.convert('RGBA').crop((0, 0, w, h)), (0, 0))
    px = src.load()
    out = bytearray()
    for ty in range(0, ph, 8):
        for tx in range(0, pw, 8):
            nib = []
            for i in range(64):
                x, y = MORTON[i]
                r, g, b, a = px[tx + x, ty + y]
                l = (r * 77 + g * 151 + b * 28) >> 8
                if fmt == 'RGBA8':
                    out += bytes((a, b, g, r))
                elif fmt == 'RGB8':
                    out += bytes((b, g, r))
                elif fmt == 'RGBA5551':
                    out += struct.pack('<H', ((r >> 3) << 11) | ((g >> 3) << 6) | ((b >> 3) << 1) | (1 if a >= 128 else 0))
                elif fmt == 'RGB565':
                    out += struct.pack('<H', ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3))
                elif fmt == 'RGBA4':
                    out += struct.pack('<H', ((r >> 4) << 12) | ((g >> 4) << 8) | ((b >> 4) << 4) | (a >> 4))
                elif fmt == 'LA8':
                    out += bytes((a, l))
                elif fmt == 'L8':
                    out += bytes((l,))
                elif fmt == 'A8':
                    out += bytes((a,))
                elif fmt == 'LA4':
                    out += bytes(((l >> 4) << 4 | (a >> 4),))
                elif fmt in ('L4', 'A4'):
                    nib.append((l if fmt == 'L4' else a) >> 4)
            if nib:
                out += bytes(nib[k] | (nib[k + 1] << 4) for k in range(0, 64, 2))
    data_len = len(d_orig) - 0x28
    assert len(out) == data_len, (len(out), data_len)
    return bytes(out) + d_orig[-0x28:]


if __name__ == '__main__':
    if sys.argv[1] == 'topng':
        decode(open(sys.argv[2], 'rb').read()).save(sys.argv[3])
    elif sys.argv[1] == 'frompng':
        d = open(sys.argv[2], 'rb').read()
        open(sys.argv[4], 'wb').write(encode(Image.open(sys.argv[3]), d))


# ---------------------------------------------------------------------------
# Codifica ETC1 / ETC1A4: mantiene formato e dimensione dell'originale.
# Convertire un ETC1A4 in RGBA4 raddoppia la texture e fa crescere l'archivio
# decompresso: alcuni menu (es. menu Start, status.arc) hanno un buffer fisso
# e con la texture più grande il layout non viene caricato (UI invisibile).

def _etc_half_error(pix, base, table):
    """errore e indici migliori per una metà blocco con colore base e tabella dati"""
    err, idxs = 0, []
    mods = ETC_MOD[table]
    for (r, g, b) in pix:
        best, bi = None, 0
        for k, m in enumerate(mods):
            e = (_clamp(base[0] + m) - r) ** 2 + (_clamp(base[1] + m) - g) ** 2 + (_clamp(base[2] + m) - b) ** 2
            if best is None or e < best:
                best, bi = e, k
        err += best; idxs.append(bi)
    return err, idxs


def _etc_best_table(pix, base):
    best = None
    for t in range(8):
        e, idx = _etc_half_error(pix, base, t)
        if best is None or e < best[0]:
            best = (e, t, idx)
    return best


def _etc1_encode_block(px):
    """px[(x, y)] = (r, g, b) -> 8 byte ETC1 (u64 little endian)"""
    best = None
    for flip in (0, 1):
        halves = [[], []]
        coords = [[], []]
        for x in range(4):
            for y in range(4):
                s = (y >= 2) if flip else (x >= 2)
                halves[s].append(px[(x, y)]); coords[s].append((x, y))
        avg = [tuple(sum(c[i] for c in h) / len(h) for i in range(3)) for h in halves]
        cands = []
        # modo differenziale (5 bit + delta 3 bit)
        q5 = [tuple(int(round(v * 31 / 255)) for v in a) for a in avg]
        d = [q5[1][i] - q5[0][i] for i in range(3)]
        if all(-4 <= v <= 3 for v in d):
            ext = lambda c: (c << 3) | (c >> 2)
            bases = [tuple(ext(v) for v in q5[0]), tuple(ext(v) for v in q5[1])]
            cands.append((1, q5, d, bases))
        # modo individuale (4 bit per metà)
        q4 = [tuple(int(round(v * 15 / 255)) for v in a) for a in avg]
        bases4 = [tuple((v << 4) | v for v in q) for q in q4]
        cands.append((0, q4, None, bases4))
        for diff, q, dd, bases in cands:
            r0 = _etc_best_table(halves[0], bases[0])
            r1 = _etc_best_table(halves[1], bases[1])
            err = r0[0] + r1[0]
            if best is None or err < best[0]:
                best = (err, flip, diff, q, dd, (r0, r1), coords)
    err, flip, diff, q, dd, (r0, r1), coords = best
    hi = 0
    if diff:
        hi |= (q[0][0] << 27) | ((dd[0] & 7) << 24) | (q[0][1] << 19) | ((dd[1] & 7) << 16) | (q[0][2] << 11) | ((dd[2] & 7) << 8)
    else:
        hi |= (q[0][0] << 28) | (q[1][0] << 24) | (q[0][1] << 20) | (q[1][1] << 16) | (q[0][2] << 12) | (q[1][2] << 8)
    hi |= (r0[1] << 5) | (r1[1] << 2) | (diff << 1) | flip
    lo = 0
    for s, r in ((0, r0), (1, r1)):
        for (x, y), k in zip(coords[s], r[2]):
            i = x * 4 + y
            lo |= (k & 1) << i
            lo |= ((k >> 1) & 1) << (i + 16)
    return struct.pack('<Q', (hi << 32) | lo)


def encode_etc(img, d_orig):
    """Ricodifica in ETC1/ETC1A4 con le dimensioni dell'originale (stessa lunghezza dati)."""
    w, h, fmt = info(d_orig)
    assert fmt in ('ETC1', 'ETC1A4'), fmt
    pw, ph = _pot(w), _pot(h)
    src = Image.new('RGBA', (pw, ph))
    src.paste(img.convert('RGBA').crop((0, 0, w, h)), (0, 0))
    p = src.load()
    out = bytearray()
    for ty in range(0, ph, 8):
        for tx in range(0, pw, 8):
            for by in (0, 4):
                for bx in (0, 4):
                    blk = {}
                    alpha = 0
                    for x in range(4):
                        for y in range(4):
                            r, g, b, a = p[tx + bx + x, ty + by + y]
                            blk[(x, y)] = (r, g, b)
                            alpha |= ((a * 15 + 127) // 255) << ((x * 4 + y) * 4)
                    if fmt == 'ETC1A4':
                        out += struct.pack('<Q', alpha)
                    out += _etc1_encode_block(blk)
    data_len = len(d_orig) - 0x28
    assert len(out) == data_len, (len(out), data_len)
    return bytes(out) + d_orig[-0x28:]
