# Historia: Usar el menú superior

**Código**: US-017

> **Pedido origen**: PED-001
> **Spec origen**: SPEC-001
> **Requisito origen**: RF-17
> **Prioridad**: Media
> **Estado**: Borrador
> **Autor**: Pablo
> **Fecha**: 2026-11-20
> **Versión**: 0.1

---

## 1. Historia

**Como** Usuario operador
**quiero** abrir y navegar el menú superior para ejecutar acciones
**para** acceder a todas las funciones sin memorizar todas las teclas

---

## 2. Reglas de negocio aplicables

No aplica: no hay reglas de negocio específicas vinculadas a este requisito en la spec.

---

## 3. Criterios de aceptación

**Escenario 1: Abrir y navegar el menú**
Origen: CA-RF17-01
```gherkin
Given la aplicación en ejecución
When el usuario pulsa F9
Then se muestra el menú superior y se puede navegar con flechas y cambiar de menú con ←/→
```

**Escenario 2: Ejecutar acción**
Origen: CA-RF17-02
```gherkin
Given un menú abierto con una acción seleccionada
When el usuario pulsa Enter
Then el menú se cierra y se ejecuta la acción correspondiente
```

**Escenario 3: Cierre con Esc**
Origen: CA-RF17-03
```gherkin
Given un menú abierto
When el usuario pulsa Esc
Then el menú se cierra sin ejecutar ninguna acción
```

---

## 4. Fuera de alcance de la historia

- Las acciones individuales ya cubiertas por otras historias (RF-03…RF-16, RF-18…).

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