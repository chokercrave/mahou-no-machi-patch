"""Traduce NpcDataOfs (profili NPC) del 3DS e lo installa nella mod (npc.tarc).
Record UTF-16 da 88 unità: [0:6] dati, nome [6:16] (max 9 car.), pronome [16:22],
frase tipica [22:40] (max 17), 6 desinenze [40:76] da 6 unità, [76:88] dati.
In italiano, come nel DS ufficiale: pronome e desinenze vuoti (i codici $514'0/$511'N spariscono).
Fonte nomi/frasi: work/glossary/npc_it.tsv (jp_nome, it_nome, it_frase), generato/curato a parte.
"""
import os, struct, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
import tbaf

ROOT = os.path.join(os.path.dirname(__file__), '..')
X = os.path.join(ROOT, 'work', '3ds', 'romfs_x', 'npc.tarc_x', 'NpcDataOfs')
import paths
MOD = os.path.join(paths.MOD, 'romfs', 'npc.tarc')
FIELDS = {'nome': (6, 10), 'pronome': (16, 6), 'frase': (22, 18)}
ENDINGS = [(40 + 6 * k, 6) for k in range(6)]


def get(u, o, n):
    s = u[o:o + n]
    return ''.join(chr(c) for c in s[:s.index(0)] if True) if 0 in s else ''.join(map(chr, s))


def put(u, o, n, text):
    v = [ord(c) for c in text][:n - 1]
    u[o:o + n] = v + [0] * (n - len(v))


def load_map():
    m = {}
    p = os.path.join(ROOT, 'work', 'glossary', 'npc_it.tsv')
    for line in list(open(p, encoding='utf-8'))[1:]:
        c = line.rstrip('\n').split('\t')
        m[c[0]] = (c[1], c[2] if len(c) > 2 else '')
    return m


def main():
    d = open(X + '.rdbt', 'rb').read()
    x = open(X + '.rndx', 'rb').read()
    names = load_map()
    out_d, out_x, miss = bytearray(), bytearray(), []
    swap = {}  # record originale -> record italiano (per NpcData.npdt / NpcDataVlg.npvdt)
    for i in range(len(x) // 12):
        gid, off, size = struct.unpack_from('<3I', x, i * 12)
        u = list(struct.unpack(f'<{size // 2}H', d[off:off + size]))
        if size == 176:
            jp = get(u, *FIELDS['nome'])
            if jp in names:
                it_name, it_phrase = names[jp]
                if os.environ.get('NPC_TEST', '').split('=')[0] == jp:      # prova: NPC_TEST=テツ=NomeLungo
                    it_name = os.environ['NPC_TEST'].split('=', 1)[1]
                put(u, *FIELDS['pronome'], '')
                if len(it_name) > FIELDS['nome'][1] - 1:
                    # il pronome in italiano è vuoto: il nome può proseguire nel suo campo (fino a 15 car.)
                    put(u, FIELDS['nome'][0], FIELDS['nome'][1] + FIELDS['pronome'][1], it_name)
                else:
                    put(u, *FIELDS['nome'], it_name)
                if get(u, *FIELDS['frase']):
                    put(u, *FIELDS['frase'], it_phrase)
                for o, n in ENDINGS:
                    put(u, o, n, '')
            elif jp:
                miss.append(jp)
        blob = struct.pack(f'<{len(u)}H', *u)
        if size == 176:
            swap[d[off:off + size]] = blob
        out_x += struct.pack('<3I', gid, len(out_d), len(blob))
        out_d += blob
    repl = {'NpcDataOfs.rdbt': bytes(out_d), 'NpcDataOfs.rndx': bytes(out_x)}
    # le stesse schede compaiono concatenate (con intestazione) in altri due file
    xdir = os.path.dirname(X)
    for name in ('NpcData.npdt', 'NpcDataVlg.npvdt'):
        data = bytearray(open(os.path.join(xdir, name), 'rb').read())
        n = 0
        for o in range(0, len(data) - 176 + 1, 4):
            rec = bytes(data[o:o + 176])
            if rec in swap:
                data[o:o + 176] = swap[rec]; n += 1
        repl[name] = bytes(data)
        print(f'{name}: {n} schede sostituite')
    tbaf.rebuild(os.path.join(ROOT, 'work', '3ds', 'romfs', 'npc.tarc'), repl, MOD)
    print(f'npc installati; senza traduzione: {miss}')


if __name__ == '__main__':
    main()
