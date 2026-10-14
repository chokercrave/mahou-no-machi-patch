"""Schede delle immagini 2D della UI (sorgente 'png' di make_signs.py), testo col font UI (ui=True).
Trascrizioni e traduzioni sono qui. Le carica make_signs.SPEC.
Regola: stile 3DS originale (colori, contorni, posizione); lettere = ui_font.
"""
RUN = 'menu_minigame_runway/minigame_runway.arc__timg_'
SNAP = 'menu_minigame_snapshot/minigame_snapshot.arc__timg_'
SPEC = {}

# ---- minigioco passerella: "cellulari" con pillola colorata (testo bianco, contorno scuro del colore) ----
_PILL = [  # (indice, testo, sfondo chiaro (più varianti), contorno del testo)
    (0, 'Si vota!', [(145, 255, 145), (150, 255, 150), (149, 255, 149), (150, 255, 159), (140, 250, 140)], (21, 123, 38)),
    (1, 'In ascesa', [(255, 233, 84), (255, 234, 81), (255, 230, 94), (255, 231, 90), (255, 232, 92)], (115, 98, 13)),
    (2, 'Riflettori', [(255, 208, 123), (249, 208, 117), (255, 208, 117), (255, 213, 111)], (191, 72, 4)),
    (3, 'Che bolgia!', [(255, 182, 255), (255, 186, 244), (255, 187, 238)], (132, 30, 115)),
    (4, 'Trionfo!', [(249, 100, 100), (251, 98, 98), (255, 97, 97), (255, 113, 113)], (132, 13, 0), (255, 225, 106)),
]

# ---- minigioco foto: fumetti (interno bianco; testo tondo chiaro con contorno più scuro dello stesso colore).
# I fumetti lunghi sono due texture: corpo 256x64 + capo 64x64 a destra (composizione "a+b").
_BUB = {'blue': ((110, 200, 245), (18, 137, 205)), 'pink': ((255, 160, 215), (240, 80, 170)),
        'purple': ((170, 170, 255), (100, 100, 210))}
_BUBBLES = [  # (texture, testo) — una texture o "corpo+capo"
    ('blue_00+blue_01', 'Finito! Bel lavoro!'),
    ('blue_02+blue_03', 'Ultima posa: al momento giusto!'),
    ('blue_04+blue_05', 'Ora scegli la posizione dei piedi!'),
    ('blue_06+blue_07', 'Scegli come girarti~'),
    ('blue_08+blue_09', 'Ok, prossima posa~'),
    ('blue_10', 'Mh?'),
    ('blue_11+blue_12', 'Mi fai uno scatto stupendo~?'),
    ('pink_00', 'Bello, bello~!'),
    ('pink_02', 'Ok!'),
    ('pink_03+pink_04', 'Ottimo, andiamo così~!'),
    ('purple_00', 'Oh...'),
]
for tex, t in _BUBBLES:
    fam = tex.split('_')[0]
    f = '+'.join(f'{SNAP}snapshot_fukidashi_{p}.png' for p in tex.split('+'))
    w = 320 if '+' in tex else 256
    fill, ol = _BUB[fam]
    SPEC[('png', f)] = dict(
        text=t, ui=True, box=(22, 23, w - 22 if '+' in tex else 252, 50), px=18, fill=fill, outline=ol, ow=1.5,
        soft=0.8, spacing=1, erase=[(14, 22, w - 10, 51)], erase_colors=[],
        erase_except=[(255, 255, 255), (250, 255, 255), (255, 250, 255), (245, 245, 255)], except_tol=30,
        tol=40, edge=1)


# ---- editor dei disegni: pulsanti quadrati (titolo bianco in alto, contorno blu ardesia; stato 02 = rosa) ----
MYD = 'menu_mydesign/mydesign.arc__timg_'
_BTN = {'album': 'Album', 'camera': 'Fotocamera', 'complete': 'Fatto', 'retouch': 'Ritocco'}
_BLUE_TXT = [(255, 255, 255), (64, 98, 132), (90, 124, 158), (76, 101, 134), (180, 197, 214), (120, 150, 180),
             (40, 70, 110)]
