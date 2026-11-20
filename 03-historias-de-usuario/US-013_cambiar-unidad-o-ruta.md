# Historia: Cambiar unidad o ruta

**Código**: US-013

> **Pedido origen**: PED-001
> **Spec origen**: SPEC-001
> **Requisito origen**: RF-13
> **Prioridad**: Media
> **Estado**: Borrador
> **Autor**: Pablo
> **Fecha**: 2026-11-20
> **Versión**: 0.1

---

## 1. Historia

**Como** Usuario operador
**quiero** ir a una unidad o ruta escribiéndola
**para** saltar rápidamente a cualquier carpeta

---

## 2. Reglas de negocio aplicables

| Código | Regla |
|---|---|
| RN-05 | En la vista de unidades (`panel.path is None`) no hay `..`; solo unidades existentes `A:\`–`Z:\` en orden alfabético |

---

## 3. Criterios de aceptación

**Escenario 1: Cambiar a una ruta válida**
Origen: CA-RF13-01
```gherkin
Given una ruta de directorio existente
When el usuario la introduce en "Cambiar unidad o ruta..."
Then el panel cambia a esa ruta y el cursor queda en la primera entrada
```

**Escenario 2: Ruta inexistente**
Origen: CA-RF13-02
```gherkin
Given una ruta que no existe
When se confirma
Then se muestra "La ruta no existe:" con la ruta y no se cambia el panel
```

**Escenario 3: Atajo de unidad**
Origen: CA-RF13-03
```gherkin
Given el usuario introduce "D:"
When se confirma
Then se interpreta como "D:\" y se abre si es un directorio
```

**Escenario 4: Ruta de más de 260 caracteres**
Origen: CB-13
```gherkin
Given una ruta de más de 260 caracteres
When se intenta cambiar a ella
Then la operación puede fallar según la configuración de Windows (no se activa `\\?\`)
```

---

## 4. Fuera de alcance de la historia

- La vista de unidades (RF-04).

---

## 5. Dependencias

- Permisos de acceso a la ruta indicada.

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