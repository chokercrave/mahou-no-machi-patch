"""Pacchetto di rilascio, senza file del gioco: patch xdelta (ROM giapponese decrittata -> ROM italiana) + .bat che
patcha la ROM messa nella stessa cartella e ne ricava la cartella Luma3DS per la 3DS (strumenti in dati/).
Il pacchetto viene provato come farebbe un utente (check_bat).
  python make_release.py        -> release/Tongari Boushi ITA v<VERSION>/ e lo .zip accanto
Serve la ROM italiana di make_rom.py (la crea se manca: la mod deve essere gia' costruita con build_all.py)."""
import hashlib, os, shutil, subprocess, sys, zipfile

sys.path.insert(0, os.path.dirname(__file__))
import make_rom

ROOT = make_rom.ROOT
OUT = make_rom.OUT
MOD = make_rom.MOD
TID = '00040000000B4A00'
# ROM giapponese originale (sorgente della xdelta): quella indicata a prepare.py, altrimenti il percorso storico
_ROM_PATH = os.path.join(ROOT, 'work', 'rom_path.txt')
ORIG = (open(_ROM_PATH, encoding='utf-8').read().strip() if os.path.exists(_ROM_PATH) else
        os.path.join(ROOT, 'Tongari Boushi to Mahou no Machi (Japan)', 'Tongari Boushi to Mahou no Machi (Japan).cci'))
ORIG_SHA1 = '55dd4435cd694c8eec13f31a1157b41575d6e0fd'
XDELTA = os.path.join(ROOT, 'tools', 'xdelta3', 'xdelta3-3.0.11-x86_64.exe')
TOOL3DS = os.path.join(ROOT, 'tools', '3dstool')

LICENSES = '''Strumenti inclusi nella cartella "dati" / tools included in the "dati" folder
==============================================================================

xdelta3.exe   xdelta 3.0.11 di Joshua MacDonald, licenza GNU GPL v2.
              Sorgente / source: https://github.com/jmacd/xdelta-gpl/releases/tag/v3.0.11
3dstool.exe   3dstool 1.2.6 di dnasdw, licenza MIT.
              Sorgente / source: https://github.com/dnasdw/3dstool

luma_files.txt, exheader.xdelta e code.ips sono dati della patch / are patch data.
'''

