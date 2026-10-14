"""Traduce sul posto le stringhe UTF-16 di exefs/code.bin (work/trad/code_it.tsv: indirizzo, jp, it)
e scrive una patch IPS in mods/<titleid>/exefs/code.ips (Azahar la applica all'avvio).
Ogni stringa italiana deve stare nello spazio del giapponese più gli zeri di riempimento che seguono.
"""
import os, struct, sys

ROOT = os.path.join(os.path.dirname(__file__), '..')
CODE = os.path.join(ROOT, 'work', '3ds', 'exefs', 'code.bin')
import paths
OUT = os.path.join(paths.MOD, 'exefs', 'code.ips')
BASE = 0x100000
# fine di .rodata (exheader: 0x54b000 + 0x3c5ec) fino al limite della pagina: mappato, non usato, a zero
FREE_START, FREE_END = 0x5875ec, 0x588000


# Patch di istruzioni (indirizzo, word originale, word nuova), little-endian ARM.
# Voce parlata (borbottio): la funzione 0x241648 raggruppa i caratteri in sillabe; con soli caratteri
# < 0x1000 (latino) usa 6 caratteri per sillaba (4 in modalità veloce) contro i 3 (2) del giapponese,
# quindi il borbottio dei testi italiani finiva a metà. Con 3 (come il giapponese) copre ~75% della scrittura,
# lo stesso rapporto dell'originale; provato anche 2 (copre quasi tutto), si e' preferito tornare a 3.
INSN_PATCHES = [
    (0x241670, 0xE3A0C006, 0xE3A0C003),   # mov ip, #6 -> #3   (caratteri per sillaba, latino)
    (0x2416AC, 0xE3A0C004, 0xE3A0C002),   # mov ip, #4 -> #2   (idem, modalità veloce = passo del giapponese)
    # Tastiera dei nomi: scheda iniziale. L'init 0x263e84 legge la modalità [obj+0x38]: 2 -> scheda ABC con le altre
    # spente (0x263f88), altrimenti scheda 0 = Hiragana con tutte accese. [obj+0x46] = scheda (0 Hira, 1 Kata, 2 ABC).
    # r1 vale 2 (mov r1,#2 a 0x263ec8): così si apre su ABC e le quattro schede restano usabili (GDB 10/10).
    (0x263EE4, 0xE5C45046, 0xE5C41046),   # strb r5, [r4, #0x46] -> strb r1, [r4, #0x46]
    # ...ma all'apertura (0x264138, chiamata da 0x2d9b30) la scheda viene rimessa a 0 se la modalità non è 2/3
    # (strbne r6 con r6=0), altrimenti a 0x264174 vale la modalità (r0). Si passa sempre da 0x264174 con r0=2 nel
    # caso generale: le modalità 2/3 restano invariate, poi 0x265854 carica la tabella della scheda (GDB 10/10).
    (0x264144, 0x15C46046, 0x13A00002),   # strbne r6, [r4, #0x46] -> movne r0, #2
    (0x264148, 0x0A000009, 0xEA000009),   # beq 0x264174 -> b 0x264174
    # Nome del dialogo dei libri (cataloghi): la funzione 0x321fb4 copiava il nome in un campo da 10 caratteri
    # (obj+0x1d8, seguito da altri campi) con 0x152a94(dst, src, 10): massimo 9 caratteri ("Catalogoi"). Gli NPC normali
    # passano invece direttamente il puntatore al nome. Qui anche i libri passano il puntatore alla stringa (r1) e il
    # dialogo la copia subito nel suo buffer da 15 caratteri (0x33d874); la copia da 10 sparisce.
    (0x322084, 0xE3A0200A, 0xE1A06001),   # mov r2, #10      -> mov r6, r1   (r6 = stringa sorgente)
    (0x322088, 0xE2840F76, 0xE1A00000),   # add r0, r4, #0x1d8 -> nop
    (0x32208C, 0xEBF8C280, 0xE1A00000),   # bl 0x152a94       -> nop
    (0x322090, 0xE2846F76, 0xE1A00000),   # add r6, r4, #0x1d8 -> nop
    # SpotPass all'avvio: la macchina a stati 0x396ba0 (stato = byte obj+0x2d, tabella 0x396bb0) nello stato 0x2b
    # chiama 0x20fb20, poi se 0x4df9c8 (gia' registrato) != 0 va allo stato 0x2d; altrimenti mostra la domanda
    # (messaggio 99/180 = 99001.80, via 0x10cfa0 -> 0x11f3a0 -> 0x132f24) e passa allo stato 0x2c (risposta ->
    # 0xb5 "registrato" / 0xb6 "non utilizzabile" -> stato 0x36). Il servizio e' chiuso: invece della domanda si
    # salta a 0x396d4c (mov r0,#0x36), la stessa uscita che il gioco usa quando obj+0x2e == 4. Nessuna registrazione,
    # come rispondere "No"; lo stato 0x36 chiude il riquadro "Controllo dei dati ricevuti" e passa al titolo.
    (0x397BDC, 0xE3A000B4, 0xEAFFFC5A),   # mov r0, #0xb4 -> b 0x396d4c
    # Avvio senza loghi (1.1, "niente intro"): scena loghi = macchina a stati 0x1ffb40 (stato [r4+0x2c], tabella 0x1ffb5c).
    # Stato 2 apre i menu 0x8f/0x90 e trova le parti (restano: mai togliere parti DMST, crash 0.9.3), poi andava al 3
    # (2 loghi: entrata 60 + attesa 180/60 + uscita 60 frame, tabelle 0x5985c0/c8/c4). Si va diretti all'8 (dissolvenza
    # finale, colore 0x611e20, pool 0x20012c) con 1 frame invece di 60: 0x13efdc dimezza i frame e forza 0 -> 1.
    # Dopo lo stato 2 il codice CADE nel corpo dello stato 3 (0x1ffd20, nessun salto) che rimette lo stato a 4: per
    # saltare davvero i loghi si esce subito con lo stato 8 dall'uscita comune 0x200020 (strb r0,[r4,#0x2c]; ritorno).
    # Video a 60 fps del 10/10: senza il salto restavano attese 180+60 frame e 4 dissolvenze (~12 s).
    (0x1FFD18, 0xE3A00003, 0xE3A00008),   # mov r0, #3    -> mov r0, #8
    (0x1FFD1C, 0xE5C4002C, 0xEA0000BF),   # strb r0, [r4, #0x2c] -> b 0x200020
    # L'init della scena (0x1ffb14/0x1ffb24) copre i due schermi col colore del pool 0x1ffb38 = 0x611e50 = BIANCO
    # (costanti lette in RAM: 0x611e20 nero, 0x611e50 bianco): senza loghi restava un lampo bianco di 3 frame. -> nero.
    (0x1FFB38, 0x00611E50, 0x00611E20),   # pool: colore iniziale bianco -> nero
    (0x1FFFA8, 0xE3A0103C, 0xE3A01001),   # mov r1, #0x3c -> mov r1, #1
    # Orologio della borsa a 24 ore: 0x2ecd40 (aggiornamento data/ora della borsa, menu 62 = pc_action_bg_00, slot 9)
    # calcola PM = ora >= 12 e ora % 12 come ora - 12 * (ora * 0xAAAAAAAB >> 35); le 4 cifre hhmm vanno nelle parti
    # 8..11 (obj+0x11a8 / +0x11ec, due serie di sprite), A/P nella parte 12. Con il quoziente a 0 l'ora resta 0..23;
    # le parti A/P e M (Pos_date_num_10/11) sono spostate fuori schermo nel layout (build_ui PANE_EDITS).
    (0x2ECDB8, 0xE1A021A2, 0xE3A02000),   # lsr r2, r2, #3 -> mov r2, #0
    # Filtro parolacce di sistema (nn::ngc, archivio "ngword:"): 0x21bac0(str) = 1 se il testo contiene parole vietate
    # (ricerca per sottostringa: "Shelley" -> "hell") o piu' di 5 cifre. Chiamato dal controllo del nome (0x2659e8)
    # e da 0x2136f0. Rimosso del tutto: ritorna sempre 0 = testo valido.
    (0x21BAC0, 0xE92D4033, 0xE3A00000),   # push {r0,r1,r4,r5,lr} -> mov r0, #0
    (0x21BAC4, 0xE24DD03C, 0xE12FFF1E),   # sub sp, sp, #0x3c     -> bx lr
    # Seconda lista di parole vietate, interna al gioco: 0x261fe8(kb, maschera) mette il nome in minuscolo e cerca ogni
    # parola della lista (kb+0x28, lunghezza kb+0x2c) come sottostringa (memcmp 0x194250). Con maschera=0 (tasto OK,
    # 0x2659fc) ritorna 0 -> popup "nome non valido" e nome cancellato ("Shelley" -> "hell", 1.0 su 3DS); con maschera=1
    # copre le parole con spazi nel buffer della tastiera 0x5ff814 (chiamata solo dopo un rifiuto). Rimosso del tutto
    #: ritorna sempre 1 = valido; il corpo diventa spazio libero (GAME_NG_CAVE).
    # Lezioni a qualsiasi ora (QoL 8, 1.2): 0x27c92c calcola il turno della lezione (var 4306: 1/2/3 = prof 2001/2002/2003
    # in cattedra, script 50001..; 0 = nessuno) solo se l'ora è nella fascia [r5, r8) = 8-20, o 12-24 con l'orario
    # scelto da Olmo (var 3150105 = 1). Turno = ((ora - r5)*2 + mezz'ora + giorno) mod 5 (+1, salta il 4). Fascia di 24 ore
    # con inizio spostato di 10/15 ore (multipli di 5 ore = 10 mezz'ore): alle ore di prima resta lo stesso professore.
    (0x27C938, 0xE3A05008, 0xE3E05001),   # mov r5, #8      -> mvn r5, #1   (-2)
    (0x27C940, 0xE3A08014, 0xE3A08018),   # mov r8, #20     -> mov r8, #24
    (0x27C980, 0x03A0500C, 0x03E05002),   # moveq r5, #12   -> mvneq r5, #2 (-3)
    # Pagine a 3 righe (1.2): la finestra del dialogo (0x33d934) clona il pannello Txt_mes_win in un TextBox nuovo
    # (ctor 0x42d828 -> base 0x4333e0) con buffer di 0x40 caratteri: oltre il 64° (a capo inclusi) il testo era
    # tagliato ("20 21 2" sulla pagina numerata, 13/10; buffer 130 byte in RAM). Il parser copia fino a 192 e il pannello
    # del layout ne ha 203: si alza il clone a 128 (AllocStringBuffer alloca anche i vertici dei glifi in proporzione).
    (0x33D968, 0xE3A01040, 0xE3A01080),   # mov r1, #0x40 -> mov r1, #0x80
    (0x261FE8, 0xE92D4FF0, 0xE3A00001),   # push {r4-fp, lr}    -> mov r0, #1
    (0x261FEC, 0xE24DDF4D, 0xE12FFF1E),   # sub sp, sp, #0x134  -> bx lr
    # QoL 1.2 negozi 24/7 (con patch_shop_hours.py): tabella dei trigger orari in .rodata (record da 16 byte, valutati da
    # FUN_002a9664/0x2a9264, eseguiti da 0x2a97c4; GDB 13/10). [0] mappa, [2] ora, [3] 0x64 = "ora == [2]",
    # 0x7e = "ora == [2] e minuti >= 50", [4] tipo (1 = avvia evento [0xc]*100+[0xe], 6 = musica di chiusura).
    # Alla chiusura il commesso caccia fuori il giocatore (eventi 21x80, 224000, 300180); alle 23:50 musica di chiusura
    # (var 3211524 -> BGM 0x42 nelle mappe 45/46/52). Ora 99 = mai.
    (0x54D168, 0x6400002D, 0x6463002D),   # mappa 45, ora 0 -> 99 (evento 211/80)
    (0x54D178, 0x6400002E, 0x6463002E),   # mappa 46, ora 0 -> 99 (evento 211/80)
    (0x54D188, 0x64000033, 0x64630033),   # mappa 51, ora 0 -> 99 (evento 212/80)
    (0x54D198, 0x64000034, 0x64630034),   # mappa 52, ora 0 -> 99 (evento 211/80)
    (0x54D1A8, 0x64000037, 0x64630037),   # mappa 55, ora 0 -> 99 (evento 213/80)
    (0x54D1B8, 0x6400003A, 0x6463003A),   # mappa 58, ora 0 -> 99 (evento 215/80)
    (0x54D1C8, 0x6400003C, 0x6463003C),   # mappa 60, ora 0 -> 99 (evento 218/80)
    (0x54D1D8, 0x6400003D, 0x6463003D),   # mappa 61 (poste), ora 0 -> 99 (evento 216/80)
    (0x54D1E8, 0x6400003E, 0x6463003E),   # mappa 62 (banca), ora 0 -> 99 (evento 214/80)
    (0x54D1F8, 0x64040039, 0x64630039),   # mappa 57 (bar), ora 4 -> 99 (evento 217/80)
    (0x54D208, 0x7E17002D, 0x7E63002D),   # mappa 45, 23:50 -> mai (musica di chiusura)
    (0x54D218, 0x7E17002E, 0x7E63002E),   # mappa 46, 23:50 -> mai
    (0x54D228, 0x7E170034, 0x7E630034),   # mappa 52, 23:50 -> mai
    (0x54D278, 0x64000158, 0x64630158),   # mappa 344 (sala), ora 0 -> 99 (evento 2240/0 = script 224000)
    (0x54D288, 0x64000178, 0x64630178),   # mappa 376, ora 0 -> 99 (evento 3001/80 = script 300180)
]


