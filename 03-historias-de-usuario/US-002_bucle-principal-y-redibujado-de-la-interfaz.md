# Historia: Bucle principal y redibujado de la interfaz

**Código**: US-002

> **Pedido origen**: PED-001
> **Spec origen**: SPEC-001
> **Requisito origen**: RF-02
> **Prioridad**: Media
> **Estado**: Borrador
> **Autor**: Pablo
> **Fecha**: 2026-11-20
> **Versión**: 0.1

---

## 1. Historia

**Como** Usuario operador
**quiero** que la interfaz se redibuje automáticamente ante cambios de tamaño, en reposo para el reloj y al salir de forma limpia
**para** tener siempre una vista actualizada y recuperar la consola al terminar

---

## 2. Reglas de negocio aplicables

| Código | Regla |
|---|---|
| RN-19 | Las operaciones son síncronas en el hilo de la interfaz; copiar, mover y borrar congelan la UI hasta terminar |

---

## 3. Criterios de aceptación

**Escenario 1: Redibujado por cambio de tamaño**
Origen: CA-RF02-01
```gherkin
Given la aplicación en ejecución
When cambia el tamaño de la consola
Then se limpia el búfer, se recrea la rejilla y se repinta la interfaz completa
```

**Escenario 2: Reloj en reposo**
Origen: CA-RF02-02
```gherkin
Given la aplicación en reposo sin teclas
When transcurre 1 segundo
Then se redibuja la interfaz actualizando la hora en la barra de menú
```

**Escenario 3: Salida limpia**
Origen: CA-RF02-03
```gherkin
Given la aplicación en ejecución
When el usuario pulsa F10 o Ctrl+C
Then running pasa a False y cleanup() restaura pantalla, cursor, modo de entrada y título
```

---

## 4. Fuera de alcance de la historia

- La capa Win32 de renderizado (RF-20) y las pruebas (RF-23) se tratan por separado.

---

## 5. Dependencias

- Consola interactiva de Windows.

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