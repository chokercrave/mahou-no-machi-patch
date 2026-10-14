# Contribuire / Contributing

*[English below](#english)*

Correzioni e miglioramenti sono benvenuti: un errore di battitura, una frase che suona male, un'insegna da ritoccare,
un bug del codice.

## Segnalare un problema

Apri una **Issue** e scegli il modello adatto. Indica dove ti trovavi nel gioco, se giochi su Azahar o su 3DS e, se
puoi, allega una foto dello schermo.

## Proporre una modifica (pull request)

1. Fai un **fork** del repository e crea un ramo per la modifica.
2. Prepara il gioco e compila la patch come spiegato in [docs/compilare.md](docs/compilare.md).
3. Fai la modifica. Dove si trova ogni cosa è spiegato in
   [docs/architettura.md](docs/architettura.md#dove-modificare-cosa); per i testi segui
   [docs/traduzione.md](docs/traduzione.md).
4. Ricompila e controlla:
   - `py scripts/check_mod.py` deve dire **`problemi: 0`**;
   - prova la modifica in gioco. Su Azahar, dopo la prova, `py scripts/emu_log_check.py` deve dire 0 accessi non
     mappati: Azahar perdona errori che sulla 3DS vera bloccano il gioco.
5. Apri la pull request e compila il modello: cosa cambia, come l'hai provato.

**Non includere mai** ROM, file estratti dal gioco o file generati dalla build (`build/`, `release/`, `work/3ds/`…).
Il `.gitignore` li esclude già: se `git status` te ne mostra uno, non aggiungerlo.

### Correggere un testo senza compilare

Per una correzione piccola di un dialogo puoi anche modificare il file `.it.tsv` direttamente dal sito di GitHub (icona
della matita) e aprire la pull request da lì. Rispetta i segnaposto (`<P>`, `<X1>`, `<c4>…</c>`) e la lunghezza indicati in
[docs/traduzione.md](docs/traduzione.md): la modifica verrà provata prima di entrare nella patch.

### Licenza

Contribuendo accetti che il tuo contributo sia distribuito con la stessa licenza del progetto ([MIT](LICENSE)).

---

## English

Fixes and improvements are welcome: a typo, an awkward line, a sign to touch up, a code bug. The translation is in
Italian, but code, tooling and documentation contributions are welcome in English too.

### Reporting a problem

Open an **Issue** and pick the matching template. Say where you were in the game, whether you play on Azahar or 3DS
and, if you can, attach a screenshot.

### Proposing a change (pull request)

1. **Fork** the repository and create a branch for your change.
2. Set up the game and build the patch as explained in [docs/en/building.md](docs/en/building.md).
3. Make your change. Where everything lives is explained in
   [docs/en/architecture.md](docs/en/architecture.md#where-to-change-what).
4. Rebuild and check:
   - `py scripts/check_mod.py` must print **`problemi: 0`**;
   - test the change in game. On Azahar, after testing, `py scripts/emu_log_check.py` must report 0 unmapped accesses:
     Azahar forgives errors that freeze a real 3DS.
5. Open the pull request and fill in the template: what changes, how you tested it.

**Never include** ROMs, files extracted from the game or build outputs (`build/`, `release/`, `work/3ds/`…). The
`.gitignore` already excludes them: if `git status` shows one, don't add it.

### License

By contributing you agree that your contribution is distributed under the project's license ([MIT](LICENSE)).
