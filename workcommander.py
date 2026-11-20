#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WorkCommander
=============

Gestor de archivos de doble panel para la consola de Windows, inspirado en el
clasico Norton Commander. Se ejecuta dentro de CMD / Windows Terminal sin
dependencias externas (solo biblioteca estandar de Python).

Uso:
    python workcommander.py [carpeta_inicial]

Teclas principales:
    F1 Ayuda   F2 Refrescar   F3 Ver   F4 Editar   F5 Copiar
    F6 Mover   F7 Crear dir   F8 Borrar   F9 Menu   F10 Salir
"""

import ctypes
import os
import shutil
import stat
import string
import subprocess
import sys
import time
import traceback
from ctypes import wintypes
from datetime import datetime

if os.name != "nt":
    print("WorkCommander solo funciona en Windows.")
    sys.exit(1)

import msvcrt

# --------------------------------------------------------------------------
#  Consola Win32 (pintado por bloques, sin parpadeo)
# --------------------------------------------------------------------------

STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11

ENABLE_EXTENDED_FLAGS = 0x0080
ENABLE_QUICK_EDIT_MODE = 0x0040
ENABLE_MOUSE_INPUT = 0x0010


class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]


class SMALL_RECT(ctypes.Structure):
    _fields_ = [
        ("Left", ctypes.c_short),
        ("Top", ctypes.c_short),
        ("Right", ctypes.c_short),
        ("Bottom", ctypes.c_short),
    ]


class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
    _fields_ = [
        ("dwSize", COORD),
        ("dwCursorPosition", COORD),
        ("wAttributes", ctypes.c_ushort),
        ("srWindow", SMALL_RECT),
        ("dwMaximumWindowSize", COORD),
    ]


class CHAR_INFO(ctypes.Structure):
    _fields_ = [("Char", ctypes.c_wchar), ("Attributes", ctypes.c_ushort)]


class CONSOLE_CURSOR_INFO(ctypes.Structure):
    _fields_ = [("dwSize", wintypes.DWORD), ("bVisible", wintypes.BOOL)]


kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.GetStdHandle.argtypes = [wintypes.DWORD]
kernel32.GetStdHandle.restype = wintypes.HANDLE
kernel32.GetConsoleScreenBufferInfo.argtypes = [
    wintypes.HANDLE,
    ctypes.POINTER(CONSOLE_SCREEN_BUFFER_INFO),
]
kernel32.GetConsoleScreenBufferInfo.restype = wintypes.BOOL
kernel32.WriteConsoleOutputW.argtypes = [
    wintypes.HANDLE,
    ctypes.POINTER(CHAR_INFO),
    COORD,
    COORD,
    ctypes.POINTER(SMALL_RECT),
]
kernel32.WriteConsoleOutputW.restype = wintypes.BOOL
kernel32.SetConsoleScreenBufferSize.argtypes = [wintypes.HANDLE, COORD]
kernel32.SetConsoleScreenBufferSize.restype = wintypes.BOOL
kernel32.SetConsoleCursorInfo.argtypes = [wintypes.HANDLE, ctypes.c_void_p]
kernel32.SetConsoleCursorInfo.restype = wintypes.BOOL
kernel32.SetConsoleCursorPosition.argtypes = [wintypes.HANDLE, COORD]
kernel32.SetConsoleCursorPosition.restype = wintypes.BOOL
kernel32.SetConsoleTitleW.argtypes = [ctypes.c_wchar_p]
kernel32.GetConsoleTitleW.argtypes = [ctypes.c_wchar_p, wintypes.DWORD]
kernel32.GetConsoleTitleW.restype = wintypes.DWORD
kernel32.GetConsoleMode.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
kernel32.GetConsoleMode.restype = wintypes.BOOL
kernel32.SetConsoleMode.argtypes = [wintypes.HANDLE, wintypes.DWORD]
kernel32.SetConsoleMode.restype = wintypes.BOOL

# Colores (fondo azul clasico estilo Norton Commander)
C_NORMAL = 0x17          # gris claro sobre azul
C_FRAME = 0x1B           # cian sobre azul
C_FRAME_ACTIVE = 0x1F    # blanco brillante sobre azul
C_TITLE = 0x30           # negro sobre cian
C_DIR = 0x1F             # carpetas: blanco brillante
C_MARK = 0x1E            # marcado: amarillo
C_SELECT = 0x30          # cursor: negro sobre cian
C_SELECT_MARK = 0x3F     # cursor + marcado
C_STATUS = 0x30
C_KEYBAR = 0x30
C_KEYCHIP = 0x70         # negro sobre gris claro
C_MENUBAR = 0x70
C_MENU_ACTIVE = 0x30
C_DLG_BG = 0x17
C_DLG_TEXT = 0x1F
C_FIELD = 0x0F
C_CURSOR = 0xF0
C_HINT = 0x1B
C_VIEW = 0x17
C_ALERT = 0x3C           # rojo brillante sobre cian
C_OK = 0x3F              # blanco brillante sobre cian
C_BAR_FILL = 0x1E
C_BAR_EMPTY = 0x18
C_SHADOW = 0x00

# Marco (doble linea). Se puede forzar ASCII con WORKCOMMANDER_ASCII=1
_ASCII_FRAME = os.environ.get("WORKCOMMANDER_ASCII", "") not in ("", "0", "no")
if _ASCII_FRAME:
    TL, TR, BL, BR = "+", "+", "+", "+"
    ML, MR = "+", "+"
    H, V = "-", "|"
    BAR_FULL, BAR_EMPTY = "#", "-"
else:
    TL, TR, BL, BR = "\u2554", "\u2557", "\u255a", "\u255d"
    ML, MR = "\u2560", "\u2563"
    H, V = "\u2550", "\u2551"
    BAR_FULL, BAR_EMPTY = "\u2588", "\u2591"


class Screen:
    """Doble buffer de caracteres que se vuelca de una sola vez a la consola."""

    def __init__(self):
        self.hout = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        self.hin = kernel32.GetStdHandle(STD_INPUT_HANDLE)
        self.w = 80
        self.h = 25
        self.grid = [(" ", C_NORMAL)] * (self.w * self.h)
        self._old_input_mode = None
        self._old_title = ""
        self._cleaned = False
        self._configure()
        self.sync_size(force=True)
        if self._info() is None:
            raise RuntimeError("No hay una consola interactiva disponible.")

    # -- configuracion ----------------------------------------------------
    def _configure(self):
        title_buf = ctypes.create_unicode_buffer(512)
        if kernel32.GetConsoleTitleW(title_buf, 512):
            self._old_title = title_buf.value
        kernel32.SetConsoleTitleW("WorkCommander")
        info = CONSOLE_CURSOR_INFO(25, False)
        kernel32.SetConsoleCursorInfo(self.hout, ctypes.byref(info))
        mode = wintypes.DWORD()
        if kernel32.GetConsoleMode(self.hin, ctypes.byref(mode)):
            self._old_input_mode = mode.value
            kernel32.SetConsoleMode(
                self.hin, (mode.value | ENABLE_EXTENDED_FLAGS | ENABLE_MOUSE_INPUT) & ~ENABLE_QUICK_EDIT_MODE
            )
        try:
            ctypes.windll.user32.ShowCursor(False)
        except Exception:
            pass

    def show_cursor(self, visible=True):
        info = CONSOLE_CURSOR_INFO(25, 1 if visible else 0)
        kernel32.SetConsoleCursorInfo(self.hout, ctypes.byref(info))

    def _info(self):
        info = CONSOLE_SCREEN_BUFFER_INFO()
        if kernel32.GetConsoleScreenBufferInfo(self.hout, ctypes.byref(info)):
            return info
        return None

    def sync_size(self, force=False):
        info = self._info()
        if info is None:
            return False
        win_w = info.srWindow.Right - info.srWindow.Left + 1
        win_h = info.srWindow.Bottom - info.srWindow.Top + 1
        if win_w < 1 or win_h < 1:
            return False
        # Ampliar el buffer si la ventana crecio mas que el buffer.
        if info.dwSize.X < win_w or info.dwSize.Y < win_h:
            try:
                kernel32.SetConsoleScreenBufferSize(
                    self.hout,
                    COORD(max(win_w, info.dwSize.X), max(win_h, info.dwSize.Y)),
                )
            except Exception:
                pass
        if force or (win_w, win_h) != (self.w, self.h):
            self.w, self.h = win_w, win_h
            self.grid = [(" ", C_NORMAL)] * (self.w * self.h)
            return True
        return False

    # -- primitivas de dibujo --------------------------------------------
    def clear(self, attr=C_NORMAL):
        self.grid = [(" ", attr)] * (self.w * self.h)

    def put(self, x, y, text, attr=C_NORMAL):
        if not text or y < 0 or y >= self.h:
            return
        base = y * self.w
        for i, ch in enumerate(text):
            xx = x + i
            if xx < 0:
                continue
            if xx >= self.w:
                break
            if ch < " ":
                ch = " "
            elif ord(ch) > 0xFFFF:
                ch = "?"
            self.grid[base + xx] = (ch, attr)

    def fill(self, x, y, w, h, ch, attr=C_NORMAL):
        if w <= 0 or h <= 0:
            return
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = yy * self.w
            for xx in range(x0, x1):
                self.grid[base + xx] = (ch, attr)

    def box(self, x, y, w, h, attr=C_FRAME, title="", title_attr=C_TITLE):
        if w < 2 or h < 2:
            return
        self.put(x, y, TL + H * (w - 2) + TR, attr)
        self.put(x, y + h - 1, BL + H * (w - 2) + BR, attr)
        for yy in range(y + 1, y + h - 1):
            self.put(x, yy, V, attr)
            self.put(x + w - 1, yy, V, attr)
        if title:
            text = " %s " % title
            if len(text) > w - 2:
                text = text[: w - 3] + " "
            self.put(x + max(1, (w - len(text)) // 2), y, text, title_attr)

    def hline_sep(self, x, y, w, attr=C_FRAME):
        if w < 2:
            return
        self.put(x, y, ML + H * (w - 2) + MR, attr)

    def flush(self):
        info = self._info()
        if info is None:
            return False
        win_w = info.srWindow.Right - info.srWindow.Left + 1
        win_h = info.srWindow.Bottom - info.srWindow.Top + 1
        if (win_w, win_h) != (self.w, self.h):
            self.sync_size(force=True)
            return False
        count = self.w * self.h
        buf = (CHAR_INFO * count)()
        grid = self.grid
        for i in range(count):
            ch, attr = grid[i]
            buf[i].Char = ch
            buf[i].Attributes = attr
        origin = COORD(info.srWindow.Left, info.srWindow.Top)
        region = SMALL_RECT(
            origin.X, origin.Y, origin.X + self.w - 1, origin.Y + self.h - 1
        )
        ok = kernel32.WriteConsoleOutputW(
            self.hout, buf, COORD(self.w, self.h), COORD(0, 0), ctypes.byref(region)
        )
        return bool(ok)

    def cleanup(self):
        if self._cleaned:
            return
        self._cleaned = True
        try:
            self.sync_size(force=True)
            self.clear(C_NORMAL)
            self.flush()
            self.show_cursor(True)
            info = self._info()
            if info is not None:
                # Dejar el cursor arriba de la zona visible, sin arrastrar el
                # historial de la consola fuera de la ventana.
                kernel32.SetConsoleCursorPosition(
                    self.hout, COORD(info.srWindow.Left, info.srWindow.Top)
                )
            if self._old_input_mode is not None:
                kernel32.SetConsoleMode(self.hin, self._old_input_mode)
            try:
                ctypes.windll.user32.ShowCursor(True)
            except Exception:
                pass
            kernel32.SetConsoleTitleW(self._old_title or "WorkCommander")
        except Exception:
            pass


# --------------------------------------------------------------------------
#  Utilidades
# --------------------------------------------------------------------------


class KEY_EVENT_RECORD(ctypes.Structure):
    _fields_ = [
        ("bKeyDown", wintypes.BOOL),
        ("wRepeatCount", wintypes.WORD),
        ("wVirtualKeyCode", wintypes.WORD),
        ("wVirtualScanCode", wintypes.WORD),
        ("uChar", ctypes.c_wchar),
        ("dwControlKeyState", wintypes.DWORD),
    ]


class INPUT_RECORD(ctypes.Structure):
    class _EVENT(ctypes.Union):
        class _MOUSE_EVENT(ctypes.Structure):
            _fields_ = [
                ("dwMousePosition", COORD),
                ("dwButtonState", wintypes.DWORD),
                ("dwControlKeyState", wintypes.DWORD),
                ("dwEventFlags", wintypes.DWORD),
            ]
        _fields_ = [("KeyEvent", KEY_EVENT_RECORD), ("MouseEvent", _MOUSE_EVENT)]
    _fields_ = [("EventType", wintypes.WORD), ("Event", _EVENT)]


kernel32.GetNumberOfConsoleInputEvents.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
kernel32.GetNumberOfConsoleInputEvents.restype = wintypes.BOOL
kernel32.ReadConsoleInputW.argtypes = [wintypes.HANDLE, ctypes.POINTER(INPUT_RECORD), wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
kernel32.ReadConsoleInputW.restype = wintypes.BOOL
kernel32.PeekConsoleInputW.argtypes = [wintypes.HANDLE, ctypes.POINTER(INPUT_RECORD), wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
kernel32.PeekConsoleInputW.restype = wintypes.BOOL


def read_key():
    """Devuelve ('char', texto), ('special', codigo) o ('mouse', dict)."""
    hin = kernel32.GetStdHandle(STD_INPUT_HANDLE)
    while True:
        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            if ch in ("\x00", "\xe0"):
                return ("special", msvcrt.getwch())
            return ("char", ch)
        
        # Revisar eventos de consola (incluyendo mouse), sin consumir teclado.
        num_events = wintypes.DWORD(0)
        if kernel32.GetNumberOfConsoleInputEvents(hin, ctypes.byref(num_events)) and num_events.value > 0:
            rec = INPUT_RECORD()
            read_count = wintypes.DWORD(0)
            if kernel32.PeekConsoleInputW(hin, ctypes.byref(rec), 1, ctypes.byref(read_count)) and read_count.value > 0:
                if rec.EventType == 0x0002:  # MOUSE_EVENT
                    # Consumir el evento de mouse.
                    kernel32.ReadConsoleInputW(hin, ctypes.byref(rec), 1, ctypes.byref(read_count))
                    me = rec.Event.MouseEvent
                    return ("mouse", {
                        "x": me.dwMousePosition.X,
                        "y": me.dwMousePosition.Y,
                        "button": me.dwButtonState,
                        "flags": me.dwEventFlags
                    })
                elif rec.EventType == 0x0001:  # KEY_EVENT: dejar que msvcrt lo gestione.
                    return None
                else:
                    # Consumir otros eventos (foco, etc.) para no bloquear.
                    kernel32.ReadConsoleInputW(hin, ctypes.byref(rec), 1, ctypes.byref(read_count))
                    return None
        time.sleep(0.01)


def wrap_text(text, width):
    if width < 8:
        width = 8
    out = []
    for raw in str(text).splitlines() or [""]:
        line = raw
        while len(line) > width:
            cut = line.rfind(" ", 0, width + 1)
            if cut <= 0:
                cut = width
            out.append(line[:cut])
            line = line[cut:].lstrip()
        out.append(line)
    return out or [""]


def fmt_size(n):
    if n is None:
        return ""
    try:
        n = int(n)
    except (TypeError, ValueError):
        return ""
    if n < 100_000_000:
        return "{:,}".format(n).replace(",", ".")
    for unit, div in (("KB", 1 << 10), ("MB", 1 << 20), ("GB", 1 << 30), ("TB", 1 << 40)):
        if n < div * 1024 or unit == "TB":
            return "{:.1f} {}".format(n / div, unit)
    return "{:.1f} TB".format(n / (1 << 40))


def fmt_date(ts):
    try:
        return datetime.fromtimestamp(ts).strftime("%d/%m/%y %H:%M")
    except (OSError, TypeError, ValueError):
        return ""


def size_label(n):
    """Tamano con la palabra 'bytes' solo cuando se muestra exacto."""
    try:
        n = int(n)
    except (TypeError, ValueError):
        return ""
    text = fmt_size(n)
    return text + " bytes" if n < 100_000_000 else text


def human_size(n):
    try:
        n = float(n)
    except (TypeError, ValueError):
        return "?"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return ("{:.0f} {}".format(n, unit) if unit == "B" else "{:.1f} {}".format(n, unit))
        n /= 1024.0
    return "?"


def looks_utf16(raw):
    """Heuristica para reconocer texto UTF-16, con o sin BOM."""
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return True
    sample = raw[:4096]
    if len(sample) < 4:
        return False
    even = sample[0::2]
    odd = sample[1::2]
    if not even or not odd:
        return False
    even_nul = even.count(0) / float(len(even))
    odd_nul = odd.count(0) / float(len(odd))
    return max(even_nul, odd_nul) >= 0.30 and min(even_nul, odd_nul) <= 0.05


def decode_text(raw):
    """Decodifica texto probando BOM, UTF-16, UTF-8 y cp1252."""
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        try:
            return raw.decode("utf-16")
        except UnicodeDecodeError:
            pass
    if looks_utf16(raw):
        sample = raw[:4096]
        le = sample[1::2].count(0) >= sample[0::2].count(0)
        try:
            return raw.decode("utf-16-le" if le else "utf-16-be", "replace")
        except (UnicodeDecodeError, LookupError):
            pass
    for enc in ("utf-8", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("cp1252", "replace")


def hex_dump_lines(raw, width):
    """Volcado hexadecimal con columna ASCII, ajustado al ancho disponible."""
    width = max(10, int(width))
    per_row = 4
    for candidate in (16, 8, 4):
        if candidate * 4 + 13 <= width:
            per_row = candidate
            break
    lines = []
    for off in range(0, len(raw), per_row):
        chunk = raw[off : off + per_row]
        hexpart = " ".join("%02X" % b for b in chunk).ljust(per_row * 3 - 1)
        text = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append("%08X  %s  |%s|" % (off, hexpart, text))
    return lines or [""]


# --------------------------------------------------------------------------
#  Panel
# --------------------------------------------------------------------------


class Entry:
    __slots__ = ("name", "path", "is_dir", "size", "mtime", "is_parent", "is_drive", "hidden")

    def __init__(self, name, path, is_dir, size=0, mtime=0, is_parent=False, is_drive=False, hidden=False):
        self.name = name
        self.path = path
        self.is_dir = is_dir
        self.size = size
        self.mtime = mtime
        self.is_parent = is_parent
        self.is_drive = is_drive
        self.hidden = hidden


class Panel:
    def __init__(self, app, path):
        self.app = app
        self.path = path
        self.entries = []
        self.index = 0
        self.offset = 0
        self.marked = set()
        self.sort_key = "name"
        self.sort_rev = False
        self.reload()

    # -- datos ------------------------------------------------------------
    def title(self):
        return "Unidades" if self.path is None else self.path

    def current(self):
        if 0 <= self.index < len(self.entries):
            return self.entries[self.index]
        return None

    def reload(self, keep_name=None):
        if keep_name is None:
            cur = self.current()
            keep_name = cur.name if cur else None

        entries = []
        if self.path is None:
            for letter in string.ascii_uppercase:
                root = "%s:\\" % letter
                try:
                    if os.path.exists(root):
                        entries.append(Entry(root, root, True, is_drive=True))
                except OSError:
                    pass
        else:
            entries.append(Entry("..", None, True, is_parent=True))
            try:
                with os.scandir(self.path) as it:
                    for de in it:
                        try:
                            st = de.stat(follow_symlinks=False)
                        except OSError:
                            st = None
                        hidden = bool(getattr(st, "st_file_attributes", 0) & 0x2)
                        if hidden and not self.app.show_hidden:
                            continue
                        try:
                            is_dir = de.is_dir(follow_symlinks=False)
                        except OSError:
                            is_dir = False
                        entries.append(
                            Entry(
                                de.name,
                                os.path.join(self.path, de.name),
                                is_dir,
                                0 if is_dir or st is None else st.st_size,
                                0 if st is None else st.st_mtime,
                                hidden=hidden,
                            )
                        )
            except OSError as ex:
                self.app.flash("Sin acceso a %s (%s)" % (self.path, ex), error=True)

        self.entries = entries
        self.sort_entries()
        names = {e.name for e in self.entries}
        self.marked &= names

        if keep_name:
            for i, e in enumerate(self.entries):
                if e.name.lower() == keep_name.lower():
                    self.index = i
                    break
        if not self.entries:
            self.index = 0
        else:
            self.index = max(0, min(self.index, len(self.entries) - 1))

    def sort_entries(self):
        parent = [e for e in self.entries if e.is_parent]
        rest = [e for e in self.entries if not e.is_parent]
        dirs = [e for e in rest if e.is_dir]
        files = [e for e in rest if not e.is_dir]

        key = self.sort_key
        if key == "ext":
            fkey = lambda e: (os.path.splitext(e.name)[1].lower(), e.name.lower())
        elif key == "date":
            fkey = lambda e: e.mtime or 0
        elif key == "size":
            fkey = lambda e: e.size or 0
        else:
            fkey = lambda e: e.name.lower()

        dirs.sort(key=lambda e: e.name.lower(), reverse=self.sort_rev)
        rev = self.sort_rev or key in ("date", "size")
        files.sort(key=fkey, reverse=rev)
        self.entries = parent + dirs + files

    def move(self, delta):
        if not self.entries:
            return
        self.index = max(0, min(len(self.entries) - 1, self.index + delta))

    # -- dibujo -----------------------------------------------------------
    def draw(self, x, y, w, h, active):
        scr = self.app.scr
        if w < 10 or h < 5:
            return
        frame = C_FRAME_ACTIVE if active else C_FRAME
        scr.box(x, y, w, h, frame)
        title = self.title()
        max_t = w - 4
        if len(title) > max_t:
            title = "..." + title[-(max_t - 3):]
        text = " %s " % title
        scr.put(x + max(1, (w - len(text)) // 2), y, text, C_TITLE if active else C_FRAME)

        inner = w - 2

        # Columnas
        date_w = 14 if inner >= 44 else 0
        size_w = 10 if inner >= 34 else 0
        gaps = (1 if size_w else 0) + (1 if date_w else 0)
        name_w = inner - size_w - date_w - gaps
        if name_w < 8:
            size_w = 0
            date_w = 0
            gaps = 0
            name_w = inner

        header = "Nombre".ljust(name_w)
        if size_w:
            header += " " + "Tama\u00f1o".rjust(size_w)
        if date_w:
            header += " " + "Fecha".rjust(date_w)
        scr.put(x + 1, y + 1, header[:inner], C_FRAME)

        scr.hline_sep(x, y + 2, w, frame)

        list_y = y + 3
        list_h = h - 4
        if list_h <= 0:
            return

        total = len(self.entries)
        if self.index < self.offset:
            self.offset = self.index
        if self.index >= self.offset + list_h:
            self.offset = self.index - list_h + 1
        max_off = max(0, total - list_h)
        self.offset = max(0, min(self.offset, max_off))

        for row in range(list_h):
            i = self.offset + row
            if i >= total:
                break
            e = self.entries[i]

            attr = C_DIR if (e.is_dir or e.is_drive) else C_NORMAL
            if e.is_parent:
                attr = C_FRAME
            if e.name in self.marked:
                attr = C_MARK
            if i == self.index:
                attr = C_SELECT_MARK if e.name in self.marked else C_SELECT

            name = e.name
            if e.is_dir and not e.is_parent and not e.is_drive:
                name += "\\"
            if len(name) > name_w:
                name = name[: max(1, name_w - 1)] + ">"
            line = name.ljust(name_w)
            if size_w:
                line += " " + ("" if e.is_dir else fmt_size(e.size)).rjust(size_w)
            if date_w:
                line += " " + ("" if (e.is_parent or e.is_drive) else fmt_date(e.mtime)).rjust(date_w)
            scr.put(x + 1, list_y + row, line[:inner], attr)


# --------------------------------------------------------------------------
#  Aplicacion
# --------------------------------------------------------------------------

MENUS = [
    (
        "Archivo",
        [
            ("Ver", "op_view"),
            ("Ver forzado (texto/hex)...", "op_view_force"),
            ("Ver archivo por ruta...", "op_view_path"),
            ("Editar con Notepad", "op_edit"),
            (None, None),
            ("Copiar", "op_copy"),
            ("Mover / renombrar", "op_move"),
            ("Crear carpeta", "op_mkdir"),
            ("Borrar", "op_delete"),
            (None, None),
            ("Cambiar unidad o ruta...", "op_changedrive"),
            ("Salir", "op_quit"),
        ],
    ),
    (
        "Opciones",
        [
            ("Ordenar por nombre", "op_sort_name"),
            ("Ordenar por extension", "op_sort_ext"),
            ("Ordenar por fecha", "op_sort_date"),
            ("Ordenar por tama\u00f1o", "op_sort_size"),
            ("Invertir orden", "op_sort_rev"),
            (None, None),
            ("Mostrar archivos ocultos", "op_toggle_hidden"),
            ("Refrescar", "op_refresh"),
        ],
    ),
    (
        "Ayuda",
        [
            ("Teclas", "op_help"),
            ("Acerca de WorkCommander", "op_about"),
        ],
    ),
]

HINTS = {
    "op_view": "F3",
    "op_view_force": "",
    "op_view_path": "",
    "op_edit": "F4",
    "op_copy": "F5",
    "op_move": "F6",
    "op_mkdir": "F7",
    "op_delete": "F8",
    "op_quit": "F10",
    "op_refresh": "Ctrl+R",
    "op_help": "F1",
    "op_sort_name": "",
    "op_sort_ext": "",
    "op_sort_date": "",
    "op_sort_size": "",
    "op_sort_rev": "",
    "op_toggle_hidden": "",
    "op_changedrive": "",
    "op_about": "",
}

HELP_TEXT = """WorkCommander - Ayuda

