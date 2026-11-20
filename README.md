# WorkCommander

Gestor de archivos de **doble panel** para la consola de Windows, inspirado en el
clásico **Norton Commander**. Se ejecuta dentro de CMD o Windows Terminal, ocupa
toda la ventana y permite navegar por el sistema de archivos, ver y editar
archivos, y copiar, mover, renombrar, crear y borrar elementos con el teclado.

El proyecto es **autocontenido**: un solo archivo Python (`workcommander.py`) que
usa únicamente la biblioteca estándar y llamadas Win32 mediante `ctypes`. No
requiere `pip install`, ni ANSI/VT, ni bibliotecas de terceros en tiempo de
ejecución.

---

## 1. Ficha técnica

| Dato | Valor |
|---|---|
| Nombre | WorkCommander |
| Versión | 1.2 |
| Tipo | Aplicación de consola interactiva (TUI) |
| Plataforma | Windows (validado en Windows 10/11, CMD y Windows Terminal) |
| Lenguaje | Python 3.8+ (validado con Python 3.12.5) |
| Dependencias de ejecución | Ninguna externa: `ctypes`, `os`, `shutil`, `msvcrt`, `stat`, `string`, `subprocess`, `sys`, `time`, `datetime` |
| Renderizado | Doble búfer propio + `WriteConsoleOutputW` (sin ANSI/VT) |
| Entrada | `msvcrt.getwch()` (teclas normales y extendidas) |
| Persistencia | Ninguna de configuración/historial; se genera `workcommander_error.log` solo si ocurre un error |
| Empaquetado | PyInstaller 6.22.3, modo `--onefile --console` |
| Ejecutable | `dist\WorkCommander.exe` — 7.426.736 bytes |
| SHA-256 del ejecutable | `D4E08CA43730F57F3A14970D59803B5668F8275DFF793FED3E8B3BD2E36E2410` |
| Código fuente | `workcommander.py` — 1.931 líneas, 65.967 bytes |
| SHA-256 del fuente | `A2B1EE1FD639F16AA0E0AB2EC6AEA3F95FA420D6B483A4BD83B3B9CD4AC11122` |
| Pruebas | `tests\headless_test.py` — 471 líneas, 16.618 bytes, 5/5 correctas |
| SHA-256 de las pruebas | `C5ECB2265BF7BC3D17C8B17E8E82D36B8B908BEF21BD5629D2B5FD1D0F2C5AE8` |
| Fecha de esta revisión | 19/11/2026 |

> Los hashes y tamaños corresponden al estado descrito en este documento. Si se
> modifica el código, hay que reconstruir el ejecutable y actualizar la ficha.

---

## 2. Inicio rápido

Hay tres formas de ejecutarlo, de la más cómoda a la más manual:

### 2.1. Ejecutable incluido (no requiere Python)

```bat
dist\WorkCommander.exe
```

También se puede abrir desde el Explorador con doble clic. Al ser una
aplicación de consola, Windows abre una ventana de CMD y WorkCommander toma el
control de ella.

### 2.2. Lanzador para CMD (requiere Python instalado)

```bat
WorkCommander.bat
```

El lanzador:

1. Comprueba que `workcommander.py` esté junto al `.bat`.
2. Busca `py` (lanzador oficial de Python) y, si no existe, `python`.
3. Ejecuta el programa propagando el código de salida con `exit /b %errorlevel%`.
4. Si falta Python o el fuente, muestra un mensaje y devuelve código 1.

Se le pueden pasar argumentos; por ejemplo, una carpeta inicial:

```bat
WorkCommander.bat "D:\Proyectos"
```

### 2.3. Directamente con Python

```bat
py -3 workcommander.py
py -3 workcommander.py "C:\Users\Pablo\Documentos"
```

### 2.4. Comprobación automática de arranque

```bat
dist\WorkCommander.exe --selftest
echo %errorlevel%
```

`--selftest` construye la pantalla, dibuja un fotograma completo, restaura la
consola y devuelve `0` si todo fue bien. **Requiere una consola interactiva
real**; si se ejecuta con la salida redirigida o sin consola, falla con
`No hay una consola interactiva disponible.` (ver sección 19).

### 2.5. Pruebas headless

```bat
py -3 tests\headless_test.py
```

Salida esperada:

```
OK   test_layout
OK   test_navigation_and_sort
OK   test_copy_move_mkdir_delete
OK   test_viewer
OK   test_screen_win32_layer
--------------------------------------------------
5/5 pruebas correctas
```

---

## 3. Requisitos

- **Windows** (el programa aborta en otros sistemas con
  `WorkCommander solo funciona en Windows.`).
- **Python 3.8 o superior** si se ejecuta el fuente o el `.bat`. El ejecutable de
  `dist\` ya incluye el intérprete.
- Una **consola interactiva** con ventana de al menos **40 columnas × 12 filas**.
  Por debajo de ese tamaño se muestra un aviso en lugar de la interfaz.
- Una **fuente de consola con caracteres de dibujo de caja** (Consolas, Lucida
  Console, Cascadia Mono, etc.). Si la fuente no los muestra bien, se puede
  activar el modo ASCII (sección 12.4).
- Permisos del usuario para las rutas sobre las que se opere. WorkCommander no
  eleva privilegios: los errores de acceso se muestran en un diálogo.

No se necesita:

- Conexión a Internet (salvo para que `build_exe.bat` instale PyInstaller).
- Variables de entorno especiales.
- Terminal con soporte ANSI.
- Ratón (opcional: la aplicación soporta mouse para moverse y abrir archivos,
  además del teclado).

---

## 4. Aspecto de la interfaz

La pantalla se divide en cinco zonas:

```
 WorkCommander   Archivo  Opciones  Ayuda                F9 Menu   F10 Salir   21:19:35
╔════════════ C:\Users\Pablo\Documentos ════════════╗╔══════════════ D:\Backup ══════════════╗
║Nombre          Tamaño      Fecha                   ║║Nombre          Tamaño      Fecha      ║
╠════════════════════════════════════════════════════╣╠═══════════════════════════════════════╣
║..                                                  ║║..                                     ║
║Proyectos\                                          ║║2025\                                  ║
║informe final.txt  120.345 19/11/26 18:30           ║║fotos\                                 ║
║notas.md             4.210 19/11/26 18:30           ║║respaldo.zip   5.500.000 19/11/26 18:30║
║                                                    ║║LEEME.txt            900 19/11/26 18:30║
║                                                    ║║                                       ║
║                                                    ║║                                       ║
║                                                    ║║                                       ║
║                                                    ║║                                       ║
╚════════════════════════════════════════════════════╝╚═══════════════════════════════════════╝
 informe final.txt   120.345 bytes              Libre: 82,4 GB   19/11/2026 21:19
 1 Ayuda  2 Refr.  3 Ver  4 Editar  5 Copiar  6 Mover  7 Nueva  8 Borrar  9 Menu  0 Salir
```

> El ejemplo es ilustrativo; el ancho real de las columnas se adapta a la ventana.

### 4.1. Barra de menú (fila 0)

- A la izquierda: ` WorkCommander ` y los menús **Archivo**, **Opciones**,
  **Ayuda**.
- A la derecha, si cabe: `F9 Menu   F10 Salir   HH:MM:SS`.
- El reloj se actualiza en cada redibujado; en reposo, como máximo una vez por
  segundo.

### 4.2. Paneles (filas 1 a `alto-3`)

- Dos paneles simétricos: izquierdo y derecho. El ancho se reparte con
  `ancho // 2` para el izquierdo y el resto para el derecho.
- El **panel activo** se distingue por el color del marco y del título: cian
  normal si está inactivo, blanco brillante si está activo.
- Cada panel tiene un marco doble, un título centrado con la ruta actual (o
  `Unidades`), una fila de encabezados y una línea separadora.
- Columnas:
  - **Nombre**: siempre.
  - **Tamaño**: si el ancho interior es al menos 34.
  - **Fecha**: si el ancho interior es al menos 44.
  - En ventanas estrechas se van ocultando columnas y el nombre ocupa todo.
