# Historia: Editar archivo con Notepad

**Código**: US-008

> **Pedido origen**: PED-001
> **Spec origen**: SPEC-001
> **Requisito origen**: RF-08
> **Prioridad**: Media
> **Estado**: Borrador
> **Autor**: Pablo
> **Fecha**: 2026-11-20
> **Versión**: 0.1

---

## 1. Historia

**Como** Usuario operador
**quiero** abrir el archivo seleccionado en Notepad y volver a la aplicación al cerrarlo
**para** editarlo con un editor externo sin perder el contexto

---

## 2. Reglas de negocio aplicables

| Código | Regla |
|---|---|
| RN-09 | Al pulsar Enter sobre un archivo se ejecuta/abre con su aplicación asociada (`os.startfile`), sin confirmación previa |

---

## 3. Criterios de aceptación

**Escenario 1: Editar archivo existente**
Origen: CA-RF08-01
```gherkin
Given el cursor sobre un archivo (no carpeta ni unidad)
When el usuario pulsa F4
Then se lanza Notepad con ese archivo y la aplicación espera a su cierre
```

**Escenario 2: Retorno sin recarga automática**
Origen: CA-RF08-02
```gherkin
Given se cerró Notepad tras editar
When la aplicación vuelve al panel
Then la interfaz se redibuja pero los metadatos del archivo no se actualizan hasta F2
```

---

## 4. Fuera de alcance de la historia

- La recarga manual de paneles (RF-16).

---

## 5. Dependencias

- Notepad disponible en el sistema.

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