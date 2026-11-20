# Historia: Ayuda y Acerca de

**Código**: US-018

> **Pedido origen**: PED-001
> **Spec origen**: SPEC-001
> **Requisito origen**: RF-18
> **Prioridad**: Media
> **Estado**: Borrador
> **Autor**: Pablo
> **Fecha**: 2026-11-20
> **Versión**: 0.1

---

## 1. Historia

**Como** Usuario operador
**quiero** consultar la ayuda de teclas y la información de versión
**para** aprender a usar la aplicación y conocer su versión

---

## 2. Reglas de negocio aplicables

No aplica: no hay reglas de negocio específicas vinculadas a este requisito en la spec.

---

## 3. Criterios de aceptación

**Escenario 1: Ayuda de teclas**
Origen: CA-RF18-01
```gherkin
Given el menú Ayuda abierto
When se selecciona "Teclas"
Then se muestra un paginador de pantalla completa con el resumen de funciones, navegación y operaciones
```

**Escenario 2: Acerca de**
Origen: CA-RF18-02
```gherkin
Given el menú Ayuda abierto
When se selecciona "Acerca de WorkCommander"
Then se muestra un diálogo con nombre, versión, descripción y tecnologías
```

---

## 4. Fuera de alcance de la historia

- La ayuda detallada del README (documentación externa).

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