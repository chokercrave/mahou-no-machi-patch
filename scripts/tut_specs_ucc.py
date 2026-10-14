"""Lavagne ucc_tuto_NN (schermo superiore 400 px, immagine 512x256) e ucc_tuto_NN_u (320x256): tutorial dei lavori
(cucina, cucito, tè, fiori...). Stesso testo nelle due versioni: titoletto in alto + 1-2 righe in basso."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import tut_board as tb, tut_edit
from tut_edit import retext, hdr

ARCH = 'menu_tutorial_pics3'
STEPS = {
    1: ('Gira il pennino per mescolare', ['Regola la velocità di mescolata', 'per non far traboccare!']),
    2: ('Cuoci a puntino nel forno', ['Guarda bene nel forno e, quando è', 'dorato, tocca per fermare!']),
    4: ('Raffredda bene in frigo', ['Gira la valvola per mandare il freddo nel', 'frigo; quando è freddo premi OK']),
    5: ('Mescola e gira per cuocere', ['Strofina e mescola per non bruciare,', 'tocca per girare la padella!']),
    6: ('Friggi senza esagerare', ['Controlla il colore degli ingredienti', 'e toglili prima che brucino!']),
    7: ('Decora con cura', ['Decora con cura con i condimenti!']),
    8: ('Decora con cura', ['Decora con cura con i condimenti!']),
    9: ('Impiatta con cura', ['Impiatta gli ingredienti con cura!']),
    10: ('Annoda bene il nastro', ['Tocca seguendo la procedura', 'per annodare il nastro!']),
    11: ('Cuci bene con la macchina', ['Cuci con la macchina seguendo', 'la linea sulla stoffa!']),
    12: ('Prepara un tè delizioso', ['Attento a non scaldare troppo,', 'prepara un tè delizioso!']),
    13: ('Estrai bene il profumo', ['Attento a non scaldare troppo,', 'estrai il profumo con cura!']),
    14: ('Lucida bene il prodotto', ['Lucida con cura fino in fondo', 'per farlo brillare!']),
    15: ('Incarta bene i fiori', ['Tocca seguendo la procedura', 'per incartare i fiori!']),
    16: ('Sistema bene i fiori', ['Sposta i fiori per', 'sistemarli bene!']),
    17: ('Mescola e fai sobbollire', ['Togli la schiuma toccando e', 'mescola per non bruciare!']),
    18: ('Decora con cura', ['Decora bene le pietre preziose!']),
    19: ('Disponi con cura', ['Disponi gli ingredienti con cura!']),
    20: ('Estrai bene il colore', ['Attento a non scaldare troppo,', 'estrai bene il colore!']),
    21: ('Impiatta con cura', ['Impiatta il gelato con cura!']),
}


def save(img, name):
    d = os.path.join(tb.OUT, ARCH)
    os.makedirs(d, exist_ok=True)
    w = img.width
    img.crop((0, 0, 256, 256)).save(os.path.join(d, name + '_l.png'))
    img.crop((256, 0, w, 256)).save(os.path.join(d, name + '_r.png'))


def one(name, head, foot):
    img = tb.load(name)
    tut_edit.PHOTO = False
    hdr(img, (0, 44, 0, 63), head)
    x1 = 438 if name == 'ucc_tuto_04' else img.width - 24
    retext(img, (24, 184, x1, 224), foot, align='l', px=12)
    save(img, name)


def main(only=None):
    for n, (head, foot) in STEPS.items():
        for name in (f'ucc_tuto_{n:02d}', f'ucc_tuto_{n:02d}_u'):
            if only and name not in only:
                continue
            try:
                one(name, head, foot)
                print('ok', name)
            except Exception as e:
                print(f'  ! {name}: {type(e).__name__} {e}')


if __name__ == '__main__':
    main(sys.argv[1:])
