"""Insegne dei negozi (texture CGFX dei modelli 3D) in italiano, nello STILE dell'originale.
Per ogni insegna (SPEC): si cancella il testo giapponese (maschera = zona + colori del testo, poi
inpainting per diffusione dai bordi) e si disegna l'italiano a strati come l'originale:
ombra, contorni (dall'esterno all'interno), riempimento (colore o sfumatura verticale), a 4x poi ridotto.
  python make_signs.py preview      -> work/img_it/signs/_anteprima.png (originale | italiano)
  python make_signs.py              -> PNG in work/img_it/signs/<archivio>/<file>.png
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.join(os.path.dirname(__file__), '..')
SRC = os.path.join(ROOT, 'work', '3ds', 'romfs_x', 'model', 'map', 'shoppingmall')
OUT = os.path.join(ROOT, 'work', 'img_it', 'signs')
FONTS = os.path.join(ROOT, 'tools', 'fonts')
sys.path.insert(0, os.path.dirname(__file__))
import cgfx

S = 4   # supercampionamento
USE_LAMA = True   # ricostruzione dello sfondo con LaMa; False = OpenCV Telea

# archivio, file, testo, font, dimensione (px a 1x), box testo (x0,y0,x1,y1), riempimento, strati
# riempimento: (r,g,b) oppure ((r,g,b) alto, (r,g,b) basso); contorni: [(colore, spessore px a 1x), ...]
# erase: lista di rettangoli dove c'era il testo + colori del testo da togliere (distanza massima)
TEX = 'tex'                                                     # sorgente generica 'percorso@texture[@ritaglio]'
_MALL = 'model/map/shoppingmall/map_shoppingmall_model.tarc_x/'
_PLANE = 'model/map/plane/map_plane_model.tarc_x/'
SPEC = {
    ('shop_kanban_tex', '03.bctex'): dict(
        text='Udon', font='KaushanScript', size=36, box=(30, 6, 110, 58), rot=-4,
        fill=(36, 24, 18), strokes=[((250, 238, 205), 2), ((36, 24, 18), 1)], shadow=None,
        erase=[(31, 9, 109, 55)], erase_colors=[(30, 22, 18), (90, 70, 50), (150, 120, 80)], tol=120,
        edge=3,
        halo=[(255, 250, 235), (240, 235, 220)], grow=3, halo_tol=60, smooth=7),
    ('shop_kanban_tex', '07.bctex'): dict(
        # stesso ingombro di クレープ (x 2-85, y 17-63): la scritta arriva all'angolo in basso a sinistra
        # "C" grande che copre il bordo tagliato della carta (x~30); lettere che "saltellano" (mondo magico)
        text='Crêpes', font='Lobster', size=40, box=(1, 17, 87, 64), rot=8, anchor='bottom', xscale=0.9,
        letter_scale=[1.45, 1.0, 1.06, 0.96, 1.04, 0.98], letter_dy=[2, 0, -1, 1, -1, 1],
        fill=((120, 205, 250), (35, 130, 215)), strokes=[((30, 95, 185), 2), ((255, 255, 255), 4)],
        shadow=((20, 60, 120), (1, 2)),
        erase=[(0, 10, 94, 64)], erase_colors=[(90, 180, 240), (60, 150, 225), (150, 210, 245),
                                               (110, 200, 250), (170, 230, 255), (80, 190, 245)], tol=70,
        halo=[(255, 255, 255), (200, 235, 255)], grow=4, halo_tol=80,
        protect_colors=[(41, 41, 90), (20, 20, 60), (70, 70, 140)],   # mirtilli (blu notte)
        # carta a strisce e cono: li ricostruisce LaMa da solo (meglio di pattern/clear manuali);
        # i resti azzurri del vecchio contorno al bordo sinistro diventano trasparenti
        veto_colors=[(90, 205, 255), (130, 220, 255), (60, 170, 240), (98, 172, 230)], veto_tol=90,
        veto_zone=(0, 10, 100, 64)),     # tutta la zona del vecchio testo (la panna bianca è lontana da questi azzurri)
    ('shop_kanban_tex', '02.bctex'): dict(
        text='Ramen', font='KaushanScript', size=38, box=(2, 4, 126, 62), rot=-5,
        fill=(15, 15, 15), strokes=[((40, 40, 40), 5), ((255, 255, 255), 4), ((15, 15, 15), 1)], shadow=None,
        erase=[(0, 0, 128, 64)], erase_colors=[(15, 15, 15)], tol=60,
        halo=[(255, 255, 255), (220, 220, 220)], grow=4, halo_tol=70),
    # ---- gruppo 1: cibo e locali ----
    ('shop_kanban_tex', '01.bctex'): dict(                 # 中華飯店
        text='Cucina\nCinese', font='Shojumaru', size=60, box='auto', xscale='auto', leading=0.02,
        fill=((255, 235, 120), (225, 160, 30)), strokes=[((90, 40, 10), 2)], shadow=None,
        # colori misurati: lettere oro (224,192,48) (176,112,16) (192,144,32) + riflessi; pannello (160,0,16)
        erase=[(6, 6, 122, 58)], erase_colors=[(224, 192, 48), (176, 112, 16), (192, 144, 32), (240, 240, 192),
                                               (240, 224, 176), (208, 168, 40)], tol=60, edge=1),
    ('shop_kanban_tex', '04.bctex'): dict(                 # そば
        text='Soba', font='KaushanScript', size=60, box='auto', xscale='auto', rot=-6,
        fill=(250, 250, 245), strokes=[((60, 65, 55), 2)], shadow=None,
        erase=[(28, 4, 96, 60)], erase_colors=[(245, 245, 240), (215, 215, 205)], tol=90),
    ('shop_kanban_tex', '09.bctex'): dict(                 # 甘味処
        text='Dolci', font='MochiyPopOne', size=60, box='auto', xscale='auto', rot=-5,
        letter_scale=[1.25, 1.0, 1.05, 0.95, 1.05], letter_dy=[1, -1, 1, -1, 0],
        fill=(255, 255, 255), strokes=[((70, 35, 70), 2)], shadow=None,
        erase=[(0, 4, 78, 62)], erase_colors=[(250, 250, 250), (220, 215, 225)], tol=90),
    ('shop_kanban_tex', '11.bctex'): dict(                 # ナマステカリー
        text='Namaste Curry', font='TitanOne', size=60, box=(17, 29, 111, 51), xscale='auto',   # centrata sulla fascia
        fill=((245, 160, 40), (215, 105, 20)), strokes=[((120, 55, 10), 1)], shadow=None,
        # colori misurati: lettere (192,112,0), contorno (64,32,0), sfumature verso il bianco del pannello
        erase=[(14, 29, 122, 52)], erase_colors=[(192, 112, 0), (64, 32, 0), (208, 144, 64), (224, 176, 128),
                                                 (240, 208, 176), (128, 72, 0)], tol=50, edge=1,
        # fascia gialla uniforme in orizzontale: si ricostruisce riga per riga col colore dei suoi bordi
        erase_all=True, rowfill=(13, 29, 115, 52)),
    ('shop_kanban_tex', '12.bctex'): dict(                 # 丼 (lanterna)
        # box un po' più largo del solo 丼: usa anche lo spazio libero a destra sulla lanterna
        # "D" grande in alto a sinistra: copre i resti del contorno del 丼 (tecnica Crêpes)
        text='Donburi', font='KaushanScript', size=60, box=(42, 2, 116, 62), xscale='auto', rot=-4,
        letter_scale=[1.8, 1.0, 1.0, 1.05, 1.0, 1.0, 1.0], letter_dy=[0, 0, -1, 1, 0, -1, 1],
        veto_colors=[(255, 255, 255), (200, 200, 200), (40, 40, 50)], veto_tol=60, veto_zone=(42, 0, 104, 64),
        fill=(25, 25, 30), strokes=[((255, 255, 255), 2)], shadow=None,
        erase=[(42, 4, 100, 62)], erase_colors=[(25, 25, 30), (255, 255, 255), (60, 60, 70), (40, 40, 50),
                                                (110, 110, 120), (200, 200, 200)], tol=80, edge=2,
        # la ciotolina a sinistra non si tocca (per colore: si sovrappone al tratto sinistro del 丼)
        protect_colors=[(80, 112, 160), (64, 112, 144), (224, 160, 16), (240, 176, 48), (224, 208, 208),
                        (192, 176, 176), (96, 128, 176)], protect_tol=40, protect_zone=(0, 0, 47, 64)),
    ('shop_kanban_tex', '13.bctex'): dict(                 # 珈琲店
        text='Caffè', font='Courgette', size=60, box='auto', xscale='auto', rot=-4,
        letter_scale=[1.3, 1.0, 1.0, 1.0, 1.0], letter_dy=[1, 0, -1, 0, 0],
        fill=(250, 248, 240), strokes=[((85, 50, 30), 3)], shadow=((50, 30, 15), (1, 1)),
        erase=[(30, 16, 114, 58)], erase_colors=[(245, 245, 240), (210, 205, 195), (80, 55, 35), (120, 90, 60)],
        tol=80, edge=2),
    ('shop_kanban_tex', '17.bctex'): dict(                 # すきやき
        text='Sukiyaki', font='KaushanScript', size=60, box='auto', xscale='auto', rot=-6,
        letter_scale=[1.4, 1.0, 1.0, 1.0, 1.1, 1.0, 1.0, 1.0], letter_dy=[2, 0, -1, 1, 0, -1, 1, 0],
        fill=(250, 250, 250), strokes=[((40, 35, 35), 2)], shadow=None,
        erase=[(48, 6, 128, 62)], erase_colors=[(250, 250, 250), (220, 220, 220)], tol=80),
    ('shop_kanban_tex', '18.bctex'): dict(                 # 鉄板焼き
        # appoggiata sul bordo della piastra e più alta: copre i buchi della spatola (tecnica Crêpes)
        text='Teppanyaki', font='PottaOne', size=60, box=(0, 5, 128, 49), anchor='bottom', xscale='auto', rot=-3,
        letter_scale=[1.35, 1.0, 1.05, 1.0, 1.08, 1.0, 1.05, 1.0, 1.08, 1.0], letter_dy=[1, 0, -1, 1, 0, -1, 1, 0, -1, 1],
        # contorno bianco spesso come in 鉄板焼き: unisce le lettere in un "adesivo" e copre i manici delle spatole
        fill=((240, 90, 20), (200, 50, 10)), strokes=[((255, 255, 255), 5)], shadow=None, fill_holes=(255, 255, 255),
        erase=[(0, 0, 128, 44)], erase_colors=[(220, 70, 20), (240, 110, 40), (255, 255, 255)], tol=90,
        # spatole tolte: grigio-marroni nell'angolo in alto a destra, sopra la piastra
        erase2=dict(zone=(84, 0, 128, 34), colors=[(96, 80, 64), (48, 32, 32), (64, 64, 48), (80, 80, 64),
                                                   (112, 96, 80), (32, 24, 24)], tol=70),
        # il vecchio contorno bianco sopra la piastra: LaMa lo "continua" come fumo -> secondo passaggio/vuoto
        veto_colors=[(255, 255, 255), (235, 235, 235), (210, 215, 215)], veto_tol=60, veto_zone=(0, 0, 128, 40),
        repass=dict(zone=(60, 30, 128, 50), min_sum=450),   # velo chiaro sopra il bordo destro della piastra
        clear=[(0, 0, 128, 33), (92, 0, 128, 38), (120, 38, 128, 52)]),        # sopra la piastra c'era il vuoto (la spatola non è in maschera: resta)
    ('shop_kanban_tex', '19.bctex'): dict(                 # 寿司
        text='Sushi', font='KaushanScript', size=60, box='auto', xscale='auto', rot=-4,
        fill=(30, 30, 60), strokes=[((250, 225, 140), 1)], shadow=None,
        erase=[(26, 8, 104, 58)], erase_colors=[(30, 30, 60), (60, 60, 90)], tol=80, edge=2,
        halo=[(250, 230, 150), (255, 245, 200)], grow=3, halo_tol=70),
    ('shop_kanban_tex', '20.bctex'): dict(                 # 食堂
        text='Trattoria', font='AbrilFatface', size=60, box=(16, 12, 114, 54), xscale='auto',
        letter_scale=[1.3, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        fill=(15, 15, 15), strokes=[((255, 255, 255), 2)], shadow=None,
        # si cancella anche il sole arancione (coperto quasi tutto dalle lettere), poi l'anello ridipinto
        # pulito; la zona NON tocca i bordi del pannello (mezzelune verdi, sporgenze sopra/sotto)
        erase=[(20, 7, 110, 55)], erase_colors=[(15, 15, 15), (255, 255, 255),
                                                (255, 124, 43), (255, 148, 82), (240, 170, 110)], tol=60, edge=1,
        ring=dict(c=(64, 31), ro=24, ri=18, color=(255, 132, 50), color2=(250, 118, 38))),
    # ---- gruppo 2: moda, casa e negozi vari ----
    ('shop_kanban_tex', '22.bctex'): dict(                 # グリーンガーデン (prestito inglese)
        text='Green\nGarden', font='Grandstander', variant='Bold', size=60, box='auto', xscale='auto', rot=-4,
        fill=((205, 245, 95), (120, 180, 20)), strokes=[((45, 70, 10), 2)], shadow=None,
        erase=[(16, 8, 112, 56)], erase_colors=[(144, 192, 16), (160, 208, 48), (128, 160, 64), (112, 144, 64),
                                                (176, 224, 96), (208, 240, 128), (80, 96, 16)], tol=60),
    ('shop_kanban_tex', '28.bctex'): dict(                 # ボウシ屋 (lettere multicolore sul cappello)
        text='Cappelli', font='Fredoka', variant='Bold', size=60, box='auto', xscale='auto', rot=-6,
        letter_fill=[(110, 190, 50), (90, 150, 230), (170, 110, 220), (160, 96, 64)],
        strokes=[((255, 255, 255), 2)], shadow=None,
        erase=[(14, 22, 124, 60)], erase_colors=[], tol=60,
        erase_except=[(224, 64, 96), (240, 192, 208), (240, 112, 144), (240, 240, 240), (192, 0, 48),
                      (240, 80, 112), (240, 160, 176)], except_tol=50),
    ('shop_kanban_tex', '31.bctex'): dict(                 # せれくとショップ (prestito inglese, stile neon)
        # due righe sfalsate come せれくと (in alto a sinistra) e ショップ (in basso a destra)
        text='Select Shop', font='Satisfy', size=60, xscale='auto', xscale_min=0.75,
        lines_at=[dict(text='Select', box=(3, 3, 72, 40), rot=-6, letter_scale=[1.35, 1, 1, 1.05, 1, 1],
                       letter_dy=[1, 0, -1, 0, 1, 0]),
                  dict(text='Shop', box=(50, 26, 120, 61), rot=-6, letter_scale=[1.35, 1, 1.05, 1],
                       letter_dy=[0, 1, -1, 1])],
        fill=(255, 255, 255), strokes=[((150, 30, 170), 4), ((240, 110, 200), 2)], shadow=None,
        erase=[(0, 4, 124, 62)], erase_colors=[(240, 240, 240), (240, 112, 192), (240, 176, 224)], tol=60),
    ('shop_kanban_tex', '32.bctex'): dict(                 # アクアショップ
        text='Acquari', font='Fredoka', variant='Bold', size=60, box='auto', xscale='auto', rot=-3,
        fill=((195, 240, 255), (110, 200, 240)), strokes=[((20, 70, 150), 2)], shadow=None,
        erase=[(0, 34, 126, 63)], erase_colors=[(160, 224, 240), (128, 224, 240), (144, 224, 240),
                                                (16, 64, 144), (16, 64, 160), (96, 176, 224)], tol=60,
        protect_colors=[(240, 64, 0), (240, 128, 64), (16, 16, 16)], protect_zone=(40, 0, 128, 48)),
    ('shop_kanban_tex', '33.bctex'): dict(                 # 魚屋
        text='Pescheria', font='PermanentMarker', size=60, box=(16, 10, 112, 62), xscale='auto', xscale_min=0.6, rot=-5,
        letter_scale=[1.35, 1, 1, 1, 1, 1, 1, 1, 1], letter_dy=[1, 0, -1, 1, 0, -1, 1, 0, -1],
        fill=(15, 20, 30), strokes=[((255, 255, 255), 3)], shadow=None,
        erase=[(24, 14, 106, 62)], erase_colors=[(0, 0, 0), (16, 32, 32), (32, 40, 48), (16, 48, 96), (32, 64, 112)],
        tol=60, edge=1,
        halo=[(240, 240, 240), (224, 240, 240)], grow=3, halo_tol=60),
    ('shop_kanban_tex', '34.bctex'): dict(                 # よろずや (emporio generico)
        text='Bazar', font='AbrilFatface', size=60, box='auto', xscale='auto',
        fill=((255, 235, 140), (200, 140, 30)), strokes=[((90, 50, 10), 2)], shadow=None,
        erase=[(14, 10, 116, 54)], erase_colors=[], tol=60,
        erase_except=[(16, 16, 16), (16, 16, 0), (0, 0, 0), (24, 24, 24)], except_tol=45),
    ('shop_kanban_tex', '37.bctex'): dict(                 # マーケット (FRESH FOOD resta)
        text='MERCATO', font='Bungee', size=60, box='auto', xscale='auto',
        fill=(255, 255, 255), strokes=[((150, 0, 0), 1)], shadow=None,
        erase=[(14, 36, 116, 60)], erase_colors=[], tol=60,
        erase_except=[(192, 0, 0), (240, 32, 0), (176, 0, 0), (208, 16, 0)], except_tol=60),
    ('shop_kanban_tex', '38.bctex'): dict(                 # インテリア: una lettera per faccia di cubo
        # ogni lettera riempie il riquadro della katakana originale; tratto da pennarello marrone come l'originale
        text='DECOR', font='PermanentMarker', size=40,
        letters_box=[('D', 6, 20, 22, 47, 3), ('E', 29, 22, 47, 44, -4), ('C', 55, 8, 74, 30, 0),
                     ('O', 87, 16, 102, 40, 0), ('R', 107, 32, 122, 56, -3)],
        fill=(115, 55, 45), strokes=[], shadow=None,
        erase=[(0, 6, 124, 60)], erase_colors=[(112, 64, 48), (80, 48, 32), (128, 80, 64), (96, 56, 40)], tol=45),
    ('shop_kanban_tex', '39.bctex'): dict(                 # 電器店: l'insegna è solo il neon delle lettere
        # stile neon dell'originale (cuore bianco, anelli arancio) e fulmine giallo tenuto al suo posto
        text='Elettronica', font='Righteous', size=60, box=(36, 3, 127, 61), xscale='auto', xscale_min=0.45,
        letter_scale=[1.4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        fill=(255, 255, 245), strokes=[((176, 96, 0), 8), ((240, 140, 0), 6), ((255, 200, 90), 3)], shadow=None,
        erase=[(0, 0, 128, 64)], erase_colors=[], tol=60, erase_all=True, clear=[(0, 0, 128, 64)],
        protect_colors=[(240, 224, 0), (240, 240, 96), (248, 232, 32)], protect_tol=30,
        protect_zone=(14, 30, 42, 51)),
    ('shop_kanban_tex', '41.bctex'): dict(                 # 時計店
        text='Orologi', font='PlayfairDisplay', variant='Bold', size=60, box='auto', xscale='auto',
        fill=((255, 235, 150), (200, 150, 40)), strokes=[((60, 40, 10), 1)], shadow=None,
        erase=[(54, 12, 122, 54)], erase_colors=[], tol=60,
        erase_except=[(32, 16, 32), (48, 32, 32), (16, 16, 16), (40, 24, 40)], except_tol=40),
    ('shop_kanban_tex', '42.bctex'): dict(                 # 楽器店
        text='Strumenti', font='SigmarOne', size=60, box=(1, 19, 127, 64), xscale='auto', xscale_min=0.55, rot=-3,
        letter_scale=[1.25, 1, 1, 1, 1, 1, 1, 1, 1], letter_dy=[1, 0, -1, 0, 1, 0, -1, 0, 1],
        fill=((255, 225, 120), (210, 130, 30)), strokes=[((20, 5, 0), 3)], shadow=None,
        erase=[(0, 24, 128, 64)], erase_colors=[(208, 128, 32), (240, 192, 64), (240, 224, 128), (176, 96, 16),
                                                (240, 224, 112), (192, 112, 16), (128, 80, 16), (144, 80, 16)],
        tol=50, erase2=dict(zone=(0, 34, 128, 64), colors=[(16, 0, 0), (0, 0, 0), (32, 8, 0), (48, 16, 0)], tol=50),
        protect_colors=[(128, 48, 0), (96, 32, 0), (112, 48, 0), (144, 64, 0), (144, 48, 0), (176, 80, 16)],
        protect_tol=28,
        protect_zone=(34, 0, 128, 44)),
    ('shop_kanban_tex', '43.bctex'): dict(                 # 百貨店
        text='Grandi\nMagazzini', font='PlayfairDisplay', variant='Bold', size=60, box='auto', xscale='auto',
        leading=-0.1, fill=(250, 245, 205), strokes=[((60, 0, 20), 1)], shadow=None,
        erase=[(28, 21, 122, 60)], erase_colors=[], tol=60, edge=2,
        erase_except=[(80, 0, 32), (96, 32, 48), (64, 0, 16), (88, 16, 40)], except_tol=45),
    ('shop_kanban_tex', '47.bctex'): dict(                 # ユニフォーム ("divisa" nei dialoghi)
        text='Divise', font='TitanOne', size=60, box='auto', xscale='auto',
        fill=((255, 240, 80), (240, 190, 0)), strokes=[((190, 110, 0), 3)], shadow=None,
        erase=[(6, 20, 124, 54)], erase_colors=[(240, 224, 48), (192, 112, 0), (240, 192, 0), (240, 160, 0),
                                                (224, 176, 32), (160, 96, 0)], tol=50),
    ('shop_kanban_tex', '50.bctex'): dict(                 # ふしぎメゾン (lettere multicolore)
        # lettere che seguono la nuvoletta, con altezze diverse come ふしぎメゾン
        text='Maison Magica', font='CherrySwash', size=60, box=(5, 13, 123, 59), xscale='auto', xscale_min=0.5, rot=-3,
        letter_scale=[1.45, 1.0, 1.1, 0.95, 1.05, 1.0, 0.6, 1.45, 1.0, 1.1, 0.95, 1.05, 1.15],
        letter_dy=[3, 0, -2, 0, 1, -1, 0, 3, 0, -2, 1, -1, 1],
        letter_fill=[(240, 90, 200), (90, 220, 50), (240, 220, 60), (220, 40, 180), (120, 200, 255), (240, 220, 60),
                     (220, 40, 180), (240, 220, 60), (90, 220, 50), (240, 90, 200), (120, 200, 255), (240, 220, 60)],
        strokes=[((80, 48, 144), 3), ((255, 255, 255), 2)], shadow=None,
        erase=[(6, 16, 122, 58)], erase_colors=[], tol=60,
        erase_except=[(224, 224, 240), (240, 240, 240), (144, 80, 192), (80, 48, 144), (160, 96, 208),
                      (208, 208, 232), (232, 232, 248)], edge=2,
        rowfill=(14, 20, 114, 54), rowfill_min_sum=640,   # nuvoletta bianco-lavanda uniforme in orizzontale
        except_tol=45),
    # ---- città: atlante shop_magic01 (9 varianti di stagione) ----
    ('atlas', 'shop_magic01@0,256,128,320'): dict(          # targa かめや (scritta "やめか") -> Emporio
        text='Emporio', font='KaushanScript', size=60, box='auto', xscale='auto',
        letter_scale=[1.3, 1, 1, 1, 1, 1, 1], letter_dy=[1, 0, -1, 0, 1, 0, -1],
        fill=(40, 35, 22), strokes=[], shadow=None,
        # interno crema con sfumatura verticale: tutto ciò che non è crema si toglie e si rifà riga per riga
        erase=[(18, 17, 106, 50)], erase_colors=[], tol=45, edge=1,
        erase_except=[(224, 208, 208), (240, 224, 224), (208, 192, 192), (232, 216, 216), (216, 200, 200)],
        except_tol=40, rowfill=(18, 17, 106, 50), rowfill_min_sum=560),
    ('atlas', 'shop_magic01@60,128,100,256'): dict(         # tavoletta verticale 魔法の材料 -> MAGIA
        text='MAGIA', font='KaushanScript', size=40,
        letters_box=[('M', 9, 16, 27, 32, 0), ('A', 9, 33, 27, 49, 0), ('G', 9, 50, 27, 66, 0),
                     ('I', 9, 67, 27, 84, 0), ('A', 9, 85, 27, 101, 0)],
        fill=(45, 18, 5), strokes=[], shadow=None,
        erase=[(9, 15, 28, 106)], erase_colors=[(32, 0, 0), (48, 16, 0), (48, 32, 0), (64, 32, 0), (16, 0, 0)],
        tol=30, edge=1,
        erase_except=[(96, 48, 32), (112, 80, 48), (96, 64, 32), (112, 64, 32), (128, 80, 48), (120, 78, 45)],
        except_tol=22),
    # ---- interno del negozio di magia (texture nel modello sh_r_mahou.bcres) ----
    ('plane', 'sh_r_mahou.bcres@r_maho_bord00'): dict(      # rotolo verticale 魔法の材料 -> MAGIA (come fuori)
        text='MAGIA', font='KaushanScript', size=36,
        letters_box=[('M', 8, 16, 25, 32, 0), ('A', 8, 33, 25, 49, 0), ('G', 8, 50, 25, 66, 0),
                     ('I', 8, 67, 25, 84, 0), ('A', 8, 85, 25, 101, 0)],
        fill=(45, 18, 5), strokes=[], shadow=None,
        erase=[(7, 15, 26, 106)], erase_colors=[(32, 0, 0), (48, 16, 0), (48, 32, 0), (64, 32, 0), (16, 0, 0),
                                                (80, 40, 16)],
        tol=34, edge=1,
        erase_except=[(96, 48, 32), (112, 80, 48), (96, 64, 32), (112, 64, 32), (128, 80, 48), (120, 78, 45)],
        except_tol=22),
    ('plane', 'sh_r_mahou.bcres@r_maho_exit'): dict(        # tappetino 来来 (tile specchiato): stella magica
        star=dict(c=(37, 32), ro=19, ri=5.5, n=4, fill=(30, 200, 115), outline=(8, 105, 50), ow=1.3,
                  core=(2.2, (190, 255, 210))),
        erase=[(16, 6, 64, 62)], erase_colors=[],
        erase_except=[(200, 24, 0), (184, 16, 0), (216, 32, 0), (168, 8, 0), (152, 0, 0), (136, 0, 0)],
        except_tol=45, tol=70, edge=2, smooth=3),
    # ---- inventario texture 3D (tex_inventory + tex_review_merge): sorgente 'tex', tutte le copie identiche ----
    (TEX, _MALL + 'ShopDef05.bcres@05_magic@0,128,128,192'): dict(   # facciata vicina: targa やめか -> Emporio
        text='Emporio', font='KaushanScript', size=60, box='auto', xscale='auto',
        letter_scale=[1.3, 1, 1, 1, 1, 1, 1], letter_dy=[1, 0, -1, 0, 1, 0, -1],
        fill=(40, 35, 22), strokes=[], shadow=None,
        erase=[(18, 8, 110, 49)], erase_colors=[], tol=45, edge=1,
        erase_except=[(224, 208, 208), (240, 224, 224), (208, 192, 192), (232, 216, 216), (216, 200, 200)],
        except_tol=40, rowfill=(18, 8, 110, 49), rowfill_min_sum=560),
    (TEX, _MALL + 'ShopDef05.bcres@05_magic@128,192,256,224'): dict(  # listello orizzontale 魔法の材料 -> MAGIA
        text='MAGIA', font='KaushanScript', size=34,
        letters_box=[('M', 20, 4, 36, 28, 0), ('A', 38, 4, 54, 28, 0), ('G', 56, 4, 72, 28, 0),
                     ('I', 74, 4, 90, 28, 0), ('A', 92, 4, 108, 28, 0)],
        fill=(45, 18, 5), strokes=[], shadow=None,
        erase=[(16, 2, 112, 30)], erase_colors=[(32, 0, 0), (48, 16, 0), (48, 32, 0), (64, 32, 0), (16, 0, 0),
                                                (80, 40, 16)], tol=34, edge=1),
    (TEX, _MALL + 'ShopDef05SideBoard.bctex@05_magic_side'): dict(   # targa laterale (più grande) -> Emporio
        text='Emporio', font='KaushanScript', size=60, xscale='auto',
        letter_scale=[1.3, 1, 1, 1, 1, 1, 1], letter_dy=[1, 0, -1, 0, 1, 0, -1],
        fill=(40, 35, 22), strokes=[], shadow=None,
        box=(20, 14, 112, 49), erase=[(18, 14, 114, 52)], erase_colors=[], tol=45, edge=1,
        erase_except=[(224, 208, 208), (240, 224, 224), (208, 192, 192), (232, 216, 216), (216, 200, 200)],
        except_tol=40),
    (TEX, _PLANE + 'sc_classroom.bcres@bg_r_sc00_p00'): dict(       # calligrafia げんき/に (aula)
        text='Un bel\nsaluto', font='KaushanScript', size=40, box=(3, 4, 61, 60), xscale='auto', leading=-0.15,
        fill=(20, 20, 24), strokes=[], shadow=None,
        erase=[(0, 0, 64, 64)], erase_colors=[], erase_except=[(240, 240, 248), (224, 224, 232), (255, 255, 255)],
        except_tol=40, tol=40, edge=1),
    (TEX, _PLANE + 'sc_classroom.bcres@bg_r_sc00_p01'): dict(       # calligrafia あい/さつ
        text='con\ngioia!', font='KaushanScript', size=40, box=(3, 4, 61, 60), xscale='auto', leading=-0.15,
        fill=(20, 20, 24), strokes=[], shadow=None,
        erase=[(0, 0, 64, 64)], erase_colors=[], erase_except=[(240, 240, 248), (224, 224, 232), (255, 255, 255)],
        except_tol=40, tol=40, edge=1),
    (TEX, _PLANE + 'sc_passage.bcres@sc_path_frame'): dict(         # cornice 一日一魔法 (corridoio)
        text='Una magia\nal giorno', font='KaushanScript', size=60, box=(28, 30, 212, 106), xscale='auto',
        leading=-0.2, fill=(24, 18, 14), strokes=[], shadow=None,
        erase=[(30, 34, 216, 108)], erase_colors=[(0, 0, 0), (32, 24, 16), (64, 48, 40), (96, 88, 80),
                                                  (128, 120, 112), (160, 152, 144)], tol=60, edge=2,
        protect=[(216, 80, 240, 106)]),
    (TEX, _PLANE + 'uma_b_cloth.bcres@huku_b'): dict(                # sacchetto 福 -> "?" (sacchetto a sorpresa)
        text='?', font='TitanOne', size=40, box=(10, 24, 40, 60), fill=(255, 255, 255), strokes=[], shadow=None,
        erase=[(8, 24, 42, 60)], erase_colors=[(255, 255, 255), (240, 224, 224), (240, 200, 200), (224, 160, 160)],
        tol=70, edge=1),
    (TEX, _PLANE + 'uma_yt_isu.bcres@yatai01@32,32,64,96'): dict(    # lanterna ラーメン -> RAMEN in colonna
        text='RAMEN', font='LilitaOne', size=16,
        letters_box=[('R', 4, 8, 28, 18, 0), ('A', 4, 18, 28, 28, 0), ('M', 4, 28, 28, 38, 0),
                     ('E', 4, 38, 28, 48, 0), ('N', 4, 48, 28, 58, 0)],
        fill=(10, 10, 10), strokes=[], shadow=None, erase=[(2, 6, 30, 62)], erase_colors=[(0, 0, 0), (32, 0, 0),
        (64, 16, 0)], tol=70, edge=1),
    (TEX, _PLANE + 'uma_yt_isu.bcres@yatai01@0,100,128,128'): dict(  # noren ひげまる -> Baffo
        text='Baffo', font='Shojumaru', size=22,
        letters_box=[('B', 6, 2, 28, 24, 0), ('a', 34, 4, 54, 24, 0), ('f', 58, 2, 76, 24, 0),
                     ('f', 80, 2, 98, 24, 0), ('o', 104, 4, 124, 24, 0)],
        fill=(240, 224, 64), strokes=[], shadow=None,
        erase=[(0, 1, 128, 25)], erase_colors=[(240, 224, 64), (224, 208, 48), (240, 240, 96), (208, 176, 48),
                                               (192, 160, 64)], tol=60, edge=1),
    (TEX, _PLANE + 'uma_yt_isu.bcres@yatai01@28,132,62,190'): dict(  # targa bianca ラーメン -> RAMEN in colonna
        text='RAMEN', font='LilitaOne', size=16,
        letters_box=[('R', 6, 6, 28, 15, 0), ('A', 6, 16, 28, 25, 0), ('M', 6, 26, 28, 35, 0),
                     ('E', 6, 36, 28, 45, 0), ('N', 6, 46, 28, 55, 0)],
        fill=(10, 10, 10), strokes=[], shadow=None,
        erase=[(4, 4, 30, 56)], erase_colors=[(0, 0, 0), (32, 32, 32), (64, 64, 64), (96, 96, 96)], tol=60, edge=1),
    (TEX, _MALL + 'FairObjectSeason00.bcres@fair_object_January'): dict(   # daruma 初売 -> Primi saldi
        text='Primi\nsaldi', font='KaushanScript', size=60, box=(84, 150, 174, 234), xscale='auto', leading=-0.2,
        fill=(112, 72, 16), strokes=[], shadow=None,
        erase=[(80, 148, 178, 236)], erase_colors=[(112, 72, 16), (96, 56, 8), (128, 88, 32), (80, 48, 8),
                                                   (144, 112, 64)], tol=60, edge=1),
    (TEX, _MALL + 'FairObjectSeason07.bcres@fair_object_August01@128,0,192,64'): dict(   # lanterna 祭 (spenta)
        text='Festa', font='LilitaOne', size=24, box=(4, 14, 60, 50), xscale='auto',
        fill=(255, 236, 236), strokes=[((200, 40, 40), 1)], shadow=None,
        erase=[(10, 10, 56, 60)], erase_colors=[(255, 255, 255), (240, 208, 208), (240, 176, 176), (255, 224, 224)],
        tol=80, edge=1),
    (TEX, _MALL + 'FairObjectSeason07.bcres@fair_object_August01@192,0,256,64'): dict(   # lanterna 祭 (accesa)
        text='Festa', font='LilitaOne', size=24, box=(4, 14, 60, 50), xscale='auto',
        fill=(232, 56, 48), strokes=[((255, 240, 240), 1)], shadow=None,
        erase=[(8, 8, 58, 62)], erase_colors=[],
        erase_except=[(240, 240, 240), (224, 224, 224), (208, 208, 208), (192, 192, 192), (232, 232, 232),
                      (255, 255, 255)], except_tol=30, tol=70, edge=1),
    (TEX, _MALL + 'FairObjectSeason07.bcres@fair_object_August01@0,64,64,128'): dict(    # adesivo 祭
        text='Festa', font='LilitaOne', size=26, box=(3, 18, 61, 48), xscale='auto',
        fill=(12, 12, 20), strokes=[((255, 255, 255), 2), ((232, 168, 168), 2)], shadow=None,
        erase=[(0, 0, 64, 64)], erase_colors=[], erase_all=True, tol=40, edge=1, clear=[(0, 0, 64, 64)]),
    (TEX, _MALL + 'ShopBoard.bcres@kanban00'): None,                 # ふしぎメゾン: stessa scheda del 50.bctex
    (TEX, 'model/char/npc_model_clothtex.tarc_x/npc1052c01_cloth.bctex@c01_cloth@40,4,80,36'): dict(  # happi 祭
        text='Festa', font='LilitaOne', size=14, box=(2, 7, 38, 25), xscale='auto',
        fill=(224, 24, 24), strokes=[((255, 255, 255), 1)], shadow=None,
        erase=[(6, 4, 36, 30)], erase_colors=[(224, 24, 24), (240, 64, 64), (255, 255, 255), (240, 160, 160),
                                              (192, 32, 32)], tol=70, edge=1),
    (TEX, 'model/npc/npc_model.tarc_x/1052.bcres@ch00_top1@40,4,80,36'): None,   # stessa happi nel modello
    (TEX, 'model/char/npc_model_base.tarc_x/uma_09.bcmdl@c02_skin@16,0,56,32'): dict(   # ventaglio 賞 -> Bravo!
        text='Bravo!', font='KaushanScript', size=16, box=(4, 4, 36, 26), xscale='auto', rot=-6,
        fill=(30, 16, 12), strokes=[], shadow=None,
        erase=[(6, 2, 36, 30)], erase_colors=[(30, 16, 12), (64, 32, 24), (96, 48, 40), (128, 64, 48)],
        tol=60, edge=1),
    # ---- gruppo 3: insegne stagionali ----
    ('shop_kanban_season_tex', '05.bctex'): dict(          # おかあさんありがとう (festa della mamma)
        text='Grazie\nmamma!', font='Fredoka', variant='Bold', size=60, box='auto', xscale='auto', leading=-0.1,
        fill=((250, 135, 175), (230, 60, 120)), strokes=[((255, 255, 255), 3)], shadow=None,
        fill_holes=(255, 255, 255),
        erase=[(20, 6, 108, 58)], erase_colors=[(240, 80, 112), (240, 128, 160), (240, 160, 176), (240, 112, 144)],
        tol=45, halo=[(240, 240, 240), (255, 255, 255)], grow=3, halo_tol=50),
    ('shop_kanban_season_tex', '06.bctex'): dict(          # おとうさんありがとう (festa del papà)
        text='Grazie\npapà!', font='Fredoka', variant='Bold', size=60, box='auto', xscale='auto', rot=10,
        leading=-0.1, fill=(255, 255, 255), strokes=[((30, 60, 170), 3), ((120, 160, 240), 1)], shadow=None,
        erase=[(2, 4, 88, 60)], erase_colors=[(240, 240, 240), (224, 240, 240), (128, 160, 240), (176, 192, 240),
                                              (224, 224, 240)], tol=50, edge=1),
    ('shop_kanban_season_tex', '08.bctex'): dict(          # 祭 (festival)
        text='Festa', font='KaushanScript', size=60, box='auto', xscale='auto', rot=-5,
        letter_scale=[1.4, 1, 1, 1, 1], letter_dy=[1, 0, -1, 1, 0],
        fill=(15, 15, 15), strokes=[((255, 255, 255), 3)], shadow=None, fill_holes=(255, 255, 255),
        erase=[(36, 8, 94, 60)], erase_colors=[(0, 0, 0), (16, 16, 16)], tol=60, edge=1,
        halo=[(240, 240, 240), (255, 255, 255)], grow=3, halo_tol=50),
    ('shop_kanban_season_tex', '11.bctex'): dict(          # 芸術祭 (festa dell'arte)
        text="Festa\ndell'Arte", font='CherrySwash', size=60, box=(10, 15, 124, 59), xscale='auto', leading=-0.2,
        fill=((230, 70, 240), (190, 0, 200)), strokes=[((90, 20, 130), 3), ((255, 230, 255), 2)], shadow=None,
        erase=[(10, 16, 124, 58)], erase_colors=[(208, 0, 224), (208, 0, 208), (224, 48, 224), (192, 0, 192),
                                                (240, 160, 240), (224, 112, 240), (240, 128, 240)],
        tol=45, edge=2, halo=[(240, 208, 240), (255, 240, 255)], grow=3, halo_tol=50,
        protect_colors=[(160, 48, 224), (128, 64, 208), (96, 32, 160), (112, 48, 176)], protect_tol=25),
    ('shop_kanban_season_tex', '17.bctex'): dict(          # お得意様セール (saldi per i clienti affezionati)
        text='Saldi\nVIP', font='Righteous', size=60, box='auto', xscale='auto', leading=-0.05,
        fill=((255, 235, 170), (220, 150, 60)), strokes=[((110, 30, 0), 2), ((255, 250, 230), 1)], shadow=None,
        erase=[(14, 8, 112, 60)], erase_colors=[(192, 96, 32), (240, 240, 224), (240, 240, 240), (224, 160, 96),
                                                (240, 208, 160)], tol=50, edge=1),
    ('shop_kanban_season_tex', '18.bctex'): dict(          # 特価品セール! : l'insegna è solo scritta
        text='Offerte speciali!', font='SigmarOne', size=60, xscale='auto', xscale_min=0.6,
        lines_at=[dict(text='Offerte', box=(1, 6, 92, 42), rot=-4, fill=((240, 40, 30), (190, 0, 0)),
                       strokes=[((0, 0, 0), 5), ((255, 255, 255), 3)], letter_scale=[1.25, 1, 1, 1, 1, 1, 1]),
                  dict(text='speciali!', box=(40, 30, 125, 62), rot=-4, fill=(15, 15, 15),
                       strokes=[((0, 0, 0), 4), ((255, 255, 255), 2)])],
        fill=(15, 15, 15), strokes=[], shadow=None, fill_holes=(255, 255, 255),
        erase=[(0, 0, 128, 64)], erase_colors=[], tol=60, erase_all=True, clear=[(0, 0, 128, 64)]),
    ('shop_kanban_season_tex', '19.bctex'): dict(          # 特売日セール! sull'esplosione rossa/gialla
        text='Giorno di saldi!', font='BowlbyOneSC', size=60, xscale='auto', xscale_min=0.6,
        lines_at=[dict(text='Giorno', box=(1, 3, 96, 40), rot=-4, letter_scale=[1.3, 1, 1, 1, 1, 1]),
                  dict(text='di saldi!', box=(36, 30, 126, 62), rot=-4)],
        fill=(10, 10, 10), strokes=[((255, 255, 255), 4)], shadow=None, fill_holes=(255, 255, 255),
        erase=[(0, 0, 128, 64)], erase_colors=[(0, 0, 0), (240, 240, 240), (48, 48, 48), (64, 64, 64),
                                               (80, 80, 80), (255, 255, 255)], tol=50, edge=1),
}
# immagini 2D della UI (sorgente 'png', font UI): schede in ui_specs.py
import ui_specs
SPEC.update(ui_specs.SPEC)
# schede uguali ad altre (stessa grafica in un altro file)
SPEC[(TEX, _MALL + 'ShopBoard.bcres@kanban00')] = dict(SPEC[('shop_kanban_tex', '50.bctex')])
SPEC[(TEX, 'model/npc/npc_model.tarc_x/1052.bcres@ch00_top1@40,4,80,36')] = dict(
    SPEC[(TEX, 'model/char/npc_model_clothtex.tarc_x/npc1052c01_cloth.bctex@c01_cloth@40,4,80,36')])
# adesivo 祭 della piazza in città: stesso disegno della fiera di agosto, nell'atlante delle stagioni
SPEC[('atlas', 'sp_maturi@0,64,64,128')] = dict(
    SPEC[(TEX, _MALL + 'FairObjectSeason07.bcres@fair_object_August01@0,64,64,128')])

# ---- insegne come nel DS EUROPEO: Harrows, Vivian's Boutique, Daisy's Flowers ----
_GOLD = ((252, 238, 150), (196, 142, 24))
_GOLD_COLS = [(252, 240, 170), (240, 210, 70), (200, 160, 30), (160, 110, 20), (110, 70, 15), (70, 40, 10),
              (255, 250, 220), (224, 184, 48), (180, 130, 20), (130, 90, 15), (90, 55, 10)]


def _halogen(dx=0, dy=0, **kw):
    """Halogen -> Harrows: stesso stile oro (sfumatura + contorno bruno); la barra sotto resta"""
    sp = dict(
        text='Harrows', font='PlayfairDisplay', variant='Bold', size=60, box=(5 + dx, 12 + dy, 123 + dx, 48 + dy),
        xscale='auto', fill=_GOLD, strokes=[((96, 58, 12), 1)], shadow=((70, 40, 10), (1, 1)),
        erase=[(5 + dx, 12 + dy, 123 + dx, 49 + dy), (68 + dx, 49 + dy, 92 + dx, 54 + dy)], erase_colors=[], erase_all=True,
        tol=40, edge=1, rowfill=(60 + dx, 49 + dy, 100 + dx, 54 + dy), clear=[(5 + dx, 12 + dy, 123 + dx, 49 + dy)])
    sp.update(kw)
    return sp


_DAISY_COLS = [(247, 189, 90), (243, 192, 90), (246, 189, 90), (251, 183, 98), (247, 196, 94), (192, 124, 56),
               (169, 101, 33), (214, 156, 66), (209, 158, 73), (221, 153, 68), (219, 153, 70), (241, 183, 93),
               (196, 128, 43), (170, 102, 34)]


def _daisy(dx=0, dy=0, **kw):
    """Flowerdaisy -> Daisy's Flowers: scritta oro su pannello rosso (rifatto riga per riga); la cornice
    (diagonali comprese) e le margherite restano"""
    sp = dict(
        text="Daisy's Flowers", font='Courgette', size=60, box=(40 + dx, 17 + dy, 211 + dx, 46 + dy), xscale='auto',
        xscale_min=0.5, fill=((250, 204, 112), (238, 172, 72)), strokes=[((246, 190, 92), 1)],
        shadow=((150, 90, 30), (1, 1)),
        erase=[(38 + dx, 16 + dy, 213 + dx, 48 + dy)], erase_colors=[], tol=36, edge=1,
        # tutto cio' che NON e' rosso pannello si toglie (lettere), poi il pannello si rifa riga per riga
        erase_except=[(206, 0, 16), (205, 0, 18), (192, 5, 22), (170, 17, 17), (160, 20, 20), (196, 0, 9),
                      (112, 10, 10), (161, 0, 0), (214, 78, 27)], except_tol=30,
        season_override={'08_fushigi': dict(erase_except=[
            (206, 0, 99), (205, 0, 103), (192, 5, 90), (156, 16, 65), (153, 17, 68), (196, 0, 94), (112, 10, 44),
            (162, 0, 60), (128, 26, 0)])},
        protect_lines=[((52 + dx, 13 + dy), (36 + dx, 26 + dy), 3.5), ((192 + dx, 12 + dy), (218 + dx, 24 + dy), 3.2)],
        rowfill=(38 + dx, 16 + dy, 213 + dx, 50 + dy))
    sp.update(kw)
    return sp


_SMILE_BLUE = (36, 121, 206)


def _smile(**kw):
    """striscia "Smile ★" -> "Vivian's / Boutique" (due righe, bianco con contorno blu come "Smile").
    La texture e' stirata in verticale (~1.5x) sul modello: le lettere si disegnano piu' larghe (xscale).
    Le due tessere "Vi" (stesso disegno, affiancate = "ViVi") NON si toccano: sono la stessa immagine ripetuta."""
    sp = dict(
        text="Vivian's\nBoutique", font='Fredoka', variant='Bold', size=60, box=(1, 0, 108, 30), xscale=1.8,
        leading=-0.2, fill=(255, 255, 255), strokes=[((255, 255, 255), 2), (_SMILE_BLUE, 1)],
        shadow=((115, 115, 115), (1, 1)),
        erase=[(0, 0, 107, 29)], erase_colors=[], erase_all=True, tol=40, edge=1, clear=[(0, 0, 107, 29)],
        # stagione "fushigi": il contorno dell'originale e' viola, non blu
        season_override={'08_fushigi': dict(strokes=[((255, 255, 255), 2), ((151, 32, 202), 1)])})
    sp.update(kw)
    return sp


SPEC[('atlas', 'shop_cloth00@128,0,256,31')] = _smile()
SPEC[('atlas', 'sh_b01_o03@0,0,128,31')] = _smile()
def _halogen_mall(**kw):
    """Halogen del centro commerciale (texture 256x256 'mall_07_a', ritaglio 28,90..132,132): testo su vuoto,
    due barre sotto che restano; LaMa ricostruisce lo sfondo (traforo bianco e vuoto)"""
    sp = _halogen(box=(7, 5, 98, 29), erase=[(6, 4, 99, 30), (56, 30, 74, 34)], rowfill=(52, 30, 80, 34), clear=None)
    sp.update(kw)
    return sp


_MALL_HALOGEN_FUSHIGI = dict(fill=((214, 200, 255), (176, 70, 190)), strokes=[((70, 20, 96), 1)],
                             shadow=((50, 10, 70), (1, 1)))
SPEC[(TEX, _MALL + 'Concourse.bcres@mall_07_a@28,90,132,132')] = _halogen_mall()
SPEC[(TEX, _MALL + 'Concourse_Tex_Night.bctex@mall_07_a@28,90,132,132')] = _halogen_mall()
SPEC[(TEX, _MALL + 'Concourse_Tex_Fushigi.bctex@mall_07_a@28,90,132,132')] = _halogen_mall(**_MALL_HALOGEN_FUSHIGI)
SPEC[(TEX, _MALL + 'ShopDef03.bcres@03_flower@0,192,256,256')] = _daisy()
SPEC[(TEX, _MALL + 'ShopDef02.bcres@02_cloth@128,96,256,127')] = _smile()
# targa laterale del centro commerciale (128x64): adesivo con "flower / daisy" + margherite -> "Daisy's / Flowers"
_FS_GOLD = ((255, 208, 112), (244, 170, 70))
_PETALS = [(247, 247, 198), (255, 247, 239), (255, 234, 183), (255, 246, 229), (246, 246, 195), (255, 246, 246),
           (247, 247, 197), (246, 246, 197), (255, 255, 255), (250, 240, 215)]
SPEC[(TEX, _MALL + 'ShopDef03SideBoard.bctex@03_flower_side')] = dict(
    text="Daisy's\nFlowers", font='Chewy', size=60, xscale='auto', xscale_min=0.6,
    lines_at=[dict(text="Daisy's", box=(4, 8, 115, 43), rot=-5),   # come "flower" originale: copre il bordo della margherita
              dict(text='Flowers', box=(42, 36, 124, 63), rot=-1)],
    fill=_FS_GOLD, strokes=[((130, 0, 0), 2)], shadow=None,
    erase=[(6, 2, 124, 62)], erase_colors=[], tol=36, edge=1,
    erase_except=[(206, 0, 16), (205, 0, 18), (204, 0, 14), (205, 0, 24), (206, 2, 19), (205, 0, 15), (196, 0, 9),
                  (208, 0, 0), (186, 0, 16), (191, 0, 0), (185, 0, 4)], except_tol=26,
    protect_colors=_PETALS, protect_tol=22,
    protect=[(14, 29, 32, 50), (35, 41, 48, 54), (80, 4, 90, 14), (97, 11, 113, 28)],
    flat_fill=[((84, 12, 104, 32), (206, 0, 16)), ((8, 20, 40, 31), (206, 0, 16)), ((5, 3, 30, 15), (206, 0, 16))])
# targa laterale della boutique (128x64): "ViVi" ciano + cappello + "Smile ★" -> "Vivian's" (ciano) / "Boutique" (bianco-blu);
# il cappello e la stella restano
SPEC[(TEX, _MALL + 'ShopDef02SideBoard.bctex@02_cloth_side')] = dict(
    text="Vivian's Boutique", font='Fredoka', variant='Bold', size=60, xscale='auto', xscale_min=0.6,
    lines_at=[dict(text="Vivian's", box=(3, 4, 88, 40), rot=-2, fill=((100, 245, 255), (8, 214, 245)),
                   strokes=[((255, 255, 255), 4), ((5, 141, 192), 2)], shadow=((115, 115, 115), (2, 2))),
              dict(text='Boutique', box=(24, 41, 98, 60), rot=0, fill=(255, 255, 255),
                   strokes=[((255, 255, 255), 3), (_SMILE_BLUE, 2)], shadow=((115, 115, 115), (1, 1)))],
    fill=(255, 255, 255), strokes=[], shadow=None,
    erase=[(2, 2, 76, 14), (2, 14, 89, 46), (2, 42, 97, 60)], erase_colors=[], erase_all=True, tol=40, edge=1,
    protect_colors=[(66, 198, 174), (66, 198, 173), (255, 191, 2)], protect_tol=24, protect_zone=(76, 0, 128, 46))
SPEC[('atlas', 'sh_flower_o00@0,0,256,64')] = _daisy()
SPEC[('atlas', 'sh_zakka_o00@0,0,128,64')] = _halogen()
SPEC[('atlas', 'shop_zakka01@100,204,224,256')] = _halogen(-4, -8)


ATLAS_DIR = os.path.join(ROOT, 'work', '3ds', 'romfs_x', 'model', 'map', 'object', 'season',
                         'map_field_object_tex.tarc_x')
PLANE_DIR = os.path.join(ROOT, 'work', '3ds', 'romfs_x', 'model', 'map', 'plane', 'map_plane_model.tarc_x')


def load(arc, f):
    if arc == 'atlas':
        # f = 'nome_texture@x0,y0,x1,y1[@file_stagione]': ritaglio di un atlante dei modelli della città
        name, crop, *rest = f.split('@')
        season = rest[0] if rest else '00_spring_day.bctex'
        d = open(os.path.join(ATLAS_DIR, season), 'rb').read()
        t = [x for x in cgfx.textures(d) if x[0] == name][0]
        box = tuple(int(v) for v in crop.split(','))
        return d, t, cgfx.decode(d, t).convert('RGBA').crop(box)
    if arc == 'png':
        # f = 'cartella_ui/file.png': immagine 2D della UI già estratta (work/img/ui); il risultato va in
        # work/img_it/_auto/<cartella>/<file> e lo installa build_images.py.
        # f = 'a.png+b.png': COMPOSIZIONE di più texture affiancate (es. fumetto = corpo 256 + capo 64):
        # la scheda lavora sull'insieme, poi png_parts() lo ridivide nelle texture originali
        # 'a.png^3': nel layout il pezzo sta 3 px PIÙ IN ALTO degli altri -> composto alzato di 3 (il testo resta dritto a schermo)
        parts = [(Image.open(os.path.join(ROOT, 'work', 'img', 'ui', p)).convert('RGBA'), dy) for p, dy in map(_png_part, f.split('+'))]
        img = Image.new('RGBA', (sum(p.width for p, _ in parts), max(p.height for p, _ in parts)), (0, 0, 0, 0))
        x = 0
        for p, dy in parts:
            img.alpha_composite(p, (x, 0), (0, dy, p.width, p.height)) if dy >= 0 else img.paste(p, (x, -dy)); x += p.width
        return None, None, img
    if arc == 'tex':
        # f = 'percorso/in/romfs_x/file@nome_texture[@x0,y0,x1,y1]': qualunque texture CGFX (anche ritaglio);
        # all'installazione va in TUTTE le copie identiche (stesso hash) presenti negli archivi
        path, name, *crop = f.split('@')
        d = open(os.path.join(ROOT, 'work', '3ds', 'romfs_x', path), 'rb').read()
        t = [x for x in cgfx.textures(d) if x[0] == name][0]
        img = cgfx.decode(d, t).convert('RGBA')
        if crop:
            img = img.crop(tuple(int(v) for v in crop[0].split(',')))
        return d, t, img
    if arc == 'plane':
        # f = 'modello.bcres@nome_texture': texture incorporata in un modello di stanza (map_plane_model)
        fname, name = f.split('@')[:2]
        d = open(os.path.join(PLANE_DIR, fname), 'rb').read()
        t = [x for x in cgfx.textures(d) if x[0] == name][0]
        return d, t, cgfx.decode(d, t).convert('RGBA')
    d = open(os.path.join(SRC, arc + '.tarc_x', f), 'rb').read()
    t = cgfx.textures(d)[0]
    return d, t, cgfx.decode(d, t).convert('RGBA')


_LAMA = None
ALPHA_CUT = 200     # pixel ricostruito opaco solo se il modello è sicuro (evita sagome che "debordano")


def lama_inpaint(img, mask):
    """inpainting con LaMa (tools/models/lama_fp32.onnx, onnxruntime, CPU).
    L'immagine va su sfondo magenta (così il modello ricostruisce anche la sagoma), ingrandita a 512 di
    lato; il risultato torna alla dimensione originale e si usa solo dentro la maschera. I pixel
    ricostruiti vicini al magenta diventano trasparenti."""
    global _LAMA
    import cv2, onnxruntime as ort
    if _LAMA is None:
        _LAMA = ort.InferenceSession(os.path.join(ROOT, 'tools', 'models', 'lama_fp32.onnx'),
                                     providers=['CPUExecutionProvider'])
    a = np.asarray(img).copy()
    H, W = mask.shape
    # colori: le zone trasparenti (fuori maschera) si riempiono coi colori vicini, così il modello
    # non vede mai colori "finti" che poi colerebbero nella ricostruzione
    transp = (a[..., 3] < 128) & ~mask
    rgb = a[..., :3].copy()
    if transp.any():
        rgb = cv2.inpaint(np.ascontiguousarray(rgb), (transp * 255).astype(np.uint8), 5, cv2.INPAINT_TELEA)
    s = 512 / max(W, H)
    w2, h2 = int(round(W * s)), int(round(H * s))
    mk = cv2.resize(mask.astype(np.uint8) * 255, (w2, h2), interpolation=cv2.INTER_NEAREST)
    mk = cv2.dilate(mk, np.ones((5, 5), np.uint8))
    m512 = np.zeros((512, 512), np.float32); m512[:h2, :w2] = (mk > 0)

    def run(img3):
        up = cv2.resize(img3.astype(np.float32), (w2, h2), interpolation=cv2.INTER_CUBIC)
        canvas = np.zeros((512, 512, 3), np.float32)
        canvas[:h2, :w2] = up
        canvas[h2:, :w2] = up[-1:, :, :]                          # bordo replicato sotto
        x = (canvas / 255.0).transpose(2, 0, 1)[None]
        out = _LAMA.run(None, {'image': x, 'mask': m512[None, None]})[0][0].transpose(1, 2, 0)
        if out.max() <= 1.5:
            out = out * 255.0
        return cv2.resize(out[:h2, :w2], (W, H), interpolation=cv2.INTER_AREA).clip(0, 255)

    res = run(rgb)
    # sagoma: il canale alfa ricostruito come immagine in scala di grigi, poi reso netto
    al3 = np.repeat(a[..., 3:4], 3, 2)
    alpha = np.where(run(al3).mean(2) > ALPHA_CUT, 255, 0).astype(np.uint8)
    a[mask, :3] = res[mask].astype(np.uint8)
    a[mask, 3] = alpha[mask]
    return Image.fromarray(a, 'RGBA')


def inpaint(img, mask, radius=3, smooth=0):
    if USE_LAMA:
        return lama_inpaint(img, mask)
    """ricostruisce lo sfondo sotto il testo con OpenCV (Telea), colore e trasparenza separati"""
    import cv2
    a = np.asarray(img).copy()
    m = (mask * 255).astype(np.uint8)
    rgb = cv2.inpaint(np.ascontiguousarray(a[..., :3]), m, radius, cv2.INPAINT_TELEA)
    alpha = cv2.inpaint(np.ascontiguousarray(a[..., 3]), m, radius, cv2.INPAINT_TELEA)
    if smooth:
        # sfondi sfumati (pergamena, pannelli): convoluzione normalizzata = media sfocata dei soli pixel
        # buoni (fuori dal testo), senza le strisciate dell'inpainting
        known = (~mask).astype(np.float32)
        src = a[..., :3].astype(np.float32) * known[..., None]
        num = cv2.GaussianBlur(src, (0, 0), smooth)
        den = cv2.GaussianBlur(known, (0, 0), smooth)[..., None]
        est = (num / np.maximum(den, 1e-3)).clip(0, 255).astype(np.uint8)
        rgb = np.where(mask[..., None], est, rgb)
    # trasparenza netta nella zona ricostruita: niente velature (gli "aloni")
    alpha = np.where(mask, np.where(alpha > 160, 255, 0), alpha).astype(np.uint8)
    return Image.fromarray(np.dstack([rgb, alpha]), 'RGBA')


def paint_panel(img, sp):
    """fondo ridisegnato (per pannelli semplici dove il testo copriva quasi tutto): sfumatura radiale
    dal colore centrale a quello del bordo, con leggera grana; solo dentro sp['panel'] (rettangolo)"""
    if not sp.get('panel'):
        return img
    x0, y0, x1, y1 = sp['panel']
    inner, outer = np.array(sp['panel_colors'][0], np.float32), np.array(sp['panel_colors'][1], np.float32)
    h, w = y1 - y0, x1 - x0
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) / np.sqrt(2)
    r = np.clip(r * 1.25, 0, 1) ** 1.6
    col = inner * (1 - r[..., None]) + outer * r[..., None]
    rng = np.random.default_rng(7)
    col += rng.normal(0, 4, col.shape).astype(np.float32)          # grana della carta
    a = np.asarray(img).copy().astype(np.float32)
    # raccordo morbido col fondo originale ai bordi del pannello (niente cuciture)
    f = sp.get('feather', 3)
    wgt = np.ones((h, w), np.float32)
    for i in range(f):
        k = (i + 1) / (f + 1)
        wgt[i, :] = np.minimum(wgt[i, :], k); wgt[h - 1 - i, :] = np.minimum(wgt[h - 1 - i, :], k)
        wgt[:, i] = np.minimum(wgt[:, i], k); wgt[:, w - 1 - i] = np.minimum(wgt[:, w - 1 - i], k)
    reg = a[y0:y1, x0:x1, :3]
    a[y0:y1, x0:x1, :3] = reg * (1 - wgt[..., None]) + col.clip(0, 255) * wgt[..., None]
    a[y0:y1, x0:x1, 3] = 255
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA')


def pattern_fill(img, orig, mask, sp):
    """motivi periodici (strisce, quadretti) dentro sp['pattern'] = (x0,y0,x1,y1): ogni pixel cancellato
    prende il colore dell'originale nello stesso punto del motivo, spostato di k periodi in orizzontale.
    Il periodo si stima per autocorrelazione sulle righe visibili."""
    if not sp.get('pattern'):
        return img
    x0, y0, x1, y1 = sp['pattern']
    o = np.asarray(orig).astype(np.int32)
    a = np.asarray(img).copy()
    best, per = None, sp.get('period')
    if not per:
        for p in range(3, (x1 - x0) // 2):
            diffs = []
            for y in range(y0, y1):
                for x in range(x0, x1 - p):
                    if not mask[y, x] and not mask[y, x + p] and o[y, x, 3] > 200 and o[y, x + p, 3] > 200:
                        diffs.append(np.abs(o[y, x, :3] - o[y, x + p, :3]).sum())
            if len(diffs) > 30:
                s = float(np.mean(diffs))
                if best is None or s < best:
                    best, per = s, p
    for y in range(y0, y1):
        for x in range(x0, x1):
            if not mask[y, x]:
                continue
            for k in list(range(1, 12)) + list(range(-1, -12, -1)):
                xs = x + k * per
                if x0 <= xs < x1 and not mask[y, xs] and o[y, xs, 3] > 0:
                    a[y, x] = o[y, xs]
                    break
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def surface_fit(img, orig, mask, sp):
    """superfici morbide (pergamena, pannelli): dentro sp['surface'] = (x0,y0,x1,y1) i pixel cancellati
    prendono il valore di un polinomio 2D (grado sp['deg']) adattato ai pixel visibili della stessa zona,
    più una grana con la stessa deviazione dell'originale. Niente chiazze, niente cuciture."""
    if not sp.get('surface'):
        return img
    x0, y0, x1, y1 = sp['surface']
    deg = sp.get('deg', 3)
    o = np.asarray(orig).astype(np.float64)
    a = np.asarray(img).copy().astype(np.float64)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    u, v = (xx - x0) / max(1, x1 - x0 - 1) * 2 - 1, (yy - y0) / max(1, y1 - y0 - 1) * 2 - 1
    terms = [u ** i * v ** j for i in range(deg + 1) for j in range(deg + 1 - i)]
    A = np.stack([t.ravel() for t in terms], 1)
    sub_m = mask[y0:y1, x0:x1].ravel()
    known = ~sub_m & (o[y0:y1, x0:x1, 3].ravel() > 250)
    rng = np.random.default_rng(11)
    noise = rng.normal(0, 1, sub_m.shape)            # grana monocromatica (uguale sui 3 canali)
    for c in range(3):
        col = o[y0:y1, x0:x1, c].ravel()
        coef, *_ = np.linalg.lstsq(A[known], col[known], rcond=None)
        fit = A @ coef
        lo, hi = np.percentile(col[known], 2), np.percentile(col[known], 98)
        fit = fit.clip(lo, hi)                        # niente estrapolazioni fuori dai colori reali
        sd = float(np.std(col[known] - fit[known])) * sp.get('grain', 0.6)
        val = fit + noise * sd
        ch = a[y0:y1, x0:x1, c].ravel()
        ch[sub_m] = val[sub_m]
        a[y0:y1, x0:x1, c] = ch.reshape(y1 - y0, x1 - x0)
    blk = a[y0:y1, x0:x1, 3]
    blk[mask[y0:y1, x0:x1]] = 255
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA')


