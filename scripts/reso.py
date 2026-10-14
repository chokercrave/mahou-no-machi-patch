"""Parser / serializzatore per i testi RESO (.rdbt + .rndx) di Tongari Boushi 3DS.

.rndx : array di (u32 id, u32 offset, u32 size) -> blocchi RESO dentro .rdbt
RESO  : 'RESO', u32 n_slot, '1.21', u32 1, (u32 size, u32 offset)[n_slot], dati allineati 0x10
Slot  : testo UTF-16LE.  Codici di controllo:  '$' arg ('\\'' arg)* ';'
        con arg = 0x8000 + numero.

Rappresentazione testuale (lossless):
  [$24'7026'0]  codice di controllo (numeri decimali; 'uXXXX' se arg < 0x8000)
  [#XXXX]       unita' UTF-16 non stampabile (es. [#0000] terminatore)
  [[            '[' letterale
"""
import json, struct, sys

HDR_MAGIC = b'RESO'


def align(n, a=0x10):
    return (n + a - 1) & ~(a - 1)


# ---------- testo <-> unita' UTF-16 ----------

def units_to_text(units):
    out, i, n = [], 0, len(units)
    while i < n:
        u = units[i]
        if u == 0x24:  # '$'
            j = i + 1
            while j < n and units[j] != 0x3B:
                j += 1
            if j < n:
                args, cur = [], []
                for a in units[i + 1:j]:
                    if a == 0x27:
                        args.append(cur); cur = []
                    else:
                        cur.append(a)
                args.append(cur)
                parts = ['+'.join(str(a - 0x8000) if a >= 0x8000 else f'u{a:04X}' for a in arg)
                         for arg in args]
                out.append('[$' + "'".join(parts) + ']')
                i = j + 1
                continue
        if u == 0x5B:
            out.append('[[')
        elif u < 0x20 or 0xD800 <= u < 0xE000 or u >= 0xE000 and u < 0xF900:
            out.append(f'[#{u:04X}]')
        else:
            out.append(chr(u))
        i += 1
    return ''.join(out)


def _arg_units(tok):
    res = []
    for t in tok.split('+') if tok else []:
        res.append(int(t[1:], 16) if t.startswith('u') else 0x8000 + int(t))
    return res


def text_to_units(s):
    units, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c == '[':
            if s.startswith('[[', i):
                units.append(0x5B); i += 2; continue
            j = s.index(']', i)
            body = s[i + 1:j]
            if body.startswith('#'):
                units.append(int(body[1:], 16))
            elif body.startswith('$'):
                units.append(0x24)
                for k, tok in enumerate(body[1:].split("'")):
                    if k:
                        units.append(0x27)
                    units += _arg_units(tok)
                units.append(0x3B)
            else:
                raise ValueError(f'token sconosciuto [{body}]')
            i = j + 1
            continue
        units.append(ord(c))
        i += 1
    return units


# ---------- RESO ----------

def parse_reso(b):
    assert b[:4] == HDR_MAGIC, b[:4]
    n = struct.unpack_from('<I', b, 4)[0]
    slots = []
    for k in range(n):
        size, off = struct.unpack_from('<II', b, 0x10 + k * 8)
        if size == 0 and off == 0:
            slots.append(None); continue
        raw = b[off:off + size]
        slots.append(units_to_text(struct.unpack(f'<{size // 2}H', raw)))
    return dict(head=b[8:0x10].hex(), slots=slots)


def build_reso(r):
    slots = r['slots']
    n = len(slots)
    table = bytearray()
    data = bytearray()
    base = align(0x10 + n * 8)
    seen = {}  # testi identici condividono lo stesso offset, come nell'originale
    for s in slots:
        if s is None:
            table += struct.pack('<II', 0, 0); continue
        u = text_to_units(s)
        raw = struct.pack(f'<{len(u)}H', *u)
        if raw not in seen:
            seen[raw] = base + len(data)
            data += raw
            data += b'\0' * (align(len(data)) - len(data))
        table += struct.pack('<II', len(raw), seen[raw])
    out = HDR_MAGIC + struct.pack('<I', n) + bytes.fromhex(r['head']) + table
    out += b'\0' * (base - len(out))
    return bytes(out + data)


# ---------- rdbt + rndx ----------

def load(rdbt_path, rndx_path):
    d = open(rdbt_path, 'rb').read()
    x = open(rndx_path, 'rb').read()
    groups = []
    for i in range(len(x) // 12):
        gid, off, size = struct.unpack_from('<3I', x, i * 12)
        blob = d[off:off + size]
        if blob[:4] == HDR_MAGIC:
            groups.append(dict(id=gid, **parse_reso(blob)))
        else:  # voce piatta (es. onemsg): una sola stringa UTF-16
            groups.append(dict(id=gid, text=units_to_text(struct.unpack(f'<{size // 2}H', blob))))
    return groups


def save(groups, rdbt_path, rndx_path):
    d, x = bytearray(), bytearray()
    for g in groups:
        if 'text' in g:
            u = text_to_units(g['text'])
            blob = struct.pack(f'<{len(u)}H', *u)
        else:
            blob = build_reso(g)
        x += struct.pack('<3I', g['id'], len(d), len(blob))
        d += blob
    open(rdbt_path, 'wb').write(d)
    open(rndx_path, 'wb').write(x)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'export':    # reso.py export file.rdbt file.rndx out.json
        g = load(sys.argv[2], sys.argv[3])
        json.dump(g, open(sys.argv[4], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'{len(g)} gruppi, {sum(1 if "text" in x else sum(s is not None for s in x["slots"]) for x in g)} messaggi')
    elif cmd == 'import':  # reso.py import in.json out.rdbt out.rndx
        save(json.load(open(sys.argv[2], encoding='utf-8')), sys.argv[3], sys.argv[4])