_PINK_TXT = [(255, 255, 255), (237, 171, 213), (255, 188, 205), (255, 219, 244), (255, 191, 208), (230, 150, 200)]
for name, t in _BTN.items():
    for st in ('00', '01', '02'):
        pink = st == '02'
        SPEC[('png', f'{MYD}button_{name}_{st}.png')] = dict(
            text=t, ui=True, box=(27, 33, 103, 49), px=16, fill=(255, 255, 255),
            outline=(237, 150, 205) if pink else (64, 98, 132), ow=1.5, soft=0.6, spacing=1,
            erase=[(34, 31, 99, 53)], erase_colors=_PINK_TXT if pink else _BLUE_TXT, tol=45, edge=1,
            halo=[(255, 230, 245), (250, 210, 235), (245, 200, 230)] if pink else
            [(200, 215, 230), (220, 235, 245), (233, 250, 255), (210, 230, 240), (190, 210, 225)], grow=2, halo_tol=35,
            rowfill=(30, 31, 101, 53), rowfill_min_sum=0)


# ---- editor dei disegni: nuvolette dei tasti L/R ("Lさつえい" = scatta con L). 00 blu su bianco, 01 arancio su crema
for side in ('l', 'r'):
    for st in ('00', '01'):
        gold = st == '01'
        SPEC[('png', f'{MYD}shutter_button_{side}_{st}.png')] = dict(
            text=f'{side.upper()} Scatta', ui=True, box=(38, 21, 92, 45) if side == 'l' else (41, 21, 98, 45), px=17,
            fill=(255, 150, 20) if gold else (18, 150, 210), outline=(255, 215, 90) if gold else (130, 220, 255),
            ow=1, soft=0.6, spacing=1, erase=[(36, 24, 94, 43)] if side == 'l' else [(35, 24, 99, 43)], erase_colors=[],
            erase_except=[(255, 252, 202), (255, 255, 183), (255, 255, 200), (255, 251, 200), (255, 255, 199),
                          (255, 255, 217), (255, 255, 251)] if gold else
            [(255, 255, 255), (251, 255, 255), (234, 255, 255), (250, 255, 255), (240, 255, 255)],
            except_tol=25, tol=40, edge=1, rowfill=(36, 24, 94, 43) if side == 'l' else (35, 24, 99, 43), rowfill_min_sum=0)


# ---- etichette su fondo TRASPARENTE: si cancella tutto e si riscrive nel colore originale ----
def _clear(w, h):
    return dict(erase=[(0, 0, w, h)], erase_colors=[], erase_all=True, clear=[(0, 0, w, h)], tol=40, edge=1)


for f, t, w, h, col in [
        ('menu_chest/chest.arc__timg_txt_chest.png', 'Armadio', 64, 16, (107, 58, 0)),
        ('menu_dustbox/dustbox.arc__timg_txt_dustbox.png', 'Cestino', 64, 16, (0, 89, 130)),
        ('menu_safe/safe.arc__timg_txt_safe.png', 'Cassa', 32, 16, (127, 61, 12))]:          # 32 px: "Cassaforte" non entra
    SPEC[('png', f)] = dict(text=t, ui=True, box=(0, 1, w, h), px=13, fill=col, outline=None,
                            spacing=0 if w < 40 else 1, **_clear(w, h))
SPEC[('png', 'menu_uma/uma.arc__timg_uma_title_00.png+menu_uma/uma.arc__timg_uma_title_01.png')] = dict(
    # いままでにかいけつしたじけん (titolo diviso su due texture 256+128)
    text='Casi risolti finora', ui=True, box=(14, 2, 370, 31), px=26, fill=(98, 41, 41), outline=None,
    spacing=1, weight='Bold', **_clear(384, 32))
SPEC[('png', 'menu_solved_event_list/solvedeventlist.arc__timg_solvedeventlist_head_00.png+'
             'menu_solved_event_list/solvedeventlist.arc__timg_solvedeventlist_head_01.png')] = dict(
    # いままでにかいけつした じけん (256+64): ghirigori ai lati (x 1-39 e 283-318) da tenere, testo marrone con bordo bianco
    text='Casi risolti finora', ui=True, box=(44, 3, 280, 30), px=20, fill=(110, 42, 8), outline=(255, 255, 255),
    ow=1.5, soft=0.6, spacing=1, weight='Bold',
    erase=[(40, 0, 282, 32)], erase_colors=[], erase_all=True, clear=[(40, 0, 282, 32)], tol=40, edge=1)