Teclas de funcion
  F1              Esta ayuda
  F2              Refrescar paneles
  F3              Ver archivo (texto o hexadecimal)
  F4              Editar con Notepad
  F5              Copiar al otro panel
  F6              Mover / renombrar
  F7              Crear carpeta
  F8              Borrar
  F9              Menu superior
  F10             Salir

Navegacion
  Flechas         Mover el cursor
  Tab             Cambiar de panel
  Enter           Entrar a carpeta / abrir archivo
  Retroceso       Subir un nivel
  Inicio / Fin    Primera / ultima entrada
  RePag / AvPag   Pagina arriba / abajo
  Insert          Marcar o desmarcar
  Ctrl+R          Refrescar
  Letras          Busqueda rapida por nombre

Operaciones
  Los elementos marcados con Insert se procesan en conjunto.
  Al copiar o mover se usa como destino la carpeta del otro panel.
  En la raiz de una unidad, ".." muestra la lista de unidades.

Visor
  F3 abre cualquier archivo. Si parece binario, permite elegir texto o
  hexadecimal. Los archivos UTF-16 (por ejemplo INI) se detectan solos.
  Archivo > Ver forzado abre el archivo actual como texto o hexadecimal.
  Archivo > Ver archivo por ruta permite escribir cualquier ruta, incluso
  archivos ocultos que no aparezcan en el panel.

