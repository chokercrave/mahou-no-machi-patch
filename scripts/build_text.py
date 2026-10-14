"""Applica le traduzioni (work/trad/*.json, chiave pagina -> corpo italiano) ai testi 3DS,
reimpacchetta gli archivi e li installa nella mod LayeredFS.
Ordine di priorità: manual > lotti > ds (il primo che ha la chiave vince).
"""
import json, os, re, sys, tempfile, collections
sys.path.insert(0, os.path.dirname(__file__))
import reso, tbaf, textdb
from tm_ds import split_page, page_key
from batch_prep import to_placeholders

# Misure verificate in gioco (pagine di calibrazione):
#  - avanzamento di un carattere = larghezza nel font LC (CWDH) + 2 px; riga utile ~200 px
#    (25 'a'/'m'/'M' per riga, 30 'i' ci stanno)
#  - massimo 3 righe visibili; la terza riga si ferma prima della freccia ▶ (LINE3_PX)
#  - il gioco tagliava la pagina a 64 unità (caratteri + a capo): era il TextBox clonato dalla finestra del dialogo
#    con buffer di 0x40; dalla 1.2 build_code lo alza a 0x80 (provato 13/10: "01 .. 30" su 4 righe tutto visibile)
LINE_PX = 200
LINE3_PX = 170              # terza riga: fino a "20 .. 27" (167 px); con "28" (189 px) finisce sotto la freccia ▶
MAX_LINES = 3
MAX_CH = 120                # unità per pagina (buffer del TextBox del dialogo = 128 con la patch 0x33D968)
OLD_MAX_CH = 64             # slot non dialogo (pagina unica, finestre diverse): limite misurato prima della patch
QUESTION_JP = 12            # pagina col codice di scelta più lunga di così in giapponese = domanda, non opzione
CHOICE_CH = 15             # opzioni: il buffer ne contiene 16 SENZA terminatore -> con 16 compare memoria sporca dopo ("Lucidarla sempre" + resti, 13/10); il gioco taglia a 16
# menu del file 99 (creazione personaggio, sistema): 16 caratteri riempiono il buffer senza terminatore e dopo
# l opzione compare memoria sporca ("Fammi scegliere. W", 13/10) -> lì massimo 15
PAGE_CH_TEST = {}           # slot -> limite di unità per pagina (prove col righello)
GENDER_MARK = '§'            # desinenza o/a secondo il sesso del giocatore -> [$599] (gender_tag.py)
PLURAL_MARK = '¤'            # desinenza plurale i/e secondo il sesso del giocatore -> [$598] (QoL 7: "fidanzat¤")
GENDER_TAG = True
CHOICE = re.compile(r"\[\$1[89]'")   # codice delle opzioni di scelta
CHOICE_PX = 150           # larghezza utile di un'opzione: il riquadro esce dal bordo destro, ~168 = bordo; 150 = margine
NAME_CH = 8                 # lunghezza stimata di un nome inserito dal gioco
NAME_PX = NAME_CH * 8
TAG = re.compile(r'</?c\d*>|<P>|<X\d+>')
_WIDTHS = None


def char_px(ch):
    global _WIDTHS
    if _WIDTHS is None:
        from bcfnt import Bcfnt
        f = Bcfnt(open(os.path.join(textdb.ROOT, 'work', 'font', 'LC.bcfnt'), 'rb').read())
        _WIDTHS = {chr(c): f.widths[g][2][2] for c, g in f.cmap.items()}
    return _WIDTHS.get({GENDER_MARK: 'o', PLURAL_MARK: 'e'}.get(ch, ch), 12) + 2


from tm_ds import TEXTUAL

# Codici che inseriscono testo a runtime: tutti i 5xx tranne quelli che non stampano nulla in italiano
# (511 desinenza, 514 pronome) o sono campi a parte (560/561 destinatario/mittente lettere, 590 contatore).
# Prima contavano solo i codici in TEXTUAL: 517/518/553/555... (nomi di oggetti) valevano 0 -> pagine troncabili.
ITEM_CH = 17                # nomi oggetto: fino a 118 px (blob_texts.ITEM_PX) ~ 17 caratteri
ITEM_CODES = {507, 517, 518, 545, 553, 554, 555, 571, 572, 573, 580}
NO_TEXT = {511, 514, 560, 561, 590, 522}


