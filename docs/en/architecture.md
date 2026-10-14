# Project architecture

*[Italiano](../architettura.md)*

How the repository is organized, what each build step does and where to change things. To build the patch see
[building.md](building.md). Code comments and script messages are in Italian.

- [Folders](#folders)
- [The build step by step](#the-build-step-by-step)
- [Game file formats](#game-file-formats)
- [The game code](#the-game-code)
- [Rules to avoid crashes on a real 3DS](#rules-to-avoid-crashes-on-a-real-3ds)
- [Where to change what](#where-to-change-what)

## Folders

```
scripts/              all Python scripts (build, formats, generators, checks)
work/trad/            translations: dialogue batches, tables, interface, code
work/trad/batches/    dialogue batches: bNNN.tsv (Japanese) + bNNN.it.tsv (Italian), mNNN = rewrites
work/glossary/        Italian character names
work/img/labels/      index of the graphic labels to regenerate
work/v11/funcmap.tsv  function map between Ver.1.0 and Ver.1.1 code
tools/fonts/          free fonts for the signs (licenses in LICENZE_FONT.txt)
docs/                 documentation
```

Folders created on your computer and never uploaded to GitHub (they are in `.gitignore`):

```
work/3ds/             the game extracted by prepare.py (romfs, exefs, headers)
work/3ds/romfs_x/     extracted .tarc archives
work/v11/exefs, raw/  code and exheader of the 1.1 update
work/img/ui, work/tut original textures as PNG, base for the image generators
work/img_it/          generated Italian images
build/                the finished mod
release/              the packages
tools/3dstool, xdelta3, models   external tools
```

## The build step by step

`scripts/build_all.py` runs these steps, in this order. Each one reads the original files from `work/3ds` and writes
the modified files into the mod (`build/00040000000B4A00`, or the folder set in `local_paths.json`).

| # | Step | What it does |
|---|---|---|
| 1 | `build_fonts` | Adds accented letters to the game fonts. |
| 2 | `batch_import` | Reads the dialogue batches `bNNN.it.tsv`, checks placeholders and characters, writes `batch_pages.json`. |
| 3 | `fix_slots` | One-off fixes of single lines (writes batch `m006`). |
| 4 | `manual_import` | Reads the rewrite batches `mNNN.it.tsv`, writes `manual_pages.json`. |
| 5 | `gen_labels` | Draws the graphic labels from `labels_it.tsv`. Empties `work/img_it/_auto`. |
| 6 | `build_text` | Applies all dialogue to the game text files (RESO format). Priority: rewrites > batches > DS version texts. |
| 7 | `blob_texts import` / `build` | Texts in unnamed blocks inside archives (item names, products, magic words). |
| 8 | `build_npc` | Character profiles. |
| 9 | `build_tables` | String tables in `common.tarc` (menus, shop, bag windows). |
| 10 | `build_ui` | Interface layout texts (`ui_trad.json`) and enlarged text buffers. |
| 11 | `make_recipe_list` … `make_license_headers` | Small interface images: recipe lists, notices, plates, tabs, titles. |
| 12 | `make_images` | Other menu images (buttons, titles). |
| 13 | `make_magazine_logo`, `make_magazine_bg`, `make_magazine_pages`, `make_magazine`, `make_magpage_labels` | The *Spell & Spill* magazine: logo, backgrounds, pages and titles. |
| 14 | `make_signs` | 3D shop signs and 2D images: erases the Japanese, rebuilds the background and redraws the Italian in layers (shadow, outlines, fill). |
| 15 | `make_credits` | End credits. |
| 16 | `make_tutorials` | Lesson and tutorial blackboards. |
| 17 | `build_images` | Puts all generated images into the game textures. |
| 18 | `make_title_credit` | Patch credit with the version number on the title screen. |
| 19 | `make_logo_skip` | Removes the boot logos. |
| 20 | `patch_shop_hours` | Event scripts: 24/7 shops, relationships, options, spells. |
| 21 | `build_code` | Game code: translated strings, ARM patches, port to Ver.1.1, exheader. |

The slow generators (`make_signs` and the magazine) keep a cache in `work/cache_steps`: if their code and inputs don't
change, the build copies the previous result back. `--nocache` forces regeneration.

## Game file formats

| Format | Contents | Script |
|---|---|---|
| `.tarc` (TBAF) | Konami archive with per-file LZ11 compression | `tbaf.py` |
| RESO (`.rdbt` + `.rndx`) | Dialogue and message texts | `reso.py`, `textdb.py` |
| EVSC (`.rdbt` + `.rndx` in `script.tarc`) | Event scripts (dialogue, choices, spells, doors) | `evsc.py` |
| DARC (`.arc`) | Layout archive | `darc.py` |
| BCLYT | Interface layouts and text panes | `bclyt.py` |
| BCLIM | 2D textures | `bclim.py` |
| BCFNT | Fonts | `bcfnt.py`, `font_patch.py` |
| CGFX | 3D models and their textures (signs) | `cgfx.py` |
| UTF-16 string tables | Menus, shop, etc. in `common.tarc` | `strtable.py` |

`evsc.py` is also a disassembler: useful to read what an event script does before changing it.

## The game code

`build_code.py` works on `exefs/code.bin`:

- **Strings in the code:** from `work/trad/code_it.tsv` (address, Japanese, Italian). If the Italian doesn't fit, the
  string is moved to free space and the pointers are updated.
- **ARM patches:** written in assembly inside the scripts (`options.py`, `fast_travel.py`, `name_plate.py`, …) and
  assembled by `armasm.py`. New code goes into space the game doesn't use: the padding at the end of the `.text`
  section and the two banned-word filter functions, removed by the patch.
- **Ver.1.1:** patches are written for Ver.1.0 addresses. `port11.py` moves them to 1.1 using `work/v11/funcmap.tsv`
  and checks word by word that the target code is the expected one. `port_audit.py` repeats the check on all patches.
- **Exheader:** the mod contains an already patched `code.bin` and the 1.1 exheader, instead of a `code.ips` patch.
  Luma3DS writes some of its own data at the end of the code sections: with `code.ips` that data ended up on top of
  our new code and the game froze at boot. The exheader sets the right section sizes.

Findings on the game's internals (addresses, variables, structures) are collected in
[note_tecniche.md](../note_tecniche.md) (Italian).

## Rules to avoid crashes on a real 3DS

The Azahar emulator forgives errors that freeze the game on a real 3DS. The rules the build follows:

1. **Alignment:** archives, textures and code stay 4-byte aligned. A misaligned access works in Azahar, not on the
   console.
2. **No NULL reads:** Azahar returns 0, the 3DS crashes. After every emulator test, `emu_log_check.py` looks for these
   accesses in the log.
3. **Don't remove layout parts:** the code looks up menu panes and parts by name or position. To hide one, zero its
   texture, scale or position; never delete it.
4. **Original compression:** every file inside a `.tarc` keeps its original compression. Compressing files the game
   reads uncompressed breaks, for example, the dialogue.
5. **Maximum lengths:** some texts have a fixed limit (`short_limits.json`, `blob_limits.json`), for example 15
   characters for menu choices.

`check_mod.py` automatically checks points 1, 4 and the archive structure.

## Where to change what

| I want to change… | File | Then |
|---|---|---|
| a line of dialogue | `work/trad/batches/*.it.tsv` (search the Italian text) | `build_all.py --from batch_import` |
| an interface menu or label | `work/trad/ui_trad.json` | `build_all.py --from build_ui` |
| names of items, products, magic words | `work/trad/batches/iNNN.it.tsv` | `build_all.py --from batch_import` |
| game and shop menu entries | `work/trad/tables/*.json` | `build_all.py --from batch_import` |
| a text inside the code (e.g. system messages) | `work/trad/code_it.tsv` | `build_all.py --only build_code` |
| a sign or a 2D image | `scripts/make_signs.py` (signs), `scripts/ui_specs.py` (images) | `build_all.py --from make_signs` |
| a blackboard | `scripts/tut_specs_*.py`, `scripts/tut_charm.py` | `build_all.py --from make_tutorials` |
| a magazine title | `scripts/mag_texts.py` | `build_all.py --from make_magazine_bg` |
| the Options or a gameplay improvement | `scripts/options.py`, `fast_travel.py`, `patch_relationships.py`, `patch_shop_hours.py` | `build_all.py --from patch_shop_hours` (`--from build_text` if you also change the lines) |