for f in ('menu_recipe/recipe.arc__timg_055_m_bracelet.png', 'menu_recipe_set/recipe.arc__timg_055_m_bracelet.png'):
    SPEC[('png', f)] = dict(text='Bracciale\nmagico', ui=True, box=(4, 20, 124, 110), px=30, fill=(0, 0, 0),
                            outline=None, spacing=0, leading=6, weight='Bold', **_clear(128, 128))
# titoli grandi del minigioco passerella: lettere tonde con doppio contorno (bianco + scuro)
SPEC[('png', f'{RUN}runway_txt_00.png')] = dict(
    text='Via alla\npasserella!', font='Grandstander', variant='Black', size=46, box=(14, 14, 242, 114),
    xscale='auto', leading=-0.12, fill=((255, 150, 225), (240, 60, 180)),
    strokes=[((255, 255, 255), 4), ((205, 10, 154), 1.5)], shadow=None, **_clear(256, 128))
SPEC[('png', f'{RUN}runway_txt_01.png')] = dict(
    text='Al via\nla regia!', font='Grandstander', variant='Black', size=46, box=(14, 14, 242, 114),
    xscale='auto', leading=-0.12, fill=((255, 230, 90), (225, 174, 4)),
    strokes=[((255, 255, 255), 4), ((124, 90, 0), 1.5)], shadow=None, **_clear(256, 128))


# ---- banner con riccioli (corpo 256x64 + capo 64x64): testo fra i riccioli, pillola crema/azzurra a
# sfumatura verticale (rowfill), lettere senza contorno ----
_HEAD = [('menu_customerlist/npclist.arc__timg_customerlist_head_0', 'Clienti abituali', (138, 78, 60),
          [(253, 253, 212), (255, 255, 216), (255, 250, 216), (255, 255, 215), (255, 247, 213)]),
         ('menu_npclist/npclist.arc__timg_customerlist_head_0', 'Clienti abituali', (138, 78, 60),
          [(253, 253, 212), (255, 255, 216), (255, 250, 216), (255, 255, 215), (255, 247, 213)]),
         ('menu_requestlist/npclist.arc__timg_customerlist_head_0', 'Clienti abituali', (138, 78, 60),
          [(253, 253, 212), (255, 255, 216), (255, 250, 216), (255, 255, 215), (255, 247, 213)]),
         ('menu_buyitem/000.bin__timg_customerlist_head_0', 'Vendita a distanza', (55, 123, 140),
          [(229, 253, 253), (228, 255, 255), (230, 255, 255), (227, 252, 255), (233, 255, 255), (225, 255, 255),
           (231, 255, 255)])]
for base, t, col, bg in _HEAD:
    SPEC[('png', f'{base}0.png+{base}1.png')] = dict(
        text=t, ui=True, box=(68, 16, 234, 52), px=26, fill=col, outline=None, spacing=0, weight='Bold',
        erase=[(66, 15, 239, 53)], erase_colors=[], erase_except=bg, except_tol=28, tol=40, edge=1,
        rowfill=(66, 15, 239, 53), rowfill_min_sum=0)


# ---- pillola "あと◯◯にち" (mancano NN giorni): due scritte ai lati dei cerchi del numero -> "Tra ◯◯ gg" ----
for d in ('menu_customerlist', 'menu_npclist', 'menu_requestlist'):
    SPEC[('png', f'{d}/npclist.arc__timg_day_font.png')] = dict(
        text='Tra', texts=[('Tra', (15, 21, 44, 46)), ('gg', (86, 21, 114, 46))], ui=True, box=(15, 21, 44, 46),
        px=20, fill=(255, 221, 0), outline=(204, 102, 51), ow=1.5, soft=0.6, spacing=0, weight='Bold',
        erase=[(15, 21, 44, 46), (85, 21, 115, 46)], erase_colors=[], erase_except=[(255, 255, 204), (255, 255, 210)],
        except_tol=30, tol=40, edge=1)


# ---- lotto etichette varie ----
# condizioni d'uso (titolo diviso 256+?): rosso con contorno bianco sulla barra blu a bande (rowfill)
_AUP = 'menu_acceptable_use_policy/acceptable_use_policy.arc__timg_aup_bg_0'
SPEC[('png', f'{_AUP}0.png+{_AUP}1.png')] = dict(
    text="Importante: Termini d'uso", ui=True, box=(66, 18, 266, 50), px=22, fill=(165, 0, 8), outline=(255, 255, 255),
    ow=2, soft=0.8, spacing=0, weight='Bold',
    erase=[(66, 17, 266, 51)], erase_colors=[], erase_except=[(13, 127, 205), (43, 146, 250), (30, 136, 228),
                                                             (20, 132, 215), (36, 140, 240)],
    except_tol=30, tol=40, edge=1, rowfill=(66, 17, 266, 51), rowfill_min_sum=0)
