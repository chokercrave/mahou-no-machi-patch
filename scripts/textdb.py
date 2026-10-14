"""Database dei testi 3DS da tradurre e strumenti comuni.

Unità di traduzione = "pagina": un pezzo di slot tra due [#0000].
Ogni pagina ha: codici iniziali (faccia/espressione/voce: $22 $23 $24), corpo, codici finali.
La chiave di confronto ('norm') toglie codici, furigana, a capo e spazi.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import reso

ROOT = os.path.join(os.path.dirname(__file__), '..')
X = os.path.join(ROOT, 'work', '3ds', 'romfs_x')
FILES = {
    'message': 'message/message.tarc_x/message',
    'onemsg': 'message/message.tarc_x/onemsg',
    'actscript': 'script.tarc_x/actscript',
    'npc': 'npc.tarc_x/NpcDataOfs',
}
JP = re.compile(r'[぀-ヿ一-鿿＀-￯]')
TAG = re.compile(r'\[\$[^\]]*\]|\[#[0-9A-F]{4}\]')
FURI = re.compile(r'\{([^|}]*)\|[^}]*\}')
LEAD = re.compile(r"^(?:\[\$2[234]'[^\]]*\])+")   # codici faccia/espressione/voce a inizio pagina


def norm(s):
    s = FURI.sub(r'\1', s)
    s = TAG.sub('', s)
    return re.sub(r'[\s▼　]', '', s)


def split_pages(slot):
    """Slot -> lista di pagine; l'ultimo elemento è la coda (es. '[#000C]')."""
    return slot.split('[#0000]')


def load_all():
    """{file: gruppi RESO}"""
    return {k: reso.load(os.path.join(X, p + '.rdbt'), os.path.join(X, p + '.rndx')) for k, p in FILES.items()}


def iter_slots(groups):
    """(chiave, testo) per ogni slot non vuoto; chiave = 'gid' o 'gid.slot'."""
    for g in groups:
        if 'text' in g:
            yield str(g['id']), g['text']
        else:
            for i, s in enumerate(g['slots']):
                if s:
                    yield f"{g['id']}.{i}", s