def symmetry_fill(img, orig, mask, sp):
    """oggetti simmetrici (ciotole, piatti): sp['shape'] = (cx, cy, rx, ry) ellisse dell'oggetto.
    Dentro l'ellisse un pixel cancellato si copia dallo specchio orizzontale, poi verticale, poi
    centrale (il primo visibile); fuori dall'ellisse diventa trasparente. Mantiene la pixel art."""
    if not sp.get('shape'):
        return img
    cx, cy, rx, ry = sp['shape']
    o = np.asarray(orig)
    a = np.asarray(img).copy()
    H, W = mask.shape
    done = np.zeros_like(mask)
    for y in range(H):
        for x in range(W):
            if not mask[y, x]:
                continue
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 > 1.0:
                a[y, x] = (0, 0, 0, 0)
                done[y, x] = True
                continue
            for sx, sy in ((2 * cx - x, y), (x, 2 * cy - y), (2 * cx - x, 2 * cy - y)):
                sx, sy = int(round(sx)), int(round(sy))
                if 0 <= sx < W and 0 <= sy < H and not mask[sy, sx] and o[sy, sx, 3] > 0:
                    a[y, x] = o[sy, sx]
                    done[y, x] = True
                    break
    return Image.fromarray(a, 'RGBA')


def row_fill(img, orig, mask, sp):
    """fasce uniformi in orizzontale (pannelli con righe di colore): dentro sp['rowfill'] = (x0,y0,x1,y1)
    ogni pixel cancellato prende la media dei pixel NON cancellati della stessa riga nel rettangolo"""
    if not sp.get('rowfill'):
        return img
    x0, y0, x1, y1 = sp['rowfill']
    o = np.asarray(orig).astype(np.float32)
    a = np.asarray(img).copy()
    for y in range(y0, y1):
        good = ~mask[y, x0:x1] & (o[y, x0:x1, 3] > 200)
        if sp.get('rowfill_min_sum'):        # solo pixel chiari (fondo vero, non bordi del vecchio testo)
            good &= o[y, x0:x1, :3].sum(1) > sp['rowfill_min_sum']
        if good.sum() == 0:
            continue
        col = np.median(o[y, x0:x1][good], axis=0)
        row = a[y, x0:x1]
        row[mask[y, x0:x1]] = col.astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