BAT = r'''@echo off
setlocal
cd /d "%~dp0"
title Patch italiana - Tongari Boushi to Mahou no Machi
set "PATCH=Tongari Boushi ITA v{ver}.xdelta"
set "OUT=Tongari Boushi ITA v{ver}.3ds"
set "D=%~dp0dati\"
set "T=%~dp0_tongari_patch_temp"
set "L=%~dp0luma\titles\{tid}"
echo.
echo  Tongari Boushi to Mahou no Machi - patch italiana v{ver}
echo  ------------------------------------------------------
echo.
if not exist "%PATCH%" goto nopatch
if not exist "%D%3dstool.exe" goto nopatch
set "SRC="
for %%F in (*.cci) do if not defined SRC set "SRC=%%F"
if defined SRC goto found
for %%F in (*.3ds) do call :pick "%%F"
if not defined SRC goto nosrc
:found
echo  ROM originale / original ROM: %SRC%
echo  1/2 Applico la patch / applying the patch...
"%D%xdelta3.exe" -d -f -s "%SRC%" "%PATCH%" "%OUT%"
if errorlevel 1 goto fail
echo  2/2 Creo la cartella luma per la 3DS / creating the luma folder for 3DS...
if exist "%T%" rmdir /s /q "%T%"
if exist "%L%" rmdir /s /q "%L%"
mkdir "%T%"
"%D%3dstool.exe" -xt0f cci "%T%\p0.cxi" "%OUT%" >nul || goto lumafail
"%D%3dstool.exe" -xtf cxi "%T%\p0.cxi" --exh "%T%\exh.bin" --exefs "%T%\exefs.bin" --romfs "%T%\romfs.bin" >nul || goto lumafail
del "%T%\p0.cxi"
"%D%3dstool.exe" -xtfu exefs "%T%\exefs.bin" --exefs-dir "%T%\exefs" >nul || goto lumafail
"%D%3dstool.exe" -xtf romfs "%T%\romfs.bin" --romfs-dir "%T%\romfs" >nul || goto lumafail
set "ERR="
for /f "usebackq delims=" %%P in ("%D%luma_files.txt") do call :copyone "%%P"
if defined ERR goto lumafail
"%D%xdelta3.exe" -d -f -s "%T%\exh.bin" "%D%exheader.xdelta" "%L%\exheader.bin" || goto lumafail
copy /y "%T%\exefs\code.bin" "%L%\code.bin" >nul || goto lumafail
copy /y "%D%code.ips" "%L%\code.ips" >nul || goto lumafail
rmdir /s /q "%T%"
echo.
echo  Fatto! / Done!
echo    %OUT%   -^> Azahar
echo    luma\   -^> scheda SD della 3DS / 3DS SD card
echo  La ROM originale non e' stata modificata / the original ROM is untouched.
goto end
:copyone
for %%Q in ("%L%\romfs\%~1") do if not exist "%%~dpQ" mkdir "%%~dpQ"
copy /y "%T%\romfs\%~1" "%L%\romfs\%~1" >nul || set "ERR=1"
exit /b 0
:pick
echo %~n1| findstr /b /c:"Tongari Boushi ITA" >nul && exit /b 0
if not defined SRC set "SRC=%~1"
exit /b 0
:nopatch
echo  ERRORE: mancano file del pacchetto ("%PATCH%" o la cartella "dati").
echo  ERROR: package files are missing ("%PATCH%" or the "dati" folder).
goto end
:nosrc
echo  ERRORE: nessuna ROM trovata.
echo  Metti in questa cartella la ROM giapponese del gioco, file .cci o .3ds decrittato,
echo  poi avvia di nuovo questo file.
echo.
echo  ERROR: no ROM found. Put the Japanese ROM (.cci or decrypted .3ds) in this
echo  folder, then run this file again.
goto end
:fail
if exist "%OUT%" del "%OUT%"
echo.
echo  ERRORE: la patch non si applica a questa ROM.
echo  Serve la ROM giapponese DECRITTATA, non modificata e non ridotta:
echo  "Tongari Boushi to Mahou no Machi (Japan)", 256 MB, SHA-1 {sha1}
echo.
echo  ERROR: the patch does not apply to this ROM. You need the DECRYPTED,
echo  unmodified, untrimmed Japanese ROM (256 MB, SHA-1 above).
goto end
:lumafail
if exist "%T%" rmdir /s /q "%T%"
if exist "%L%" rmdir /s /q "%L%"
echo.
echo  ERRORE: la ROM italiana e' pronta, ma non sono riuscito a creare la cartella luma
echo  (spazio su disco esaurito?). Libera spazio e riprova.
echo  ERROR: the Italian ROM is ready, but the luma folder could not be created
echo  (disk full?). Free some space and try again.
:end
echo.
pause
'''

