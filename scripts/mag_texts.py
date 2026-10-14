"""Testi italiani dei titoli della rivista Spell & Spill: ISSUES[numero][sprite][id unita'] = testo | None (lascia) | (testo, rettangolo)
Gli id sono quelli di mag_blobs.blobs (gap 4, ordine di lettura); il rettangolo restringe l'unita' a una parte (es. testo vicino a un bollino)."""
ISSUES = {}


class E:
    """cancella i pixel dell'unita' dentro il rettangolo (es. il kanji 号 accanto al numero del bollino)"""
    def __init__(self, rect):
        self.rect = rect


class Z:
    """cancella tutta l'unita' (es. il kanji 号 dopo i numeri, che in italiano non serve)"""


class I(str):
    """testo dentro una forma (ovale, etichetta): si cambia solo il testo, la forma resta"""


def issue(n, **sprites):
    ISSUES[n] = {f'MG{n:02d}_{k}': v for k, v in sprites.items()}


H1 = 'Speciale Capodanno: kimono portafortuna!'
issue(1,
      co1_obj1={1: H1, 2: 'Capodanno', 3: 'Buon anno!'},
      co2_obj1={1: 'Auguri~', 2: H1, 3: None},
      co2_obj2={1: 'Auguri~', 2: H1, 3: None},
      t2n_obj1={1: E((437, 10, 458, 52)), 2: H1},
      t2n_obj2={1: ('Speciale sfilate di moda', (270, 0, 408, 60)), 2: H1})

H2 = 'Inverno carino: look naturale!'
issue(2,
      co1_obj1={1: H2, 2: 'Divertiamoci col freddo!', 3: 'Stile calduccio'},
      co2_obj1={1: 'Il look di cui si parla', 2: H2},
      co2_obj2={1: 'Tutti gli occhi su di te!', 2: H2},
      t2n_obj1={1: 'N.2', 2: H2},
      t2n_obj2={1: 'N.2', 2: 'Speciale sfilate di moda', 3: H2})

H3 = 'Stile cappotto: eleganza da indossare!'
V3 = 'Per chi ama la moda è un must'
issue(3,
      co1_obj1={1: H3, 2: None, 3: 'Look di tendenza da non perdere', 4: None, 5: None, 6: None, 7: None},
      co2_obj1={1: V3, 2: H3},
      co2_obj2={1: V3, 2: H3},
      t2n_obj1={1: 'N.3', 2: H3},
      t2n_obj2={1: 'Speciale sfilate di moda', 2: 'N.3', 3: H3})

H4 = 'Più fascino: speciale carino e cool'
V4 = 'Ha battuto ogni record?! Che stile!'
SB = 'Speciale sfilate di moda'
issue(4,
      co1_obj1={1: (H4, (125, 0, 328, 80)), 2: None, 3: None, 4: 'Il look che cercavi!'},
      co2_obj1={1: H4, 2: V4},
      co2_obj2={1: H4, 2: None, 3: V4, 4: None},
      t2n_obj1={1: E((437, 10, 458, 52)), 2: 'Dolce-amaro', 3: H4},
      t2n_obj2={1: E((437, 10, 458, 52)), 2: 'Dolce-amaro', 3: [(SB, (195, 176, 330, 206)), (H4, (50, 176, 348, 256))]})

H5 = 'Come la neve: splendidi in bianco!'
V5 = "Anche d'inverno, esci con stile!"
B5 = 'In bianco, perfetta per i giorni di neve'
issue(5,
      co1_obj1={1: (H5, (170, 5, 352, 75)), 2: None, 3: V5, 4: None, 5: None},
      co2_obj1={1: I('Look classico per tutti'), 2: H5},
      co2_obj2={1: I('Look classico per tutti'), 2: H5},
      t2n_obj1={1: 'N.5', 2: B5, 3: H5},
      t2n_obj2={1: 'N.5', 2: SB, 3: B5, 4: H5})

H6 = 'Esci in città con un look caldo!'
V6 = 'Look alla moda che convince'
I6 = I('Che calduccio!')
P6 = I('Adoro la moda')
issue(6,
      co1_obj1={1: H6, 2: V6},
      co2_obj1={1: H6, 2: I6, 3: None, 4: None, 5: P6},
      co2_obj2={1: H6, 2: I6, 3: None, 4: None, 5: P6},
      t2n_obj1={1: 'N.6', 2: H6},
      t2n_obj2={1: [('N.6', (410, 8, 458, 38)), (SB, (300, 38, 458, 68))], 2: H6})

H7 = 'San Valentino: look da adulta, cuore a mille!'
V7 = 'Look completo da donna elegante'
issue(7,
      co1_obj1={1: 'San Valentino: look da adulta', 2: None, 3: None, 4: 'La luce nascosta nel look', 5: None, 6: None, 7: None, 8: 'Cuore a mille!'},
      co2_obj1={1: V7, 2: H7},
      co2_obj2={1: V7, 2: H7},
      t2n_obj1={1: 'N.7', 2: H7},
      t2n_obj2={1: [('N.7', (421, 5, 458, 45)), (SB, (266, 5, 420, 45))], 2: H7})