# classifica del centro commerciale: "TOP 10" (inglese) resta; si rifà solo モールランキング
_MALL = 'menu_shop_mallranking/shop_mallranking.arc__timg_mall_hedder_0'
SPEC[('png', f'{_MALL}0.png+{_MALL}1.png')] = dict(
    text='Classifica negozi', font='Grandstander', variant='Black', size=26, box=(36, 1, 230, 31), xscale='auto',
    fill=((255, 215, 215), (255, 190, 205)), strokes=[((255, 255, 255), 3.5), ((196, 43, 128), 2)], shadow=None,
    erase=[(34, 0, 232, 32)], erase_colors=[], erase_all=True, clear=[(34, 0, 232, 32)], tol=40, edge=1)
# registrazione del nome: scritta bruna semitrasparente fra due riccioli, fondo trasparente
SPEC[('png', 'menu_entry_item_name/entryitmname.arc__timg_ename_hedder.png')] = dict(
    text='Registra nome', ui=True, box=(64, 6, 208, 32), px=22, fill=(140, 64, 50), outline=None, spacing=0,
    weight='Bold', erase=[(64, 5, 208, 33)], erase_colors=[], erase_all=True, clear=[(64, 5, 208, 33)], tol=40, edge=1)
# barre arancio del negozio (16 px): testo bianco con contorno bruno, piccolo -> font del gioco
for k, t in (('0', 'Usa ciò che hai'), ('1', 'Compra dal falegname')):
    SPEC[('png', f'menu_pcshop/pc_shop.arc__timg_pc_in_obj_0{k}.png')] = dict(
        text=t, ui=True, box=(30, 1, 250, 16), halign='left', px=13, fill=(255, 255, 255), outline=(170, 60, 10),
        ow=1, soft=0.4, spacing=1,
        erase=[(29, 0, 175, 16)], erase_colors=[(255, 255, 255), (170, 60, 10), (200, 90, 20), (140, 50, 10),
                                                (230, 200, 160)], tol=60, edge=1)
# titoli del libro delle creature (nuvola verde / blu): testo bianco
for fam, t, bgc in (('bug', 'Creature di terra', [(110, 150, 40), (100, 140, 35), (120, 160, 50), (95, 135, 30)]),
                    ('fish', "Creature d'acqua", [(60, 100, 160), (55, 95, 150), (70, 110, 170), (50, 90, 145)])):
    SPEC[('png', f'menu_picturebook/picturebook.arc__timg_{fam}_title_00.png')] = dict(
        text=t, ui=True, box=(70, 22, 250, 54), px=24, fill=(255, 255, 255), outline=None, spacing=0, weight='Bold',
        erase=[(70, 22, 252, 54)], erase_colors=[(255, 255, 255), (240, 240, 230), (220, 230, 200), (200, 215, 225)],
        tol=60, edge=1)
# piccole: menu pasti, numero di capi rifatti, reputazione, timer
SPEC[('png', 'menu_meal/mealmenu.arc__timg_mealmenu_title_00.png')] = dict(
    text='Menu dei pasti', ui=True, box=(16, 4, 118, 26), px=16, fill=(150, 70, 5), outline=None, spacing=0,
    weight='Bold', erase=[(16, 4, 122, 26)], erase_colors=[], erase_except=[(255, 220, 137), (253, 253, 212),
                                                                            (255, 255, 216), (255, 255, 215),
                                                                            (255, 255, 217), (255, 255, 208)],
    except_tol=25, tol=40, edge=1, rowfill=(16, 4, 122, 26), rowfill_min_sum=0)
SPEC[('png', 'menu_arrange_rem/arrange_list.arc__timg_arrange_num_line_00.png')] = dict(
    text='Capi rifatti', ui=True, box=(12, 0, 116, 16), px=13, fill=(136, 85, 34), outline=None, spacing=1,
    erase=[(6, 0, 124, 16)], erase_colors=[], erase_except=[(253, 187, 0), (251, 183, 13), (252, 186, 5), (252, 186, 13)],
    except_tol=40, tol=40, edge=1, rowfill=(10, 0, 118, 16), rowfill_min_sum=0)
