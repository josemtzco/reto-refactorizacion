# Bitácora de refactorización

**Nombre:** Jose Juan Martinez Morales

**Matrícula:** 
**Fecha:** Octubre 05, 2026

Registra aquí **cada refactorización** que realices con Claude Code. Copia el
prompt tal cual lo escribiste (o un resumen fiel si fue una conversación larga),
describe el cambio que se aplicó al código y justifica por qué mejora la calidad.
Después de cada cambio ejecuta `pytest` y anota el resultado.

| #  | Prompt usado | Cambio realizado | Justificación | Tests OK |
|----|--------------|------------------|---------------|----------|
| 1  | Aplica la fase R1 de la auditoría: quitar las cabeceras `# -*- coding: utf-8 -*-` de los 4 archivos de `src/` | Se borró la primera línea de `gestor.py`, `almacen.py`, `reportes.py` y `main.py` (`ruff --fix --select UP009`). | Quita una línea que sobra en Python 3 (#18). Categoría: eliminar código muerto o comentarios obsoletos. | ✅ 20 passed · ruff: 16 errores (antes 20) · referencia idéntica |
| 2  | Aplica la fase R2 de la auditoría: ordenar los imports de `main.py` (almacen, gestor, reportes) | `main.py`: `import almacen` ahora va antes de `import gestor` (`ruff --fix --select I001`). | Imports en orden alfabético, como pide PEP 8 (#19). Categoría: renombrar/ordenar para legibilidad (cambio mecánico, sin lógica). | ✅ 20 passed · ruff: 15 errores (antes 16) · referencia idéntica |
| 3  | Aplica la fase R3 de la auditoría: eliminar código muerto (`calcular_descuento_viejo`, `exportar_txt` comentado, `reporteViejoCSV`, `MODO_DEBUG`) | `gestor.py`: se borraron `calcular_descuento_viejo`, el bloque comentado `exportar_txt` y `MODO_DEBUG`. `reportes.py`: se borró `reporteViejoCSV` y `import os`, que quedó sin uso. Se comprobó que nada en `src/` ni `tests/` los usa. | Menos código que mantener y menos avisos de ruff (#13, #22). `import os` es código muerto extra no listado en la auditoría. Categoría: eliminar código muerto o comentarios obsoletos. | ✅ 20 passed · ruff: 12 errores (antes 15) · referencia idéntica |
| 4 | Aplica la fase R4 de la auditoría: nombres descriptivos en pedir_numero y alertas | main.py:pedir_numero: temp2 pasa a respuesta, comentario inicial a docstring y hints (mensaje: str -> float). main.py:menu: len(bajos) == 0 pasa a not bajos. | Nombre que dice lo que guarda y condición más simple (#23). Categoría: renombrar variables o funciones. | ✅ 20 passed · ruff: 12 errores (antes 12) · referencia idéntica |
| 5 | Aplica la fase R5 de la auditoría: nombre descriptivo en actualizar_stock | gestor.py:actualizar_stock: aux pasa a nuevo_stock y se agregan hints (codigo: str, cantidad: int, -> bool). Mensajes y orden de validación igual. | El nombre dice qué guarda la variable (#16). Categoría: renombrar variables o funciones. | ✅ 20 passed · ruff: 12 errores (antes 12) · referencia idéntica |
| 6 | Aplica la fase R6 de la auditoría: constantes para IVA, descuentos y VIP | gestor.py: 8 constantes nuevas arriba del archivo (umbrales y tasas de descuento, TASA_IVA, PREFIJO_VIP, MONTO_MINIMO_VIP, TASA_EXTRA_VIP) y se usan en registrar_venta y cotizar. Solo se cambian los números; la estructura de los if y las fórmulas quedan igual. | Los números mágicos ahora tienen nombre y un solo lugar para cambiarlos (#2). Categoría: renombrar variables o funciones (constantes con nombre). | ✅ 20 passed · ruff: 12 errores (antes 12) · referencia idéntica |
| 7 | Aplica la fase R7 de la auditoría: constante STOCK_MINIMO en reportes | reportes.py: nueva constante STOCK_MINIMO = 5, usada en productos_stock_bajo y reporte_inventario. | El 5 mágico ahora tiene nombre y está en un solo lugar (#10). Categoría: renombrar variables o funciones (constante con nombre). | ✅ 20 passed · ruff: 12 errores (antes 12) · referencia idéntica |
| 8 | Aplica la fase R8 de la auditoría: usar with open en la persistencia | almacen.py:guardar_datos y cargar_datos: open/close manual pasa a with open (as archivo); se quita el modo "r"; se agregan hints. La carga del estado sigue en sitio. | El archivo se cierra solo aunque haya error y el código es más corto (#5, #20). Categoría: mejorar manejo de errores. | ✅ 20 passed · ruff: 9 errores (antes 12) · referencia idéntica |
| 9 | Aplica la fase R9 de la auditoría: acotar la excepción de archivo corrupto | almacen.py:cargar_datos: except Exception pasa a except ValueError. | Ya no oculta errores ajenos al archivo; ValueError atrapa JSON inválido y bytes no UTF-8 (#6). Categoría: mejorar manejo de errores. | ✅ 20 passed · ruff: 9 errores (antes 9) · referencia idéntica (incluye b"\xff\xfe") |

> Agrega más filas si realizas más de 5 refactorizaciones.

## Reflexión final (10-15 líneas)

Responde: ¿Qué tan útil fue Claude Code para detectar y corregir los problemas?
¿Qué propuso la IA que tú no habías notado? ¿En qué casos tuviste que corregir
o rechazar sus sugerencias? ¿Qué aprendiste sobre refactorizar con apoyo de IA?

*(Escribe aquí tu reflexión)*
