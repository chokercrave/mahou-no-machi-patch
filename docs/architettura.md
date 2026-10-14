# Architettura del progetto

*[English](en/architecture.md)*

Come è organizzato il repository, cosa fa ogni passaggio della build e dove mettere le mani per cambiare qualcosa.
Per compilare la patch vedi [compilare.md](compilare.md).

- [Cartelle](#cartelle)
- [La build passo per passo](#la-build-passo-per-passo)
- [Formati dei file del gioco](#formati-dei-file-del-gioco)
- [Il codice del gioco](#il-codice-del-gioco)
- [Regole per non far crashare la 3DS](#regole-per-non-far-crashare-la-3ds)
- [Dove modificare cosa](#dove-modificare-cosa)

## Cartelle

```
scripts/              tutti gli script Python (build, formati, generatori, controlli)
work/trad/            traduzioni: lotti di dialoghi, tabelle, interfaccia, codice
work/trad/batches/    lotti di dialoghi: bNNN.tsv (giapponese) + bNNN.it.tsv (italiano), mNNN = riscritture
work/glossary/        nomi italiani dei personaggi
work/img/labels/      indice delle etichette grafiche da rigenerare
work/v11/funcmap.tsv  corrispondenza delle funzioni fra codice Ver.1.0 e Ver.1.1
tools/fonts/          font liberi delle insegne (licenze in LICENZE_FONT.txt)
docs/                 documentazione
```

Cartelle create sul tuo computer e mai caricate su GitHub (sono nel `.gitignore`):

```
work/3ds/             il gioco estratto da prepare.py (romfs, exefs, intestazioni)
work/3ds/romfs_x/     archivi .tarc estratti
work/v11/exefs, raw/  codice ed exheader dell'aggiornamento 1.1
work/img/ui, work/tut texture originali in PNG, base per i generatori di immagini
work/img_it/          immagini italiane generate (e cache dei generatori lenti)
build/                la mod finita
release/              i pacchetti
tools/3dstool, xdelta3, models   strumenti esterni
```

## La build passo per passo

`scripts/build_all.py` esegue questi passaggi, in quest'ordine. Ognuno legge i file originali da `work/3ds` e scrive i
file modificati nella mod (`build/00040000000B4A00`, o la cartella scelta in `local_paths.json`).

| # | Passaggio | Cosa fa |
|---|---|---|
| 1 | `build_fonts` | Aggiunge ai font del gioco le lettere accentate. |
| 2 | `batch_import` | Legge i lotti di dialoghi `bNNN.it.tsv`, controlla segnaposto e caratteri, crea `batch_pages.json`. |
| 3 | `fix_slots` | Correzioni puntuali di singole battute (scrive il lotto `m006`). |
| 4 | `manual_import` | Legge i lotti di riscrittura `mNNN.it.tsv`, crea `manual_pages.json`. |
| 5 | `gen_labels` | Disegna le etichette grafiche da `labels_it.tsv`. Svuota `work/img_it/_auto`. |
| 6 | `build_text` | Applica tutti i dialoghi ai file di testo del gioco (formato RESO). Priorità: riscritture > lotti > testi della versione DS. |
| 7 | `blob_texts import` / `build` | Testi in blocchi senza nome dentro gli archivi (nomi di oggetti, prodotti, parole magiche). |
| 8 | `build_npc` | Profili dei personaggi. |
| 9 | `build_tables` | Tabelle di stringhe di `common.tarc` (menu, negozio, finestre della borsa). |
| 10 | `build_ui` | Testi dei layout dell'interfaccia (`ui_trad.json`) e buffer di testo allargati. |
| 11 | `make_recipe_list` … `make_license_headers` | Piccole immagini dell'interfaccia: liste ricette, avvisi, targhette, linguette, titoli. |
| 12 | `make_images` | Altre immagini dei menu (pulsanti, titoli). |
| 13 | `make_magazine_logo`, `make_magazine_bg`, `make_magazine_pages`, `make_magazine`, `make_magpage_labels` | Rivista *Spell & Spill*: logo, sfondi, pagine e titoli. |
| 14 | `make_signs` | Insegne 3D dei negozi e immagini 2D: cancella il giapponese, ricostruisce lo sfondo e ridisegna l'italiano a strati (ombra, contorni, riempimento). |
| 15 | `make_credits` | Crediti finali. |
| 16 | `make_tutorials` | Lavagne delle lezioni e dei tutorial. |
| 17 | `build_images` | Inserisce tutte le immagini generate nelle texture del gioco. |
| 18 | `make_title_credit` | Credito della patch con il numero di versione sul titolo. |
| 19 | `make_logo_skip` | Toglie i loghi iniziali. |
| 20 | `patch_shop_hours` | Script degli eventi: negozi 24/7, relazioni, opzioni, incantesimi. |
| 21 | `build_code` | Codice del gioco: stringhe tradotte, patch ARM, porting alla Ver.1.1, exheader. |

I generatori lenti (`make_signs` e la rivista) salvano una cache in `work/cache_steps`: se il loro codice
e i loro file di partenza non cambiano, la build ricopia il risultato precedente. `--nocache` forza la rigenerazione.

## Formati dei file del gioco

| Formato | Cosa contiene | Script |
|---|---|---|
| `.tarc` (TBAF) | Archivio di Konami con compressione LZ11 per file | `tbaf.py` |
| RESO (`.rdbt` + `.rndx`) | Testi dei dialoghi e dei messaggi | `reso.py`, `textdb.py` |
| EVSC (`.rdbt` + `.rndx` in `script.tarc`) | Script degli eventi (dialoghi, scelte, magie, porte) | `evsc.py` |
| DARC (`.arc`) | Archivio dei layout | `darc.py` |
| BCLYT | Layout dell'interfaccia e pannelli di testo | `bclyt.py` |
| BCLIM | Texture 2D | `bclim.py` |
| BCFNT | Font | `bcfnt.py`, `font_patch.py` |
| CGFX | Modelli 3D e loro texture (insegne) | `cgfx.py` |
| tabelle con stringhe UTF-16 | Menu, negozio, ecc. in `common.tarc` | `strtable.py` |

`evsc.py` è anche un disassemblatore: utile per leggere cosa fa uno script di evento prima di modificarlo.

## Il codice del gioco

`build_code.py` lavora su `exefs/code.bin`:

- **Stringhe nel codice:** da `work/trad/code_it.tsv` (indirizzo, giapponese, italiano). Se l'italiano non ci sta, la
  stringa viene spostata in uno spazio libero e i puntatori aggiornati.
- **Patch ARM:** scritte in assembly dentro gli script (`options.py`, `fast_travel.py`, `name_plate.py`, …) e
  assemblate da `armasm.py`. Il codice nuovo va in spazi che il gioco non usa: il riempimento in fondo alla sezione `.text` e le
  due funzioni del filtro delle parole vietate, tolte dalla patch.
- **Ver.1.1:** le patch sono scritte per gli indirizzi della Ver.1.0. `port11.py` le riporta sulla 1.1 usando
  `work/v11/funcmap.tsv` e controlla parola per parola che il codice di destinazione sia quello atteso.
  `port_audit.py` ripete il controllo su tutte le patch.
- **Exheader:** la mod contiene `code.bin` già patchato e l'exheader della 1.1, invece di una patch `code.ips`. Luma3DS
  scrive alcuni dati suoi in fondo alle sezioni del codice: con `code.ips` quei dati finivano sopra il nostro codice
  nuovo e il gioco si bloccava all'avvio. L'exheader fissa le dimensioni giuste delle sezioni.

Le scoperte sul funzionamento interno del gioco (indirizzi, variabili, strutture) sono raccolte in
[note_tecniche.md](note_tecniche.md).

## Regole per non far crashare la 3DS

L'emulatore Azahar perdona errori che sulla 3DS vera bloccano il gioco. Le regole che la build rispetta:

1. **Allineamento:** archivi, texture e codice restano allineati a 4 byte. Un accesso disallineato in Azahar funziona,
   sulla console no.
2. **Niente letture da NULL:** Azahar restituisce 0, la 3DS si blocca. Dopo ogni prova in emulatore,
   `emu_log_check.py` cerca questi accessi nel log.
3. **Non togliere parti dei layout:** il codice cerca pannelli e parti dei menu per nome o posizione. Per nasconderne
   una si azzerano la texture, la scala o la posizione, non la si elimina.
4. **Compressione originale:** ogni file dentro un `.tarc` mantiene la compressione che aveva. Comprimere file che il
   gioco legge non compressi rompe, per esempio, i dialoghi.
5. **Lunghezze massime:** alcuni testi hanno un limite fisso (`short_limits.json`, `blob_limits.json`), per esempio 15
   caratteri per le scelte nei menu.

`check_mod.py` controlla automaticamente i punti 1, 4 e la struttura degli archivi.

## Dove modificare cosa

| Voglio cambiare… | File | Poi |
|---|---|---|
| una battuta di dialogo | `work/trad/batches/*.it.tsv` (cerca il testo italiano) | `build_all.py --from batch_import` |
| un menu o un'etichetta dell'interfaccia | `work/trad/ui_trad.json` | `build_all.py --from build_ui` |
| nomi di oggetti, prodotti, parole magiche | `work/trad/batches/iNNN.it.tsv` | `build_all.py --from batch_import` |
| voci dei menu di gioco e del negozio | `work/trad/tables/*.json` | `build_all.py --from batch_import` |
| un testo nel codice (es. messaggi di sistema) | `work/trad/code_it.tsv` | `build_all.py --only build_code` |
| un'insegna o un'immagine 2D | `scripts/make_signs.py` (insegne), `scripts/ui_specs.py` (immagini) | `build_all.py --from make_signs` |
| una lavagna | `scripts/tut_specs_*.py`, `scripts/tut_charm.py` | `build_all.py --from make_tutorials` |
| un titolo della rivista | `scripts/mag_texts.py` | `build_all.py --from make_magazine_bg` |
| le Opzioni o un miglioramento di gioco | `scripts/options.py`, `fast_travel.py`, `patch_relationships.py`, `patch_shop_hours.py` | `build_all.py --from patch_shop_hours` (`--from build_text` se cambi anche le battute) |

Le regole di stile della traduzione (segnaposto, lunghezze, tono) sono in [traduzione.md](traduzione.md).
