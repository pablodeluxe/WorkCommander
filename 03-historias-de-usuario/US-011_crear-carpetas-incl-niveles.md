# Historia: Crear carpetas (incl. niveles)

**Código**: US-011

> **Pedido origen**: PED-001
> **Spec origen**: SPEC-001
> **Requisito origen**: RF-11
> **Prioridad**: Media
> **Estado**: Borrador
> **Autor**: Pablo
> **Fecha**: 2026-11-20
> **Versión**: 0.1

---

## 1. Historia

**Como** Usuario operador
**quiero** crear una carpeta (incluso con niveles intermedios) dentro del panel activo
**para** organizar archivos nuevos

---

## 2. Reglas de negocio aplicables

| Código | Regla |
|---|---|
| RN-05 | En la vista de unidades (`panel.path is None`) no hay `..`; solo unidades existentes `A:\`–`Z:\` en orden alfabético |

---

## 3. Criterios de aceptación

**Escenario 1: Crear carpeta simple**
Origen: CA-RF11-01
```gherkin
Given el panel activo en una carpeta válida
When el usuario pulsa F7 e introduce un nombre
Then se crea la carpeta y el cursor queda sobre ella
```

**Escenario 2: Crear carpeta con niveles intermedios**
Origen: CA-RF11-02
```gherkin
Given el usuario introduce una ruta relativa con separadores
When se confirma
Then se crean todos los niveles intermedios
```

**Escenario 3: Carpeta ya existente**
Origen: CA-RF11-03
```gherkin
Given el nombre introducido ya existe
When se confirma
Then se muestra un diálogo de error y no se modifica nada
```

**Escenario 4: No disponible en vista de unidades**
Origen: CA-RF11-04
```gherkin
Given el panel en vista de unidades
When el usuario pulsa F7
Then la operación no está disponible / no actúa
```

---

## 4. Fuera de alcance de la historia

- El cambio de unidad o ruta (RF-13).

---

## 5. Dependencias

- Permisos de escritura en la carpeta del panel.

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