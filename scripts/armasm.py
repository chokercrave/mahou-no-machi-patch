"""Mini assemblatore ARM (ARMv6K, modalità ARM) per le poche istruzioni delle patch del codice.
Ogni word prodotta va verificata con capstone (asm() lo fa da sé e confronta col testo atteso).

Sintassi supportata (minuscole, registri r0-r12/sp/lr/pc, suffissi di condizione):
  mov/mvn/add/sub/rsb/and/orr/bic/cmp/cmn/tst{cc}{s} rd, rn, #imm | rm[, lsl|lsr|asr #n]
  ldr/str/ldrb/strb/ldrh/strh{cc} rd, [rn, #imm] | [rn], #imm (post) | [rn, rm] ;  ldr rd, =valore
  push/pop {reglist} ; b/bl{cc} etichetta|indirizzo ; vmov sN, rM ; vcvt.f32.s32 sD, sM ; vstr sD, [rn, #imm]
  etichette 'nome:' ; '.word v' ; '.bytes b0,b1,...' ; '.align' ; '.pool' (letterali di ldr =)
"""
import re, struct

# Registro di rilocazione (porting 1.0 -> 1.1, port11.py): per ogni parola emessa che contiene un indirizzo del programma
# (salti b/bl, letterali di ldr =, .word) -> (indirizzo assoluto della parola, 'b' | 'ptr', destinazione/valore).
# I .bytes (stringhe UTF-16, tabelle) non ci finiscono mai.
RELOCS = []
CONSTS = set()          # indirizzi dei letterali '=#valore': costanti pure, port11 le copia senza rilocarle
PROG = (0x100000, 0x700000)

COND = {'eq': 0, 'ne': 1, 'hs': 2, 'cs': 2, 'lo': 3, 'cc': 3, 'mi': 4, 'pl': 5, 'vs': 6, 'vc': 7,
        'hi': 8, 'ls': 9, 'ge': 10, 'lt': 11, 'gt': 12, 'le': 13, 'al': 14}
DP = {'and': 0, 'eor': 1, 'sub': 2, 'rsb': 3, 'add': 4, 'adc': 5, 'sbc': 6, 'rsc': 7, 'tst': 8, 'teq': 9,
      'cmp': 10, 'cmn': 11, 'orr': 12, 'mov': 13, 'bic': 14, 'mvn': 15}
SHIFT = {'lsl': 0, 'lsr': 1, 'asr': 2, 'ror': 3}


def reg(s):
    s = s.strip()
    return {'sp': 13, 'lr': 14, 'pc': 15, 'ip': 12, 'fp': 11, 'sl': 10, 'sb': 9}.get(s, None) if not s.startswith('r') \
        else int(s[1:])


def imm(s):
    s = s.strip().lstrip('#')
    return int(s, 0)


def rot_imm(v):
    v &= 0xFFFFFFFF
    for r in range(16):
        x = ((v << (2 * r)) | (v >> (32 - 2 * r))) & 0xFFFFFFFF if r else v
        if x < 256:
            return (r << 8) | x
    raise ValueError(f'immediato non codificabile: {v:#x}')


def split_ops(s):
    out, depth, cur = [], 0, ''
    for ch in s:
        if ch in '[{':
            depth += 1
        elif ch in ']}':
            depth -= 1
        if ch == ',' and depth == 0:
            out.append(cur.strip()); cur = ''
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def parse_mn(mn, bases):
    """mnemonico -> (base, cond, s_flag)"""
    for b in sorted(bases, key=len, reverse=True):
        if mn.startswith(b):
            rest = mn[len(b):]
            s = False
            if rest.endswith('s') and rest[:-1] in COND or rest == 's':
                s, rest = True, rest[:-1]
            if rest == '' or rest in COND:
                return b, COND.get(rest, 14), s
    return None