H8 = 'Look monocromatico: un look di classe!'
V8 = 'Look monocromatico completo'
issue(8,
      co1_obj1={1: 'Look di base', 2: H8},
      co2_obj1={1: H8, 2: V8},
      co2_obj2={1: H8, 2: V8},
      t2n_obj1={1: I('N.8'), 2: H8},
      t2n_obj2={1: SB, 2: I('N.8'), 3: H8})

H9 = 'Look naturale e carino: tutto rosa!'
V9a = 'Il mio preferito è questo!'
V9b = 'Look da amare'
V9c = 'Amo il rosa!'
issue(9,
      co1_obj1={1: H9, 2: V9a},
      co2_obj1={1: H9, 2: V9b, 3: V9c},
      co2_obj2={1: H9, 2: V9c, 3: V9b},
      t2n_obj1={1: I('N.9'), 2: (V9c, (103, 133, 160, 186)), 3: H9},
      t2n_obj2={1: SB, 2: I('N.9'), 3: (V9c, (103, 133, 160, 186)), 4: H9})

H10 = 'Look sportivo: sei una campionessa di stile!'
V10 = 'Vorrei giocare coi look per sempre!'
issue(10,
      co1_obj1={1: H10, 2: 'È arrivato il look alla moda'},
      co2_obj1={1: V10, 2: 'Energia al MAX!', 3: H10},
      co2_obj2={1: 'Energia al MAX!', 2: H10},
      t2n_obj1={1: I('N.10'), 2: 'Attiva!', 3: (H10, (122, 149, 393, 247))},
      t2n_obj2={1: [(SB, (260, 5, 406, 45)), (I('N.10'), (406, 5, 458, 45))], 2: 'Attiva!', 3: (H10, (122, 149, 392, 248))})

H11 = 'White Day: un passo avanti con un look carino!'
V11a = 'Incontrati grazie al look del destino!'
V11b = 'Il mio look porta felicità'
ST = 'Sguardi incollati su di te!'
issue(11,
      co1_obj1={1: H11, 2: V11a},
      co2_obj1={1: H11, 2: 'Batticuore!', 3: V11b},
      co2_obj2={1: [('Batticuore!', (225, 48, 285, 76)), (H11, (55, 5, 230, 76))], 2: 'Un tocco di fascino'},
      t2n_obj1={1: [(I('N.11'), (408, 15, 458, 60)), (ST, (355, 50, 440, 100))], 2: H11},
      t2n_obj2={1: [(SB, (278, 5, 412, 38)), (I('N.11'), (412, 15, 458, 50)), (ST, (355, 52, 440, 95))], 2: H11})

H12 = 'Look HAPPY dai colori caldi'
issue(12,
      co1_obj1={1: H12, 2: 'Decorazioni colorate!', 3: None, 4: None},
      co2_obj1={1: H12, 2: 'Alziamo il morale!', 3: 'Decoriamo!'},
      co2_obj2={1: H12, 2: 'Decoriamo!'},
      t2n_obj1={1: I('N.12'), 2: H12},
      t2n_obj2={1: SB, 2: I('N.12'), 3: H12})

H13 = "Gambe di primavera: con i leggings catturi l'attenzione!"
issue(13,
      co1_obj1={1: H13, 2: None, 3: 'Più slanciata', 4: None},
      co2_obj1={1: 'Più slanciata', 2: 'Incanta con le gambe!', 3: H13},
      co2_obj2={1: 'Più slanciata', 2: H13, 3: 'Incanta con le gambe!'},
      t2n_obj1={1: I('N.13'), 2: H13, 3: 'Tocco di stile ai piedi'},
      t2n_obj2={1: I('N.13'), 2: SB, 3: H13, 4: 'Tocco di stile ai piedi'})

H14 = 'Trovato da Spell & Spill! Super look'
issue(14,
      co1_obj1={1: 'I classici del look di tendenza', 2: H14},
      co2_obj1={1: H14, 2: 'Da esperte!'},
      co2_obj2={1: I('Da esperte!'), 2: H14},
      t2n_obj1={1: 'N.14', 2: H14},
      t2n_obj2={1: [(SB, (312, 5, 412, 52)), ('N.14', (412, 5, 458, 52))], 2: H14})

