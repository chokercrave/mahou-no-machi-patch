# Tongari Boushi to Mahou no Machi — Patch italiana

*[English below](#english)*

Traduzione italiana completa di **Tongari Boushi to Mahou no Machi** (とんがりボウシと魔法の町, Konami, 2012), il
seguito per Nintendo 3DS di *Enchanted Folk and the School of Wizardry*, uscito solo in Giappone. Funziona su
emulatore (Azahar) e su 3DS con Luma3DS.

Il repository contiene **gli strumenti e i testi** della traduzione, non il gioco: nessun file di Nintendo o Konami è
incluso. Per giocare serve la propria copia del gioco.

> **▶ [Applica la patch online](https://darkenedforest.github.io/tongari-boushi-to-oshare-na-mahou-tsukai-archive/patches/#3ds)**, direttamente nel browser: c'è il patcher per **Azahar** e il patcher per **3DS** (Luma3DS). Niente da installare, la ROM resta sul tuo computer.

## Cosa contiene (rispetto al gioco originale)

- **Tutto in italiano:** dialoghi, menu, oggetti, nomi, insegne dei negozi, lavagne delle lezioni, la rivista
  *Spell & Spill*, titoli e crediti, ridisegnati nello stile dell'originale. Dialoghi al femminile se giochi con una
  ragazza.
- **Adattato all'italiano:** dialoghi su 3 righe, nomi interi di vestiti e accessori, orologio a 24 ore, tastiera del
  nome che parte dalle lettere (ABC) e accetta i nomi propri che il filtro rifiutava, avvio diretto al titolo.
- **Più comodo da giocare:**
  - negozi e servizi aperti 24 ore su 24, lezioni a qualsiasi ora;
  - fidanzamento e amicizia con chiunque, di qualsiasi sesso;
  - viaggio rapido dalla Mappa del villaggio;
  - tieni premuto **B** e il testo compare subito;
  - un menu **Opzioni**, chiesto ai professori o a Reginaldo: soldi infiniti, legami stabili, merce nuova nei negozi,
    incantesimi che non consumano i materiali.
- **Una sola patch** per il gioco base Ver.1.0 e per l'aggiornamento Ver.1.1. I salvataggi restano compatibili.

Come funziona ogni cosa, e come si usa in partita: **[docs/funzionalita.md](docs/funzionalita.md)**. Le guide sono anche sul [sito di Darkened Forest](https://darkenedforest.github.io/tongari-boushi-to-oshare-na-mahou-tsukai-archive/3ds/).

## Installazione

### Online, nel browser (consigliato)

Apri la **[pagina della patch sul sito di Darkened Forest](https://darkenedforest.github.io/tongari-boushi-to-oshare-na-mahou-tsukai-archive/patches/#3ds)**, scegli la ROM giapponese **decrittata** (`.cci` o `.3ds`) e il tuo sistema:

- **Patcher per Azahar** (*Azahar emulator*): ottieni `Tongari Boushi ITA vX.Y.3ds`, da aprire con Azahar.
- **Patcher per 3DS** (*3DS (Luma3DS)*): ottieni `Tongari Boushi ITA vX.Y - 3DS luma.zip`. Apri lo zip e copia la cartella `luma` nella radice della scheda SD (vedi [Sulla 3DS](#sulla-3ds)).

Tutto avviene sul tuo computer: la ROM non viene caricata da nessuna parte.

### Offline, con Windows

Scarica l'ultima versione dalla pagina **[Releases](../../releases)** ed estrai lo zip.

1. Metti nella cartella estratta la ROM giapponese **decrittata** del gioco (`.cci` o `.3ds`), accanto ad
   `Applica patch.bat`.
2. Avvia `Applica patch.bat`. Vengono creati:
   - `Tongari Boushi ITA vX.Y.3ds`, la ROM in italiano da aprire con **Azahar**;
   - la cartella `luma`, per la **3DS con Luma3DS**.

### Sulla 3DS

Se hai una versione precedente cancella `SD:/luma/titles/00040000000B4A00`, poi copia la cartella
`luma` nella radice della scheda SD. Tieni premuto SELECT all'accensione e attiva *Enable game patching*. Funziona con
la cartuccia e con il gioco installato.

Il primo avvio dopo l'installazione è più lento: aspetta senza spegnere la console.

## Documentazione

| Guida | Per chi |
|---|---|
| [Funzionalità](docs/funzionalita.md) | Chi gioca: tutte le novità e come usarle |
| [Compilare la patch](docs/compilare.md) | Chi vuole ricostruire la patch dalla propria copia del gioco |
| [Architettura](docs/architettura.md) | Chi vuole modificare la patch: build, formati, regole per la 3DS |
| [Guida alla traduzione](docs/traduzione.md) | Chi vuole correggere i testi |
| [Note tecniche](docs/note_tecniche.md) | Indirizzi, variabili e strutture del gioco scoperti durante il lavoro |
| [Registro delle versioni](CHANGELOG.md) | Cosa è cambiato in ogni versione |

Compilare in breve, dopo aver installato gli [strumenti esterni](docs/compilare.md#2-strumenti-esterni):

```bash
py -m pip install -r requirements.txt
py scripts/prepare.py "rom.cci" "aggiornamento_1.1.cia"
py scripts/build_all.py
```

## Segnalare un problema o contribuire

Apri una segnalazione nella pagina **[Issues](../../issues)**: descrivi dove ti trovavi nel gioco, se giochi su
Azahar o su 3DS, e allega una foto dello schermo se puoi.

Correzioni e miglioramenti sono benvenuti come **pull request**: come prepararle e provarle è spiegato in
[CONTRIBUTING.md](CONTRIBUTING.md).

## Ringraziamenti

- **Darkened Forest**, per il [Field Guide dell'archivio di Tongari Boushi](https://darkenedforest.github.io/tongari-boushi-to-oshare-na-mahou-tsukai-archive/field-guide/): per il permesso di usare quei dati, per le idee, per l'aiuto offerto e le informazioni condivise.
- **[Inochi-Pm](https://github.com/InochiPM)**, il cui [thread su GBAtemp](https://gbatemp.net/threads/translation-tongari-boushi-to-mahou-no-machi-3ds.555312/) ha ispirato questa traduzione; per le idee, per l'aiuto offerto e le informazioni condivise.
- I font delle insegne sono Google Fonts liberi (licenze OFL 1.1 e Apache 2.0, vedi `tools/fonts`).

## Licenza

Il codice e i testi di questo repository sono distribuiti con licenza **MIT** (vedi [LICENSE](LICENSE)). La licenza non
riguarda il gioco e i suoi file, che appartengono a Konami, né i font in `tools/fonts`, che hanno le proprie licenze
libere (vedi `tools/fonts/LICENZE_FONT.txt`).
*Tongari Boushi* è un marchio di Konami; Nintendo 3DS è un marchio di Nintendo. Questo è un progetto amatoriale non
ufficiale, senza scopo di lucro e non affiliato con Konami o Nintendo.

---

## English

Complete Italian translation of **Tongari Boushi to Mahou no Machi** (Konami, 2012), the Nintendo 3DS sequel to
*Enchanted Folk and the School of Wizardry*, released in Japan only. It works on emulator (Azahar) and on 3DS with
Luma3DS.

This repository contains **the tools and the texts** of the translation, not the game: no Nintendo or Konami files are
included. You need your own copy of the game.

> **▶ [Patch online](https://darkenedforest.github.io/tongari-boushi-to-oshare-na-mahou-tsukai-archive/patches/#3ds)**, right in your browser: there is a patcher for **Azahar** and a patcher for **3DS** (Luma3DS). Nothing to install, and your ROM stays on your computer.

### What it includes (compared to the original game)

- **Everything in Italian:** dialogue, menus, items, names, shop signs, lesson blackboards, the *Spell & Spill*
  magazine, titles and credits, redrawn in the original style. Feminine dialogue when playing as a girl.
- **Adapted for Italian:** 3-line dialogue boxes, full clothing and accessory names, 24-hour clock, a name keyboard
  that opens on Latin letters (ABC) and accepts proper names the word filter used to reject, boot straight to the title.
- **Quality-of-life improvements:**
  - shops and services open 24/7, lessons at any hour;
  - dating and best friendship with anyone, of any sex;
  - fast travel from the village Map;
  - hold **B** and text appears instantly;
  - an **Options** menu, asked to the teachers or to Reginaldo: infinite money, stable bonds, new stock in shops,
    spells that don't use up materials.
- **A single patch** for the base game Ver.1.0 and the Ver.1.1 update. Saves stay compatible.

How every feature works and how to use it in game: **[docs/en/features.md](docs/en/features.md)**. The guides are also on [Darkened Forest's site](https://darkenedforest.github.io/tongari-boushi-to-oshare-na-mahou-tsukai-archive/3ds/).

### Installation

#### Online, in your browser (recommended)

Open the **[patch page on Darkened Forest's site](https://darkenedforest.github.io/tongari-boushi-to-oshare-na-mahou-tsukai-archive/patches/#3ds)**, choose your **decrypted** Japanese ROM (`.cci` or `.3ds`) and your system:

- **Azahar patcher** (*Azahar emulator*): you get `Tongari Boushi ITA vX.Y.3ds`, to open with Azahar.
- **3DS patcher** (*3DS (Luma3DS)*): you get `Tongari Boushi ITA vX.Y - 3DS luma.zip`. Open the zip and copy the `luma` folder to the root of the SD card (see [On 3DS](#on-3ds)).

Everything runs on your computer: the ROM is not uploaded anywhere.

#### Offline, on Windows

Download the latest version from the **[Releases](../../releases)** page and extract the zip.

1. Put your **decrypted** Japanese ROM (`.cci` or `.3ds`) in the extracted folder, next to `Applica patch.bat`.
2. Run `Applica patch.bat`. It creates:
   - `Tongari Boushi ITA vX.Y.3ds`, the Italian ROM to open with **Azahar**;
   - the `luma` folder, for **3DS with Luma3DS**.

#### On 3DS

If you have a previous version delete `SD:/luma/titles/00040000000B4A00`, then copy the `luma` folder to
the root of the SD card. Hold SELECT at boot and enable *Enable game patching*. It works with the cartridge and with the
installed game.

The first launch after installing is slower: wait without turning the console off.

### Documentation

| Guide | For |
|---|---|
| [Features](docs/en/features.md) | Players: every new feature and how to use it |
| [Building](docs/en/building.md) | Rebuilding the patch from your own copy of the game |
| [Architecture](docs/en/architecture.md) | Modifying the patch: build, formats, rules for real hardware |
| [Technical notes](docs/en/technical_notes.md) | Addresses, variables and game structures found during the work |
| [Changelog](CHANGELOG.md) | What changed in each version |

The translation style guide is in Italian (`docs/traduzione.md`).

### Reporting a problem or contributing

Open an issue on the **[Issues](../../issues)** page: say where you were in the game, whether you play on Azahar or
3DS, and attach a screenshot if you can.

Fixes and improvements are welcome as **pull requests**: how to prepare and test them is explained in
[CONTRIBUTING.md](CONTRIBUTING.md).

### Credits

- **Darkened Forest**, for the [Tongari Boushi archive Field Guide](https://darkenedforest.github.io/tongari-boushi-to-oshare-na-mahou-tsukai-archive/field-guide/): for permission to use that data, for the ideas, the help offered and the information shared.
- **[Inochi-Pm](https://github.com/InochiPM)**, whose [GBAtemp thread](https://gbatemp.net/threads/translation-tongari-boushi-to-mahou-no-machi-3ds.555312/) inspired this translation; for the ideas, the help offered and the information shared.
- The sign fonts are free Google Fonts (OFL 1.1 and Apache 2.0 licenses, see `tools/fonts`).

### License

The code and texts in this repository are released under the **MIT** license (see [LICENSE](LICENSE)). The license
does not cover the game and its files, which belong to Konami, nor the fonts in `tools/fonts`, which keep their own free
licenses (see `tools/fonts/LICENZE_FONT.txt`).
*Tongari Boushi* is a trademark of Konami; Nintendo 3DS is a trademark of Nintendo. This is an unofficial,
non-commercial fan project, not affiliated with Konami or Nintendo.