Consejo: agrande la ventana de CMD para ver mas columnas.
"""


class WorkCommander:
    def __init__(self, start_path=None, screen=None):
        self.scr = screen if screen is not None else Screen()
        self.show_hidden = True
        self.active = 0
        self.running = True
        self.flash_text = ""
        self.flash_error = False
        self.flash_time = 0.0
        self.last_draw = 0.0
        self.menu_open = False
        self.menu_idx = 0
        self.item_idx = 0
        self.menu_x = []
        self._prog = None
        self.search_buf = ""
        self.search_time = 0.0
        self.mouse_x = -1
        self.mouse_y = -1
        self.mouse_over = False
        self._view_split = None
        self.viewers = [None, None]

        if not start_path or not os.path.isdir(start_path):
            start_path = os.getcwd()
        start_path = os.path.abspath(start_path)

        self.panels = [Panel(self, start_path), Panel(self, start_path)]

    # -- infraestructura --------------------------------------------------
    def flash(self, text, error=False):
        self.flash_text = text
        self.flash_error = error
        self.flash_time = time.time()

    def page_size(self):
        return max(1, self.scr.h - 7)

    def selected_entries(self):
        p = self.panels[self.active]
        marked = [
            e for e in p.entries
            if e.name in p.marked and not e.is_parent and not e.is_drive
        ]
        if marked:
            return marked
        e = p.current()
        if e is None or e.is_parent or e.is_drive:
            return []
        return [e]

    def _norm_target(self, panel, text):
        text = text.strip().strip('"')
        if not text:
            return None
        text = os.path.expandvars(os.path.expanduser(text))
        if not os.path.isabs(text):
            base = panel.path or os.getcwd()
            text = os.path.abspath(os.path.join(base, text))
        return text

    def _on_rm_error(self, func, path, exc):
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except OSError:
            pass

    # -- dialogo base -----------------------------------------------------
    def _dialog_frame(self, title, w, h, error=False):
        scr = self.scr
        w = max(10, min(w, scr.w - 2))
        h = max(5, min(h, scr.h - 2))
        x = max(0, (scr.w - w) // 2)
        y = max(0, (scr.h - h) // 2)
        if x + 1 + w <= scr.w and y + 1 + h <= scr.h:
            scr.fill(x + 1, y + 1, w, h, " ", C_SHADOW)
        scr.fill(x, y, w, h, " ", C_DLG_BG)
        scr.box(x, y, w, h, C_ALERT if error else C_FRAME)
        t = " %s " % title
        if len(t) > w - 2:
            t = t[: w - 3] + " "
        scr.put(x + max(1, (w - len(t)) // 2), y, t, C_TITLE)
        return x, y, w, h

    def dialog_input(self, title, label, default=""):
        scr = self.scr
        text = list(default)
        pos = len(text)
        need = max(len(label) + 8, len(default) + 10, 48)
        w = min(max(40, need), max(40, scr.w - 4))
        h = 8
        while True:
            x, y, w, h = self._dialog_frame(title, w, h)
            scr.put(x + 2, y + 2, label[: max(1, w - 4)], C_DLG_TEXT)
            scr.fill(x + 2, y + 4, max(1, w - 4), 1, " ", C_FIELD)
            inner = max(1, w - 6)
            start = 0
            if pos > inner - 1:
                start = pos - (inner - 1)
            view = "".join(text[start:start + inner])
            scr.put(x + 3, y + 4, view, C_FIELD)
            ch = text[pos] if pos < len(text) else " "
            scr.put(x + 3 + (pos - start), y + 4, ch, C_CURSOR)
            scr.put(x + 2, y + 6, "Enter = aceptar     Esc = cancelar"[: max(1, w - 4)], C_HINT)
            scr.flush()

            key = read_key()
            if not key:
                continue
            kind, val = key
            if kind == "mouse":
                self.mouse_x = val["x"]
                self.mouse_y = val["y"]
                self.mouse_over = True
                continue
            if kind == "special":
                if val == "K":
                    pos = max(0, pos - 1)
                elif val == "M":
                    pos = min(len(text), pos + 1)
                elif val == "G":
                    pos = 0
                elif val == "O":
                    pos = len(text)
                elif val == "S":
                    if pos < len(text):
                        del text[pos]
                elif val == "H" or val == "P":
                    pass
                continue
            if val == "\r":
                return "".join(text).strip()
            if val == "\x1b":
                return None
            if val == "\x08":
                if pos > 0:
                    del text[pos - 1]
                    pos -= 1
                continue
            if val == "\x7f":
                if pos < len(text):
                    del text[pos]
                continue
            if val and val >= " ":
                if len(text) < 2048:
                    text.insert(pos, val)
                    pos += 1

    def dialog_confirm(self, title, lines):
        scr = self.scr
        w = min(max([len(l) for l in lines] + [len(title) + 6, 46]), max(30, scr.w - 4))
        wrapped = []
        for l in lines:
            wrapped.extend(wrap_text(l, max(10, w - 4)))
        h = min(len(wrapped) + 6, max(6, scr.h - 2))
        x, y, w, h = self._dialog_frame(title, w, h)
        for i, line in enumerate(wrapped):
            if y + 2 + i >= y + h - 3:
                break
            scr.put(x + 2, y + 2 + i, line[: w - 4], C_DLG_TEXT)
        scr.put(x + 2, y + h - 2, "  (S) Si        (N) No  "[: max(1, w - 4)], C_HINT)
        scr.flush()
        while True:
            key = read_key()
            if not key:
                continue
            kind, val = key
            if kind == "mouse":
                self.mouse_x = val["x"]
                self.mouse_y = val["y"]
                self.mouse_over = True
                continue
            if kind == "special":
                continue
            if val in ("s", "S", "y", "Y", "\r"):
                return True
            if val in ("n", "N", "\x1b"):
                return False

    def dialog_choice(self, title, lines, options):
        """Muestra varias opciones de tecla y devuelve la clave elegida o None."""
        scr = self.scr
        hint = "   ".join("(%s) %s" % (key.upper(), label) for key, label in options)
        hint += "   Esc Cancelar"
        w = min(
            max([len(l) for l in lines] + [len(title) + 6, len(hint) + 4, 46]),
            max(30, scr.w - 4),
        )
        wrapped = []
        for line in lines:
            wrapped.extend(wrap_text(line, max(10, w - 4)))
        h = min(len(wrapped) + 6, max(6, scr.h - 2))
        x, y, w, h = self._dialog_frame(title, w, h)
        row = 0
        for line in wrapped:
            if y + 2 + row >= y + h - 3:
                scr.put(x + 2, y + h - 3, "..."[: max(1, w - 4)], C_DLG_TEXT)
                break
            scr.put(x + 2, y + 2 + row, line[: w - 4], C_DLG_TEXT)
            row += 1
        scr.put(x + 2, y + h - 2, hint[: max(1, w - 4)], C_HINT)
        scr.flush()
        while True:
            key = read_key()
            if not key:
                continue
            kind, val = key
            if kind == "mouse":
                self.mouse_x = val["x"]
                self.mouse_y = val["y"]
                self.mouse_over = True
                continue
            if kind == "special":
                continue
            if val == "\x1b":
                return None
            if val == "\r":
                return options[0][0] if options else None
            low = val.lower()
            for k, _label in options:
                if low == k.lower():
                    return k

    def dialog_message(self, title, lines, error=False):
        scr = self.scr
        w = min(max([len(l) for l in lines] + [len(title) + 6, 46]), max(30, scr.w - 4))
        wrapped = []
        for l in lines:
            wrapped.extend(wrap_text(l, max(10, w - 4)))
        if not wrapped:
            wrapped = [""]
        h = min(len(wrapped) + 6, max(6, scr.h - 2))
        x, y, w, h = self._dialog_frame(title, w, h, error=error)
        row = 0
        for line in wrapped:
            if y + 2 + row >= y + h - 3:
                scr.put(x + 2, y + h - 3, "..."[: max(1, w - 4)], C_DLG_TEXT)
                break
            scr.put(x + 2, y + 2 + row, line[: w - 4], C_ALERT if error else C_DLG_TEXT)
            row += 1
        scr.put(x + 2, y + h - 2, " Pulse una tecla para continuar "[: max(1, w - 4)], C_HINT)
        scr.flush()
        read_key()

    # -- progreso ---------------------------------------------------------
    def _progress_show(self, label, done, total, current):
        scr = self.scr
        w = min(max(58, len(label) + 10), max(30, scr.w - 4))
        h = 9
        x, y, w, h = self._dialog_frame("Progreso", w, h)
        scr.put(x + 2, y + 2, label[: w - 4], C_DLG_TEXT)
        bw = max(4, w - 8)
        pct = (done / total) if total else 0.0
        filled = int(bw * pct)
        scr.put(x + 3, y + 4, BAR_FULL * filled, C_BAR_FILL)
        scr.put(x + 3 + filled, y + 4, BAR_EMPTY * (bw - filled), C_BAR_EMPTY)
        scr.put(x + 3, y + 5, ("%d / %d   %d%%" % (done, total, int(pct * 100)))[: w - 4], C_DLG_TEXT)
        scr.put(x + 3, y + 6, current[: w - 4], C_HINT)
        scr.put(x + 2, y + 7, "Esc = cancelar"[: w - 4], C_HINT)
        scr.flush()

    def _progress(self, label, done, total, current=""):
        if self._prog is None:
            return
        now = time.time()
        # Cancelar con Esc sin bloquear
        hin = kernel32.GetStdHandle(STD_INPUT_HANDLE)
        num_events = wintypes.DWORD(0)
        if kernel32.GetNumberOfConsoleInputEvents(hin, ctypes.byref(num_events)) and num_events.value > 0:
            rec = INPUT_RECORD()
            read_count = wintypes.DWORD(0)
            if kernel32.ReadConsoleInputW(hin, ctypes.byref(rec), 1, ctypes.byref(read_count)) and read_count.value > 0:
                if rec.EventType == 0x0001:  # KEY_EVENT
                    if rec.Event.KeyEvent.bKeyDown and rec.Event.KeyEvent.uChar.UnicodeChar == "\x1b":
                        self._prog["cancel"] = True
        if now - self._prog["last"] < 0.05 and done < total:
            return
        self._prog["last"] = now
        self._progress_show(label, done, total, current)

    # -- copia ------------------------------------------------------------
    def _copy_jobs(self, jobs):
        plan_dirs = []
        plan_files = []
        for src, dst in jobs:
            src = os.path.abspath(src)
            dst = os.path.abspath(dst)
            if os.path.isdir(src):
                plan_dirs.append(dst)
                for root, _dirs, files in os.walk(src):
                    rel = os.path.relpath(root, src)
                    tgt = dst if rel == "." else os.path.join(dst, rel)
                    if rel != ".":
                        plan_dirs.append(tgt)
                    for f in files:
                        plan_files.append((os.path.join(root, f), os.path.join(tgt, f)))
            else:
                if not os.path.isdir(os.path.dirname(dst)):
                    self.dialog_message("Copiar", ["La carpeta destino no existe:", os.path.dirname(dst)], error=True)
                    return False
                plan_files.append((src, dst))

        total = len(plan_files)
        self._prog = {"last": 0.0, "cancel": False}
        errors = []
        try:
            for d in plan_dirs:
                if self._prog["cancel"]:
                    break
                try:
                    os.makedirs(d, exist_ok=True)
                except OSError as ex:
                    errors.append("%s: %s" % (d, ex))
            if total == 0:
                self._progress("Creando carpetas...", 1, 1, "")
            for i, (s, d) in enumerate(plan_files, 1):
                if self._prog["cancel"]:
                    break
                try:
                    os.makedirs(os.path.dirname(d), exist_ok=True)
                    shutil.copy2(s, d)
                except OSError as ex:
                    errors.append("%s: %s" % (os.path.basename(s), ex))
                self._progress("Copiando archivos...", i, total, os.path.basename(s))
        finally:
            cancelled = self._prog["cancel"]
            self._prog = None

        if cancelled:
            self.dialog_message("Copiar", ["Operacion cancelada por el usuario."])
            return False
        if errors:
            lines = ["Se produjeron %d error(es):" % len(errors)] + errors[:8]
            if len(errors) > 8:
                lines.append("... y %d mas." % (len(errors) - 8))
            self.dialog_message("Copiar", lines, error=True)
        return not errors

    # -- visor / paginador ------------------------------------------------
    def pager_blocking(self, title, disp, info=""):
        scr = self.scr
        split_side = getattr(self, "_view_split", None)
        top = 0
        while True:
            scr.sync_size()
            
            # Calcular limites segun si es visor dividido (mitad de pantalla) o completo
            if split_side == 0:
                vx, vy, vw, vh = 0, 1, scr.w // 2, scr.h - 3
            elif split_side == 1:
                vw = scr.w - scr.w // 2
                vx, vy, vw, vh = scr.w // 2, 1, vw, scr.h - 3
            else:
                vx, vy, vw, vh = 0, 0, scr.w, scr.h

            page = max(1, vh - 2)
            top = max(0, min(top, max(0, len(disp) - page)))
            
            # Limpiar y dibujar marco del visor en su region correspondiente
            scr.fill(vx, vy, vw, vh, " ", C_VIEW)
            scr.box(vx, vy, vw, vh, C_FRAME, title)
            
            for i in range(page):
                if top + i >= len(disp):
                    break
                line_text = disp[top + i][: vw - 2]
                scr.put(vx + 1, vy + 1 + i, line_text.ljust(vw - 2), C_VIEW)
                
            # Barra de estado inferior dentro del visor o en su linea inferior
            pos = "Lineas %d-%d de %d" % (
                min(top + 1, len(disp)),
                min(top + page, len(disp)),
                len(disp),
            )
            bar = " %s | %s | Esc salir" % (info, pos)
            scr.put(vx + 1, vy + vh - 1, bar[: vw - 2].ljust(vw - 2), C_STATUS)
            
            # Cursor estilo MS-DOS en posicion del mouse
            if self.mouse_over and vx <= self.mouse_x < vx + vw and vy <= self.mouse_y < vy + vh:
                idx = self.mouse_y * scr.w + self.mouse_x
                if idx < len(scr.grid):
                    ch, attr = scr.grid[idx]
                    fg = attr & 0x0F
                    bg = (attr >> 4) & 0x0F
                    scr.grid[idx] = (ch, (fg << 4) | bg)
            scr.flush()

            key = read_key()
            if not key:
                continue
            kind, val = key
            if kind == "char":
                if val in ("\x1b", "q", "Q"):
                    return
                continue
            if kind == "special":
                if val in ("=", "D"):
                    return
                if val == "H":
                    top = max(0, top - 1)
                elif val == "P":
                    top = min(max(0, len(disp) - page), top + 1)
                elif val == "I":
                    top = max(0, top - page)
                elif val == "Q":
                    top = min(max(0, len(disp) - page), top + page)
                elif val == "G":
                    top = 0
                elif val == "O":
                    top = max(0, len(disp) - page)
            elif kind == "mouse":
                self.mouse_x = val["x"]
                self.mouse_y = val["y"]
                self.mouse_over = True
                # Click fuera del visor para cerrarlo
                mx, my = val["x"], val["y"]
                if not (vx <= mx < vx + vw and vy <= my < vy + vh):
                    if val["button"] & 0x1:
                        return

    def pager(self, title, disp, info=""):
        # Visor no bloqueante: el renderizado persistente se hace en draw().
        return

    def view_file(self, path, mode=None, split_side=None):
        """Abre cualquier archivo. mode: None (auto), "t" (texto) o "h" (hex)."""
        self._view_split = split_side
        try:
            size = os.path.getsize(path)
            with open(path, "rb") as f:
                raw = f.read(8 * 1024 * 1024 + 1)
        except OSError as ex:
            self.dialog_message("Ver", ["No se pudo abrir el archivo:", str(ex)], error=True)
            return

        truncated = len(raw) > 8 * 1024 * 1024
        raw = raw[: 8 * 1024 * 1024]
        binary = (not looks_utf16(raw)) and (b"\x00" in raw[:8192])
        if binary and mode not in ("t", "h"):
            choice = self.dialog_choice(
                "Ver",
                [
                    "El archivo parece ser binario:",
                    os.path.basename(path),
                    "\u00bfC\u00f3mo desea abrirlo?",
                ],
                [("t", "Texto"), ("h", "Hexadecimal")],
            )
            if not choice:
                return
            mode = choice

        scr = self.scr
        vw = (scr.w // 2 if split_side is not None else scr.w) - 2
        width = max(10, vw)

        if mode == "h":
            disp = hex_dump_lines(raw, width)
            info = "%s%s  hexadecimal" % (
                size_label(size),
                " (truncado)" if truncated else "",
            )
            side = split_side if split_side is not None else self.active
            self.viewers[side] = {
                "title": os.path.basename(path) + " [hex]",
                "disp": disp,
                "info": info,
                "top": 0,
            }
            self.pager(os.path.basename(path) + " [hex]", disp, info)
            return

        text = decode_text(raw)
        disp = []
        for line in text.split("\n"):
            line = line.rstrip("\r").replace("\t", "    ")
            if binary:
                line = "".join(c if c >= " " and c != "\x7f" else "." for c in line)
            else:
                line = "".join(c if c >= " " and c != "\x7f" else " " for c in line)
            if line == "":
                disp.append("")
                continue
            while len(line) > width:
                disp.append(line[:width])
                line = line[width:]
            disp.append(line)

        info = "%s%s" % (size_label(size), " (truncado)" if truncated else "")
        if binary:
            info += "  texto forzado"
        side = split_side if split_side is not None else self.active
        self.viewers[side] = {
            "title": os.path.basename(path),
            "disp": disp,
            "info": info,
            "top": 0,
        }
        self.pager(os.path.basename(path), disp, info)

    # -- navegacion -------------------------------------------------------
    def op_enter(self):
        p = self.panels[self.active]
        e = p.current()
        if e is None:
            return
        if e.is_drive:
            p.path = e.name
            p.reload()
            p.index = 0
            return
        if e.is_parent:
            self.op_up()
            return
        if e.is_dir:
            p.path = e.path
            p.reload()
            p.index = 0
            return
        try:
            os.startfile(e.path)
        except OSError as ex:
            self.dialog_message("Abrir", ["No se pudo abrir el archivo:", str(ex)], error=True)

    def op_up(self):
        p = self.panels[self.active]
        if p.path is None:
            return
        drive, tail = os.path.splitdrive(p.path)
        if tail in ("\\", "/", ""):
            old = drive + "\\"
            p.path = None
            p.reload(keep_name=old)
            return
        old = os.path.basename(p.path.rstrip("\\/"))
        parent = os.path.dirname(p.path.rstrip("\\/"))
        p.path = parent
        p.reload(keep_name=old)

    def toggle_mark(self):
        p = self.panels[self.active]
        e = p.current()
        if e is None or e.is_parent or e.is_drive:
            return
        if e.name in p.marked:
            p.marked.discard(e.name)
        else:
            p.marked.add(e.name)
        p.move(1)

    def quick_search(self, ch):
        now = time.time()
        if now - self.search_time > 1.2:
            self.search_buf = ""
        self.search_time = now
        self.search_buf += ch.lower()
        p = self.panels[self.active]
        for i, e in enumerate(p.entries):
            if e.name.lower().startswith(self.search_buf):
                p.index = i
                return

    # -- operaciones ------------------------------------------------------
    def op_view(self):
        p = self.panels[self.active]
        e = p.current()
        if e is None or e.is_parent or e.is_drive:
            return
        if e.is_dir:
            self.dialog_message("Ver", ["Es una carpeta, no un archivo."])
            return
        self.view_file(e.path, split_side=self.active)

    def op_view_force(self):
        p = self.panels[self.active]
        e = p.current()
        if e is None or e.is_parent or e.is_drive:
            self.dialog_message("Ver", ["Seleccione un archivo en el panel."])
            return
        if e.is_dir:
            self.dialog_message("Ver", ["Es una carpeta, no un archivo."])
            return
        choice = self.dialog_choice(
            "Ver forzado",
            ["Archivo:", e.name, "Elija el modo de visualizaci\u00f3n."],
            [("t", "Texto"), ("h", "Hexadecimal")],
        )
        if not choice:
            return
        self.view_file(e.path, mode=choice, split_side=self.active)

    def op_view_path(self):
        p = self.panels[self.active]
        e = p.current()
        if (
            e is not None
            and e.path
            and not e.is_dir
            and not e.is_parent
            and not e.is_drive
        ):
            default = e.path
        else:
            default = p.path or "C:\\"
        text = self.dialog_input("Ver archivo", "Ruta del archivo:", default)
        if not text:
            return
        path = self._norm_target(p, text)
        if not path:
            return
        if not os.path.isfile(path):
            self.dialog_message("Ver", ["No es un archivo existente:", path], error=True)
            return
        self.view_file(path, split_side=self.active)

    def op_edit(self):
        p = self.panels[self.active]
        e = p.current()
        if e is None or e.is_parent or e.is_drive or e.is_dir:
            return
        self.scr.show_cursor(True)
        self.scr.clear(C_NORMAL)
        self.scr.flush()
        try:
            subprocess.run(["notepad.exe", e.path])
        except OSError:
            try:
                os.startfile(e.path)
            except OSError as ex:
                self.dialog_message("Editar", ["No se pudo abrir el editor:", str(ex)], error=True)
        finally:
            self.scr.sync_size(force=True)
            self.scr.show_cursor(False)
            self.draw()

    def op_copy(self):
        p = self.panels[self.active]
        srcs = self.selected_entries()
        if not srcs:
            return
        other = self.panels[1 - self.active]
        default = other.path if other.path else "C:\\"
        target = self.dialog_input("Copiar", "Copiar %d elemento(s) a:" % len(srcs), default)
        if not target:
            return
        target = self._norm_target(p, target)
        if target is None:
            return

        jobs = []
        if len(srcs) == 1:
            src = srcs[0].path
            if os.path.isdir(target):
                dst = os.path.join(target, os.path.basename(src.rstrip("\\/")))
            else:
                dst = target
            jobs.append((src, dst))
        else:
            if not os.path.isdir(target):
                self.dialog_message(
                    "Copiar", ["El destino debe ser una carpeta existente.", target], error=True
                )
                return
            for e in srcs:
                jobs.append((e.path, os.path.join(target, e.name)))

        for src, dst in jobs:
            if not src or not dst:
                continue
            a = os.path.normcase(os.path.abspath(src))
            b = os.path.normcase(os.path.abspath(dst))
            if a == b:
                self.dialog_message("Copiar", ["El origen y el destino son el mismo."], error=True)
                return
            if os.path.isdir(src):
                if os.path.exists(dst) and not os.path.isdir(dst):
                    self.dialog_message(
                        "Copiar",
                        ["El destino existe y no es una carpeta:", dst],
                        error=True,
                    )
                    return
                if b == a or b.startswith(a + os.sep):
                    self.dialog_message(
                        "Copiar", ["No se puede copiar una carpeta dentro de si misma."], error=True
                    )
                    return
            elif os.path.isdir(dst):
                self.dialog_message(
                    "Copiar",
                    ["El destino es una carpeta y el origen es un archivo:", dst],
                    error=True,
                )
                return

        conflicts = [dst for _src, dst in jobs if os.path.exists(dst)]
        if conflicts:
            if not self.dialog_confirm(
                "Copiar",
                ["Ya existe(n) %d destino(s)." % len(conflicts), "\u00bfSobrescribir?"],
            ):
                return

        ok = self._copy_jobs(jobs)
        p.reload()
        other.reload()
        if ok:
            self.flash("Copiado: %d elemento(s)" % len(srcs))

    def op_move(self):
        p = self.panels[self.active]
        srcs = self.selected_entries()
        if not srcs:
            return

        if len(srcs) == 1:
            e = srcs[0]
            if not p.path:
                return
            target = self.dialog_input(
                "Mover / renombrar", 'Nuevo nombre o destino para "%s":' % e.name, e.name
            )
            if not target:
                return
            raw = target.strip().strip('"')
            if not raw:
                return
            if os.sep in raw or "/" in raw or (len(raw) >= 2 and raw[1] == ":"):
                dst = self._norm_target(p, raw)
                if dst and os.path.isdir(dst):
                    dst = os.path.join(dst, e.name)
            else:
                dst = os.path.join(p.path, raw)
            if not dst:
                return
            if os.path.normcase(os.path.abspath(dst)) == os.path.normcase(os.path.abspath(e.path)):
                return
            if os.path.exists(dst):
                if os.path.isdir(dst):
                    self.dialog_message(
                        "Mover",
                        ["Ya existe una carpeta con ese nombre.", "No se sobrescribe con un archivo.", dst],
                        error=True,
                    )
                    return
                if not self.dialog_confirm(
                    "Mover", ["El destino ya existe:", dst, "\u00bfSobrescribir?"]
                ):
                    return
                try:
                    os.remove(dst)
                except OSError as ex:
                    self.dialog_message("Mover", [str(ex)], error=True)
                    return
            try:
                shutil.move(e.path, dst)
            except OSError as ex:
                self.dialog_message("Mover", ["No se pudo mover:", str(ex)], error=True)
                return
            p.reload(keep_name=os.path.basename(dst.rstrip("\\/")))
        else:
            other = self.panels[1 - self.active]
            default = other.path if other.path else "C:\\"
            target = self.dialog_input(
                "Mover", "Mover %d elemento(s) a:" % len(srcs), default
            )
            if not target:
                return
            target = self._norm_target(p, target)
            if not target or not os.path.isdir(target):
                self.dialog_message(
                    "Mover", ["El destino debe ser una carpeta existente."], error=True
                )
                return
            conflicts = [e for e in srcs if os.path.exists(os.path.join(target, e.name))]
            if conflicts:
                if not self.dialog_confirm(
                    "Mover",
                    ["Ya existe(n) %d destino(s)." % len(conflicts), "\u00bfSobrescribir?"],
                ):
                    return
            errors = []
            for e in srcs:
                dst = os.path.join(target, e.name)
                try:
                    if os.path.exists(dst):
                        if os.path.isdir(dst):
                            errors.append("%s: ya existe una carpeta con ese nombre" % e.name)
                            continue
                        os.remove(dst)
                    shutil.move(e.path, dst)
                except OSError as ex:
                    errors.append("%s: %s" % (e.name, ex))
            p.marked.clear()
            p.reload()
            other.reload()
            if errors:
                self.dialog_message("Mover", errors[:9], error=True)
            else:
                self.flash("Movido: %d elemento(s)" % len(srcs))
            return

        p.reload()
        self.panels[1 - self.active].reload()

    def op_mkdir(self):
        p = self.panels[self.active]
        if p.path is None:
            return
        name = self.dialog_input("Crear carpeta", "Nombre de la nueva carpeta:", "")
        if not name:
            return
        name = name.strip().strip('"')
        if not name:
            return
        target = name if os.path.isabs(name) else os.path.join(p.path, name)
        try:
            os.makedirs(target)
        except OSError as ex:
            self.dialog_message("Crear carpeta", ["No se pudo crear:", str(ex)], error=True)
            return
        p.reload(keep_name=os.path.basename(target.rstrip("\\/")))
        self.flash("Carpeta creada: %s" % os.path.basename(target.rstrip("\\/")))

    def op_delete(self):
        try:
            p = self.panels[self.active]
            srcs = self.selected_entries()
            if not srcs:
                return
        except Exception as ex:
            log_error(ex)
            self.dialog_message("Borrar", ["Error:", str(ex)], error=True)
            return
        names = ", ".join(e.name for e in srcs[:3])
        if len(srcs) > 3:
            names += " ..."
        if not self.dialog_confirm(
            "Borrar",
            [
                "\u00bfBorrar %d elemento(s)?" % len(srcs),
                names,
                "",
                "Esta accion no se puede deshacer.",
            ],
        ):
            return

        errors = []
        for e in srcs:
            try:
                if os.path.isdir(e.path) and not os.path.islink(e.path):
                    shutil.rmtree(e.path, onerror=self._on_rm_error)
                else:
                    try:
                        os.remove(e.path)
                    except PermissionError:
                        os.chmod(e.path, stat.S_IWRITE)
                        os.remove(e.path)
            except OSError as ex:
                errors.append("%s: %s" % (e.name, ex))

        p.marked.clear()
        p.reload()
        self.panels[1 - self.active].reload()
        if errors:
            self.dialog_message("Borrar", errors[:9], error=True)
        else:
            self.flash("Borrado: %d elemento(s)" % len(srcs))

    def op_changedrive(self):
        p = self.panels[self.active]
        default = p.path[:2] if p.path and len(p.path) > 1 and p.path[1] == ":" else "C:"
        val = self.dialog_input("Cambiar unidad o ruta", "Unidad o carpeta:", default)
        if not val:
            return
        path = os.path.expandvars(os.path.expanduser(val.strip().strip('"')))
        if len(path) == 2 and path[1] == ":":
            path += "\\"
        try:
            path = os.path.abspath(path)
        except OSError:
            return
        if not os.path.isdir(path):
            self.dialog_message("Cambiar unidad", ["La ruta no existe:", path], error=True)
            return
        p.path = path
        p.reload()
        p.index = 0

    def op_refresh(self):
        self.panels[0].reload()
        self.panels[1].reload()
        self.flash("Paneles actualizados")

    def op_help(self):
        lines = []
        width = max(10, self.scr.w - 1)
        for raw in HELP_TEXT.split("\n"):
            lines.extend(wrap_text(raw, width))
        self._view_split = None
        self.pager_blocking("Ayuda de WorkCommander", lines)
        self.draw()

    def op_about(self):
        self.dialog_message(
            "Acerca de",
            [
                "WorkCommander 1.2",
                "Gestor de archivos de doble panel para consola Windows.",
                "Inspirado en el clasico Norton Commander.",
                "Python + API de consola Win32.",
            ],
        )

    def op_quit(self):
        self.running = False

    # -- orden y opciones -------------------------------------------------
    def _set_sort(self, key):
        p = self.panels[self.active]
        p.sort_key = key
        p.sort_rev = False
        p.reload()

    def op_sort_name(self):
        self._set_sort("name")

    def op_sort_ext(self):
        self._set_sort("ext")

    def op_sort_date(self):
        self._set_sort("date")

    def op_sort_size(self):
        self._set_sort("size")

    def op_sort_rev(self):
        p = self.panels[self.active]
        p.sort_rev = not p.sort_rev
        p.reload()

    def op_toggle_hidden(self):
        self.show_hidden = not self.show_hidden
        self.panels[0].reload()
        self.panels[1].reload()
        self.flash("Archivos ocultos: %s" % ("visibles" if self.show_hidden else "ocultos"))

    # -- dibujo del marco -------------------------------------------------
    def draw_menubar(self):
        scr = self.scr
        scr.fill(0, 0, scr.w, 1, " ", C_MENUBAR)
        scr.put(1, 0, " WorkCommander ", C_TITLE)
        x = len(" WorkCommander ") + 2
        self.menu_x = []
        for i, (name, _items) in enumerate(MENUS):
            label = " %s " % name
            self.menu_x.append(x)
            attr = C_MENU_ACTIVE if (self.menu_open and i == self.menu_idx) else C_MENUBAR
            scr.put(x, 0, label, attr)
            x += len(label)
        right = "F9 Menu   F10 Salir   " + time.strftime("%H:%M:%S")
        if len(right) < scr.w:
            scr.put(scr.w - len(right), 0, right, C_MENUBAR)

    def draw_status(self):
        scr = self.scr
        y = scr.h - 2
        scr.fill(0, y, scr.w, 1, " ", C_STATUS)
        p = self.panels[self.active]
        e = p.current()

        if time.time() - self.flash_time < 4.0 and self.flash_text:
            left = " " + self.flash_text
            attr = C_ALERT if self.flash_error else C_OK
        else:
            attr = C_STATUS
            if e is None:
                left = " Sin elementos"
            elif e.is_drive:
                left = " Unidad %s   Pulse Enter para abrir" % e.name
            elif e.is_parent:
                left = " ..\\   (subir un nivel)"
            elif e.is_dir:
                left = " %s\\   <DIR>" % e.name
            else:
                left = " %s   %s" % (e.name, size_label(e.size))
            if p.marked:
                left += "   [%d marcados]" % len(p.marked)

        right = ""
        if p.path:
            try:
                free = human_size(shutil.disk_usage(p.path).free)
            except OSError:
                free = "?"
            right = "Libre: %s   " % free
        right += time.strftime("%d/%m/%Y %H:%M")

        room = max(1, scr.w - len(right) - 2)
        scr.put(0, y, left[:room], attr)
        if len(right) < scr.w:
            scr.put(scr.w - len(right), y, right, C_STATUS)

    def draw_keybar(self):
        scr = self.scr
        y = scr.h - 1
        labels = ["Ayuda", "Refr.", "Ver", "Editar", "Copiar", "Mover", "Nueva", "Borrar", "Menu", "Salir"]
        scr.fill(0, y, scr.w, 1, " ", C_KEYBAR)

        keys = [str(i + 1) for i in range(len(labels))]
        segs = [len(keys[i]) + 1 + len(labels[i]) for i in range(len(labels))]
        total = sum(segs) + len(labels) - 1
        if total <= scr.w:
            gaps = [1] * (len(labels) - 1)
            extra = scr.w - total
            i = 0
            while extra > 0:
                gaps[i % len(gaps)] += 1
                extra -= 1
                i += 1
            x = 0
            for i, label in enumerate(labels):
                scr.put(x, y, keys[i], C_KEYCHIP)
                scr.put(x + len(keys[i]), y, " " + label, C_KEYBAR)
                x += segs[i]
                if i < len(gaps):
                    x += gaps[i]
            return

        # Ventanas angostas: columnas fijas con etiquetas recortadas.
        slot = max(6, scr.w // 10)
        for i, label in enumerate(labels):
            sx = i * slot
            if sx >= scr.w:
                break
            sw = (scr.w - sx) if i == 9 else slot
            scr.fill(sx, y, sw, 1, " ", C_KEYBAR)
            chip = " %d " % (i + 1)
            if len(chip) <= sw:
                scr.put(sx, y, chip, C_KEYCHIP)
                avail = sw - len(chip)
                if avail > 0:
                    scr.put(sx + len(chip), y, (" " + label)[:avail], C_KEYBAR)

    def _draw_viewer(self, scr, v, x, y, w, h, active):
        if w < 10 or h < 5:
            return
        scr.fill(x, y, w, h, " ", C_VIEW)
        scr.box(x, y, w, h, C_FRAME_ACTIVE if active else C_FRAME, v["title"])
        disp = v["disp"]
        page = max(1, h - 2)
        top = v["top"]
        top = max(0, min(top, max(0, len(disp) - page)))
        v["top"] = top
        for i in range(page):
            if top + i >= len(disp):
                break
            line_text = disp[top + i][: w - 2]
            scr.put(x + 1, y + 1 + i, line_text.ljust(w - 2), C_VIEW)
        pos = "Lineas %d-%d de %d" % (
            min(top + 1, len(disp)),
            min(top + page, len(disp)),
            len(disp),
        )
        bar = " %s | %s | Esc cerrar" % (v["info"], pos)
        scr.put(x + 1, y + h - 1, bar[: w - 2].ljust(w - 2), C_STATUS)

    def draw(self):
        scr = self.scr
        scr.sync_size()
        if scr.w < 40 or scr.h < 12:
            scr.clear(C_NORMAL)
            scr.put(0, 0, "Consola demasiado peque\u00f1a.", C_ALERT)
            scr.put(0, 1, "Agrande la ventana a 40x12 como minimo.", C_NORMAL)
            scr.flush()
            self.last_draw = time.time()
            return

        scr.clear(C_NORMAL)
        self.draw_menubar()

        panel_h = scr.h - 3
        left_w = scr.w // 2
        regions = [(0, 1, left_w, panel_h), (left_w, 1, scr.w - left_w, panel_h)]
        for side in (0, 1):
            x, y, w, h = regions[side]
            v = self.viewers[side]
            if v is not None:
                self._draw_viewer(scr, v, x, y, w, h, self.active == side)
            else:
                self.panels[side].draw(x, y, w, h, self.active == side)

        self.draw_status()
        self.draw_keybar()
        
        # Dibujar cursor estilo MS-DOS (bloque rectangular) en posicion del mouse
        if self.mouse_over and 0 <= self.mouse_x < scr.w and 0 <= self.mouse_y < scr.h:
            idx = self.mouse_y * scr.w + self.mouse_x
            if idx < len(scr.grid):
                ch, attr = scr.grid[idx]
                # Invertir colores para simular bloque
                fg = attr & 0x0F
                bg = (attr >> 4) & 0x0F
                new_attr = (fg << 4) | bg
                scr.grid[idx] = (ch, new_attr)
        
        scr.flush()
        self.last_draw = time.time()

    # -- menu -------------------------------------------------------------
    def _first_actionable(self, idx):
        items = MENUS[idx][1]
        for i, (_label, action) in enumerate(items):
            if action is not None:
                return i
        return 0

    def _menu_move(self, delta):
        items = MENUS[self.menu_idx][1]
        i = self.item_idx
        for _ in range(len(items)):
            i = (i + delta) % len(items)
            if items[i][1] is not None:
                self.item_idx = i
                return

    def draw_menu(self):
        scr = self.scr
        _name, items = MENUS[self.menu_idx]
        labels = [l for l, _a in items if l]
        w = max([len(l) for l in labels] + [len(_name) + 4]) + 10
        w = min(max(24, w), scr.w - 2)
        x = min(self.menu_x[self.menu_idx] if self.menu_x else 1, scr.w - w - 1)
        x = max(0, x)
        h = len(items) + 2
        if 1 + h > scr.h:
            h = scr.h - 1
        if x + 1 + w <= scr.w and 2 + h <= scr.h:
            scr.fill(x + 1, 2, w, h, " ", C_SHADOW)
        scr.fill(x, 1, w, h, " ", C_DLG_BG)
        scr.box(x, 1, w, h, C_FRAME)

        for i, (label, action) in enumerate(items):
            yy = 2 + i
            if yy >= 1 + h - 1:
                break
            if action is None:
                scr.put(x, yy, ML + H * (w - 2) + MR, C_FRAME)
                continue
            attr = C_SELECT if i == self.item_idx else C_DLG_BG
            scr.fill(x + 1, yy, w - 2, 1, " ", attr)
            scr.put(x + 2, yy, label, attr)
            hint = HINTS.get(action, "")
            if hint and len(label) + len(hint) + 4 < w:
                scr.put(x + w - 2 - len(hint), yy, hint, attr)

    def menu_loop(self):
        self.menu_open = True
        self.menu_idx = 0
        self.item_idx = 0
        while True:
            self.draw()
            self.draw_menu()
            self.scr.flush()
            key = read_key()
            if not key:
                continue
            kind, val = key
            if kind == "mouse":
                self.mouse_x = val["x"]
                self.mouse_y = val["y"]
                self.mouse_over = True
                continue
            
            if kind == "special":
                if val == "C":
                    break
                if val == "D":
                    self.running = False
                    break
                if val == "H":
                    self._menu_move(-1)
                    continue
                if val == "P":
                    self._menu_move(1)
                    continue
                if val in ("K", "M"):
                    step = -1 if val == "K" else 1
                    self.menu_idx = (self.menu_idx + step) % len(MENUS)
                    self.item_idx = self._first_actionable(self.menu_idx)
                    continue
                continue

            if val == "\x1b":
                break
            if val == "\t":
                self.menu_idx = (self.menu_idx + 1) % len(MENUS)
                self.item_idx = self._first_actionable(self.menu_idx)
                continue
            if val in ("\r", " "):
                _label, action = MENUS[self.menu_idx][1][self.item_idx]
                if action:
                    self.menu_open = False
                    getattr(self, action)()
                    return
                continue
            if val and len(val) == 1 and val.lower() in string.ascii_lowercase:
                items = MENUS[self.menu_idx][1]
                for i, (label, action) in enumerate(items):
                    if action and label.lower().startswith(val.lower()):
                        self.item_idx = i
                        break

        self.menu_open = False

    # -- bucle de teclas --------------------------------------------------
    def handle_key(self, key):
        kind, val = key
        p = self.panels[self.active]
        
        # Si hay un visor abierto en el panel activo, enrutar teclas a el.
        v = self.viewers[self.active]
        if v is not None:
            scr = self.scr
            panel_h = scr.h - 3
            page = max(1, panel_h - 2)
            disp = v["disp"]
            if kind == "char":
                if val in ("\x1b", "q", "Q"):
                    self.viewers[self.active] = None
                return
            if kind == "special":
                if val == "H":
                    v["top"] = max(0, v["top"] - 1)
                elif val == "P":
                    v["top"] = min(max(0, len(disp) - page), v["top"] + 1)
                elif val == "I":
                    v["top"] = max(0, v["top"] - page)
                elif val == "Q":
                    v["top"] = min(max(0, len(disp) - page), v["top"] + page)
                elif val == "G":
                    v["top"] = 0
                elif val == "O":
                    v["top"] = max(0, len(disp) - page)
                elif val in ("K", "M"):
                    self.active = 0 if val == "K" else 1
                elif val == "\x0f":
                    self.active = 1 - self.active
            elif val in ("\t", "\x0f"):
                self.active = 1 - self.active
            return
        
        if kind == "special":
            if val == "H":
                p.move(-1)
            elif val == "P":
                p.move(1)
            elif val == "K":
                self.active = 0
            elif val == "M":
                self.active = 1
            elif val == "G":
                p.index = 0
            elif val == "O":
                p.index = max(0, len(p.entries) - 1)
            elif val == "I":
                p.move(-self.page_size())
            elif val == "Q":
                p.move(self.page_size())
            elif val == "R":
                self.toggle_mark()
            elif val == "S":
                self.op_delete()
            elif val == ";":
                self.op_help()
            elif val == "<":
                self.op_refresh()
            elif val == "=":
                self.op_view()
            elif val == ">":
                self.op_edit()
            elif val == "?":
                self.op_copy()
            elif val == "@":
                self.op_move()
            elif val == "A":
                self.op_mkdir()
            elif val == "B":
                self.op_delete()
            elif val == "C":
                self.menu_loop()
            elif val == "D":
                self.op_quit()
            elif val == "\x0f":
                self.active = 1 - self.active
            return

        if val == "\r":
            self.op_enter()
        elif val in ("\t", "\x0f"):
            self.active = 1 - self.active
        elif val == "\x1b":
            pass
        elif val == "\x08":
            self.op_up()
        elif val == "\x12":
            self.op_refresh()
        elif val == "\x03":
            self.op_quit()
        elif val and len(val) == 1 and val >= " ":
            self.quick_search(val)

    def handle_mouse(self, ev):
        scr = self.scr
        mx, my = ev["x"], ev["y"]
        button = ev["button"]
        flags = ev["flags"]
        
        # Actualizar posicion del mouse
        self.mouse_x = mx
        self.mouse_y = my
        self.mouse_over = (0 <= mx < scr.w and 0 <= my < scr.h)
        
        # Click izquierdo (button & 1, sin movimiento)
        if button & 0x1 and flags == 0:
            panel_h = scr.h - 3
            if 1 <= my < 1 + panel_h:
                mid = scr.w // 2
                if mx < mid:
                    self.active = 0
                else:
                    self.active = 1
                # Solo seleccionar entrada si no hay visor en ese lado.
                if self.viewers[self.active] is None:
                    p = self.panels[self.active]
                    list_y = 1 + 3
                    row = my - list_y
                    if 0 <= row < panel_h - 4:
                        idx = p.offset + row
                        if 0 <= idx < len(p.entries):
                            p.index = idx

    # -- ejecucion --------------------------------------------------------
    def run(self):
        scr = self.scr
        self.draw()
        try:
            while self.running:
                if scr.sync_size():
                    self.draw()
                
                # Revisar eventos de consola (teclado + mouse)
                hin = kernel32.GetStdHandle(STD_INPUT_HANDLE)
                num_events = wintypes.DWORD(0)
                if kernel32.GetNumberOfConsoleInputEvents(hin, ctypes.byref(num_events)) and num_events.value > 0:
                    try:
                        key = read_key()
                    except Exception as ex:
                        log_error(ex)
                        continue
                    if key is not None:
                        try:
                            if key[0] == "mouse":
                                self.handle_mouse(key[1])
                            else:
                                self.handle_key(key)
                        except Exception as ex:
                            log_error(ex)
                        if self.running:
                            try:
                                self.draw()
                            except Exception as ex:
                                log_error(ex)
                else:
                    if time.time() - self.last_draw >= 1.0:
                        try:
                            self.draw()
                        except Exception as ex:
                            log_error(ex)
                    time.sleep(0.02)
        except KeyboardInterrupt:
            pass
        except Exception as ex:
            log_error(ex)
        finally:
            scr.cleanup()


def log_error(exc):
    try:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workcommander_error.log")
    except Exception:
        path = os.path.join(os.getcwd(), "workcommander_error.log")
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write("=" * 70 + "\n")
            f.write(time.strftime("%Y-%m-%d %H:%M:%S") + "\n")
            traceback.print_exc(file=f)
            f.write("\n")
    except Exception:
        pass


def main():
    start = None
    for arg in sys.argv[1:]:
        if not arg.startswith("-") and os.path.isdir(arg):
            start = arg
            break
    try:
        app = WorkCommander(start)
    except Exception as ex:
        log_error(ex)
        print("No se pudo iniciar WorkCommander: %s" % ex)
        return 1

    if "--selftest" in sys.argv:
        try:
            app.draw()
            return 0
        finally:
            app.scr.cleanup()

    try:
        app.run()
    except Exception as ex:
        log_error(ex)
    return 0


if __name__ == "__main__":
    sys.exit(main())
