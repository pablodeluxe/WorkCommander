# Historia: Salir y restaurar la consola

**Código**: US-019

> **Pedido origen**: PED-001
> **Spec origen**: SPEC-001
> **Requisito origen**: RF-19
> **Prioridad**: Media
> **Estado**: Borrador
> **Autor**: Pablo
> **Fecha**: 2026-11-20
> **Versión**: 0.1

---

## 1. Historia

**Como** Usuario operador
**quiero** salir de la aplicación y que la consola quede usable
**para** continuar trabajando en la terminal tras usar WorkCommander

---

## 2. Reglas de negocio aplicables

| Código | Regla |
|---|---|
| RN-01 | La aplicación solo funciona en Windows; en otros sistemas aborta con el mensaje `WorkCommander solo funciona en Windows.` |

---

## 3. Criterios de aceptación

**Escenario 1: Salida con F10**
Origen: CA-RF19-01
```gherkin
Given la aplicación en ejecución
When el usuario pulsa F10
Then la aplicación termina y la consola queda usable
```

**Escenario 2: Restauración de consola**
Origen: CA-RF19-02
```gherkin
Given la aplicación terminó normalmente
When se inspecciona la consola
Then el título original se restauró, el cursor es visible y el modo de entrada es el original
```

**Escenario 3: Proceso matado abruptamente**
Origen: CB-15
```gherkin
Given el proceso se mata abruptamente
When no se ejecuta cleanup
Then el título puede quedar "WorkCommander"
```

---

## 4. Fuera de alcance de la historia

- El bucle principal (RF-02).

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