- Los nombres demasiado largos se truncan y terminan en `>`.
- Las carpetas se dibujan con `\` final y en blanco brillante.
- `..` (subir un nivel) se dibuja en color de marco.
- La entrada bajo el cursor se resalta con fondo cian; si además está marcada,
  se usa el color de marcado + cursor.
- Las entradas marcadas con `Insert` se muestran en amarillo.
- El desplazamiento vertical (`offset`) se ajusta automáticamente para mantener
  visible el cursor.

### 4.3. Barra de estado (penúltima fila)

- A la izquierda:
  - Un mensaje temporal de éxito o error (4 segundos), o
  - la descripción de la entrada actual: `..\ (subir un nivel)`, `<DIR>`, nombre
    y tamaño exacto, o `Unidad C:\ Pulse Enter para abrir`, o `Sin elementos`.
  - Si hay marcas: `   [N marcados]`.
- A la derecha: espacio libre del volumen actual (`Libre: 82,4 GB`) y la fecha y
  hora actuales.
- Los mensajes de error se muestran en rojo brillante sobre cian; los de éxito
  en blanco brillante sobre cian.

### 4.4. Barra de teclas (última fila)

Muestra diez segmentos: `1 Ayuda`, `2 Refr.`, `3 Ver`, `4 Editar`, `5 Copiar`,
`6 Mover`, `7 Nueva`, `8 Borrar`, `9 Menu`, `0 Salir`.

Los dígitos `1`–`0` son **etiquetas visuales** que representan `F1`–`F10`; no son
teclas de acceso. Escribir un número en el panel realiza búsqueda rápida. Si la
ventana es estrecha, la barra usa columnas fijas y recorta las etiquetas.

### 4.5. Paleta de colores

Los atributos son bytes de consola Win32: nibble bajo = color de texto, nibble
alto = color de fondo.

| Constante | Valor | Significado |
|---|---|---|
| `C_NORMAL` | `0x17` | Gris claro sobre azul (fondo general) |
| `C_FRAME` | `0x1B` | Cian sobre azul (marco inactivo) |
| `C_FRAME_ACTIVE` | `0x1F` | Blanco brillante sobre azul (marco activo) |
| `C_TITLE` | `0x30` | Negro sobre cian (títulos) |
| `C_DIR` | `0x1F` | Blanco brillante (carpetas) |
| `C_MARK` | `0x1E` | Amarillo (marcados) |
| `C_SELECT` | `0x30` | Negro sobre cian (cursor) |
| `C_SELECT_MARK` | `0x3F` | Blanco brillante sobre cian (cursor + marca) |
| `C_STATUS` | `0x30` | Negro sobre cian (barra de estado) |
| `C_KEYBAR` | `0x30` | Negro sobre cian (barra de teclas) |
| `C_KEYCHIP` | `0x70` | Negro sobre gris claro (chip de tecla) |
| `C_MENUBAR` | `0x70` | Negro sobre gris claro (barra de menú) |
| `C_MENU_ACTIVE` | `0x30` | Menú desplegado activo |
| `C_DLG_BG` | `0x17` | Fondo de diálogo |
| `C_DLG_TEXT` | `0x1F` | Texto de diálogo |
| `C_FIELD` | `0x0F` | Campo de texto |
| `C_CURSOR` | `0xF0` | Blanco sobre negro (cursor de edición) |
| `C_HINT` | `0x1B` | Cian (ayudas y pistas) |
| `C_VIEW` | `0x17` | Visor de archivos |
| `C_ALERT` | `0x3C` | Rojo brillante sobre cian (errores) |
| `C_OK` | `0x3F` | Blanco brillante sobre cian (éxito) |
| `C_BAR_FILL` | `0x1E` | Amarillo (barra de progreso llena) |
| `C_BAR_EMPTY` | `0x18` | Gris sobre azul (barra vacía) |
| `C_SHADOW` | `0x00` | Sombra de diálogos |

---

## 5. Modelo de datos y semántica de las entradas

### 5.1. `Entry`

Representa una fila de un panel. Usa `__slots__` para ahorrar memoria.

| Campo | Tipo | Significado |
|---|---|---|
| `name` | `str` | Nombre mostrado (`..`, `C:\`, nombre de archivo o carpeta) |
| `path` | `str \| None` | Ruta absoluta; `None` para `..` y para unidades |
| `is_dir` | `bool` | Es carpeta (incluye unidades y `..`) |
| `size` | `int` | Tamaño en bytes; `0` para carpetas |
| `mtime` | `float` | Fecha de modificación Unix; `0` si no se pudo leer |
| `is_parent` | `bool` | Es la entrada especial `..` |
| `is_drive` | `bool` | Es una unidad de la vista `Unidades` |
| `hidden` | `bool` | Tenía el atributo Win32 `FILE_ATTRIBUTE_HIDDEN` (`0x2`) |

Reglas:

- En una carpeta normal, `entries[0]` es siempre `..`.
- En la vista de unidades (`panel.path is None`), **no** hay `..`; solo unidades
  existentes, en orden alfabético.
- `is_parent` e `is_drive` nunca son seleccionables para operaciones ni
  marcables. `selected_entries()` y `toggle_mark()` los excluyen explícitamente.
- Las carpetas se ordenan siempre por nombre, antes que los archivos.

### 5.2. `Panel`

| Campo | Significado |
|---|---|
| `app` | Referencia a la aplicación (para `show_hidden`, `flash`, etc.) |
| `path` | Ruta actual, o `None` para la vista de unidades |
| `entries` | Lista de `Entry` ya ordenada |
| `index` | Índice del cursor dentro de `entries` |
| `offset` | Primera fila visible (scroll) |
| `marked` | `set` de **nombres** marcados (no rutas) |
| `sort_key` | `"name"`, `"ext"`, `"date"` o `"size"` |
| `sort_rev` | Invertir el orden |

`marked` guarda nombres porque dentro de una carpeta los nombres son únicos y
así se pueden conservar las marcas tras un `reload()`; en cada recarga se
intersecta con los nombres existentes.

### 5.3. Estado global de `WorkCommander`

| Campo | Significado |
|---|---|
| `scr` | Pantalla (`Screen` real o `FakeScreen` en pruebas) |
| `show_hidden` | Mostrar archivos ocultos; **inicialmente `True`** |
| `active` | Panel activo: `0` izquierdo, `1` derecho |
| `running` | Bucle principal activo |
| `flash_text`, `flash_error`, `flash_time` | Mensaje temporal de la barra de estado |
| `last_draw` | Última vez que se dibujó (para el reloj) |
| `menu_open`, `menu_idx`, `item_idx`, `menu_x` | Estado del menú superior |
| `_prog` | Estado interno del progreso de copia (`None` si no hay copia) |
| `search_buf`, `search_time` | Búsqueda rápida incremental |
| `panels` | `[Panel, Panel]`; ambos arrancan en la misma ruta inicial |

---

## 6. Mapa de teclas

### 6.1. Teclas de función y atajos

| Tecla | Acción | Método interno |
|---|---|---|
| `F1` | Ayuda en el paginador | `op_help` |
| `F2` | Refrescar ambos paneles | `op_refresh` |
| `F3` | Ver archivo (texto, binario o hexadecimal) | `op_view` |
| `F4` | Editar con Notepad | `op_edit` |
| `F5` | Copiar al otro panel | `op_copy` |
| `F6` | Mover / renombrar | `op_move` |
| `F7` | Crear carpeta | `op_mkdir` |
| `F8` | Borrar | `op_delete` |
| `F9` | Abrir menú superior | `menu_loop` |
| `F10` | Salir | `op_quit` |
| `Ctrl+R` | Refrescar | `op_refresh` |
| `Ctrl+C` | Salir | `op_quit` (o `KeyboardInterrupt`) |
| Menú Archivo → Ver forzado | Elegir texto o hexadecimal para el archivo actual | `op_view_force` |
| Menú Archivo → Ver por ruta | Abrir cualquier ruta, incluida una oculta | `op_view_path` |

> En algunas configuraciones de consola, `Ctrl+C` lo intercepta Windows antes de
> llegar a `msvcrt`; en ese caso el bucle principal lo trata como
> `KeyboardInterrupt` y también sale limpiamente.

### 6.2. Navegación

| Tecla | Acción |
|---|---|
| `↑` / `↓` | Mover el cursor una fila |
| `←` | Activar panel izquierdo |
| `→` | Activar panel derecho |
| `Tab` / `Shift+Tab` | Alternar panel activo |
| `Enter` | Entrar en carpeta, abrir unidad, subir con `..`, o abrir archivo con su aplicación asociada |
| `Retroceso` | Subir un nivel (en la raíz de la unidad pasa a la vista de unidades) |
| `Inicio` / `Fin` | Primera / última entrada |
| `RePág` / `AvPág` | Desplazar una página |
| `Insert` | Marcar/desmarcar y avanzar una fila |
| `Supr` | Borrar (alias de `F8`) |
| Letras, números, símbolos imprimibles | Búsqueda rápida |

### 6.3. Códigos internos de `msvcrt`

`read_key()` devuelve una tupla:

- `("char", texto)` para teclas normales.
- `("special", código)` cuando `getwch()` devuelve el prefijo `\x00` o `\xe0`;
  entonces se lee un segundo carácter que identifica la tecla extendida.

| Tecla | Prefijo | Código | Rama en `handle_key` |
|---|---|---|---|
| `↑` | `\xe0`/`\x00` | `H` | `p.move(-1)` |
| `↓` | `\xe0`/`\x00` | `P` | `p.move(1)` |
| `←` | `\xe0`/`\x00` | `K` | panel izquierdo |
| `→` | `\xe0`/`\x00` | `M` | panel derecho |
| `Inicio` | `\xe0`/`\x00` | `G` | índice 0 |
| `Fin` | `\xe0`/`\x00` | `O` | último índice |
| `RePág` | `\xe0`/`\x00` | `I` | `-page_size()` |
| `AvPág` | `\xe0`/`\x00` | `Q` | `+page_size()` |
| `Insert` | `\xe0`/`\x00` | `R` | `toggle_mark()` |
| `Supr` | `\xe0`/`\x00` | `S` | `op_delete()` |
| `F1` | `\x00` | `;` | `op_help()` |
| `F2` | `\x00` | `<` | `op_refresh()` |
| `F3` | `\x00` | `=` | `op_view()` |
| `F4` | `\x00` | `>` | `op_edit()` |
| `F5` | `\x00` | `?` | `op_copy()` |
| `F6` | `\x00` | `@` | `op_move()` |
| `F7` | `\x00` | `A` | `op_mkdir()` |
| `F8` | `\x00` | `B` | `op_delete()` |
| `F9` | `\x00` | `C` | `menu_loop()` |
| `F10` | `\x00` | `D` | `op_quit()` |
| `Shift+Tab` | — | `\x0f` | alternar panel |

Teclas de control normales:

| Tecla | Carácter | Acción |
|---|---|---|
| `Enter` | `\r` | `op_enter()` |
| `Tab` | `\t` | alternar panel |
| `Esc` | `\x1b` | sin efecto en el panel |
| `Retroceso` | `\x08` | `op_up()` |
| `Ctrl+R` | `\x12` | `op_refresh()` |
| `Ctrl+C` | `\x03` | `op_quit()` |

> **Importante:** las letras y símbolos que se escriben en el panel (`A`, `B`,
> `;`, etc.) llegan como `("char", ...)` y se usan para búsqueda rápida, no para
> las funciones. Los códigos `A`–`D`, `;`–`?` solo se interpretan como funciones
> cuando vienen precedidos por `\x00`/`\xe0`.

### 6.4. Teclas dentro del menú

| Tecla | Acción |
|---|---|
| `↑` / `↓` | Mover la selección (salta separadores) |
| `←` / `→` | Cambiar de menú |
| `Tab` | Siguiente menú |
| `Enter` / `Espacio` | Ejecutar la acción |
| Letra | Saltar a la primera acción cuyo texto empiece por esa letra |
| `Esc` | Cerrar el menú |
| `F10` | Salir de la aplicación |

> Si varias acciones empiezan por la misma letra, se elige la primera. Por eso,
> dentro de **Opciones**, la letra `o` siempre selecciona "Ordenar por nombre".

### 6.5. Teclas en diálogos y visor

Diálogo de entrada (`dialog_input`):

| Tecla | Acción |
|---|---|
| Caracteres imprimibles | Insertar en el cursor (máximo 2048) |
| `←` / `→` | Mover el cursor |
| `Inicio` / `Fin` | Ir al principio / final |
| `Retroceso` | Borrar a la izquierda |
| `Supr` | Borrar en el cursor |
| `Enter` | Aceptar y devolver el texto (sin espacios extremos) |
| `Esc` | Cancelar (`None`) |

Confirmación (`dialog_confirm`): `S`, `s`, `Y`, `y` o `Enter` = sí; `N`, `n` o
`Esc` = no. Otras teclas se ignoran.

Elección múltiple (`dialog_choice`): devuelve la clave de la opción pulsada
(`t` para texto, `h` para hexadecimal) o `None` con `Esc`. `Enter` elige la
primera opción. Se usa al abrir un archivo binario y en **Ver forzado**.

Mensaje (`dialog_message`): cualquier tecla lo cierra.

Visor/paginador (`pager`): `↑`/`↓`, `RePág`/`AvPág`, `Inicio`/`Fin`, `q`/`Q`/`Esc`
para salir, `F10` también cierra.

---

## 7. Funcionalidad detallada

### 7.1. Arranque

`main()`:

1. Recorre `sys.argv[1:]` y toma como carpeta inicial el primer argumento que no
   empiece por `-` y que sea un directorio existente.
2. Si no hay carpeta válida, usa `os.getcwd()`.
3. Convierte la ruta a absoluta.
4. Crea `WorkCommander(start)`.
   - Si no se inyecta una pantalla (pruebas), crea `Screen()`.
   - Crea **dos paneles** con la misma ruta inicial.
5. Si se pasó `--selftest`, dibuja una vez, limpia la consola y devuelve `0`.
6. En caso contrario, ejecuta `app.run()`.
7. Cualquier excepción al crear la aplicación se imprime como
   `No se pudo iniciar WorkCommander: ...` y devuelve `1`.

### 7.2. Bucle principal

```text
draw()
mientras running:
    si cambió el tamaño de la consola: draw()
    si hay tecla disponible:
        leer tecla
        handle_key(tecla)
        si sigue running: draw()
    si no:
        si pasó >= 1 segundo desde el último dibujo: draw()   # reloj
        dormir 20 ms
