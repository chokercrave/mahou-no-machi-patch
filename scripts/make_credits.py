"""Crediti (menu_staff_roll_pic, staff_name_NN, 256x256): titoli tradotti, nomi e societa in caratteri latini (Nome Cognome), col font del gioco
(DF_kyougeki, come le lavagne) e gli ornamenti a ricciolo dell'originale; colori arancio/marrone dell'originale. Il layout (altezza delle righe)
segue le righe dell'originale. Uscita: work/img_it/_auto/menu_staff_roll_pic/staff_name_NN.png (dopo gen_labels).
  python make_credits.py [numeri] [--test]     (--test scrive in work/tut/credits_test)"""
import os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import ui_font

ROOT = os.path.join(os.path.dirname(__file__), '..')
SRC = os.path.join(ROOT, 'work', 'img', 'ui', 'menu_staff_roll_pic')
OUT = os.path.join(ROOT, 'work', 'img_it', '_auto', 'menu_staff_roll_pic')
PX = 13

# --- hiragana -> romaji (Hepburn, vocali lunghe come nei crediti occidentali: ou->o, oo->oh, uu->u) ---
_B = dict(zip('あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん',
              'a i u e o ka ki ku ke ko sa shi su se so ta chi tsu te to na ni nu ne no ha hi fu he ho ma mi mu me mo ya yu yo ra ri ru re ro wa o n'.split()))
_B.update(dict(zip('がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ',
                   'ga gi gu ge go za ji zu ze zo da ji zu de do ba bi bu be bo pa pi pu pe po'.split())))
_Y = {'きゃ': 'kya', 'きゅ': 'kyu', 'きょ': 'kyo', 'しゃ': 'sha', 'しゅ': 'shu', 'しょ': 'sho', 'ちゃ': 'cha', 'ちゅ': 'chu', 'ちょ': 'cho',
      'にゃ': 'nya', 'にゅ': 'nyu', 'にょ': 'nyo', 'ひゃ': 'hya', 'ひゅ': 'hyu', 'ひょ': 'hyo', 'みゃ': 'mya', 'みゅ': 'myu', 'みょ': 'myo',
      'りゃ': 'rya', 'りゅ': 'ryu', 'りょ': 'ryo', 'ぎゃ': 'gya', 'ぎゅ': 'gyu', 'ぎょ': 'gyo', 'じゃ': 'ja', 'じゅ': 'ju', 'じょ': 'jo',
      'びゃ': 'bya', 'びゅ': 'byu', 'びょ': 'byo', 'ぴゃ': 'pya', 'ぴゅ': 'pyu', 'ぴょ': 'pyo'}


def romaji(h):
    out, i = '', 0
    while i < len(h):
        c = h[i]
        if h[i:i + 2] in _Y:
            out += _Y[h[i:i + 2]]
            i += 2
            continue
        if c == 'っ':
            nxt = romaji(h[i + 1:i + 3]) if i + 1 < len(h) else ''
            out += 't' if nxt.startswith('ch') else (nxt[0] if nxt else 't')
            i += 1
            continue
        out += _B.get(c, c)
        i += 1
    for a, b in (('ou', 'o'), ('oo', 'oh'), ('uu', 'u')):
        out = out.replace(a, b)
    return out


def N(fam, given):
    return (romaji(given).capitalize() + ' ' + romaji(fam).capitalize()).strip()


def H(t):
    return ('h', t)


def P(f, g):
    return ('n', N(f, g))


def C(t):
    return ('c', t)


