# Historia: Arrancar WorkCommander y elegir carpeta inicial

**Código**: US-001

> **Pedido origen**: PED-001
> **Spec origen**: SPEC-001
> **Requisito origen**: RF-01
> **Prioridad**: Media
> **Estado**: Borrador
> **Autor**: Pablo
> **Fecha**: 2026-11-20
> **Versión**: 0.1

---

## 1. Historia

**Como** Usuario operador
**quiero** iniciar WorkCommander indicando una carpeta inicial (o usar la actual por defecto) y ejecutar la autoprueba
**para** comenzar a trabajar en el directorio que me interesa y verificar que la consola es usable

---

## 2. Reglas de negocio aplicables

| Código | Regla |
|---|---|
| RN-01 | La aplicación solo funciona en Windows; en otros sistemas aborta con el mensaje `WorkCommander solo funciona en Windows.` |
| RN-02 | Se requiere una consola interactiva con al menos 40 columnas × 12 filas; por debajo se muestra el aviso `Consola demasiado pequeña.` |

---

## 3. Criterios de aceptación

**Escenario 1: Arranque con carpeta inicial por argumento**
Origen: CA-RF01-01
```gherkin
Given una consola interactiva de Windows y una carpeta existente D:\Proyectos
When se ejecuta WorkCommander con el argumento "D:\Proyectos"
Then ambos paneles muestran el contenido de D:\Proyectos y la aplicación queda en ejecución
```

**Escenario 2: Arranque sin argumento válido**
Origen: CA-RF01-02
```gherkin
Given ninguna carpeta válida pasada como argumento
When se inicia la aplicación
Then ambos paneles arrancan en el directorio de trabajo actual (ruta absoluta)
```

**Escenario 3: Autoprueba**
Origen: CA-RF01-03
```gherkin
Given una consola interactiva real
When se ejecuta con --selftest
Then se dibuja un fotograma completo, se restaura la consola y el código de salida es 0
```

---

## 4. Fuera de alcance de la historia

- El renderizado interno y la capa Win32 (RF-20) y las pruebas headless (RF-23) se tratan por separado.
- La persistencia de carpeta inicial entre sesiones no está prevista (fuera de alcance del proyecto).

---

## 5. Dependencias

- Consola interactiva de Windows disponible.
- Carpeta inicial existente y accesible (permisos del usuario).

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