al salir: cleanup() de la consola
```

- El sondeo es de 20 ms; no hay bloqueo esperando teclas, lo que permite
  redibujar el reloj y detectar redimensiones.
- Un redimensionado limpia el búfer y repinta.
- `KeyboardInterrupt` también sale limpiamente.

### 7.3. Navegación

- **Entrar en carpeta**: asigna `p.path = e.path`, recarga y coloca el cursor en
  la primera entrada (normalmente `..`).
- **Entrar en unidad**: `p.path = e.name` (por ejemplo `C:\`), recarga y cursor
  en 0.
- **Abrir archivo**: `os.startfile(e.path)`, es decir, se abre con la aplicación
  asociada de Windows. Esto incluye ejecutables y documentos. Si falla, se
  muestra un diálogo de error.
- **Subir (`..` o Retroceso)**:
  - Si la ruta actual es la raíz (`C:\`), se pasa a la vista de unidades
    (`path = None`) y el cursor queda sobre la unidad de origen.
  - Si no, se sube a `dirname` y el cursor queda sobre el nombre de la carpeta
    de la que se venía (si existe).
- La vista de unidades enumera `A:\` … `Z:\` comprobando `os.path.exists`.

### 7.4. Marcado múltiple

- `Insert` añade o quita el nombre actual de `p.marked` y avanza una fila.
- Las marcas se dibujan en amarillo.
- `selected_entries()`:
  - Si hay marcas, devuelve **solo** las entradas marcadas (excluyendo `..` y
    unidades).
  - Si no hay marcas, devuelve la entrada bajo el cursor, salvo que sea `..` o
    una unidad, en cuyo caso devuelve `[]`.
- Las operaciones de copiar, mover y borrar usan `selected_entries()`.
- Tras copiar, mover o borrar se recargan los paneles; las marcas se limpian
  explícitamente en mover y borrar, y se intersectan por nombre en las recargas.
- En la vista de unidades no se puede marcar ni operar.

### 7.5. Búsqueda rápida

- Cualquier carácter imprimible en el panel llama a `quick_search(ch)`.
- Se acumula en `search_buf` durante 1,2 segundos; después se reinicia.
- Se busca, en orden, la primera entrada cuyo nombre en minúsculas **empiece
  por** el buffer. No hace cíclico: si no hay coincidencia, el cursor no cambia.
- No distingue mayúsculas/minúsculas ni acentos (comparación directa de `str`).

### 7.6. Ver archivo (visor interno)

**F3 abre cualquier archivo listado**, sea texto, binario, INI, UTF-16 o tenga
atributos ocultos. Ya no existe el bloqueo "no se puede mostrar como texto". Si
el archivo está oculto y la opción de mostrar ocultos está desactivada, se puede
abrir con **Archivo > Ver archivo por ruta...**.

`view_file(path, mode=None)`:

1. Lee como máximo **8 MiB + 1 byte** en modo binario.
2. Si leyó más de 8 MiB, marca el contenido como truncado.
3. Detecta si es **UTF-16** por BOM (`FF FE` / `FE FF`) o por el patrón de bytes
   nulos alternos. En ese caso lo trata como texto, aunque contenga `\x00`.
4. Si no es UTF-16 y encuentra un byte `\x00` en los primeros **8 KiB**,
   considera el archivo binario y muestra un diálogo con estas opciones:
   - `(T) Texto`: lo abre como texto, sustituyendo los caracteres de control por
     puntos para que se vean.
   - `(H) Hexadecimal`: muestra un volcado hex con columna ASCII.
   - `Esc`: cancela y vuelve al panel.
   - `Enter`: equivale a `(T) Texto`.
5. Decodifica el texto probando, en orden: BOM UTF-8, UTF-16 con BOM, UTF-16
   sin BOM, **UTF-8** y **cp1252**; como último recurso, cp1252 con reemplazo.
6. Convierte tabuladores en 4 espacios.
7. En texto normal sustituye los caracteres de control por espacios; en texto
   forzado de un binario los sustituye por puntos.
8. Parte las líneas que exceden el ancho de la consola (`ancho - 1`) en trozos.
9. Abre el paginador con el nombre del archivo y, en la barra inferior, el tamaño
   (`size_label`), ` (truncado)` si corresponde y ` texto forzado` cuando se
   abrió un binario como texto.

El volcado hexadecimal se adapta al ancho de la ventana (16, 8 o 4 bytes por
fila) y tiene este formato:

```text
00000000  4D 5A 90 00 03 00 00 00 04 00 00 00 FF FF 00 00  |MZ..............|
00000010  00 00 00 00 40 00 00 00 00 00 00 00 00 00 00 00  |....@...........|
```

El título del paginador añade ` [hex]` en modo hexadecimal.

#### Modos forzados

Además de F3, el menú **Archivo** ofrece:

| Acción | Comportamiento |
|---|---|
| `Ver` (F3) | Modo automático: texto, o elección texto/hex si es binario |
| `Ver forzado (texto/hex)...` | Pregunta siempre el modo y abre el archivo actual sin importar su contenido |
| `Ver archivo por ruta...` | Pide una ruta y abre ese archivo; permite rutas ocultas o fuera del panel |

`Ver archivo por ruta...` usa como valor inicial la ruta del archivo actual (o la
carpeta del panel), expande variables y `~`, acepta rutas relativas y no exige
que el archivo aparezca listado. Es la vía para abrir un archivo oculto cuando
la opción de mostrar ocultos está desactivada.

El visor es de **solo lectura**. No interpreta HTML, Markdown ni secuencias de
escape; muestra el texto o los bytes tal cual. El límite de 8 MiB se aplica
también al volcado hexadecimal.

### 7.7. Editar con Notepad

`op_edit()`:

- Solo actúa sobre archivos (no `..`, unidades ni carpetas).
- Muestra el cursor, limpia la pantalla y lanza `notepad.exe` con la ruta,
  esperando a que se cierre (`subprocess.run`).
- Si `notepad.exe` no se puede lanzar, intenta `os.startfile`.
- Al volver: fuerza redimensionado, oculta el cursor y redibuja.
- No recarga los paneles automáticamente; para ver cambios de tamaño/fecha hay
  que refrescar (`F2`).

### 7.8. Copiar

`op_copy()` usa como destino por defecto la ruta del **otro panel** (o `C:\` si
el otro panel está en la vista de unidades). El usuario puede editar la ruta en
el diálogo.

#### Construcción del destino

| Caso | Destino resultante |
|---|---|
| 1 origen y el destino es una carpeta existente | `destino\nombre_origen` (basename) |
| 1 origen y el destino no existe | la ruta escrita, tal cual (puede crear un archivo con ese nombre) |
| 1 origen y el destino es un archivo existente | esa ruta exacta (se pedirá sobrescribir) |
| Varios orígenes y destino es carpeta existente | `destino\nombre` para cada uno |
| Varios orígenes y destino no es carpeta | Error: `El destino debe ser una carpeta existente.` |

Las rutas relativas se resuelven contra la carpeta del panel activo. Se expanden
variables de entorno (`%VAR%`) y `~`. Se eliminan comillas externas y espacios.

#### Validaciones previas (todas obligatorias)

| Situación | Resultado |
|---|---|
| Origen y destino son la misma ruta | Error `El origen y el destino son el mismo.` |
| Copiar una carpeta sobre un archivo existente | Error `El destino existe y no es una carpeta:` |
| Copiar una carpeta dentro de sí misma o de una subcarpeta | Error `No se puede copiar una carpeta dentro de si misma.` |
| Copiar un archivo sobre una carpeta existente | Error `El destino es una carpeta y el origen es un archivo:` |
| Hay destinos existentes | Una única confirmación `¿Sobrescribir?` para todos |

Si el usuario cancela la confirmación, no se toca nada.

#### Ejecución (`_copy_jobs`)

1. **Planificación**:
   - Para cada origen carpeta: se añade el destino a `plan_dirs` y se recorre con
     `os.walk`, añadiendo subcarpetas y pares `(archivo_origen, archivo_destino)`
     a `plan_files`.
   - Para cada origen archivo: se comprueba que exista la carpeta destino; si no,
     se aborta con diálogo.
2. **Carpetas primero**: `os.makedirs(d, exist_ok=True)` para todas. Así se
   conservan carpetas vacías y se garantiza que exista la jerarquía.
3. **Archivos**: `shutil.copy2(s, d)` para cada par, creando el directorio
   padre si hace falta. `copy2` conserva fecha de modificación y permisos.
4. **Progreso**: se muestra un diálogo con barra, contador `n / total`, porcentaje
   y nombre del archivo actual. Se refresca como máximo cada 50 ms.
5. **Cancelación**: mientras el progreso está activo se consumen las teclas
   disponibles; `Esc` activa `cancel`. Se comprueba entre carpeta y carpeta y
   entre archivo y archivo.
6. **Errores**: se acumulan y se muestran al final en un diálogo (máximo 8,
   indicando cuántos más hay).
7. **Resultado**:
   - Cancelado: mensaje `Operacion cancelada por el usuario.` y `False`.
   - Errores: diálogo de error y `False`.
   - Éxito: `True`, y `op_copy` muestra `Copiado: N elemento(s)`.
8. Se recargan ambos paneles siempre.

> Los errores por archivo **no** se muestran uno a uno ni permiten reintentar,
> omitir o renombrar. El mensaje de éxito solo aparece si no hubo ningún error.

### 7.9. Mover / renombrar

#### Un solo elemento

El diálogo se inicializa con el nombre actual y admite:

- **Nombre simple** (sin separadores ni `X:`): se renombra dentro de la misma
  carpeta (`panel.path\nombre`).
- **Ruta con separador o unidad**: se normaliza; si el resultado es una carpeta
  existente, se mueve **dentro** de ella conservando el nombre original.
- Si el destino es idéntico al origen, no hace nada.

Si el destino ya existe:

| Destino existente | Acción |
|---|---|
| Carpeta | Se rechaza siempre con `Ya existe una carpeta con ese nombre. No se sobrescribe con un archivo.` |
| Archivo | Se pide confirmación; si se acepta, se **elimina** y se mueve encima |

El movimiento usa `shutil.move`, por lo que dentro del mismo volumen es un
renombrado rápido y entre volúmenes copia y borra. Al terminar, el cursor queda
sobre el nuevo nombre.

#### Varios elementos marcados

1. Se pide una carpeta destino (por defecto, la del otro panel).
2. Debe ser una carpeta **existente**; si no, error.
3. Si algún destino ya existe, una única confirmación para todos.
4. Para cada elemento:
   - Si el destino es una carpeta: se registra el error y se **omite** (nunca se
     borra una carpeta para colocar un archivo).
   - Si el destino es un archivo: se elimina y se mueve encima.
5. Se limpian las marcas y se recargan ambos paneles.
6. Si hubo errores, se muestran (máximo 9); si no, `Movido: N elemento(s)`.

### 7.10. Crear carpeta

- No disponible en la vista de unidades.
- Pide un nombre. Si es una ruta absoluta, se usa tal cual; si es relativa, se
  crea dentro del panel activo.
- Usa `os.makedirs`, por lo que **crea también los niveles intermedios**.
- Si ya existe, `OSError` y diálogo de error.
- Al terminar, el cursor queda sobre la carpeta creada y se muestra
  `Carpeta creada: nombre`.

### 7.11. Borrar

- Usa la selección (marcados o cursor).
- Pide confirmación con el número de elementos, hasta 3 nombres y el aviso
  `Esta accion no se puede deshacer.`
- Para carpetas (que no sean enlaces simbólicos): `shutil.rmtree` con un manejador
  que hace `chmod +w` y reintenta.
- Para archivos: `os.remove`; si da `PermissionError`, hace `chmod +w` y reintenta.
- **No usa la Papelera de Reciclaje.** El borrado es permanente.
- Limpia marcas, recarga ambos paneles y muestra error o `Borrado: N elemento(s)`.

### 7.12. Cambiar unidad o ruta

- Pide una unidad (`D:`) o una ruta.
- Expande variables y `~`, quita comillas.
- Si el texto es exactamente dos caracteres y el segundo es `:`, añade `\`.
- Convierte a absoluta y comprueba que sea un directorio.
- Si no existe: `La ruta no existe:`.
- Si es válida: cambia `panel.path`, recarga y coloca el cursor en 0.
- No valida que sea una unidad montada más allá de `os.path.isdir`.

### 7.13. Ordenar

Opciones del menú **Opciones**:

| Acción | `sort_key` | Orden de archivos por defecto |
|---|---|---|
| Ordenar por nombre | `name` | Ascendente por nombre |
| Ordenar por extensión | `ext` | Ascendente por extensión y luego nombre |
| Ordenar por fecha | `date` | **Descendente** (más reciente primero) |
| Ordenar por tamaño | `size` | **Descendente** (más grande primero) |
| Invertir orden | — | Alterna `sort_rev` |

Detalles:

- Las carpetas van siempre antes que los archivos y se ordenan por nombre.
- `sort_rev` invierte las carpetas y los archivos. En fecha/tamaño, el orden
  "normal" ya es descendente; invertir lo vuelve ascendente.
- Cambiar de criterio reinicia `sort_rev = False`.
- El orden es **por panel**: cada panel conserva su propio `sort_key` y
  `sort_rev`.
- Ordenar recarga el panel y conserva el cursor por nombre si es posible.

### 7.14. Archivos ocultos

- `show_hidden` es global y empieza en `True`.
- Se considera oculto lo que tenga el atributo Win32 `0x2`
  (`FILE_ATTRIBUTE_HIDDEN`), incluidos directorios.
- Al desactivarlo, se recargan ambos paneles y se muestra
  `Archivos ocultos: visibles` u `ocultos`.
- No hay opción para mostrar archivos de sistema por separado: se muestran si no
  son ocultos.

### 7.15. Refrescar

- `F2` o `Ctrl+R` recargan ambos paneles.
- Se conserva el cursor por nombre cuando es posible.
- Se muestra `Paneles actualizados`.
- Útil después de editar con Notepad o de cambios externos.

### 7.16. Menú superior

Estructura exacta (`MENUS`):

```text
Archivo
  Ver                      F3
  Ver forzado (texto/hex)...
  Ver archivo por ruta...
  Editar con Notepad       F4
  -------------------------
  Copiar                   F5
  Mover / renombrar        F6
  Crear carpeta            F7
  Borrar                   F8
  -------------------------
  Cambiar unidad o ruta...
  Salir                    F10

