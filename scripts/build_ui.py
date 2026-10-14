"""Layout dell'interfaccia (ui/*.tarc -> *.arc DARC -> *.bclyt):
- applica work/trad/ui_trad.json ({testo jp: testo it}) ai pannelli di testo txt1;
- allarga il buffer di TUTTI i pannelli di testo: il gioco ci copia a runtime testi presi dai messaggi
  (titoli, nomi, oggetti) che in italiano sono più lunghi e altrimenti traboccano nel pannello successivo.
Installa i tarc ricostruiti nella mod. menu_font è gestito da build_fonts.py.
"""
import json, re, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import bclyt, darc, tbaf

ROOT = os.path.join(os.path.dirname(__file__), '..')
X = os.path.join(ROOT, 'work', '3ds', 'romfs_x', 'ui')
ORIG = os.path.join(ROOT, 'work', '3ds', 'romfs', 'ui')
import paths
MOD = os.path.join(paths.MOD, 'romfs', 'ui')
SKIP = {'menu_font.tarc'}
# Modifiche geometriche: prefisso del file bclyt -> {pannello: (dx, dw)}.
# Targhetta del nome nei dialoghi (3 immagini: capo sinistro, centro, capo destro + testo):
# il nome NPC ora può arrivare a 15 caratteri (build_npc), allarghiamo di NAME_DW verso destra.
NAME_DW = 0.0      # la targhetta ora è DINAMICA (patch del codice, name_plate.py): layout originale.
                   # Prima era +28 fisso per i nomi da 15 caratteri, troppo lunga per fiori e incantesimi.