def inserted_ch(code):
    """caratteri stimati per un codice [$N...] inserito dal gioco"""
    if code in ITEM_CODES:
        return ITEM_CH
    if 500 <= code < 600 and code not in NO_TEXT:
        return NAME_CH
    return 0


def _tag_px(t, tags):
    """larghezza di un segnaposto: i nomi inseriti dal gioco occupano spazio, gli effetti no"""
    if t == '<P>':
        return NAME_PX
    if tags and t in tags:
        m = re.match(r"\[\$(\d+)", tags[t])
        return inserted_ch(int(m.group(1))) * 8 if m else 0
    return NAME_PX


def visible_len(s, tags=None):
    """larghezza in pixel"""
    return sum(char_px(c) for c in TAG.sub('', s)) + sum(_tag_px(t, tags) for t in re.findall(r'<P>|<X\d+>', s))


def wrap(it, tags=None):
    """A capo automatico per riga di LINE_PX pixel; rispetta gli a capo espliciti ('/')."""
    lines = []
    for para in it.split(' / '):
        cur = ''
        for w in para.split(' '):
            if cur and visible_len(cur + ' ' + w, tags) > LINE_PX:
                lines.append(cur); cur = w
            else:
                cur = cur + ' ' + w if cur else w
        lines.append(cur)
    return lines


CODE_TOK = re.compile(r"\[\$[^\]]*\]|\[\[|\[#[0-9A-F]{4}\]|.", re.S)


# [$0'n] (cambio colore): MISURATO in gioco (righello 2026-10-08) che NON occupa posti nel buffer della pagina:
# stesso taglio con e senza 6 colori. (L'ipotesi precedente di 5 unità dava ~2800 divisioni inutili.)
COLOR_UNITS = 0


def _measure(s, units=False):
    """(pixel, caratteri stampati) di un testo con codici reali del gioco.
    units=True: il secondo valore conta anche i cambi colore (COLOR_UNITS, misurato = 0)."""
    px = ch = 0
    for t in CODE_TOK.findall(s):
        if t.startswith('[$'):
            m = re.match(r"\[\$(\d+)", t)
            n = inserted_ch(int(m.group(1))) if m else 0
            if n:
                px += n * 8; ch += n
            elif units and m and int(m.group(1)) == 0:
                ch += COLOR_UNITS
        elif t.startswith('[#'):
            continue
        else:
            c = '[' if t == '[[' else t
            px += char_px(c); ch += 1
    return px, ch


LETTER_CH, LETTER_LINES = 32, 4   # corpo delle lettere: 4 pannelli-riga da 33 caratteri (layout input_letter)


def layout(text, letter=False, max_ch=None, arrow=True):
    """testo con codici reali (' \\n ' = a capo forzato) -> lista di pagine (righe unite da ▼).
    letter=True: righe da LETTER_CH caratteri, fino a LETTER_LINES righe per pagina, nessun limite di 63."""
    max_lines, max_ch = (LETTER_LINES, 10 ** 6) if letter else (MAX_LINES, max_ch or MAX_CH)
    pages, page, n = [], [], 0

    def too_long(s):
        if letter:
            return _measure(s)[1] > LETTER_CH
        idx = len(page) if len(page) < max_lines else 0       # riga che occuperà nella pagina
        return _measure(s)[0] > (LINE3_PX if arrow and idx == MAX_LINES - 1 else LINE_PX)

    def push(l):
        nonlocal page, n
        c = _measure(l, units=not letter)[1]
        if page and (len(page) >= max_lines or n + 1 + c > max_ch):
            pages.append(page); page, n = [], 0
        page.append(l); n += c + (1 if len(page) > 1 else 0)

    for para in text.split('\n'):
        cur = ''
        for w in para.split():
            cand = cur + ' ' + w if cur else w
            if cur and too_long(cand):
                push(cur); cur = w
            else:
                cur = cand
        push(cur)
    pages.append(page)
    return ['▼'.join(p) for p in pages]


def is_letter(where):
    gid = int(where.split(':')[1].split('.')[0]) if ':' in where else 0
    return 98000 <= gid < 99000


def render_batch(it, tags):
    """testo italiano con segnaposto -> testo con codici reali (a capo forzati come \\n)"""
    out = it.replace('[', '[[').replace(' / ', '\n')
    for k, v in {'</c>': "[$0'1]", **tags}.items():
        out = out.replace(k, v)
    return out

