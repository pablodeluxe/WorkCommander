# Historia: Borrar permanentemente

**Código**: US-012

> **Pedido origen**: PED-001
> **Spec origen**: SPEC-001
> **Requisito origen**: RF-12
> **Prioridad**: Media
> **Estado**: Borrador
> **Autor**: Pablo
> **Fecha**: 2026-11-20
> **Versión**: 0.1

---

## 1. Historia

**Como** Usuario operador
**quiero** borrar la selección de forma permanente tras confirmación
**para** liberar espacio sin usar la Papelera

---

## 2. Reglas de negocio aplicables

| Código | Regla |
|---|---|
| RN-08 | El borrado es permanente: no se usa la Papelera de Reciclaje y no hay deshacer |
| RN-11 | Las operaciones de copiar, mover y borrar usan la selección: si hay marcas, solo las marcadas; si no, la entrada bajo el cursor (salvo `..` o unidad, que dan selección vacía) |

---

## 3. Criterios de aceptación

**Escenario 1: Borrado con confirmación**
Origen: CA-RF12-01
```gherkin
Given una selección de archivos/carpetas
When el usuario pulsa F8 y confirma
Then los elementos se borran permanentemente y se muestra "Borrado: N elemento(s)"
```

**Escenario 2: Cancelación de borrado**
Origen: CA-RF12-02
```gherkin
Given el diálogo de confirmación
When el usuario responde no o Esc
Then no se borra nada
```

**Escenario 3: Permiso denegado con reintento**
Origen: CA-RF12-03
```gherkin
Given un archivo de solo lectura
When se borra
Then se intenta chmod +w y se reintenta el borrado
```

**Escenario 4: Borrado permanente sin Papelera**
Origen: CB-01
```gherkin
Given se borra un elemento
When se confirma
Then no se usa la Papelera de Reciclaje y no hay deshacer
```

---

## 4. Fuera de alcance de la historia

- La copia (RF-09) y el movimiento (RF-10).

---

## 5. Dependencias

- Permisos de borrado sobre los elementos.

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