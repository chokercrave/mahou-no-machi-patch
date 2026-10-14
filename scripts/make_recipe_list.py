"""Nomi delle liste ricette (ucc/ucc_common.tarc -> 005.bin): non e' un RESO ma una tabella:
u32 conteggio(35), u32 inizio pool stringhe (0x1a8), poi 35 voci da 12 byte [u32 offset stringa | 8 byte attributi],
poi il pool UTF-16LE con terminatori. Si traducono le stringhe e si ricalcolano gli offset delle voci."""
import os, struct, sys
sys.path.insert(0, os.path.dirname(__file__))
import tbaf
import blob_texts as b

TR = {
    'オーブンりょうりレシピ': 'Ricette al forno', 'にこみりょうりレシピ': 'Ricette stufati',
    'つめたいスイーツレシピ': 'Ricette dolci freddi', 'フライパンりょうりレシピ': 'Ricette in padella',
    'あげものレシピ': 'Ricette fritti', 'ふくレシピ': 'Ricette abiti', 'ティアラレシピ': 'Ricette tiare',
    'ネックレスレシピ': 'Ricette collane', 'はなたばレシピ': 'Ricette bouquet',
    'こいするケーキのレシピ': "Torta d'amore", 'ムードクッキーのレシピ': 'Biscotti mood',
    'ビックリパイのレシピ': 'Torta a sorpresa', 'イケてるふくのレシピ': 'Abito alla moda',
    'ラッキーチャームのレシピ': 'Portafortuna', 'まほうのランプのレシピ': 'Lampada magica',
    'ジュエリーボックスのレシピ': 'Portagioie', 'おさそいブーケのレシピ': "Bouquet d'invito",
    'やすらぎティーのレシピ': 'Tè rilassante', 'みわくのかおりのレシピ': 'Aroma seducente',
    'イタズラはねペンのレシピ': 'Penna birichina', 'ビッグマックレシピ': 'Maxi panino',
    'ふしぎなスープ': 'Zuppa misteriosa', 'イヤリングレシピ': 'Ricette orecchini'}


def convert(d):
    n, pool = struct.unpack_from('<2I', d, 0)
    ents = [(struct.unpack_from('<I', d, 4 + i * 12)[0], d[8 + i * 12:16 + i * 12]) for i in range(n)]
    new_pool, newoff = bytearray(), {}
    out = bytearray(d[:pool])
    for i, (off, rest) in enumerate(ents):
        if off not in newoff:
            end = off
            while d[end:end + 2] != b'\0\0':
                end += 2
            s = d[off:end].decode('utf-16-le')
            s = TR.get(s, s)
            newoff[off] = pool + len(new_pool)
            new_pool += (s + '\0').encode('utf-16-le')
        struct.pack_into('<I', out, 4 + i * 12, newoff[off])
    return bytes(out) + bytes(new_pool)


def main():
    src = os.path.join(b.X, 'ucc/ucc_common.tarc_x', '005.bin')
    data = convert(open(src, 'rb').read())
    out = os.path.join(b.MOD, 'ucc/ucc_common.tarc')
    tmp = out + '.tmp'
    tbaf.rebuild(out, {'005.bin': data}, tmp)
    os.replace(tmp, out)
    print('005.bin ricette:', len(data), 'byte')


if __name__ == '__main__':
    main()