ROOT = textdb.ROOT
TRAD = os.path.join(ROOT, 'work', 'trad')
import paths
MODS = os.path.join(paths.MOD, 'romfs')
SOURCES = ['manual_pages.json', 'batch_pages.json', 'ds_pages.json']
ARCHIVES = {  # archivio romfs -> file di testo che contiene
    'message/message.tarc': ['message', 'onemsg'],
    'npc.tarc': ['npc'],
}


def load_trad():
    """(ds: chiave pagina -> corpo con codici,  lotti: giapponese con segnaposto -> italiano con segnaposto)"""
    load = lambda n: json.load(open(os.path.join(TRAD, n), encoding='utf-8')) if os.path.exists(os.path.join(TRAD, n)) else {}
    bt = load('batch_pages.json')
    bt.update(load('manual_pages.json'))
    return load('ds_pages.json'), bt


# La base testi usa il giapponese come chiave: la stessa parola ha UNA traduzione in tutto il gioco.
# Eccezioni per slot preciso (slot -> {giapponese: italiano}):
SLOT_TEXT = {
    'message:99020.14': {'ライムライト': 'Limelight'},     # titolo di canzone, non il bar (Bar Saranno Famosi)
    'message:52007.72': {'うめる<X1>': 'Interrare<X1>'},  # opzione del quiz = parola magica; la stessa chiave altrove ha limite 8
    # QoL 7: Bouquet d'invito (script 128080, patch_relationships): la scelta "pronto?" diventa il tipo di legame
    'message:99033.7': {'心のじゅんびは できた？': 'Che cosa vuoi dichiarare?'},
    'message:99033.8': {'もうだいじょうぶ！<X1>': 'Amore<X1>', 'まだ<X1>': 'Amicizia<X1>'},
    # opzioni della patch (options.py): la voce "Orario" del menu del Prof. Olmo apre le opzioni (script 1021)
    'message:32012.5': {'じかんわり<X1>': 'Opzioni<X1>'},
}

# Slot riscritti per intero (anche slot vuoti): testo finale nel formato del gioco, a capo '▼' già messi.
# Opzioni del Prof. Olmo (options.py, script 1021): 64 domanda -> 65 scelta (-> 59 o 77, indice in var 8392),
# poi lo script mostra 66/67 (viaggio rapido acceso/spento), 73/74 (soldi infiniti) o 78/79 (legami stabili); 59/73/74/77/78/79 erano vuoti.
SLOT_RAW = {
    'message:52000.64': "Vuoi che cambi qualche▼magia per te?[#0000]Quale magia vuoi cambiare?[#0000][$19'65][#0000][#000C]",
    # come le scelte originali (52000.21 -> 22/23): ogni opzione salta a un messaggio di risposta (59/77 erano vuoti)
    'message:52000.65': "[$55][#0000]Viaggio rapido[$19'59][#0000]Soldi infiniti[$19'59][#0000]Legami stabili[$19'59][#0000]Merce nuova[$19'59][#0000]Riusa materiali[$19'59][#0000]Niente[$19'77][#0000][#000C]",
    'message:52000.59': "Vediamo un po'...[#0000][#000C]",
    'message:52000.77': "Va bene. Torna quando vuoi.[#0000][#000C]",
    'message:52000.66': "Ecco fatto! Sulla Mappa▼tocca due volte un luogo▼per arrivarci subito.[#0000][#000C]",
    'message:52000.67': "Va bene: ho sciolto la▼magia del viaggio rapido.[#0000][#000C]",
    'message:52000.73': "Ecco fatto! Da oggi i tuoi▼soldi non finiranno mai.[#0000][#000C]",
    'message:52000.74': "Va bene: i tuoi soldi▼torneranno normali.[#0000][#000C]",
    'message:52000.78': "Ecco fatto! Da oggi i legami▼non caleranno più, anche▼se non vedi qualcuno.[#0000][#000C]",
    'message:52000.84': "Ecco fatto! Nei negozi▼arriva merce nuova, anche▼all'Emporio della Magia.[#0000][#000C]",
    # riusa materiali (options.py, var 4331): 94 acceso / 5 spento (slot vuoti, mai usati dagli script)
    'message:52000.94': "Ecco fatto! Da oggi gli▼incantesimi non useranno▼più i materiali.[#0000][#000C]",
    'message:52000.5': "Va bene: gli incantesimi▼torneranno a consumare i▼materiali.[#0000][#000C]",
    'message:52000.79': "Va bene: i legami con gli▼abitanti torneranno normali.[#0000][#000C]",
}

