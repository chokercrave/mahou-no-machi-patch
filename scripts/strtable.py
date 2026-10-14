"""Tabelle binarie con pool di stringhe UTF-16 (MenuString.bin, GameCoinShop.bin, ItemSlotWindowMessageData.bin...).
Header (u32): 0 n_record, 1 dim_record, 2 off_pool, 3 dim_pool, 4 off_record, 5 dim_tabella,
              6 off_riloc, 7 n_riloc, 8 0, 9 ultima stringa (rel. al pool), 10 dim_pool-1, 11 0, 12 id tipo, 13 0
Rilocazioni: offset assoluti dei campi u32 che puntano (in assoluto) dentro al pool.
  python strtable.py export file.bin out.json
  python strtable.py import file.bin trad.json out.bin     (trad.json: {jp: it})
"""
import json, struct, sys


def load(d):
    h = list(struct.unpack_from('<14I', d, 0))
    relocs = list(struct.unpack_from(f'<{h[7]}I', d, h[6]))
    ptrs = {r: struct.unpack_from('<I', d, r)[0] for r in relocs}

    def s(o):
        e = o
        while d[e:e + 2] != b'\0\0':
            e += 2
        return d[o:e].decode('utf-16-le')
    return h, relocs, {r: s(p) for r, p in ptrs.items()}


def build(d, repl):
    h, relocs, strs = load(d)
    # stessa condivisione dell'originale: una stringa per ogni puntatore distinto, in ordine di offset
    orig = {r: struct.unpack_from('<I', d, r)[0] for r in relocs}
    pool, at = bytearray(), {}
    last = 0
    for p in sorted(set(orig.values())):
        r = next(r for r in relocs if orig[r] == p)
        at[p] = len(pool)
        last = len(pool)
        pool += repl.get(strs[r], strs[r]).encode('utf-16-le') + b'\0\0'
    pool += b'\0' * (h[2] + h[3] - (h[2] + len(pool))) if not repl else b''
    pool_off = h[2]
    rec_off = pool_off + len(pool)
    rec_off += -rec_off % 4
    shift = rec_off - h[4]
    table = bytearray(d[h[4]:h[4] + h[5]])
    new_relocs = []
    for r in relocs:
        assert h[4] <= r < h[4] + h[5], 'puntatore fuori dalla tabella'
        struct.pack_into('<I', table, r - h[4], pool_off + at[orig[r]])
        new_relocs.append(r + shift)
    out = bytearray(d[:pool_off]) + pool
    out += b'\0' * (rec_off - len(out))
    out += table
    gap = h[6] - (h[4] + h[5])
    out += d[h[4] + h[5]:h[6]]
    reloc_off = len(out)
    out += struct.pack(f'<{len(new_relocs)}I', *new_relocs)
    h[3], h[4], h[6], h[9], h[10] = len(pool), rec_off, reloc_off, last, len(pool) - 1
    struct.pack_into('<14I', out, 0, *h)
    return bytes(out)


if __name__ == '__main__':
    cmd, src = sys.argv[1], sys.argv[2]
    d = open(src, 'rb').read()
    if cmd == 'export':
        _, relocs, strs = load(d)
        uniq = list(dict.fromkeys(strs[r] for r in relocs))
        json.dump({s: '' for s in uniq}, open(sys.argv[3], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(len(uniq), 'stringhe')
    elif cmd == 'import':
        repl = {k: v for k, v in json.load(open(sys.argv[3], encoding='utf-8')).items() if v}
        out = build(d, repl)
        assert load(out)[2] == {r + 0: v for r, v in load(out)[2].items()}
        open(sys.argv[4], 'wb').write(out)
        print('ok', len(out))