# Date in formato italiano (GG/MM/AAAA, compleanno GG/MM): il gioco scrive le cifre in pannelli separati,
# basta spostarli. Borsa: 10 posizioni da 11 px (AAAA/MM/GG -> GG/MM/AAAA).
_BAG = {0: 6, 1: 7, 2: 8, 3: 9, 4: 5, 5: 3, 6: 4, 7: 2, 8: 0, 9: 1}     # posizione vecchia -> nuova
# Patente (etichetta "Data      /    /"): le cifre sono pannelli allineati a destra; gli slash sono nel testo della etichetta,
# misurati in game (2026-10-09) a x~24.5 e ~45.5 (centri). Cifre: giorno con bordo destro a 19, mese a 41, anno a 73
# (originali: 99/69/39 in makeprofile_obj, 109/79/49 in shopprofile)
_LICENSE = {'Txt_day': (-80.0, 0.0), 'Txt_month': (-28.0, 0.0), 'Txt_year': (38.0, 0.0)}
# licenza negozio: stessa etichetta e stesse coordinate dei pannelli, ma il contenitore delle cifre e' 10 px piu' a sinistra
# (per questo gli originali sono 109/79/49): gli stessi spostamenti della patente danno la stessa resa (prima -10: cifre sugli slash)
_LICENSE_SHOP = dict(_LICENSE)
# testo specifico per un pannello (prefisso del bclyt, pannello) quando la traduzione generale non ci sta
PANE_TEXT = {
    ('blyt/corde_bg_u', 'Txt_tub_on_00'): 'Oggetti',      # linguetta da 52 px: "Inventario" andava a capo
    ('blyt/corde_bg_u', 'Txt_tub_off_00'): 'Oggetti',
    ('blyt/goods_list_bar', 'Txt_rich_01'): 'R',          # lista prodotti: "Ritch" copriva "17/17" (test 10/10)
}
# allineamento orizzontale del testo (byte +0x54 di txt1: 0 sinistra, 1 centro, 2 destra)
PANE_ALIGN = {
    ('blyt/corde_obj', 'Txt_lr'): 1,          # "Ruota" fra i tasti L e R
    ('blyt/charmake_bg', 'Txt_lr_01'): 1,     # idem nella creazione del personaggio (pannello 52 px centrato, testo a sinistra: test HW 10/10)
    # patente: etichette Nome / Compleanno / Segno centrate nelle loro targhette marroni (pannelli larghi come la targhetta)
    ('blyt/makeprofile_obj', 'Txt_name'): 1, ('blyt/makeprofile_obj', 'Txt_birth'): 1, ('blyt/makeprofile_obj', 'Txt_star_chart'): 1,
    # barra incassi del negozio: "Incassi" allineato a sinistra finiva attaccato al doppio arco della pillola
    ('blyt/mes_win_04', 'Txt_mes_00'): 1,
}
POP_TXT_DX = 7.0    # misurato in game: targhetta = testo + ~26 px, margini 6 sx / 20 dx senza correzione -> +7 centra i nomi normali (i nomi cortissimi hanno una larghezza minima: restano un po' a sinistra)
EXACT = set()   # layout selezionati per nome intero (altrimenti il prefisso colpirebbe anche pop_up_01/_02)
PANE_EDITS = {
    'blyt/mes_win_00': {'Pic_mes_name_01': (NAME_DW / 2, NAME_DW), 'Pic_mes_name_02': (NAME_DW, 0.0),
                      'Txt_mes_name': (NAME_DW / 2, NAME_DW)},
    'blyt/pc_action_bg_00': {**{f'Pos_date_num_{o:02d}': (11.0 * (n - o), 0.0) for o, n in _BAG.items()},
                             # ora a 24 ore (patch del codice 0x2ecdb8): "AM"/"PM" (10, 11) fuori schermo,
                             # hh:mm (12..16) 4 px a sinistra, con l'ultima cifra sotto l'ultima dell'anno (x=146)
                             'Pos_date_num_10': (-1000.0, 0.0), 'Pos_date_num_11': (-1000.0, 0.0),
                             **{f'Pos_date_num_{o}': (-4.0, 0.0) for o in range(12, 17)}},
    'blyt/makeprofile_obj': {**_LICENSE, 'Txt_birth_month': (31.0, 0.0), 'Txt_birth_day': (-31.0, 0.0)},
    # cursore della tastiera sulla patente (0x263b48: tabella per tipo di campo -> Pos_birth_cur00 mese, _02 giorno):
    # segue le cifre scambiate qui sopra (prima la freccia del mese stava sul giorno e viceversa; test HW 10/10)
    'blyt/makeprofile_win_cur': {'Pos_birth_cur00': (31.0, 0.0), 'Pos_birth_cur01': (31.0, 0.0),
                                 'Pos_birth_cur02': (-31.0, 0.0), 'Pos_birth_cur03': (-31.0, 0.0),
                                 # nome della scuola (prima partita): il testo parte dal bordo del pannello (-88), il cursore
                                 # da -72 (inizio dei 12 caratteri JP da 12 px centrati) + larghezze reali -> ~16 px avanti (freccia larga 8: -13)
                                 **{f'Pos_scool_cur0{i}': (-13.0, 0.0) for i in range(4)},   # -16 copriva l'ultima lettera di ~3 px
                                 # nome del negozio (tipo 5: Txt_school di shopprofile, stesso pannello 176 centrato): base -82
                                 # -> stessa resa della scuola (-72-13 = -85). DA VERIFICARE in gioco col nome negozio
                                 'Pos_shopname_cur': (-3.0, 0.0)},
    'blyt/shopprofile': _LICENSE_SHOP,
    # libro delle creature: "Non registrato" andava a capo nel pannello da 60 px; +16 px tenendo fermo il bordo sinistro (origine al centro: x += 8)
    # cornice dei soldi nel negozio: le cifre toccavano "Ritch" (allargato +10): numeri 6 px a sinistra
    # (+ sprite dietro allungato di 12 px verso destra: "Ritch" toccava il bordo arancione)
    'blyt/buyitem_money_frame': {'Txt_money_01': (-6.0, 0.0), 'Txt_money_04': (-6.0, 0.0), 'Pic_frame_01': (6.0, 12.0)},
    'blyt/mailorder_money_frame': {'Pic_frame_01': (6.0, 12.0)},
    'blyt/bug_book_bg_00': {'Txt_unregistered': (8.0, 16.0)},
    'blyt/fish_book_bg_00': {'Txt_unregistered': (8.0, 16.0)},
    # targhetta degli oggetti: ora DINAMICA (patch del codice, pop_plate.py), layout originale
    # pannello del nome nei messaggi: 110 px facevano andare a capo i nomi con spazio ("Catalogo pesci" -> si vedeva solo
    # "Catalogo"); +60 px verso destra, bordo sinistro fermo (la targhetta si adatta da sola: name_plate.py)
    'blyt/mes_win_': {'Txt_mes_name': (30.0, 60.0)},
    # rivista Spell & Spill, pagina delle collezioni: i nomi dei personaggi sono VERTICALI (stile giapponese) e in
    # italiano andavano a capo ogni 2 lettere ("Cr/is/ti/na ©"). Tolti dalla vista (fuori schermo; il pannello resta)
    'blyt/magpage_08_pos_': {'Txt_chara_name_l': (-1000.0, 0.0), 'Txt_chara_name_r': (-1000.0, 0.0)},
}


