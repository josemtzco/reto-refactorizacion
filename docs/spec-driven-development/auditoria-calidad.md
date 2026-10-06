# Auditoría de calidad de `src/`

> Diagnóstico previo a la refactorización. No se modificó código.
> Los códigos de ruff (`UP009`, `C901`, …) se infirieron leyendo el código:
> al momento de la auditoría no existía `.venv`, así que ruff y pytest no se
> ejecutaron. Confirmarlos con `.venv\Scripts\python -m ruff check src`.

## Tabla de hallazgos (ordenada por severidad)

| # | archivo:función | code smell | severidad | refactorización propuesta | riesgo para los tests |
|---|---|---|---|---|---|
| 1 | `gestor.py:86` `registrar_venta` | Función "hace-todo" (valida, calcula, muta stock, folio, ticket, guarda). `if/else` anidados en 4 niveles; complejidad ≈ 12 (`C901`). | alta | Cláusulas de guarda con el **mismo orden** (código vacío → no existe → cantidad → stock); extraer `_calcular_descuento`, `_construir_ticket`, `_crear_registro_venta`. | **Alto**: es lo más probado (totales, folio, stock, rechazos). Los tests no validan el texto del ticket ni los mensajes de `ultimo_error`, así que un cambio ahí pasaría desapercibido. |
| 2 | `gestor.py:115-131` y `gestor.py:173-181` `registrar_venta` / `cotizar` | Lógica de descuento por volumen duplicada; números mágicos (1000, 500, 0.10, 0.05, 0.16, 200, 0.02). | alta | `_descuento_por_volumen(subtotal)` compartida; constantes `UMBRAL_DESCUENTO_ALTO`, `TASA_DESCUENTO_ALTO`, `TASA_IVA`, `PREFIJO_VIP`, `MONTO_MINIMO_VIP`, `TASA_EXTRA_VIP`. `cotizar` sigue **sin** VIP. | **Medio**: `test_cotizar_coincide…` y las 3 pruebas de descuento lo vigilan bien. El VIP solo tiene un caso (600 → 5 % + 2 %). |
| 3 | `gestor.py:126-130` `registrar_venta` | 4 `if` anidados para VIP (`SIM102`); `cliente[0:3] == "VIP"` en vez de `startswith`. | alta | `_aplica_vip(cliente, base) -> bool` con `bool(cliente) and cliente.startswith(PREFIJO_VIP) and base > MONTO_MINIMO_VIP`. La base del umbral sigue siendo `aux - desc`, es decir, **después** del descuento por volumen. | **Medio**: un solo test VIP. No se prueba el umbral de 200 ni `cliente=None`. |
| 4 | `main.py:21` `menu` | Cadena de 8 `elif` dentro de un `while`, con `if` anidados; complejidad ≈ 14 (`C901`). Nombres de una letra (`c`, `n`, `p`, `s`, `v`, `t`, `op`, `cli`, `cant`). | alta | Una función por opción (`_opcion_agregar_producto`, …) y un dict `OPCIONES = {"1": …}` para despacharlas; la opción 8 (guardar y salir) como caso especial del bucle. | **Nulo en pytest** (no hay tests de `main`), pero el riesgo real es alto: hay que verificarlo manualmente con el menú. |
| 5 | `almacen.py:16-18` `guardar_datos`, `almacen.py:30-37` `cargar_datos` | `open` + `close` manual: si `json.dump` falla, el archivo queda abierto. `close()` duplicado en dos caminos. | alta | `with open(...)` en ambas; en `cargar_datos`, solo el `json.load` dentro del `with`/`try` y la carga del estado después. | **Bajo**: 3 tests de ida y vuelta. No hay test de "archivo corrupto". |
| 6 | `almacen.py:33` `cargar_datos` | `except Exception` demasiado amplio. | media | `except ValueError` (cubre `JSONDecodeError` **y** `UnicodeDecodeError`), para que `"archivo corrupto"` salga en los mismos casos que antes. | **Bajo**. Ojo: usar solo `JSONDecodeError` cambiaría el comportamiento con bytes inválidos. |
| 7 | `gestor.py:15` `contadorVentas` | Global en mixedCase (`N816`). | media | Renombrar a `contador_ventas` en `gestor` (líneas 15, 22, 25, 94, 136, 138) y `almacen` (líneas 15, 44) **en el mismo commit**. La clave JSON `"contador"` no cambia. | **Medio**: si falta un sitio, `test_el_folio_continua…` falla (lo detecta). Los tests no usan el nombre directamente. |
| 8 | `almacen.py:48` `hayArchivo` | Nombre fuera de PEP 8 (`N802`, no está en `ignore-names`); `if/else` que devuelve booleanos (`SIM103`). | media | `hay_archivo(ruta: str) -> bool: return os.path.exists(ruta)`; actualizar `main.py:23`. | **Nulo en pytest** (solo la usa `main`). |
| 9 | `reportes.py:48` `mas_vendidos` | Ordenamiento burbuja manual; conteo con `if/else`; nombres `aux`, `temp`, `t`. | media | `conteo[c] = conteo.get(c, 0) + cant` y `sorted(conteo.items(), key=lambda par: par[1], reverse=True)[:n]`. `sorted` con `reverse=True` es estable, así que los empates conservan el mismo orden que con la burbuja. | **Bajo**: `test_mas_vendidos…` lo cubre (sin empates). |
| 10 | `reportes.py:23` `reporte_inventario`, `reportes.py:69` `resumen_ventas` | Texto armado con `+` y `str()`; nombres `s`, `aux`, `t`, `p`; umbral `5` duplicado con `productos_stock_bajo`. | media | f-strings, `STOCK_MINIMO = 5`, nombres descriptivos. Se mantiene `print` + `return` (contrato). | **Bajo** en el inventario (se prueba por contenido). `resumen_ventas` no tiene tests: comparar su salida antes y después. |
| 11 | `reportes.py:9` `hacer_cosa` | Nombre que no dice qué hace. | media | `formatear_dinero(monto: float) -> str`, manteniendo `str(round(monto, 2))` (no `:.2f`). | **Bajo**: es interna y la cubre el reporte de inventario. |
| 12 | `gestor.py:148-159` ticket | Concatenación con `t = t + …`; variable `t`. | media | `_construir_ticket(venta, descuento) -> str` con f-strings; la condición sigue siendo `desc > 0` sobre el descuento **sin redondear**. | **Nulo en pytest** (no hay tests del ticket), pero el riesgo silencioso es alto: usar una salida de referencia (ver paso 0). |
| 13 | `gestor.py:185` `calcular_descuento_viejo`, `gestor.py:193-198` `exportar_txt` comentado, `reportes.py:83` `reporteViejoCSV` | Código muerto (`reporteViejoCSV` además tiene `N802` y `open`/`close` manual). | media | Eliminarlo (nada en `src/` ni `tests/` lo usa) y registrarlo en la bitácora. | **Nulo**. |
| 14 | `gestor.py:29` `agregarProducto` | `x = {}` seguido de 4 asignaciones; `codigo is None or codigo == ""`. | baja | Dict literal; `codigo in (None, "")` en vez de `not codigo`, porque `not codigo` cambiaría el resultado para `0`. Mismo orden de validación; se conserva el nombre. | **Bajo**: bien cubierta. |
| 15 | `gestor.py:77` `buscarProducto` | Bucle que acumula en `temp2`; `texto.lower()` se calcula en cada vuelta. | baja | Comprensión, con el texto en minúsculas calculado una sola vez. Se conserva el nombre. | **Bajo**. |
| 16 | `gestor.py:63` `actualizar_stock` | Variable `aux`. | baja | `nuevo_stock`. | **Bajo**. |
| 17 | `reportes.py:14` `productos_stock_bajo`, `reportes.py:40` `total_vendido` | Bucles que acumulan; `temp2`, `t`; el `5` mágico. | baja | Comprensión con `STOCK_MINIMO`; `round(sum(v["total"] for v in gestor.VENTAS), 2)`. | **Bajo**: tests exactos de las dos. |
| 18 | Los 4 archivos, línea 1 | `# -*- coding: utf-8 -*-` sobra en Python 3 (`UP009`). | baja | Quitarlo. | **Nulo**. |
| 19 | `main.py:4-6` | Imports desordenados (`I001`). | baja | Orden alfabético: `almacen`, `gestor`, `reportes`. | **Nulo**. |
| 20 | `almacen.py:30` | Modo `"r"` explícito y redundante (`UP015`). | baja | Quitarlo al pasar a `with`. | **Nulo**. |
| 21 | Todo `src/` | Sin type hints. | baja | Anotar cada función al tocarla (`str \| None`, `dict[str, dict]`, `list[tuple[str, int]]`). | **Nulo**. |
| 22 | `gestor.py:17` `MODO_DEBUG` | Constante que nadie usa. | baja | Eliminarla y registrarlo en la bitácora. | **Nulo**. |
| 23 | `main.py:11` `pedir_numero`, `main.py:72` | Nombre `temp2`; `len(bajos) == 0`. | baja | `respuesta`; `if not bajos:`. | **Nulo en pytest**. |
| — | Estado global con `global` en `gestor` | Acoplamiento por estado global mutable. | (no se toca) | Fuera de alcance: `gestor.INVENTARIO` / `VENTAS` / `ultimo_error` son contrato. En `cargar_datos` se sigue **modificando en sitio** (`clear` + `update`/`extend`), nunca reasignando. | — |