SPEC[('png', 'menu_make_profile/makeprofile.arc__timg_shopprofile_koumoku_02.png')] = dict(
    text='Fama', ui=True, box=(48, 8, 94, 24), px=13, fill=(255, 220, 33), outline=(132, 81, 0), ow=1, soft=0.4,
    spacing=1, erase=[(42, 9, 92, 23)], erase_colors=[],
    erase_except=[(138, 72, 56), (138, 70, 53), (139, 73, 49), (137, 71, 54), (138, 72, 55), (133, 75, 51)],
    except_tol=18, tol=40, edge=1)
SPEC[('png', 'menu_ucc/ucc_common_timer.arc__timg_ucc_timer.png')] = dict(
    text='Tempo rimasto', ui=True, box=(28, 36, 101, 53), px=13, fill=(255, 255, 255), outline=(68, 167, 208), ow=1, soft=0.4,
    spacing=0, erase=[(27, 36, 103, 53)], erase_colors=[],
    erase_except=[(90, 189, 239), (91, 190, 239), (90, 189, 238), (87, 189, 240), (98, 183, 234)], except_tol=14,
    tol=50, edge=1, rowfill=(27, 36, 103, 53), rowfill_min_sum=0)
for sz in 'lms':
    SPEC[('png', f'menu_pcshop/pc_in_obj_size_{sz}.png')] = dict(
        text=f'Mis.{sz.upper()}', ui=True, box=(1, 1, 32, 16), px=11, fill=(255, 255, 255), outline=None, spacing=0,
        erase=[(0, 0, 32, 16)], erase_colors=[(255, 255, 255), (230, 220, 220), (210, 200, 200)], tol=60, edge=1)


# ---- icone delle parole magiche はい / ちがう: lettere calligrafiche "Y" e "N" -> "Sì" e "No", stesso stile ----
for f, t in (('menu_magic_icon/ma01_14.png', 'Sì'), ('menu_magic_icon/ma01_15.png', 'No')):
    SPEC[('png', f)] = dict(
        text=t, font='KaushanScript', size=24, box=(4, 3, 28, 29), xscale='auto', fill=(24, 49, 148),
        strokes=[((24, 49, 148), 0.8)],
        shadow=None, erase=[(4, 4, 28, 28)], erase_colors=[(24, 49, 148), (40, 70, 160), (60, 90, 175), (90, 120, 195)],
        tol=60, edge=1, rowfill=(4, 4, 28, 28), rowfill_min_sum=400)


# ---- libretto della banca: titolo よきんつうちょう e unità リッチ (x3) ----
SPEC[('png', 'menu_bankbook/bank.arc__timg_bg_00.png')] = dict(
    text='Libretto', ui=True, box=(34, 16, 150, 52), px=30, fill=(0, 85, 136),
    outline=(255, 255, 255), ow=2, soft=0.8, spacing=0, weight='Bold',
    erase=[(26, 14, 156, 54)], erase_colors=[(0, 85, 136), (255, 255, 255), (119, 170, 187), (170, 204, 221),
                                             (136, 187, 204), (60, 120, 160), (238, 255, 255)], tol=40, edge=1)
SPEC[('png', 'menu_bankbook/bank.arc__timg_bg_01.png')] = dict(
    text='Ritch', texts=[('Ritch', (14, 54, 58, 74)), ('Ritch', (14, 90, 58, 110)), ('Ritch', (14, 156, 58, 176))],
    ui=True, box=(14, 54, 58, 74), px=16, fill=(0, 102, 204), outline=(255, 255, 255), ow=1.5, soft=0.6,
    spacing=0, weight='Bold',
    erase=[(14, 54, 54, 74), (14, 90, 54, 110), (14, 156, 54, 176)],
    erase_colors=[(0, 102, 204), (255, 255, 255), (102, 153, 221), (85, 153, 221), (50, 120, 210)], tol=50, edge=1)

for i, t, bg, ol, *fc in _PILL:
    SPEC[('png', f'{RUN}keit_icon_{i:02d}.png')] = dict(
        text=t, ui=True, box=(41, 7, 98, 21), px=13, fill=fc[0] if fc else (255, 255, 255), outline=ol, ow=1, soft=0.5,
        erase=[(37, 8, 98, 21)], erase_colors=[], erase_except=bg, except_tol=40, tol=40, edge=1)