def widen_unit(blob, panes, dw=10.0):
    """"Ritch" (5 lettere) va a capo nei pannelli da 3 caratteri giapponesi (liste del negozio): si allargano di 10 unita'
    tenendo fermo il bordo sinistro (origine orizzontale = byte origine % 3: 0 sinistra, 1 centro, 2 destra)"""
    import struct
    for pane in panes:
        for m, o, sz in bclyt.sections(blob):
            if m == b'txt1' and blob[o + 0xC:o + 0x1C].split(b'\0')[0].decode('latin1') == pane:
                w = struct.unpack_from('<f', blob, o + 0x44)[0]
                if w <= 36.0:
                    dx = (0.0, dw / 2, dw)[blob[o + 9] % 3]
                    blob = bclyt.move_pane(blob, pane, dx, dw) or blob
                break
    return blob


# nomi oggetto nelle liste: pannelli da ~120 px. Il font viene stretto del 16% (larghezza glifo 12 -> 10) cosi' entrano
# nomi da ~140 px (ITEM_PX in blob_texts.py) senza abbreviazioni
SQUEEZE = 10.0 / 12.0
SQUEEZE_PANES = {'Txt_goods_name', 'Txt_item_name', 'Txt_ex_item_name', 'Txt_ex_item', 'Txt_ex_item_01', 'Txt_in_item',
                 'Txt_in_item_01'} | {f'Txt_itemlist_{i:02d}' for i in range(7)}


def squeeze_names(name, blob):
    import struct
    blob = bytearray(blob)
    for m, o, sz in bclyt.sections(bytes(blob)):
        if m != b'txt1':
            continue
        pn = blob[o + 0xC:o + 0x1C].split(b'\0')[0].decode('latin1')
        w = struct.unpack_from('<f', blob, o + 0x44)[0]
        if 100.0 <= w <= 125.0 and (pn in SQUEEZE_PANES or (pn == 'Txt_name_00' and 'item_sheet' in name)):
            fw = struct.unpack_from('<f', blob, o + 0x64)[0]
            struct.pack_into('<f', blob, o + 0x64, fw * SQUEEZE)
        elif name.startswith('blyt/map_name_win') and pn.startswith('Txt_map_name_'):
            fw = struct.unpack_from('<f', blob, o + 0x64)[0]
            struct.pack_into('<f', blob, o + 0x64, fw * MAP_SQUEEZE)
    return bytes(blob)


# nomi dei luoghi sulla mappa (riquadro 150 px): prima il font era stretto del 12% per "Grandi Magazzini Freccia"; con i
# nomi attuali il piu' largo e' 139 px a scala piena ("Negozio del Fantagatto"; "Massimiliano abita qui" 125). Stretto, la
# "i" di LC (1 px) cadeva fra due campioni e spariva ("Centro commerc ale", "Sala Event", 14/10): scala piena
MAP_SQUEEZE = 1.0


PLACEHOLDER = re.compile(r'^[A-Z0-9０-９ｍｃ　 /:|…\-\[\]【】]+$')   # segnaposto (nomi, numeri): il gioco li sostituisce a runtime
FIT_MIN = 0.8        # larghezza minima del font per le etichette statiche (0.8 = come il -20% dei nomi oggetto)
WIDEN_MAX = 26.0     # allargamento massimo di un pannello (solo nei layout delle ricette)


