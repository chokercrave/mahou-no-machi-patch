"""BCLYT (layout 3DS): pannelli di testo (txt1) con lettura e sostituzione del testo.
txt1: header pannello (pan1, 0x4C byte da magic) poi:
  +0x4C u16 buf_len(byte)  +0x4E u16 str_len(byte)  +0x50 u16 mat  +0x52 u16 font
  +0x54 u8 origin +0x55 u8 align +0x56 u16 pad  +0x58 u32 text_off (dal magic) +0x5C colori, dimensioni font...
Il testo è UTF-16LE terminato da 0, lungo str_len (escluso il terminatore? incluso), buffer buf_len.
"""
import struct


def sections(d):
    assert d[:4] == b'CLYT', d[:4]
    hdr = struct.unpack_from('<H', d, 6)[0]
    n = struct.unpack_from('<I', d, 0x10)[0]
    o = hdr
    out = []
    for _ in range(n):
        magic = d[o:o + 4]
        size = struct.unpack_from('<I', d, o + 4)[0]
        out.append((magic, o, size))
        o += size
    return out


def move_pane(d, name, dx=0.0, dw=0.0):
    """sposta (x += dx) e allarga (w += dw) il pannello col nome dato; restituisce il nuovo blob
    (None se il pannello non c'è). pan1/txt1/pic1/wnd1: traslazione a +0x24, dimensioni a +0x44."""
    out = bytearray(d)
    hit = False
    for magic, o, size in sections(d):
        if magic in (b'pan1', b'txt1', b'pic1', b'wnd1', b'bnd1') and \
                d[o + 0x0C:o + 0x1C].split(b'\0')[0].decode('ascii', 'replace') == name:
            x = struct.unpack_from('<f', d, o + 0x24)[0]
            w = struct.unpack_from('<f', d, o + 0x44)[0]
            struct.pack_into('<f', out, o + 0x24, x + dx)
            struct.pack_into('<f', out, o + 0x44, w + dw)
            hit = True
    return bytes(out) if hit else None


def texts(d):
    """[(offset sezione, nome pannello, testo, buf_len)]"""
    res = []
    for magic, o, size in sections(d):
        if magic != b'txt1':
            continue
        name = d[o + 0x0C:o + 0x1C].split(b'\0')[0].decode('ascii', 'replace')
        buf_len, str_len = struct.unpack_from('<HH', d, o + 0x4C)
        toff = struct.unpack_from('<I', d, o + 0x58)[0]
        raw = d[o + toff:o + toff + str_len]
        res.append((o, name, raw.decode('utf-16-le', 'replace').rstrip('\0'), buf_len))
    return res


def grown(buf_len):
    """capacità allargata per i testi italiani scritti a runtime (più lunghi del giapponese)"""
    n = max(int(buf_len * 2.5), 64)
    return n + (-n % 4)


def set_texts(d, repl, grow=False):
    """repl: {nome pannello: nuovo testo}. Ricostruisce le sezioni txt1 interessate (anche più lunghe).
    grow=True: allarga il buffer di TUTTI i pannelli di testo (il gioco ci copia testi a runtime)."""
    out = bytearray(d[:struct.unpack_from('<H', d, 6)[0]])
    for magic, o, size in sections(d):
        sec = bytearray(d[o:o + size])
        if magic == b'txt1':
            name = sec[0x0C:0x1C].split(b'\0')[0].decode('ascii', 'replace')
            if name in repl or grow:
                toff = struct.unpack_from('<I', sec, 0x58)[0]
                buf_len, str_len = struct.unpack_from('<HH', sec, 0x4C)
                if name in repl:
                    new = repl[name].encode('utf-16-le') + b'\0\0'
                else:
                    new = bytes(sec[toff:toff + str_len])
                    if not new.endswith(b'\0\0'):
                        new += b'\0\0'
                tail = sec[toff + buf_len:]          # eventuali dati dopo il buffer originale
                if not tail.strip(b'\0'):
                    # sono solo i 2 byte di riempimento che allineavano la sezione a 4: il corpo nuovo
                    # e' gia' allineato, tenerli sposterebbe di 2 byte tutte le sezioni successive
                    # (crash per accesso non allineato su 3DS vera: ldm sulla posizione di un pan1)
                    tail = b''
                if grow:
                    buf_len = max(buf_len, grown(buf_len))
                # il buffer non si restringe mai: il gioco ci scrive anche testo a runtime
                body = sec[:toff] + new + b'\0' * max(0, buf_len - len(new))
                body += b'\0' * (-len(body) % 4)
                newbuf = len(body) - toff
                sec = bytearray(body + tail)
                sec += b'\0' * (-len(sec) % 4)
                struct.pack_into('<HH', sec, 0x4C, newbuf, len(new))
                struct.pack_into('<I', sec, 4, len(sec))
        out += sec
    struct.pack_into('<I', out, 0xC, len(out))
    return bytes(out)