README = '''Tongari Boushi to Mahou no Machi - patch italiana v{ver}
=========================================================

Traduzione italiana completa del gioco per Nintendo 3DS (Konami, 2012, solo Giappone),
seguito di "Enchanted Folk and the School of Wizardry" (DS).
Funziona su emulatore (Azahar) e su 3DS con Luma3DS.

INSTALLAZIONE
  1. Metti la ROM giapponese del gioco in questa cartella, accanto a "Applica patch.bat".
     Deve essere la ROM decrittata, non modificata (con la 3DS puoi ricavarla dalla tua
     cartuccia con GodMode9):
       Tongari Boushi to Mahou no Machi (Japan).cci  - 256 MB
       SHA-1 {sha1}
  2. Avvia "Applica patch.bat". Dopo qualche secondo trovi in questa cartella:
       "Tongari Boushi ITA v{ver}.3ds"  la ROM in italiano, da aprire con Azahar
       "luma"                          la cartella per la 3DS con Luma3DS
  La ROM originale resta intatta.
  Senza Windows o senza scaricare niente: puoi applicare la patch anche nel browser (ROM per
  Azahar o cartella luma per la 3DS), sul sito di Darkened Forest: https://darkenedforest.github.io/tongari-boushi-to-oshare-na-mahou-tsukai-archive/patches/#3ds

EMULATORE (Azahar): apri "Tongari Boushi ITA v{ver}.3ds".

3DS CON LUMA3DS (funziona con la cartuccia e con il gioco installato)
  1. Se hai una versione precedente della patch, cancella prima la cartella
     SD:/luma/titles/{tid}. Poi copia la cartella "luma" nella radice della scheda SD
     (unisci le cartelle se "luma" esiste gia').
     Risultato: SD:/luma/titles/{tid}/romfs, code.bin, exheader.bin, code.ips
  2. Tieni premuto SELECT all'accensione per aprire la configurazione di Luma e attiva
     "Enable game patching" (in alcune versioni: "Enable loading external FIRMs and modules").
  3. Avvia il gioco: e' in italiano. Il primo avvio dopo l'installazione e' piu' lento
     (il gioco prepara i suoi dati): aspetta e non spegnere la console.
  Per tornare al giapponese basta rinominare o togliere la cartella {tid}.

Salvataggi: compatibili con quelli del gioco originale (la patch non cambia il formato).

VERSIONE DEL GIOCO: la patch contiene gia' l'aggiornamento ufficiale Ver.1.1 (Luma
carica al suo posto il codice 1.1 tradotto), quindi funziona sia col gioco base Ver.1.0
sia con l'aggiornamento Ver.1.1 installato: non c'e' niente da installare o togliere.
Anche la .3ds creata dalla patch e' gia' Ver.1.1: non installarci sopra l'aggiornamento.

COSA CONTIENE LA PATCH (rispetto al gioco originale)
  Traduzione
  - Tutti i testi in italiano: dialoghi, menu, oggetti, vestiti, ricette e nomi dei
    personaggi (con i nomi della versione europea del primo gioco per DS, dove esistono).
  - Insegne dei negozi, lavagne delle lezioni, rivista "Spell & Spill", titoli, crediti
    e avvisi ridisegnati in italiano, nello stile dell'originale.
  - Dialoghi al femminile se giochi con una ragazza.
  - Dialoghi su 3 righe; nomi interi di vestiti e accessori; orologio a 24 ore.
  - Tastiera del nome che si apre sulle lettere (ABC); nomi propri prima rifiutati
    dal filtro delle parole (Massimo, Cassandra...) ora accettati.
  - Il gioco parte subito dalla schermata del titolo, senza loghi.
  Miglioramenti di gioco
  - Negozi e servizi aperti 24 ore su 24; lezioni a qualsiasi ora.
  - Fidanzamento e amicizia con chiunque, di qualsiasi sesso: regala il Bouquet
    d'invito e scegli Amore o Amicizia.
  - Viaggio rapido: sulla Mappa del villaggio tocca un luogo e poi tocca di nuovo la
    stessa icona: sparisci in una nuvola di fumo e ricompari li'.
  - Tieni premuto B e il testo dei dialoghi compare subito.
  - Menu "Opzioni", da chiedere ai professori (anche davanti all'aula) o a Reginaldo,
    il capo del dormitorio:
      Viaggio rapido   acceso/spento
      Soldi infiniti   il portafoglio non scende mai
      Legami stabili   amore e amicizia non calano se non vedi qualcuno
      Merce nuova      rifornisce subito tutti i negozi
      Riusa materiali  gli incantesimi non consumano l'oggetto (torna nella borsa)
  Dettagli su ogni funzione: docs/funzionalita.md su
  https://github.com/chokercrave/mahou-no-machi-patch

PROBLEMI NOTI
  - Il nome del negozio ha al massimo 12 caratteri.
  - Alcuni nomi di oggetti e piatti sono ancora abbreviati.
  - Poche texture minori sono ancora in giapponese (alcuni menu, posta, mappa, qualche
    pagina della rivista).
'''

