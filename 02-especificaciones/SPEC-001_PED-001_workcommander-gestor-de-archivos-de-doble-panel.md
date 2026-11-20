# Spec: SPEC-001 · WorkCommander - Gestor de archivos de doble panel

> **Pedido origen**: PED-001
> **Estado**: Aprobada
> **Autor**: Pablo
> **Fecha**: 2026-11-20
> **Versión**: 0.1

---

## 1. Resumen y objetivo

**Problema que resuelve**: Gestionar archivos y carpetas desde la consola de Windows de forma rápida y completa usando solo el teclado, sin depender de una GUI ni de librerías externas, en una interfaz de doble panel inspirada en Norton Commander.

**Para quién**: Usuarios de Windows (técnicos, administradores, usuarios avanzados) que trabajan en CMD o Windows Terminal y necesitan copiar, mover, renombrar, crear, borrar, ver y editar archivos sin salir de la consola.

**Por qué importa ahora**: El proyecto ya está implementado y documentado (README v1.2, código fuente de 1.931 líneas, 5/5 pruebas headless correctas, ejecutable autónomo). Esta especificación formaliza el comportamiento esperado para que el equipo pueda estimar, construir, probar y mantener sin volver a relevar lo ya documentado.

**Resultado esperado**: Una aplicación de consola autocontenida (un único archivo Python o un `.exe`) que ocupa toda la ventana, muestra dos paneles simétricos, permite navegar el sistema de archivos y ejecutar operaciones de archivo con feedback visual, validaciones previas y manejo de errores, sin persistencia de configuración.

---

## 2. Alcance

Qué SÍ incluye esta funcionalidad/proyecto:

- Aplicación de consola interactiva (TUI) de doble panel para Windows.
- Navegación por carpetas, unidades y sistema de archivos.
- Operaciones sobre archivos y carpetas: ver, editar con Notepad, copiar, mover/renombrar, crear carpeta, borrar.
- Cambio de unidad o ruta, ordenación y visibilidad de archivos ocultos.
- Visor interno de solo lectura (texto y hexadecimal) con detección de codificación.
- Menú superior con acciones y atajos de teclado F1–F10.
- Búsqueda rápida incremental por nombre.
- Marcado múltiple de entradas.
- Renderizado sin parpadeo mediante doble búfer y `WriteConsoleOutputW` (sin ANSI).
- Autoprueba `--selftest` y pruebas headless (5 escenarios).
- Empaquetado con PyInstaller en un ejecutable único.

---

## 3. Fuera de alcance

Qué explícitamente NO cubre esta spec (evita scope creep y ambigüedad futura):

