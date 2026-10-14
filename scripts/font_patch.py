"""Aggiunge a un BCFNT i glifi mancanti copiandoli da un BCFNT donatore con le stesse metriche.
I nuovi glifi occupano gli slot liberi dell'ultimo foglio e, se serve, fogli nuovi in coda;
CWDH viene esteso e i nuovi codici finiscono nel blocco CMAP di tipo scan (ordinato).
  python font_patch.py <dest.bcfnt> <donatore.bcfnt> <out.bcfnt> ["caratteri"]
"""
import struct, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from bcfnt import Bcfnt, encode_sheet

ITA_CHARS = 'àáèéìíòóùúÀÁÈÉÌÍÒÓÙÚçÇñÑ°«»‘’”êâôîûëïüöäÊÔ'


def from_donor(dst, donor, chars):
    """{carattere: (cella, larghezza)} copiati da un font con le stesse metriche."""
    assert (dst.cell_w, dst.cell_h, dst.sheet_fmt) == (donor.cell_w, donor.cell_h, donor.sheet_fmt)
    chars = [c for c in dict.fromkeys(chars) if ord(c) not in dst.cmap]
    missing = [c for c in chars if ord(c) not in donor.cmap]
    assert not missing, f'il donatore non ha: {"".join(missing)}'
    cache = {}
    for g in (donor.cmap[ord(c)] for c in chars):
        s = donor.cell_origin(g)[0]
        if s not in cache:
            cache[s] = donor.sheet_pixels(s)
    return {c: (donor.glyph_cell(donor.cmap[ord(c)], cache), donor.widths[donor.cmap[ord(c)]][2]) for c in chars}


