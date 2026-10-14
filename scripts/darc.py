"""Archivi DARC (.arc) dei layout 3DS: lettura e ricostruzione.
Header: 'darc' u16 bom u16 hdr(0x1C) u32 ver u32 filesize u32 tbl_off u32 tbl_len u32 data_off
Tabella: nodi da 12 byte (u32 nome|flag dir, u32 offset/parent, u32 size/next), poi nomi UTF-16.
"""
import struct


def parse(d):
    assert d[:4] == b'darc'
    tbl_off, tbl_len, data_off = struct.unpack_from('<III', d, 0x10)
    root_n = struct.unpack_from('<III', d, tbl_off)[2]
    names_off = tbl_off + root_n * 12
    nodes = []
    for i in range(root_n):
        a, b, c = struct.unpack_from('<III', d, tbl_off + i * 12)
        is_dir = bool(a & 0x01000000)
        no = names_off + (a & 0xFFFFFF)
        end = no
        while d[end:end + 2] != b'\0\0':
            end += 2
        nodes.append(dict(idx=i, dir=is_dir, name=d[no:end].decode('utf-16-le'), off=b, size=c))
    # percorsi completi
    path, stack = [], []
    files = []
    for n in nodes:
        while stack and n['idx'] >= stack[-1][1]:
            stack.pop()
        if n['dir']:
            stack.append((n['name'], n['size']))
        else:
            p = '/'.join(s[0] for s in stack if s[0] not in ('', '.')) + '/' + n['name']
            files.append(dict(n, path=p.lstrip('/')))
    return nodes, files


def read_files(d):
    _, files = parse(d)
    return {f['path']: d[f['off']:f['off'] + f['size']] for f in files}


def rebuild(d, repl):
    """Ricostruisce l'archivio sostituendo {percorso: bytes}; tabella e nomi invariati."""
    tbl_off, tbl_len, data_off = struct.unpack_from('<III', d, 0x10)
    nodes, files = parse(d)
    by_idx = {f['idx']: f for f in files}
    order = sorted(files, key=lambda f: f['off'])
    out = bytearray(d[:data_off])
    for f in order:
        blob = repl.get(f['path'], d[f['off']:f['off'] + f['size']])
        out += b'\0' * (-len(out) % 0x80 if f['path'].endswith(('.bclim', '.bcfnt')) else -len(out) % 4)
        struct.pack_into('<III', out, tbl_off + f['idx'] * 12,
                         struct.unpack_from('<I', d, tbl_off + f['idx'] * 12)[0], len(out), len(blob))
        out += blob
    struct.pack_into('<I', out, 0xC, len(out))
    return bytes(out)
