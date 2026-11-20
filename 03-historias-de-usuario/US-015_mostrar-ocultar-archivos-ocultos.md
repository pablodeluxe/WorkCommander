# Historia: Mostrar/ocultar archivos ocultos

**Código**: US-015

> **Pedido origen**: PED-001
> **Spec origen**: SPEC-001
> **Requisito origen**: RF-15
> **Prioridad**: Media
> **Estado**: Borrador
> **Autor**: Pablo
> **Fecha**: 2026-11-20
> **Versión**: 0.1

---

## 1. Historia

**Como** Usuario operador
**quiero** alternar la visibilidad de archivos ocultos en ambos paneles
**para** ver o esconder archivos ocultos según necesite

---

## 2. Reglas de negocio aplicables

| Código | Regla |
|---|---|
| RN-03 | `show_hidden` (mostrar archivos ocultos) comienza en `True`; los ocultos se ven por defecto |
| RN-17 | Se considera oculto lo que tenga el atributo Win32 `FILE_ATTRIBUTE_HIDDEN` (`0x2`), incluidos directorios |

---

## 3. Criterios de aceptación

**Escenario 1: Alternar visibilidad**
Origen: CA-RF15-01
```gherkin
Given archivos ocultos en el directorio actual
When el usuario desactiva "Mostrar archivos ocultos"
Then los ocultos desaparecen de ambos paneles y se muestra el estado "ocultos"
```

**Escenario 2: Estado inicial visible**
Origen: CA-RF15-02
```gherkin
Given la aplicación recién iniciada
When se muestra un directorio con archivos ocultos
Then los archivos ocultos son visibles por defecto
```

---

## 4. Fuera de alcance de la historia

- La apertura de archivos ocultos por ruta (RF-07).

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