H15 = 'Gita fuori in tunica: look di primavera!'
V15a = 'Il nuovo standard è questo'
V15b = 'Cambia umore: andiamo a spasso!'
issue(15,
      co1_obj1={1: H15, 2: 'Morbido, perfetto per la passeggiata'},
      co2_obj1={1: V15a, 2: V15b, 3: H15, 4: None},
      co2_obj2={1: None, 2: V15a, 3: H15, 4: None},
      t2n_obj1={1: [('N.15', (356, 226, 396, 248)), (I('Tante novità!'), (108, 148, 172, 200)), E((138, 198, 174, 232)), (H15, (172, 160, 396, 250))]},
      t2n_obj2={1: SB, 2: [('N.15', (356, 226, 396, 248)), (I('Tante novità!'), (108, 148, 175, 200)), E((138, 198, 174, 232)), (H15, (172, 160, 396, 250))]})

H16 = 'Nuovo semestre: uniformi in stile infinito SP'
V16a = 'Scoperte le più brave!'
V16b = 'La lezione inizia...!'
issue(16,
      co1_obj1={1: H16, 2: V16a},
      co2_obj1={1: V16b, 2: H16},
      co2_obj2={1: V16b, 2: H16},
      t2n_obj1={1: 'N.16', 2: None, 3: None, 4: None, 5: H16, 6: None, 7: None, 8: None, 9: None},
      t2n_obj2={1: SB, 2: 'N.16', 3: None, 4: None, 5: None, 6: H16, 7: None, 8: None, 9: None, 10: None})

H17 = 'Carina e vincente: punta tutto sul rosa!'
V17a = 'Mmm, alla fine è questo!'
V17b = 'Troppo carino!'
issue(17,
      co1_obj1={1: H17, 2: None, 3: None},
      co2_obj1={1: H17, 2: None, 3: V17a, 4: V17b},
      co2_obj2={1: H17, 2: V17b},
      t2n_obj1={1: 'N.17', 2: None, 3: H17},
      t2n_obj2={1: 'N.17', 2: SB, 3: None, 4: H17})

H18a, H18b = 'Sweet', 'Rosa e verde'
H18 = 'Dolce umore: rosa e verde'
V18o = I('Look che ruba il cuore')


def h18(heart, head):
    return [(I(H18a), heart), (H18b, head)]


issue(18,
      co1_obj1={1: 'Colori che conquistano!', 2: None, 3: h18((58, 194, 112, 248), (112, 194, 246, 248)), 4: None},
      co2_obj1={1: h18((58, 8, 110, 60), (110, 8, 228, 60)), 2: 'Vestiti di colori!', 3: V18o, 4: None},
      co2_obj2={1: h18((58, 8, 110, 60), (110, 8, 228, 60)), 2: V18o},
      t2n_obj1={1: 'N.18', 2: None, 3: [(I(H18a), (126, 174, 205, 245)), (H18b, (203, 186, 390, 248))], 4: None, 5: None, 6: None},
      t2n_obj2={1: 'N.18', 2: SB, 3: None, 4: None, 5: None, 6: None, 7: None})

H19 = 'Look da donna: le tecniche da cui iniziare'
T19 = 'Passa al look adulto!'
issue(19,
      co1_obj1={1: H19, 2: None, 3: 'Bellezza', 4: None, 5: None},
      co2_obj1={1: 'Facciamoci belle!', 2: H19},
      co2_obj2={1: 'Vestiamoci!', 2: H19},
      t2n_obj1={1: 'N.19', 2: [(T19, (56, 144, 210, 188)), (H19, (56, 188, 300, 250))]},
      t2n_obj2={1: [('N.19', (412, 8, 458, 36)), (SB, (333, 36, 458, 62))], 2: [(T19, (56, 144, 210, 188)), (H19, (56, 188, 300, 250))]})

H20 = 'Ricarica di bellezza: primavera in denim!'
V20a = 'I classici non tradiscono!'
V20b = 'Presenza discreta'
V20c = 'Un look tutto mio!'
V20d = 'Mix primaverile'
issue(20,
      co1_obj1={1: V20a, 2: H20},
      co2_obj1={1: H20, 2: V20c, 3: V20b},
      co2_obj2={1: H20, 2: V20b},
      t2n_obj1={1: 'N.20', 2: V20d, 3: (H20, (60, 166, 300, 248)), 4: None},
      t2n_obj2={1: SB, 2: 'N.20', 3: V20d, 4: (H20, (60, 166, 300, 248)), 5: None})

H21 = 'Occhio! Look da diavoletta ammaliante'
V21 = 'Attira gli sguardi'
issue(21,
      co1_obj1={1: H21, 2: V21},
      co2_obj1={1: None, 2: 'Romantica', 3: H21, 4: None},
      co2_obj2={1: 'Romantica', 2: H21},
      t2n_obj1={1: 'N.21', 2: H21},
      t2n_obj2={1: [('N.21', (410, 8, 458, 36)), (SB, (318, 36, 458, 62))], 2: H21})

H22 = 'Tocco di stile: pop colorato!'
V22a = 'Scateniamoci!'
V22b = 'Look che colpisce!'
V22c = 'Monella!'
issue(22,
      co1_obj1={1: H22, 2: V22a},
      co2_obj1={1: None, 2: V22b, 3: H22, 4: None, 5: None},
      co2_obj2={1: V22b, 2: H22},
      t2n_obj1={1: 'N.22', 2: V22c, 3: H22},
      t2n_obj2={1: [('N.22', (406, 6, 460, 60)), (SB, (264, 12, 406, 56))], 2: V22c, 3: H22})

