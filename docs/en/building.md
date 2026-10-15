# Building the patch from source

*[Italiano](../compilare.md)*

This guide rebuilds the patch from **your own copy of the game**. The repository contains no Nintendo or Konami
files: the scripts read them from your dump and apply the translation.

You only need this to modify the patch or check how it is made. To play, just download the ready package from the
**Releases** page.

- [Quick start](#quick-start)
- [1. Requirements](#1-requirements)
- [2. External tools](#2-external-tools)
- [3. Game files](#3-game-files)
- [4. Preparation](#4-preparation)
- [5. Building](#5-building)
- [6. Testing the mod](#6-testing-the-mod)
- [7. Making the package](#7-making-the-package)
- [Rebuilding after a change](#rebuilding-after-a-change)
- [Troubleshooting](#troubleshooting)

## Quick start

```bash
git clone https://github.com/chokercrave/mahou-no-machi-patch.git
cd mahou-no-machi-patch
py -m pip install -r requirements.txt
py scripts/prepare.py "C:/games/Tongari.cci" "C:/games/Tongari Update v1.1.cia"
py scripts/build_all.py
py scripts/check_mod.py
py scripts/make_release.py
```

The result is in `build/00040000000B4A00` (the mod) and in `release/` (the package to distribute). You first need the
tools from [step 2](#2-external-tools).

## 1. Requirements

- **Windows 10 or 11.** Some tools are `.exe` files and two image generators use Windows fonts (Arial, Segoe UI).
- **Python 3.14** (the version used for development) from [python.org](https://www.python.org/downloads/). Tick
  *Add python.exe to PATH* during installation.
- **Git**, from [git-scm.com](https://git-scm.com/download/win), or download the repository as a ZIP from the green
  **Code** button on GitHub.
- About **3 GB** of free disk space.

Install the Python libraries with:

```bash
py -m pip install -r requirements.txt
```

## 2. External tools

They are not in the repository for license or size reasons. Put them exactly in these folders:

| Tool | Download | Location |
|---|---|---|
| **3dstool** 1.2.6 (extracts and rebuilds 3DS ROMs) | [github.com/dnasdw/3dstool/releases](https://github.com/dnasdw/3dstool/releases) | `tools/3dstool/3dstool.exe` plus the `.txt` files from the zip |
| **xdelta3** 3.0.11 x86_64 (creates the package patch) | [github.com/jmacd/xdelta-gpl/releases/tag/v3.0.11](https://github.com/jmacd/xdelta-gpl/releases/tag/v3.0.11) | `tools/xdelta3/xdelta3-3.0.11-x86_64.exe` |
| **LaMa** in ONNX format, `lama_fp32.onnx` (208 MB, rebuilds the background under the sign lettering) | [huggingface.co/Carve/LaMa-ONNX](https://huggingface.co/Carve/LaMa-ONNX/resolve/main/lama_fp32.onnx) | `tools/models/lama_fp32.onnx` |

SHA-256 of `lama_fp32.onnx`: `1faef5301d78db7dda502fe59966957ec4b79dd64e16f03ed96913c7a4eb68d6`.

The sign fonts are already in `tools/fonts` (licenses in `tools/fonts/LICENZE_FONT.txt`).

## 3. Game files

You need two **decrypted** files, taken from your console with [GodMode9](https://github.com/d0k3/GodMode9):

| File | What it is | Check |
|---|---|---|
| ROM `.cci` / `.3ds` | dump of the Japanese **Ver.1.0** cartridge (00040000000B4A00), 256 MB | SHA-1 `55dd4435cd694c8eec13f31a1157b41575d6e0fd` |
| `.cia` | official **Ver.1.1** update (v1056, 0004000E000B4A00), about 3 MB | checked by `prepare.py` |

With GodMode9 you dump the cartridge and build a CIA of the installed update; both must then be decrypted with the
*Decrypt file* option. An encrypted, trimmed or other-region ROM won't work.

Why the update is needed too: the patch contains the Ver.1.1 code, so it works with and without the update installed.
Only the update's code (`code.bin`) and exheader are used.

## 4. Preparation

```bash
py scripts/prepare.py "path/to/rom.cci" "path/to/update.cia"
```

Run it **once**. The script:

1. extracts the ROM into `work/3ds` (headers, code, romfs);
2. extracts the update's code and exheader into `work/v11`;
3. checks the hashes: if the dump is not the expected one it stops and says so;
4. extracts the game's `.tarc` archives into `work/3ds/romfs_x`;
5. converts to PNG the original textures that the image generators use as a base (`work/img`, `work/tut`).

If you change source files, run it again with `--force`.

## 5. Building

```bash
py scripts/build_all.py
py scripts/check_mod.py
```

`build_all.py` runs every step in the right order: texts, fonts, interface, images, signs, magazine, blackboards, event
scripts, code. The first run takes about **20–25 minutes**, mostly for the signs, the magazine and texture encoding. Later runs reuse a
cache for the slow generators and take a few minutes.

`check_mod.py` compares every file of the mod with the original: archive structure, alignment, sizes and texture
formats. **It must print `problemi: 0`** (0 problems). An error here usually means a crash on real 3DS hardware, even
if the emulator seems fine.

The mod ends up in `build/00040000000B4A00`:

```
build/00040000000B4A00/
├── romfs/           modified game files (only the changed ones)
├── exefs/code.bin   translated and patched Ver.1.1 code
└── exheader.bin     exheader matching the new code
```

To change the output folder (for example to write straight into Azahar's mods folder) create `local_paths.json` in the
project root, as explained in `scripts/paths.py`.

## 6. Testing the mod

**Azahar:** copy the `00040000000B4A00` folder into `%APPDATA%/Azahar/load/mods/` (in Azahar: right-click the game,
*Open Mods Location*) and start the original Japanese ROM. After each test you can run:

```bash
py scripts/emu_log_check.py
```

It searches Azahar's log for reads from invalid addresses. Azahar ignores them, but on a real 3DS they crash the game:
if it finds even one, the change must be fixed.

**3DS with Luma3DS:** copy the contents of `00040000000B4A00` into `SD:/luma/titles/00040000000B4A00/` and enable
*Enable game patching* in the Luma configuration (hold SELECT at boot).

## 7. Making the package

```bash
py scripts/make_release.py
```

Creates the zip to distribute in `release/`. The version comes from the `VERSION` file, the source ROM is the one given
to `prepare.py`.

```
Tongari Boushi ITA vX.Y/
├── Applica patch.bat              applies the patch and creates the luma folder
├── Tongari Boushi ITA vX.Y.xdelta differences between the original and the Italian ROM
├── LEGGIMI.txt, README.txt        instructions
└── dati/                          xdelta3, 3dstool, list of files for Luma, licenses
```

The package **contains no game files**: `Applica patch.bat` creates the Italian ROM from the user's ROM and extracts
the `luma` folder for 3DS from it. Before zipping, `make_release.py` tests the package the way a user would: it runs
the `.bat` on a copy and checks that the resulting ROM and `luma` folder are byte-identical to the build. The Italian
ROM used for the test is then deleted.

`make_release.py` also prepares, in `release/sito/`, the files for the **online patchers** on [Darkened Forest's site](https://darkenedforest.github.io/tongari-boushi-to-oshare-na-mahou-tsukai-archive/patches/#3ds):
the same xdelta under the site's file name (`tongari-boushi-ita-vX.Y.xdelta`, Azahar patcher) and `luma_vX.Y.json`,
the data the browser uses to build the `luma` folder from the patched ROM (3DS patcher: file list with CRC32 and the
exheader changes, no game files; see `scripts/luma_web.py`). The xdelta has no secondary compression (`-S none`),
because the in-browser patcher (RomPatcher.js) can't read it.

## Rebuilding after a change

`build_all.py` takes two options to avoid redoing everything:

```bash
py scripts/build_all.py --from build_text      # from this step to the end
py scripts/build_all.py --only build_code      # only the given steps, comma-separated
```

Rules to remember:

- `gen_labels` empties the generated images folder: after it, every later step is needed, so use `--from`, not
  `--only`.
- `build_ui` rewrites whole interface archives: after it too, use `--from build_ui`.
- When in doubt, a full build is always safe.

Where to change things (texts, images, code) is explained in [architecture.md](architecture.md).

## Troubleshooting

The scripts print their messages in Italian.

| Message | Cause and fix |
|---|---|
| `dump non riconosciuto` (dump not recognized) | ROM or update differ from the expected ones. You need the Japanese Ver.1.0 cartridge and the v1056 update, decrypted. |
| `il CIA non contiene un NCCH leggibile` (no readable NCCH in the CIA) | The CIA is still encrypted: decrypt it with GodMode9. |
| `manca ...3dstool.exe` / `xdelta3` (missing) | Tool not in the folder given in [step 2](#2-external-tools). |
| `prova del pacchetto fallita` (package test failed) | The `.bat` doesn't recreate the build exactly: the message lists the different files. It happens if the mod changed during `make_release` or the source ROM is not the one given to `prepare.py`. |
| error about `lama_fp32.onnx` | Model missing or incomplete: check the SHA-256. |
| `ModuleNotFoundError` | Missing libraries: `py -m pip install -r requirements.txt`. |
| `problemi: N` from `check_mod.py` | A generated file doesn't match the original format: the message says which. Don't distribute the mod until it is back to 0. |
