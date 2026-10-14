"""Vocabolario delle parole magiche già tradotto (work/trad/batches/i007): giapponese -> italiano, per le etichette delle lavagne."""
import os
ROOT = os.path.join(os.path.dirname(__file__), '..')


def load():
    jp, it = {}, {}
    d = os.path.join(ROOT, 'work', 'trad', 'batches')
    for f, t in (('i007.tsv', jp), ('i007.it.tsv', it)):
        for l in open(os.path.join(d, f), encoding='utf-8'):
            p = l.rstrip('\n').split('\t')
            if len(p) > 1 and p[0].isdigit():
                t[int(p[0])] = p[1]
    return {jp[k]: it[k] for k in jp if k in it and 4400 <= k < 4800}


WORDS = load()


def W(jp):
    return WORDS[jp]