H23 = 'Cool Beauty: guida allo stile'
V23a = 'Record battuto?! Che gusto!'
V23b = 'Da vedere!'
issue(23,
      co1_obj1={1: H23, 2: V23a},
      co2_obj1={1: V23b, 2: H23},
      co2_obj2={1: V23b, 2: H23},
      t2n_obj1={1: 'N.23', 2: H23, 3: None},
      t2n_obj2={1: [('N.23', (408, 8, 456, 42)), (SB, (262, 10, 408, 48))], 2: H23, 3: None})

# 21: tag "注目!" separato dal titolo
M21 = 'Look da diavoletta ammaliante'
nar = lambda r1, r2: [('Ehi!', r1), (M21, r2)]
issue(21,
      co1_obj1={1: nar((56, 8, 88, 62), (88, 8, 250, 66)), 2: V21},
      co2_obj1={1: None, 2: 'Romantica', 3: nar((56, 190, 90, 250), (90, 190, 252, 250)), 4: None},
      co2_obj2={1: 'Romantica', 2: nar((56, 190, 90, 250), (90, 190, 252, 250))},
      t2n_obj1={1: 'N.21', 2: [('Occhio!', (56, 148, 130, 190)), (M21, (56, 188, 316, 250))]},
      t2n_obj2={1: [('N.21', (410, 8, 458, 36)), (SB, (318, 36, 458, 62))],
                2: [('Occhio!', (56, 148, 130, 190)), (M21, (56, 188, 316, 250))]})

# 23: bollino "まるわかり" separato dal titolo
M23 = 'Cool Beauty Style'
B23 = 'Tutto chiaro'
issue(23,
      co1_obj1={1: [(B23, (146, 8, 224, 84)), (M23, (224, 8, 366, 84))], 2: V23a},
      co2_obj1={1: V23b, 2: [(B23, (56, 170, 134, 250)), (M23, (134, 170, 278, 250))]},
      co2_obj2={1: V23b, 2: [(B23, (56, 170, 134, 250)), (M23, (134, 170, 278, 250))]},
      t2n_obj1={1: 'N.23', 2: [(B23, (56, 124, 142, 190)), (M23, (56, 124, 336, 252))], 3: None},
      t2n_obj2={1: [('N.23', (408, 8, 456, 42)), (SB, (262, 10, 408, 48))],
                2: [(B23, (56, 124, 142, 190)), (M23, (56, 124, 336, 252))], 3: None})

H24 = "Storia d'amore coi nastri dei sogni"
V24a = 'Look alla moda pieno di felicità'
V24b = 'Che dolcezza!'
V24c = 'Il look di cui si parla!'
BB24 = I('Nastri!')
issue(24,
      co1_obj1={1: None, 2: V24a, 3: H24},
      co2_obj1={1: H24, 2: V24b, 3: V24c},
      co2_obj2={1: H24, 2: V24b},
      t2n_obj1={1: 'N.24', 2: [(BB24, (56, 146, 134, 196)), H24]},
      t2n_obj2={1: [('N.24', (403, 6, 458, 44)), (SB, (258, 10, 404, 50))], 2: [(BB24, (56, 146, 134, 196)), H24]})

H25 = 'Look supremo: vai in testa!'
V25a = 'Il solito stile non basta!'
V25b = 'Energia MAX'
V25c = 'In posa!'
T25 = ('Batticuore!', (56, 134, 150, 180))
issue(25,
      co1_obj1={1: V25a, 2: H25},
      co2_obj1={1: H25, 2: V25b, 3: V25c},
      co2_obj2={1: H25, 2: V25c},
      t2n_obj1={1: 'N.25', 2: [T25, H25]},
      t2n_obj2={1: SB, 2: 'N.25', 3: [T25, H25]})

H26 = 'Estate scintillante: look con canotta'
issue(26,
      co1_obj1={1: H26, 2: "È arrivata l'estate!"},
      co2_obj1={1: 'Fresca!', 2: 'Il look del momento da copiare', 3: H26},
      co2_obj2={1: 'Fresca!', 2: H26},
      t2n_obj1={1: 'N.26', 2: H26},
      t2n_obj2={1: 'N.26', 2: SB, 3: H26})

H27 = 'Look naturale 1-2-3'
V27a = 'Che bello fare look!'
T27 = ('Morbido', (56, 172, 134, 206))
issue(27,
      co1_obj1={1: 'Relax', 2: H27},
      co2_obj1={1: 'Le basi prima di tutto', 2: V27a, 3: 'È questo!', 4: [T27, (H27, (56, 172, 242, 250))]},
      co2_obj2={1: V27a, 2: [('Morbido', (56, 174, 130, 206)), (H27, (56, 172, 242, 250))]},
      t2n_obj1={1: 'N.27', 2: [('Puro', (108, 148, 162, 196)), (H27, (108, 148, 388, 248))]},
      t2n_obj2={1: SB, 2: 'N.27', 3: [('Puro', (108, 148, 162, 196)), (H27, (108, 148, 388, 248))]})