# Opzioni da tutti i prof (14/10; options.TEACHERS = uno script per prof). Davanti all'aula la domanda
# "quale corso?" saltava subito alla lista dei corsi ([$49'n]): ora salta a un menu nuovo (slot vuoto, non referenziato)
# Scegli il corso / Opzioni / Lascia. In sala professori la voce "Opzioni" si aggiunge al loro menu, prima di "Lascia".
# banco: (righe "quale corso?", salto alla lista, slot menu, slot opzioni o None = 32013.37 di Olmo, script, salto "Lascia")
_TEACH = {32010: ((0, 1, 2, 3), 1007, 72, 73, 1022, 1141, 5),
          32012: ((0, 1, 2, 3), 1208, 70, None, 1021, 1338, None),
          32014: ((0, 1, 2, 3), 1407, 74, 75, 1023, 1574, 5),
          32019: ((50, 51, 52), 1957, 36, 37, 1024, 10758, 55)}
SLOT_EDIT = {}      # slot -> [(vecchio, nuovo)] sul testo gia' tradotto (ogni sostituzione deve avvenire)
for _b, (_lines, _list, _menu, _opt, _sid, _bye, _staff) in _TEACH.items():
    _o = 1337 if _opt is None else (_b - 32000) * 100 + _opt
    _m = (_b - 32000) * 100 + _menu
    for _l in _lines:
        SLOT_EDIT[f'message:{_b}.{_l}'] = [(f"[$19'{_list}]", f"[$19'{_m}]")]
    SLOT_RAW[f'message:{_b}.{_menu}'] = (f"[$55][#0000]Scegli il corso[$19'{_list}][#0000]Opzioni[$19'{_o}][#0000]"
                                         f"Lascia[$19'{_bye}][#0000][#000C]")
    if _opt is not None:
        SLOT_RAW[f'message:{_b}.{_opt}'] = f"Ma certo.[$73'{_sid // 100}'{_sid % 100}'1][#0000][#000C]"
    if _staff is not None:
        SLOT_EDIT[f'message:{_b}.{_staff}'] = [(f"[#0000]Lascia[$19'{_bye}]", f"[#0000]Opzioni[$19'{_o}][#0000]Lascia[$19'{_bye}]")]
# Reginaldo (capo dormitorio, npc 2013; options.HELPERS script 1025): non e' un gran mago, chiede al Preside.
# Menu 32082.4 + "Opzioni" -> 32082.60; slot vuoti fuori dagli intervalli casuali [$17'8205'8259] / [$17'8310'8349].
SLOT_EDIT['message:32082.4'] = [("[#0000]Lascia[$19'8379]", "[#0000]Opzioni[$19'8260][#0000]Lascia[$19'8379]")]
_REG = {
    '32082.60': "Le magie della città? Non▼sono un gran mago...[#0000]Però posso chiederle al▼Preside per te![$73'10'25'1][#0000][#000C]",
    '32082.61': "Cosa vuoi che chieda al▼Preside?[#0000][$19'8262][#0000][#000C]",
    '32082.62': ("[$55][#0000]Viaggio rapido[$19'8263][#0000]Soldi infiniti[$19'8263][#0000]Legami stabili[$19'8263][#0000]"
                 "Merce nuova[$19'8263][#0000]Riusa materiali[$19'8263][#0000]Niente[$19'8264][#0000][#000C]"),
    '32082.63': "D'accordo, vado subito a▼chiederglielo![#0000][#000C]",
    '32082.64': "Va bene. Torna quando vuoi.[#0000][#000C]",
    '32082.65': 'Fatto! Il Preside ha▼lanciato la magia.[#0000]' + "Sulla Mappa tocca due▼volte un luogo per▼arrivarci subito.[#0000][#000C]",
    '32082.77': 'Fatto! Il Preside ha▼sciolto la magia.[#0000]' + "Niente più viaggio rapido▼sulla Mappa.[#0000][#000C]",
    '32082.78': 'Fatto! Il Preside ha▼lanciato la magia.[#0000]' + "Da oggi i tuoi soldi▼non finiranno mai.[#0000][#000C]",
    '32082.79': 'Fatto! Il Preside ha▼sciolto la magia.[#0000]' + "I tuoi soldi torneranno▼normali.[#0000][#000C]",
    '32083.1': 'Fatto! Il Preside ha▼lanciato la magia.[#0000]' + "Da oggi i legami non▼caleranno più, anche▼senza vedervi.[#0000][#000C]",
    '32083.3': 'Fatto! Il Preside ha▼sciolto la magia.[#0000]' + "I legami con gli abitanti▼torneranno normali.[#0000][#000C]",
    '32083.88': 'Fatto! Il Preside ha▼lanciato la magia.[#0000]' + "Nei negozi arriva merce▼nuova, anche all'Emporio▼della Magia.[#0000][#000C]",
    '32083.89': 'Fatto! Il Preside ha▼lanciato la magia.[#0000]' + "Da oggi gli incantesimi▼non useranno più i▼materiali.[#0000][#000C]",
    '32083.90': 'Fatto! Il Preside ha▼sciolto la magia.[#0000]' + "Gli incantesimi torneranno▼a consumare i materiali.[#0000][#000C]",
}
SLOT_RAW.update({f'message:{k}': v for k, v in _REG.items()})
SLOT_DONE = set()


