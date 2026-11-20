# Historia: Búsqueda rápida por prefijo

**Código**: US-006

> **Pedido origen**: PED-001
> **Spec origen**: SPEC-001
> **Requisito origen**: RF-06
> **Prioridad**: Media
> **Estado**: Borrador
> **Autor**: Pablo
> **Fecha**: 2026-11-20
> **Versión**: 0.1

---

## 1. Historia

**Como** Usuario operador
**quiero** escribir caracteres para saltar a la primera entrada cuyo nombre empiece por ese texto
**para** localizar archivos rápidamente sin menús

---

## 2. Reglas de negocio aplicables

| Código | Regla |
|---|---|
| RN-04 | En una carpeta normal, la primera entrada (indice 0) es siempre la entrada especial `..` |
| RN-05 | En la vista de unidades (`panel.path is None`) no hay `..`; solo unidades existentes `A:\`–`Z:\` en orden alfabético |

---

## 3. Criterios de aceptación

**Escenario 1: Búsqueda por prefijo**
Origen: CA-RF06-01
```gherkin
Given un panel con entradas cuyos nombres empiezan por distintas letras
When el usuario escribe "no"
Then el cursor se sitúa en la primera entrada cuyo nombre empieza por "no"
```

**Escenario 2: Reinicio del buffer**
Origen: CA-RF06-02
```gherkin
Given el usuario escribió caracteres hace más de 1,2 segundos
When escribe un nuevo carácter
Then el buffer se reinicia con ese carácter
```

---

## 4. Fuera de alcance de la historia

- La ordenación de entradas (RF-14).

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