H28 = 'La chiave è "carino": camicie estive SP'
V28a = 'Più stile con ogni look!'
V28b = 'Equilibrio perfetto!'
V28c = "Protagonista dell'estate!"
issue(28,
      co1_obj1={1: V28a, 2: H28},
      co2_obj1={1: V28b, 2: V28c, 3: H28},
      co2_obj2={1: V28c, 2: V28b, 3: H28},
      t2n_obj1={1: 'N.28', 2: H28},
      t2n_obj2={1: [('N.28', (406, 8, 458, 44)), (SB, (268, 8, 406, 48))], 2: H28})

H29 = 'Punta sul Cool: look vincente!'
V29 = 'Il solito look non basta'
issue(29,
      co1_obj1={1: 'Stile UP', 2: H29},
      co2_obj1={1: H29, 2: 'Che bello!', 3: V29},
      co2_obj2={1: H29, 2: V29},
      t2n_obj1={1: 'N.29', 2: 'Look forte', 3: H29},
      t2n_obj2={1: 'N.29', 2: SB, 3: 'Look forte', 4: H29})

H30 = 'Estate al top: look da conquista!'
issue(30,
      co1_obj1={1: H30, 2: 'Funziona in amore?!'},
      co2_obj1={1: 'Occhio, assolutamente!', 2: H30},
      co2_obj2={1: 'Amore estivo', 2: H30},
      t2n_obj1={1: 'N.30', 2: H30},
      t2n_obj2={1: 'N.30', 2: SB, 3: H30})

H31 = 'Stile a righe: look risolto!'
T31 = ('Il look del momento', (56, 105, 215, 174))
M31 = (H31, (56, 174, 336, 250))
issue(31,
      co1_obj1={1: H31, 2: 'Il marinaro è un must'},
      co2_obj1={1: 'Classico estivo', 2: 'A righe!', 3: H31},
      co2_obj2={1: 'A righe!', 2: H31},
      t2n_obj1={1: 'N.31', 2: [T31, M31], 3: None},
      t2n_obj2={1: [('N.31', (404, 6, 458, 40)), (SB, (258, 8, 404, 50))], 2: [T31, M31], 3: None})

H32 = "Adoro l'azzurro: look fresco d'estate!"
V32 = 'Successo estivo'
issue(32,
      co1_obj1={1: H32, 2: 'Curo il mio stile'},
      co2_obj1={1: V32, 2: 'Il colore fa la differenza', 3: H32},
      co2_obj2={1: V32, 2: H32},
      t2n_obj1={1: 'N.32', 2: 'Frizzante', 3: H32},
      t2n_obj2={1: 'N.32', 2: SB, 3: 'Frizzante', 4: H32})

B33 = I('Look giapponese')
G33 = 'Gran Expo'
issue(33,
      co1_obj1={1: [(B33, (60, 16, 116, 110)), (G33, (60, 110, 116, 216))], 2: 'Arriva lo stile giapponese!'},
      co2_obj1={1: None, 2: [(B33, (418, 136, 454, 204)), (G33, (374, 136, 454, 250))], 3: 'Composta'},
      co2_obj2={1: 'Composta', 2: [(B33, (418, 136, 454, 204)), (G33, (374, 136, 454, 250))]},
      t2n_obj1={1: 'N.33', 2: [(B33, (402, 44, 452, 172)), (G33, (311, 44, 452, 250))]},
      t2n_obj2={1: SB, 2: 'N.33', 3: [(B33, (402, 44, 452, 172)), (G33, (311, 44, 452, 250))]})

H34 = 'Look estivo da urlo!'
B34a = ('Pieno di energia!', (166, 6, 244, 70))
B34b = ('Super estate', (214, 66, 298, 140))
T34 = ('Troppo figo!', (56, 118, 200, 160))
issue(34,
      co1_obj1={1: 'Spiega le ali: look alla moda!', 2: H34},
      co2_obj1={1: [B34a, B34b], 2: [('Piena estate!', (364, 178, 456, 250)), H34]},
      co2_obj2={1: 'Super estate', 2: H34},
      t2n_obj1={1: 'N.34', 2: [T34, (H34, (56, 158, 336, 250))]},
      t2n_obj2={1: 'N.34', 2: [(SB, (196, 180, 320, 206)), T34, (H34, (56, 158, 336, 250))]})

