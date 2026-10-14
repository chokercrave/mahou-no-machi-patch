"""Cartelle comuni a tutti gli script.

  MOD          cartella della mod costruita (romfs/, exefs/, exheader.bin)     default: build/00040000000B4A00
  AZAHAR_USER  cartella dati di Azahar (log, schede SD), solo per emu_log_check.py e save_edit.py
               default: %APPDATA%/Azahar

Si cambiano con il file local_paths.json nella radice del progetto (non versionato). I percorsi relativi partono dalla
radice. Esempio, per costruire direttamente nella cartella mods di Azahar e provare subito la mod:
  {"mod": "C:/Users/<nome>/AppData/Roaming/Azahar/load/mods/00040000000B4A00",
   "azahar_user": "C:/Users/<nome>/AppData/Roaming/Azahar"}
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TITLE = '00040000000B4A00'
_LOCAL = os.path.join(ROOT, 'local_paths.json')
_cfg = json.load(open(_LOCAL, encoding='utf-8')) if os.path.exists(_LOCAL) else {}


def _abs(p):
    return os.path.normpath(os.path.join(ROOT, os.path.expandvars(p)))


MOD = _abs(_cfg.get('mod', os.path.join('build', TITLE)))
AZAHAR_USER = _abs(_cfg.get('azahar_user', os.path.join('%APPDATA%', 'Azahar')))