# ---- prezzi (setprice): "[prezzo] リッチで [n] コ / ぜんぶうれたら … リッチ / そのうちりえきは … リッチ" ----
# due texture che a schermo si sovrappongono (plate_00 x -174, plate_01 x +56): una scheda per texture.
# Riga 1 su quadretti chiari (pattern, periodo 12), righe 2-3 su pillola azzurra uniforme (rowfill).
_SP = 'menu_setprice/setprice.arc__timg_setprice_plate_0'
_SP_BG = [(236, 252, 255), (213, 246, 255), (215, 248, 255), (235, 255, 255), (219, 244, 255), (220, 255, 255),
          (234, 251, 255), (228, 255, 255), (226, 242, 250), (214, 247, 255), (213, 247, 247), (233, 255, 255),
          (232, 249, 255), (117, 207, 240), (124, 207, 255), (116, 207, 255), (121, 206, 240), (114, 205, 246),
          (117, 208, 241), (116, 207, 240), (119, 210, 243)]
_SP_KW = dict(ui=True, px=14, fill=(35, 118, 208), outline=(255, 255, 255), ow=1.5, soft=0.6, spacing=1,
              weight='Bold', erase_colors=[], erase_except=_SP_BG, except_tol=20, tol=40, edge=1, period=12)
SPEC[('png', f'{_SP}0.png')] = dict(
    _SP_KW, text='Ritch x', halign='left',
    texts=[('Ritch x', (175, 89, 234, 109)), ('Se vendi tutto', (34, 129, 148, 151)), ('Guadagno', (34, 168, 148, 190))],
    box=(175, 89, 234, 109), erase=[(172, 88, 236, 110), (33, 129, 150, 151), (33, 168, 150, 190)],
    pattern=(150, 84, 240, 114), rowfill=(33, 129, 150, 190), rowfill_min_sum=560)
SPEC[('png', f'{_SP}1.png')] = dict(
    _SP_KW, text='pz.', halign='left',
    texts=[('pz.', (55, 91, 90, 109)), ('Ritch', (45, 131, 98, 151)), ('Ritch', (45, 169, 98, 189))],
    box=(55, 91, 84, 109), erase=[(54, 90, 86, 110), (42, 130, 86, 151), (42, 169, 86, 190)],
    pattern=(40, 84, 100, 114), rowfill=(42, 130, 98, 190), rowfill_min_sum=560)


# ---- centro commerciale (4 archivi con le stesse texture) ----
# titolo ショッピングモール (128+64, pillola rosa): la scritta lunga non entra fra i due riccioli -> si tolgono i riccioli
# (la pillola è uniforme in orizzontale: rowfill) e si tengono i cuori alle estremità.
# banner おみせをおきかえて… (256+128): scritta azzurra con contorno blu sul bianco.
# buste ダウンロード / すれちがいてんぽ (intestazione a fasce) e ali にしウイング / ひがしウィング (rosa, fondo trasparente).
_MALL_BG = [(255, 216, 233), (253, 237, 245), (255, 241, 249), (255, 230, 247), (253, 220, 237), (255, 224, 233),
            (255, 230, 239), (255, 223, 240), (255, 250, 250), (255, 225, 242), (255, 213, 230), (255, 245, 255),
            (255, 228, 255)]
