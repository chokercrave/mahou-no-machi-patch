"""Estrattore archivi TBAF (.tarc) di Tongari Boushi to Mahou no Machi (3DS).

Header (little endian):
  0x00 'TBAF'  0x04 u32 size   0x08 u32 ?(4)  0x0C u32 ?(1)
  0x10 u32 ?   0x14 u32 entry_table_off   0x18 u32 ?   0x1C u32 name_table_off
  0x20 u32 name_table_size
Entry (0x20 byte): u32 id/hash, u32 name_off, u32 data_off,
  u32 raw_size, u32 stored_size, u32 compressed (1 = LZ11)
"""
import os, struct, sys
from ndspy import lz10


def lz11_decompress(data):
    # ndspy supporta solo LZ10; implementazione LZ11 minimale
    assert data[0] == 0x11
    size = int.from_bytes(data[1:4], 'little')
    pos = 4
    if size == 0:
        size = int.from_bytes(data[4:8], 'little'); pos = 8
    out = bytearray()
    while len(out) < size:
        flags = data[pos]; pos += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if not (flags & (0x80 >> bit)):
                out.append(data[pos]); pos += 1
                continue
            b0 = data[pos]; ind = b0 >> 4
            if ind == 0:
                length = (((b0 & 0xF) << 4) | (data[pos+1] >> 4)) + 0x11
                disp = ((data[pos+1] & 0xF) << 8) | data[pos+2]; pos += 3
            elif ind == 1:
                length = (((b0 & 0xF) << 12) | (data[pos+1] << 4) | (data[pos+2] >> 4)) + 0x111
                disp = ((data[pos+2] & 0xF) << 8) | data[pos+3]; pos += 4
            else:
                length = ind + 1
                disp = ((b0 & 0xF) << 8) | data[pos+1]; pos += 2
            start = len(out) - disp - 1
            for i in range(length):
                out.append(out[start + i])
    return bytes(out)


def lz11_compress(data, chain=24):
    """LZ11 greedy con catene hash (finestra 4 KB). Tutti i file originali dei tarc sono LZ11:
    rimetterli compressi evita archivi 4x più grandi (il gioco li carica in buffer di dimensione fissa)."""
    n = len(data)
    out = bytearray(b'\x11' + n.to_bytes(3, 'little') if n < 0x1000000 else b'\x11\0\0\0' + n.to_bytes(4, 'little'))
    head, prev = {}, [0] * n
    pos = 0
    while pos < n:
        flag_at = len(out); out.append(0); flags = 0
        for bit in range(8):
            if pos >= n:
                break
            best_len = best_disp = 0
            if pos + 3 <= n:
                key = data[pos:pos + 3]
                cand = head.get(key, -1); tries = chain
                maxl = min(0x10110, n - pos)
                while cand >= 0 and pos - cand <= 0x1000 and tries:
                    if data[cand + best_len:cand + best_len + 1] == data[pos + best_len:pos + best_len + 1]:
                        l = 3
                        while l < maxl and data[cand + l] == data[pos + l]:
                            l += 1
                        if l > best_len:
                            best_len, best_disp = l, pos - cand - 1
                            if l == maxl:
                                break
                    cand = prev[cand]; tries -= 1
            step = best_len if best_len >= 3 else 1
            for p in range(pos, min(pos + step, n - 2)):     # aggiorna le catene per i byte consumati
                k = data[p:p + 3]
                prev[p] = head.get(k, -1); head[k] = p
            if best_len >= 3:
                flags |= 0x80 >> bit
                d = best_disp
                if best_len <= 0x10:
                    out += bytes((((best_len - 1) << 4) | (d >> 8), d & 0xFF))
                elif best_len <= 0x110:
                    l = best_len - 0x11
                    out += bytes((l >> 4, ((l & 0xF) << 4) | (d >> 8), d & 0xFF))
                else:
                    l = best_len - 0x111
                    out += bytes((0x10 | (l >> 12), (l >> 4) & 0xFF, ((l & 0xF) << 4) | (d >> 8), d & 0xFF))
                pos += best_len
            else:
                out.append(data[pos]); pos += 1
        out[flag_at] = flags
    return bytes(out)