def apply_insn_patches(d):
    for addr, old, new in INSN_PATCHES:
        o = addr - BASE
        assert struct.unpack_from('<I', d, o)[0] == old, f'{addr:#x}: istruzione originale diversa'
        struct.pack_into('<I', d, o, new)


def apply_name_plate(d):
    """targhetta del nome dinamica (vedi name_plate.py): routine nel riempimento in fondo a .text"""
    sys.path.insert(0, os.path.dirname(__file__))
    import name_plate as np_
    code, _ = np_.build()
    o = np_.CAVE - BASE
    assert d[o:o + len(code)] == b'\0' * len(code), 'spazio della routine non libero'
    d[o:o + len(code)] = code
    for site in np_.CALL_SITES:
        so = site - BASE
        old = struct.unpack_from('<I', d, so)[0]
        assert old >> 24 == 0xEB and site + 8 + ((old & 0xFFFFFF) << 2) - (1 << 26 if old & 0x800000 else 0) \
            == np_.SET_STRING, f'{site:#x}: non è bl {np_.SET_STRING:#x}'
        struct.pack_into('<I', d, so, np_.call_patch(site))
    # patente: nomi di bacchetta e cappello in campi da 40 caratteri (license_names.py), subito dopo
    import license_names as ln
    base = (np_.CAVE + len(code) + 3) & ~3
    lcode, lab = ln.build(base)
    assert base + len(lcode) <= np_.CAVE_END, 'spazio finito nel riempimento di .text'
    o = base - BASE
    assert d[o:o + len(lcode)] == b'\0' * len(lcode)
    d[o:o + len(lcode)] = lcode
    for site, kind, target, label in ln.SITES:
        so = site - BASE
        old = struct.unpack_from('<I', d, so)[0]
        off = old & 0xFFFFFF
        off = off - (1 << 24) if off & 0x800000 else off
        assert (old >> 24) == (0xEB if kind == 'bl' else 0xEA) and site + 8 + off * 4 == target, \
            f'{site:#x}: non è {kind} {target:#x}'
        struct.pack_into('<I', d, so, ln.branch(site, lab[label], kind == 'bl'))
    # targhetta dinamica dei nomi di oggetti/parole (pop_plate.py): il codice sta nello spazio nn::ngc (apply_ngc_cave),
    # qui solo le tabelle delle larghezze in .rodata (DF_kyougeki per name_plate, LC per pop_plate)
    import pop_plate as pp
    for addr, tab in ((np_.TABLE, np_.width_table()), (pp.TABLE, pp.width_table())):
        o = addr - BASE
        assert d[o:o + 256] == bytes(256), f'{addr:#x}: spazio della tabella non libero'
        d[o:o + 256] = bytes(tab)
    base2 = base + len(lcode)
    pcode = b''
    # patente, riga della scuola: "Scuola di magia <città>" invece di "<città>:Scuola" (license_school.py)
    import license_school as ls
    base3 = (base2 + len(pcode) + 3) & ~3
    scode, measure = ls.build(base3)
    assert base3 + len(scode) <= np_.CAVE_END, 'spazio finito nel riempimento di .text (license_school)'
    o = base3 - BASE
    assert d[o:o + len(scode)] == bytes(len(scode))
    d[o:o + len(scode)] = scode
    so = ls.SITE - BASE
    assert struct.unpack_from('<I', d, so)[0] == ls.EXPECT[0], f'{ls.SITE:#x}: istruzione inattesa'
    for k, w in enumerate(ls.patch_words(measure)):
        struct.pack_into('<I', d, so + 4 * k, w)