Opciones
  Ordenar por nombre
  Ordenar por extension
  Ordenar por fecha
  Ordenar por tamaño
  Invertir orden
  -------------------------
  Mostrar archivos ocultos
  Refrescar                Ctrl+R

Ayuda
  Teclas
  Acerca de WorkCommander
```

- El menú se dibuja superpuesto a los paneles, con sombra.
- Los separadores son líneas horizontales.
- Las teclas de función se muestran a la derecha de cada acción cuando caben.
- Al ejecutar una acción, el menú se cierra antes de llamar al método.
- Si una acción abre un diálogo o el paginador, al volver se redibuja el panel.

### 7.17. Ayuda y Acerca de

- **Teclas**: abre el paginador con `HELP_TEXT`, que resume funciones,
  navegación y operaciones.
- **Acerca de**: diálogo con nombre, versión 1.1, descripción y tecnologías.

### 7.18. Salir

- `F10`, `Ctrl+C` o la acción **Salir** ponen `running = False`.
- El `finally` de `run()` llama a `scr.cleanup()`:
  - rellena la pantalla con espacios,
  - vuelca el búfer,
  - muestra el cursor,
  - coloca el cursor en la esquina superior izquierda de la ventana,
  - restaura el modo de entrada original,
  - restaura el título original de la consola (o `WorkCommander`).

---

## 8. Arquitectura del código

`workcommander.py` es un único módulo. Orden interno:

```text
1. Docstring y comprobación de plataforma
2. Structs de Win32 (COORD, SMALL_RECT, CONSOLE_SCREEN_BUFFER_INFO,
   CHAR_INFO, CONSOLE_CURSOR_INFO)