def paint_ring(img, sp):
    """elemento decorativo ridisegnato: anello (es. sole a pennellata) sp['ring'] =
    dict(c=(cx,cy), ro=raggio esterno, ri=raggio interno, color=(r,g,b), color2=(r,g,b) opzionale)"""
    if not sp.get('ring'):
        return img
    r = sp['ring']
    W, H = img.size
    Z = 8
    yy, xx = np.mgrid[0:H * Z, 0:W * Z] / Z
    d = np.hypot(xx - r['c'][0], yy - r['c'][1])
    rng = np.random.default_rng(5)
    ang = np.arctan2(yy - r['c'][1], xx - r['c'][0])
    wob = 0.8 * np.sin(ang * 3 + 1.3) + 0.5 * np.sin(ang * 7)            # bordo irregolare, da pennellata
    inside = (d < r['ro'] + wob) & (d > r['ri'] - wob * 0.6)
    a = Image.fromarray((inside * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    c1 = np.array(r['color'], np.float32)
    c2 = np.array(r.get('color2', r['color']), np.float32)
    t = np.clip((np.arange(H) - (r['c'][1] - r['ro'])) / (2 * r['ro']), 0, 1)[:, None, None]
    col = (c1 * (1 - t) + c2 * t).repeat(W, 1).astype(np.uint8)
    layer = Image.fromarray(np.dstack([col, np.asarray(a)]), 'RGBA')
    return Image.alpha_composite(img, layer)


def apply_clear(img, mask, sp):
    """zone (rettangoli) dove sotto il testo c'era solo vuoto: i pixel cancellati diventano trasparenti"""
    if not sp.get('clear'):
        return img
    a = np.asarray(img).copy()
    for x0, y0, x1, y1 in sp['clear']:
        sub = mask[y0:y1, x0:x1]
        a[y0:y1, x0:x1, 3][sub] = 0
    return Image.fromarray(a, 'RGBA')


def text_mask(img, sp):
    a = np.asarray(img.convert('RGB'), dtype=np.int32)
    m = np.zeros(a.shape[:2], bool)
    region = np.zeros_like(m)
    for x0, y0, x1, y1 in sp['erase']:
        region[y0:y1, x0:x1] = True
    for c in sp['erase_colors']:
        m |= (np.abs(a - np.array(c)).sum(2) < sp['tol'])
    if sp.get('erase_all'):                 # fondo semplice (fasce, pannelli): si cancella tutta la zona
        m |= True
    if sp.get('erase_except'):              # scritte multicolore su fondo semplice: tutto ciò che NON è fondo
        bg = np.zeros(m.shape, bool)
        for c in sp['erase_except']:
            bg |= np.abs(a - np.array(c)).sum(2) < sp.get('except_tol', 60)
        m |= ~bg
    if sp.get('erase2'):                    # elementi grafici da togliere in una zona (es. spatole)
        e2 = sp['erase2']
        zx0, zy0, zx1, zy1 = e2['zone']
        z2 = np.zeros(m.shape, bool)
        for c in e2['colors']:
            z2 |= np.abs(a - np.array(c)).sum(2) < e2.get('tol', 60)
        zone = np.zeros(m.shape, bool); zone[zy0:zy1, zx0:zx1] = True
        m |= z2 & zone & (np.asarray(img)[..., 3] > 0)
    # i pixel già trasparenti hanno colori "a caso": non fanno parte del testo
    region &= np.asarray(img)[..., 3] > 0
    m &= region
    # alone: contorno delle lettere originali (es. bordo bianco) entro 'grow' px dalle lettere
    if sp.get('halo'):
        g = sp.get('grow', 3)
        near = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * g + 1))) > 0
        h = np.zeros_like(m)
        for c in sp['halo']:
            h |= (np.abs(a - np.array(c)).sum(2) < sp.get('halo_tol', 90))
        m |= near & h & region
    # allarga per prendere l'antialias del contorno, compresi i pixel semitrasparenti vicini alle lettere
    grow = sp.get('edge', 2)
    mi = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * grow + 1))
    m2 = np.asarray(mi) > 0
    alpha = np.asarray(img)[..., 3]
    soft = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * grow + 3))) > 0
    m2 |= soft & (alpha < 250) & (alpha > 0) & region
    return m2