- Persistencia de configuración, historial o preferencias entre sesiones.
- Uso de la Papelera de Reciclaje o deshacer operaciones.
- Edición de archivos dentro del visor (solo lectura).
- Soporte de sistemas operativos distintos de Windows.
- Instalador, firma digital, icono personalizado, recurso de versión o asociación de archivos.
- Soporte de rutas largas (`\\?\`) ni rutas UNC en la vista de unidades (aunque se pueden escribir manualmente).
- Soporte de ratón para operaciones (solo selección de panel/entrada; ver RF-21 y PA-02).
- Concurrencia o hilos; todas las operaciones son síncronas.
- Edición de archivos binarios o formatos especiales.

---

## 4. Actores / roles

> Un actor puede ser una persona, otro sistema o un dispositivo.

| Actor | Descripción | Interacción principal |
|---|---|---|
| Usuario operador | Persona que usa la aplicación en la consola | Navega, selecciona, ejecuta operaciones y confirma diálogos |
| Consola de Windows | Dispositivo/terminal donde se renderiza la interfaz | Provee entrada de teclado/ratón y salida de texto; tamaño mínimo 40×12 |
| Sistema de archivos de Windows | Sistema externo que almacena carpetas y archivos | Se lee, crea, modifica y borra según las operaciones del usuario |
| Aplicaciones asociadas de Windows | Sistemas externos invocados por el SO | Abren archivos al pulsar Enter; Notepad edita archivos al usar F4 |
| Fuente de consola | Componente del entorno (fuente de texto) | Provee los glifos de dibujo de caja; si no, se usa modo ASCII |

---

## 5. Reglas de negocio

| Código | Regla | Origen | Base |
|---|---|---|---|
| RN-01 | La aplicación solo funciona en Windows; en otros sistemas aborta con el mensaje `WorkCommander solo funciona en Windows.` | README §3, §16; código líneas 1-4 | Hecho explícito |
| RN-02 | Se requiere una consola interactiva con al menos 40 columnas × 12 filas; por debajo se muestra el aviso `Consola demasiado pequeña.` | README §3, §14; código `draw()` | Hecho explícito |
| RN-03 | `show_hidden` (mostrar archivos ocultos) comienza en `True`; los ocultos se ven por defecto | README §5.3, §7.14; código `__init__` | Hecho explícito |
| RN-04 | En una carpeta normal, `entries[0]` es siempre la entrada especial `..` | README §5.1; código `Panel.reload()` | Hecho explícito |
| RN-05 | En la vista de unidades (`panel.path is None`) no hay `..`; solo unidades existentes `A:\`–`Z:\` en orden alfabético | README §5.1, §7.3; código `Panel.reload()` | Hecho explícito |
| RN-06 | Las entradas `..` y las unidades no son seleccionables para operaciones ni marcables | README §5.1; código `selected_entries()`, `toggle_mark()` | Hecho explícito |
| RN-07 | Las carpetas se ordenan siempre por nombre y van antes que los archivos | README §5.1, §7.13; código `Panel.sort_entries()` | Hecho explícito |
| RN-08 | El borrado es permanente: no se usa la Papelera de Reciclaje y no hay deshacer | README §7.11, §15.1; código `op_delete()` | Hecho explícito |
| RN-09 | Al pulsar Enter sobre un archivo se ejecuta/abre con su aplicación asociada (`os.startfile`), sin confirmación previa | README §7.3, §15.5; código `op_enter()` | Hecho explícito |
| RN-10 | El visor interno es de solo lectura y lee como máximo 8 MiB (+1 byte para detectar truncado) | README §7.6; código `view_file()` | Hecho explícito |
| RN-11 | Las operaciones de copiar, mover y borrar usan la selección: si hay marcas, solo las marcadas; si no, la entrada bajo el cursor (salvo `..` o unidad, que dan selección vacía) | README §7.4; código `selected_entries()` | Hecho explícito |
| RN-12 | Las marcas se guardan por nombre y se conservan tras recargar el panel, intersectando con los nombres existentes | README §5.2, §7.4; código `Panel.reload()` | Hecho explícito |
| RN-13 | La confirmación de sobrescritura es única para todo el lote; no hay opciones "sí a todo / no a todo / renombrar" por archivo | README §7.8, §15.11; código `op_copy()`, `op_move()` | Hecho explícito |
| RN-14 | No se sobrescribe una carpeta con un archivo ni un archivo con una carpeta en copia/movimiento; esos casos se rechazan | README §7.8, §7.9, §15.8-10; código `op_copy()`, `op_move()` | Hecho explícito |
| RN-15 | No se puede copiar una carpeta dentro de sí misma ni de una subcarpeta suya | README §7.8; código `op_copy()` | Hecho explícito |
| RN-16 | F3 nunca rechaza un archivo: los binarios ofrecen elegir texto o hexadecimal; los archivos ocultos se pueden abrir por ruta | README §7.6, §19; código `view_file()`, `op_view()` | Hecho explícito |
| RN-17 | Se considera oculto lo que tenga el atributo Win32 `FILE_ATTRIBUTE_HIDDEN` (`0x2`), incluidos directorios | README §7.14; código `Panel.reload()` | Hecho explícito |
| RN-18 | Los caracteres de marco son Unicode por defecto; se activa el modo ASCII si `WORKCOMMANDER_ASCII` tiene un valor distinto de vacío, `0` o `no` (nota: `false` también activa ASCII) | README §9.7; código constante `_ASCII_FRAME` | Hecho explícito |
| RN-19 | Las operaciones son síncronas en el hilo de la interfaz; copiar, mover y borrar congelan la UI hasta terminar | README §14; código `run()`, `op_*` | Hecho explícito |
| RN-20 | La prioridad de los requisitos funcionales no estaba definida en las fuentes; se consultó al requirente, quien definió prioridad Media para todos los RF (consulta PA-01, respondida) | README (sin sección de prioridades); código (sin prioridades); consulta al usuario 20/11/2026 | Hecho explícito |

---

## 6. Requisitos funcionales

### RF-01: Arranque y parámetros de línea de comandos

**Descripción**: Al iniciar, la aplicación toma como carpeta inicial el primer argumento de línea de comandos que no empiece por `-` y sea un directorio existente; si no hay ninguno válido, usa el directorio de trabajo actual. Convierte la ruta a absoluta y crea dos paneles con esa misma ruta. Si se pasa `--selftest`, dibuja un fotograma completo, restaura la consola y devuelve 0. Cualquier excepción al crear la aplicación se informa y devuelve 1.

**Reglas relacionadas**: RN-01, RN-02

**Criterios de aceptación**:

CA-RF01-01: Arranque con carpeta inicial por argumento
```
Given una consola interactiva de Windows y una carpeta existente D:\Proyectos
When se ejecuta WorkCommander con el argumento "D:\Proyectos"
Then ambos paneles muestran el contenido de D:\Proyectos y la aplicación queda en ejecución
```

CA-RF01-02: Arranque sin argumento válido
```
Given ninguna carpeta válida pasada como argumento
When se inicia la aplicación
Then ambos paneles arrancan en el directorio de trabajo actual (ruta absoluta)
```

CA-RF01-03: Autoprueba
```
Given una consola interactiva real
When se ejecuta con --selftest
Then se dibuja un fotograma completo, se restaura la consola y el código de salida es 0
```

**Prioridad**: Media

**Origen**: README §2.3, §7.1, §19; código `main()`, `WorkCommander.__init__()`

**Base**: Hecho explícito

---

### RF-02: Bucle principal y redibujado

**Descripción**: El bucle principal dibuja la interfaz, sondea la entrada cada 20 ms, detecta cambios de tamaño de la consola y redibuja; en reposo redibuja como máximo una vez por segundo para actualizar el reloj. `KeyboardInterrupt` sale limpiamente. Al salir se ejecuta `cleanup()`.

**Reglas relacionadas**: RN-19

**Criterios de aceptación**:

CA-RF02-01: Redibujado por cambio de tamaño
```
Given la aplicación en ejecución
When cambia el tamaño de la consola
Then se limpia el búfer, se recrea la rejilla y se repinta la interfaz completa
```

CA-RF02-02: Reloj en reposo
```
Given la aplicación en reposo sin teclas
When transcurre 1 segundo
Then se redibuja la interfaz actualizando la hora en la barra de menú
```

CA-RF02-03: Salida limpia
```
Given la aplicación en ejecución
When el usuario pulsa F10 o Ctrl+C
Then running pasa a False y cleanup() restaura pantalla, cursor, modo de entrada y título
```

**Prioridad**: Media

**Origen**: README §7.2, §7.18; código `WorkCommander.run()`

**Base**: Hecho explícito

---

### RF-03: Navegación entre paneles y entradas

**Descripción**: El usuario se mueve con las flechas, Inicio/Fin, RePág/AvPág; activa el panel izquierdo o derecho con ←/→ o Tab/Shift+Tab. Enter sobre carpeta entra, sobre unidad la abre, sobre archivo lo abre con su aplicación asociada, sobre `..` sube un nivel. Retroceso sube un nivel (y en la raíz de la unidad pasa a la vista de unidades). El desplazamiento vertical se ajusta para mantener visible el cursor.

**Reglas relacionadas**: RN-04, RN-05, RN-06, RN-09

**Criterios de aceptación**:

CA-RF03-01: Entrar en carpeta
```
Given el cursor sobre una carpeta en el panel activo
When el usuario pulsa Enter
Then el panel muestra el contenido de esa carpeta y el cursor queda en la primera entrada
```

CA-RF03-02: Subir de nivel en raíz de unidad
```
Given el panel está en la raíz de una unidad (por ejemplo C:\)
When el usuario pulsa Retroceso
Then el panel pasa a la vista de unidades y el cursor queda sobre la unidad de origen
```

CA-RF03-03: Abrir archivo
```
Given el cursor sobre un archivo no oculto listado
When el usuario pulsa Enter
Then el archivo se abre con su aplicación asociada de Windows
```

CA-RF03-04: Cambio de panel activo
```
Given dos paneles visibles
When el usuario pulsa Tab
Then el panel activo alterna y su marco se resalta en blanco brillante
```

**Prioridad**: Media

**Origen**: README §6.2, §7.3; código `op_enter()`, `op_up()`, `handle_key()`

**Base**: Hecho explícito

---

### RF-04: Vista de unidades

**Descripción**: Cuando `panel.path is None`, el panel lista las unidades `A:\`–`Z:\` existentes en orden alfabético, sin entrada `..`. No se puede marcar ni operar en esta vista. Subir desde la raíz de una unidad vuelve a esta vista.

**Reglas relacionadas**: RN-05, RN-06

**Criterios de aceptación**:

CA-RF04-01: Listado de unidades existentes
```
Given el panel en vista de unidades
When se dibuja el panel
Then se muestran solo las unidades existentes (A:\ a Z:\) en orden alfabético, sin ".."
```

CA-RF04-02: Sin operaciones en vista de unidades
```
Given el panel en vista de unidades
When el usuario intenta marcar o ejecutar una operación de archivo
Then no se marca ni se opera ninguna entrada
```

**Prioridad**: Media

**Origen**: README §5.1, §7.3; código `Panel.reload()`

**Base**: Hecho explícito

---

### RF-05: Marcado múltiple

**Descripción**: Insert marca/desmarca la entrada actual y avanza una fila. Las marcas se dibujan en amarillo. Las operaciones usan la selección resultante. Tras copiar/mover/borrar se limpian las marcas o se intersectan por nombre en las recargas.

**Reglas relacionadas**: RN-06, RN-11, RN-12

**Criterios de aceptación**:

CA-RF05-01: Marcar y avanzar
```
Given el cursor sobre una entrada operable
When el usuario pulsa Insert
Then la entrada se marca (amarillo) y el cursor avanza una fila
```

CA-RF05-02: Selección con marcas
```
Given existen entradas marcadas en el panel activo
When se ejecuta una operación de copiar/mover/borrar
Then se operan únicamente las entradas marcadas
```

**Prioridad**: Media

**Origen**: README §6.2, §7.4; código `toggle_mark()`, `selected_entries()`

**Base**: Hecho explícito

---

### RF-06: Búsqueda rápida incremental

**Descripción**: Cualquier carácter imprimible en el panel acumula un buffer durante 1,2 segundos; se busca la primera entrada cuyo nombre (en minúsculas) empiece por el buffer. No es cíclica y no distingue mayúsculas/minúsculas ni acentos.

**Reglas relacionadas**: RN-04, RN-05

**Criterios de aceptación**:

CA-RF06-01: Búsqueda por prefijo
```
Given un panel con entradas cuyos nombres empiezan por distintas letras
When el usuario escribe "no"
Then el cursor se sitúa en la primera entrada cuyo nombre empieza por "no"
```

CA-RF06-02: Reinicio del buffer
```
Given el usuario escribió caracteres hace más de 1,2 segundos
When escribe un nuevo carácter
Then el buffer se reinicia con ese carácter
```

**Prioridad**: Media

**Origen**: README §7.5; código `quick_search()`

**Base**: Hecho explícito

---

### RF-07: Visualización de archivos (visor interno)

**Descripción**: F3 abre cualquier archivo listado en un visor modal que ocupa la mitad de la pantalla correspondiente al panel activo (el otro panel sigue visible). Detecta UTF-16 por BOM o patrón de bytes nulos alternos; si no es UTF-16 y contiene `\x00` en los primeros 8 KiB, ofrece elegir texto o hexadecimal. Decodifica probando BOM UTF-8, UTF-16, UTF-8 y cp1252. Convierte tabuladores a 4 espacios y parte líneas que exceden el ancho. El visor se cierra con Esc/q/Q. El menú ofrece "Ver forzado (texto/hex)" y "Ver archivo por ruta..." (permite rutas ocultas o fuera del panel).

**Reglas relacionadas**: RN-10, RN-16

**Criterios de aceptación**:

CA-RF07-01: Texto normal
```
Given un archivo de texto UTF-8 listado
When el usuario pulsa F3
Then se muestra su contenido en el visor de media pantalla con tamaño, estado de truncado y rango de líneas
```

CA-RF07-02: Archivo binario
```
Given un archivo que contiene \x00 y no parece UTF-16
When el usuario pulsa F3
Then se muestra un diálogo con opciones Texto y Hexadecimal y Esc cancela
```

CA-RF07-03: Volcado hexadecimal
```
Given el usuario elige Hexadecimal
When se abre el visor
Then se muestra un volcado hex con columna ASCII adaptado al ancho (16/8/4 bytes por fila)
```

CA-RF07-04: Ver archivo por ruta
```
Given una ruta de archivo oculto o no listado
When se usa Archivo > Ver archivo por ruta... y se confirma
Then se abre ese archivo en el visor si existe
```

CA-RF07-05: Cierre del visor
```
Given un visor abierto en el panel activo
When el usuario pulsa Esc o q o Q
Then el visor se cierra y el panel vuelve a mostrarse
```

**Prioridad**: Media

**Origen**: README §7.6; código `view_file()`, `op_view()`, `op_view_force()`, `op_view_path()`, `_draw_viewer()`

**Base**: Hecho explícito (código difiere del README en la modalidad de media pantalla; ver PA-03, PA-05)

---

### RF-08: Edición con Notepad

**Descripción**: F4 lanza `notepad.exe` con la ruta del archivo seleccionado, esperando a que se cierre. Al volver fuerza redimensionado, oculta el cursor y redibuja. No recarga los paneles automáticamente (usar F2 para ver cambios de tamaño/fecha). Solo actúa sobre archivos.

**Reglas relacionadas**: RN-09

**Criterios de aceptación**:

CA-RF08-01: Editar archivo existente
```
Given el cursor sobre un archivo (no carpeta ni unidad)
When el usuario pulsa F4
Then se lanza Notepad con ese archivo y la aplicación espera a su cierre
```

CA-RF08-02: Retorno sin recarga automática
```
Given se cerró Notepad tras editar
When la aplicación vuelve al panel
Then la interfaz se redibuja pero los metadatos del archivo no se actualizan hasta F2
```

**Prioridad**: Media

**Origen**: README §7.7; código `op_edit()`

**Base**: Hecho explícito

---

### RF-09: Copia de archivos y carpetas

**Descripción**: F5 copia la selección al otro panel (o a la ruta indicada). Construye el destino según los casos documentados (1 origen vs varios; carpeta existente vs inexistente). Valida previamente mismo origen/destino, carpeta sobre archivo, carpeta dentro de sí misma, archivo sobre carpeta. Pide una única confirmación de sobrescritura si hay destinos existentes. Planifica carpetas y archivos, crea carpetas primero, copia con `shutil.copy2` conservando metadatos, muestra progreso con barra y permite cancelar con Esc. Acumula errores y los muestra al final (máximo 8). Recarga ambos paneles siempre.

**Reglas relacionadas**: RN-11, RN-13, RN-14, RN-15

**Criterios de aceptación**:

CA-RF09-01: Copiar archivo a carpeta existente
```
Given un archivo seleccionado en el panel activo y el otro panel en una carpeta existente
When el usuario pulsa F5 y confirma
Then el archivo aparece en la carpeta destino con sus metadatos conservados
```

CA-RF09-02: Copiar carpeta recursivamente
```
Given una carpeta seleccionada
When se copia a un destino válido
Then se crean todas las subcarpetas (incluidas las vacías) y se copian todos los archivos
```

CA-RF09-03: Rechazo de copia inválida
```
Given se intenta copiar una carpeta sobre un archivo existente (o un archivo sobre una carpeta, o una carpeta dentro de sí misma)
When se valida la operación
Then se muestra el mensaje de error correspondiente y no se modifica el disco
```

CA-RF09-04: Cancelación de copia
```
Given una copia en progreso
When el usuario pulsa Esc
Then la copia se detiene, se muestra "Operacion cancelada por el usuario." y no se reporta éxito
```

CA-RF09-05: Sobrescritura única
```
Given existen destinos que ya existen
When se solicita confirmación
Then se pide una única confirmación para todos; si se cancela, no se toca nada
```

**Prioridad**: Media

**Origen**: README §7.8; código `op_copy()`, `_copy_jobs()`

**Base**: Hecho explícito

---

### RF-10: Movimiento y renombrado

**Descripción**: F6 mueve o renombra. Un solo elemento: si el texto es un nombre simple, renombra en la misma carpeta; si es una ruta con separador o unidad, normaliza y, si el resultado es una carpeta existente, mueve dentro conservando el nombre. Si el destino es idéntico al origen, no hace nada. Si el destino existe: carpeta se rechaza siempre; archivo pide confirmación y se elimina antes de mover. Usa `shutil.move`. Varios elementos: pide carpeta destino existente, confirma sobrescrituras en bloque, omite (con error) si el destino es carpeta, elimina y mueve si es archivo. Limpia marcas y recarga ambos paneles.

**Reglas relacionadas**: RN-11, RN-13, RN-14

**Criterios de aceptación**:

CA-RF10-01: Renombrar en la misma carpeta
```
Given un único archivo seleccionado
When el usuario pulsa F6 e introduce un nombre simple sin separadores
Then el archivo se renombra dentro de la misma carpeta
```

CA-RF10-02: Mover a carpeta existente
```
Given un único elemento seleccionado
When el usuario introduce una ruta que resulta una carpeta existente
Then el elemento se mueve dentro de esa carpeta conservando su nombre
```

CA-RF10-03: Rechazo de mover archivo sobre carpeta
```
Given el destino ya existe como carpeta
When se intenta mover un archivo sobre ella
Then se rechaza con "Ya existe una carpeta con ese nombre. No se sobrescribe con un archivo."
```

CA-RF10-04: Movimiento múltiple con destino inválido
```
Given varios elementos marcados
When el destino no es una carpeta existente
Then se muestra error y no se mueve nada
```

**Prioridad**: Media

**Origen**: README §7.9; código `op_move()`

**Base**: Hecho explícito

---

### RF-11: Creación de carpetas

**Descripción**: F7 crea una carpeta. No disponible en la vista de unidades. Pide un nombre; si es ruta absoluta se usa tal cual, si es relativa se crea dentro del panel activo. Usa `os.makedirs` (crea niveles intermedios). Si ya existe, muestra error. Al terminar el cursor queda sobre la carpeta creada y se muestra `Carpeta creada: nombre`.

**Reglas relacionadas**: RN-05

**Criterios de aceptación**:

CA-RF11-01: Crear carpeta simple
```
Given el panel activo en una carpeta válida
When el usuario pulsa F7 e introduce un nombre
Then se crea la carpeta y el cursor queda sobre ella
```

CA-RF11-02: Crear carpeta con niveles intermedios
```
Given el usuario introduce una ruta relativa con separadores
When se confirma
Then se crean todos los niveles intermedios
```

CA-RF11-03: Carpeta ya existente
```
Given el nombre introducido ya existe
When se confirma
Then se muestra un diálogo de error y no se modifica nada
```

CA-RF11-04: No disponible en vista de unidades
```
Given el panel en vista de unidades
When el usuario pulsa F7
Then la operación no está disponible / no actúa
```

**Prioridad**: Media

**Origen**: README §7.10; código `op_mkdir()`

**Base**: Hecho explícito

---

### RF-12: Borrado permanente

**Descripción**: F8 (y Supr) borra la selección tras una confirmación que indica el número de elementos, hasta 3 nombres y el aviso `Esta accion no se puede deshacer.`. Carpetas (que no sean enlaces simbólicos) se borran con `shutil.rmtree` reintentando tras `chmod +w`; archivos con `os.remove` reintentando tras `chmod +w` en caso de `PermissionError`. No usa la Papelera. Limpia marcas, recarga ambos paneles y muestra error o `Borrado: N elemento(s)`.

**Reglas relacionadas**: RN-08, RN-11

**Criterios de aceptación**:

CA-RF12-01: Borrado con confirmación
```
Given una selección de archivos/carpetas
When el usuario pulsa F8 y confirma
Then los elementos se borran permanentemente y se muestra "Borrado: N elemento(s)"
```

CA-RF12-02: Cancelación de borrado
```
Given el diálogo de confirmación
When el usuario responde no o Esc
Then no se borra nada
```

CA-RF12-03: Permiso denegado con reintento
```
Given un archivo de solo lectura
When se borra
Then se intenta chmod +w y se reintenta el borrado
```

**Prioridad**: Media

**Origen**: README §7.11; código `op_delete()`

**Base**: Hecho explícito

---

### RF-13: Cambio de unidad o ruta

**Descripción**: El menú "Cambiar unidad o ruta..." pide una unidad (`D:`) o una ruta. Expande variables y `~`, quita comillas. Si el texto es exactamente dos caracteres y el segundo es `:`, añade `\`. Convierte a absoluta y comprueba que sea un directorio; si no existe muestra `La ruta no existe:`. Si es válida, cambia `panel.path`, recarga y coloca el cursor en 0.

**Reglas relacionadas**: RN-05

**Criterios de aceptación**:

CA-RF13-01: Cambiar a una ruta válida
```
Given una ruta de directorio existente
When el usuario la introduce en "Cambiar unidad o ruta..."
Then el panel cambia a esa ruta y el cursor queda en la primera entrada
```

CA-RF13-02: Ruta inexistente
```
Given una ruta que no existe
When se confirma
Then se muestra "La ruta no existe:" con la ruta y no se cambia el panel
```

CA-RF13-03: Atajo de unidad
```
Given el usuario introduce "D:"
When se confirma
Then se interpreta como "D:\" y se abre si es un directorio
```

**Prioridad**: Media

**Origen**: README §7.12; código `op_changedrive()`

**Base**: Hecho explícito

---

### RF-14: Ordenación de entradas

**Descripción**: El menú Opciones permite ordenar por nombre, extensión, fecha o tamaño, e invertir el orden. Las carpetas van siempre antes que los archivos y se ordenan por nombre; `sort_rev` invierte ambos grupos. En fecha y tamaño el orden normal es descendente. Cambiar de criterio reinicia `sort_rev = False`. El orden es por panel (cada panel conserva su criterio). Ordenar recarga el panel conservando el cursor por nombre si es posible.

**Reglas relacionadas**: RN-07

**Criterios de aceptación**:

CA-RF14-01: Ordenar por extensión
```
Given un panel con archivos de distintas extensiones
When se elige "Ordenar por extensión"
Then los archivos se ordenan por extensión y luego por nombre, con carpetas antes
```

CA-RF14-02: Invertir orden
```
Given un criterio activo
When se elige "Invertir orden"
Then el orden de carpetas y archivos se invierte
```

CA-RF14-03: Orden independiente por panel
```
Given dos paneles con criterios distintos
When se ordena un panel
Then el otro conserva su criterio y orden
```

**Prioridad**: Media

**Origen**: README §7.13; código `_set_sort()`, `op_sort_*()`, `Panel.sort_entries()`

**Base**: Hecho explícito

---

### RF-15: Visibilidad de archivos ocultos

**Descripción**: La opción "Mostrar archivos ocultos" alterna la visibilidad global (`show_hidden`), recarga ambos paneles y muestra el estado (`Archivos ocultos: visibles` u `ocultos`). No hay opción separada para archivos de sistema.

**Reglas relacionadas**: RN-03, RN-17

**Criterios de aceptación**:

CA-RF15-01: Alternar visibilidad
```
Given archivos ocultos en el directorio actual
When el usuario desactiva "Mostrar archivos ocultos"
Then los ocultos desaparecen de ambos paneles y se muestra el estado "ocultos"
```

CA-RF15-02: Estado inicial visible
```
Given la aplicación recién iniciada
When se muestra un directorio con archivos ocultos
Then los archivos ocultos son visibles por defecto
```

**Prioridad**: Media

**Origen**: README §7.14; código `op_toggle_hidden()`

**Base**: Hecho explícito

---

### RF-16: Refresco de paneles

**Descripción**: F2 o Ctrl+R recargan ambos paneles, conservando el cursor por nombre cuando es posible, y muestran `Paneles actualizados`. Útil tras editar con Notepad o cambios externos.

**Reglas relacionadas**: RN-12

**Criterios de aceptación**:

CA-RF16-01: Refresco manual
```
Given cambios externos en las carpetas mostradas
When el usuario pulsa F2
Then ambos paneles se recargan y se muestra "Paneles actualizados"
```

CA-RF16-02: Conservación del cursor
```
Given el cursor sobre un elemento existente
When se refresca
Then el cursor permanece sobre ese elemento si sigue existiendo
```

**Prioridad**: Media

**Origen**: README §7.15; código `op_refresh()`

**Base**: Hecho explícito

---

### RF-17: Menú superior y acciones

**Descripción**: F9 abre un menú superior con tres menús (Archivo, Opciones, Ayuda) y sus acciones. Se navega con flechas, ←/→ cambia de menú, Tab avanza, Enter/Espacio ejecuta, una letra salta a la primera acción que empiece por ella, Esc cierra, F10 sale. El menú se dibuja superpuesto con sombra; los separadores son líneas. Las acciones se invocan por nombre de método. Las teclas de función se muestran a la derecha cuando caben.

**Reglas relacionadas**: (ninguna específica)

**Criterios de aceptación**:

CA-RF17-01: Abrir y navegar el menú
```
Given la aplicación en ejecución
When el usuario pulsa F9
Then se muestra el menú superior y se puede navegar con flechas y cambiar de menú con ←/→
```

CA-RF17-02: Ejecutar acción
```
Given un menú abierto con una acción seleccionada
When el usuario pulsa Enter
Then el menú se cierra y se ejecuta la acción correspondiente
```

CA-RF17-03: Cierre con Esc
```
Given un menú abierto
When el usuario pulsa Esc
Then el menú se cierra sin ejecutar ninguna acción
```

**Prioridad**: Media

**Origen**: README §7.16; código `menu_loop()`, `draw_menu()`, `MENUS`

**Base**: Hecho explícito

---

### RF-18: Ayuda y Acerca de

**Descripción**: El menú Ayuda ofrece "Teclas", que abre un paginador de pantalla completa con `HELP_TEXT`, y "Acerca de WorkCommander", que muestra un diálogo con nombre, versión 1.2, descripción y tecnologías.

**Reglas relacionadas**: (ninguna específica)

**Criterios de aceptación**:

CA-RF18-01: Ayuda de teclas
```
Given el menú Ayuda abierto
When se selecciona "Teclas"
Then se muestra un paginador de pantalla completa con el resumen de funciones, navegación y operaciones
```

CA-RF18-02: Acerca de
```
Given el menú Ayuda abierto
When se selecciona "Acerca de WorkCommander"
Then se muestra un diálogo con nombre, versión, descripción y tecnologías
```

**Prioridad**: Media

**Origen**: README §7.17; código `op_help()`, `op_about()`

**Base**: Hecho explícito (versión 1.2 según código; README registro de cambios solo hasta 1.1, ver PA-04)

---

### RF-19: Salida y limpieza de consola

**Descripción**: F10, Ctrl+C o la acción Salir ponen `running = False`. El `finally` de `run()` llama a `cleanup()`: rellena la pantalla con espacios, vuelca el búfer, muestra el cursor, coloca el cursor arriba a la izquierda, restaura el modo de entrada original y el título original de la consola (o `WorkCommander`).

**Reglas relacionadas**: RN-01

**Criterios de aceptación**:

CA-RF19-01: Salida con F10
```
Given la aplicación en ejecución
When el usuario pulsa F10
Then la aplicación termina y la consola queda usable
```

CA-RF19-02: Restauración de consola
```
Given la aplicación terminó normalmente
When se inspecciona la consola
Then el título original se restauró, el cursor es visible y el modo de entrada es el original
```

**Prioridad**: Media

**Origen**: README §7.18; código `op_quit()`, `Screen.cleanup()`

**Base**: Hecho explícito

---

### RF-20: Renderizado sin parpadeo (capa Win32)

**Descripción**: La interfaz se renderiza con un doble búfer propio (rejilla de tuplas `(carácter, atributo)`) volcado en una sola llamada a `WriteConsoleOutputW`. No usa ANSI/VT. Oculta el cursor durante el uso. Amplía el búfer si la ventana creció, nunca lo reduce. Caracteres fuera del BMP se sustituyen por `?`. Los caracteres de control se convierten en espacios en `put()`.

**Reglas relacionadas**: RN-02, RN-18

**Criterios de aceptación**:

CA-RF20-01: Fotograma completo en una llamada
```
Given una ventana visible de W×H
When se ejecuta flush()
Then se escribe toda la ventana en una única llamada a WriteConsoleOutputW sin borrar antes
```

CA-RF20-02: Ampliación de búfer
```
Given la ventana creció respecto al búfer actual
When se sincroniza el tamaño
Then el búfer se amplía (max) y la rejilla se recrea
```

**Prioridad**: Media

**Origen**: README §8.1, §9.5; código `Screen.flush()`, `Screen.sync_size()`

**Base**: Hecho explícito

---

### RF-21: Soporte de mouse (selección)

**Descripción**: La aplicación habilita la entrada de ratón en la consola (desactivando Quick Edit). Un clic izquierdo sin movimiento activa el panel correspondiente (izquierdo o derecho) y, si no hay visor abierto en ese lado, selecciona la entrada de la fila clicada. El menú ignora los eventos de ratón (solo actualiza la posición). Esta funcionalidad no está documentada en el README (que afirma "sin ratón"), por lo que se requiere confirmación de alcance (PA-02).

**Reglas relacionadas**: (ninguna específica)

**Criterios de aceptación**:

CA-RF21-01: Activar panel y seleccionar entrada con clic
```
Given dos paneles visibles sin visor
When el usuario hace clic izquierdo en una fila del panel derecho
Then el panel derecho queda activo y el cursor se sitúa en la entrada clicada
```

CA-RF21-02: Mouse en menú
```
Given el menú superior abierto
When se mueven eventos de ratón
Then solo se actualiza la posición del cursor de ratón, sin ejecutar acciones
```

**Prioridad**: Media

**Origen**: código `handle_mouse()`, `_configure()`; README §3 (afirma "No se necesita ratón" y §15.17 "Sin ratón")

**Base**: Inferencia razonable → PA-02

---

### RF-22: Consola demasiado pequeña

**Descripción**: Si la ventana tiene menos de 40 columnas o 12 filas, en lugar de la interfaz se muestra el mensaje `Consola demasiado pequeña.` y la indicación de agrandar a 40×12. El resto de la funcionalidad no está disponible hasta agrandar.

**Reglas relacionadas**: RN-02

**Criterios de aceptación**:

CA-RF22-01: Aviso en consola pequeña
```
Given una ventana de 30×10
When se dibuja la interfaz
Then se muestra "Consola demasiado pequeña." y la indicación de tamaño mínimo
```

**Prioridad**: Media

**Origen**: README §3, §14; código `draw()`

**Base**: Hecho explícito

---

### RF-23: Pruebas headless y contratos

**Descripción**: El proyecto incluye `tests/headless_test.py` con 5 pruebas (layout, navegación y orden, copia/movimiento/creación/borrado, visor, capa Win32 simulada) que usan `FakeScreen` y `FakeKernel` y deben pasar 5/5. Estas pruebas no validan consola real, redimensionado físico ni entrada real.

**Reglas relacionadas**: (ninguna específica)

**Criterios de aceptación**:

CA-RF23-01: Ejecución de pruebas
```
Given el entorno Windows con Python 3.8+
When se ejecuta py -3 tests\headless_test.py
Then se imprimen 5 "OK" y el resultado final es "5/5 pruebas correctas"
```

**Prioridad**: Media

**Origen**: README §12; código `tests/headless_test.py`

**Base**: Hecho explícito

---

## 7. Casos borde y manejo de errores

| Código | Caso | Comportamiento esperado |
|---|---|---|
| CB-01 | Borrado permanente sin Papelera | No hay deshacer; la confirmación advierte `Esta accion no se puede deshacer.` |
| CB-02 | Copiar un archivo a una ruta inexistente | Se crea un archivo con ese nombre (no se valida que sea carpeta) |
| CB-03 | Copiar una carpeta sobre un archivo existente | Se rechaza con `El destino existe y no es una carpeta:` |
| CB-04 | Copiar un archivo sobre una carpeta existente | Se rechaza con `El destino es una carpeta y el origen es un archivo:` |
| CB-05 | Copiar una carpeta dentro de sí misma o subcarpeta | Se rechaza con `No se puede copiar una carpeta dentro de si misma.` |
| CB-06 | Mover un archivo sobre una carpeta existente | Se rechaza con `Ya existe una carpeta con ese nombre. No se sobrescribe con un archivo.` |
| CB-07 | Mover varios elementos a destino no carpeta | Error `El destino debe ser una carpeta existente.` |
| CB-08 | Origen y destino idénticos en copia | Error `El origen y el destino son el mismo.` |
| CB-09 | Archivo mayor a 8 MiB en el visor | Se trunca y se indica ` (truncado)` |
| CB-10 | Archivo binario con `\x00` | Se ofrece Texto o Hexadecimal; Esc cancela |
| CB-11 | Carpeta inaccesible en `reload()` | Flash de error y lista vacía con `..` |
| CB-12 | Ventana menor a 40×12 | Se muestra `Consola demasiado pequeña.` en lugar de la interfaz |
| CB-13 | Ruta de más de 260 caracteres | Puede fallar según configuración de Windows; no se activa `\\?\` |
| CB-14 | Enlaces simbólicos y junctions | `os.walk` no sigue enlaces a directorios; `copy2` copia el contenido del archivo enlazado; sin manejo especial de reparse points |
| CB-15 | Proceso matado abruptamente | El título puede quedar `WorkCommander`; no hay cleanup |
| CB-16 | Ejecutable en ejecución al compilar | `PermissionError (WinError 5)`; cerrar instancias antes |
| CB-17 | Fuentes sin glifos de caja | Marcos se ven como letras raras; usar Consolas/Cascadia o `WORKCOMMANDER_ASCII=1` (nota: `false` también activa ASCII) |

---

## 8. Modelo de datos conceptual

> Entidades principales y relaciones, sin definir el esquema de base de datos: eso es diseño, no especificación.

**Entidad: Entry**
- `name`: str — nombre mostrado (`..`, `C:\`, nombre de archivo o carpeta)
- `path`: str | None — ruta absoluta; None para `..` y unidades
- `is_dir`: bool — es carpeta (incluye unidades y `..`)
- `size`: int — tamaño en bytes; 0 para carpetas
- `mtime`: float — fecha de modificación Unix; 0 si no se pudo leer
- `is_parent`: bool — es la entrada especial `..`
- `is_drive`: bool — es una unidad de la vista `Unidades`
- `hidden`: bool — tenía el atributo Win32 `FILE_ATTRIBUTE_HIDDEN` (`0x2`)
- Relación con: Panel (contenida en `entries`)

**Entidad: Panel**
- `app`: referencia a WorkCommander (para `show_hidden`, `flash`, etc.)
- `path`: str | None — ruta actual o None para vista de unidades
- `entries`: lista de Entry — lista ya ordenada
- `index`: int — índice del cursor dentro de `entries`
- `offset`: int — primera fila visible (scroll)
- `marked`: conjunto de nombres (str) — nombres marcados (no rutas)
- `sort_key`: str — "name", "ext", "date" o "size"
- `sort_rev`: bool — invertir el orden
- Relación con: WorkCommander (contenida en `panels`)

**Entidad: WorkCommander (estado global)**
- `scr`: Screen real o FakeScreen (pruebas)
- `show_hidden`: bool — inicialmente True
- `active`: int — panel activo (0 izquierdo, 1 derecho)
- `running`: bool — bucle principal activo
- `flash_text`, `flash_error`, `flash_time`: mensaje temporal de la barra de estado
- `last_draw`: float — última vez que se dibujó (reloj)
- `menu_open`, `menu_idx`, `item_idx`, `menu_x`: estado del menú superior
- `_prog`: estado interno del progreso de copia (None si no hay copia)
- `search_buf`, `search_time`: búsqueda rápida incremental
- `panels`: dos Panel — ambos arrancan en la misma ruta inicial
- `viewers`: viewer o None por panel — visor modal por panel
- `mouse_x`, `mouse_y`, `mouse_over`: estado del ratón
- Relación con: Panel, Screen, Entry

**Entidad: Screen (capa de renderizado)**
- Rejilla plana de tuplas `(carácter, atributo)` de tamaño `ancho * alto`
- Handles de consola Win32, título original, modo de entrada original
- Relación con: WorkCommander (inyectable para pruebas)

---

## 9. Restricciones y supuestos

**Restricciones**:
- Técnicas: solo Windows; requiere consola interactiva real; sin dependencias externas en ejecución; sin ANSI/VT; sin elevación de privilegios; rutas de hasta 260 caracteres (sin `\\?\`); sin Internet (salvo instalación de PyInstaller para compilar).
- De negocio: borrado permanente sin Papelera; sin persistencia de configuración; sin edición en el visor.
- De tiempo/recursos: operaciones síncronas que congelan la interfaz; solo la copia muestra progreso y permite cancelar.
- De entorno: fuente de consola con glifos de caja (o activar modo ASCII); ventana mínima 40×12.

**Supuestos**:
- El usuario tiene permisos suficientes sobre las rutas sobre las que opera; los errores de acceso se muestran en un diálogo. → PA-06 (confirmar si se requiere manejo de permisos elevados)
- La consola soporta `WriteConsoleOutputW` y el modo de entrada extendido. → PA-06
- El comportamiento documentado en el código fuente prevalece sobre el README cuando hay contradicción (mouse, visor de media pantalla, versión 1.2). → PA-02, PA-03, PA-04

---

## 10. Definición de "hecho" (Definition of Done)

- [ ] Todos los requisitos funcionales (RF-0X) tienen criterios de aceptación verificados
- [ ] Casos borde de la sección 7 cubiertos con manejo explícito
- [ ] Preguntas abiertas de impacto alto respondidas
- [ ] Documentación actualizada (README, ficha técnica, hashes) tras cambios de comportamiento
- [ ] Revisión de stakeholder aprobada
- [ ] Tests headless (5/5) pasando
- [ ] `--selftest` devuelve 0 en una consola real
- [ ] Ejecutable recompilado si se modificó el código

---

## 11. Preguntas abiertas

| Código | Pregunta | Impacto | Quién responde | Estado |
|---|---|---|---|---|
| PA-01 | ¿Qué prioridad (Alta/Media/Baja) tiene cada requisito funcional RF-01 a RF-23? Las fuentes no definen prioridades por requisito. (Respondida: prioridad Media para todos los RF.) | Medio: afecta planificación y orden de implementación | Product owner / requirente | Respondida |
| PA-02 | El README afirma "Sin ratón: no hay clic, rueda ni selección con ratón" (§3, §15.17), pero el código implementa selección de panel/entrada con clic izquierdo y habilita ENABLE_MOUSE_INPUT. ¿Es el soporte de ratón una funcionalidad intencional que debe documentarse y mantenerse? | Medio: define alcance de entrada soportada y pruebas | Product owner / desarrollador | Abierta |
| PA-03 | El README describe F3 como un paginador bloqueante de pantalla completa, pero el código implementa un visor modal que ocupa la mitad de la pantalla (panel activo) y enruta las teclas hasta cerrarlo. ¿Cuál es el comportamiento deseado y a documentar? | Medio: afecta UX y documentación | Product owner / desarrollador | Abierta |
| PA-04 | La ficha técnica del README dice versión 1.2 y el código muestra "WorkCommander 1.2" en Acerca de, pero el registro de cambios solo documenta hasta 1.1. ¿Cuál es la versión vigente y qué cambios la justifican? | Bajo: trazabilidad y comunicación | Product owner / desarrollador | Abierta |
| PA-05 | El README indica que F10 cierra el visor, pero el código no maneja F10 en el visor (solo Esc/q/Q). ¿Debe F10 cerrar el visor o salir de la aplicación? | Bajo: comportamiento de tecla en visor | Product owner / desarrollador | Abierta |
| PA-06 | ¿Se requiere manejo de permisos elevados o rutas protegidas más allá del reintento con chmod +w? ¿Y soporte de rutas largas (`\\?\`)? | Bajo: casos borde de acceso | Product owner / desarrollador | Abierta |

---

## Historial de cambios

| Versión | Fecha | Cambio | Autor |
|---|---|---|---|
| 0.1 | 2026-11-20 | Versión inicial de la especificación funcional | Pablo |