RAW_DONE = set()     # slot di SLOT_RAW che esistono davvero nel gruppo (altrimenti verrebbero ignorati)


def edit_slot(where, text):
    for old, new in SLOT_EDIT.get(where, ()):
        assert text and text.count(old) == 1, f'{where}: {old!r} non trovato in {text!r}'
        text = text.replace(old, new)
        SLOT_DONE.add(where)
    return text


OVERFLOW = []   # pagine troppo lunghe in slot dove non si possono aggiungere pagine
SHOP_LOG = []   # (dove, prima, dopo) delle pagine toccate da fix_shops (scritto in work/trad/shops_log.tsv)

# Insegne come nel DS EUROPEO: Harrows, Vivian's Boutique, Daisy's Flowers (make_signs.py)
# Nomi dei negozi "MISTO": nei dialoghi il nome del GLOSSARIO DS, e alla prima
# menzione di ogni conversazione l'insegna che si vede in gioco tra parentesi, es. "I fiori di Viola
# (Flowerdaisy)". Il negozio si riconosce dal GIAPPONESE (le traduzioni hanno varianti).
# (giapponese, nome DS, insegna o None, genere: m | mv (maschile, vocale) | f | mpl | ipl ("I ..."), varianti IT)
SHOPS = [
    (('フラワーデイジー',), 'I fiori di Viola', "Daisy's Flowers", 'ipl',
     ['I fiori di Viola', 'I Fiori di Viola', 'Fiori Viola', 'fiori di Viola', 'Fiori di Viola', 'Flowerdaisy']),
    (('ハロゲンデパート', 'ハロゲン'), 'Grandi Magazzini Freccia', 'Harrows', 'mpl',
     ['Grandi Magazzini Freccia', 'Grandi Magazzini Alogeni', 'Grandi Magazzini Halogen', 'Grande Magazzino Halogen',
      'Magazzini Halogen', 'magazzini Halogen', 'grande magazzino Halogen']),
    (('ライムライト',), 'Bar Saranno Famosi', 'Lime Light', 'm',
     ['Bar Saranno Famosi', 'Saranno Famosi', 'Bar Famosi', 'Lime Light', 'Limelight']),
    (('スマイル・ビビ', 'スマイルビビ'), 'Boutique Vivian', "Vivian's Boutique", 'f',
     ['Boutique Vivian', 'Boutique di Vivian', 'Da Vivian', 'Smile Vivi', 'Smile Bibi']),
    (('モン・パリ',), 'Acconciature Mon Paris', None, 'fpl', ['Acconciature Mon Paris', 'Mon Paris']),
    (('かめや',), 'Emporio della Magia', None, 'mv', ['Emporio della Magia', 'Emporio', 'Tartaruga']),
    (('恋人みさき', 'こいびとみさき'), 'Punta degli Innamorati', None, 'f',
     ['Punta degli Innamorati', 'Punta degli innamorati', 'Capo degli Innamorati', 'Promontorio degli Innamorati']),
]
# articolo/preposizione articolata davanti al nome -> forma giusta per il genere del nome DS
_ART = {
    'mv': {'il': "l'", 'lo': "l'", 'la': "l'", 'alla': "all'", 'della': "dell'", 'dalla': "dall'", 'nella': "nell'", 'da': "dall'", 'al': "all'", 'del': "dell'", 'dal': "dall'", 'nel': "nell'", 'sul': "sull'"},
    'f': {'il': 'la', 'lo': 'la', 'al': 'alla', 'del': 'della', 'dal': 'dalla', 'nel': 'nella', 'sul': 'sulla',
          "l'": 'la', "all'": 'alla', "dell'": 'della', "dall'": 'dalla', "nell'": 'nella', 'da': 'dalla'},
    'fpl': {'il': 'le', 'lo': 'le', 'al': 'alle', 'del': 'delle', 'dal': 'dalle', 'nel': 'nelle', 'sul': 'sulle'},
    'mpl': {'il': 'i', 'lo': 'i', 'da': 'dai', 'al': 'ai', 'del': 'dei', 'dal': 'dai', 'nel': 'nei', 'sul': 'sui'},
    'ipl': {'il': 'i', 'lo': 'i', 'da': 'dai', 'al': 'ai', 'del': 'dei', 'dal': 'dai', 'nel': 'nei', 'sul': 'sui',
            'i': 'i', 'ai': 'ai', 'dei': 'dei', 'dai': 'dai', 'nei': 'nei', 'sui': 'sui'},
    'm': {"l'": 'il', "all'": 'al', "dell'": 'del', "dall'": 'dal', "nell'": 'nel', 'lo': 'il', 'la': 'il',
          'alla': 'al', 'della': 'del', 'dalla': 'dal', 'nella': 'nel'},
}
_COL = r"\[\$0'\d+\]"

