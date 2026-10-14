"""Lavagne coorde* (look): titoli, titoletti e testi liberi. Coordinate dei rettangoli = fogli work/tut/sheets/coorde_NN.png."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import tut_edit

ARCH = 'menu_tutorial_pics'
SPECS = {
    'coorde01_1': [('T', ['Le basi del look'])],
    'coorde01_2': [('h', 'Abbinare il look', 68),
                   ('r', (510, 85, 560, 115), 'Top', dict(big=True, px=20, align='l')),
                   ('r', (510, 140, 560, 172), 'Pantaloni', dict(big=True, px=18, align='l')),
                   ('r', (520, 200, 548, 224), 'Scarpe', dict(big=True, px=15, align='l'))],
    'coorde01_3': [('h', 'Creare un look 1', 340),
                   ('r', (190, 428, 285, 468), ['Premi il tasto R', 'o tocca lo schermo'], dict(align='l', px=12))],
    'coorde01_4': [('h', 'Creare un look 2', 340)],
    'coorde01_5': [('h', 'Come indossare un look', 68)],
    'coorde02_1': [('T', ['Gli stili del look'])],
    'coorde02_2': [('h', 'Stili di base', 342)] + [('r', (x0, y0 - 11, x1, y0 + 12), t, dict(big=True, px=15)) for x0, x1, y0, t in [
        (55, 155, 381, 'Carino'), (55, 155, 405, 'Pop'), (55, 155, 429, 'Naturale'), (55, 155, 453, 'Cool'), (55, 155, 477, 'Sportivo'),
        (165, 268, 381, 'Rock'), (165, 268, 405, 'Standard'), (165, 268, 429, 'Elegante'), (165, 268, 453, 'Mistero'), (165, 268, 477, 'Uniforme')]],
    'coorde02_3': [('h', 'Stile caotico', 342)],
    'coorde03_1': [('T', ['Vendere i look'])],
    'coorde03_2': [('h', 'Il manichino dei look', 68), ('r', (475, 190, 520, 220), 'Posa', dict(px=12))],
    'coorde03_3': [('h', 'Come fissare il prezzo', 342), ('r', (62, 484, 280, 508), 'Somma del prezzo degli oggetti usati', dict(px=11))],
    'coorde04_1': [('T', ["Berry's"])],
    'coorde04_2': [('h', 'Aggiornamento della rivista', 68),
                   ('r', (95, 163, 285, 184), "La rivista di moda delle maghe: Berry's", dict(px=11)),
                   ('r', (45, 195, 285, 235), ["La rivista di moda Berry's", 'esce ogni mercoledì.'], dict(align='l', px=12))],
    'coorde04_3': [('h', 'Il tema della prossima settimana', 68),
                   ('r', (390, 195, 598, 232), ["Controlla l'anteprima di Berry's", 'e scopri il prossimo tema!'], dict(align='l', px=11))],
    'coorde05_1': [('T', ['Talent scout'])],
    'coorde05_2': [('h', 'Fatti scoprire', 342),
                   ('r', (385, 462, 610, 507), ['Se giri per la città ben vestita,', 'un talent-scout potrebbe notarti!'], dict(align='l', px=11))],
    'coorde05_3': [('h', 'Il servizio fotografico', 68),
                   ('r', (45, 195, 260, 232), ['Se vieni scoperta, ti aspetta', 'un servizio fotografico!'], dict(align='l', px=12))],
    'coorde06_1': [('T', ['Evento di moda'])],
    'coorde06_2': [('h', 'Cosa succede a un evento di moda', 342)],
    'coorde06_3': [('h', 'Chi non sa che look scegliere', 342),
                   ('r', (375, 465, 610, 512), ['Risolvi i dubbi di stile', 'degli abitanti!'], dict(align='r', px=12))],
    'coorde07_1': [('T', ['Partecipare alla', 'sfilata di moda'])],
    'coorde07_2': [('h', 'Periodo della sfilata', 68),
                   ('r', (385, 195, 600, 232), ['Nella Sala Eventi, ogni mese', 'dal 20 a fine mese!!'], dict(px=12))],
    'coorde07_3': [('h', 'Occorrente per la sfilata', 342), ('r', (38, 483, 300, 507), 'Prepara 2 o 3 look.', dict(px=12))],
    'coorde08_1': [('T', ['Contenuti della', 'sfilata di moda'])],
    'coorde08_2': [('h', 'La passerella', 68)],
    'coorde08_3': [('h', 'Tipi di trofeo', 68),
                   ('b', (84, 90, 112, 108), 'Prim.', dict(px=11)),
                   ('b', (212, 90, 236, 108), 'Aut.', dict(px=11)),
                   ('b', (93, 145, 121, 163), 'Est.', dict(px=11)),
                   ('b', (203, 147, 231, 163), 'Inv.', dict(px=11)),
                   ('r', (375, 195, 625, 235), ['Il MVP di stile riceve un trofeo', 'per ogni stagione!'], dict(px=12))],
    'coorde09_1': [('T', ['Consigli sul look', 'dagli amici'])],
    'coorde09_2': [('h', 'Facciamo shopping in coppia', 342),
                   ('r', (375, 365, 440, 387), 'Tasto X', dict(px=11)),
                   ('r', (370, 462, 600, 507), ['Premi X per parlare agli abitanti', 'e fate shopping insieme!'], dict(align='l', px=12))],
    'coorde09_3': [('h', 'Vai da Bibi', 68),
                   ('r', (30, 195, 300, 240), ['Vai da Smile Bibi, la regina dei negozi', 'di moda del centro commerciale!!'], dict(align='l', px=11))],
    'coorde10_1': [('T', ['Linea di moda'])],
    'coorde10_2': [('h', 'Avere una tua linea di moda', 342),
                   ('r', (205, 395, 252, 415), 'Linea', dict(px=11)),
                   ('r', (55, 462, 280, 507), ['Vinci il MVP di stile', 'e crea la tua linea!'], dict(align='l', px=12))],
    'coorde10_3': [('h', 'Chiedi a Jacqueline', 342),
                   ('r', (385, 478, 610, 515), ['"Organizza una sfilata"', "\"Pubblica un annuncio su Berry's\""], dict(px=11))],
    'coorde11_1': [('T', ['Organizzare una', 'sfilata di moda'])],
    'coorde11_2': [('h', 'Preparare la sfilata', 68),
                   ('r', (440, 90, 495, 108), 'Palco', dict(px=11)),
                   ('r', (550, 92, 612, 108), 'Musica', dict(px=11)),
                   ('r', (385, 130, 420, 148), 'Luci', dict(px=11)),
                   ('r', (415, 175, 462, 192), 'Modelle', dict(px=11)),
                   ('r', (430, 205, 560, 228), 'Cosa va preparato', dict(px=12))],
    'coorde11_3': [('h', 'Audizione', 342), ('r', (55, 480, 285, 505), 'Scegli due modelle con le audizioni!', dict(px=11))],
}




# --- coorde12..15: look magici (stesso schema degli incantesimi Charm: titolo, procedura, formula) ---
import tut_board as tb
from tut_edit import retext
from magic_words import W

LOOK = {
    12: ('Danza', [('Materiale:', 'Lapislazzuli'), ('Luogo:', "Stanza di amico o amato"), ('Condizione:', 'Scegli prima il look')], ['Magia', 'Look', 'Stanza', 'Appunt.']),
    13: ('Notte', [('Materiale:', 'Turchese'), ('Luogo:', 'Terrazza della torre (notte)'), ('Condizione:', 'Scegli un look carino')], ['Magia', 'Look', 'Torre', 'Appunt.']),
    14: ('Reale', [('Materiale:', 'Diamante'), ('Luogo:', 'Castello'), ('Condizione:', 'Scegli prima il look')], ['Magia', 'Look', 'Reggia', 'Princ.', 'Re']),
    15: ('Riflettori', [('Materiale:', 'Cristallo'), ('Luogo:', 'Durante un evento di moda'), ('Condizione:', 'Scegli prima il look')], ['Magia', 'Look', 'Sala', 'Sfilata']),
}


def looks(only=None):
    for n, (name, rows, labels) in LOOK.items():
        full = 'Look magico ' + name
        n1, n2, n3 = f'coorde{n:02d}_1', f'coorde{n:02d}_2', f'coorde{n:02d}_3'
        if not only or n1 in only:
            lines = [full] if tb.chalk(full, 22).width <= 220 else ['Look magico', name]
            tb.save(tb.title(tb.load(n1), lines), n1, ARCH)
            print('ok', n1)
        if not only or n2 in only:
            b = tb.load(n2)
            r = tb.find_box(b)
            tb.erase(b, (14, 20, 306, r[3] + 2))
            tb.header(b, r[1], full, 'Procedura')
            new = tb.box_rows(b, r[1], rows)
            if new[3] > r[3] + 4:
                print(f'  ! {n2}: riquadro più alto ({new[3]} > {r[3]})')
            tb.save(b, n2, ARCH)
            print('ok', n2)
        if not only or n3 in only:
            b = tb.load(n3)
            r = tb.find_boxes(b)[0]
            tb.header(b, r[1], full, 'Formula')
            tut_edit.PHOTO = False
            retext(b, (30, 180, 300, 204) if n == 15 else (30, 166, 300, 192), 'Trasformati e prova a recitarla!', px=11)
            if n == 14:
                retext(b, (190, 96, 242, 116), 'A scelta', px=9)
            tb.menu_labels(b, labels, centers=[75, 117, 159, 204, 242] if n == 14 else None)
            tb.save(b, n3, ARCH)
            print('ok', n3)


if __name__ == '__main__':
    tut_edit.run_family(SPECS, ARCH, sys.argv[1:] or None)
    looks(sys.argv[1:] or None)