# Spazio per codice nuovo: il filtro parolacce e' spento (INSN_PATCHES 0x21BAC0 -> mov r0,#0; bx lr), quindi il blocco
# nn::ngc che solo lui chiamava (0x3f644c-0x3f6f4f) e' codice morto: riferimenti esterni solo dal filtro e dal puntatore
# 0x579ed0 dello stato ngc (usato solo da ngc). NON usare 0x3f6f50+ (chiamato da 0x3f77a4) ne' prima di 0x3f644c.
NGC_CAVE, NGC_CAVE_END = 0x3F644C, 0x3F6F50
# Altro spazio libero (1.1): corpo della lista parole vietate del gioco 0x261fe8, spenta all'ingresso (INSN_PATCHES).
# Nessun salto o puntatore esterno punta dentro (scansione 10/10); pool incluso (0x262180 = 0x5ff814). 404 byte.
GAME_NG_CAVE, GAME_NG_CAVE_END = 0x261FF0, 0x262184


def apply_game_ng_cave(d):
    """Etichetta "おみせ" della lista prodotti (goods_list_bar Txt_shop, buffer 8): 0x3078d8 `addlo r1, pc` punta al
    letterale locale 0x307a84 (3 caratteri, troppo corto per "Negozio"). Diventa `ldrlo r1, [pc]` (stesso scostamento):
    in 0x307a84 si scrive il puntatore a "Negozio" nello spazio GAME_NG_CAVE (corpo della lista parole vietate)."""
    assert any(a == 0x261FE8 and new == 0xE3A00001 for a, _, new in INSN_PATCHES), 'lista parole vietate attiva: spazio in uso'
    s = 'Negozio'.encode('utf-16-le') + b'\0\0'
    at = GAME_NG_CAVE
    assert at + len(s) <= GAME_NG_CAVE_END
    d[at - BASE:at - BASE + len(s)] = s
    assert d[0x307A84 - BASE:0x307A8C - BASE] == 'おみせ'.encode('utf-16-le') + b'\0\0'
    d[0x307A84 - BASE:0x307A8C - BASE] = struct.pack('<II', at, 0)
    w = struct.unpack_from('<I', d, 0x3078D8 - BASE)[0]
    assert w == 0x328F1F69, hex(w)                    # addlo r1, pc, #0x1a4
    struct.pack_into('<I', d, 0x3078D8 - BASE, 0x359F11A4)  # ldrlo r1, [pc, #0x1a4] -> [0x307a84]


