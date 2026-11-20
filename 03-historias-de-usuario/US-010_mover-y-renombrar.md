# Historia: Mover y renombrar

**Código**: US-010

> **Pedido origen**: PED-001
> **Spec origen**: SPEC-001
> **Requisito origen**: RF-10
> **Prioridad**: Media
> **Estado**: Borrador
> **Autor**: Pablo
> **Fecha**: 2026-11-20
> **Versión**: 0.1

---

## 1. Historia

**Como** Usuario operador
**quiero** mover o renombrar la selección (uno o varios elementos) con las reglas de destino
**para** reorganizar archivos y carpetas

---

## 2. Reglas de negocio aplicables

| Código | Regla |
|---|---|
| RN-11 | Las operaciones de copiar, mover y borrar usan la selección: si hay marcas, solo las marcadas; si no, la entrada bajo el cursor (salvo `..` o unidad, que dan selección vacía) |
| RN-13 | La confirmación de sobrescritura es única para todo el lote; no hay opciones "sí a todo / no a todo / renombrar" por archivo |
| RN-14 | No se sobrescribe una carpeta con un archivo ni un archivo con una carpeta en copia/movimiento; esos casos se rechazan |

---

## 3. Criterios de aceptación

**Escenario 1: Renombrar en la misma carpeta**
Origen: CA-RF10-01
```gherkin
Given un único archivo seleccionado
When el usuario pulsa F6 e introduce un nombre simple sin separadores
Then el archivo se renombra dentro de la misma carpeta
```

**Escenario 2: Mover a carpeta existente**
Origen: CA-RF10-02
```gherkin
Given un único elemento seleccionado
When el usuario introduce una ruta que resulta una carpeta existente
Then el elemento se mueve dentro de esa carpeta conservando su nombre
```

**Escenario 3: Rechazo de mover archivo sobre carpeta**
Origen: CA-RF10-03
```gherkin
Given el destino ya existe como carpeta
When se intenta mover un archivo sobre ella
Then se rechaza con "Ya existe una carpeta con ese nombre. No se sobrescribe con un archivo."
```

**Escenario 4: Movimiento múltiple con destino inválido**
Origen: CA-RF10-04
```gherkin
Given varios elementos marcados
When el destino no es una carpeta existente
Then se muestra error y no se mueve nada
```

**Escenario 5: Mover un archivo sobre una carpeta existente**
Origen: CB-06
```gherkin
Given el destino ya existe como carpeta
When se intenta mover un archivo sobre ella
Then se rechaza con "Ya existe una carpeta con ese nombre. No se sobrescribe con un archivo."
```

**Escenario 6: Movimiento múltiple a destino no carpeta**
Origen: CB-07
```gherkin
Given varios elementos marcados
When el destino no es una carpeta existente
Then se muestra "El destino debe ser una carpeta existente."
```

**Escenario 7: Ruta de más de 260 caracteres**
Origen: CB-13
```gherkin
Given una ruta de más de 260 caracteres
When se intenta mover
Then la operación puede fallar según la configuración de Windows (no se activa `\\?\`)
```

---

## 4. Fuera de alcance de la historia

- La copia (RF-09) y el borrado (RF-12).

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