# Rivista ベリーズ ("Berry's" nella traduzione): rinominata "Spell & Spill" (gioco di parole:
# incantesimi + pettegolezzi). Solo la rivista (riconosciuta dal giapponese); i mobili "berry" restano.
MAGAZINE = ('ベリーズ', "Berry's", 'Spell ＆ Spill')   # ＆ a tutta larghezza: nel font lo slot '&' è la ù della tastiera
_ART_S = {'il': 'lo', 'del': 'dello', 'al': 'allo', 'dal': 'dallo', 'nel': 'nello', 'sul': 'sullo', 'un': 'uno'}


def fix_magazine(text, jp):
    if MAGAZINE[0] not in jp:
        return text

    def rep(m):
        art = m.group(1)
        new = ''
        if art is not None:
            a = _ART_S.get(art.lower(), art)
            new = (a[0].upper() + a[1:] if art[0].isupper() else a) + ' '
        return new + (m.group(2) or '') + MAGAZINE[2]
    return re.sub(r"(?:(?<![\w'])(il|del|al|dal|nel|sul|un|Il|Del|Al|Dal|Nel|Sul|Un)\s+)?(" + _COL + r")?"
                  + re.escape(MAGAZINE[1]), rep, text)


_PRESIDE_ART = {'la': 'il', 'La': 'Il', 'della': 'del', 'Della': 'Del', 'alla': 'al', 'Alla': 'Al', 'dalla': 'dal',
                'Dalla': 'Dal', 'nella': 'nel', 'Nella': 'Nel', 'sulla': 'sul', 'Sulla': 'Sul'}


def fix_preside(text, jp):
    """Come nel DS italiano: quando i personaggi nominano il preside (校長(先生) col codice
    colore del nome) e' "Preside Sol"; la targhetta del nome e le intestazioni restano "Preside". Il ruolo generico
    ("un preside", "mai preside") non cambia. Corregge anche il genere sbagliato della traduzione ("la Preside")."""
    if '校長' not in jp or '<c3>Preside</c>' not in text:
        return text
    text = re.sub(r'(?<!\bun )(?<!\bmai )<c3>Preside</c>', '<c3>Preside Sol</c>', text)
    return re.sub(r"\b(" + '|'.join(_PRESIDE_ART) + r")( <c3>Preside Sol</c>)",
                  lambda m: _PRESIDE_ART[m.group(1)] + m.group(2), text)