3. Declaraciones de kernel32 y constantes de color
4. Caracteres de marco (Unicode o ASCII)
5. class Screen
6. Utilidades: read_key, wrap_text, fmt_size, fmt_date, size_label, human_size
7. class Entry
8. class Panel
9. MENUS, HINTS, HELP_TEXT
10. class WorkCommander
11. main()
```

### 8.1. `Screen`

Doble búfer de caracteres con atributos. La rejilla es una lista plana de tuplas
`(carácter, atributo)` de tamaño `ancho * alto`.

| Método | Función |
|---|---|
| `__init__` | Obtiene handles, configura título/cursor/modo, sincroniza tamaño y valida que haya consola |
| `_configure` | Guarda título y modo de entrada; pone título `WorkCommander`; oculta cursor; desactiva Quick Edit |
| `show_cursor(visible)` | Muestra u oculta el cursor |
| `_info()` | Devuelve `CONSOLE_SCREEN_BUFFER_INFO` o `None` |
| `sync_size(force=False)` | Lee el tamaño de la ventana; amplía el búfer si hace falta; recrea la rejilla si cambió |
| `clear(attr)` | Rellena la rejilla con espacios |
| `put(x, y, text, attr)` | Escribe texto recortando fuera de límites; control chars → espacio; > `0xFFFF` → `?` |
| `fill(x, y, w, h, ch, attr)` | Rellena un rectángulo |
| `box(x, y, w, h, attr, title, title_attr)` | Dibuja marco doble con título centrado |
| `hline_sep(x, y, w, attr)` | Línea separadora con conectores laterales |
| `flush()` | Convierte la rejilla en `CHAR_INFO[]` y la envía con `WriteConsoleOutputW` |
| `cleanup()` | Restaura pantalla, cursor, posición, modo de entrada y título |

Detalles importantes:

- `flush()` comprueba primero que el tamaño de la ventana siga coincidiendo; si
  cambió, llama a `sync_size(force=True)` y devuelve `False` sin pintar.
- Se escribe **toda** la ventana visible en una sola llamada, por lo que no hay
  parpadeo ni parpadeo de cursor.
- `sync_size` solo **amplía** el búfer (`max`), nunca lo reduce, para evitar
  errores de Win32 cuando la ventana es más grande que el búfer.
- La rejilla se recrea al cambiar de tamaño, perdiendo el contenido anterior;
  `draw()` la repinta completa.

### 8.2. `Panel`

| Método | Función |
|---|---|
| `title()` | `Unidades` o la ruta |
| `current()` | Entrada bajo el cursor o `None` |
| `reload(keep_name=None)` | Relee el directorio o las unidades, filtra ocultos, ordena, conserva cursor y marcas |
| `sort_entries()` | Separa `..`, carpetas y archivos; ordena según criterio |
| `move(delta)` | Mueve el cursor con límites |
| `draw(...)` | Dibuja marco, título, columnas, filas y scroll |

`reload()`:

1. Determina `keep_name`: el parámetro o el nombre actual.
2. Si `path is None`, enumera unidades existentes.
3. Si no, añade `..` y recorre con `os.scandir`.
4. Para cada entrada usa `de.stat(follow_symlinks=False)`; si falla, `st = None`.
5. Filtra ocultos según `app.show_hidden`.
6. Detecta carpetas con `de.is_dir(follow_symlinks=False)`.
7. Ordena y conserva las marcas que sigan existiendo.
8. Intenta colocar el cursor en `keep_name` (sin distinguir mayúsculas).
9. Ajusta el índice a los límites.
10. Si no puede acceder a la carpeta, muestra un flash de error y deja la lista
    vacía (con `..`).

### 8.3. `WorkCommander`

Métodos agrupados:

- **Infraestructura**: `flash`, `page_size`, `selected_entries`,
  `_norm_target`, `_on_rm_error`.
- **Diálogos**: `_dialog_frame`, `dialog_input`, `dialog_confirm`,
  `dialog_choice`, `dialog_message`.
- **Progreso**: `_progress_show`, `_progress`.
- **Copia**: `_copy_jobs`.
- **Visor**: `pager`, `view_file`.
- **Navegación**: `op_enter`, `op_up`, `toggle_mark`, `quick_search`.
- **Operaciones**: `op_view`, `op_view_force`, `op_view_path`, `op_edit`,
  `op_copy`, `op_move`, `op_mkdir`, `op_delete`, `op_changedrive`, `op_refresh`,
  `op_help`, `op_about`, `op_quit`.
- **Opciones**: `_set_sort`, `op_sort_*`, `op_toggle_hidden`.
- **Dibujo**: `draw_menubar`, `draw_status`, `draw_keybar`, `draw`.
- **Menú**: `_first_actionable`, `_menu_move`, `draw_menu`, `menu_loop`.
- **Entrada**: `handle_key`.
- **Ejecución**: `run`.

### 8.4. Contratos de los métodos principales

| Firma | Devuelve | Efecto |
|---|---|---|
| `WorkCommander(start_path=None, screen=None)` | instancia | Crea pantalla si no se inyecta y dos paneles en `start_path` (o `cwd`) |
| `Panel(app, path)` | instancia | Carga la carpeta o la vista de unidades si `path is None` |
| `Panel.reload(keep_name=None)` | `None` | Relee, filtra, ordena y ajusta cursor/marcas |
| `Panel.move(delta)` | `None` | Mueve el cursor con límites |
| `Screen.sync_size(force=False)` | `bool` | `True` si cambió el tamaño |
| `Screen.flush()` | `bool` | `True` si el fotograma se escribió |
| `read_key()` | `(kind, value)` | `kind` es `"char"` o `"special"` |
| `dialog_input(title, label, default="")` | `str \| None` | Texto aceptado o `None` si se cancela |
| `dialog_confirm(title, lines)` | `bool` | `True` para sí |
| `dialog_choice(title, lines, options)` | `str \| None` | Clave elegida (`t`, `h`, …) o `None` con `Esc` |
| `dialog_message(title, lines, error=False)` | `None` | Bloquea hasta una tecla |
| `view_file(path, mode=None)` | `None` | Abre texto/hex; `mode="t"` o `"h"` fuerza el modo |
| `looks_utf16(raw)` | `bool` | Heurística de BOM o bytes nulos alternos |
| `decode_text(raw)` | `str` | BOM/UTF-16/UTF-8/cp1252 |
| `hex_dump_lines(raw, width)` | `list[str]` | Volcado hex con columna ASCII |
| `selected_entries()` | `list[Entry]` | Marcados, o el cursor; `[]` para `..`/unidad |
| `_norm_target(panel, text)` | `str \| None` | Ruta absoluta normalizada o `None` |
| `_copy_jobs(jobs)` | `bool` | `True` solo si no hubo errores ni cancelación |
| `op_view_force()` | `None` | Pregunta texto/hex y abre la entrada actual |
| `op_view_path()` | `None` | Pide una ruta y abre ese archivo |
| `op_copy/op_move/op_mkdir/op_delete()` | `None` | Operaciones completas con diálogos y recargas |
| `handle_key((kind, val))` | `None` | Despacha una tecla |
| `run()` | `None` | Bucle principal hasta `running = False` |

### 8.5. Estructuras de datos constantes

| Constante | Forma | Uso |
|---|---|---|
| `MENUS` | `list[(título, list[(etiqueta, acción)])]` | Menú superior; `(None, None)` es separador |
| `HINTS` | `dict[acción, etiqueta]` | Tecla mostrada a la derecha de cada acción |
| `HELP_TEXT` | `str` multilínea | Texto del paginador de ayuda |
| `C_*` | `int` | Atributos de color Win32 |
| `TL, TR, BL, BR, ML, MR, H, V` | `str` | Glifos del marco |
| `BAR_FULL, BAR_EMPTY` | `str` | Caracteres de la barra de progreso |

Las acciones de `MENUS` son **nombres de métodos** de `WorkCommander`; el menú
las invoca con `getattr(self, action)()`. Para añadir una acción basta con que el
método exista y esté listado.

---

## 9. Capa Win32 en detalle

### 9.1. Handles y constantes

```python
STD_INPUT_HANDLE  = -10
STD_OUTPUT_HANDLE = -11
ENABLE_EXTENDED_FLAGS = 0x0080
ENABLE_QUICK_EDIT_MODE = 0x0040
```

Se cargan una sola vez:

```python
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
```

y se declaran `argtypes`/`restype` para las funciones usadas. Esto es importante
en 64 bits: sin declarar los tipos, los punteros y `HANDLE` pueden truncarse.

### 9.2. Estructuras

| Estructura | Campos |
|---|---|
| `COORD` | `X`, `Y` (`c_short`) |
| `SMALL_RECT` | `Left`, `Top`, `Right`, `Bottom` (`c_short`) |
| `CONSOLE_SCREEN_BUFFER_INFO` | `dwSize`, `dwCursorPosition`, `wAttributes`, `srWindow`, `dwMaximumWindowSize` |
| `CHAR_INFO` | `Char` (`c_wchar`, UTF-16), `Attributes` (`c_ushort`) |
| `CONSOLE_CURSOR_INFO` | `dwSize` (`DWORD`, se usa 25), `bVisible` (`BOOL`) |

### 9.3. Funciones

| Función | Uso |
|---|---|
| `GetStdHandle` | Obtener handles de entrada/salida |
| `GetConsoleScreenBufferInfo` | Tamaño del búfer, ventana visible y posición del cursor |
| `WriteConsoleOutputW` | Volcar el fotograma completo |
| `SetConsoleScreenBufferSize` | Ampliar el búfer si la ventana creció |
| `SetConsoleCursorInfo` | Ocultar/mostrar el cursor |
| `SetConsoleCursorPosition` | Dejar el cursor arriba a la izquierda al salir |
| `SetConsoleTitleW` / `GetConsoleTitleW` | Guardar y restaurar el título |
| `GetConsoleMode` / `SetConsoleMode` | Guardar y restaurar el modo de entrada |

### 9.4. Modo de entrada

Al iniciar:

```python
mode = GetConsoleMode(hin)
SetConsoleMode(hin, (mode | ENABLE_EXTENDED_FLAGS) & ~ENABLE_QUICK_EDIT_MODE)
```

- `ENABLE_EXTENDED_FLAGS` garantiza que los flags extendidos se apliquen.
- Desactivar `ENABLE_QUICK_EDIT_MODE` evita que un clic o una selección con el
  ratón congelen la aplicación y bloqueen la lectura de teclas.
- No se activa `ENABLE_VIRTUAL_TERMINAL_INPUT`; se usan las teclas clásicas de
  `msvcrt`.
- Al salir se restaura exactamente el modo original.

### 9.5. Escritura del fotograma

`flush()`:

1. Vuelve a leer la ventana visible.
2. Si el tamaño no coincide, sincroniza y aborta el fotograma.
3. Reserva `CHAR_INFO[ancho * alto]`.
4. Copia cada `(char, attr)` de la rejilla.
5. Usa como origen `COORD(0, 0)` y tamaño `COORD(ancho, alto)`.
6. Usa como región destino `SMALL_RECT` desde `srWindow.Left/Top` hasta
   `srWindow.Left+ancho-1 / Top+alto-1`.
7. Llama a `WriteConsoleOutputW`.

Ventajas:

- Sin parpadeo: no se borra la pantalla antes de pintar.
- Sin ANSI: funciona en consolas antiguas.
- Los atributos de color se aplican por celda.
- El cursor permanece oculto, salvo al editar con Notepad.

### 9.6. Unicode y limitaciones

- `CHAR_INFO.Char` es `c_wchar` (UTF-16). Caracteres fuera del BMP se sustituyen
  por `?`.
- El texto se escribe con `WriteConsoleOutputW` (variante Unicode).
- No se usan pares sustitutos ni emoji.
- Los caracteres de control se convierten en espacios en `put()`.

### 9.7. Caracteres de marco

Por defecto:

```text
╔ ╗ ╚ ╝ ╠ ╣ ═ ║ █ ░
```

Si se define `WORKCOMMANDER_ASCII` con un valor distinto de vacío, `0` o `no`
(por ejemplo `1`, `true`, `si`, `false`), se usan:

```text
+ + + + + + - | # -
```

La comprobación es literal:

```python
_ASCII_FRAME = os.environ.get("WORKCOMMANDER_ASCII", "") not in ("", "0", "no")
```

Es decir, `WORKCOMMANDER_ASCII=false` **también** activa el modo ASCII.

---

## 10. Flujos de control

### 10.1. `handle_key`

```text
si kind == "special":
    H/P        mover cursor
    K/M        activar panel izquierdo/derecho
    G/O        inicio/fin
    I/Q        página arriba/abajo
    R          marcar/desmarcar
    S          borrar
    ; < = > ? @ A B C D   F1..F10
    \x0f      alternar panel (Shift+Tab)
    resto      ignorar

