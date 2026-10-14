"""QoL 1.2: negozi e servizi aperti 24/7 (script.tarc -> evscript.rdbt).

L'orario non sta nel codice ma negli script EVSC delle porte (docs/RE_atlas.md §4): in testa a ogni script c'e'
  op016(op007(op08f(1056876), 9), <ramo aperto>)      se ora >= 9 entra, altrimenti op063(54xx) "orario: dalle 9 alle 24"
e per il bar (edificio 57 nello script condiviso 25611/25612)
  op016(op019(op009(ora, 3), op007(ora, 8)), <aperto>)  ora <= 3 OR ora >= 8
Si sostituisce la soglia dell'op007 (9 oppure 8) con -1.0: la condizione e' sempre vera (anche se op007 fosse '>').
Stessa dimensione dei token: nessun offset di salto cambia.
"""
import os, struct, sys
sys.path.insert(0, os.path.dirname(__file__))
import evsc, tbaf, patch_relationships, fast_travel, options
from check_mod import MOD

HOUR = 1056876
F = lambda x: struct.unpack('<I', struct.pack('<f', x))[0]
# (script, offset del nodo op016, soglia originale)
SITES = [(25534, 0x58, 9), (25550, 0x58, 9), (25552, 0x48, 9), (25666, 0x30, 9), (250005, 0x30, 9),
         (25611, 0x888, 8), (25611, 0x910, 9), (25612, 0x888, 8), (25612, 0x910, 9)]
SRC = os.path.join(evsc.ROOT, 'work', '3ds', 'romfs', 'script.tarc')
OUT = os.path.join(MOD, 'script.tarc')


def patch(rdbt, rndx):
    rdbt = bytearray(rdbt)
    idx = {sid: (off, sz) for sid, off, sz in (struct.unpack_from('<3I', rndx, i) for i in range(0, len(rndx), 12))}
    for sid, node, val in SITES:
        off, sz = idx[sid]
        toks = list(evsc.tokens(bytes(rdbt[off:off + sz])))
        k0 = next(i for i, (k, v, t) in enumerate(toks) if k == node)
        assert toks[k0][1] == 0x20016, (sid, hex(node), 'non e un op016')
        hit = [i for i in range(k0, min(k0 + 12, len(toks) - 3))
               if toks[i][1] == 0x20007 and toks[i + 1][1] == 0x1008f and toks[i + 2][1] == F(HOUR)]
        assert len(hit) == 1, (sid, hex(node), 'controllo ora non trovato')
        k, v, t = toks[hit[0] + 3]
        assert v == F(val), (sid, hex(node), 'soglia diversa', hex(v))
        struct.pack_into('<I', rdbt, off + k, F(-1.0))
    return bytes(rdbt)


def main():
    ents = {e['name']: e for e in tbaf.parse(open(SRC, 'rb').read())}
    raw = lambda n: tbaf.decompress(ents[n]['data']) if ents[n]['comp'] else ents[n]['data']
    old, rndx = raw('evscript.rdbt'), raw('evscript.rndx')
    new = patch(old, rndx)
    # controllo: cambiano solo i 9 token delle soglie
    diff = [i for i in range(0, len(old), 4) if old[i:i + 4] != new[i:i + 4]]
    assert len(diff) == len(SITES), diff
    # QoL 7: relazioni con qualsiasi sesso (stesso archivio: una sola ricostruzione di script.tarc)
    rel = patch_relationships.patch(new, rndx)
    off = next(o for s, o, _ in (struct.unpack_from('<3I', rndx, i) for i in range(0, len(rndx), 12))
               if s == patch_relationships.SID)
    blk = rel[off:off + len(evsc.load('evscript')[patch_relationships.SID])]
    print(f'128080 (Bouquet d\'invito): {patch_relationships.prove(blk)} combinazioni del modello OK')
    # QoL 1 (1.5): eventi del viaggio rapido (fast_travel.py) in fondo all'archivio, indice riordinato
    new, newx = fast_travel.add_scripts(rel, rndx)
    # riusa materiali (options.py): negli incantesimi op06c(18, 1) -> op06c(18, 4), deciso dal codice con la var 4331
    new, nspell = options.spell_scripts(new, newx)
    # opzioni della patch dal Prof. Olmo (options.py): nuovo script 1021 in fondo, indice ripuntato
    new, newx = options.replace_script(new, newx)
    tbaf.rebuild(SRC, {'evscript.rdbt': new, 'evscript.rndx': newx}, OUT)
    back = {e['name']: e for e in tbaf.parse(open(OUT, 'rb').read())}
    for n, v in (('evscript.rdbt', new), ('evscript.rndx', newx)):
        assert (tbaf.decompress(back[n]['data']) if back[n]['comp'] else back[n]['data']) == v, n
    print(f'script.tarc: {len(fast_travel.DEST)} eventi del viaggio rapido ({fast_travel.GROUP}xx, con il fumo)')
    print(f'script.tarc: script {sorted(options.TEACHERS)} + {sorted(options.HELPERS)} = opzioni dei prof e di Reginaldo')
    print(f'script.tarc: {nspell} op06c(18, 1) -> modo 4 in {len(options.SPELLS)} incantesimi (riusa materiali, var 4331)')
    print(f'script.tarc: {len(SITES)} soglie orarie -> -1 (negozi 24/7)')


if __name__ == '__main__':
    main()