def fix_shops(text, jp, seen, sign_ok):
    """normalizza i nomi dei negozi in `text` (codici reali); `seen` = negozi già nominati nella conversazione"""
    for keys, name, sign, gender, variants in SHOPS:
        if not any(k in jp for k in keys):
            continue
        alts = '|'.join(re.escape(v) for v in sorted(variants, key=len, reverse=True))
        pat = re.compile(r"(?:(?<![\w'])(\w+'?|[Ll]'|[Dd]ell'|[Aa]ll'|[Dd]all'|[Nn]ell')\s*)?(" + _COL + r")(?:" + alts + r")(\[\$0'1\])")

        def rep(m):
            art, col, end = m.group(1), m.group(2), m.group(3)
            shown = name
            pre = ''
            if gender == 'ipl':                       # "I fiori di Viola": l'articolo si fonde con la preposizione
                shown = name[2:].capitalize() if name.startswith('I ') else name
                shown = 'Fiori di Viola' if shown.lower() == 'fiori di viola' else shown
            if art is not None:
                low = art.lower()
                new = _ART.get(gender, {}).get(low, art)
                if gender == 'ipl' and low not in _ART['ipl']:
                    shown = name                          # nessuna preposizione: si tiene "I fiori di Viola"
                if art[0].isupper():
                    new = new[0].upper() + new[1:]
                pre = new + ('' if new.endswith("'") else ' ')
            elif gender == 'ipl':
                shown = name
            tail = ''
            if sign and sign_ok and name not in seen:
                tail = f' ({sign})'
            seen.add(name)
            return f'{pre}{col}{shown}{end}{tail}'
        text = pat.sub(rep, text)
    return text


def can_split(slot, where):
    """Si possono aggiungere pagine? No per: fumetti onemsg (varianti a posizione fissa),
    lettere 98xxx (campi destinatario|corpo|mittente), didascalie della rivista 991xx."""
    if where.startswith('onemsg') or "[$560]" in slot or "[$561]" in slot:
        return False
    gid = int(where.split(':')[1].split('.')[0]) if ':' in where else 0
    return not (98000 <= gid < 99000 or 99100 <= gid < 99200)


def translate_slot(slot, db, stats, where=''):
    ds, bt = db
    dialogue = can_split(slot, where)
    pages = []
    shops_seen = set()
    for p in textdb.split_pages(slot):
        lead, body, trail = split_page(p)
        if textdb.JP.search(body):
            stats['tot'] += 1
            jp, tags = to_placeholders(body + trail)
            text = None
            if jp in SLOT_TEXT.get(where, ()):
                stats['ok'] += 1
                text = render_batch(SLOT_TEXT[where][jp], tags)
            elif jp in bt:
                stats['ok'] += 1; stats['bt'] += 1
                text = render_batch(bt[jp], tags)          # contiene già la coda (trail)
            elif page_key(body) in ds:
                stats['ok'] += 1
                text = ds[page_key(body)].replace('▼', ' ') + trail
            if text is not None and jp not in SLOT_TEXT.get(where, ()):
                before = text
                text = fix_shops(text, body, shops_seen, dialogue and not CHOICE.search(trail))
                text = fix_magazine(text, body)
                text = fix_preside(text, body)
                if text != before:
                    stats['shops'] += 1
                    SHOP_LOG.append((where, before, text))
            if text is not None and CHOICE.search(trail) and len(textdb.norm(body)) > QUESTION_JP:
                # pagina con codice di scelta ma lunga già in giapponese: è la DOMANDA (riquadro del
                # dialogo), non un'opzione. A capo normale, ma resta una sola pagina.
                one = re.sub(r'\s+', ' ', text.replace(' // ', ' ').replace('\n', ' ')).strip()
                parts = layout(one.replace('▼', ' '))
                if len(parts) > 1:
                    OVERFLOW.append((where, jp))
                    stats['overflow'] += 1
                pages.append(lead + '▼'.join(parts))
                continue
            if text is not None and CHOICE.search(trail):
                # opzione di un menu di scelta ([$19'n] menu, [$18'n] risposte dei quiz delle lezioni): una sola riga, mai divisa (le pagine sono le opzioni)
                one = re.sub(r'\s+', ' ', text.replace('▼', ' ').replace(' // ', ' ').replace('\n', ' ')).strip()
                vis = len(re.sub(r'\[\$[^\]]*\]', '', one).replace('[[', '['))
                if _measure(one)[0] > CHOICE_PX or vis > CHOICE_CH:
                    OVERFLOW.append((where, jp))
                    stats['choice_long'] += 1
                p = lead + one
                pages.append(p)
                continue
            if text is not None:
                parts = []
                for chunk in text.split(' // '):        # ' // ' = nuova pagina esplicita
                    parts += layout(chunk, letter=is_letter(where), max_ch=PAGE_CH_TEST.get(where) or (None if dialogue else OLD_MAX_CH), arrow=dialogue)
                if text.startswith(' ') and parts and not parts[0].startswith(' '):
                    parts[0] = ' ' + parts[0]           # suffisso attaccato a un nome dal gioco: "Naomi" + " abita qui"
                if len(parts) > 1 and not dialogue:
                    OVERFLOW.append((where, jp))
                    stats['overflow'] += 1
                    parts = ['▼'.join(parts)]           # resta una pagina (verrà troncata)
                if len(parts) > 1:
                    stats['split'] += 1
                p = ('[#0000]' + lead).join(lead + parts[0:1][0] if i == 0 else x for i, x in enumerate(parts))
            if text is not None:
                # pronome del personaggio: vuoto in italiano (come nel DS); il suo campo NPC ora
                # ospita la coda dei nomi lunghi (build_npc), quindi non va mai stampato
                p = p.replace("[$514'0]", '')
        pages.append(p)
    return ('[#0000]'.join(pages).replace(GENDER_MARK, '[$599]' if GENDER_TAG else 'o')
            .replace(PLURAL_MARK, '[$598]' if GENDER_TAG else 'i'))