si kind == "char":
    \r         entrar/abrir
    \t, \x0f   alternar panel
    \x1b       ignorar
    \x08       subir nivel
    \x12       refrescar
    \x03       salir
    imprimible búsqueda rápida
```

### 10.2. `menu_loop`

```text
menu_open = True
mientras True:
    draw()            # paneles + barra
    draw_menu()       # menú superpuesto
    flush()
    leer tecla
    especiales: arriba/abajo, izquierda/derecha, F9 cierra, F10 sale
    Esc cierra
    Tab cambia de menú
    Enter/Espacio ejecuta la acción y sale del menú
    letra: salta a la primera acción que empiece por ella
menu_open = False
```

### 10.3. `dialog_input`

```text
texto = lista(default)
pos = len(texto)
mientras True:
    calcular tamaño y centrar
    dibujar etiqueta, campo, cursor y ayuda
    flush()
    leer tecla
    editar / mover cursor / borrar
    Enter -> devolver texto.strip()
    Esc   -> devolver None
```

El campo se desplaza horizontalmente cuando el cursor supera el ancho interior.
El texto máximo es de 2048 caracteres.

### 10.4. `pager`

```text
top = 0
mientras True:
    sincronizar tamaño
    page = alto - 2
    limitar top
    limpiar con C_VIEW
    dibujar título y líneas
    dibujar barra con rango "Lineas X-Y de N"
    leer tecla
    flechas / RePág / AvPág / Inicio / Fin
    q, Q, Esc, F10 -> salir
```

La barra inferior incluye `info` (por ejemplo tamaño y truncado) y las teclas.

### 10.5. `_copy_jobs`

```text
plan_dirs = []
plan_files = []
para cada (src, dst):
    si src es carpeta:
        plan_dirs += [dst]
        os.walk(src):
            plan_dirs += subcarpetas
            plan_files += (archivo, destino)
    si es archivo:
        si no existe dirname(dst): error y salir
        plan_files += (src, dst)

crear todas las plan_dirs
si no hay archivos: mostrar progreso "Creando carpetas..."
para cada archivo:
    si cancel: break
    makedirs(dirname)
    copy2
    progreso