# per ogni immagine le righe dall'alto in basso: titolo (h) | nome (n) | testo semplice (c)
ROWS = {
    1: [C('Konami Digital Entertainment')],
    2: [H('Produttore'), P('ふじさわ', 'やすし')],
    3: [H('Direttore'), P('こばやし', 'ゆういち'), P('ねもと', 'たかみつ')],
    4: [H('Direttore del design'), P('いけだ', 'しゅうへい'), P('おの', 'さわか'), H('Designer'), P('たなか', 'ひでき'), P('こにし', 'まさと'),
        H('Responsabile tecnico'), P('すずき', 'あつし')],
    5: [H('Consulente tecnico'), P('のぐち', 'くにひこ'), P('なかやま', 'たから'), P('かわまた', 'よしのり'), P('まつもと', 'かずや'),
        P('やまだ', 'きよし'), P('たかだ', 'ようへい'), P('いたくら', 'まこと'), P('くまくら', 'ひろし')],
    6: [H('Consulente di rete'), P('かみや', 'さとし'), H('Direttore del suono'), P('ふるさわ', 'としひさ'), H('Musica del tema'), P('とだ', 'のぶこ')],
    7: [H('Responsabile di progetto'), P('むかいとうげ', 'しんご'), H('Supporto al progetto'), P('いしはら', 'あきひろ'), P('かんの', 'まさのぶ'),
        P('こむた', 'おさむ'), P('しまざき', 'かつや'), P('そのべ', 'ひろあき')],
    8: [H('Produzione esterna in collaborazione')],
    9: [C('Tapot Co., Ltd.')],
    10: [H('Direttore'), P('いわさわ', 'よしあき'), H('Responsabile di progetto'), P('よこい', 'ひさき'), H('Direttore tecnico'), P('やまき', 'てるひと')],
    11: [H('Programmatore capo'), P('みやけ', 'ようへい'), P('いけだ', 'ひとし'), H('Programmatore'), P('かいえだ', 'とみのぶ'), P('はまだ', 'しょう'),
         P('ますたに', 'ひであき'), P('かわい', 'じゅんいち'), P('あしざわ', 'しゅうほ')],
    12: [P('おだ', 'こう'), P('かとう', 'まお'), P('ふくだ', 'まさよし'), P('やまもと', 'もりひで'), P('かしわざき', 'ひろあつ'), P('いしまる', 'けんじ'),
         P('なかじま', 'やすちか'), P('みべ', 'じゅんいち'), P('ひご', 'こうすけ')],
    13: [H('Scripter'), P('さかえ', 'ひろつぐ'), P('みやでら', 'かずひこ'), P('いさやま', 'ひでよ')],
    14: [H('Designer capo'), P('のぐち', 'こうじ'), H('Designer'), P('まえだ', 'さきこ'), P('さいとう', 'えり'), P('よねやま', 'ゆうこ'),
         P('おの', 'りょう'), P('こばやし', 'ちえ'), P('はやかわ', 'しんいち')],
    15: [P('みやした', 'ゆうじ'), P('まさき', 'きょうせい'), P('いしごうおか', 'たく'), P('まるやま', 'いくみ'), P('たけむら', 'ともみ'),
         P('しろうず', 'せいごう'), P('さとう', 'たかゆき')],
    16: [H('Pianificatore capo'), P('ふじい', 'だいすけ'), H('Pianificatore'), P('おおはし', 'ごろう'), P('つゆざき', 'たかゆき'),
         P('ひらとう', 'しゅう'), P('いたがき', 'ゆうすけ')],
    17: [H('Tester'), P('いのたに', 'まさひこ'), P('まつお', 'くにひろ'), P('くろずみ', 'ゆたか'), P('いのうえ', 'けんた'), P('たかさき', 'えいじ'),
         P('よしおか', 'じろ')],
    18: [P('よしおか', 'まさる')],
    19: [H('Produzione del design'), C('Millennium Kitchen Co., Ltd.')],
    20: [H('Designer'), P('くろさわ', 'てつたろう'), P('くむら', 'あさこ'), P('ばんどう', 'よしのり'), P('ほんま', 'しゅんすけ'), P('なかがみ', 'めぐみ'),
         P('くまもと', 'みつひろ'), P('たしろ', 'だいへい'), P('あさが', 'みき'), P('さとう', 'あきこ')],
    21: [P('ほんま', 'かいち'), P('よもぎだ', 'ひろみ'), P('てらい', 'りょういち')],
    22: [P('あやべ', 'かず')],
    23: [H('Produzione dello scenario'), C('Elsewhere Ltd.')],
    24: [H('Gestione dello scenario'), P('おがわ', 'かえで'), H('Scrittore capo'), P('たかおか', 'しゅんのすけ'), H('Assistente allo scenario'),
         P('たかさき', 'とおる'), C('Fuh')],
    25: [H('Scrittore'), P('いずの', 'ひらなりにごう'), C('Koshidango'), P('あかい', 'けい'), P('つちだ', 'たろう'), P('みなみの', 'みなみ'), P('かんの', 'しんし')],
    26: [C('Genki Co., Ltd.')],
    27: [H('Programmatore'), P('よねやま', 'たつとし'), H('Pianificatore'), P('もちづき', 'けんいち')],
    28: [H('Character design'), C('HACCAN')],
    29: [C('Coconuts Studio'), H('Design dei mobili'), P('さいとう', 'かよこ'), C('Cubist Co., Ltd.'), H('Design dei mobili'), P('みやざわ', 'ただし')],
    30: [H('Produzione musiche'), C('Sound Aims Ltd.')],
    31: [H('Direttore del suono'), P('みちした', 'もも'), H('Composizione'), P('ちかもり', 'しんや'), P('たまる', 'まさひろ'), P('おかだ', 'ひろのり'),
         P('おおつか', 'まさのり'), P('にしもと', 'ともよ')],
    32: [H('Conversione'), P('さいとう', 'たかゆき'), P('たむら', 'こうたろう')],
    33: [C('Konami Digital Entertainment'), H('Promozione e marketing')],
    34: [H('Marketing'), P('なかむら', 'たかし'), P('つきのき', 'たけひこ'), H('Promozione'), P('きぐち', 'さとこ'), P('こんどう', 'としひろ'),
         H('Sito web'), P('さなだ', 'まさゆき')],
    35: [H('Pubbliche relazioni'), P('よしい', 'みさこ'), H('Vendite'), P('わかばやし', 'てつや'), P('あつみ', 'ひでやす'),
         H('Ricerca di mercato'), P('すずき', 'よしあき')],
    36: [H('Direttore artistico'), P('こさか', 'みほ'), H('Artwork designer'), P('さが', 'ゆきよ')],
    37: [H('Debug'), C('Quality Control Center'), C('Monitoring Group'), P('おおはし', 'なおと'), C('Digital Hearts Co., Ltd.')],
    38: [H('Design dei caratteri'), C('Fontworks Inc.')],
    39: [H('Ringraziamenti speciali'), P('なかむら', 'けんじ'), P('あらい', 'たかこ')],
    40: [H('Produttore senior'), P('うちだ', 'あかり')],
    41: [C('(C)2012 Konami Digital Entertainment')],
}