def main():
    db = load_trad()
    groups = textdb.load_all()
    tmp = tempfile.mkdtemp()
    for arc, names in ARCHIVES.items():
        repl = {}
        for name in names:
            stats = collections.Counter()
            if name == 'npc':
                continue  # struttura binaria: gestita a parte (nomi/pronomi)
            for g in groups[name]:
                if 'text' in g:
                    g['text'] = translate_slot(g['text'], db, stats, f"{name}:{g['id']}")
                else:
                    RAW_DONE.update(k for k in (f"{name}:{g['id']}.{i}" for i in range(len(g['slots']))) if k in SLOT_RAW)
                    g['slots'] = [SLOT_RAW.get(f"{name}:{g['id']}.{i}") or
                                  edit_slot(f"{name}:{g['id']}.{i}",
                                            translate_slot(s, db, stats, f"{name}:{g['id']}.{i}") if s else s)
                                  for i, s in enumerate(g['slots'])]
            rd, rx = os.path.join(tmp, name + '.rdbt'), os.path.join(tmp, name + '.rndx')
            reso.save(groups[name], rd, rx)
            repl[name + '.rdbt'] = open(rd, 'rb').read()
            repl[name + '.rndx'] = open(rx, 'rb').read()
            print(f'{name:10} pagine tradotte {stats["ok"]}/{stats["tot"]} ({100 * stats["ok"] / max(stats["tot"], 1):.1f}%), '
                  f'di cui nuove {stats["bt"]}; divise in più pagine {stats["split"]}; troppo lunghe (non divisibili) {stats["overflow"]}; '
                  f'opzioni di scelta troppo lunghe {stats["choice_long"]}')
        if not repl:
            continue
        out = os.path.join(MODS, arc)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        tbaf.rebuild(os.path.join(ROOT, 'work', '3ds', 'romfs', arc), repl, out)
        chk = {e['name']: tbaf.decompress(e['data']) if e['comp'] else e['data'] for e in tbaf.parse(open(out, 'rb').read())}
        assert all(chk[k] == v for k, v in repl.items())
    with open(os.path.join(TRAD, 'overflow.tsv'), 'w', encoding='utf-8') as f:
        for where, jp in OVERFLOW:
            f.write(f'{where}\t{jp}\n')
    with open(os.path.join(TRAD, 'shops_log.tsv'), 'w', encoding='utf-8') as f:
        for where, a, b in SHOP_LOG:
            f.write(f'{where}\t{a}\t{b}\n')
    print(f'nomi dei negozi sistemati in {len(SHOP_LOG)} pagine (work/trad/shops_log.tsv)')
    assert SLOT_DONE == set(SLOT_EDIT), f'slot non modificati: {set(SLOT_EDIT) - SLOT_DONE}'
    assert RAW_DONE == set(SLOT_RAW), f'slot riscritti inesistenti: {set(SLOT_RAW) - RAW_DONE}'
    print('mod aggiornata')


if __name__ == '__main__':
    main()