def _draw_word(sp, sz):
    """disegna la parola lettera per lettera su una tela ampia (niente tagli) e restituisce
    (layer RGBA, bbox inchiostro). Per lettera: scala (sp['letter_scale']) e spostamento verticale
    (sp['letter_dy'], px a 1x, positivo = in giù) per l'effetto "magico/goofy"."""
    text = sp['text']
    scales = sp.get('letter_scale') or [1.0] * len(text)
    dys = sp.get('letter_dy') or [0] * len(text)
    path = os.path.join(FONTS, sp['font'] + '.ttf')
    fonts = [ImageFont.truetype(path, max(4, int(round(sz * S * k)))) for k in scales]
    if sp.get('variant'):                   # font variabili (Fredoka, Baloo2...): es. 'Bold', 'SemiBold'
        for f in fonts:
            try:
                f.set_variation_by_name(sp['variant'])
            except Exception:
                pass
    track = sp.get('tracking', 0) * S
    pad = max([w for _, w in sp['strokes']] + [0]) * S
    # posizioni: linea di base comune, avanzamento della singola lettera (scalata)
    xs, x = [], 0
    for ch, f in zip(text, fonts):
        xs.append(x)
        x += f.getlength(ch) + track
    PADC = 64 * S
    cw, chh = int(x + 2 * PADC), int(sz * S * max(scales) * 2 + 2 * PADC)
    base_y = PADC + sz * S * max(scales) * 1.2
    layer = Image.new('RGBA', (cw, chh), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pos = [(PADC + xi, base_y + dy * S) for xi, dy in zip(xs, dys)]
    if sp.get('shadow'):
        col, (sx, sy) = sp['shadow']
        for ch, f, (px, py) in zip(text, fonts, pos):
            d.text((px + sx * S, py + sy * S), ch, font=f, anchor='ls', fill=col + (200,),
                   stroke_width=pad, stroke_fill=col + (200,))
    for col, wdt in sorted(sp['strokes'], key=lambda s: -s[1]):          # dal contorno più largo (esterno)
        for ch, f, (px, py) in zip(text, fonts, pos):
            d.text((px, py), ch, font=f, anchor='ls', fill=col, stroke_width=wdt * S, stroke_fill=col)
    fm = Image.new('L', layer.size, 0)
    dm = ImageDraw.Draw(fm)
    for ch, f, (px, py) in zip(text, fonts, pos):
        dm.text((px, py), ch, font=f, anchor='ls', fill=255)
    fb = fm.getbbox() or (0, 0, 1, 1)
    if sp.get('letter_fill'):               # un colore per lettera (scritte multicolore come l'originale)
        cols = sp['letter_fill']
        ci = 0
        for ch, f, (px, py) in zip(text, fonts, pos):
            if ch == ' ':
                continue
            lm = Image.new('L', layer.size, 0)
            ImageDraw.Draw(lm).text((px, py), ch, font=f, anchor='ls', fill=255)
            layer.paste(Image.new('RGBA', layer.size, tuple(cols[ci % len(cols)]) + (255,)), (0, 0), lm)
            ci += 1
        return layer, layer.getbbox()
    fill = sp['fill']
    if isinstance(fill[0], tuple):                       # sfumatura verticale sull'altezza delle lettere
        top, bot = np.array(fill[0], np.float32), np.array(fill[1], np.float32)
        t = np.clip((np.arange(layer.size[1]) - fb[1]) / max(1, fb[3] - fb[1]), 0, 1)[:, None]
        grad = (top * (1 - t) + bot * t).astype(np.uint8)
        fimg = Image.fromarray(np.repeat(grad[:, None, :], layer.size[0], 1), 'RGB').convert('RGBA')
    else:
        fimg = Image.new('RGBA', layer.size, tuple(fill) + (255,))
    layer.paste(fimg, (0, 0), fm)
    return layer, layer.getbbox()


def render_text(sp, size):
    """testo a strati, adattato al box dell'originale, su tela ampia; poi compressione orizzontale,
    rotazione, rientro nei bordi (niente lettere tagliate) e riduzione alla dimensione della texture"""
    W, H = size
    if sp.get('letters_box'):
        # ogni lettera riempie il riquadro della lettera originale: (lettera, x0, y0, x1, y1, rotazione)
        layer = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
        for ch, bx0, by0, bx1, by1, rot in sp['letters_box']:
            w_, b_ = _draw_word(dict(sp, text=ch, letter_scale=None, letter_dy=None), 40)
            g = w_.crop(b_)
            if rot:
                g = g.rotate(rot, resample=Image.BICUBIC, expand=True)
                g = g.crop(g.getbbox())
            k_ = min((bx1 - bx0) * S / g.size[0], (by1 - by0) * S / g.size[1])
            g = g.resize((max(1, int(g.size[0] * k_)), max(1, int(g.size[1] * k_))), Image.LANCZOS)
            cx, cy = (bx0 + bx1) / 2 * S, (by0 + by1) / 2 * S
            layer.alpha_composite(g, (int(cx - g.size[0] / 2), int(cy - g.size[1] / 2)))
        return layer.resize((W, H), Image.LANCZOS)
    if sp.get('lines_at'):
        # righe disposte liberamente dentro la sagoma, ognuna col suo riquadro/scala/saltellio
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        for ln in sp['lines_at']:
            sub = dict(sp, lines_at=None, **ln)
            layer.alpha_composite(render_text(sub, size))
        return layer
    if sp.get('letters_at'):
        # lettere in posizioni fisse (es. una per cubo): (lettera, cx, cy, corpo, rotazione)
        layer = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
        for ch, cx, cy, size_, rot in sp['letters_at']:
            w_, b_ = _draw_word(dict(sp, text=ch, letter_scale=None, letter_dy=None), size_)
            g = w_.crop(b_)
            if rot:
                g = g.rotate(rot, resample=Image.BICUBIC, expand=True)
            layer.alpha_composite(g, (int(cx * S - g.size[0] / 2), int(cy * S - g.size[1] / 2)))
        return layer.resize((W, H), Image.LANCZOS)
    x0, y0, x1, y1 = sp['box']
    k = sp.get('xscale', 1.0)
    sz = sp['size']
    if sp.get('xscale') == 'auto':
        # stessa altezza del testo originale: se la parola è più "bassa e larga" del box, la si condensa
        w_, b_ = _draw_word(dict(sp, text=sp['text'].split('\n')[0]), 40)
        nl = sp['text'].count('\n') + 1
        ratio_word = (b_[2] - b_[0]) / max(1, (b_[3] - b_[1]) * nl)
        ratio_box = (x1 - x0) / max(1, (y1 - y0))
        k = max(sp.get('xscale_min', 0.7), min(1.0, ratio_box / ratio_word))
    lines = sp['text'].split('\n')

    def draw(sz):
        """una o più righe, centrate, con interlinea sp['leading'] (frazione del corpo)"""
        parts = []
        for li, t in enumerate(lines):
            sub = dict(sp, text=t)
            if len(lines) > 1:                     # scala/saltellio per lettera solo sulla prima riga
                if li:
                    sub.pop('letter_scale', None); sub.pop('letter_dy', None)
            w_, b_ = _draw_word(sub, sz)
            parts.append(w_.crop(b_))
        if len(parts) == 1:
            return parts[0]
        gap = int(sz * S * sp.get('leading', -0.05))
        Wt = max(p.size[0] for p in parts)
        Ht = sum(p.size[1] for p in parts) + gap * (len(parts) - 1)
        out = Image.new('RGBA', (Wt, max(1, Ht)), (0, 0, 0, 0))
        y = 0
        for p in parts:
            out.alpha_composite(p, ((Wt - p.size[0]) // 2, max(0, y)))
            y += p.size[1] + gap
        return out

    while True:                                          # corpo massimo che entra nel box
        word = draw(sz)
        tw, th = word.size[0] * k, word.size[1]
        if tw <= (x1 - x0) * S and th <= (y1 - y0) * S or sz <= 8:
            break
        sz -= 1
    if k != 1.0:
        word = word.resize((max(1, int(round(word.size[0] * k))), word.size[1]), Image.LANCZOS)
    if sp.get('rot'):
        word = word.rotate(sp['rot'], resample=Image.BICUBIC, expand=True)
        word = word.crop(word.getbbox())
    ww, wh = word.size
    # posizione nel box: centrata, o appoggiata in basso a sinistra (scritte che toccano l'angolo)
    if sp.get('anchor') == 'bottom':
        px, py = x0 * S, y1 * S - wh
    else:
        px, py = x0 * S + ((x1 - x0) * S - ww) // 2, y0 * S + ((y1 - y0) * S - wh) // 2
    m_ = S                                               # mai fuori dall'immagine (1 px di margine)
    px = min(max(px, m_), W * S - m_ - ww)
    py = min(max(py, m_), H * S - m_ - wh)
    layer = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
    layer.alpha_composite(word, (int(px), int(py)))
    if sp.get('fill_holes'):
        # spazi chiusi dentro la scritta (occhielli di e, p, a...) riempiti col colore del contorno:
        # la scritta diventa un "adesivo" pieno come gli originali (niente buchi sullo sfondo)
        import cv2
        al = (np.asarray(layer)[..., 3] > 40).astype(np.uint8)
        flood = al.copy() * 255
        h_, w_ = flood.shape
        ff = np.zeros((h_ + 2, w_ + 2), np.uint8)
        cv2.floodFill(flood, ff, (0, 0), 128)
        holes = flood == 0
        a = np.asarray(layer).copy()
        a[holes] = tuple(sp['fill_holes']) + (255,)
        layer = Image.fromarray(a, 'RGBA')
    return layer.resize((W, H), Image.LANCZOS)


def make(arc, f):
    # per gli atlanti la stessa scheda vale per tutte le varianti di stagione (suffisso @file)
    sp = SPEC.get((arc, f)) or SPEC[(arc, '@'.join(f.split('@')[:2]))]      # 'tex': chiave esatta
    for k_, ov in (sp.get('season_override') or {}).items():                # varianti di stagione (es. fushigi)
        if k_ in f:
            sp = dict(sp, **ov)
    d, t, img = load(arc, f)
    m = text_mask(img, sp)
    for x0, y0, x1, y1 in sp.get('protect', []):          # zone da non toccare mai
        m[y0:y1, x0:x1] = False
    if sp.get('protect_lines'):                            # segmenti (cornici diagonali): (p0, p1, mezzo spessore)
        lm = Image.new('L', (m.shape[1], m.shape[0]), 0)
        for p0, p1, hw in sp['protect_lines']:
            ImageDraw.Draw(lm).line([tuple(p0), tuple(p1)], fill=255, width=max(1, int(round(hw * 2))))
        m &= ~(np.asarray(lm) > 0)
    if sp.get('protect_colors'):                           # oggetti da non toccare, per colore (es. mirtilli)
        a = np.asarray(img).astype(np.int32)
        keep = np.zeros(m.shape, bool)
        for c in sp['protect_colors']:
            keep |= np.abs(a[..., :3] - np.array(c)).sum(2) < sp.get('protect_tol', 60)
        if sp.get('protect_zone'):                         # protezione per colore solo in questa zona
            zx0, zy0, zx1, zy1 = sp['protect_zone']
            zone = np.zeros(m.shape, bool); zone[zy0:zy1, zx0:zx1] = True
            keep &= zone
        keep = np.asarray(Image.fromarray((keep * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))) > 0
        m &= ~keep
    else:
        keep = np.zeros(m.shape, bool)
    if sp.get('box') == 'auto' and not (sp.get('letters_at') or sp.get('letters_box') or sp.get('lines_at')):
        # stesso ingombro del testo originale: bbox della maschera, con 1 px di aria
        ys, xs = np.where(m)
        sp = dict(sp, box=(max(0, int(xs.min()) - 1), max(0, int(ys.min()) - 1),
                           min(img.size[0], int(xs.max()) + 2), min(img.size[1], int(ys.max()) + 2)))
    if sp.get('ui') and sp.get('text'):
        text = render_ui(sp, img.size)                 # font UI (ui_font) nei colori dell'originale
    else:
        text = render_text(sp, img.size) if sp.get('text') else Image.new('RGBA', img.size, (0, 0, 0, 0))
    if sp.get('star'):
        text = Image.alpha_composite(text, draw_star(img.size, sp['star']))
    # "clear" vale solo dove il nuovo testo non copre: sotto le lettere lo sfondo resta ricostruito
    cover = np.asarray(text.split()[3].filter(ImageFilter.MaxFilter(3))) > 0
    # gli oggetti protetti non fanno da "sorgente" per la ricostruzione: si riempie anche sotto di loro
    # e poi si rimettono gli originali sopra
    base = inpaint(img, m | keep, smooth=sp.get('smooth', 0))
    if keep.any():
        ba, oa = np.asarray(base).copy(), np.asarray(img)
        ba[keep] = oa[keep]
        base = Image.fromarray(ba, 'RGBA')
    if sp.get('veto_colors'):
        # resti del vecchio testo (colore delle lettere originali) rimasti visibili fuori dalla nuova
        # scritta: secondo passaggio di LaMa su quei pixel, che li ricostruisce dal contesto
        ba = np.asarray(base)
        rgbb = ba[..., :3].astype(np.int32)
        veto = np.zeros(m.shape, bool)
        for c in sp['veto_colors']:
            veto |= np.abs(rgbb - np.array(c)).sum(2) < sp.get('veto_tol', 80)
        veto &= ba[..., 3] > 0
        if sp.get('veto_zone'):
            zx0, zy0, zx1, zy1 = sp['veto_zone']
            zone = np.zeros(m.shape, bool); zone[zy0:zy1, zx0:zx1] = True
            veto &= zone
        # limiti esatti: escluso solo il testo vero e solo i pixel col colore protetto (niente margini)
        text_strict = np.asarray(text.split()[3]) > 200      # testo davvero opaco (non l'antialias)
        keep_core = np.zeros(m.shape, bool)
        for c in sp.get('protect_colors', []):
            keep_core |= np.abs(rgbb - np.array(c)).sum(2) < sp.get('protect_tol', 60)
        veto &= ~text_strict & ~keep_core
        veto = np.asarray(Image.fromarray((veto * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))) > 0
        veto &= ~keep_core & ~text_strict
        if veto.any():
            base = lama_inpaint(base, veto)
            m = m | veto
            # se è ancora del colore delle vecchie lettere, era la loro sagoma: vuoto
            ba = np.asarray(base).copy()
            still = np.zeros(m.shape, bool)
            for c in sp['veto_colors']:
                still |= np.abs(ba[..., :3].astype(np.int32) - np.array(c)).sum(2) < sp.get('veto_tol', 80)
            if not sp.get('veto_keep_alpha'):
                ba[still & veto, 3] = 0
            base = Image.fromarray(ba, 'RGBA')
    if sp.get('repass'):
        # secondo passaggio LaMa su una zona (es. veli chiari residui), contesto = risultato del primo
        ba = np.asarray(base)
        rz = np.zeros(m.shape, bool)
        x0r, y0r, x1r, y1r = sp['repass']['zone']
        rz[y0r:y1r, x0r:x1r] = True
        light = ba[..., :3].astype(np.int32).sum(2) > sp['repass'].get('min_sum', 560)
        # anche pixel originali fuori maschera (es. contorno bianco del vecchio testo sopra un oggetto)
        rz &= light & (ba[..., 3] > 0) & ~(np.asarray(text.split()[3]) > 200)
        if rz.any():
            rz = np.asarray(Image.fromarray((rz * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))) > 0
            base = lama_inpaint(base, rz)
            m = m | rz
    base = pattern_fill(base, img, m, sp)
    base = row_fill(base, img, m, sp)
    base = paint_ring(base, sp)
    base = surface_fit(base, img, m, sp)
    base = symmetry_fill(base, img, m, sp)
    for (fx0, fy0, fx1, fy1), fcol in sp.get('flat_fill', []):          # zone dove LaMa "continua" un oggetto vicino
        ba = np.asarray(base).copy()
        sub = ba[fy0:fy1, fx0:fx1]
        sel = m[fy0:fy1, fx0:fx1] & (sub[..., 3] > 0)                  # solo il colore: la sagoma non cambia
        sub[sel, :3] = tuple(fcol)
        base = Image.fromarray(ba, 'RGBA')
    base = apply_clear(base, m & ~(np.asarray(text.split()[3]) > 200), sp)   # copertura = testo opaco
    base = paint_panel(base, sp)
    out = Image.alpha_composite(base, text)
    make.last_text = text                  # strato della sola scritta (export PSD a livelli)
    return img, out, base, m


def render_ui(sp, size):
    """testo col font UI (ui_font: Grandstander pixel, contorno rotondo sfumato) centrato in sp['box'];
    sp: fill, outline (None = senza contorno), ow, px (massimo), soft, spacing, leading"""
    import ui_font
    if sp.get('texts'):                    # più scritte separate nella stessa immagine: [(testo, box), ...]
        lay = Image.new('RGBA', size, (0, 0, 0, 0))
        for t, b in sp['texts']:
            lay.alpha_composite(render_ui(dict(sp, text=t, box=b, texts=None), size))
        return lay
    x0, y0, x1, y1 = sp['box']
    kw = dict(outline=tuple(sp['outline']) if sp.get('outline') else (0, 0, 0),
              ow=sp.get('ow', 2.5) if sp.get('outline') else 0, soft=sp.get('soft', 1.5),
              spacing=sp.get('spacing', 1), leading=sp.get('leading', -2), weight=sp.get('weight'))
    im = ui_font.fit(sp['text'], tuple(sp['fill']), x1 - x0, y1 - y0, px_max=sp.get('px', 22),
                     px_min=sp.get('px_min', 8), **kw)
    lay = Image.new('RGBA', size, (0, 0, 0, 0))
    ax = {'left': x0, 'right': x1 - im.width}.get(sp.get('halign'), (x0 + x1 - im.width) // 2)
    lay.alpha_composite(im, (int(ax), int((y0 + y1 - im.height) // 2 + sp.get('dy', 0))))
    return lay


def draw_star(size, st, ss=8):
    """stella a n punte (simmetrica: va bene anche su texture specchiate), disegnata in supersampling.
    st = dict(c=(cx, cy), ro, ri, n=4, rot=0, fill, outline=None, ow=0)"""
    import math
    W, H = size[0] * ss, size[1] * ss
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay)
    cx, cy = st['c'][0] * ss, st['c'][1] * ss
    n = st.get('n', 4)

    def poly(ro, ri):
        pts = []
        for k in range(2 * n):
            r = ro if k % 2 == 0 else ri
            a = math.radians(st.get('rot', 0)) - math.pi / 2 + k * math.pi / n
            pts.append((cx + r * ss * math.cos(a), cy + r * ss * math.sin(a)))
        return pts
    if st.get('outline'):
        ow = st.get('ow', 1.5)
        dr.polygon(poly(st['ro'] + ow * 1.6, st['ri'] + ow), fill=tuple(st['outline']) + (255,))
    dr.polygon(poly(st['ro'], st['ri']), fill=tuple(st['fill']) + (255,))
    if st.get('core'):                       # punto luminoso al centro
        r = st['core'][0] * ss
        dr.ellipse((cx - r, cy - r, cx + r, cy + r), fill=tuple(st['core'][1]) + (255,))
    return lay.resize(size, Image.LANCZOS)


def main(preview):
    rows = []
    for (arc, f) in SPEC:
        orig, out, base, m = make(arc, f)
        if preview:
            mimg = orig.copy()
            ov = Image.new('RGBA', orig.size, (255, 0, 255, 255))
            mimg.paste(ov, (0, 0), Image.fromarray((m * 200).astype(np.uint8)))
            rows.append((orig, mimg, base, out))
        else:
            os.makedirs(os.path.join(OUT, arc), exist_ok=True)
            out.save(os.path.join(OUT, arc, f.replace('.bctex', '.png')))
    if preview:
        # colonne: originale | maschera (magenta) | sfondo ricostruito | italiano
        Z = 2
        W, H = rows[0][0].size
        sheet = Image.new('RGBA', ((W * Z + 8) * 4, (H * Z + 6) * len(rows)), (110, 110, 110, 255))
        for i, imgs in enumerate(rows):
            for j, im in enumerate(imgs):
                sheet.alpha_composite(im.resize((W * Z, H * Z), Image.NEAREST), (j * (W * Z + 8), i * (H * Z + 6)))
        os.makedirs(OUT, exist_ok=True)
        sheet.save(os.path.join(OUT, '_anteprima.png'))
        print('anteprima ->', os.path.join(OUT, '_anteprima.png'))


SEASONS = sorted(f for f in os.listdir(ATLAS_DIR) if f.endswith('.bctex')) if os.path.isdir(ATLAS_DIR) else []
CACHE = os.path.join(OUT, '_cache.json')
import paths
MOD = os.path.join(paths.MOD, 'romfs')
ORIG_ROMFS = os.path.join(ROOT, 'work', '3ds', 'romfs')
TARC = {'shop_kanban_tex': 'model/map/shoppingmall/shop_kanban_tex.tarc',
        'shop_kanban_season_tex': 'model/map/shoppingmall/shop_kanban_season_tex.tarc',
        'atlas': 'model/map/object/season/map_field_object_tex.tarc',
        'plane': 'model/map/plane/map_plane_model.tarc'}


def _png_part(p):
    """'cartella/file.png^3' -> ('cartella/file.png', 3): pezzo di una composizione spostato in alto di 3 px"""
    p, _, dy = p.partition('^')
    return p, int(dy or 0)


def _png_path(arc, f):
    if arc in ('tex', 'png'):
        # con la cartella nel nome: la stessa texture in archivi diversi (es. mall_map_bag_01 in menu_shop_mall,
        # _comment, _edit, _gcoin) ha originali diversi e prima finiva tutta nello stesso file
        f = '+'.join(p.replace('/', '__').replace('^', '_up') for p in f.split('+'))
    safe = f.replace('@', '_').replace(',', '-').replace('.bctex', '').replace('\\', '_')
    return os.path.join(OUT, arc, safe + '.png')


_CODE_HASH = __import__('hashlib').sha1(open(__file__, 'rb').read()).hexdigest()


def _spec_hash(sp):
    import hashlib, json
    font = os.path.join(FONTS, sp.get('font', '') + '.ttf')
    blob = json.dumps(sp, sort_keys=True, default=str) + str(os.path.getsize(font) if os.path.exists(font) else 0)
    # anche il codice che disegna: senza, una modifica a make_signs.py lasciava in cache immagini fatte col codice vecchio
    # (una build da zero dava risultati diversi da quella incrementale)
    blob += _CODE_HASH
    if sp.get('ui'):                       # le schede col font UI cambiano anche se cambia ui_font.py
        uf = os.path.join(os.path.dirname(__file__), 'ui_font.py')
        blob += hashlib.sha1(open(uf, 'rb').read()).hexdigest()
    return hashlib.sha1(blob.encode('utf-8')).hexdigest()[:16]


def _png_install(v, out):
    """scrive l'immagine 2D in work/img_it/_auto (composizioni "a+b" ridivise nelle texture originali)"""
    x = 0
    for part, dy in map(_png_part, v.split('+')):
        src = Image.open(os.path.join(ROOT, 'work', 'img', 'ui', part)).convert('RGBA')
        w = src.size
        dst = os.path.join(ROOT, 'work', 'img_it', '_auto', part.replace('/', os.sep))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        piece = out.crop((x, -dy, x + w[0], w[1] - dy))
        if dy > 0:      # righe sopra il composto: restano quelle originali (tagliate nella composizione)
            piece.paste(src.crop((0, 0, w[0], dy)), (0, 0))
        elif dy < 0:
            piece.paste(src.crop((0, w[1] + dy, w[0], w[1])), (0, w[1] + dy))
        piece.save(dst)
        x += w[0]


def render(force=False, only=None):
    """genera i PNG finali (solo per le schede cambiate): insegne normali + ritagli dell'atlante per stagione"""
    import json
    cache = json.load(open(CACHE, encoding='utf-8')) if os.path.exists(CACHE) else {}
    todo = []
    for (arc, f), sp in SPEC.items():
        if only and not only(arc, f):
            continue
        variants = [f + '@' + s for s in SEASONS] if arc == 'atlas' else [f]
        for v in variants:
            todo.append((arc, v, _spec_hash(sp)))
    n = 0
    for arc, v, h in todo:
        p = _png_path(arc, v)
        if not force and cache.get(f'{arc}|{v}') == h and os.path.exists(p):
            if arc == 'png':                      # le copie in _auto vanno sempre rimesse (gen_labels svuota _auto)
                _png_install(v, Image.open(p).convert('RGBA'))
            continue
        _, out, _, _ = make(arc, v)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        out.save(p)
        if arc == 'png':                                  # immagini 2D: le installa build_images.py
            _png_install(v, out)
        cache[f'{arc}|{v}'] = h
        n += 1
        json.dump(cache, open(CACHE, 'w', encoding='utf-8'), indent=0)
    print(f'insegne: {n} rigenerate, {len(todo) - n} invariate')


def install():
    """rimette i PNG nelle texture CGFX (stesso formato/dimensione) e ricostruisce i tarc nella mod"""
    sys.path.insert(0, os.path.dirname(__file__))
    import tbaf
    repl = {}
    for (arc, f), sp in SPEC.items():
        if arc in ('atlas', 'tex', 'png'):
            continue
        d, t, _ = load(arc, f)
        key = f.split('@')[0] if arc == 'plane' else f      # più texture dello stesso modello: si accumulano
        if key in repl.get(arc, {}):
            d = repl[arc][key]
            t = [x for x in cgfx.textures(d) if x[0] == t[0]][0]
        img = Image.open(_png_path(arc, f)).convert('RGBA')
        raw = cgfx.encode(img, d, t)
        repl.setdefault(arc, {})[key] = d[:t[4]] + raw + d[t[4] + t[5]:]
    # atlante: per ogni stagione si decodifica la texture intera, si incollano i ritagli e si ricodifica
    atlas = [(f.split('@')[0], tuple(int(v) for v in f.split('@')[1].split(','))) for (a, f) in SPEC if a == 'atlas']
    for season in SEASONS:
        d = open(os.path.join(ATLAS_DIR, season), 'rb').read()
        data = d
        for name in sorted(set(n for n, _ in atlas)):
            t = [x for x in cgfx.textures(data) if x[0] == name][0]
            full = cgfx.decode(data, t).convert('RGBA')
            for n_, box in atlas:
                if n_ == name:
                    full.paste(Image.open(_png_path('atlas', f'{name}@{",".join(map(str, box))}@{season}'))
                               .convert('RGBA'), box[:2])
            raw = cgfx.encode(full, data, t)
            data = data[:t[4]] + raw + data[t[4] + t[5]:]
        repl.setdefault('atlas', {})[season] = data
    # da qui gli archivi sono indicizzati per percorso del tarc (così 'tex' può aggiungersi agli stessi)
    by_tarc = {TARC[arc]: files for arc, files in repl.items()}
    install_tex(by_tarc)
    for rel, files in by_tarc.items():
        out = os.path.join(MOD, rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        tbaf.rebuild(os.path.join(ORIG_ROMFS, rel), files, out)
        chk = {e['name']: tbaf.decompress(e['data']) if e['comp'] else e['data']
               for e in tbaf.parse(open(out, 'rb').read())}
        assert all(chk[k] == v for k, v in files.items()), rel
        print(f'{rel}: {len(files)} file sostituiti')


TEX_SCAN = ('model', 'field_common.tarc_x', 'battle_common.tarc_x')     # dove cercare le copie


def install_tex(by_tarc):
    """schede 'tex': si ricompone la texture (ritagli incollati sull'originale), poi la si scrive in ogni
    copia identica (stesso hash dei dati) di tutti gli archivi, anche dentro file già modificati"""
    import hashlib
    X = os.path.join(ROOT, 'work', '3ds', 'romfs_x')
    groups = {}
    for (arc, f), sp in SPEC.items():
        if arc == 'tex':
            path, name, *crop = f.split('@')
            groups.setdefault((path, name), []).append((f, crop[0] if crop else None))
    if not groups:
        return
    new_raw = {}                                         # (nome, hash originale) -> dati nuovi
    for (path, name), parts in groups.items():
        d = open(os.path.join(X, path), 'rb').read()
        t = [x for x in cgfx.textures(d) if x[0] == name][0]
        full = cgfx.decode(d, t).convert('RGBA')
        for f, crop in parts:
            png = Image.open(_png_path('tex', f)).convert('RGBA')
            full.paste(png, tuple(int(v) for v in crop.split(','))[:2] if crop else (0, 0))
        h = hashlib.sha1(d[t[4]:t[4] + t[5]]).hexdigest()
        new_raw[(name, h)] = (cgfx.encode(full, d, t), t[1], t[2], t[3])
    names = {n.encode() for n, _ in new_raw}
    n_copies = 0
    for top in TEX_SCAN:
        for r, _, fs in os.walk(os.path.join(X, top)):
            if not r.endswith('.tarc_x'):
                continue
            rel_tarc = os.path.relpath(r, X)[:-2].replace(os.sep, '/')
            for fn in fs:
                p = os.path.join(r, fn)
                d = by_tarc.get(rel_tarc, {}).get(fn) or open(p, 'rb').read()
                if not any(n in d for n in names):
                    continue
                try:
                    ts = cgfx.textures(d)
                except Exception:
                    continue
                orig = open(p, 'rb').read()               # l'hash si confronta sull'originale
                changed = False
                for t in ts:
                    ot = [x for x in cgfx.textures(orig) if x[0] == t[0] and x[4] == t[4]]
                    if not ot:
                        continue
                    h = hashlib.sha1(orig[ot[0][4]:ot[0][4] + ot[0][5]]).hexdigest()
                    nr = new_raw.get((t[0], h))
                    if nr and (t[1], t[2], t[3]) == nr[1:] and len(nr[0]) == t[5]:
                        d = d[:t[4]] + nr[0] + d[t[4] + t[5]:]
                        changed = True
                        n_copies += 1
                if changed:
                    by_tarc.setdefault(rel_tarc, {})[fn] = d
    print(f'texture generiche: {len(new_raw)} texture in {n_copies} copie')


EU_KEYS = ('sh_zakka_o00', 'shop_zakka01', 'sh_flower_o00', 'shop_cloth00', 'sh_b01_o03', 'mall_07_a',
           'ShopDef02', 'ShopDef03')


def _is_eu(arc, f):
    return any(k in f for k in EU_KEYS)


def eu_preview(Z=3):
    """anteprima originale | nuova (3x) delle insegne EU, ognuna alla sua dimensione, stagioni diverse comprese"""
    from PIL import ImageDraw as _D
    rows = []
    for (arc, f) in SPEC:
        if not _is_eu(arc, f):
            continue
        for v in ([f + '@' + s for s in ('00_spring_day.bctex', '06_winter_day.bctex', '08_fushigi.bctex')]
                  if arc == 'atlas' else [f]):
            if arc == 'atlas' and 'sh_b01' in v and not v.endswith('00_spring_day.bctex'):
                continue
            _, _, o = load(arc, v)
            n = Image.open(_png_path(arc, v)).convert('RGBA')
            rows.append((v if arc == 'atlas' else f.split('/')[-1], o, n))
    W = max(r[1].width for r in rows) * Z
    H = sum(r[1].height * Z + 16 for r in rows)
    sheet = Image.new('RGB', (2 * W + 12, H), (120, 120, 120))
    dr = _D.Draw(sheet)
    y = 0
    for name, o, n in rows:
        dr.text((2, y + 1), name, fill=(255, 255, 0))
        for j, im in enumerate((o, n)):
            bg = Image.new('RGBA', im.size, (120, 120, 120, 255))
            bg.alpha_composite(im)
            sheet.paste(bg.resize((im.width * Z, im.height * Z), Image.NEAREST).convert('RGB'), (j * (W + 12), y + 12))
        y += o.height * Z + 16
    os.makedirs(OUT, exist_ok=True)
    sheet.save(os.path.join(OUT, '_eu_preview.png'))
    print('anteprima EU ->', os.path.join(OUT, '_eu_preview.png'), sheet.size)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if cmd == 'render_eu':
        render('--force' in sys.argv, only=_is_eu)
        eu_preview()
        sys.exit(0)
    if cmd == 'eu_preview':
        eu_preview()
        sys.exit(0)
    if cmd == 'preview':
        main(True)
    elif cmd == 'render':
        render('--force' in sys.argv)
    elif cmd == 'install':
        install()
    else:                       # build completa: genera ciò che manca/è cambiato e installa
        render()
        install()