H35 = 'Con i volant, che allegria!'
issue(35,
      co1_obj1={1: H35, 2: "Bello l'uso dei volant!"},
      co2_obj1={1: H35, 2: 'Dolly!', 3: 'Soffice'},
      co2_obj2={1: H35, 2: 'Soffice', 3: 'Dolly!'},
      t2n_obj1={1: 'N.35', 2: 'Morbido!', 3: H35},
      t2n_obj2={1: 'N.35', 2: SB, 3: 'Morbido!', 4: H35})

# 34 (correzione): titolo e tag "夏本番!" in rettangoli disgiunti
issue(34,
      co1_obj1={1: 'Spiega le ali: look alla moda!', 2: H34},
      co2_obj1={1: [B34a, B34b], 2: [('Piena estate!', (364, 178, 456, 250)), (H34, (260, 176, 366, 250))]},
      co2_obj2={1: 'Super estate', 2: H34},
      t2n_obj1={1: 'N.34', 2: [T34, (H34, (56, 158, 336, 250))]},
      t2n_obj2={1: 'N.34', 2: [(SB, (196, 180, 320, 206)), T34, (H34, (56, 158, 336, 250))]})

H36 = 'Look rock: speciale infuocato!'
T36 = ('Sfida al nuovo look', (88, 165, 182, 250))
issue(36,
      co1_obj1={1: None, 2: None, 3: H36},
      co2_obj1={1: H36, 2: 'Imprimi il ritmo nel cuore!', 3: None},
      co2_obj2={1: H36, 2: None},
      t2n_obj1={1: 'N.36', 2: [T36, (H36, (182, 165, 424, 250))]},
      t2n_obj2={1: [('N.36', (404, 8, 458, 44)), (SB, (258, 8, 404, 48))], 2: [T36, (H36, (182, 165, 424, 250))]})

H37 = 'Maestra dei look stilosi'
issue(37,
      co1_obj1={1: H37, 2: 'Un passo avanti!', 3: None},
      co2_obj1={1: 'Popolare', 2: H37},
      co2_obj2={1: 'Popolare', 2: H37},
      t2n_obj1={1: 'N.37', 2: H37},
      t2n_obj2={1: SB, 2: 'N.37', 3: H37})

H38 = 'Carina e alla moda: sali di livello!'
H38r = (H38, (319, 88, 455, 252))
issue(38,
      co1_obj1={1: None, 2: 'Lo adoro!', 3: None, 4: H38},
      co2_obj1={1: H38, 2: 'Batticuore!'},
      co2_obj2={1: H38},
      t2n_obj1={1: 'N.38', 2: H38r},
      t2n_obj2={1: SB, 2: 'N.38', 3: H38r})

H39 = 'Autunno sportivo al MAX!'
T39 = ('Carica di carineria!', (350, 126, 440, 160))
issue(39,
      co1_obj1={1: 'Adorabile', 2: 'Super alla moda', 3: H39},
      co2_obj1={1: 'Boom di popolarità', 2: H39},
      co2_obj2={1: 'Boom di popolarità', 2: H39},
      t2n_obj1={1: 'N.39', 2: [T39, (H39, (170, 126, 456, 250))]},
      t2n_obj2={1: 'N.39', 2: SB, 3: [T39, (H39, (170, 126, 456, 250))]})

H40 = 'Collezione arancio-marrone'
O40 = 'Abbina i colori'
issue(40,
      co1_obj1={1: 'Il tocco autunnale è un must!', 2: H40},
      co2_obj1={1: H40, 2: O40},
      co2_obj2={1: H40, 2: O40},
      t2n_obj1={1: 'N.40', 2: H40},
      t2n_obj2={1: SB, 2: 'N.40', 3: H40})

H41 = "Speciale autunno: i classici da abbinare"
T41 = ('Appeal discreto', (54, 104, 150, 172))
M41 = (H41, (54, 172, 332, 250))
issue(41,
      co1_obj1={1: 'Facile da abbinare', 2: H41},
      co2_obj1={1: H41, 2: 'Questo!'},
      co2_obj2={1: H41, 2: 'Questo!'},
      t2n_obj1={1: 'N.41', 2: [T41, M41]},
      t2n_obj2={1: SB, 2: 'N.41', 3: [T41, M41]})

H42 = 'Eleganza di tendenza: tutti i look!'
V42 = 'Il look che fa innamorare'
T42 = ('Come una star', (51, 115, 150, 176))
M42 = (H42, (51, 115, 366, 252))
issue(42,
      co1_obj1={1: 'Un livello in più!', 2: H42},
      co2_obj1={1: None, 2: V42, 3: H42},
      co2_obj2={1: None, 2: H42, 3: V42},
      t2n_obj1={1: 'N.42', 2: [T42, M42]},
      t2n_obj2={1: SB, 2: 'N.42', 3: [T42, M42]})

