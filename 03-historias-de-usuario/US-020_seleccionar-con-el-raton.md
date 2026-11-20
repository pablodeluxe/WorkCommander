# Historia: Seleccionar con el ratón

**Código**: US-020

> **Pedido origen**: PED-001
> **Spec origen**: SPEC-001
> **Requisito origen**: RF-21
> **Prioridad**: Media
> **Estado**: Borrador
> **Autor**: Pablo
> **Fecha**: 2026-11-20
> **Versión**: 0.1

---

## 1. Historia

**Como** Usuario operador
**quiero** activar un panel y seleccionar una entrada con un clic izquierdo
**para** usar el ratón como alternativa a las teclas

---

## 2. Reglas de negocio aplicables

No aplica: no hay reglas de negocio específicas vinculadas a este requisito en la spec.

---

## 3. Criterios de aceptación

**Escenario 1: Activar panel y seleccionar entrada con clic**
Origen: CA-RF21-01
```gherkin
Given dos paneles visibles sin visor
When el usuario hace clic izquierdo en una fila del panel derecho
Then el panel derecho queda activo y el cursor se sitúa en la entrada clicada
```

**Escenario 2: Mouse en menú**
Origen: CA-RF21-02
```gherkin
Given el menú superior abierto
When se mueven eventos de ratón
Then solo se actualiza la posición del cursor de ratón, sin ejecutar acciones
```

---

## 4. Fuera de alcance de la historia

- Operaciones completas con ratón (no soportadas; ver PA-02).

---

## 5. Dependencias

- Consola con soporte de entrada de ratón habilitada.

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