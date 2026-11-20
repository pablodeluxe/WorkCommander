# Historia: Ver archivo en el visor

**Código**: US-007

> **Pedido origen**: PED-001
> **Spec origen**: SPEC-001
> **Requisito origen**: RF-07
> **Prioridad**: Media
> **Estado**: Borrador
> **Autor**: Pablo
> **Fecha**: 2026-11-20
> **Versión**: 0.1

---

## 1. Historia

**Como** Usuario operador
**quiero** abrir y leer cualquier archivo (texto o hexadecimal) en un visor de media pantalla
**para** inspeccionar su contenido sin salir de la aplicación

---

## 2. Reglas de negocio aplicables

| Código | Regla |
|---|---|
| RN-10 | El visor interno es de solo lectura y lee como máximo 8 MiB (+1 byte para detectar truncado) |
| RN-16 | F3 nunca rechaza un archivo: los binarios ofrecen elegir texto o hexadecimal; los archivos ocultos se pueden abrir por ruta |

---

## 3. Criterios de aceptación

**Escenario 1: Texto normal**
Origen: CA-RF07-01
```gherkin
Given un archivo de texto UTF-8 listado
When el usuario pulsa F3
Then se muestra su contenido en el visor de media pantalla con tamaño, estado de truncado y rango de líneas
```

**Escenario 2: Archivo binario**
Origen: CA-RF07-02
```gherkin
Given un archivo que contiene \x00 y no parece UTF-16
When el usuario pulsa F3
Then se muestra un diálogo con opciones Texto y Hexadecimal y Esc cancela
```

**Escenario 3: Volcado hexadecimal**
Origen: CA-RF07-03
```gherkin
Given el usuario elige Hexadecimal
When se abre el visor
Then se muestra un volcado hex con columna ASCII adaptado al ancho (16/8/4 bytes por fila)
```

**Escenario 4: Ver archivo por ruta**
Origen: CA-RF07-04
```gherkin
Given una ruta de archivo oculto o no listado
When se usa Archivo > Ver archivo por ruta... y se confirma
Then se abre ese archivo en el visor si existe
```

**Escenario 5: Cierre del visor**
Origen: CA-RF07-05
```gherkin
Given un visor abierto en el panel activo
When el usuario pulsa Esc o q o Q
Then el visor se cierra y el panel vuelve a mostrarse
```

**Escenario 6: Archivo mayor a 8 MiB**
Origen: CB-09
```gherkin
Given un archivo de más de 8 MiB
When se abre en el visor
Then el contenido se trunca y se indica " (truncado)"
```

**Escenario 7: Archivo binario con \x00**
Origen: CB-10
```gherkin
Given un archivo binario con \x00
When se pulsa F3
Then se ofrece Texto o Hexadecimal y Esc cancela
```

---

## 4. Fuera de alcance de la historia

- La edición de archivos (RF-08) y el paginador de ayuda (RF-18).

---

## 5. Dependencias

- Permisos de lectura sobre el archivo.

---

## 6. Definición de "listo" (Definition of Ready)

Lo que tiene que cumplirse para que desarrollo pueda tomar la historia:

- [ ] La spec origen está aprobada
- [ ] No hay preguntas abiertas en la spec que afecten a esta historia
- [ ] Cada escenario tiene su origen (CA o CB) y se puede probar
- [ ] Las dependencias están resueltas o tienen fecha comprometida
- [ ] La historia se puede desarrollar y probar sola
- [ ] No aplica: no se definieron criterios adicionales

---

## 7. Definición de "hecho" (Definition of Done)

Lo que tiene que cumplirse para dar el desarrollo por terminado:

- [ ] Todos los escenarios de aceptación pasan
- [ ] Los criterios de la spec citados como origen están verificados por QA
- [ ] Las reglas de negocio aplicables se cumplen, incluido el escenario que falla cuando se incumplen
- [ ] No se agregó comportamiento fuera del alcance de la historia
- [ ] No aplica: no se definieron criterios adicionales

---

## Historial de cambios

| Versión | Fecha | Cambio | Autor |
|---|---|---|---|
| 0.1 | 2026-11-20 | Versión inicial | Pablo |