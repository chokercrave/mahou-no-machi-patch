# Guida alla traduzione

Regole per correggere o migliorare i testi italiani. Valgono per i lotti di dialoghi in `work/trad/batches/`; per gli
altri file vedi la tabella "Dove modificare cosa" in [architettura.md](architettura.md#dove-modificare-cosa).

## I lotti di dialoghi

Ogni lotto è una coppia di file:

- `bNNN.tsv`: il testo giapponese, una pagina per riga: `id<TAB>giapponese`;
- `bNNN.it.tsv`: la traduzione, **una riga per ogni id, nello stesso ordine**: `id<TAB>italiano`.

I lotti `mNNN` sono riscritture e hanno la precedenza sui `bNNN`; i lotti `iNNN` contengono nomi di oggetti, prodotti
e parole magiche.

Una **pagina** è il testo che compare in un solo riquadro. Righe vicine sono spesso battute della stessa conversazione:
leggile insieme per capire il contesto. Dove la stessa frase esisteva nella versione europea del gioco per DS, la build
usa quella traduzione ufficiale (`work/trad/ds_pages.json`).

Per trovare una battuta vista in gioco, cerca nel testo italiano dei file `.it.tsv` una parte della frase. Dopo la
modifica:

```bash
py scripts/build_all.py --from batch_import
```

`batch_import` e `manual_import` scartano le righe che non rispettano le regole qui sotto e le elencano in
`work/trad/batch_errors.tsv`: controlla quel file dopo ogni modifica.

## Segnaposto

Ogni segnaposto del giapponese va copiato **identico** nell'italiano, lo stesso numero di volte:

| Segnaposto | Significato |
|---|---|
| `<P>` | Nome del giocatore. Il giapponese usa spesso il nome al posto di "tu": in italiano si può sostituire con "tu"/"ti" ed eliminarlo. È l'unico che si può togliere. |
| `<X1>`, `<X2>`… | Parola inserita dal gioco: un nome, un oggetto, un luogo, una cifra, oppure un effetto (pausa, suono). Se in giapponese sta in fondo senza testo dopo, di solito è un effetto: lascialo in fondo. |
| `<c4>parola</c>` (anche c2, c3, c5, c8…) | Parola colorata. Mettilo attorno alla parola italiana corrispondente; ogni `<cN>` si chiude con `</c>`. |
| `[$599]` | Desinenza che si accorda al sesso del giocatore: `pront[$599]` diventa "pronto" o "pronta". |
| `[$598]` | Come `[$599]` per il plurale: "i" oppure "e". |

## Lunghezza

Il riquadro contiene **3 righe da circa 32 caratteri**; l'a capo lo fa il gioco.

- Ogni pagina deve stare entro **90 caratteri circa**. `<P>` e `<X…>` contano circa 8 caratteri.
- Se il giapponese è lungo, riassumi come faceva la localizzazione DS: va bene adattare, purché il senso resti.
- Le pagine brevissime (`…`, `!?`, versi) restano brevissime.
- Le scelte nei menu hanno al massimo **15 caratteri**; altri limiti fissi sono in `work/trad/short_limits.json`.

## Stile

- Italiano naturale e colloquiale, adatto a ragazzi. Niente calchi dal giapponese, niente "-san" o onorifici.
- **Il giocatore può essere maschio o femmina.** Quando si parla al giocatore, evita gli accordi di genere oppure usa
  `[$599]`: "Sei stanc[$599]?" oppure "Hai l'aria stanca?".
- Gli abitanti si danno del tu. Insegnanti, negozianti e personaggi altolocati possono essere più formali.
- Le parlate dei personaggi si rendono in italiano: i gatti commessi aggiungono ogni tanto "miao!", Hassan parla un
  italiano stentato e buffo, il Ministro è pomposo.
- Onomatopee all'italiana: "Uffa!", "Evvai!", "Mmm…", "Ehi!".
- Punteggiatura: `...` o `…`, `!?`, virgolette `""` (mai 「」).
- I caratteri 葱 蕪 蓬 蓮 韮 sono **icone** del font del gioco (cuore, faccina arrabbiata, sorriso, zampa, faccina
  triste): copiali così come sono.
- Caratteri permessi: ASCII, à è é ì ò ù À È É Ì Ò Ù ç ° « » ' " … ♪. Niente emoji o altri simboli.

## Termini fissi

| Giapponese | Italiano |
|---|---|
| コーデ / スーパーコーデ | look / super look |
| 店長 | capo (quando ci si rivolge al giocatore) / direttore del negozio |
| ベリーズ | Berry's: la build lo sostituisce con *Spell & Spill*, il nome italiano della rivista |
| トレンドランキング | Classifica delle Tendenze |
| フェア | fiera |
| ショッピングモール, モール | centro commerciale |
| ロイヤルブランド | Marchio Reale |
| マイスター | Maestro |
| 校長 | Preside |
| まほう / まほう語 | magia / linguistica magica |
| じゅぎょう | lezione |
| ウワサ | voci, pettegolezzi |
| 親友 / 恋人 | amico per la pelle / fidanzato, fidanzata |

I nomi dei personaggi sono in `work/glossary/npc_it.tsv`.

## Controllo prima di salvare

1. Stesso numero di righe e stessi id del file giapponese.
2. In ogni riga, gli stessi segnaposto del giapponese.
3. Nessun carattere giapponese rimasto (tranne le icone).
4. Nessuna pagina oltre i 90 caratteri circa.
