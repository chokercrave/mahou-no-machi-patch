# Compilare la patch dai sorgenti

*[English](en/building.md)*

Questa guida ricostruisce la patch partendo dalla **propria copia del gioco**. Il repository non contiene file di
Nintendo o Konami: gli script li leggono dal tuo dump e ci applicano la traduzione.

Ti serve solo se vuoi modificare la patch o controllare come è fatta. Per giocare basta scaricare il pacchetto pronto
dalla pagina **Releases**.

- [In breve](#in-breve)
- [1. Requisiti](#1-requisiti)
- [2. Strumenti esterni](#2-strumenti-esterni)
- [3. I file del gioco](#3-i-file-del-gioco)
- [4. Preparazione](#4-preparazione)
- [5. Compilazione](#5-compilazione)
- [6. Provare la mod](#6-provare-la-mod)
- [7. Creare il pacchetto](#7-creare-il-pacchetto)
- [Ricompilare dopo una modifica](#ricompilare-dopo-una-modifica)
- [Problemi frequenti](#problemi-frequenti)

## In breve

```bash
git clone https://github.com/chokercrave/mahou-no-machi-patch.git
cd mahou-no-machi-patch
py -m pip install -r requirements.txt
py scripts/prepare.py "C:/giochi/Tongari.cci" "C:/giochi/Tongari Update v1.1.cia"
py scripts/build_all.py
py scripts/check_mod.py
py scripts/make_release.py
```

Il risultato è in `build/00040000000B4A00` (la mod) e in `release/` (il pacchetto da distribuire). Prima però servono
gli strumenti del [punto 2](#2-strumenti-esterni).

## 1. Requisiti

- **Windows 10 o 11.** Alcuni strumenti sono `.exe` e due generatori di immagini usano i font di Windows
  (Arial, Segoe UI).
- **Python 3.14** (la versione usata per lo sviluppo) da [python.org](https://www.python.org/downloads/). Durante
  l'installazione spunta *Add python.exe to PATH*.
- **Git**, da [git-scm.com](https://git-scm.com/download/win), oppure scarica il repository come ZIP dal pulsante
  verde **Code** di GitHub.
- Circa **3 GB** liberi su disco.

Le librerie Python si installano con:

```bash
py -m pip install -r requirements.txt
```

## 2. Strumenti esterni

Non sono nel repository per motivi di licenza o di dimensione. Mettili esattamente in queste cartelle:

| Strumento | Dove scaricarlo | Dove metterlo |
|---|---|---|
| **3dstool** 1.2.6 (estrae e ricostruisce le ROM 3DS) | [github.com/dnasdw/3dstool/releases](https://github.com/dnasdw/3dstool/releases) | `tools/3dstool/3dstool.exe` più i file `.txt` dello zip |
| **xdelta3** 3.0.11 x86_64 (crea la patch del pacchetto) | [github.com/jmacd/xdelta-gpl/releases/tag/v3.0.11](https://github.com/jmacd/xdelta-gpl/releases/tag/v3.0.11) | `tools/xdelta3/xdelta3-3.0.11-x86_64.exe` |
| **LaMa** in formato ONNX, `lama_fp32.onnx` (208 MB, ricostruisce lo sfondo sotto le scritte delle insegne) | [huggingface.co/Carve/LaMa-ONNX](https://huggingface.co/Carve/LaMa-ONNX/resolve/main/lama_fp32.onnx) | `tools/models/lama_fp32.onnx` |

Impronta SHA-256 di `lama_fp32.onnx`: `1faef5301d78db7dda502fe59966957ec4b79dd64e16f03ed96913c7a4eb68d6`.

I font delle insegne sono già in `tools/fonts` (licenze in `tools/fonts/LICENZE_FONT.txt`).

## 3. I file del gioco

Servono due file, **decrittati**, ricavati dalla tua console con [GodMode9](https://github.com/d0k3/GodMode9):

| File | Cosa è | Controllo |
|---|---|---|
| ROM `.cci` / `.3ds` | dump della cartuccia giapponese **Ver.1.0** (00040000000B4A00), 256 MB | SHA-1 `55dd4435cd694c8eec13f31a1157b41575d6e0fd` |
| `.cia` | aggiornamento ufficiale **Ver.1.1** (v1056, 0004000E000B4A00), circa 3 MB | lo controlla `prepare.py` |

Con GodMode9 si fa il dump della cartuccia e si crea il CIA dell'aggiornamento installato; entrambi vanno poi
decrittati con l'opzione *Decrypt file*. Una ROM crittata, ridotta (*trimmed*) o di un'altra regione non va bene.

Perché serve anche l'aggiornamento: la patch contiene il codice della Ver.1.1, così funziona con e senza aggiornamento
installato. Dell'aggiornamento si usano solo il codice (`code.bin`) e l'exheader.

## 4. Preparazione

```bash
py scripts/prepare.py "percorso/della/rom.cci" "percorso/dell/aggiornamento.cia"
```

Va eseguito **una volta sola**. Lo script:

1. estrae la ROM in `work/3ds` (intestazioni, codice, romfs);
2. estrae codice ed exheader dell'aggiornamento in `work/v11`;
3. controlla le impronte: se il dump è diverso da quello previsto si ferma e lo dice;
4. estrae gli archivi `.tarc` del gioco in `work/3ds/romfs_x`;
5. converte in PNG le texture originali che i generatori di immagini usano come base (`work/img`, `work/tut`).

Se cambi file di partenza, rifallo con `--force`.

## 5. Compilazione

```bash
py scripts/build_all.py
py scripts/check_mod.py
```

`build_all.py` esegue tutti i passaggi nell'ordine giusto: testi, font, interfaccia, immagini, insegne, rivista,
lavagne, script degli eventi, codice. La prima volta richiede circa **20–25 minuti**, quasi tutti per le insegne, la
rivista e la codifica delle texture. Le volte dopo i generatori lenti riusano una cache e bastano pochi minuti.

`check_mod.py` confronta ogni file della mod con l'originale: struttura degli archivi, allineamenti, dimensioni e
formati delle texture. **Deve dire `problemi: 0`.** Un errore qui di solito vuol dire un crash sulla 3DS vera, anche se
l'emulatore sembra funzionare.

La mod finisce in `build/00040000000B4A00`:

```
build/00040000000B4A00/
├── romfs/           file del gioco modificati (solo quelli cambiati)
├── exefs/code.bin   codice Ver.1.1 tradotto e patchato
└── exheader.bin     exheader adattato al codice nuovo
```

Per cambiare la cartella di uscita (per esempio per scrivere direttamente nella cartella mods di Azahar) crea il file
`local_paths.json` nella radice del progetto, come spiegato in `scripts/paths.py`.

## 6. Provare la mod

**Azahar:** copia la cartella `00040000000B4A00` in `%APPDATA%/Azahar/load/mods/` (in Azahar: tasto destro sul gioco,
*Open Mods Location*) e avvia la ROM giapponese originale. Dopo ogni prova puoi lanciare:

```bash
py scripts/emu_log_check.py
```

Lo script cerca nel log di Azahar le letture da indirizzi non validi. Azahar le ignora, ma sulla 3DS vera fanno
crashare il gioco: se ne trova anche una sola, la modifica va corretta.

**3DS con Luma3DS:** copia il contenuto di `00040000000B4A00` in `SD:/luma/titles/00040000000B4A00/` e attiva
*Enable game patching* nella configurazione di Luma (tieni premuto SELECT all'accensione).

## 7. Creare il pacchetto

```bash
py scripts/make_release.py
```

Crea in `release/` lo zip da distribuire. La versione viene dal file `VERSION`, la ROM di partenza è quella indicata a
`prepare.py`.

```
Tongari Boushi ITA vX.Y/
├── Applica patch.bat              applica la patch e crea la cartella luma
├── Tongari Boushi ITA vX.Y.xdelta differenze fra la ROM originale e quella italiana
├── LEGGIMI.txt, README.txt        istruzioni
└── dati/                          xdelta3, 3dstool, elenco dei file per Luma, licenze
```

Il pacchetto **non contiene file del gioco**: `Applica patch.bat` crea la ROM italiana dalla ROM dell'utente e ne
estrae la cartella `luma` per la 3DS. Prima di creare lo zip, `make_release.py` prova il pacchetto come farebbe un
utente: lancia il `.bat` su una copia e controlla che la ROM e la cartella `luma` ottenute siano identiche, byte per
byte, alla build. La ROM italiana usata per la prova viene poi cancellata.

## Ricompilare dopo una modifica

`build_all.py` accetta due opzioni per non rifare tutto:

```bash
py scripts/build_all.py --from build_text      # da questo passaggio fino alla fine
py scripts/build_all.py --only build_code      # solo i passaggi indicati, separati da virgole
```

Regole da ricordare:

- `gen_labels` svuota la cartella delle immagini generate: dopo averlo eseguito servono tutti i passaggi successivi,
  quindi usa `--from`, non `--only`.
- `build_ui` riscrive interi archivi dell'interfaccia: anche dopo di lui usa `--from build_ui`.
- In caso di dubbio, una compilazione completa è sempre sicura.

Dove modificare le cose (testi, immagini, codice) è spiegato in [architettura.md](architettura.md) e
[traduzione.md](traduzione.md).

## Problemi frequenti

| Messaggio | Causa e soluzione |
|---|---|
| `dump non riconosciuto` | ROM o aggiornamento diversi da quelli previsti. Servono la cartuccia giapponese Ver.1.0 e l'aggiornamento v1056, decrittati. |
| `il CIA non contiene un NCCH leggibile` | Il CIA è ancora crittato: decrittalo con GodMode9. |
| `manca ...3dstool.exe` / `xdelta3` | Strumento non nella cartella indicata al [punto 2](#2-strumenti-esterni). |
| `prova del pacchetto fallita` | Il `.bat` non ricrea esattamente la build: il messaggio elenca i file diversi. Succede se la mod è cambiata durante `make_release` o se la ROM di partenza non è quella di `prepare.py`. |
| errore su `lama_fp32.onnx` | Modello mancante o incompleto: controlla l'impronta SHA-256. |
| `ModuleNotFoundError` | Librerie mancanti: `py -m pip install -r requirements.txt`. |
| `problemi: N` da `check_mod.py` | Un file generato non rispetta il formato originale: il messaggio indica quale. Non distribuire la mod finché non torna a 0. |