def fit_static(name, blob):
    """etichette italiane statiche piu' larghe del pannello: prima si allarga (ricette: ci sono spazi liberi a destra),
    poi si restringe la larghezza del font fino a FIT_MIN (misurato con LC.bcfnt, come name_px)"""
    import struct, build_text
    blob = bytearray(blob)
    widen_ok = 'recipe_sheet' in name
    for m, o, sz in bclyt.sections(bytes(blob)):
        if m != b'txt1':
            continue
        pane = blob[o + 0xC:o + 0x1C].split(b'\0')[0].decode('latin1')
        w = struct.unpack_from('<f', blob, o + 0x44)[0]
        fw = struct.unpack_from('<f', blob, o + 0x64)[0]
        ln = struct.unpack_from('<H', blob, o + 0x4E)[0]
        toff = struct.unpack_from('<I', blob, o + 0x58)[0]
        t = bytes(blob[o + toff:o + toff + ln]).decode('utf-16-le', 'replace').rstrip('\0')
        if not t.strip() or w <= 20 or PLACEHOLDER.match(t) or re.search(r'[぀-ヿ一-鿿]', t):
            continue
        px = max(sum(build_text.char_px(c) - 1 for c in l) for l in t.split(chr(10))) * fw / 12.0
        if px <= w + 1:
            continue
        if widen_ok:
            dw = min(px - w + 2, WIDEN_MAX)
            dx = (0.0, dw / 2, dw)[blob[o + 9] % 3]
            x = struct.unpack_from('<f', blob, o + 0x24)[0]
            struct.pack_into('<f', blob, o + 0x24, x + dx)
            struct.pack_into('<f', blob, o + 0x44, w + dw)
            w += dw
        if px > w + 1:
            struct.pack_into('<f', blob, o + 0x64, fw * max(FIT_MIN, (w - 1) / px))
    return bytes(blob)



def edit_panes(name, blob):
    import struct
    blob = squeeze_names(name, blob)
    blob = fit_static(name, blob)
    for (prefix, pane), al in PANE_ALIGN.items():
        if name.startswith(prefix):
            blob = bytearray(blob)
            for m, o, s in bclyt.sections(bytes(blob)):
                if m == b'txt1' and blob[o + 0xC:o + 0x24].split(b'\0')[0].decode('latin1') == pane:
                    blob[o + 0x54] = al
            blob = bytes(blob)
    for prefix, edits in PANE_EDITS.items():
        if name == prefix + '.bclyt' if prefix in EXACT else name.startswith(prefix):
            for pane, (dx, dw) in edits.items():
                blob = bclyt.move_pane(blob, pane, dx, dw) or blob
    return blob


def main():
    trad = json.load(open(os.path.join(ROOT, 'work', 'trad', 'ui_trad.json'), encoding='utf-8'))
    os.makedirs(MOD, exist_ok=True)
    n_pan = n_arc = 0
    for d in sorted(os.listdir(X)):
        tarc = d[:-2]                                   # menu_x.tarc_x -> menu_x.tarc
        if tarc in SKIP or not os.path.exists(os.path.join(ORIG, tarc)):
            continue
        repl_tarc = {}
        for f in os.listdir(os.path.join(X, d)):
            if not (f.endswith('.arc') or f.endswith('.bin')):
                continue
            data = open(os.path.join(X, d, f), 'rb').read()
            if data[:4] != b'darc':
                continue
            files = darc.read_files(data)
            repl = {}
            for name, blob in files.items():
                if not name.endswith('.bclyt'):
                    continue
                pr = {pn: trad[t] for _, pn, t, _ in bclyt.texts(blob) if t in trad}
                for (pref, pn), txt in PANE_TEXT.items():      # testi diversi per pannelli stretti
                    if name.startswith(pref) and pn in pr:
                        pr[pn] = txt
                n_pan += len(pr)
                wide = [pn for _, pn, t, _ in bclyt.texts(blob) if t == 'リッチ' and pn in pr]
                new = bclyt.set_texts(blob, pr, grow=True)
                new = widen_unit(new, wide)
                chk = {pn: t for _, pn, t, _ in bclyt.texts(new)}
                assert all(chk[k] == v for k, v in pr.items()), (d, name)
                repl[name] = edit_panes(name, new)
            if repl:
                repl_tarc[f] = darc.rebuild(data, repl)
        if not repl_tarc:
            continue
        out = os.path.join(MOD, tarc)
        tbaf.rebuild(os.path.join(ORIG, tarc), repl_tarc, out)
        n_arc += 1
    print(f'{n_pan} pannelli tradotti; buffer allargati in {n_arc} archivi ui')


if __name__ == '__main__':
    main()