def decompress(data):
    if data[0] == 0x11:
        return lz11_decompress(data)
    if data[0] == 0x10:
        return lz10.decompress(data)
    raise ValueError(f'compressione sconosciuta 0x{data[0]:02X}')


def _count(data):
    """numero di voci; variante senza tabella dei nomi (name_off = 0): conteggio nell'header"""
    ent_off = struct.unpack_from('<I', data, 0x14)[0]
    name_off = struct.unpack_from('<I', data, 0x1C)[0]
    if name_off == 0:
        return ent_off, struct.unpack_from('<I', data, 0x08)[0]
    return ent_off, (name_off - ent_off) // 0x20


def parse(data):
    assert data[:4] == b'TBAF', 'non TBAF'
    ent_off, n = _count(data)
    entries = []
    for i in range(n):
        eid, noff, doff, raw, stored, comp = struct.unpack_from('<6I', data, ent_off + i * 0x20)
        if noff == 0 and doff == 0:
            continue
        name = data[noff:data.index(b'\0', noff)].decode('ascii', 'replace') if noff else f'{i:03d}.bin'
        blob = data[doff:doff + stored]
        entries.append(dict(id=eid, name=name, raw=raw, stored=stored, comp=comp, data=blob))
    return entries


def rebuild(path, replacements, out_path):
    """Ricostruisce un TBAF sostituendo {nome: bytes}. I file sostituiti sono ricompressi in LZ11
    come gli originali (comp=1); se la compressione non conviene restano non compressi (comp=0)."""
    data = bytearray(open(path, 'rb').read())
    ent_off, n = _count(data)
    entries = []
    for i in range(n):
        f = list(struct.unpack_from('<8I', data, ent_off + i * 0x20))
        if f[1] == 0 and f[2] == 0:
            entries.append((f, None)); continue
        name = data[f[1]:data.index(b'\0', f[1])].decode('ascii') if f[1] else f'{i:03d}.bin'
        blob = replacements.get(name, bytes(data[f[2]:f[2] + f[4]]))
        if name in replacements:
            # si rispetta lo stato originale: alcuni file sono non compressi apposta (letti così dal gioco)
            raw = blob
            if f[5]:
                z = lz11_compress(raw)
                blob = z if len(z) < len(raw) else raw
            f[3], f[4], f[5] = len(raw), len(blob), int(len(blob) != len(raw) or (f[5] and blob is not raw))
        entries.append((f, blob))
    first = min(f[2] for f, b in entries if b is not None)
    out = bytearray(data[:first])
    for i, (f, blob) in enumerate(entries):
        if blob is None:
            continue
        out += b'\0' * ((-len(out)) % 0x10)
        f[2] = len(out)
        out += blob
        struct.pack_into('<8I', out, ent_off + i * 0x20, *f)
    struct.pack_into('<I', out, 4, len(out))
    open(out_path, 'wb').write(out)


def extract(path, outdir):
    data = open(path, 'rb').read()
    os.makedirs(outdir, exist_ok=True)
    for e in parse(data):
        blob = decompress(e['data']) if e['comp'] else e['data']
        if len(blob) != e['raw']:
            print(f'  ! {e["name"]}: size {len(blob)} != {e["raw"]}')
        open(os.path.join(outdir, e['name']), 'wb').write(blob)
        # archivi annidati
        if blob[:4] == b'TBAF':
            extract(os.path.join(outdir, e['name']), os.path.join(outdir, e['name'] + '_x'))


if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    for root, _, files in os.walk(src):
        for f in files:
            if f.endswith('.tarc'):
                p = os.path.join(root, f)
                rel = os.path.relpath(p, src)
                try:
                    extract(p, os.path.join(dst, rel + '_x'))
                except Exception as ex:
                    print('ERRORE', rel, ex)
