# Historia: Vista de unidades (A: a Z:)

**Código**: US-004

> **Pedido origen**: PED-001
> **Spec origen**: SPEC-001
> **Requisito origen**: RF-04
> **Prioridad**: Media
> **Estado**: Borrador
> **Autor**: Pablo
> **Fecha**: 2026-11-20
> **Versión**: 0.1

---

## 1. Historia

**Como** Usuario operador
**quiero** ver la lista de unidades existentes y no operar sobre ellas
**para** elegir desde qué unidad empezar a navegar

---

## 2. Reglas de negocio aplicables

| Código | Regla |
|---|---|
| RN-05 | En la vista de unidades (`panel.path is None`) no hay `..`; solo unidades existentes `A:\`–`Z:\` en orden alfabético |
| RN-06 | Las entradas `..` y las unidades no son seleccionables para operaciones ni marcables |

---

## 3. Criterios de aceptación

**Escenario 1: Listado de unidades existentes**
Origen: CA-RF04-01
```gherkin
Given el panel en vista de unidades
When se dibuja el panel
Then se muestran solo las unidades existentes (A:\ a Z:\) en orden alfabético, sin ".."
```

**Escenario 2: Sin operaciones en vista de unidades**
Origen: CA-RF04-02
```gherkin
Given el panel en vista de unidades
When el usuario intenta marcar o ejecutar una operación de archivo
Then no se marca ni se opera ninguna entrada
```

**Escenario 3: Carpeta inaccesible al recargar**
Origen: CB-11
```gherkin
Given una carpeta sin permisos de lectura
When se intenta cargar su contenido
Then se muestra un flash de error y la lista queda vacía con ".."
```

---

## 4. Fuera de alcance de la historia

- La navegación general entre carpetas (RF-03).

---

## 5. Dependencias

- Acceso al sistema de archivos para comprobar existencia de unidades.

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