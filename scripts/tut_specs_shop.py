"""Lavagne shop_NN_k (negozio: ricette, clienti, pubblicità): titolo grande sulla _1, titoletti, riquadri delle procedure,
formule magiche (menu con icone) e didascalie sotto le icone degli ingredienti. Coordinate 'r' = fogli work/tut/sheets/shop_NN.png."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import tut_board as tb, tut_edit, shop_caps
from tut_edit import hdr, H, tile_of, retext
from magic_words import W

ARCH = 'menu_tutorial_pics2'

# titolo grande (_1): una o due righe
TITLES = {
    0: "Cos'è un negozio?", 1: 'Ricette al forno', 2: 'Ricette di bouquet', 3: 'Ricette di vestiti',
    4: 'Effetto della pubblicità', 5: 'Le ricette', 6: ['Ricetta:', "Biscotti dell'umore"], 7: 'Ricette di dolci freddi',
    8: 'Ricette in padella', 9: ['Ricetta:', "Bouquet d'invito"], 10: 'Ricetta: Collane', 11: ['Ricetta:', 'Abiti alla moda'],
    12: 'La reputazione', 13: 'Tendenze e fiere', 14: ['Come procurare e', 'riporre i materiali'], 15: 'Esporre i prodotti',
    16: ['Ricetta:', "Torta dell'amore"], 17: 'Ricette di fritti', 18: 'Ricette di stufati', 19: ['Ricetta:', 'Tè calmo'],
    20: 'Ricetta: Tiara', 21: ['Ricetta:', 'Amuleto'], 22: ['Ricetta:', 'Bracciale magico'], 23: ['Ricetta:', 'Penna burla'],
    24: 'I clienti', 25: 'Le tendenze', 26: ['Sapori e immagini', 'dei prodotti'], 27: 'Gestire i prodotti',
    28: ['Ricetta:', 'Pie sorpresa'], 29: ['Ricetta:', 'Profumo ammaliante'], 30: ['Ricetta:', 'Portagioie'],
    31: ['Ricetta:', 'Lampada magica'], 32: 'Le richieste', 33: 'Cura dei gioielli', 34: 'Coltivare i fiori',
    35: "L'aspetto del negozio", 36: 'Ricetta: Orecchini',
}

# titoletti delle altre lavagne: 'h' = testo (una riga)
HEAD = {
    'shop_00_2': 'Il negozio', 'shop_00_3': 'Come funziona il negozio',
    'shop_01_2': 'Ricette al forno', 'shop_01_3': 'Ricette al forno',
    'shop_02_2': 'Bouquet', 'shop_02_3': 'Bouquet',
    'shop_03_2': "Scegli la forma dell'abito", 'shop_03_3': "Scegli il motivo dell'abito",
    'shop_04_2': 'Effetto della pubblicità', 'shop_04_3': 'Cosa scopri dai consigli',
    'shop_05_2': 'Ricette varie', 'shop_05_3': 'Ricette magiche',
    'shop_06_2': "Biscotti dell'umore: procedura",
    'shop_07_2': 'Come fare il gelato', 'shop_07_3': 'Come fare il parfait',
    'shop_08_2': 'Piatti classici in padella', 'shop_08_3': 'Piatti speciali in padella',
    'shop_09_2': "Bouquet d'invito: procedura",
    'shop_10_2': 'Come fare una collana', 'shop_10_3': 'Cura della collana',
    'shop_11_2': 'Abiti alla moda: procedura',
    'shop_12_2': 'La reputazione', 'shop_12_3': 'Reputazione buona e cattiva',
    'shop_13_2': 'Le tendenze', 'shop_13_3': 'Le fiere',
    'shop_14_2': 'Come ottenere i materiali', 'shop_14_3': 'Riporli in magazzino',
    'shop_15_2': 'Disporre i prodotti',
    'shop_16_2': "Torta dell'amore: procedura",
    'shop_17_2': 'Fritti classici', 'shop_17_3': 'Fritti speciali',
    'shop_18_2': 'Stufati', 'shop_18_3': 'Stufati',
    'shop_19_2': 'Tè calmo: procedura',
    'shop_20_2': 'Come fare una tiara', 'shop_20_3': 'Cura della tiara',
    'shop_21_2': 'Amuleto: procedura',
    'shop_22_2': 'Bracciale magico: procedura',
    'shop_23_2': 'Penna burla: procedura',
    'shop_24_2': 'Servire i prodotti', 'shop_24_3': 'Prendere gli ordini',
    'shop_25_2': 'Come lanciare una tendenza', 'shop_25_3': 'Attenzione alle tendenze',
    'shop_26_2': 'Il sapore', 'shop_26_3': "L'immagine",
    'shop_27_2': 'Esamina i prodotti', 'shop_27_3': 'Come fissare il prezzo',
    'shop_28_2': 'Pie sorpresa: procedura',
    'shop_29_2': 'Profumo ammaliante: procedura',
    'shop_30_2': 'Portagioie: procedura',
    'shop_31_2': 'Lampada magica: procedura',
    'shop_32_2': 'Le richieste', 'shop_32_3': 'Le richieste',
    'shop_33_2': 'Come curare i gioielli', 'shop_33_3': 'Effetto della cura',
    'shop_34_2': 'Come coltivare i fiori', 'shop_34_3': 'Se vendi i fiori...?',
    'shop_35_2': 'Aspetto del negozio', 'shop_35_3': "Effetto dell'insegna",
    'shop_36_2': 'Come fare gli orecchini', 'shop_36_3': 'Cura degli orecchini',
}

# lavagne 'procedura' (_2): riquadri grigi con Ingrediente/Effetto, uno per riquadro (dall'alto)
ING, EFF = 'Ingred.:', 'Effetto:'
PROC = {
    'shop_06_2': [[(ING, "Goccia di luna, ecc."), (EFF, "Atmosfera felice")],
                  [(ING, "Grasso di rana, ecc."), (EFF, "Atmosfera romantica")],
                  [(ING, "Elisir dell'angelo, ecc."), (EFF, "Atmosfera allegra")]],
    'shop_09_2': [[(ING, "Lacrime di fanciulla"), (EFF, "Fai capire chiaramente i tuoi sentimenti")]],
    'shop_11_2': [[(ING, "Frammento di stelle filanti"), (EFF, "Aspetto carino")],
                  [(ING, "Squama di drago"), (EFF, "Aspetto cool")],
                  [(ING, "Scarabeo d'oro"), (EFF, "Aspetto semplice")],
                  [(ING, "Rovo di rose nere"), (EFF, "Aspetto sontuoso")]],
    'shop_16_2': [[(ING, "Elisir dell'angelo"), (EFF, "L'affetto messo nel dolce arriva a destinazione")]],
    'shop_19_2': [[(ING, "Teiera di vetro"), ('', "Rugiada di rosa"), (EFF, "Calma l'animo di chi lo beve")]],
    'shop_21_2': [[(ING, "Medicina misteriosa"), ('', "Scarabeo d'argento, Smeraldo"), (EFF, "Porta fortuna")]],
    'shop_22_2': [[(ING, "Squama di drago"), (EFF, "Usi meglio gli strumenti")]],
    'shop_23_2': [[(ING, "Piuma rara"), ('', "Rubino, Goccia di luna"), (EFF, "Si attiva lo scherzo")]],
    'shop_28_2': [[(ING, "Radice di Mandragora"), (EFF, "Trasmetti le parole del cuore")]],
    'shop_29_2': [[(ING, "Boccetta di vetro, Elisir dell'angelo"), (EFF, "Attira chi ama il profumo")]],
    'shop_30_2': [[(ING, "Scatola antica"), ('', "Frammento di stelle filanti"), (EFF, "Le gemme riposte possono moltiplicarsi")]],
    'shop_31_2': [[(ING, "Lampada antica"), ('', "Artiglio di strega"), (EFF, "Il desiderio si avvera")]],
}

# lavagne 'formula' (_3): nome della ricetta + icone con etichette
MEN = {
    6: ("Biscotti dell'umore", ['まほう', 'ふしぎ', 'いっしょ']),
    9: ("Bouquet d'invito", ['まほう', 'あそぶ', 'いっしょ']),
    11: ('Abiti alla moda', ['まほう', 'みる', 'ようふく', 'みんな']),
    16: ("Torta dell'amore", ['まほう', 'ラブ', 'うえ']),
    19: ('Tè calmo', ['まほう', 'いっしょ', 'おんしつ']),
    21: ('Amuleto', ['まほう', 'うらない', 'うえ', 'にっこり']),
    22: ('Bracciale magico', ['まほう', 'つえ', 'あそぶ', 'うえ']),
    23: ('Penna burla', ['まほう', 'おく', 'いたずら']),
    28: ('Pie sorpresa', ['まほう', 'あげる', 'ひみつ']),
    29: ('Profumo ammaliante', ['まほう', 'あつまる', 'はな']),
    30: ('Portagioie', ['まほう', 'こうせき', 'たくさん']),
    31: ('Lampada magica', ['まほう', 'もろう', 'ふしぎ']),
}
EXTRA = {'あそぶ': 'Gioco', 'こうせき': 'Minerali', 'もろう': 'Ricevere', 'いっしょ': 'Insieme', 'おんしつ': 'Serra'}


def word(jp):
    return EXTRA.get(jp) or W(jp)


# didascalie sotto le icone, in ordine di lettura (riga per riga); lista = due righe
CAPS0 = {
    'shop_01_2': ['Farina', 'Lievito', 'Pane', 'Farina', 'Burro', 'Crostata'],
    'shop_01_3': ['Farina', 'Zucchero', 'Torta', 'Farina', 'Salsa pizza', 'Pizza', 'Farina', ['Lievito', 'chimico'], 'Muffin'],
    'shop_07_2': ['Latte', 'Frutta, ecc.', 'Gelato'],
    'shop_07_3': ['Latte', 'Frutta, ecc.', 'Parfait', 'Sciroppo'],
    'shop_08_3': ['Farina', ['Lievito', 'chimico'], 'Pancake'],
    'shop_17_2': ['Farina', 'Uovo sbattuto', 'Tempura', ['Pane','grattato'], 'Uovo sbattuto', 'Frittura'],
    'shop_17_3': ['Farina', 'Zucchero', 'Ciambella', 'Farina', 'Carne a pezzi', 'Pollo fritto'],
    'shop_18_2': ['Roux curry', 'Dashi', 'Besciamella'],
    'shop_18_3': ['Riso', 'Roux curry', 'Curry', 'Ramen', ['Pasta', 'cinese'], 'Dashi'],
}
CAPS = {k: [(v.split(' ', 1) if isinstance(v, str) and ' ' in v and len(v) > 8 else v) for v in vs] for k, vs in CAPS0.items()}
# icone non rilevate (poco sature): rettangoli da aggiungere
ADD = {'shop_01_3': [(240, 80, 262, 100)]}

# altri testi liberi: 'r' (rettangolo del foglio) / 'b' (rettangolo della lavagna)
EXTRAOPS = {
    'shop_00_3': [('r', (453, 372, 540, 398), 'Prodotti', dict(px=11)),
                  ('r', (378, 445, 467, 472), 'Vendita', dict(px=11)),
                  ('r', (521, 445, 610, 472), 'Soldi', dict(px=11))],
    'shop_26_2': [('b', (86, 79, 126, 103), 'Gusto', dict(px=11)), ('b', (188, 79, 244, 103), 'Aroma', dict(px=11))] +
                 [('b', (84, y - 9, 146, y + 9), t, dict(px=11)) for y, t in zip((117, 139, 161, 183), ('Dolce', 'Piccante', 'Salato', 'Aspro'))] +
                 [('b', (184, y - 9, 252, y + 9), t, dict(px=11)) for y, t in zip((117, 139, 161, 183), ('Dolce', 'Fresco', 'Calmo', 'Intenso'))],
    'shop_26_3': [('b', (82, 79, 126, 103), 'Colore', dict(px=11)), ('b', (192, 79, 268, 103), 'Impressione', dict(px=10))] +
                 [('b', (60, y - 9, 102, y + 9), t, dict(px=11)) for y, t in zip((117, 139, 161, 183), ('Bianco', 'Nero', 'Rosso', 'Verde'))] +
                 [('b', (104, y - 9, 162, y + 9), t, dict(px=11)) for y, t in zip((117, 139, 161, 183), ('Blu', 'Giallo', 'Rosa', 'Marrone'))] +
                 [('b', (190, y - 9, 264, y + 9), t, dict(px=11)) for y, t in zip((117, 139, 161, 183), ('Carino', 'Cool', 'Semplice', 'Sontuoso'))],
    'shop_27_3': [('b', (43, 58, 90, 80), 'Prezzo', dict(px=11)), ('b', (228, 58, 280, 80), 'Quantità', dict(px=11))],
    'shop_03_2': [('b', (98, 134, 148, 148), 'Cartamodelli', dict(px=8))],
    'shop_13_3': [('r', (105, 480, 230, 500), 'Editto del re', dict(px=11))],
}


# finestra 'classifica delle tendenze' (schermata di gioco): etichetta, targhetta e nomi nelle righe
RANK = {
    'shop_13_2': ((183, 75, 246, 88), (216, 96, 261, 106), [((204, 107, 238, 117), 'Torta'), ((204, 130, 228, 141), 'Crostata'),
                  ((203, 153, 234, 166), 'Gelato'), ((202, 177, 244, 190), 'Muffin')]),
    'shop_04_2': ((184, 75, 246, 87), None, [((208, 112, 237, 124), 'Gelato'), ((206, 134, 228, 146), 'Crostata'),
                  ((206, 156, 236, 169), 'Torta'), ((206, 179, 245, 191), 'Muffin')]),
}


XB = {'shop_27_2': (90, 82, 148, 102), 'shop_33_2': (112, 85, 168, 101)}
RANK['shop_05_2'] = (None, None, [((93, 76, 143, 92), 'Torta'), ((93, 100, 143, 116), 'Bouquet'), ((93, 124, 143, 140), 'Abito')])


def do_rank(img, name):
    from tut_specs_mydesign import put
    tab, flag, rows = RANK[name]
    if tab:
        put(img, tab, 'Tendenze', (235, 235, 235), None, 9)
    if flag:
        put(img, flag, 'In voga!', (255, 255, 255), None, 8)
    for rect, t in rows:
        put(img, rect, t, (30, 50, 130), None, 10, align='l')
    if name == 'shop_04_2':
        tut_edit.PHOTO = False
        retext(img, (54, 84, 128, 104), ['Consiglio:', 'il gelato!'], px=9)


def title_lines(n):
    t = TITLES[n]
    return t if isinstance(t, list) else [t]


def do_title(name, n):
    return tb.title(tb.load(name), title_lines(n))


def do_head(img, name):
    if name in PROC:
        b0 = tb.find_boxes(img)[0][1]
        return hdr(img, (0, b0 - 38, 0, b0 - 4), HEAD[name])
    col, row = tile_of(name)
    y = 68 if row == 0 else 342
    if name == 'shop_27_3':
        y = 62
    hdr(img, H((col, row), (0, y - 12, 0, y + (8 if name == 'shop_27_3' else 9 if name in PROC else 15))), HEAD[name])


def do_proc(img, name):
    boxes = tb.find_boxes(img)
    sets = PROC[name]
    assert len(boxes) == len(sets), (name, boxes)
    for box in boxes:
        tb.erase(img, (box[0] - 4, box[1] - 4, box[2] + 4, box[3] + 4))
    top = boxes[0][1]
    multi = len(sets) > 1
    for rows in sets:
        r = tb.box_rows(img, top, rows, row_h=13 if multi else 17, pad=(8, 5) if multi else (10, 7), px=11 if multi else 13)
        top = r[3] + 5


def do_menu(img, name, n):
    rname, labs = MEN[n]
    r = tb.find_boxes(img)[0]
    tb.header(img, r[1], rname, 'Formula')
    tb.menu_labels(img, [word(w) for w in labs])


def run(only=None):
    tut_edit.PHOTO = False
    names = [f'shop_{n:02d}_{k}' for n in TITLES for k in (1, 2, 3)]
    for name in names:
        if only and name not in only:
            continue
        n, k = int(name[5:7]), int(name[8])
        if name == 'shop_15_3':
            continue
        try:
            img = tb.load(name)
        except Exception:
            continue
        try:
            if k == 1:
                tb.title(img, title_lines(n))
            else:
                if name in HEAD:
                    do_head(img, name)
                if name in PROC:
                    do_proc(img, name)
                if k == 3 and n in MEN:
                    do_menu(img, name, n)
            if name in CAPS:
                shop_caps.captions(img, CAPS[name], add=ADD.get(name, ()))
            if name in XB:
                from tut_specs_mydesign import put
                put(img, XB[name], 'Tasto X', (255, 255, 255), (40, 40, 50), 10)
            if name in RANK:
                do_rank(img, name)
            if name in EXTRAOPS:
                tut_edit.apply_ops(name, img, EXTRAOPS[name])
            tb.save(img, name, ARCH)
            print('ok', name)
        except Exception as e:
            import traceback
            print(f'  ! {name}: {type(e).__name__} {e}')


if __name__ == '__main__':
    run(sys.argv[1:] or None)

