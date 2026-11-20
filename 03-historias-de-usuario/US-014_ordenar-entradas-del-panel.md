# Historia: Ordenar entradas del panel

**Código**: US-014

> **Pedido origen**: PED-001
> **Spec origen**: SPEC-001
> **Requisito origen**: RF-14
> **Prioridad**: Media
> **Estado**: Borrador
> **Autor**: Pablo
> **Fecha**: 2026-11-20
> **Versión**: 0.1

---

## 1. Historia

**Como** Usuario operador
**quiero** ordenar el panel por nombre, extensión, fecha o tamaño e invertir el orden
**para** encontrar archivos más rápido

---

## 2. Reglas de negocio aplicables

| Código | Regla |
|---|---|
| RN-07 | Las carpetas se ordenan siempre por nombre y van antes que los archivos |

---

## 3. Criterios de aceptación

**Escenario 1: Ordenar por extensión**
Origen: CA-RF14-01
```gherkin
Given un panel con archivos de distintas extensiones
When se elige "Ordenar por extensión"
Then los archivos se ordenan por extensión y luego por nombre, con carpetas antes
```

**Escenario 2: Invertir orden**
Origen: CA-RF14-02
```gherkin
Given un criterio activo
When se elige "Invertir orden"
Then el orden de carpetas y archivos se invierte
```

**Escenario 3: Orden independiente por panel**
Origen: CA-RF14-03
```gherkin
Given dos paneles con criterios distintos
When se ordena un panel
Then el otro conserva su criterio y orden
```

---

## 4. Fuera de alcance de la historia

- El refresco de paneles (RF-16).

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