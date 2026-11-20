# Historia: Navegar paneles, carpetas y archivos

**Código**: US-003

> **Pedido origen**: PED-001
> **Spec origen**: SPEC-001
> **Requisito origen**: RF-03
> **Prioridad**: Media
> **Estado**: Borrador
> **Autor**: Pablo
> **Fecha**: 2026-11-20
> **Versión**: 0.1

---

## 1. Historia

**Como** Usuario operador
**quiero** moverme entre paneles y entradas, entrar en carpetas, subir niveles y abrir archivos con Enter
**para** recorrer el sistema de archivos sin usar el ratón

---

## 2. Reglas de negocio aplicables

| Código | Regla |
|---|---|
| RN-04 | En una carpeta normal, la primera entrada (indice 0) es siempre la entrada especial `..` |
| RN-05 | En la vista de unidades (`panel.path is None`) no hay `..`; solo unidades existentes `A:\`–`Z:\` en orden alfabético |
| RN-06 | Las entradas `..` y las unidades no son seleccionables para operaciones ni marcables |
| RN-09 | Al pulsar Enter sobre un archivo se ejecuta/abre con su aplicación asociada (`os.startfile`), sin confirmación previa |

---

## 3. Criterios de aceptación

**Escenario 1: Entrar en carpeta**
Origen: CA-RF03-01
```gherkin
Given el cursor sobre una carpeta en el panel activo
When el usuario pulsa Enter
Then el panel muestra el contenido de esa carpeta y el cursor queda en la primera entrada
```

**Escenario 2: Subir de nivel en raíz de unidad**
Origen: CA-RF03-02
```gherkin
Given el panel está en la raíz de una unidad (por ejemplo C:\)
When el usuario pulsa Retroceso
Then el panel pasa a la vista de unidades y el cursor queda sobre la unidad de origen
```

**Escenario 3: Abrir archivo**
Origen: CA-RF03-03
```gherkin
Given el cursor sobre un archivo no oculto listado
When el usuario pulsa Enter
Then el archivo se abre con su aplicación asociada de Windows
```

**Escenario 4: Cambio de panel activo**
Origen: CA-RF03-04
```gherkin
Given dos paneles visibles
When el usuario pulsa Tab
Then el panel activo alterna y su marco se resalta en blanco brillante
```

**Escenario 5: Carpeta inaccesible al navegar**
Origen: CB-11
```gherkin
Given una carpeta sin permisos de lectura
When se intenta cargar su contenido
Then se muestra un flash de error y la lista queda vacía con ".."
```

---

## 4. Fuera de alcance de la historia

- La vista de unidades como modo independiente (RF-04).
- El marcado múltiple (RF-05) y la búsqueda rápida (RF-06).

---

## 5. Dependencias

- Permisos de lectura sobre las carpetas navegadas.

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