def patch(dst, glyphs):
    """glyphs: {carattere: (cella come lista di righe di byte LA4, (left, glyph_w, char_w))}."""
    chars = [c for c in glyphs if ord(c) not in dst.cmap]
    d = dst.data
    gps = dst.glyphs_per_sheet()
    nglyph = len(dst.widths)
    assert sorted(dst.widths) == list(range(nglyph))
    nsheets = max(dst.nsheets, -(-(nglyph + len(chars)) // gps))

    sheets = [dst.sheet_pixels(i) for i in range(dst.nsheets)]
    sheets += [[bytearray(dst.sheet_w) for _ in range(dst.sheet_h)] for _ in range(nsheets - dst.nsheets)]
    new_widths, new_map = [], {}
    for k, c in enumerate(chars):
        cell, width = glyphs[c]
        g_dst = nglyph + k
        s, x, y = dst.cell_origin(g_dst)
        for j, row in enumerate(cell):
            sheets[s][y + j][x:x + dst.cell_w] = row
        new_widths.append(width)
        new_map[ord(c)] = g_dst

    # --- ricostruzione: header+FINF+TGLP(header) invariati fino ai dati dei fogli ---
    out = bytearray(d[:dst.sheet_data_off])
    for px in sheets:
        out += encode_sheet(px)
    tglp_start = dst.tglp_off - 8
    struct.pack_into('<I', out, tglp_start + 4, len(out) - tglp_start)
    struct.pack_into('<H', out, dst.tglp_off + 8, nsheets)
    out += b'\0' * (-len(out) % 4)

    # CWDH unico blocco 0..n-1
    widths = [dst.widths[i][2] for i in range(nglyph)] + new_widths
    cwdh_start = len(out)
    body = struct.pack('<HHI', 0, len(widths) - 1, 0) + b''.join(struct.pack('<bBB', *w) for w in widths)
    body += b'\0' * (-(len(body) + 8) % 4)
    out += b'CWDH' + struct.pack('<I', len(body) + 8) + body

    # CMAP: blocchi originali copiati, quello scan riscritto con i nuovi codici
    cmap_starts = []
    for (o, cs, ce, method) in dst.cmaps:
        start = len(out)
        cmap_starts.append(start)
        if method == 2:
            n = struct.unpack_from('<H', d, o + 12)[0]
            pairs = dict(struct.unpack_from('<HH', d, o + 14 + i * 4) for i in range(n))
            pairs.update(new_map)
            body = struct.pack('<HHHHI', cs, ce, 2, 0, 0) + struct.pack('<H', len(pairs))
            body += b''.join(struct.pack('<HH', c, g) for c, g in sorted(pairs.items()))
            body += b'\0' * (-(len(body) + 8) % 4)
        else:
            size = struct.unpack_from('<I', d, o - 4)[0]
            body = bytes(d[o:o - 8 + size])
        out += b'CMAP' + struct.pack('<I', len(body) + 8) + body
    assert any(m == 2 for *_, m in dst.cmaps)
    for i, start in enumerate(cmap_starts):
        nxt = cmap_starts[i + 1] + 8 if i + 1 < len(cmap_starts) else 0
        struct.pack_into('<I', out, start + 8 + 8, nxt)

    # FINF: puntatori CWDH/CMAP; header: dimensione file
    struct.pack_into('<I', out, dst.finf_off + 8 + 8 + 4, cwdh_start + 8)
    struct.pack_into('<I', out, dst.finf_off + 8 + 8 + 8, cmap_starts[0] + 8)
    struct.pack_into('<I', out, 0xC, len(out))
    return bytes(out), chars


def remap(data, mapping):
    """Fa disegnare a certi codici il glifo di un altro carattere (es. '<' -> glifo di 'à').
    I blocchi CMAP diretti che contengono quei codici diventano blocchi a tabella (metodo 1).
    I blocchi CMAP sono in coda al file: si tronca al primo e si riscrivono tutti."""
    f = Bcfnt(data)
    d = f.data
    target = {ord(k): f.cmap[ord(v)] for k, v in mapping.items()}
    first = min(o for o, *_ in f.cmaps) - 8
    out = bytearray(d[:first])
    starts = []
    for (o, cs, ce, method) in f.cmaps:
        starts.append(len(out))
        if method == 0 and any(cs <= c <= ce for c in target):
            base = struct.unpack_from('<H', d, o + 12)[0]
            idx = [target.get(c, base + (c - cs)) for c in range(cs, ce + 1)]
            body = struct.pack('<HHHHI', cs, ce, 1, 0, 0) + struct.pack(f'<{len(idx)}H', *idx)
        else:
            size = struct.unpack_from('<I', d, o - 4)[0]
            body = bytes(d[o:o - 8 + size])
        body += b'\0' * (-(len(body) + 8) % 4)
        out += b'CMAP' + struct.pack('<I', len(body) + 8) + body
    for i, s in enumerate(starts):
        struct.pack_into('<I', out, s + 16, starts[i + 1] + 8 if i + 1 < len(starts) else 0)
    struct.pack_into('<I', out, f.finf_off + 8 + 8 + 8, starts[0] + 8)
    struct.pack_into('<I', out, 0xC, len(out))
    chk = Bcfnt(bytes(out))
    for c, g in target.items():
        assert chk.cmap[c] == g
    return bytes(out)


def patch_and_verify(dst, glyphs, out_path):
    data, added = patch(dst, glyphs)
    chk = Bcfnt(data)
    for c in added:
        g = chk.cmap[ord(c)]
        assert chk.glyph_cell(g) == [bytes(r) for r in glyphs[c][0]]
        assert chk.widths[g][2] == glyphs[c][1]
    for c, g in dst.cmap.items():
        assert chk.cmap[c] == g
    open(out_path, 'wb').write(data)
    print(f'aggiunti {len(added)} glifi: {"".join(added)}  -> {out_path} ({len(data)} byte, {chk.nsheets} fogli)')


if __name__ == '__main__':
    dst = Bcfnt(open(sys.argv[1], 'rb').read())
    donor = Bcfnt(open(sys.argv[2], 'rb').read())
    patch_and_verify(dst, from_donor(dst, donor, sys.argv[4] if len(sys.argv) > 4 else ITA_CHARS), sys.argv[3])