def asm(src, base, symbols=None):
    """assembla src all'indirizzo base; restituisce (bytes, etichette). symbols: nomi esterni -> indirizzo"""
    lines = [l.split(';')[0].split('@ ')[0].rstrip() for l in src.splitlines()]
    labels = dict(symbols or {})
    pool = []

    def size_of(l):
        l = l.strip()
        if not l or l.endswith(':'):
            return 0
        if l.startswith('.bytes'):
            return len(l[6:].split(','))
        if l.startswith('.align'):
            return None
        if l.startswith('.pool'):
            return None
        return 4

    # 1° passaggio: indirizzi delle etichette (pool: 4 byte per ogni ldr = prima del .pool)
    pc, npool = base, 0
    for l in lines:
        t = l.strip()
        if t.endswith(':'):
            labels[t[:-1]] = pc
            continue
        if t.startswith('.align'):
            pc = (pc + 3) & ~3
            continue
        if t.startswith('.pool'):
            pc = (pc + 3) & ~3
            pc += 4 * npool
            npool = 0
            continue
        if re.search(r',\s*=', t):
            npool += 1
        pc += size_of(t)
    # 2° passaggio
    out = bytearray()
    pending = []                         # (offset istruzione, valore) per ldr =
    for l in lines:
        t = l.strip()
        if not t or t.endswith(':'):
            continue
        pc = base + len(out)
        if t.startswith('.align'):
            out += b'\0' * ((-len(out)) % 4)
            continue
        if t.startswith('.pool'):
            out += b'\0' * ((-len(out)) % 4)
            for off, val, const in pending:
                lit = base + len(out)
                d = lit - (base + off) - 8
                w = struct.unpack_from('<I', out, off)[0] | (1 << 23) | d
                struct.pack_into('<I', out, off, w)
                if const:
                    CONSTS.add(lit)
                elif PROG[0] <= (val & 0xFFFFFFFF) < PROG[1]:
                    RELOCS.append((lit, 'ptr', val & 0xFFFFFFFF))
                out += struct.pack('<I', val & 0xFFFFFFFF)
            pending = []
            continue
        if t.startswith('.word'):
            v = t[5:].strip()
            val = (labels[v] if v in labels else int(v, 0)) & 0xFFFFFFFF
            if PROG[0] <= val < PROG[1]:
                RELOCS.append((pc, 'ptr', val))
            out += struct.pack('<I', val)
            continue
        if t.startswith('.bytes'):
            out += bytes(int(x, 0) for x in t[6:].split(','))
            continue
        mn, _, ops = t.partition(' ')
        o = split_ops(ops)
        w = None
        # VFP
        if mn == 'vmov':
            sn, rt = int(o[0][1:]), reg(o[1])
            w = 0xEE000A10 | ((sn >> 1) << 16) | (rt << 12) | ((sn & 1) << 7)
        elif mn == 'vcvt.f32.s32':
            sd, sm = int(o[0][1:]), int(o[1][1:])
            w = 0xEEB80AC0 | ((sd & 1) << 22) | ((sd >> 1) << 12) | ((sm & 1) << 5) | (sm >> 1)
        elif mn == 'vstr':
            sd = int(o[0][1:])
            m = re.match(r'\[(\w+)(?:,\s*#(-?\w+))?\]', o[1])
            rn, off = reg(m.group(1)), int(m.group(2) or '0', 0)
            u = 1 if off >= 0 else 0
            w = 0xED000A00 | (u << 23) | ((sd & 1) << 22) | (rn << 16) | ((sd >> 1) << 12) | (abs(off) // 4)
        elif mn in ('push', 'pop'):
            regs = 0
            for part in o[0].strip('{}').split(','):
                part = part.strip()
                if '-' in part:
                    a, b = part.split('-')
                    for r in range(reg(a), reg(b) + 1):
                        regs |= 1 << r
                else:
                    regs |= 1 << reg(part)
            w = (0xE92D0000 if mn == 'push' else 0xE8BD0000) | regs
        else:
            p = parse_mn(mn, ['bl', 'b'])
            if p and (mn == p[0] or mn[len(p[0]):] in COND) and mn not in ('bic', 'bics') and not mn.startswith('bic'):
                b_, c, _ = p
                tgt = labels[o[0]] if o[0] in labels else int(o[0], 0)
                RELOCS.append((pc, 'b', tgt))
                d = (tgt - pc - 8) >> 2
                w = (c << 28) | (0xB << 24 if b_ == 'bl' else 0xA << 24) | (d & 0xFFFFFF)
            else:
                p = parse_mn(mn, ['ldrb', 'strb', 'ldrh', 'strh', 'ldr', 'str'])
                if p:
                    b_, c, _ = p
                    rd = reg(o[0])
                    load = b_.startswith('ldr')
                    if o[1].startswith('='):
                        # '=#valore': costante pura (testo, id di variabile...) mai rilocata da port11 anche se cade
                        # nell'intervallo degli indirizzi (es. "_01\0" = 0x31305f sembrava un puntatore nel .text)
                        const = o[1].startswith('=#')
                        v = o[1][2:] if const else o[1][1:]
                        val = labels[v] if v in labels else int(v, 0)
                        w = (c << 28) | 0x051F0000 | (rd << 12)          # ldr rd, [pc, #?] (U riempito al .pool)
                        pending.append((len(out), val, const))
                    else:
                        post = re.match(r'\[(\w+)\],\s*#(-?\w+)$', ops.split(',', 1)[1].strip())
                        pre = re.match(r'\[(\w+)(?:,\s*#(-?\w+))?\]$', o[1])
                        regoff = re.match(r'\[(\w+),\s*(r\d+|ip|sb|sl|fp)\]$', o[1])
                        if b_ in ('ldrh', 'strh'):
                            if post:
                                rn, off, P = reg(post.group(1)), int(post.group(2), 0), 0
                            else:
                                rn, off, P = reg(pre.group(1)), int(pre.group(2) or '0', 0), 1
                            u = 1 if off >= 0 else 0
                            off = abs(off)
                            w = (c << 28) | (P << 24) | (u << 23) | (1 << 22) | ((1 if load else 0) << 20) | \
                                (rn << 16) | (rd << 12) | ((off >> 4) << 8) | 0xB0 | (off & 15)
                        elif regoff:
                            rn, rm = reg(regoff.group(1)), reg(regoff.group(2))
                            w = (c << 28) | (0x7 << 24) | (1 << 23) | ((1 if 'b' in b_[3:] else 0) << 22) | \
                                ((1 if load else 0) << 20) | (rn << 16) | (rd << 12) | rm
                        else:
                            if post:
                                rn, off, P = reg(post.group(1)), int(post.group(2), 0), 0
                            else:
                                rn, off, P = reg(pre.group(1)), int(pre.group(2) or '0', 0), 1
                            u = 1 if off >= 0 else 0
                            w = (c << 28) | (0x4 << 24) | (P << 24) | (u << 23) | \
                                ((1 if b_.endswith('b') else 0) << 22) | ((1 if load else 0) << 20) | \
                                (rn << 16) | (rd << 12) | abs(off)
                else:
                    p = parse_mn(mn, list(DP))
                    if not p:
                        raise ValueError(f'istruzione non supportata: {t}')
                    b_, c, s = p
                    op = DP[b_]
                    if b_ in ('cmp', 'cmn', 'tst', 'teq'):
                        rd, rn, src2, s = 0, reg(o[0]), o[1:], True
                    elif b_ in ('mov', 'mvn'):
                        rd, rn, src2 = reg(o[0]), 0, o[1:]
                    else:
                        rd, rn, src2 = reg(o[0]), reg(o[1]), o[2:]
                    if src2[0].startswith('#'):
                        op2 = (1 << 25) | rot_imm(imm(src2[0]))
                    else:
                        rm = reg(src2[0])
                        sh = 0
                        if len(src2) > 1:
                            k, n = src2[1].split()
                            sh = (imm(n) << 7) | (SHIFT[k] << 5)
                        op2 = sh | rm
                    w = (c << 28) | op2 | (op << 21) | ((1 if s else 0) << 20) | (rn << 16) | (rd << 12)
        out += struct.pack('<I', w & 0xFFFFFFFF)
    assert not pending, 'ldr = senza .pool finale'
    return bytes(out), labels


def listing(code, base):
    from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM
    md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    return [f'{i.address:#x}: {i.mnemonic} {i.op_str}' for i in md.disasm(code, base)]
