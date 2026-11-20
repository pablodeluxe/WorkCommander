# Casos de prueba manuales — WorkCommander

> Generados a partir de SPEC-001 y las historias US-001…US-021.
> Formato genérico (Markdown). Un caso por criterio de aceptación (CA) y caso borde (CB) citado.
> Prioridad heredada: Media (todos los RF). Estado: Borrador.

---

## US-001 — Arrancar WorkCommander y elegir carpeta inicial (RF-01)

### TC-001: Arranque con carpeta inicial por argumento
- **Origen:** CA-RF01-01
- **Precondiciones:** Consola interactiva de Windows disponible. Carpeta `D:\Proyectos` existe y es accesible.
- **Datos de prueba:** Argumento `"D:\Proyectos"`.
- **Pasos:**
  1. Acción: Ejecutar `WorkCommander.exe "D:\Proyectos"`. → Esperado: la aplicación inicia sin error.
  2. Acción: Observar ambos paneles. → Esperado: ambos muestran el contenido de `D:\Proyectos`.
  3. Acción: Interactuar con la UI. → Esperado: la aplicación queda en ejecución.
- **Resultado esperado final:** Arranque correcto en la carpeta indicada.

### TC-002: Arranque sin argumento válido
- **Origen:** CA-RF01-02
- **Precondiciones:** Consola interactiva disponible. Directorio de trabajo actual conocido.
- **Datos de prueba:** Sin argumentos.
- **Pasos:**
  1. Acción: Ejecutar `WorkCommander.exe` sin argumentos. → Esperado: la aplicación inicia.
  2. Acción: Observar ambos paneles. → Esperado: ambos arrancan en el directorio de trabajo actual (ruta absoluta).
- **Resultado esperado final:** Arranque en cwd.

### TC-003: Autoprueba (--selftest)
- **Origen:** CA-RF01-03
- **Precondiciones:** Consola interactiva real disponible.
- **Datos de prueba:** Argumento `--selftest`.
- **Pasos:**
  1. Acción: Ejecutar `WorkCommander.exe --selftest`. → Esperado: se dibuja un fotograma completo.
  2. Acción: Verificar código de salida. → Esperado: código 0 y consola restaurada.
- **Resultado esperado final:** Selftest OK.

---

## US-002 — Bucle principal y redibujado (RF-02)

### TC-004: Redibujado por cambio de tamaño
- **Origen:** CA-RF02-01
- **Precondiciones:** Aplicación en ejecución.
- **Datos de prueba:** Ventana inicial 80×25.
- **Pasos:**
  1. Acción: Cambiar el tamaño de la ventana de consola. → Esperado: la interfaz se repinta completa sin parpadeo.
- **Resultado esperado final:** Redibujado correcto tras resize.

### TC-005: Reloj en reposo
- **Origen:** CA-RF02-02
- **Precondiciones:** Aplicación en reposo, sin teclas.
- **Datos de prueba:** Espera de 1,5 s.
- **Pasos:**
  1. Acción: No pulsar ninguna tecla durante 1,5 s. → Esperado: la hora de la barra de menú se actualiza.
- **Resultado esperado final:** Reloj actualizado.

### TC-006: Salida limpia
- **Origen:** CA-RF02-03
- **Precondiciones:** Aplicación en ejecución.
- **Datos de prueba:** Tecla F10.
- **Pasos:**
  1. Acción: Pulsar F10. → Esperado: la aplicación termina.
  2. Acción: Inspeccionar la consola. → Esperado: cursor visible, título restaurado, modo de entrada original.
- **Resultado esperado final:** Consola usable tras salir.

---

## US-003 — Navegar paneles, carpetas y archivos (RF-03)

### TC-007: Entrar en carpeta
- **Origen:** CA-RF03-01
- **Precondiciones:** Panel activo con cursor sobre una carpeta.
- **Datos de prueba:** Carpeta `Proyectos`.
- **Pasos:**
  1. Acción: Pulsar Enter sobre la carpeta. → Esperado: el panel muestra su contenido y el cursor queda en la primera entrada.
- **Resultado esperado final:** Navegación a carpeta correcta.