README_EN = '''Tongari Boushi to Mahou no Machi - Italian patch v{ver}
=======================================================

Complete Italian translation of the Nintendo 3DS game (Konami, 2012, Japan only),
the sequel to "Enchanted Folk and the School of Wizardry" (DS).
Works on emulator (Azahar) and on a real 3DS with Luma3DS.

INSTALLATION
  1. Put the Japanese ROM of the game in this folder, next to "Applica patch.bat".
     It must be the decrypted, unmodified ROM (on a 3DS you can dump it from your
     cartridge with GodMode9):
       Tongari Boushi to Mahou no Machi (Japan).cci  - 256 MB
       SHA-1 {sha1}
  2. Run "Applica patch.bat" (= "Apply patch"). After a few seconds this folder contains:
       "Tongari Boushi ITA v{ver}.3ds"  the Italian ROM, to open with Azahar
       "luma"                          the folder for 3DS with Luma3DS
  Your original ROM is left untouched.
  Not on Windows? Apply the .xdelta file with any xdelta3 tool (e.g. Delta Patcher):
    xdelta3 -d -s "<original ROM>" "Tongari Boushi ITA v{ver}.xdelta" "Tongari Boushi ITA v{ver}.3ds"
  You can also patch in your browser (ROM for Azahar or luma folder for 3DS) on Darkened Forest's site:
    https://darkenedforest.github.io/tongari-boushi-to-oshare-na-mahou-tsukai-archive/patches/#3ds

EMULATOR (Azahar): open "Tongari Boushi ITA v{ver}.3ds".

3DS WITH LUMA3DS (works with the cartridge and with the installed game)
  1. If you have an older version of the patch, delete the folder
     SD:/luma/titles/{tid} first. Then copy the "luma" folder to the root of the SD
     card (merge the folders if "luma" already exists).
     Result: SD:/luma/titles/{tid}/romfs, code.bin, exheader.bin, code.ips
  2. Hold SELECT while powering on to open the Luma configuration and enable
     "Enable game patching" (in some versions: "Enable loading external FIRMs and modules").
  3. Start the game: it is in Italian. The first launch after installing is slower
     (the game sets up its data): wait and don't turn off the console.
  To go back to Japanese, rename or remove the {tid} folder.

Saves: compatible with those of the original game (the save format is unchanged).

GAME VERSION: the patch already contains the official Ver.1.1 update (Luma loads
the patched 1.1 code in its place), so it works with the base game Ver.1.0 and with
the Ver.1.1 update installed alike: nothing to install or uninstall.
The patched .3ds is also Ver.1.1: do not install the update on top of it.

WHAT THE PATCH INCLUDES (compared to the original game)
  Translation
  - Every text in Italian: dialogue, menus, items, clothes, recipes and character
    names (using the names of the European release of the first DS game, where they exist).
  - Shop signs, lesson blackboards, the "Spell & Spill" magazine, titles, credits and
    notices redrawn in Italian, in the original style.
  - Feminine dialogue when you play as a girl.
  - 3-line dialogue boxes; full clothing and accessory names; 24-hour clock.
  - Name keyboard opens on Latin letters (ABC); proper names rejected by the word
    filter (Massimo, Cassandra...) are now accepted.
  - The game starts straight at the title screen, without logos.
  Gameplay improvements
  - Shops and services open 24/7; lessons at any hour.
  - Dating and best friendship with anyone, of any gender: give the Invitation
    Bouquet and choose Love or Friendship.
  - Fast travel: on the village Map tap a place, then tap the same icon again: you
    vanish in a puff of smoke and reappear there.
  - Hold B and dialogue text appears instantly.
  - "Options" menu, asked to the teachers (also in front of the classroom) or to
    Reginaldo, the dorm head:
      Fast travel      on/off
      Infinite money   your wallet never goes down
      Stable bonds     love and friendship don't drop when you don't see someone
      New stock        restocks every shop at once
      Reuse materials  spells don't use up the held item (it goes back to the bag)
  Details on every feature: docs/en/features.md at
  https://github.com/chokercrave/mahou-no-machi-patch

KNOWN ISSUES
  - The shop name is limited to 12 characters.
  - Some item and dish names are still abbreviated.
  - A few minor textures are still in Japanese (some menus, mail, map, a few
    magazine pages).
'''