for _d in ('menu_shop_mall', 'menu_shop_mall_comment', 'menu_shop_mall_edit', 'menu_shop_mall_gcoin'):
    _m = f'{_d}/shop_mall.arc__timg_'
    SPEC[('png', f'{_m}mall_title_00.png+{_m}mall_title_01.png')] = dict(
        text='Centro commerciale', ui=True, box=(30, 6, 162, 24), px=14, fill=(145, 26, 94), outline=None, spacing=1,
        weight='Bold', erase=[(27, 6, 166, 24)], erase_colors=[], erase_except=_MALL_BG, except_tol=24, tol=40, edge=1,
        rowfill=(14, 6, 178, 24), rowfill_min_sum=660)
    SPEC[('png', f'{_m}mes_win_shop_00.png+{_m}mes_win_shop_01.png')] = dict(
        text='Crea il tuo centro commerciale!', ui=True, box=(24, 19, 362, 45), px=20,
        fill=(70, 205, 250), outline=(15, 110, 200), ow=2, soft=0.6, spacing=1, weight='Bold',
        erase=[(20, 19, 366, 45)], erase_colors=[], erase_except=[(255, 255, 255), (251, 255, 255), (250, 255, 255)],
        except_tol=12, tol=40, edge=1, rowfill=(16, 19, 370, 45), rowfill_min_sum=740)
    SPEC[('png', f'{_m}mall_map_bag_00.png')] = dict(
        text='Scaricati', ui=True, box=(20, 13, 108, 31), px=14, fill=(150, 90, 220), outline=(255, 255, 255), ow=1.5,
        soft=0.6, spacing=1, weight='Bold', erase=[(26, 12, 100, 31)], erase_colors=[],
        erase_except=[(199, 207, 255), (190, 190, 239), (200, 208, 255), (197, 205, 255), (201, 209, 242),
                      (239, 230, 255), (240, 231, 255)], except_tol=20, tol=40, edge=1,
        rowfill=(14, 12, 116, 31), rowfill_min_sum=560)
    SPEC[('png', f'{_m}mall_map_bag_01.png')] = dict(
        text='Incontrati', ui=True, box=(20, 13, 108, 31), px=14, fill=(160, 100, 30), outline=(255, 255, 255), ow=1.5,
        soft=0.6, spacing=1, weight='Bold', erase=[(20, 12, 104, 31)], erase_colors=[],
        erase_except=[(255, 233, 182), (238, 197, 148), (255, 233, 175), (255, 231, 182), (255, 232, 183),
                      (237, 196, 147), (255, 230, 180), (255, 232, 191), (255, 240, 157)], except_tol=20, tol=40,
        edge=1, rowfill=(14, 12, 116, 31), rowfill_min_sum=560)
    SPEC[('png', f'{_m}mall_map_sheet.png')] = dict(
        text='Ala ovest', texts=[('Ala ovest', (30, 196, 106, 214)), ('Ala est', (140, 196, 224, 214))], ui=True,
        box=(30, 196, 106, 214), px=14, fill=(255, 153, 170), outline=(255, 255, 255), ow=1.5, soft=0.6, spacing=1,
        weight='Bold', erase=[(30, 195, 106, 215), (140, 195, 224, 215)], erase_colors=[], erase_all=True,
        clear=[(30, 195, 106, 215), (140, 195, 224, 215)], tol=40, edge=1)


# ---- editor dei disegni: fumetti-banner bianchi (stesso stile del banner del centro commerciale, 256+128) ----
_MYD_BAN = [('0', '1', 'Personalizza i tuoi capi preferiti!'),
            ('2', '3', 'Scrivi e disegna il tuo motivo!'),
            ('4', '5', 'Adatta la foto e mettila sul capo!')]
for _a, _b, _t in _MYD_BAN:
    SPEC[('png', f'{MYD}mes_win_photo_0{_a}.png+{MYD}mes_win_photo_0{_b}.png')] = dict(
        text=_t, ui=True, box=(24, 19, 362, 45), px=20, fill=(70, 205, 250), outline=(15, 110, 200), ow=2, soft=0.6,
        spacing=1, weight='Bold', erase=[(20, 19, 366, 45)], erase_colors=[],
        erase_except=[(255, 255, 255), (251, 255, 255), (250, 255, 255)], except_tol=12, tol=40, edge=1,
        rowfill=(16, 19, 370, 45), rowfill_min_sum=740)

# ---- provino (audition): pillola ランウェイモデル / オーディション中… in 3 colori; a schermo il pezzo _01 (64) sta
# a SINISTRA del _00 (128) e 3 px PIÙ IN ALTO (audition_title.bclyt: _01 y=+3) -> composizione "01^3+00".
# Testo blu notte su bianco, due righe.
_AUD = 'menu_audition/audition.arc__timg_audition_title_'
for _c in ('red', 'blue', 'yel'):
    SPEC[('png', f'{_AUD}{_c}_01.png^3+{_AUD}{_c}_00.png')] = dict(
        text='Provino modelle\nin corso…', ui=True, box=(30, 12, 190, 46), px=14, fill=(17, 51, 85), outline=None,
        spacing=1, leading=3, erase=[(26, 12, 192, 47)],
        erase_colors=[(17, 51, 85), (85, 102, 136), (153, 170, 187), (204, 204, 221), (50, 70, 100), (120, 135, 160)],
        tol=60, edge=1, rowfill=(28, 12, 192, 46), rowfill_min_sum=720)