def bands(alpha, gap=3):
    rows = np.nonzero((alpha > 30).any(1))[0]
    out, start, prev = [], None, None
    for y in rows:
        if start is None:
            start = prev = y
        elif y - prev > gap:
            out.append((start, prev))
            start = y
        prev = y
    if start is not None:
        out.append((start, prev))
    return out


def paint(mask, color):
    im = Image.new('RGBA', mask.size, tuple(color) + (0,))
    im.putalpha(mask)
    return im


def build(n):
    src = Image.open(os.path.join(SRC, f'staff_name_{n:02d}.png')).convert('RGBA')
    a = np.asarray(src)
    rgb = a[..., :3].astype(int)
    alpha = a[..., 3]
    orange = (alpha > 80) & (rgb[..., 0] > 200) & (rgb[..., 1] < 150) & (rgb[..., 2] < 90)
    dark = (alpha > 160) & ~orange
    bnd = bands(alpha)
    rows = ROWS[n]
    if len(bnd) != len(rows):
        print(f'  ! staff_name_{n:02d}: {len(bnd)} righe nell originale, {len(rows)} nel testo')
        return None
    col_o = tuple(int(v) for v in np.median(rgb[orange], axis=0)) if orange.any() else (255, 78, 18)
    col_b = tuple(int(v) for v in np.median(rgb[dark], axis=0)) if dark.any() else (110, 60, 10)
    out = Image.new('RGBA', src.size, (0, 0, 0, 0))
    for (y0, y1), (kind, txt) in zip(bnd, rows):
        band = (slice(y0, y1 + 1), slice(None))
        allx = np.nonzero((alpha[band] > 30).any(0))[0]
        cx = (allx.min() + allx.max() + 1) / 2
        mask = ui_font.core_small(txt, PX, 1)
        if kind == 'h':
            ox = np.nonzero(orange[band].any(0))[0]
            oy = np.nonzero(orange[band].any(1))[0]
            if len(ox) == 0:
                print(f'  ! staff_name_{n:02d}: riga {y0} senza arancione')
                continue
            lx1, rx0 = ox.min(), ox.max() + 1
            orn_l = src.crop((allx.min(), y0, lx1, y1 + 1))
            orn_r = src.crop((rx0, y0, allx.max() + 1, y1 + 1))
            ty = y0 + (oy.min() + oy.max() + 1) / 2
            total = orn_l.width + 3 + mask.width + 3 + orn_r.width
            x = max(0, min(int(round(cx - total / 2)), src.width - total))
            out.alpha_composite(orn_l, (x, y0))
            out.alpha_composite(paint(mask, col_o), (x + orn_l.width + 3, int(round(ty - mask.height / 2))))
            out.alpha_composite(orn_r, (x + orn_l.width + 3 + mask.width + 3, y0))
        else:
            x = max(0, min(int(round(cx - mask.width / 2)), src.width - mask.width))
            out.alpha_composite(paint(mask, col_b), (x, int(round((y0 + y1 + 1) / 2 - mask.height / 2))))
    return out


def main(args):
    test = '--test' in args
    nums = [int(a) for a in args if a.isdigit()] or sorted(ROWS)
    d = os.path.join(ROOT, 'work', 'tut', 'credits_test') if test else OUT
    os.makedirs(d, exist_ok=True)
    done = 0
    for n in nums:
        im = build(n)
        if im is not None:
            im.save(os.path.join(d, f'staff_name_{n:02d}.png'))
            done += 1
    print(f'{done} immagini dei crediti scritte in {os.path.relpath(d, ROOT)}')


if __name__ == '__main__':
    main(sys.argv[1:])