def sha1(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def check_bat(pkg, rom, ver, files):
    """prova il pacchetto come un utente: copia + ROM originale, Applica patch.bat, confronto con la mod"""
    test = os.path.join(OUT, '_prova_pacchetto')
    if os.path.isdir(test):
        shutil.rmtree(test)
    shutil.copytree(pkg, test)
    # una cartella luma gia' esistente (pacchetto estratto nella radice della SD): il .bat non deve toccarne il resto
    keep = {os.path.join(test, 'luma', 'config.ini'): b'config', os.path.join(test, 'luma', 'titles', '0004000000123400', 'x'): b'x'}
    for p, data in keep.items():
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'wb').write(data)
    src = os.path.join(test, 'Tongari Boushi to Mahou no Machi (Japan).cci')
    try:
        os.link(ORIG, src)                      # stesso disco: nessuna copia da 256 MB
    except OSError:
        shutil.copyfile(ORIG, src)
    # percorso completo: con NoDefaultCurrentDirectoryInExePath cmd non cerca nella cartella corrente
    r = subprocess.run(['cmd', '/c', 'call', os.path.join(test, 'Applica patch.bat')], cwd=test, stdin=subprocess.DEVNULL, capture_output=True,
                       text=True, encoding='cp850', errors='replace')
    lt = os.path.join(test, 'luma', 'titles', TID)
    same = lambda a, b: os.path.exists(a) and open(a, 'rb').read() == open(b, 'rb').read()
    bad = [f for f in files if not same(os.path.join(lt, 'romfs', f), os.path.join(MOD, 'romfs', f))]
    bad += [f for f, b in (('code.bin', os.path.join(MOD, 'exefs', 'code.bin')),
                           ('exheader.bin', os.path.join(MOD, 'exheader.bin'))) if not same(os.path.join(lt, f), b)]
    if not same(os.path.join(lt, 'code.ips'), os.path.join(pkg, 'dati', 'code.ips')):
        bad.append('code.ips')
    out3ds = os.path.join(test, f'Tongari Boushi ITA v{ver}.3ds')
    if not os.path.exists(out3ds) or sha1(out3ds) != sha1(rom):
        bad.append('ROM .3ds')
    bad += [os.path.relpath(p, test) for p, data in keep.items() if not os.path.exists(p) or open(p, 'rb').read() != data]
    extra = sorted(set(os.listdir(test)) - set(os.listdir(pkg)) - {os.path.basename(src), os.path.basename(out3ds), 'luma'})
    shutil.rmtree(test)
    if bad or extra:
        sys.exit(f"prova del pacchetto fallita: diversi {bad[:10]}, file in piu' {extra}\n{r.stdout[-2000:]}")
    print(f'prova del pacchetto: Applica patch.bat -> ROM identica, luma identica alla mod ({len(files)} file romfs)')


