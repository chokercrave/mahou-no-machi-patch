"""Lavagne tutorial della famiglia Charm (27 incantesimi x 3 lavagne: titolo, procedura, parole magiche).
  python tut_charm.py [n ...]     rende gli incantesimi indicati (default tutti) in work/img_it/_auto/menu_tutorial_pics*/"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import tut_board as tb

ARCH = 'menu_tutorial_pics'
NOTE = ['Amico: scrivi il nome di un', 'amico che vive in città']
BC = 'Bosco o città'
INC = 'Incanto'
# n: (titolo, [righe procedura], [etichette menu], nota)
D = {
    1: ('Pioggia', [('Materiale:', 'Acquamarina'), ('Luogo:', BC), ('Condizione:', 'Giorno sereno o nuvoloso')], [INC, 'Sole', 'Tristezza'], 0),
    2: ('Arcobaleno', [('Materiale:', 'Turchese'), ('Luogo:', BC), ('Condizione:', 'Giorno di pioggia')], [INC, 'Sole', 'Sorriso'], 0),
    3: ('Fiordipioggia', [('Materiale:', '4 margherite'), ('Luogo:', 'Dove ci sono 4 margherite')], [INC, 'Fiore', 'Molti'], 0),
    4: ('Messaggio stellare', [('Materiale:', 'Frammento di stelle filanti'), ('Luogo:', BC)], [INC, 'Stella', 'Vista'], 0),
    5: ('Amicizia', [('Materiale:', 'Smeraldo'), ('Luogo:', 'Rovine')], [INC, 'Sempre', 'Insieme'], 0),
    6: ('Dicoilmioamore', [('Materiale:', 'Rosa rossa'), ('Luogo:', 'Capo degli innamorati'), ('Condizione:', 'Mentre suona la campana')], [INC, 'Sfida', 'Amore'], 0),
    7: ("Sogni d'oro", [('Materiale:', 'Lapislazzuli'), ('Luogo:', 'Letto in camera tua'), ('Condizione:', 'Di notte')], [INC, 'Dormire', 'Appunt.', 'Amico'], 1),
    8: ('Pace', [('Materiale:', 'Margherita gialla'), ('Luogo:', "Dentro l'ufficio postale")], [INC, 'Tristezza', 'Scambio', 'Sorriso'], 0),
    9: ('Compagno di banco', [('Materiale:', 'Mughetto bianco'), ('Luogo:', 'Il tuo banco')], [INC, 'Lezione', 'Appunt.', 'Amico'], 1),
    10: ('Popolarità', [('Materiale:', 'Rugiada di rosa'), ('Luogo:', 'Rovine'), ('Condizione:', 'Notte')], [INC, 'Tutti', 'Guardare'], 0),
    11: ('Bravo a scuola', [('Materiale:', 'Ametista'), ('Luogo:', 'Aula')], [INC, 'Studiare', 'Su'], 0),
    12: ('Invisibilità', [('Materiale:', 'Cristallo'), ('Luogo:', 'Rovine')], [INC, 'Vedere', 'Diverso'], 0),
    13: ('Fiormistero', [('Materiale:', 'Fiore dal colore raro'), ('Luogo:', BC), ('Condizione:', 'Annaffialo ogni giorno')], [INC, 'Mistero', 'Dare'], 0),
    14: ('Cancello mistero', [('Materiale:', 'Margherita nera'), ('Luogo:', BC)], [INC, 'Venire', 'Porta'], 0),
    15: ('Risparmi segreti', [('Materiale:', 'Denaro'), ('Luogo:', BC), ('Condizione:', 'Annaffialo ogni giorno')], [INC, 'Denaro', 'Amore'], 0),
    16: ('Udito fine', [('Materiale:', 'Artiglio di strega'), ('Luogo:', 'Davanti allo specchio')], [INC, 'Vedere', 'Voci'], 0),
    17: ('Caccia tesoro', [('Materiale:', 'Oro'), ('Luogo:', 'Vicino alla fontana')], [INC, 'Giocare', 'Tesoro'], 0),
    18: ('Fortuna', [('Materiale:', 'Pietra del tuo mese'), ('Luogo:', BC), ('Condizione:', "Ora = giorno del compleanno")], [INC, INC, INC], 0),
    19: ('Fungo', [('Materiale:', 'Fungo'), ('Luogo:', 'Foresta dei funghi')], [INC, 'Dispetto', 'Fungo', 'Amico'], 1),
    20: ('Porte comunicanti', [('Materiale:', 'Zaffiro'), ('Luogo:', 'Porta di inizio e di fine')], [INC, 'Venire', 'Stanza'], 0),
    21: ('Pioggia di dolci', [('Materiale:', 'Fiore di dolci'), ('Luogo:', 'Dove ci sono fiori di dolci'), ('Condizione:', 'Giorno di pioggia o neve')], [INC, 'Dolci', 'Molti'], 0),
    22: ('Perspicacia', [('Materiale:', 'Turchese'), ('Luogo:', BC)], [INC, 'Vedere', 'Voglia'], 0),
    23: ('Volantini', [('Materiale:', 'Diamante'), ('Luogo:', BC), ('Condizione:', 'Giorno sereno')], [INC, 'Pubblicità', 'Molti'], 0),
    24: ('Moltiplica funghi', [('Materiale:', 'Fungo'), ('Luogo:', 'Foresta dei funghi'), ('Condizione:', 'Stesso fungo per 3 giorni')], [INC, 'Fungo', 'Molti'], 0),
    25: ('Caccia insetti', [('Materiale:', 'Zucchero'), ('Luogo:', 'Davanti alla fontana')], [INC, 'Giocare', 'Insetto'], 0),
    26: ('Commesso modello', [('Materiale:', '100 Ritch'), ('Luogo:', 'Cucina'), ('Condizione:', "Recitalo 3 volte")], [INC, 'Pubblicità', 'Su'], 0),
    31: ('Aurora', [('Materiale:', 'Smeraldo'), ('Luogo:', 'Dove si vede bene il cielo'), ('Condizione:', 'Notte')], [INC, 'Cielo', 'Splendido'], 0),
}


SPECIAL = {
    1: ('Omuncolo', [('Materiale:', 'Oggetto speciale'), ('Luogo:', '???'), ('Condizione:', 'Ogni giorno per 7 giorni')], [INC, 'Fungo', 'Mistero', 'Osso'], 0),
    2: ('Genio amico', [('Materiale:', 'Cerchio magico'), ('Luogo:', 'Piazza davanti al parco')], [INC, 'Magia', 'Amici', 'Giocare', 'Venire'], 0),
    3: ('Spettrina!', [('Materiale:', 'Tulipano rosso'), ('Luogo:', 'Maschi: bagno maschi'), (' ', 'Femmine: bagno femmine')],
        [[INC, 'Gioco', 'Donna', 'Bagno'], [INC, 'Gioco', 'Uomo', 'Bagno']], 0),
    4: ('Alberomondo', [('Luogo:', 'Davanti alla foresta di funghi')], [INC, 'Saluto', 'Albero'], 0),
}


def one(n, D=D, pre='Charm', arch=ARCH):
    name, rows, labels, note = D[n]
    full = 'Incantesimo ' + name
    # 1: titolo grande
    b = tb.load(f'{pre}_{n:02d}_1')
    lines = [full] if tb.chalk(full, 22).width <= 220 else ['Incantesimo', name]
    tb.save(tb.title(b, lines), f'{pre}_{n:02d}_1', arch)
    # 2: procedura
    b = tb.load(f'{pre}_{n:02d}_2')
    r = tb.find_box(b)
    tb.erase(b, (14, 20, 306, r[3] + 2))
    tb.header(b, r[1], full, 'Procedura')
    new = tb.box_rows(b, r[1], rows)
    if new[3] > r[3] + 4:
        # 3 righe dove l'originale ne aveva 2: righe piu' strette invece di coprire il disegno sotto il riquadro
        b = tb.load(f'{pre}_{n:02d}_2')
        tb.erase(b, (14, 20, 306, r[3] + 2))
        tb.header(b, r[1], full, 'Procedura')
        new = tb.box_rows(b, r[1], rows, row_h=14, pad=(10, 5))
    if new[3] > r[3] + 4:
        print(f'  ! {pre}_{n:02d}_2: riquadro più alto ({new[3]} > {r[3]})')
    tb.save(b, f'{pre}_{n:02d}_2', arch)
    # 3: parole magiche
    b = tb.load(f'{pre}_{n:02d}_3')
    r = tb.find_boxes(b)[0]
    tb.header(b, r[1], full, 'Parole magiche')
    tb.menu_labels(b, labels, NOTE if note else None)
    tb.save(b, f'{pre}_{n:02d}_3', arch)


if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] == 'special':
        for k in sorted(SPECIAL):
            one(k, SPECIAL, 'Special', 'menu_tutorial_pics3')
            print('ok special', k)
    else:
        ks = [int(a) for a in args] or sorted(D)
        for k in ks:
            one(k)
            print('ok', k)