H43 = "Goditi l'autunno con il rosso!?"
T43 = (I('Audace!'), (58, 138, 134, 200))
issue(43,
      co1_obj1={1: 'Autunno rosso fuoco!', 2: H43},
      co2_obj1={1: 'Rosso SP', 2: H43, 3: 'Voglio il segreto del look!'},
      co2_obj2={1: 'Rosso SP', 2: H43},
      t2n_obj1={1: 'N.43', 2: [T43, H43]},
      t2n_obj2={1: SB, 2: 'N.43', 3: [T43, H43]})

H44 = 'Speciale Halloween'
T44a = (I('Scherzi!'), (56, 22, 162, 78))
T44b = (I('Scherzi!'), (56, 196, 134, 248))
T44c = (I('Scherzi!'), (56, 190, 160, 250))
issue(44,
      co1_obj1={1: [T44a, (H44, (160, 8, 262, 78))], 2: None},
      co2_obj1={1: 'Birichina!', 2: None, 3: [T44b, (H44, (130, 163, 246, 248))]},
      co2_obj2={1: 'Birichina!', 2: None, 3: [T44b, (H44, (130, 163, 246, 248))]},
      t2n_obj1={1: 'N.44', 2: [T44c, (H44, (160, 118, 320, 250))]},
      t2n_obj2={1: SB, 2: 'N.44', 3: [T44c, (H44, (160, 118, 320, 250))]})

H45 = 'Giacca cool per donne in gamba'
V45 = 'Più efficienza sul lavoro!'
issue(45,
      co1_obj1={1: '120% cool', 2: H45},
      co2_obj1={1: V45, 2: H45},
      co2_obj2={1: V45, 2: H45},
      t2n_obj1={1: 'N.45', 2: H45},
      t2n_obj2={1: 'N.45', 2: [(SB, (178, 188, 316, 214)), H45]})

H46 = 'Collezione stile elegante'
T46 = ('Scopri un lato nuovo!', (352, 118, 452, 174))
issue(46,
      co1_obj1={1: H46, 2: 'Un look che profuma di batticuore'},
      co2_obj1={1: "La parola d'ordine dello stile", 2: 'Perfetto', 3: H46},
      co2_obj2={1: "La parola d'ordine", 2: H46},
      t2n_obj1={1: 'N.46', 2: 'Scopri un lato nuovo!', 3: H46},
      t2n_obj2={1: 'N.46', 2: [T46, (SB, (255, 175, 402, 198)), H46]})

H47 = 'Sfida! Super Style da urlo'
T47 = ('Con questo vinci!', (54, 108, 190, 150))
issue(47,
      co1_obj1={1: H47, 2: 'Un look di livello platino'},
      co2_obj1={1: 'Ce la faccio!', 2: H47},
      co2_obj2={1: 'Ce la faccio!', 2: H47},
      t2n_obj1={1: 'N.47', 2: [T47, (H47, (54, 164, 326, 252))]},
      t2n_obj2={1: SB, 2: 'N.47', 3: [T47, (H47, (54, 164, 326, 252))]})

# 45/46 (correzione): il bollino "Speciale sfilate" sta dentro il titolo
issue(45,
      co1_obj1={1: '120% cool', 2: H45},
      co2_obj1={1: V45, 2: H45},
      co2_obj2={1: V45, 2: H45},
      t2n_obj1={1: 'N.45', 2: H45},
      t2n_obj2={1: 'N.45', 2: [(SB, (178, 188, 316, 214)), ('Donne in gamba:', (56, 146, 178, 208)), ('giacca cool', (56, 208, 322, 252))]})
issue(46,
      co1_obj1={1: H46, 2: 'Un look che profuma di batticuore'},
      co2_obj1={1: "La parola d'ordine dello stile", 2: 'Perfetto', 3: H46},
      co2_obj2={1: "La parola d'ordine", 2: H46},
      t2n_obj1={1: 'N.46', 2: 'Scopri un lato nuovo!', 3: H46},
      t2n_obj2={1: 'N.46', 2: [('Scopri un lato nuovo!', (352, 118, 452, 170)), (SB, (255, 162, 402, 188)), (H46, (120, 188, 452, 256))]})

H48 = 'Look con giacca: fai colpo con stile!'
T48 = [('Look giacca', (320, 122, 458, 192)), ('Colpisci con stile!', (320, 192, 458, 252))]
issue(48,
      co1_obj1={1: H48, 2: 'Capo imprescindibile!'},
      co2_obj1={1: 'Da non perdere!', 2: 'Che atmosfera!', 3: H48},
      co2_obj2={1: 'Che atmosfera!', 2: H48},
      t2n_obj1={1: 'N.48', 2: T48},
      t2n_obj2={1: 'N.48', 2: SB, 3: T48})

H49 = "Cool girl d'inverno: look da urlo!"
V49 = 'Colori diversi dal solito'
T49 = ('Contro il freddo!', (336, 130, 424, 180))
M49 = (H49, (183, 128, 456, 250))
issue(49,
      co1_obj1={1: 'Il mio obiettivo: questo look', 2: H49},
      co2_obj1={1: H49, 2: V49, 3: 'Ti svelo un segreto di stile'},
      co2_obj2={1: H49, 2: V49},
      t2n_obj1={1: 'N.49', 2: [T49, M49]},
      t2n_obj2={1: 'N.49', 2: SB, 3: [T49, M49]})

