#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruebas sin consola interactiva para WorkCommander.

Se usa una pantalla falsa para validar el dibujado y las operaciones de
archivos sin abrir una ventana de CMD.
"""

import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import workcommander as wc  # noqa: E402

TL, TR, BL, BR, H, V, ML, MR = wc.TL, wc.TR, wc.BL, wc.BR, wc.H, wc.V, wc.ML, wc.MR


class FakeScreen:
    def __init__(self, w=100, h=32):
        self.w = w
        self.h = h
        self.grid = [(" ", 0)] * (w * h)
        self.frames = 0

    def sync_size(self, force=False):
        return False

    def clear(self, attr=wc.C_NORMAL):
        self.grid = [(" ", attr)] * (self.w * self.h)

    def put(self, x, y, text, attr=wc.C_NORMAL):
        if not text or y < 0 or y >= self.h:
            return
        for i, ch in enumerate(text):
            xx = x + i
            if 0 <= xx < self.w:
                self.grid[y * self.w + xx] = (ch, attr)

    def fill(self, x, y, w, h, ch, attr=wc.C_NORMAL):
        for yy in range(max(0, y), min(self.h, y + h)):
            for xx in range(max(0, x), min(self.w, x + w)):
                self.grid[yy * self.w + xx] = (ch, attr)

    def box(self, x, y, w, h, attr=wc.C_FRAME, title="", title_attr=wc.C_TITLE):
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

    def hline_sep(self, x, y, w, attr=wc.C_FRAME):
        self.put(x, y, ML + H * (w - 2) + MR, attr)

    def flush(self):
        self.frames += 1
        return True

    def show_cursor(self, visible=True):
        pass

    def cleanup(self):
        pass

    def lines(self):
        out = []
        for y in range(self.h):
            row = "".join(self.grid[y * self.w + x][0] for x in range(self.w))
            out.append(row)
        return out

    def text(self):
        return "\n".join(self.lines())


def make_app(tmp, width=100, height=32):
    scr = FakeScreen(width, height)
    app = wc.WorkCommander(tmp, screen=scr)
    app.draw()
    return app, scr


def test_layout():
    tmp = tempfile.mkdtemp(prefix="wc_layout_")
    try:
        os.makedirs(os.path.join(tmp, "carpeta"))
        with open(os.path.join(tmp, "archivo.txt"), "w", encoding="utf-8") as f:
            f.write("hola")
        app, scr = make_app(tmp)
        lines = scr.lines()
        text = "\n".join(lines)
        assert len(lines) == 32 and all(len(l) == 100 for l in lines), "dimensiones"
        assert "WorkCommander" in lines[0], "barra de menu"
        assert "F10 Salir" in lines[0], "ayuda de salida"
        assert lines[0].count("Archivo") == 1, "menu Archivo"
        assert TL in text and TR in text and BL in text and BR in text, "marcos"
        assert "Nombre" in text, "encabezado de columnas"
        assert "archivo.txt" in text and "carpeta\\" in text, "entradas"
        # El cursor debe estar sobre "..", primera entrada
        assert app.panels[0].current().name == ".."
        # La barra de teclas ocupa la ultima fila
        last = lines[-1]
        assert "Ayuda" in last or "Ayud" in last, "barra de teclas"
        assert "Salir" in last, "tecla 10"
        app.scr.cleanup()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_navigation_and_sort():
    tmp = tempfile.mkdtemp(prefix="wc_nav_")
    try:
        os.makedirs(os.path.join(tmp, "dir_b"))
        os.makedirs(os.path.join(tmp, "dir_a"))
        for name in ("b.txt", "a.log", "c.txt"):
            open(os.path.join(tmp, name), "w").close()
        app, _scr = make_app(tmp)
        p = app.panels[0]
        names = [e.name for e in p.entries]
        assert names[0] == "..", names
        assert names[1:3] == ["dir_a", "dir_b"], names
        # Orden por extension: los .log van antes que los .txt
        app.op_sort_ext()
        files = [e.name for e in p.entries if not e.is_dir]
        assert files == ["a.log", "b.txt", "c.txt"], files
        # Orden inverso
        app.op_sort_rev()
        files = [e.name for e in p.entries if not e.is_dir]
        assert files == ["c.txt", "b.txt", "a.log"], files
        # Navegacion con Enter y retroceso
        p.index = [e.name for e in p.entries].index("dir_a")
        app.op_enter()
        assert p.path.endswith("dir_a"), p.path
        app.op_up()
        assert os.path.normcase(p.path) == os.path.normcase(tmp), p.path
        assert p.current().name == "dir_a", p.current().name
        # Marcado multiple
        p.index = 0
        marks = []
        for name in ("b.txt", "c.txt"):
            p.index = [e.name for e in p.entries].index(name)
            app.toggle_mark()
            marks.append(name)
        assert p.marked == set(marks), p.marked
        assert len(app.selected_entries()) == 2
        # Busqueda rapida
        app.quick_search("b")
        assert p.current().name.startswith("b"), p.current().name
        # La vista de unidades no permite marcar ni operar sobre unidades
        p.path = None
        p.reload()
        assert p.current().is_drive, p.current().name
        assert app.selected_entries() == []
        app.toggle_mark()
        assert p.marked == set(), p.marked
        app.scr.cleanup()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_copy_move_mkdir_delete():
    tmp = tempfile.mkdtemp(prefix="wc_ops_")
    try:
        left = os.path.join(tmp, "izq")
        right = os.path.join(tmp, "der")
        os.makedirs(left)
        os.makedirs(right)
        with open(os.path.join(left, "uno.txt"), "w", encoding="utf-8") as f:
            f.write("contenido uno")
        os.makedirs(os.path.join(left, "sub"))
        with open(os.path.join(left, "sub", "dos.txt"), "w", encoding="utf-8") as f:
            f.write("contenido dos")

        app, _scr = make_app(left)
        app.panels[1].path = right
        app.panels[1].reload()
        app.modal_text = []

        app.dialog_message = lambda *a, **k: app.modal_text.append(a)
        app.dialog_confirm = lambda *a, **k: True
        app._progress = lambda *a, **k: None

        # Copiar archivo
        p = app.panels[0]
        p.index = [e.name for e in p.entries].index("uno.txt")
        app.dialog_input = lambda *a, **k: right
        app.op_copy()
        target = os.path.join(right, "uno.txt")
        assert os.path.isfile(target), os.listdir(right)
        assert open(target, encoding="utf-8").read() == "contenido uno"

        # Copiar carpeta completa
        p.index = [e.name for e in p.entries].index("sub")
        app.op_copy()
        assert os.path.isfile(os.path.join(right, "sub", "dos.txt"))

        # Renombrar
        p.index = [e.name for e in p.entries].index("uno.txt")
        app.dialog_input = lambda *a, **k: "renombrado.txt"
        app.op_move()
        assert os.path.isfile(os.path.join(left, "renombrado.txt"))
        assert not os.path.exists(os.path.join(left, "uno.txt"))

        # Crear carpeta
        app.dialog_input = lambda *a, **k: "nueva"
        p.index = 0
        app.op_mkdir()
        assert os.path.isdir(os.path.join(left, "nueva"))

        # Borrar archivo
        p.index = [e.name for e in p.entries].index("renombrado.txt")
        app.op_delete()
        assert not os.path.exists(os.path.join(left, "renombrado.txt"))
        assert not app.modal_text, app.modal_text

        # Copiar una carpeta sobre un archivo existente debe rechazarse
        os.makedirs(os.path.join(left, "carpeta_origen"))
        with open(os.path.join(right, "carpeta_origen"), "w", encoding="utf-8") as f:
            f.write("archivo")
        p.reload()
        p.index = [e.name for e in p.entries].index("carpeta_origen")
        app.dialog_input = lambda *a, **k: right
        app.modal_text = []
        app.op_copy()
        assert os.path.isdir(os.path.join(left, "carpeta_origen"))
        assert os.path.isfile(os.path.join(right, "carpeta_origen"))
        assert app.modal_text and app.modal_text[-1][0] == "Copiar", app.modal_text

        # Mover un archivo sobre una carpeta existente debe rechazarse
        os.makedirs(os.path.join(left, "bloque"))
        with open(os.path.join(left, "mover.txt"), "w", encoding="utf-8") as f:
            f.write("no mover")
        p.reload()
        p.index = [e.name for e in p.entries].index("mover.txt")
        app.dialog_input = lambda *a, **k: "bloque"
        app.modal_text = []
        app.op_move()
        assert os.path.isdir(os.path.join(left, "bloque"))
        assert os.path.isfile(os.path.join(left, "mover.txt"))
        assert app.modal_text and app.modal_text[-1][0] == "Mover", app.modal_text

        app.scr.cleanup()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_viewer():
    tmp = tempfile.mkdtemp(prefix="wc_view_")
    try:
        path = os.path.join(tmp, "texto.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("linea 1\n" + "x" * 300 + "\nlinea 3\n")
        app, _scr = make_app(tmp)
        captured = {}
        app.pager = lambda title, disp, info="": captured.update(title=title, disp=disp, info=info)
        app.view_file(path)
        assert captured["title"] == "texto.txt"
        assert captured["disp"][0] == "linea 1"
        assert len(captured["disp"][1]) <= max(10, app.scr.w - 1)
        assert captured["disp"][-2:] == ["linea 3", ""] or captured["disp"][-1] == "linea 3"

        # Un INI en UTF-16 con BOM debe abrirse como texto sin preguntar.
        ini = os.path.join(tmp, "oculto.ini")
        with open(ini, "wb") as f:
            f.write("[seccion]\nclave=valor\n".encode("utf-16"))
        captured.clear()
        app.dialog_choice = lambda *a, **k: None
        app.view_file(ini)
        assert captured["title"] == "oculto.ini", captured
        assert captured["disp"][0] == "[seccion]", captured["disp"][:3]
        assert "clave=valor" in captured["disp"], captured["disp"]

        # UTF-16 sin BOM tambien se detecta.
        ini2 = os.path.join(tmp, "sin_bom.ini")
        with open(ini2, "wb") as f:
            f.write("[otra]\r\nvalor=2\r\n".encode("utf-16-le"))
        captured.clear()
        app.view_file(ini2)
        assert "valor=2" in captured["disp"], captured["disp"]

        # Un binario ofrece texto o hexadecimal; el hex se muestra por filas.
        bin_path = os.path.join(tmp, "datos.bin")
        with open(bin_path, "wb") as f:
            f.write(bytes(range(256)) * 4)
        captured.clear()
        app.dialog_choice = lambda *a, **k: "h"
        app.view_file(bin_path)
        assert "hex" in captured["title"].lower(), captured["title"]
        assert captured["disp"][0].startswith("00000000  00 01 02"), captured["disp"][0]
        assert all(len(line) <= app.scr.w - 1 for line in captured["disp"])
        assert "hexadecimal" in captured["info"], captured["info"]

        # Forzar texto sobre un binario: los controles se vuelven puntos.
        captured.clear()
        app.view_file(bin_path, mode="t")
        assert captured["title"] == "datos.bin", captured["title"]
        assert captured["disp"][0].startswith("."), captured["disp"][0]
        assert "texto forzado" in captured["info"], captured["info"]

        # Cancelar la eleccion no abre nada.
        captured.clear()
        app.dialog_choice = lambda *a, **k: None
        app.view_file(bin_path)
        assert not captured, captured

        # Ver archivo por ruta permite rutas que no estan en el panel.
        hidden = os.path.join(tmp, "oculto_manual.ini")
        with open(hidden, "w", encoding="utf-8") as f:
            f.write("[manual]\nx=1\n")
        app.dialog_input = lambda *a, **k: hidden
        captured.clear()
        app.op_view_path()
        assert captured["title"] == "oculto_manual.ini", captured
        assert "[manual]" in captured["disp"], captured["disp"]

        # Ver forzado sobre la entrada actual, en hexadecimal.
        p = app.panels[0]
        p.reload()
        p.index = [e.name for e in p.entries].index("datos.bin")
        app.dialog_choice = lambda *a, **k: "h"
        captured.clear()
        app.op_view_force()
        assert "hex" in captured["title"].lower(), captured["title"]

        # El volcado hexadecimal se adapta a ventanas estrechas.
        narrow = wc.hex_dump_lines(b"ABC", 40)
        assert len(narrow[0]) <= 40, narrow[0]
        assert narrow[0].endswith("|ABC|"), narrow[0]

        # El dialogo de eleccion devuelve la tecla elegida.
        real_read = wc.read_key
        wc.read_key = lambda: ("char", "h")
        try:
            assert (
                wc.WorkCommander.dialog_choice(
                    app, "Elegir", ["Modo:"], [("t", "Texto"), ("h", "Hex")]
                )
                == "h"
            )
            wc.read_key = lambda: ("char", "\r")
            assert (
                wc.WorkCommander.dialog_choice(
                    app, "Elegir", ["Modo:"], [("t", "Texto"), ("h", "Hex")]
                )
                == "t"
            )
        finally:
            wc.read_key = real_read

        app.scr.cleanup()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


class FakeKernel:
    """Imita lo minimo de kernel32 que usa la clase Screen."""

    def __init__(self):
        self.written = None
        self.rect = None
        self.title = ""
        self.input_mode = None

    @staticmethod
    def _obj(arg):
        return getattr(arg, "_obj", arg)

    def GetStdHandle(self, which):
        return 1

    def GetConsoleScreenBufferInfo(self, handle, ptr):
        info = self._obj(ptr)
        info.dwSize = wc.COORD(100, 30)
        info.srWindow = wc.SMALL_RECT(0, 0, 99, 29)
        info.dwMaximumWindowSize = wc.COORD(120, 50)
        return 1

    def WriteConsoleOutputW(self, handle, buf, size, coord, region_ptr):
        total = size.X * size.Y
        self.written = [(buf[i].Char, buf[i].Attributes) for i in range(total)]
        self.rect = self._obj(region_ptr)
        return 1

    def SetConsoleScreenBufferSize(self, handle, coord):
        return 1

    def SetConsoleCursorInfo(self, handle, ptr):
        return 1

    def SetConsoleCursorPosition(self, handle, coord):
        return 1

    def SetConsoleTitleW(self, title):
        self.title = title
        return 1

    def GetConsoleTitleW(self, buf, size):
        buf.value = "CMD original"
        return len(buf.value)

    def GetConsoleMode(self, handle, ptr):
        self._obj(ptr).value = 0x01F7
        return 1

    def SetConsoleMode(self, handle, mode):
        self.input_mode = mode
        return 1


def test_screen_win32_layer():
    real = wc.kernel32
    fake = FakeKernel()
    wc.kernel32 = fake
    try:
        scr = wc.Screen()
        assert (scr.w, scr.h) == (100, 30), (scr.w, scr.h)
        scr.clear(wc.C_NORMAL)
        scr.put(0, 0, "Hola", wc.C_TITLE)
        scr.box(1, 1, 10, 5)
        assert scr.flush() is True
        assert fake.written is not None
        assert len(fake.written) == 100 * 30
        assert "".join(ch for ch, _a in fake.written[:4]) == "Hola"
        assert fake.written[0][1] == wc.C_TITLE
        row = 100 + 1
        assert fake.written[row][0] == wc.TL
        assert fake.rect.Left == 0 and fake.rect.Top == 0
        assert fake.title == "WorkCommander"
        # Repintar no debe romper nada
        scr.clear(wc.C_NORMAL)
        scr.put(5, 5, "\u00e1\u00e9\u00ed\u00f3\u00fa \u2588", wc.C_DIR)
        assert scr.flush() is True
        scr.cleanup()
        assert fake.title == "CMD original", fake.title
    finally:
        wc.kernel32 = real


def main():
    tests = [
        test_layout,
        test_navigation_and_sort,
        test_copy_move_mkdir_delete,
        test_viewer,
        test_screen_win32_layer,
    ]
    failed = 0
    for test in tests:
        try:
            test()
            print("OK   %s" % test.__name__)
        except Exception as ex:
            failed += 1
            print("FAIL %s: %s" % (test.__name__, ex))
    print("-" * 50)
    print("%d/%d pruebas correctas" % (len(tests) - failed, len(tests)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
