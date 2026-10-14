"""Parser BCFNT (font 3DS): header, TGLP (fogli glifi), CWDH (larghezze), CMAP (codice -> indice glifo).
  python bcfnt.py info <file.bcfnt>
"""
import struct, sys


class Bcfnt:
    def __init__(self, data):
        self.data = bytearray(data)
        d = self.data
        assert d[:4] == b'CFNT', d[:4]
        self.bom, self.hdr_size, self.version, self.file_size, self.nblocks = struct.unpack_from('<HHIII', d, 4)
        # FINF
        fo = self.hdr_size
        assert d[fo:fo + 4] == b'FINF'
        (_, self.font_type, self.line_feed, self.alter_idx, dl, dw, dcw, self.encoding,
         self.tglp_off, self.cwdh_off, self.cmap_off, self.height, self.width, self.ascent, _) = \
            struct.unpack_from('<IBBHbBBBIIIBBBB', d, fo + 4)
        self.default_width = (dl, dw, dcw)
        self.finf_off = fo
        # TGLP (offset punta ai dati dopo il magic+size)
        t = self.tglp_off
        (self.cell_w, self.cell_h, self.baseline, self.max_cw, self.sheet_size, self.nsheets,
         self.sheet_fmt, self.ncols, self.nrows, self.sheet_w, self.sheet_h, self.sheet_data_off) = \
            struct.unpack_from('<BBBBIHHHHHHI', d, t)
        # CWDH (catena)
        self.widths = {}
        o = self.cwdh_off
        while o:
            start, end, nxt = struct.unpack_from('<HHI', d, o)
            for i in range(start, end + 1):
                b = o + 8 + (i - start) * 3
                self.widths[i] = (o, b, struct.unpack_from('<bBB', d, b))
            o = nxt
        # CMAP (catena)
        self.cmap = {}
        self.cmaps = []
        o = self.cmap_off
        while o:
            cs, ce, method, _, nxt = struct.unpack_from('<HHHHI', d, o)
            self.cmaps.append((o, cs, ce, method))
            p = o + 12
            if method == 0:  # direct
                base = struct.unpack_from('<H', d, p)[0]
                for c in range(cs, ce + 1):
                    self.cmap[c] = base + (c - cs)
            elif method == 1:  # table
                for c in range(cs, ce + 1):
                    g = struct.unpack_from('<H', d, p + (c - cs) * 2)[0]
                    if g != 0xFFFF:
                        self.cmap[c] = g
            elif method == 2:  # scan
                n = struct.unpack_from('<H', d, p)[0]
                for i in range(n):
                    c, g = struct.unpack_from('<HH', d, p + 2 + i * 4)
                    self.cmap[c] = g
            o = nxt

    def glyphs_per_sheet(self):
        return self.ncols * self.nrows

    # --- fogli: LA4 (fmt 9), 1 byte/pixel, tile 8x8 in ordine Morton ---
    def sheet_pixels(self, i):
        """Foglio i come lista di righe di byte LA4 (alto nibble = L, basso = A)."""
        assert self.sheet_fmt == 9
        w, h = self.sheet_w, self.sheet_h
        raw = self.data[self.sheet_data_off + i * self.sheet_size:][:self.sheet_size]
        px = [bytearray(w) for _ in range(h)]
        for (x, y), v in zip(_tiled_order(w, h), raw):
            px[y][x] = v
        return px

    def cell_origin(self, glyph):
        """Angolo in alto a sinistra della cella del glifo (bordo di 1px tra celle)."""
        s, k = divmod(glyph, self.glyphs_per_sheet())
        r, c = divmod(k, self.ncols)
        return s, c * (self.cell_w + 1) + 1, r * (self.cell_h + 1) + 1

    def glyph_cell(self, glyph, cache=None):
        s, x, y = self.cell_origin(glyph)
        px = cache[s] if cache is not None else self.sheet_pixels(s)
        return [bytes(px[y + j][x:x + self.cell_w]) for j in range(self.cell_h)]


def _tiled_order(w, h):
    order = []
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for i in range(64):
                x = (i & 1) | ((i >> 1) & 2) | ((i >> 2) & 4)
                y = ((i >> 1) & 1) | ((i >> 2) & 2) | ((i >> 3) & 4)
                order.append((tx + x, ty + y))
    return order


def encode_sheet(px):
    h, w = len(px), len(px[0])
    return bytes(px[y][x] for x, y in _tiled_order(w, h))

    def info(self):
        return (f'type={self.font_type} enc={self.encoding} height={self.height} width={self.width} '
                f'ascent={self.ascent} linefeed={self.line_feed}\n'
                f'cell={self.cell_w}x{self.cell_h} baseline={self.baseline} maxcw={self.max_cw} '
                f'sheets={self.nsheets} fmt={self.sheet_fmt} grid={self.ncols}x{self.nrows} '
                f'sheet={self.sheet_w}x{self.sheet_h} size={self.sheet_size} data@{self.sheet_data_off:#x}\n'
                f'glifi mappati={len(self.cmap)} cmap blocks={[(hex(a), hex(b), hex(c), m) for a, b, c, m in self.cmaps]}')


if __name__ == '__main__':
    f = Bcfnt(open(sys.argv[2], 'rb').read())
    print(f.info())
    test = 'àèéìòùÀÈÉÌÒÙ\'"!?.,:;-…«»'
    print('presenti:', ''.join(c for c in test if ord(c) in f.cmap))
    print('mancanti:', ''.join(c for c in test if ord(c) not in f.cmap))
    latin = [c for c in f.cmap if 0x20 <= c < 0x250]
    print('latini:', ''.join(chr(c) for c in sorted(latin)))
