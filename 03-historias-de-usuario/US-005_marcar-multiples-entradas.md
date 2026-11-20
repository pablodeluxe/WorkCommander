# Historia: Marcar múltiples entradas

**Código**: US-005

> **Pedido origen**: PED-001
> **Spec origen**: SPEC-001
> **Requisito origen**: RF-05
> **Prioridad**: Media
> **Estado**: Borrador
> **Autor**: Pablo
> **Fecha**: 2026-11-20
> **Versión**: 0.1

---

## 1. Historia

**Como** Usuario operador
**quiero** marcar y desmarcar entradas con Insert para operarlas en lote
**para** copiar, mover o borrar varios archivos a la vez

---

## 2. Reglas de negocio aplicables

| Código | Regla |
|---|---|
| RN-06 | Las entradas `..` y las unidades no son seleccionables para operaciones ni marcables |
| RN-11 | Las operaciones de copiar, mover y borrar usan la selección: si hay marcas, solo las marcadas; si no, la entrada bajo el cursor (salvo `..` o unidad, que dan selección vacía) |
| RN-12 | Las marcas se guardan por nombre y se conservan tras recargar el panel, intersectando con los nombres existentes |

---

## 3. Criterios de aceptación

**Escenario 1: Marcar y avanzar**
Origen: CA-RF05-01
```gherkin
Given el cursor sobre una entrada operable
When el usuario pulsa Insert
Then la entrada se marca (amarillo) y el cursor avanza una fila
```

**Escenario 2: Selección con marcas**
Origen: CA-RF05-02
```gherkin
Given existen entradas marcadas en el panel activo
When se ejecuta una operación de copiar/mover/borrar
Then se operan únicamente las entradas marcadas
```

---

## 4. Fuera de alcance de la historia

- La ejecución de las operaciones sobre la selección (RF-09, RF-10, RF-12).

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