def main():
    ver = open(os.path.join(ROOT, 'VERSION'), encoding='utf-8').read().strip()
    rom = os.path.join(OUT, f'Tongari Boushi ITA v{ver}.3ds')
    make_rom.main()                 # ROM italiana solo come passaggio intermedio per la xdelta (il pacchetto non contiene la ROM)
    assert sha1(ORIG) == ORIG_SHA1, 'ROM originale diversa da quella attesa'
    pkg = os.path.join(OUT, f'Tongari Boushi ITA v{ver}')
    if os.path.isdir(pkg):
        shutil.rmtree(pkg)
    os.makedirs(pkg)
    patch = os.path.join(pkg, f'Tongari Boushi ITA v{ver}.xdelta')
    # finestra sorgente grande quanto la ROM (256 MB): trova i blocchi uguali anche lontani -> patch piccola
    # -A: niente intestazione con i nomi dei file (conterrebbe i percorsi completi del PC che crea la patch)
    # -S none: niente compressione secondaria (lzma), che RomPatcher.js (patcher nel browser del sito) non legge;
    # lo zip del pacchetto comprime comunque
    r = subprocess.run([XDELTA, '-e', '-9', '-f', '-A', '-S', 'none', '-B', str(1 << 28), '-s', ORIG, rom, patch],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(f'xdelta3 fallito:\n{r.stdout}\n{r.stderr}')
    # prova: la patch ricostruisce esattamente la ROM italiana
    test = os.path.join(OUT, '_verifica.3ds')
    r = subprocess.run([XDELTA, '-d', '-f', '-B', str(1 << 28), '-s', ORIG, patch, test], capture_output=True, text=True)
    ok = r.returncode == 0 and sha1(test) == sha1(rom)
    if os.path.exists(test):
        os.remove(test)
    if not ok:
        sys.exit(f'verifica della patch fallita\n{r.stderr}')
    for name, text in (('Applica patch.bat', BAT), ('LEGGIMI.txt', README), ('README.txt', README_EN)):
        body = text.format(ver=ver, sha1=ORIG_SHA1, tid=TID).replace('\n', '\r\n')
        open(os.path.join(pkg, name), 'w', encoding='cp1252' if name.endswith('.txt') else 'ascii', newline='').write(body)
    # Niente file del gioco nel pacchetto: il .bat ricava la cartella Luma3DS dalla ROM italiana appena creata.
    # luma/titles/<TID>: romfs (solo i file della mod, elenco luma_files.txt) + code.bin 1.1 patchato (dall'exefs della
    # ROM) + exheader 1.1 (la ROM ha quello ibrido di make_rom: exheader.xdelta lo riporta a quello della mod) +
    # code.ips vuoto, che sovrascrive quello delle versioni precedenti (Luma lo applicherebbe sopra code.bin)
    assert os.path.exists(os.path.join(MOD, 'exefs', 'code.bin')), 'serve la build unica 1.0/1.1 (code.bin + exheader)'
    data = os.path.join(pkg, 'dati')
    os.makedirs(data)
    shutil.copyfile(XDELTA, os.path.join(data, 'xdelta3.exe'))
    for f in ('3dstool.exe', 'ignore_3dstool.txt'):
        shutil.copyfile(os.path.join(TOOL3DS, f), os.path.join(data, f))
    open(os.path.join(data, 'LICENZE.txt'), 'w', encoding='cp1252', newline='\r\n').write(LICENSES)
    romfs = os.path.join(MOD, 'romfs')
    files = sorted(os.path.relpath(os.path.join(dp, f), romfs) for dp, _, fs in os.walk(romfs) for f in fs)
    open(os.path.join(data, 'luma_files.txt'), 'w', encoding='ascii', newline='\r\n').write('\n'.join(files) + '\n')
    tmp = os.path.join(OUT, '_exh')
    if os.path.isdir(tmp):
        shutil.rmtree(tmp)
    os.makedirs(tmp)
    tool = os.path.join(TOOL3DS, '3dstool.exe')
    subprocess.run([tool, '-xt0f', 'cci', 'p0.cxi', rom], cwd=tmp, check=True, capture_output=True)
    subprocess.run([tool, '-xtf', 'cxi', 'p0.cxi', '--exh', 'exh.bin'], cwd=tmp, check=True, capture_output=True)
    r = subprocess.run([XDELTA, '-e', '-9', '-f', '-A', '-s', os.path.join(tmp, 'exh.bin'), os.path.join(MOD, 'exheader.bin'),
                        os.path.join(data, 'exheader.xdelta')], capture_output=True, text=True)
    shutil.rmtree(tmp)
    if r.returncode:
        sys.exit(f'xdelta3 (exheader) fallito:\n{r.stderr}')
    open(os.path.join(data, 'code.ips'), 'wb').write(b'PATCHEOF')
    check_bat(pkg, rom, ver, files)
    z = pkg + '.zip'
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for dp, _, fs in os.walk(pkg):
            for f in fs:
                p = os.path.join(dp, f)
                zf.write(p, os.path.relpath(p, OUT))
    mb = lambda p: os.path.getsize(p) / (1 << 20)
    print(f'patch {mb(patch):.1f} MB (verificata), pacchetto -> {z} ({mb(z):.1f} MB)')
    # per il sito di Darkened Forest: la stessa xdelta col nome del bucket (scripts/upload_patches.py del sito) e i dati
    # del campo "luma" della release in patches_3ds.json (cartella Luma3DS creata nel browser, scripts/luma_web.py)
    import json, luma_web
    site = os.path.join(OUT, 'sito')
    os.makedirs(site, exist_ok=True)
    shutil.copyfile(patch, os.path.join(site, f'tongari-boushi-ita-v{ver}.xdelta'))
    with open(os.path.join(site, f'luma_v{ver}.json'), 'w', encoding='utf-8') as f:
        json.dump(luma_web.info(rom), f, separators=(',', ':'))
    print(f'sito -> {site}')
    os.remove(rom)


if __name__ == '__main__':
    main()
