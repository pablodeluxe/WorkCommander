# Historia: Copiar archivos y carpetas

**Código**: US-009

> **Pedido origen**: PED-001
> **Spec origen**: SPEC-001
> **Requisito origen**: RF-09
> **Prioridad**: Media
> **Estado**: Borrador
> **Autor**: Pablo
> **Fecha**: 2026-11-20
> **Versión**: 0.1

---

## 1. Historia

**Como** Usuario operador
**quiero** copiar la selección al otro panel (o a una ruta indicada) con validaciones y progreso
**para** duplicar archivos y carpetas conservando metadatos

---

## 2. Reglas de negocio aplicables

| Código | Regla |
|---|---|
| RN-11 | Las operaciones de copiar, mover y borrar usan la selección: si hay marcas, solo las marcadas; si no, la entrada bajo el cursor (salvo `..` o unidad, que dan selección vacía) |
| RN-13 | La confirmación de sobrescritura es única para todo el lote; no hay opciones "sí a todo / no a todo / renombrar" por archivo |
| RN-14 | No se sobrescribe una carpeta con un archivo ni un archivo con una carpeta en copia/movimiento; esos casos se rechazan |
| RN-15 | No se puede copiar una carpeta dentro de sí misma ni de una subcarpeta suya |

---

## 3. Criterios de aceptación

**Escenario 1: Copiar archivo a carpeta existente**
Origen: CA-RF09-01
```gherkin
Given un archivo seleccionado en el panel activo y el otro panel en una carpeta existente
When el usuario pulsa F5 y confirma
Then el archivo aparece en la carpeta destino con sus metadatos conservados
```

**Escenario 2: Copiar carpeta recursivamente**
Origen: CA-RF09-02
```gherkin
Given una carpeta seleccionada
When se copia a un destino válido
Then se crean todas las subcarpetas (incluidas las vacías) y se copian todos los archivos
```

**Escenario 3: Rechazo de copia inválida**
Origen: CA-RF09-03
```gherkin
Given se intenta copiar una carpeta sobre un archivo existente (o un archivo sobre una carpeta, o una carpeta dentro de sí misma)
When se valida la operación
Then se muestra el mensaje de error correspondiente y no se modifica el disco
```

**Escenario 4: Cancelación de copia**
Origen: CA-RF09-04
```gherkin
Given una copia en progreso
When el usuario pulsa Esc
Then la copia se detiene, se muestra "Operacion cancelada por el usuario." y no se reporta éxito
```

**Escenario 5: Sobrescritura única**
Origen: CA-RF09-05
```gherkin
Given existen destinos que ya existen
When se solicita confirmación
Then se pide una única confirmación para todos; si se cancela, no se toca nada
```

**Escenario 6: Copiar un archivo a una ruta inexistente**
Origen: CB-02
```gherkin
Given un archivo seleccionado
When el destino es una ruta inexistente
Then se crea un archivo con ese nombre
```

**Escenario 7: Copiar carpeta sobre archivo**
Origen: CB-03
```gherkin
Given se intenta copiar una carpeta sobre un archivo existente
When se valida
Then se rechaza con "El destino existe y no es una carpeta:"
```

**Escenario 8: Copiar archivo sobre carpeta**
Origen: CB-04
```gherkin
Given se intenta copiar un archivo sobre una carpeta existente
When se valida
Then se rechaza con "El destino es una carpeta y el origen es un archivo:"
```

**Escenario 9: Copiar carpeta dentro de sí misma**
Origen: CB-05
```gherkin
Given se intenta copiar una carpeta dentro de sí misma o de una subcarpeta
When se valida
Then se rechaza con "No se puede copiar una carpeta dentro de si misma."
```

**Escenario 10: Origen y destino idénticos**
Origen: CB-08
```gherkin
Given origen y destino son la misma ruta
When se valida
Then se muestra "El origen y el destino son el mismo."
```

---

## 4. Fuera de alcance de la historia

- El movimiento/renombrado (RF-10) y el borrado (RF-12).

---

## 5. Dependencias

- Permisos de lectura/escritura en origen y destino.

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