def apply_ngc_cave(d):
    """routine nuove nello spazio nn::ngc: fumetto dinamico della tastiera magica (bubble_plate.py)"""
    assert any(a == 0x21BAC0 and new == 0xE3A00000 for a, _, new in INSN_PATCHES), 'filtro non spento: spazio ngc in uso'
    assert struct.unpack_from('<I', d, NGC_CAVE - BASE)[0] in (0xE3500000,), 'spazio ngc: inizio inatteso'
    # targhetta dei nomi/nuvolette (pop_plate.py), spostata qui dal riempimento di .text (pieno)
    import pop_plate as pp
    pcode, _ = pp.build(NGC_CAVE)
    d[NGC_CAVE - BASE:NGC_CAVE - BASE + len(pcode)] = pcode
    for site, kind in pp.SITES:
        so = site - BASE
        old = struct.unpack_from('<I', d, so)[0]
        off = old & 0xFFFFFF
        off = off - (1 << 24) if off & 0x800000 else off
        assert (old >> 24) == (0xEB if kind == 'bl' else 0xEA) and site + 8 + off * 4 == pp.SET_STRING,             f'{site:#x}: non è {kind} {pp.SET_STRING:#x}'
        struct.pack_into('<I', d, so, pp.branch(site, NGC_CAVE, kind == 'bl'))
    import bubble_plate as bp
    base = (NGC_CAVE + len(pcode) + 3) & ~3
    code, _ = bp.build(base)
    assert base + len(code) <= NGC_CAVE_END, 'spazio ngc finito (bubble_plate)'
    d[base - BASE:base - BASE + len(code)] = code
    for site, kind in bp.SITES:
        so = site - BASE
        old = struct.unpack_from('<I', d, so)[0]
        off = old & 0xFFFFFF
        off = off - (1 << 24) if off & 0x800000 else off
        assert (old >> 24) == (0xEB if kind == 'bl' else 0xEA) and site + 8 + off * 4 == bp.SET_STRING,             f'{site:#x}: non è {kind} {bp.SET_STRING:#x}'
        struct.pack_into('<I', d, so, bp.branch(site, base, kind == 'bl'))
    # tag [$599] "o"/"a" secondo il sesso del giocatore (gender_tag.py, QoL 10), dopo il fumetto
    import gender_tag as gt
    gbase = (base + len(code) + 3) & ~3
    gend = gt.install(d, gbase)
    assert gend <= NGC_CAVE_END, 'spazio ngc finito (gender_tag)'
    # tag [$598] "i"/"e" (plurale) secondo il sesso del giocatore (QoL 7: coppie di qualsiasi sesso)
    gend = gt.install(d, (gend + 3) & ~3, tag=598)
    assert gend <= NGC_CAVE_END, 'spazio ngc finito (gender_tag 598)'
    # QoL 1 (1.5): viaggio rapido dalla Mappa (fast_travel.py): codice + tabella delle 28 destinazioni
    import fast_travel
    fend = fast_travel.install(d, (gend + 3) & ~3)
    assert fend <= NGC_CAVE_END, 'spazio ngc finito (viaggio rapido)'
    # opzioni del Prof. Olmo (options.py): soldi infiniti (ganci su FUN_001b222c / FUN_001b266c)
    import options
    oend = options.install(d, (fend + 3) & ~3)
    assert oend <= NGC_CAVE_END, 'spazio ngc finito (opzioni)'
    # DLC sempre attivi (dlc.py): installatore nella macchina di avvio (stato 0x36 + stati nuovi 0x3a/0x3b)
    import dlc
    if dlc.available():                         # pacchetto DLC facoltativo (work/dlc_gbatemp, non distribuito)
        assert dlc.install(d, (oend + 3) & ~3) <= NGC_CAVE_END, 'spazio ngc finito (dlc)'