### TC-008: Subir de nivel en raíz de unidad
- **Origen:** CA-RF03-02
- **Precondiciones:** Panel en la raíz de una unidad (ej. `C:\`).
- **Datos de prueba:** Ruta `C:\`.
- **Pasos:**
  1. Acción: Pulsar Retroceso. → Esperado: el panel pasa a vista de unidades y el cursor queda sobre la unidad de origen.
- **Resultado esperado final:** Vuelta a vista de unidades.

### TC-009: Abrir archivo
- **Origen:** CA-RF03-03
- **Precondiciones:** Cursor sobre un archivo listado (no oculto).
- **Datos de prueba:** Archivo `notas.md`.
- **Pasos:**
  1. Acción: Pulsar Enter sobre el archivo. → Esperado: se abre con su aplicación asociada de Windows.
- **Resultado esperado final:** Archivo abierto externamente.

### TC-010: Cambio de panel activo
- **Origen:** CA-RF03-04
- **Precondiciones:** Dos paneles visibles.
- **Datos de prueba:** Tecla Tab.
- **Pasos:**
  1. Acción: Pulsar Tab. → Esperado: el panel activo alterna y su marco se resalta en blanco brillante.
- **Resultado esperado final:** Panel activo cambia.

### TC-011: Carpeta inaccesible al navegar
- **Origen:** CB-11
- **Precondiciones:** Carpeta sin permisos de lectura en el panel.
- **Datos de prueba:** Carpeta protegida.
- **Pasos:**
  1. Acción: Intentar cargar su contenido. → Esperado: flash de error y lista vacía con `..`.
- **Resultado esperado final:** Manejo de error sin bloqueo.

---

## US-004 — Vista de unidades (RF-04)

### TC-012: Listado de unidades existentes
- **Origen:** CA-RF04-01
- **Precondiciones:** Panel en vista de unidades.
- **Datos de prueba:** Unidades `C:\`, `D:\` existentes.
- **Pasos:**
  1. Acción: Dibujar el panel. → Esperado: se muestran solo las unidades existentes en orden alfabético, sin `..`.
- **Resultado esperado final:** Listado correcto.

### TC-013: Sin operaciones en vista de unidades
- **Origen:** CA-RF04-02
- **Precondiciones:** Panel en vista de unidades.
- **Datos de prueba:** Tecla Insert y F5.
- **Pasos:**
  1. Acción: Intentar marcar una entrada. → Esperado: no se marca.
  2. Acción: Intentar ejecutar una operación. → Esperado: no se opera ninguna entrada.
- **Resultado esperado final:** Vista de unidades no operable.

---

## US-005 — Marcar múltiples entradas (RF-05)

### TC-014: Marcar y avanzar
- **Origen:** CA-RF05-01
- **Precondiciones:** Cursor sobre una entrada operable.
- **Datos de prueba:** Entrada `informe.txt`.
- **Pasos:**
  1. Acción: Pulsar Insert. → Esperado: la entrada se marca (amarillo) y el cursor avanza una fila.
- **Resultado esperado final:** Marca aplicada y cursor avanzado.

### TC-015: Selección con marcas
- **Origen:** CA-RF05-02
- **Precondiciones:** Existen entradas marcadas en el panel activo.
- **Datos de prueba:** 2 archivos marcados.
- **Pasos:**
  1. Acción: Ejecutar copiar/mover/borrar. → Esperado: se operan únicamente las entradas marcadas.
- **Resultado esperado final:** Operación sobre marcados.

---

## US-006 — Búsqueda rápida por prefijo (RF-06)

### TC-016: Búsqueda por prefijo
- **Origen:** CA-RF06-01
- **Precondiciones:** Panel con entradas de nombres variados.
- **Datos de prueba:** Texto "no".
- **Pasos:**
  1. Acción: Escribir "no". → Esperado: el cursor se sitúa en la primera entrada cuyo nombre empieza por "no".
- **Resultado esperado final:** Cursor en la primera coincidencia.

### TC-017: Reinicio del buffer
- **Origen:** CA-RF06-02
- **Precondiciones:** El usuario escribió caracteres hace más de 1,2 s.
- **Datos de prueba:** Espera 1,3 s y luego carácter "a".
- **Pasos:**
  1. Acción: Esperar 1,3 s y escribir "a". → Esperado: el buffer se reinicia con "a".
- **Resultado esperado final:** Buffer reiniciado.

---

## US-007 — Ver archivo en el visor (RF-07)

### TC-018: Texto normal
- **Origen:** CA-RF07-01
- **Precondiciones:** Archivo de texto UTF-8 listado.
- **Datos de prueba:** Archivo `notas.md` (UTF-8).
- **Pasos:**
  1. Acción: Pulsar F3. → Esperado: se muestra su contenido en el visor de media pantalla con tamaño, estado de truncado y rango de líneas.
- **Resultado esperado final:** Visor muestra texto.

### TC-019: Archivo binario
- **Origen:** CA-RF07-02
- **Precondiciones:** Archivo con `\x00` que no parece UTF-16.
- **Datos de prueba:** Archivo `datos.bin`.
- **Pasos:**
  1. Acción: Pulsar F3. → Esperado: diálogo con opciones Texto y Hexadecimal; Esc cancela.
- **Resultado esperado final:** Diálogo de modo.

### TC-020: Volcado hexadecimal
- **Origen:** CA-RF07-03
- **Precondiciones:** Usuario eligió Hexadecimal.
- **Datos de prueba:** Archivo binario.
- **Pasos:**
  1. Acción: Elegir Hexadecimal. → Esperado: volcado hex con columna ASCII adaptado al ancho (16/8/4 bytes por fila).
- **Resultado esperado final:** Volcado hex correcto.

### TC-021: Ver archivo por ruta
- **Origen:** CA-RF07-04
- **Precondiciones:** Ruta de archivo oculto o no listado.
- **Datos de prueba:** Ruta `C:\oculto.txt`.
- **Pasos:**
  1. Acción: Usar Archivo > Ver archivo por ruta... y confirmar. → Esperado: se abre ese archivo en el visor si existe.
- **Resultado esperado final:** Archivo abierto por ruta.

### TC-022: Cierre del visor
- **Origen:** CA-RF07-05
- **Precondiciones:** Visor abierto en el panel activo.
- **Datos de prueba:** Tecla Esc.
- **Pasos:**
  1. Acción: Pulsar Esc (o q/Q). → Esperado: el visor se cierra y el panel vuelve a mostrarse.
- **Resultado esperado final:** Visor cerrado.

### TC-023: Archivo mayor a 8 MiB
- **Origen:** CB-09
- **Precondiciones:** Archivo de más de 8 MiB.
- **Datos de prueba:** Archivo `grande.bin` (9 MiB).
- **Pasos:**
  1. Acción: Abrir en el visor. → Esperado: contenido truncado e indicación " (truncado)".
- **Resultado esperado final:** Truncado indicado.

### TC-024: Archivo binario con \x00
- **Origen:** CB-10
- **Precondiciones:** Archivo binario con `\x00`.
- **Datos de prueba:** Archivo `binario.bin`.
- **Pasos:**
  1. Acción: Pulsar F3. → Esperado: se ofrece Texto o Hexadecimal y Esc cancela.
- **Resultado esperado final:** Elección de modo.

---

## US-008 — Editar archivo con Notepad (RF-08)

### TC-025: Editar archivo existente
- **Origen:** CA-RF08-01
- **Precondiciones:** Cursor sobre un archivo (no carpeta ni unidad).
- **Datos de prueba:** Archivo `notas.md`.
- **Pasos:**
  1. Acción: Pulsar F4. → Esperado: se lanza Notepad con ese archivo y la aplicación espera a su cierre.
- **Resultado esperado final:** Notepad lanzado.

### TC-026: Retorno sin recarga automática
- **Origen:** CA-RF08-02
- **Precondiciones:** Notepad cerrado tras editar.
- **Datos de prueba:** Archivo editado.
- **Pasos:**
  1. Acción: Volver a la aplicación. → Esperado: la interfaz se redibuja pero los metadatos no se actualizan hasta F2.
- **Resultado esperado final:** Sin recarga automática.

---

## US-009 — Copiar archivos y carpetas (RF-09)

### TC-027: Copiar archivo a carpeta existente
- **Origen:** CA-RF09-01
- **Precondiciones:** Archivo seleccionado en panel activo; otro panel en carpeta existente.
- **Datos de prueba:** Archivo `a.txt` → carpeta destino.
- **Pasos:**
  1. Acción: Pulsar F5 y confirmar. → Esperado: el archivo aparece en la carpeta destino con metadatos conservados.
- **Resultado esperado final:** Copia exitosa.

### TC-028: Copiar carpeta recursivamente
- **Origen:** CA-RF09-02
- **Precondiciones:** Carpeta seleccionada.
- **Datos de prueba:** Carpeta `Proyectos`.
- **Pasos:**
  1. Acción: Copiar a destino válido. → Esperado: se crean todas las subcarpetas (incluidas vacías) y se copian todos los archivos.
- **Resultado esperado final:** Copia recursiva completa.

### TC-029: Rechazo de copia inválida
- **Origen:** CA-RF09-03
- **Precondiciones:** Intento de copiar carpeta sobre archivo (o archivo sobre carpeta, o carpeta dentro de sí misma).
- **Datos de prueba:** Casos inválidos.
- **Pasos:**
  1. Acción: Validar la operación. → Esperado: mensaje de error correspondiente y no se modifica el disco.
- **Resultado esperado final:** Rechazo sin cambios.

### TC-030: Cancelación de copia
- **Origen:** CA-RF09-04
- **Precondiciones:** Copia en progreso.
- **Datos de prueba:** Tecla Esc.
- **Pasos:**
  1. Acción: Pulsar Esc durante la copia. → Esperado: la copia se detiene, se muestra "Operacion cancelada por el usuario." y no se reporta éxito.
- **Resultado esperado final:** Cancelación correcta.

### TC-031: Sobrescritura única
- **Origen:** CA-RF09-05
- **Precondiciones:** Existen destinos que ya existen.
- **Datos de prueba:** 2 destinos existentes.
- **Pasos:**
  1. Acción: Solicitar confirmación. → Esperado: una única confirmación para todos; si se cancela, no se toca nada.
- **Resultado esperado final:** Confirmación única.

### TC-032: Copiar un archivo a una ruta inexistente
- **Origen:** CB-02
- **Precondiciones:** Archivo seleccionado.
- **Datos de prueba:** Destino `D:\noexiste.txt`.
- **Pasos:**
  1. Acción: Confirmar copia. → Esperado: se crea un archivo con ese nombre.
- **Resultado esperado final:** Archivo creado.

### TC-033: Copiar carpeta sobre archivo
- **Origen:** CB-03
- **Precondiciones:** Destino es un archivo existente.
- **Datos de prueba:** Carpeta origen + archivo destino.
- **Pasos:**
  1. Acción: Validar. → Esperado: rechazo con "El destino existe y no es una carpeta:".
- **Resultado esperado final:** Rechazo.

### TC-034: Copiar archivo sobre carpeta
- **Origen:** CB-04
- **Precondiciones:** Destino es una carpeta existente.
- **Datos de prueba:** Archivo origen + carpeta destino.
- **Pasos:**
  1. Acción: Validar. → Esperado: rechazo con "El destino es una carpeta y el origen es un archivo:".
- **Resultado esperado final:** Rechazo.

### TC-035: Copiar carpeta dentro de sí misma
- **Origen:** CB-05
- **Precondiciones:** Carpeta origen dentro del destino.
- **Datos de prueba:** Carpeta `A` copiada a `A\sub`.
- **Pasos:**
  1. Acción: Validar. → Esperado: rechazo con "No se puede copiar una carpeta dentro de si misma.".
- **Resultado esperado final:** Rechazo.

### TC-036: Origen y destino idénticos
- **Origen:** CB-08
- **Precondiciones:** Origen y destino iguales.
- **Datos de prueba:** Misma ruta.
- **Pasos:**
  1. Acción: Validar. → Esperado: "El origen y el destino son el mismo.".
- **Resultado esperado final:** Rechazo.

---

## US-010 — Mover y renombrar (RF-10)

### TC-037: Renombrar en la misma carpeta
- **Origen:** CA-RF10-01
- **Precondiciones:** Un único archivo seleccionado.
- **Datos de prueba:** Nuevo nombre `nuevo.txt`.
- **Pasos:**
  1. Acción: Pulsar F6 e introducir nombre simple. → Esperado: el archivo se renombra dentro de la misma carpeta.
- **Resultado esperado final:** Renombrado.

### TC-038: Mover a carpeta existente
- **Origen:** CA-RF10-02
- **Precondiciones:** Un único elemento seleccionado.
- **Datos de prueba:** Ruta de carpeta existente.
- **Pasos:**
  1. Acción: Introducir ruta que resulta carpeta existente. → Esperado: el elemento se mueve dentro conservando su nombre.
- **Resultado esperado final:** Movimiento correcto.

### TC-039: Rechazo de mover archivo sobre carpeta
- **Origen:** CA-RF10-03
- **Precondiciones:** Destino ya existe como carpeta.
- **Datos de prueba:** Archivo sobre carpeta.
- **Pasos:**
  1. Acción: Intentar mover. → Esperado: rechazo con "Ya existe una carpeta con ese nombre. No se sobrescribe con un archivo.".
- **Resultado esperado final:** Rechazo.

### TC-040: Movimiento múltiple con destino inválido
- **Origen:** CA-RF10-04
- **Precondiciones:** Varios elementos marcados.
- **Datos de prueba:** Destino no carpeta.
- **Pasos:**
  1. Acción: Introducir destino no carpeta. → Esperado: error y no se mueve nada.
- **Resultado esperado final:** Rechazo.

### TC-041: Mover un archivo sobre una carpeta existente
- **Origen:** CB-06
- **Precondiciones:** Destino existe como carpeta.
- **Datos de prueba:** Archivo sobre carpeta.
- **Pasos:**
  1. Acción: Intentar mover. → Esperado: rechazo con "Ya existe una carpeta con ese nombre. No se sobrescribe con un archivo.".
- **Resultado esperado final:** Rechazo.

### TC-042: Movimiento múltiple a destino no carpeta
- **Origen:** CB-07
- **Precondiciones:** Varios elementos marcados.
- **Datos de prueba:** Destino no carpeta.
- **Pasos:**
  1. Acción: Confirmar. → Esperado: "El destino debe ser una carpeta existente.".
- **Resultado esperado final:** Rechazo.

---

## US-011 — Crear carpetas (RF-11)

### TC-043: Crear carpeta simple
- **Origen:** CA-RF11-01
- **Precondiciones:** Panel activo en carpeta válida.
- **Datos de prueba:** Nombre `NuevaCarpeta`.
- **Pasos:**
  1. Acción: Pulsar F7 e introducir nombre. → Esperado: se crea la carpeta y el cursor queda sobre ella.
- **Resultado esperado final:** Carpeta creada.

### TC-044: Crear carpeta con niveles intermedios
- **Origen:** CA-RF11-02
- **Precondiciones:** Panel activo.
- **Datos de prueba:** Ruta relativa `a\b\c`.
- **Pasos:**
  1. Acción: Introducir ruta con separadores. → Esperado: se crean todos los niveles intermedios.
- **Resultado esperado final:** Niveles creados.

### TC-045: Carpeta ya existente
- **Origen:** CA-RF11-03
- **Precondiciones:** El nombre ya existe.
- **Datos de prueba:** Nombre existente.
- **Pasos:**
  1. Acción: Confirmar. → Esperado: diálogo de error y no se modifica nada.
- **Resultado esperado final:** Error mostrado.

### TC-046: No disponible en vista de unidades
- **Origen:** CA-RF11-04
- **Precondiciones:** Panel en vista de unidades.
- **Datos de prueba:** Tecla F7.
- **Pasos:**
  1. Acción: Pulsar F7. → Esperado: la operación no está disponible / no actúa.
- **Resultado esperado final:** Sin acción.

---

## US-012 — Borrar permanentemente (RF-12)

### TC-047: Borrado con confirmación
- **Origen:** CA-RF12-01
- **Precondiciones:** Selección de archivos/carpetas.
- **Datos de prueba:** 2 elementos.
- **Pasos:**
  1. Acción: Pulsar F8 y confirmar. → Esperado: los elementos se borran permanentemente y se muestra "Borrado: N elemento(s)".
- **Resultado esperado final:** Borrado permanente.

### TC-048: Cancelación de borrado
- **Origen:** CA-RF12-02
- **Precondiciones:** Diálogo de confirmación abierto.
- **Datos de prueba:** Respuesta "no" o Esc.
- **Pasos:**
  1. Acción: Responder no/Esc. → Esperado: no se borra nada.
- **Resultado esperado final:** Sin cambios.

### TC-049: Permiso denegado con reintento
- **Origen:** CA-RF12-03
- **Precondiciones:** Archivo de solo lectura.
- **Datos de prueba:** Archivo read-only.
- **Pasos:**
  1. Acción: Borrar. → Esperado: se intenta chmod +w y se reintenta el borrado.
- **Resultado esperado final:** Reintento ejecutado.

### TC-050: Borrado permanente sin Papelera
- **Origen:** CB-01
- **Precondiciones:** Elemento a borrar.
- **Datos de prueba:** Archivo.
- **Pasos:**
  1. Acción: Confirmar borrado. → Esperado: no se usa la Papelera y no hay deshacer.
- **Resultado esperado final:** Borrado irreversible.

---

## US-013 — Cambiar unidad o ruta (RF-13)

### TC-051: Cambiar a una ruta válida
- **Origen:** CA-RF13-01
- **Precondiciones:** Ruta de directorio existente.
- **Datos de prueba:** Ruta `D:\Backup`.
- **Pasos:**
  1. Acción: Introducir en "Cambiar unidad o ruta...". → Esperado: el panel cambia a esa ruta y el cursor queda en la primera entrada.
- **Resultado esperado final:** Panel cambiado.

### TC-052: Ruta inexistente
- **Origen:** CA-RF13-02
- **Precondiciones:** Ruta que no existe.
- **Datos de prueba:** Ruta `Z:\noexiste`.
- **Pasos:**
  1. Acción: Confirmar. → Esperado: se muestra "La ruta no existe:" con la ruta y no se cambia el panel.
- **Resultado esperado final:** Error y sin cambio.

### TC-053: Atajo de unidad
- **Origen:** CA-RF13-03
- **Precondiciones:** Unidad existente.
- **Datos de prueba:** Texto `D:`.
- **Pasos:**
  1. Acción: Confirmar. → Esperado: se interpreta como `D:\` y se abre si es un directorio.
- **Resultado esperado final:** Apertura de unidad.

---

## US-014 — Ordenar entradas del panel (RF-14)

### TC-054: Ordenar por extensión
- **Origen:** CA-RF14-01
- **Precondiciones:** Panel con archivos de distintas extensiones.
- **Datos de prueba:** Archivos `.txt`, `.md`, `.zip`.
- **Pasos:**
  1. Acción: Elegir "Ordenar por extensión". → Esperado: archivos ordenados por extensión y luego por nombre, con carpetas antes.
- **Resultado esperado final:** Orden por extensión.

### TC-055: Invertir orden
- **Origen:** CA-RF14-02
- **Precondiciones:** Criterio activo.
- **Datos de prueba:** Cualquier criterio.
- **Pasos:**
  1. Acción: Elegir "Invertir orden". → Esperado: el orden de carpetas y archivos se invierte.
- **Resultado esperado final:** Orden invertido.

### TC-056: Orden independiente por panel
- **Origen:** CA-RF14-03
- **Precondiciones:** Dos paneles con criterios distintos.
- **Datos de prueba:** Criterios distintos.
- **Pasos:**
  1. Acción: Ordenar un panel. → Esperado: el otro conserva su criterio y orden.
- **Resultado esperado final:** Orden independiente.

---

## US-015 — Mostrar/ocultar archivos ocultos (RF-15)

### TC-057: Alternar visibilidad
- **Origen:** CA-RF15-01
- **Precondiciones:** Archivos ocultos en el directorio actual.
- **Datos de prueba:** Archivo oculto `secreto.txt`.
- **Pasos:**
  1. Acción: Desactivar "Mostrar archivos ocultos". → Esperado: los ocultos desaparecen de ambos paneles y se muestra el estado "ocultos".
- **Resultado esperado final:** Ocultos no visibles.

### TC-058: Estado inicial visible
- **Origen:** CA-RF15-02
- **Precondiciones:** Aplicación recién iniciada.
- **Datos de prueba:** Directorio con archivos ocultos.
- **Pasos:**
  1. Acción: Mostrar directorio. → Esperado: los archivos ocultos son visibles por defecto.
- **Resultado esperado final:** Ocultos visibles al inicio.

---

## US-016 — Refrescar paneles (RF-16)

### TC-059: Refresco manual
- **Origen:** CA-RF16-01
- **Precondiciones:** Cambios externos en las carpetas mostradas.
- **Datos de prueba:** Crear/borrar archivo externamente.
- **Pasos:**
  1. Acción: Pulsar F2. → Esperado: ambos paneles se recargan y se muestra "Paneles actualizados".
- **Resultado esperado final:** Refresco correcto.

### TC-060: Conservación del cursor
- **Origen:** CA-RF16-02
- **Precondiciones:** Cursor sobre un elemento existente.
- **Datos de prueba:** Elemento `notas.md`.
- **Pasos:**
  1. Acción: Refrescar. → Esperado: el cursor permanece sobre ese elemento si sigue existiendo.
- **Resultado esperado final:** Cursor conservado.

---

## US-017 — Usar el menú superior (RF-17)

### TC-061: Abrir y navegar el menú
- **Origen:** CA-RF17-01
- **Precondiciones:** Aplicación en ejecución.
- **Datos de prueba:** Tecla F9.
- **Pasos:**
  1. Acción: Pulsar F9. → Esperado: se muestra el menú superior y se puede navegar con flechas y cambiar de menú con ←/→.
- **Resultado esperado final:** Menú navegable.

### TC-062: Ejecutar acción
- **Origen:** CA-RF17-02
- **Precondiciones:** Menú abierto con acción seleccionada.
- **Datos de prueba:** Acción "Ver".
- **Pasos:**
  1. Acción: Pulsar Enter. → Esperado: el menú se cierra y se ejecuta la acción correspondiente.
- **Resultado esperado final:** Acción ejecutada.

### TC-063: Cierre con Esc
- **Origen:** CA-RF17-03
- **Precondiciones:** Menú abierto.
- **Datos de prueba:** Tecla Esc.
- **Pasos:**
  1. Acción: Pulsar Esc. → Esperado: el menú se cierra sin ejecutar ninguna acción.
- **Resultado esperado final:** Menú cerrado.

---

## US-018 — Ayuda y Acerca de (RF-18)

### TC-064: Ayuda de teclas
- **Origen:** CA-RF18-01
- **Precondiciones:** Menú Ayuda abierto.
- **Datos de prueba:** Opción "Teclas".
- **Pasos:**
  1. Acción: Seleccionar "Teclas". → Esperado: paginador de pantalla completa con resumen de funciones, navegación y operaciones.
- **Resultado esperado final:** Ayuda mostrada.

### TC-065: Acerca de
- **Origen:** CA-RF18-02
- **Precondiciones:** Menú Ayuda abierto.
- **Datos de prueba:** Opción "Acerca de WorkCommander".
- **Pasos:**
  1. Acción: Seleccionar la opción. → Esperado: diálogo con nombre, versión, descripción y tecnologías.
- **Resultado esperado final:** Diálogo Acerca de.

---

## US-019 — Salir y restaurar la consola (RF-19)

### TC-066: Salida con F10
- **Origen:** CA-RF19-01
- **Precondiciones:** Aplicación en ejecución.
- **Datos de prueba:** Tecla F10.
- **Pasos:**
  1. Acción: Pulsar F10. → Esperado: la aplicación termina y la consola queda usable.
- **Resultado esperado final:** Salida correcta.

### TC-067: Restauración de consola
- **Origen:** CA-RF19-02
- **Precondiciones:** Aplicación terminó normalmente.
- **Datos de prueba:** Inspección visual.
- **Pasos:**
  1. Acción: Inspeccionar la consola. → Esperado: título original restaurado, cursor visible, modo de entrada original.
- **Resultado esperado final:** Consola restaurada.

### TC-068: Proceso matado abruptamente
- **Origen:** CB-15
- **Precondiciones:** Proceso terminado abruptamente.
- **Datos de prueba:** Kill del proceso.
- **Pasos:**
  1. Acción: Matar el proceso. → Esperado: el título puede quedar "WorkCommander".
- **Resultado esperado final:** Comportamiento documentado.

---

## US-020 — Seleccionar con el ratón (RF-21)

### TC-069: Activar panel y seleccionar entrada con clic
- **Origen:** CA-RF21-01
- **Precondiciones:** Dos paneles visibles sin visor.
- **Datos de prueba:** Clic izquierdo en fila del panel derecho.
- **Pasos:**
  1. Acción: Hacer clic izquierdo en una fila del panel derecho. → Esperado: el panel derecho queda activo y el cursor se sitúa en la entrada clicada.
- **Resultado esperado final:** Selección con ratón.

### TC-070: Mouse en menú
- **Origen:** CA-RF21-02
- **Precondiciones:** Menú superior abierto.
- **Datos de prueba:** Movimiento de ratón.
- **Pasos:**
  1. Acción: Mover el ratón. → Esperado: solo se actualiza la posición del cursor de ratón, sin ejecutar acciones.
- **Resultado esperado final:** Sin acción en menú.

---

## US-021 — Aviso de consola demasiado pequeña (RF-22)

### TC-071: Aviso en consola pequeña
- **Origen:** CA-RF22-01
- **Precondiciones:** Ventana de 30×10.
- **Datos de prueba:** Ventana pequeña.
- **Pasos:**
  1. Acción: Dibujar la interfaz. → Esperado: se muestra "Consola demasiado pequeña." y la indicación de tamaño mínimo.
- **Resultado esperado final:** Aviso mostrado.

### TC-072: Consola demasiado pequeña
- **Origen:** CB-12
- **Precondiciones:** Ventana menor a 40×12.
- **Datos de prueba:** Ventana 30×10.
- **Pasos:**
  1. Acción: Intentar usar la aplicación. → Esperado: se muestra el aviso en lugar de la interfaz.
- **Resultado esperado final:** Sin interfaz.

---

### TC-073: Ruta de más de 260 caracteres en copia
- **Origen:** CB-13
- **Precondiciones:** Ruta de más de 260 caracteres.
- **Datos de prueba:** Ruta larga.
- **Pasos:**
  1. Acción: Intentar copiar. → Esperado: la operación puede fallar según la configuración de Windows (no se activa `\\?\`).
- **Resultado esperado final:** Comportamiento documentado.

### TC-074: Enlaces simbólicos y junctions en copia
- **Origen:** CB-14
- **Precondiciones:** Origen es un enlace simbólico o junction.
- **Datos de prueba:** Enlace simbólico.
- **Pasos:**
  1. Acción: Copiar. → Esperado: os.walk no sigue enlaces a directorios y copy2 copia el contenido del archivo enlazado, sin manejo especial de reparse points.
- **Resultado esperado final:** Comportamiento documentado.

### TC-075: Ruta de más de 260 caracteres en movimiento
- **Origen:** CB-13
- **Precondiciones:** Ruta de más de 260 caracteres.
- **Datos de prueba:** Ruta larga.
- **Pasos:**
  1. Acción: Intentar mover. → Esperado: la operación puede fallar según la configuración de Windows (no se activa `\\?\`).
- **Resultado esperado final:** Comportamiento documentado.

### TC-076: Ruta de más de 260 caracteres en cambio de ruta
- **Origen:** CB-13
- **Precondiciones:** Ruta de más de 260 caracteres.
- **Datos de prueba:** Ruta larga.
- **Pasos:**
  1. Acción: Intentar cambiar a esa ruta. → Esperado: la operación puede fallar según la configuración de Windows (no se activa `\\?\`).
- **Resultado esperado final:** Comportamiento documentado.

**Total de casos: 76 (TC-001 a TC-076).**