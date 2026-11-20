# Historia: Aviso de consola demasiado pequeña

**Código**: US-021

> **Pedido origen**: PED-001
> **Spec origen**: SPEC-001
> **Requisito origen**: RF-22
> **Prioridad**: Media
> **Estado**: Borrador
> **Autor**: Pablo
> **Fecha**: 2026-11-20
> **Versión**: 0.1

---

## 1. Historia

**Como** Usuario operador
**quiero** recibir un aviso cuando la ventana sea menor a 40×12
**para** saber que debo agrandarla para usar la aplicación

---

## 2. Reglas de negocio aplicables

| Código | Regla |
|---|---|
| RN-02 | Se requiere una consola interactiva con al menos 40 columnas × 12 filas; por debajo se muestra el aviso `Consola demasiado pequeña.` |

---

## 3. Criterios de aceptación

**Escenario 1: Aviso en consola pequeña**
Origen: CA-RF22-01
```gherkin
Given una ventana de 30×10
When se dibuja la interfaz
Then se muestra "Consola demasiado pequeña." y la indicación de tamaño mínimo
```

**Escenario 2: Consola demasiado pequeña**
Origen: CB-12
```gherkin
Given una ventana menor a 40×12
When se intenta usar la aplicación
Then se muestra el aviso en lugar de la interfaz
```

---

## 4. Fuera de alcance de la historia

- El renderizado completo (RF-20).

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