def interior_pointers(d):
    """insieme degli indirizzi puntati da valori u32 allineati (per scoprire stringhe condivise:
    il compilatore riusa la coda di una stringa come stringa più corta)"""
    import array
    a = array.array('I', d[:len(d) // 4 * 4])
    return set(v for v in a if BASE <= v < BASE + len(d))


def relocate(d, o, jp, it, where, free):
    """Rilocazione: la stringa originale resta intatta (per chi ne usa la coda, es. i tasti della tastiera
    hiragana) e quella italiana va nello spazio libero in fondo a .rodata; si ripuntano tutti i
    riferimenti (u32 allineati) all'inizio della stringa."""
    refs = where.get(o + BASE, [])
    ib = it.encode('utf-16-le') + b'\0\0'
    if os.environ.get('CODE_NORELOC'):                  # solo per prove (bisezione di problemi)
        return False
    # il gioco copia alcune di queste stringhe in buffer RAM della lunghezza giapponese: più lunghe
    # corrompono la memoria (crash visto con "Incolla" al posto di はりつけ sulla tastiera)
    if len(it) > len(jp):
        raise SystemExit(f'{hex(o + BASE)} {jp}: "{it}" ({len(it)}) più lunga del giapponese ({len(jp)})')
    if not it or not refs or free[0] + len(ib) > free[1]:
        print(f'  saltata {hex(o + BASE)} {jp}: {len(refs)} riferimenti, spazio libero {free[1] - free[0]}')
        return False
    new = free[0]
    if os.environ.get('CODE_DEBUG'):
        print(f'  rilocata {hex(o + BASE)} {jp} -> {hex(new)} "{it}", riferimenti {[hex(r + BASE) for r in refs]}')
    d[new - BASE:new - BASE + len(ib)] = ib
    free[0] = (new + len(ib) + 3) & ~3
    for r in refs:
        d[r:r + 4] = struct.pack('<I', new)
    return True


def translate_strings(d, addr_map, free, ptrs10=None):
    """stringhe UTF-16 del codice (work/trad/code_it.tsv, indirizzi 1.0) sul posto o rilocate in [free[0], free[1]).
    ptrs10: puntatori interni della 1.0 -> la scelta "stringa condivisa" e' la stessa della build 1.0 (nella 1.1 una
    parola qualsiasi puo' coincidere per caso con un indirizzo interno, es. "FROM " 0x3c676c)"""
    orig = bytes(d)
    ptrs = interior_pointers(orig)
    n = skipped = moved = 0
    import array, collections
    where = collections.defaultdict(list)      # indirizzo puntato -> offset dei puntatori u32
    for i, v in enumerate(array.array('I', orig[:len(orig) // 4 * 4])):
        if BASE <= v < BASE + len(orig):
            where[v].append(4 * i)
    for line in open(os.path.join(ROOT, 'work', 'trad', 'code_it.tsv'), encoding='utf-8'):
        line = line.rstrip('\n')
        if not line:
            continue
        addr, jp, it = (line.split('\t') + [''])[:3]
        a10 = int(addr, 16)
        o = addr_map(a10) - BASE
        addr = hex(o + BASE)
        jb = jp.encode('utf-16-le')
        assert d[o:o + len(jb)] == jb, f'{addr}: testo originale diverso'
        # stringa condivisa: qualcuno punta a un suo carattere interno -> non si tocca
        if ptrs10 is None:
            shared = [o + BASE + k for k in range(2, len(jb) + 2, 2) if o + BASE + k in ptrs]
        else:
            shared = [o + BASE + k for k in range(2, len(jb) + 2, 2) if a10 + k in ptrs10]
        if shared:
            # se la parte condivisa è solo punteggiatura finale, la si lascia al suo posto
            p = (min(shared) - BASE - o) // 2
            suffix = jp[p:]
            if suffix and all(c in '？！…?!。' for c in suffix) and len(it) <= p + len(suffix):
                body = it[:len(it) - len(suffix)] if it.endswith(('?', '!', '？', '！')) else it
                body = body[:p].ljust(p)
                d[o:o + 2 * p] = body.encode('utf-16-le')
                n += 1
                continue
            if not relocate(d, o, jp, it, where, free):
                skipped += 1
                continue
            n += 1
            moved += 1
            continue
        # spazio: stringa + terminatore + zeri di riempimento successivi
        end = o + len(jb) + 2
        while end + 1 < len(d) and d[end] == 0 and d[end + 1] == 0:
            end += 2
        cap = (end - o) // 2 - 1
        ib = it.encode('utf-16-le')
        if len(it) > cap and os.environ.get('CODE_NORELOC'):
            it, ib = it[:cap], it[:cap].encode('utf-16-le')
        if len(it) > cap:                       # troppo lunga per il suo posto: va nello spazio libero
            if not relocate(d, o, jp, it, where, free):
                raise SystemExit(f'{addr}: "{it}" ({len(it)}) supera la capacità {cap} e non è rilocabile')
            n += 1
            moved += 1
            continue
        d[o:o + len(jb) + 2] = b'\0' * (len(jb) + 2)
        d[o:o + len(ib)] = ib
        n += 1
    return n, moved, skipped


def code_patches(d):
    apply_insn_patches(d)
    apply_name_plate(d)
    apply_ngc_cave(d)
    apply_game_ng_cave(d)


# Versione unica 1.0/1.1 (14/10): si distribuisce il codice della Ver.1.1 gia' patchato (exefs/code.bin
# decompresso) + l'exheader della 1.1; Luma (luma/titles/<tid>/code.bin + exheader.bin) e Azahar (mods/<tid>/exefs/code.bin
# + exheader.bin) li caricano al posto di quelli installati, quindi va bene con la cartuccia 1.0 e con l'aggiornamento.
# Le patch restano scritte per gli indirizzi 1.0 e vengono portate da port11.port (verifica parola per parola).
# python build_code.py --target 10  -> vecchio code.ips 1.0 (solo per le sessioni di RE: GDB e atlante usano la 1.0)
CODE11 = os.path.join(ROOT, 'work', 'v11', 'exefs', 'code.bin')
EXH11 = os.path.join(ROOT, 'work', 'v11', 'raw', 'exh.bin')
FREE11 = (0x588600, 0x588C00)                  # fine di .rodata 1.1 (0x54c000 + 0x3c600); da 0x588c00 le tabelle 1.0 0x587e00/0x587f00 (port11.TABLES_DELTA)


# Luma (3DS vera, non Azahar) fa il LayeredFS scrivendo nel codice del gioco dopo aver caricato il nostro code.bin
# (loader/source/patcher.c, findLayeredFsPayloadOffset): payload (~0x118 B) a fine .text e percorso "lf:" (39 B) a fine
# .rodata, nel riempimento della pagina, secondo le dimensioni dell'exheader. Le nostre cave stanno proprio li': Luma le
# sovrascriveva (crash all'avvio su 3DS dalla 1.5, pc in .data, lr 0x102730). Le dimensioni dichiarate si allungano fino
# alla fine delle cave, cosi' Luma scrive nel riempimento che resta dopo. Il kernel e Azahar mappano per pagine: invariato.
LUMA_PAYLOAD, LUMA_PATH = 0x200, 0x40          # spazio lasciato a Luma (payload 0x118, percorso 39 B) con margine


def luma_exheader(exh, o11, d11, ends):
    e = bytearray(exh)
    for off, end in ends.items():               # 0x10 = .text, 0x20 = .rodata
        a, pages, size = struct.unpack_from('<III', e, off)
        page_end = a + pages * 0x1000
        used = [i + BASE for i in range(a + size - BASE, page_end - BASE) if d11[i] != o11[i]]
        assert not used or used[-1] < end, f'exheader {off:#x}: byte modificati oltre la cave ({used[-1]:#x} >= {end:#x})'
        assert end % 4 == 0 and page_end - end >= (LUMA_PAYLOAD if off == 0x10 else LUMA_PATH), \
            f'exheader {off:#x}: niente spazio per il LayeredFS di Luma dopo {end:#x}'
        assert all(b == 0 for b in d11[end - BASE:page_end - BASE]), f'exheader {off:#x}: riempimento non a zero'
        struct.pack_into('<I', e, off + 8, max(size, end - a))
    return bytes(e)


def main_v11():
    import armasm, port11
    o10, o11 = open(CODE, 'rb').read(), open(CODE11, 'rb').read()
    d11 = bytearray(o11)
    free = [FREE11[0], FREE11[1]]
    def amap(x):
        y = port11.map_addr(x)
        assert y is not None, f'stringa {x:#x}: indirizzo 1.1 non determinabile'
        return y
    n, moved, skipped = translate_strings(d11, amap, free, interior_pointers(o10))
    e10 = bytearray(o10)
    armasm.RELOCS.clear(); armasm.CONSTS.clear()
    code_patches(e10)
    import name_plate as np_
    caves = [(NGC_CAVE, NGC_CAVE_END), (GAME_NG_CAVE, GAME_NG_CAVE_END), (np_.CAVE, np_.CAVE_END)]
    st = port11.port(o10, e10, o11, d11, armasm.RELOCS, caves, consts=armasm.CONSTS)
    mods = os.path.dirname(os.path.dirname(OUT))
    os.makedirs(os.path.join(mods, 'exefs'), exist_ok=True)      # build da zero: la cartella non c'e' ancora
    open(os.path.join(mods, 'exefs', 'code.bin'), 'wb').write(d11)
    ends = {0x10: port11.map_addr(np_.CAVE_END - 4) + 4, 0x20: port11.map_addr(port11.TABLES10 + 0x1FC) + 4}
    open(os.path.join(mods, 'exheader.bin'), 'wb').write(luma_exheader(open(EXH11, 'rb').read(), o11, d11, ends))
    if os.path.exists(OUT):
        os.remove(OUT)                          # Azahar applicherebbe il vecchio IPS 1.0 sopra il code.bin
    import dlc
    print(f'dlc: {dlc.copy_files(os.path.join(mods, "romfs"))} file in romfs/{dlc.FOLDER}/')
    print(f'{n} stringhe del codice tradotte ({moved} rilocate, {skipped} saltate, spazio libero {free[1] - free[0]}); '
          f'patch portate su 1.1: {st}; -> exefs/code.bin + exheader.bin (Ver.1.1)')


def main():
    if '--target' not in sys.argv or sys.argv[sys.argv.index('--target') + 1] != '10':
        return main_v11()
    d = bytearray(open(CODE, 'rb').read())
    orig = bytes(d)
    n, moved, skipped = translate_strings(d, lambda x: x, [FREE_START, FREE_END])
    code_patches(d)
    mods = os.path.dirname(os.path.dirname(OUT))
    for f in (os.path.join(mods, 'exefs', 'code.bin'), os.path.join(mods, 'exheader.bin')):
        if os.path.exists(f):
            os.remove(f)
    import dlc
    print(f'dlc: {dlc.copy_files(os.path.join(os.path.dirname(os.path.dirname(OUT)), "romfs"))} file in romfs/{dlc.FOLDER}/')
    # patch IPS (record da max 0xFFFF byte; offset a 24 bit)
    recs = bytearray(b'PATCH')
    i = 0
    while i < len(d):
        if d[i] != orig[i]:
            j = i
            while j < len(d) and (d[j] != orig[j] or (j + 1 < len(d) and d[j + 1] != orig[j + 1])) and j - i < 0xFFFF:
                j += 1
            assert i < 0x1000000
            recs += struct.pack('>I', i)[1:] + struct.pack('>H', j - i) + d[i:j]
            i = j
        else:
            i += 1
    recs += b'EOF'
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'wb').write(recs)
    print(f'{n} stringhe del codice tradotte ({moved} rilocate, {skipped} saltate); '
          f'patch {len(recs)} byte -> {os.path.relpath(OUT, ROOT)}')


if __name__ == '__main__':
    main()