si cancel: mensaje y False
si errores: diálogo y False
si no: True
```

---

## 11. Utilidades de formato

| Función | Comportamiento |
|---|---|
| `wrap_text(text, width)` | Parte por palabras; si no hay espacio, corta duro; mínimo 8 columnas; conserva líneas vacías |
| `fmt_size(n)` | Si `n < 100.000.000`, entero con separador de miles `.`; si no, `KB/MB/GB/TB` con un decimal |
| `fmt_date(ts)` | `dd/mm/aa HH:MM`; vacío si la fecha no es válida |
| `size_label(n)` | Como `fmt_size`, pero añade ` bytes` cuando el número es exacto |
| `human_size(n)` | `B/KB/MB/GB/TB` para el espacio libre; `B` sin decimales |

Ejemplos:

- `fmt_size(120345)` → `120.345`
- `fmt_size(150000000)` → `143.1 MB`
- `size_label(120345)` → `120.345 bytes`
- `size_label(150000000)` → `143.1 MB`
- `human_size(88400000000)` → `82.3 GB`

---

## 12. Pruebas

Archivo: `tests\headless_test.py`. Se ejecuta con `py -3 tests\headless_test.py`.
No usa `pytest` ni frameworks externos; tiene su propio `main()` que imprime
`OK`/`FAIL` y devuelve 0 o 1.

### 12.1. Estrategia

- **`FakeScreen`**: implementa la misma interfaz que `Screen` (`sync_size`,
  `clear`, `put`, `fill`, `box`, `hline_sep`, `flush`, `show_cursor`, `cleanup`)
  sobre una rejilla de 100×32. Añade `lines()` y `text()` para inspeccionar el
  contenido y cuenta fotogramas en `frames`.
- **`FakeKernel`**: reemplaza `wc.kernel32` para probar la capa Win32 sin consola.
  Simula un búfer de 100×30, captura las celdas escritas, el rectángulo, el
  título y el modo de entrada.
- **Inyección de dependencias**: `WorkCommander(tmp, screen=scr)` evita crear una
  consola real.
- **Sustitución de diálogos**: los tests reemplazan `dialog_input`,
  `dialog_confirm`, `dialog_choice`, `dialog_message` y `_progress` por funciones
  controladas.
- **Directorios temporales**: cada prueba crea y borra su propio
  `tempfile.mkdtemp`.

### 12.2. Cobertura de las 5 pruebas

| Prueba | Qué valida |
|---|---|
| `test_layout` | Dimensiones de la rejilla, barra de menú, `F10 Salir`, menú Archivo, marcos, encabezado `Nombre`, archivo y carpeta visibles, cursor inicial en `..`, barra de teclas |
| `test_navigation_and_sort` | `..` primero, carpetas antes que archivos, orden por extensión, orden inverso, entrar/salir de carpeta conservando el cursor, marcado múltiple, `selected_entries`, búsqueda rápida, vista de unidades sin marcas ni operaciones |
| `test_copy_move_mkdir_delete` | Copiar archivo, copiar carpeta recursiva, renombrar, crear carpeta, borrar, rechazo de copiar carpeta sobre archivo y de mover archivo sobre carpeta |
| `test_viewer` | Texto normal y wrapping de 300 caracteres; INI UTF-16 con y sin BOM; binario con elección texto/hex; volcado hex; cancelación; `Ver archivo por ruta`; `Ver forzado`; diálogo de elección; adaptación del hex a ventanas estrechas |
| `test_screen_win32_layer` | Tamaño 100×30 desde `FakeKernel`, escritura de "Hola" con atributo, marco en la fila correcta, rectángulo de escritura, título `WorkCommander`, Unicode y restauración del título |

### 12.3. Limitaciones de las pruebas

- Solo cubren la lógica y una simulación de Win32; **no** validan una consola
  real, el parpadeo, el redimensionado físico ni la entrada real.
- No cubren el menú interactivo, el paginador real, el progreso, la cancelación
  con `Esc` ni Notepad.
- Dependen de Windows: al importar `workcommander` se carga `ctypes.WinDLL` y
  `msvcrt`.
- No hay pruebas de concurrencia (no hay hilos).
- La validación en consola real se hizo manualmente con `AttachConsole` /
  `WriteConsoleInputW` (inyectando scancodes correctos: F7 `0x41`, F10 `0x44`,
  Enter `0x1C`, texto con `VK_PACKET 0xE7`).

### 12.4. Resultado actual

```text
5/5 pruebas correctas
```

El ejecutable recién compilado también devuelve `0` con `--selftest`.

---

## 13. Compilación y distribución

### 13.1. Script incluido

```bat
build_exe.bat
```

Hace:

1. `cd /d "%~dp0"`.
2. Detecta `py` y, si no, `python`.
3. `pip install --quiet --upgrade pyinstaller`.
4. `pyinstaller --noconfirm --clean --onefile --console --name WorkCommander workcommander.py`.
5. Muestra la ruta `dist\WorkCommander.exe`.

### 13.2. Comando manual equivalente

```bat
py -3 -m pip install --upgrade pyinstaller
py -3 -m PyInstaller --noconfirm --clean --onefile --console --name WorkCommander workcommander.py
```

### 13.3. Verificación posterior

```bat
dist\WorkCommander.exe --selftest
echo %errorlevel%
```

Debe imprimir `0`. Si se lanza desde PowerShell o desde un script sin consola
propia, usar `CREATE_NEW_CONSOLE` (0x10), porque `--selftest` necesita una
consola interactiva.

### 13.4. Contenido de `dist\`

- `WorkCommander.exe`: ejecutable único de ~7,4 MB. Incluye el intérprete de
  Python y los módulos usados.
- No necesita archivos adyacentes.

### 13.5. Recompilar sin errores de bloqueo

PyInstaller en modo `--onefile` **bloquea el ejecutable mientras se ejecuta**. Si
hay una instancia abierta, la compilación falla con:

```text
PermissionError: [WinError 5] Acceso denegado: ...\dist\WorkCommander.exe
```

Solución:

```powershell
Get-Process WorkCommander -ErrorAction SilentlyContinue | Stop-Process -Force
py -3 -m PyInstaller --noconfirm --clean --onefile --console --name WorkCommander workcommander.py
```

También conviene cerrar ventanas de CMD/Windows Terminal que estén ejecutando el
`.exe`.

### 13.6. Limpieza

Tras compilar se pueden borrar:

```text
build\
__pycache__\
tests\__pycache__\
WorkCommander.spec
```

`dist\` se conserva porque contiene el entregable.

### 13.7. Distribución

Para entregar el programa basta con copiar:

```text
WorkCommander.exe
```

Opcionalmente, para desarrollo:

```text
workcommander.py
WorkCommander.bat
tests\headless_test.py
```

No hay instalador, firma digital, icono personalizado, recurso de versión ni
asociación de archivos.

---

## 14. Rendimiento y límites

| Aspecto | Valor / comportamiento |
|---|---|
| Sondas de teclado | Cada 20 ms |
| Redibujo periódico | Como máximo 1 vez por segundo en reposo (reloj) |
| Redibujo tras tecla | Inmediato |
| Fotograma | Una llamada a `WriteConsoleOutputW` con toda la ventana |
| Tamaño mínimo de ventana | 40×12 |
| Columnas de tamaño/fecha | Se ocultan si el panel es estrecho |
| Visor | Máximo 8 MiB; texto o hex; detecta UTF-16; si es binario pregunta |
| Volcado hex | 16, 8 o 4 bytes por fila según el ancho |
| Campo de entrada | Máximo 2048 caracteres |
| Errores mostrados | 8 en copia, 9 en mover/borrar |
| Progreso de copia | Refresco cada 50 ms |
| Operaciones | Síncronas en el hilo de la interfaz |
| Hilos | Ninguno |
| Memoria | Rejilla de `ancho*alto` tuplas + lista de entradas del directorio |

**Consecuencia importante:** copiar, mover o borrar muchos archivos **congela la
interfaz** hasta terminar. Solo la copia muestra progreso y permite cancelar con
`Esc`, porque su bucle consume teclas. Mover y borrar no tienen progreso ni
cancelación.

---

## 15. Comportamiento no obvio y limitaciones

1. **Borrado permanente**: no se usa la Papelera de Reciclaje. No hay deshacer.
2. **Sin persistencia**: al cerrar se pierden panel activo, orden, marcas,
   carpeta inicial y preferencia de ocultos.
3. **Ambos paneles arrancan en la misma carpeta**, no en `C:\` y `D:\`.
4. **`show_hidden` empieza en `True`**: los ocultos se ven por defecto.
5. **Enter sobre un archivo lo ejecuta/abre** con `os.startfile`. No hay
   confirmación: un `.exe`, `.bat` o `.lnk` se ejecutará.
6. **F4 bloquea hasta cerrar Notepad** y no recarga automáticamente.
7. **Copiar un archivo a una ruta inexistente** crea un archivo con ese nombre,
   aunque la ruta parezca una carpeta sin barra final.
8. **Copiar una carpeta sobre un archivo existente se rechaza**; no se
   sobrescribe el archivo con la carpeta.
9. **Copiar un archivo sobre una carpeta existente se rechaza**; no se borra la
   carpeta.
10. **Mover un archivo sobre una carpeta existente se rechaza**; no se borra la
    carpeta.
11. **La confirmación de sobrescritura es única para todo el lote**, no por
    archivo. No hay opciones "sí a todo / no a todo / renombrar".
12. **Los errores de copia no se muestran uno a uno**; se resumen al final.
13. **`shutil.copy2` conserva metadatos de archivos**, pero las carpetas creadas
    no conservan sus fechas originales.
14. **Enlaces simbólicos y junctions**: `os.walk` no sigue enlaces a directorios
    por defecto; `copy2` copia el contenido del archivo enlazado. No hay manejo
    especial de reparse points.
15. **Rutas largas**: no se activa `\\?\` ni la política de long paths. Rutas de
    más de 260 caracteres pueden fallar según la configuración de Windows.
16. **Unidades**: solo letras `A:`–`Z:`. No se listan volúmenes montados en
    carpetas ni rutas UNC en la vista de unidades (aunque se pueden escribir a
    mano en "Cambiar unidad o ruta").
17. **Sin ratón**: no hay clic, rueda ni selección con ratón.
18. **Sin múltiples instancias controladas**: se pueden abrir varias.
19. **Codificaciones**: el visor detecta UTF-8, UTF-16 (BOM o patrón) y cp1252.
    Otras codificaciones (shift-jis, GBK, etc.) se verán mal; se puede usar el
    volcado hexadecimal para inspeccionar los bytes.
20. **El hex no es un editor**: es un volcado de solo lectura, sin edición ni
    búsqueda dentro del archivo.
21. **Sin archivos de sistema especiales**: no hay opción para mostrar
    `FILE_ATTRIBUTE_SYSTEM` por separado.
22. **La barra de teclas muestra dígitos 1–0**, pero las teclas reales son
    F1–F10; los dígitos hacen búsqueda rápida.
23. **El reloj y la barra de estado usan la hora local** del sistema.
24. **Al salir se limpia la pantalla**, por lo que se pierde el contenido previo
    de la consola.
25. **El título original se restaura** al salir, pero si el proceso se mata
    abruptamente puede quedar `WorkCommander`.
26. **El ejecutable puede tardar unos segundos en arrancar** porque PyInstaller
    `--onefile` se descomprime en un directorio temporal.

---

## 16. Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `No hay una consola interactiva disponible.` | Se ejecutó sin consola real, con salida redirigida o desde un servicio | Abrir CMD/Windows Terminal y ejecutar allí; en scripts usar `CREATE_NEW_CONSOLE` |
| `WorkCommander solo funciona en Windows.` | Se ejecutó en Linux/macOS | Usar Windows o una máquina virtual |
| `No se encontro Python...` | `WorkCommander.bat` no encuentra `py` ni `python` | Instalar Python 3.8+ y marcar "Add to PATH"; o usar `dist\WorkCommander.exe` |
| `No se encontro workcommander.py junto a este archivo.` | Se movió el `.bat` sin el fuente | Mantener ambos juntos o usar el `.exe` |
| Los marcos se ven como letras raras | Fuente sin glifos de caja | Cambiar a Consolas/Cascadia Mono o definir `WORKCOMMANDER_ASCII=1` |
| `Consola demasiado pequeña.` | Ventana menor de 40×12 | Agrandar la ventana |
| `PermissionError: [WinError 5]` al compilar | El `.exe` está en ejecución | Cerrar todas las instancias y recompilar |
| La aplicación se congela al copiar muchos archivos | Operación síncrona | Esperar; solo la copia permite `Esc` |
| `Acceso denegado` al borrar | Archivo de solo lectura o en uso | WorkCommander reintenta `chmod`; si está en uso, cerrar el programa que lo bloquea |
| `La carpeta destino no existe` | Ruta de destino inexistente en copia de archivo | Crear la carpeta o corregir la ruta |
| `El destino debe ser una carpeta existente.` | Copia/movimiento múltiple a una ruta que no es carpeta | Escribir una carpeta existente |
| `Ya existe una carpeta con ese nombre.` | Se intentó mover un archivo sobre una carpeta | Elegir otro nombre o borrar la carpeta manualmente |
| El visor pregunta si el archivo es binario | Contiene `\x00` y no parece UTF-16 | Elegir `T` texto, `H` hexadecimal o `Esc`; es el comportamiento nuevo |
| Un INI se ve con caracteres extraños | Codificación distinta de UTF-8/UTF-16/cp1252 | Abrirlo con `Ver forzado` en hexadecimal o convertirlo a UTF-8 |
| No aparece un archivo oculto en el panel | "Mostrar archivos ocultos" está desactivado | Activarlo en Opciones o usar `Archivo > Ver archivo por ruta...` |
| El reloj no avanza | La ventana está en modo Quick Edit o el proceso está bloqueado | WorkCommander desactiva Quick Edit; evitar seleccionar texto |
| El antivirus marca el `.exe` | Falso positivo típico de PyInstaller | Compilar localmente o añadir exclusión |
| `--selftest` devuelve 1 | No hay consola interactiva | Ejecutarlo en una consola real |
| Al salir queda la pantalla en blanco | `cleanup()` limpia la consola | Comportamiento esperado |

---

## 17. Guía de extensión

### 17.1. Añadir una operación nueva

1. Implementar `def op_mi_accion(self):` en `WorkCommander`, siguiendo el patrón:
   - obtener `p = self.panels[self.active]`;
   - usar `self.selected_entries()`;
   - validar antes de tocar disco;
   - usar `self.dialog_input`, `self.dialog_confirm`, `self.dialog_choice` o
     `self.dialog_message`;
   - recargar los paneles afectados;
   - terminar con `self.flash(...)` o un diálogo de error.
2. Añadir la entrada en `MENUS` con `("Texto", "op_mi_accion")`.
3. Añadir su pista en `HINTS` si tiene tecla.
4. Mapear la tecla en `handle_key` (recordar que las funciones llegan como
   `special`).
5. Documentarla en `HELP_TEXT`.
6. Añadir una prueba en `tests/headless_test.py` con `FakeScreen`.

### 17.2. Añadir un criterio de orden

1. Añadir el caso en `Panel.sort_entries` (`fkey`).
2. Añadir `op_sort_mi_criterio` que llame a `self._set_sort("mi_criterio")`.
3. Añadir la entrada en `MENUS`.
4. Actualizar la tabla de ordenación de este README.

### 17.3. Añadir un diálogo

Reutilizar `_dialog_frame` para centrar, sombrear y dibujar el marco. Seguir el
patrón de `dialog_input`: dibujar, `flush()`, leer tecla, actualizar estado. No
bloquear con `input()` ni con `msvcrt.getch()` directo: usar `read_key()`.

### 17.4. Añadir una tecla

- Si es extendida, averiguar su segundo código con un programa que imprima
  `repr(msvcrt.getwch())` y añadir la rama en `handle_key`.
- Si es normal, comprobar que no colisione con la búsqueda rápida.
- Actualizar `HELP_TEXT` y la tabla de teclas.

### 17.5. Cambiar colores o marco

- Colores: constantes `C_*` al inicio.
- Marco: variables `TL, TR, BL, BR, ML, MR, H, V, BAR_FULL, BAR_EMPTY`.
- Mantener el contraste y recordar que los atributos son bytes Win32.

### 17.6. Añadir persistencia (no implementada)

Puntos de entrada razonables:

- Guardar al salir en `run()` (o en `op_quit`) un JSON con rutas, panel activo,
  criterios de orden y `show_hidden`.
- Cargar en `WorkCommander.__init__` antes de crear los paneles.
- Ubicación sugerida: `%APPDATA%\WorkCommander\config.json`.
- No romper la firma `WorkCommander(start_path=None, screen=None)` que usan las
  pruebas.

### 17.7. Añadir progreso a mover/borrar

- Reutilizar `self._prog` y `self._progress`.
- Para mover entre volúmenes, `shutil.move` no informa del progreso; habría que
  implementar copia + borrado con `_copy_jobs` y luego eliminar el origen.
- Para borrar, recorrer el árbol y contar archivos antes de borrar.

### 17.8. Añadir un modo de visor

1. Ampliar `view_file(path, mode=None)` con el nuevo valor de `mode`.
2. Si el modo necesita otra representación, generar una `list[str]` y pasarla a
   `self.pager(título, líneas, info)`.
3. Añadir la opción en `dialog_choice` (por ejemplo `("d", "Decimal")`) y en
   **Ver forzado**.
4. Mantener el límite de lectura y documentar el formato.
5. Añadir un caso en `test_viewer` que capture el paginador con un `lambda`.

---

## 18. Glosario

| Término | Significado |
|---|---|
| **Panel** | Mitad de la pantalla que muestra el contenido de una carpeta o la lista de unidades |
| **Panel activo** | Panel que recibe las teclas; se resalta con marco brillante |
| **Entrada** | Fila de un panel: `..`, unidad, carpeta o archivo |
| **Marca** | Selección persistente con `Insert`, usada por las operaciones por lotes |
| **Cursor** | Fila resaltada bajo la que se aplican las acciones |
| **Vista de unidades** | Modo especial con `path = None` que lista `A:`–`Z:` |
| **Doble búfer** | Rejilla en memoria que se vuelca completa a la consola |
| **Atributo** | Byte Win32 con colores de texto/fondo |
| **CHAR_INFO** | Celda de consola: carácter + atributo |
| **Scancode / código extendido** | Segundo byte que identifica flechas, F1–F10, etc. |
| **Paginador** | Visor de solo lectura con desplazamiento |
| **Volcado hexadecimal** | Representación de bytes en hex con columna ASCII |
| **UTF-16** | Codificación de 2 bytes por carácter, habitual en INI de Windows |
| **Flash** | Mensaje temporal de la barra de estado (4 s) |
| **Job de copia** | Par `(origen, destino)` planificado por `_copy_jobs` |

---

## 19. Checklist de handoff para otra IA

Antes de modificar el proyecto:

1. Leer `workcommander.py` completo (1.931 líneas) y este README.
2. Leer `tests/headless_test.py` para conocer los contratos y los dobles.
3. Ejecutar `py -3 tests\headless_test.py` y confirmar 5/5.
4. Ejecutar `dist\WorkCommander.exe --selftest` en una consola real y confirmar
   código 0.
5. No romper estas invariantes:
   - `Panel.path is None` significa vista de unidades.
   - `entries[0]` es `..` salvo en la vista de unidades.
   - `is_parent` e `is_drive` no se marcan ni se operan.
   - Los diálogos usan `read_key()` y `scr.flush()`, nunca `input()`.
   - Las operaciones validan antes de borrar o sobrescribir.
   - `Screen.flush()` escribe la ventana completa.
   - `F3` nunca rechaza un archivo: los binarios ofrecen texto o hexadecimal.
   - Los diálogos nuevos deben usar `read_key()` y `scr.flush()`.
6. Si se cambia el comportamiento, actualizar:
   - la tabla de teclas,
   - la sección funcional correspondiente,
   - las pruebas,
   - la ficha técnica (líneas, bytes, hash, fecha),
   - el ejecutable de `dist\`.
7. Recompilar con `build_exe.bat` o el comando manual; cerrar instancias antes.
8. Verificar `--selftest`, ejecutar las pruebas y hacer un humo manual:
   - abrir, navegar, entrar/salir de carpeta,
   - cambiar de panel con Tab,
   - F7 crear carpeta,
   - F5 copiar a la otra carpeta,
   - F6 renombrar,
   - F3 ver un archivo de texto,
   - F3 sobre un binario: elegir texto y luego hexadecimal,
   - abrir un INI UTF-16 y comprobar que se ve como texto,
   - `Archivo > Ver forzado (texto/hex)...`,
   - `Archivo > Ver archivo por ruta...` con una ruta oculta,
   - F8 borrar,
   - F9 recorrer el menú,
   - F10 salir y comprobar que la consola queda usable.
9. Borrar `build\`, `__pycache__\`, `tests\__pycache__\` y `WorkCommander.spec`.
10. Actualizar los hashes SHA-256 si se entrega el `.exe`.

### Frases clave para entender el diseño

- "Todo el estado vive en memoria; no hay archivos de configuración."
- "La consola se pinta por bloques completos para evitar parpadeo."
- "Las operaciones son síncronas y usan diálogos modales."
- "La seguridad consiste en validar antes de tocar disco y nunca borrar una
  carpeta para sobrescribirla con un archivo."
- "Los tests sustituyen la pantalla y el kernel para poder ejecutarse sin
  consola."

---

## 20. Resumen de archivos

```text
WorkCommander\
├─ workcommander.py          Aplicación completa (1.931 líneas)
├─ WorkCommander.bat         Lanzador para CMD con Python
├─ build_exe.bat             Compilación con PyInstaller
├─ README.md                 Este documento
├─ dist\
│  └─ WorkCommander.exe      Ejecutable autónomo (7.426.736 bytes)
└─ tests\
   └─ headless_test.py       5 pruebas sin consola (471 líneas)
```

---

## 21. Registro de cambios

| Fecha | Cambio |
|---|---|
| 19/11/2026 | Versión inicial documentada: doble panel, menús, visor, operaciones, pruebas y ejecutable |
| 19/11/2026 | Endurecimiento: no se puede operar sobre unidades; se rechaza copiar carpeta sobre archivo, copiar archivo sobre carpeta y mover archivo sobre carpeta; el flash de éxito de copia solo aparece si no hubo errores |
| 19/11/2026 | README reescrito como documentación funcional y técnica completa para handoff |
| 19/11/2026 | **1.1**: el visor abre cualquier archivo; elección texto/hexadecimal para binarios, detección UTF-16, `Ver forzado` y `Ver archivo por ruta` para ocultos; nuevas pruebas y README actualizado |

---

**WorkCommander 1.1** — gestor de archivos de doble panel para la consola de
Windows. Sin dependencias externas, sin instalación y sin sorpresas fuera de las
documentadas aquí.