## Orden de ejecución propuesto

**Paso 0, preparar el entorno:** crear `.venv` e instalar `requirements.txt`. Después,
en un script fuera de `tests/`, guardar una **salida de referencia** de lo que los tests
no cubren: tickets (sin descuento, con volumen, con VIP), `resumen_ventas()` y los
mensajes de `ultimo_error` de cada caso de error. Compararla en cada paso.

1. **Cambios mecánicos sin lógica:** #18, #19, #20 → #13, #22 (código muerto). Bajan
   muchos avisos de ruff sin riesgo y dejan menos código que revisar después.
2. **Renombrar variables locales y añadir type hints**, módulo por módulo (#16, #23, #21).
   Cambian nombres, no lógica.
3. **Constantes** (`TASA_IVA`, umbrales, `STOCK_MINIMO`, `PREFIJO_VIP`) sin mover nada de
   sitio. Prepara los pasos 6 y 7.
4. **`almacen`:** `with open` y `except ValueError` (#5, #6), y después `hay_archivo` (#8).
   Lo cubren los tests de ida y vuelta.
5. **`reportes`:** #17 → #11 → #9 → #10. Cada uno tiene un test exacto, salvo
   `resumen_ventas`, que se compara con la salida de referencia.
6. **`gestor` (funciones simples):** #14, #15, y después #7 `contador_ventas` en un solo
   commit junto con `almacen`.
7. **`gestor` (lógica de negocio):** #2 (extraer el descuento compartido) → #3 (VIP) →
   #1 (cláusulas de guarda) → #12 (ticket). Primero se extrae lo que vigilan los tests de
   totales y `cotizar`; después se reordena el flujo de validación; al final va el
   ticket, que solo vigila la salida de referencia.
8. **`main.menu`** (#4) al final: no tiene tests, depende de los nombres que cambian en
   los pasos 4 y 6, y solo se puede comprobar ejecutando el menú a mano.

**Por qué este orden:** empieza por lo de riesgo casi nulo, que además limpia el ruido de
ruff para que cualquier error nuevo salte a la vista. Luego avanza de lo que los tests
cubren bien a lo que no cubren. Las partes más complejas (`registrar_venta`) se tocan
cuando ya existen las constantes y las funciones auxiliares, así cada paso es pequeño.
Lo que pytest no vigila (ticket, resumen, mensajes de error, `main`) queda protegido por
la salida de referencia del paso 0 y por la prueba manual final.

## Fases de refactorización (R1–R24)

Cada refactorización es una **fase** independiente, y cada fase termina en **un solo
commit** con el formato `refactor(Rn): <descripción en español>`. Ese historial de
commits es la **evidencia de validación incremental** que pide el Criterio 3: muestra
que el código pasó las pruebas después de cada cambio, no solo al final.

Las fases siguen el orden propuesto arriba. La columna "Hallazgos" remite a los números
de la tabla de hallazgos.

| Fase | Paso | Hallazgos | Archivos | Mensaje de commit |
|---|---|---|---|---|
| R1 | 1 | #18 | todos | `refactor(R1): quitar cabeceras de codificación innecesarias` |
| R2 | 1 | #19 | `main.py` | `refactor(R2): ordenar imports de main` |
| R3 | 1 | #13, #22 | `gestor.py`, `reportes.py` | `refactor(R3): eliminar código muerto` |
| R4 | 2 | #23 | `main.py` | `refactor(R4): nombres descriptivos en pedir_numero y alertas` |
| R5 | 2 | #16 | `gestor.py` | `refactor(R5): nombre descriptivo en actualizar_stock` |
| R6 | 3 | #2 (constantes) | `gestor.py` | `refactor(R6): constantes para IVA, descuentos y VIP` |
| R7 | 3 | #10 (constante) | `reportes.py` | `refactor(R7): constante STOCK_MINIMO en reportes` |
| R8 | 4 | #5, #20 | `almacen.py` | `refactor(R8): usar with open en la persistencia` |
| R9 | 4 | #6 | `almacen.py` | `refactor(R9): acotar la excepción de archivo corrupto` |
| R10 | 4 | #8 | `almacen.py`, `main.py` | `refactor(R10): renombrar hayArchivo a hay_archivo` |
| R11 | 5 | #17 | `reportes.py` | `refactor(R11): comprensiones en stock bajo y total vendido` |
| R12 | 5 | #11 | `reportes.py` | `refactor(R12): renombrar hacer_cosa a formatear_dinero` |
| R13 | 5 | #9 | `reportes.py` | `refactor(R13): usar sorted en mas_vendidos` |
| R14 | 5 | #10 | `reportes.py` | `refactor(R14): f-strings en reportes de inventario y ventas` |
| R15 | 6 | #14 | `gestor.py` | `refactor(R15): dict literal en agregarProducto` |
| R16 | 6 | #15 | `gestor.py` | `refactor(R16): comprensión en buscarProducto` |
| R17 | 6 | #7 | `gestor.py`, `almacen.py` | `refactor(R17): renombrar contadorVentas a contador_ventas` |
| R18 | 7 | #2 | `gestor.py` | `refactor(R18): extraer descuento por volumen compartido` |
| R19 | 7 | #3 | `gestor.py` | `refactor(R19): extraer regla de descuento VIP` |
| R20 | 7 | #1 | `gestor.py` | `refactor(R20): cláusulas de guarda en registrar_venta` |
| R21 | 7 | #1 | `gestor.py` | `refactor(R21): extraer cálculo de montos de la venta` |
| R22 | 7 | #12 | `gestor.py` | `refactor(R22): extraer construcción del ticket` |
| R23 | 8 | #4 | `main.py` | `refactor(R23): despachar opciones del menú con un diccionario` |
| R24 | — | #21 | todos | `refactor(R24): completar type hints` |

Los type hints (#21) se agregan a cada función cuando una fase la toca. R24 solo cubre
las funciones que no tocó ninguna fase anterior y cierra con ruff en cero errores.

### Protocolo de cada fase

1. Aplicar **solo** el cambio de la fase. Si aparece otra mejora, se anota para una
   fase nueva y no se mezcla.
2. Ejecutar `.venv\Scripts\python -m pytest`: todo en verde.
3. Ejecutar `.venv\Scripts\python -m ruff check src`: ningún error nuevo.
4. Comparar la salida de referencia del paso 0 (ticket, resumen, mensajes de
   `ultimo_error`): debe ser idéntica. En R10 y R23 se prueba además el menú a mano.
5. Si algo falla, corregir o revertir (`git restore src`) antes de seguir. Nunca se hace
   commit de una fase en rojo.
6. Registrar la fase en `docs/bitacora_josejuanmartinezmorales.md`: la fila `n` de la
   bitácora corresponde a la fase `Rn`.
7. Commit con el código **y** la fila de la bitácora:
   `git commit -m "refactor(Rn): <descripción>"`.

Si una fase resulta demasiado grande, se divide en sub-fases con su propio commit
(`R20a`, `R20b`, …) en lugar de agrupar cambios.