H50 = 'Look slim con colori freschi!'
T50 = ('Gioca coi colori!', (54, 112, 150, 166))
M50 = (H50, (54, 164, 324, 252))
issue(50,
      co1_obj1={1: H50, 2: 'Trucchi di stile'},
      co2_obj1={1: 'Voglio dirlo a tutti!', 2: None, 3: H50},
      co2_obj2={1: None, 2: H50},
      t2n_obj1={1: 'N.50', 2: [T50, M50]},
      t2n_obj2={1: SB, 2: 'N.50', 3: [T50, M50]})

issue(46,
      co1_obj1={1: H46, 2: 'Un look che profuma di batticuore'},
      co2_obj1={1: "La parola d'ordine dello stile", 2: 'Perfetto', 3: H46},
      co2_obj2={1: "La parola d'ordine", 2: H46},
      t2n_obj1={1: 'N.46', 2: 'Scopri un lato nuovo!', 3: H46},
      t2n_obj2={1: 'N.46', 2: [('Scopri un lato nuovo!', (352, 118, 452, 170)), E((255, 160, 402, 190)), H46]})

H51 = 'A Natale si vince col rosso!'
issue(51,
      co1_obj1={1: H51},
      co2_obj1={1: None, 2: H51},
      co2_obj2={1: None, 2: H51},
      t2n_obj1={1: 'N.51', 2: 'Buon Natale!', 3: H51},
      t2n_obj2={1: 'N.51', 2: SB, 3: 'Buon Natale!', 4: H51})

L52 = ('Stagione delle feste!', (56, 170, 136, 250))
R52 = ('Guida ai look formali!', (136, 170, 244, 250))
T52 = [('Splende!', (324, 176, 394, 214)), ('Stagione delle feste!', (186, 120, 326, 212)), ('Guida ai look formali!', (124, 212, 396, 252))]
issue(52,
      co1_obj1={1: 'Protagonista della festa', 2: [L52, R52]},
      co2_obj1={1: 'Balliamo?', 2: [L52, R52]},
      co2_obj2={1: [L52, R52], 2: 'Balliamo?'},
      t2n_obj1={1: 'N.52', 2: T52},
      t2n_obj2={1: SB, 2: 'N.52', 3: T52})


# ---- numeri 53-56 (sprite nelle pagine rivista) e banner del negozio MG57 ----
Z_ = Z()
T53 = 'Consigli sui nuovi look'
issue(53,
      co1_obj1={1: T53, 2: 'Lo adoro!'},
      co2_obj1={1: 'Ti sta benissimo!', 2: 'Sempre alla moda', 3: T53},
      co2_obj2={1: 'Ti sta benissimo!', 2: T53},
      t2n_obj1={1: Z_, 2: T53},
      t2n_obj2={1: SB})

M54 = 'Il colore must del look'
issue(54,
      co1_obj1={1: 'Abbinamento perfetto!', 2: 'Fatti notare!', 3: M54},
      co2_obj1={1: I('Nuove sensazioni'), 2: I('Look top del momento'), 3: M54},
      co2_obj2={1: I('Nuove sensazioni'), 2: I('Look top del momento'), 3: M54},
      t2n_obj1={1: Z_, 2: M54},
      t2n_obj2={1: SB})

C55 = 'Corso intensivo'
issue(55,
      co1_obj1={1: 'Proprio questo!', 2: C55, 3: 'Cambia lo standard della moda'},
      co2_obj1={1: I('Lo voglio troppo!'), 2: 'Super trendy', 3: C55},
      co2_obj2={1: I('Lo voglio troppo!'), 2: C55},
      t2n_obj1={1: Z_, 2: 'Un tocco in più', 3: C55})

I56 = 'Tutto sui look di tendenza'
issue(56,
      co1_obj1={1: I56, 2: 'Il meglio per te!'},
      co2_obj1={1: 'Trucchi di stile', 2: 'Occhi puntati!', 3: I56},
      co2_obj2={1: 'Il meglio per te!', 2: I56},
      t2n_obj1={1: Z_, 2: I56, 3: 'Voglio tutto!'},
      t2n_obj2={1: SB})

issue(57,
      obj_A1={1: 'Il look di oggi: successo totale!', 2: None},
      obj_A2={1: 'Il look di oggi: piace molto!', 2: None},
      obj_A3={1: 'Il look di oggi: mah, così così…', 2: None},
      obj_B1={1: 'Il look di oggi: super gusto!', 2: None},
      obj_B2={1: 'Il look di oggi: che bella vibrazione!', 2: None},
      obj_B3={1: 'Il look di oggi: atmosfera sobria…', 2: None})
