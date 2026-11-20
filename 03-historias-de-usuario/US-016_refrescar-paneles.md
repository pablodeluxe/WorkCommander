# Historia: Refrescar paneles

**Código**: US-016

> **Pedido origen**: PED-001
> **Spec origen**: SPEC-001
> **Requisito origen**: RF-16
> **Prioridad**: Media
> **Estado**: Borrador
> **Autor**: Pablo
> **Fecha**: 2026-11-20
> **Versión**: 0.1

---

## 1. Historia

**Como** Usuario operador
**quiero** refrescar ambos paneles tras cambios externos
**para** ver el estado actualizado del sistema de archivos

---

## 2. Reglas de negocio aplicables

| Código | Regla |
|---|---|
| RN-12 | Las marcas se guardan por nombre y se conservan tras recargar el panel, intersectando con los nombres existentes |

---

## 3. Criterios de aceptación

**Escenario 1: Refresco manual**
Origen: CA-RF16-01
```gherkin
Given cambios externos en las carpetas mostradas
When el usuario pulsa F2
Then ambos paneles se recargan y se muestra "Paneles actualizados"
```

**Escenario 2: Conservación del cursor**
Origen: CA-RF16-02
```gherkin
Given el cursor sobre un elemento existente
When se refresca
Then el cursor permanece sobre ese elemento si sigue existiendo
```

---

## 4. Fuera de alcance de la historia

- La edición con Notepad (RF-08), que no recarga automáticamente.

---

## 5. Dependencias

- Ninguna.

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