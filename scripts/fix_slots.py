"""Correzioni manuali per slot specifici (id gruppo.slot -> italiano con segnaposto <X1>, <P>…).
Scrive batches/m006.tsv / m006.it.tsv, importati da manual_import.py.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import textdb
from tm_ds import split_page
from batch_prep import to_placeholders

FIX = {
    # mappa (gruppo 99122): nomi dei luoghi e suffissi delle case ("[nome] abita qui") nel lotto m120
    '99104.78': ': ritaglio',
    '99104.95': ', nel negozio',
    '99104.97': '° mese',
    '99007.0': ': vestiti',
    # SpotPass all'avvio: la seconda pagina era un frammento rimasto in giapponese
    '99001.80.0': 'Vuoi ricevere tramite SpotPass dati e avvisi di questo gioco',
    '99001.80.1': '(pubblicità comprese)?',
    # ordine dei nomi: "[studente] della Scuola di Magia di [città]"
    '99002.1': '<X1>Arriva <X3> della Scuola di Magia di <X2>!',          # neutro: ragazzo o ragazza
    '99002.3': '<X1><X3> della Scuola di Magia di <X2> ha fatto ritorno a casa.',
}


# formule fisse per chiave giapponese con segnaposto (valgono ovunque compaiano)
FIX_JP = {
    '<X1>へ': 'Per <X1>,',          # lettere: destinatario
    '<X1>より': 'Da <X1>',          # lettere: mittente (prima il codice del nome spariva)
}


def main():
    groups = {g['id']: g for g in textdb.load_all()['message']}
    src, dst = [], []
    for jp, it in FIX_JP.items():
        src.append(f'{len(src)}\t{jp}')
        dst.append(f'{len(dst)}\t{it}')
    for n, (key, it) in enumerate(FIX.items(), start=len(src)):
        gid, si, *pi = map(int, key.split('.'))      # gruppo.slot[.pagina]
        slot = groups[gid]['slots'][si]
        p = textdb.split_pages(slot)[pi[0] if pi else 0]
        lead, body, trail = split_page(p)
        jp, tags = to_placeholders(body + trail)
        print(key, repr(jp), tags)
        src.append(f'{n}\t{jp}')
        dst.append(f'{n}\t{it}')
    b = os.path.join(textdb.ROOT, 'work', 'trad', 'batches')
    open(os.path.join(b, 'm006.tsv'), 'w', encoding='utf-8').write('\n'.join(src) + '\n')
    open(os.path.join(b, 'm006.it.tsv'), 'w', encoding='utf-8').write('\n'.join(dst) + '\n')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
