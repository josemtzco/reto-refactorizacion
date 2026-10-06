# CLAUDE.md — Reto de refactorización "La Esquina"

## 1. Descripción del proyecto

Gestor de inventario y ventas en consola para la tienda "La Esquina". Es código
legado que se refactoriza como reto académico: el objetivo es mejorar la calidad
(legibilidad, estilo, complejidad) **sin cambiar el comportamiento**. Los tests de
`tests/` son de caja negra y son el contrato.

| Módulo | Responsabilidad |
|---|---|
| `src/gestor.py` | Núcleo del negocio. Estado global (`INVENTARIO`, `VENTAS`, `contador_ventas`, `ultimo_error`), alta/baja/actualización/búsqueda de productos, `registrar_venta` (validación, descuentos por volumen y VIP, IVA 16 %, folio, ticket) y `cotizar`. |
| `src/almacen.py` | Persistencia en JSON: `guardar_datos`, `cargar_datos` (claves `inventario`, `ventas`, `contador`) y `hay_archivo`. Escribe `gestor.ultimo_error` en fallos. |
| `src/reportes.py` | Reportes: productos con stock bajo (< 5), reporte de inventario, total vendido, más vendidos y resumen de ventas. `reporte_inventario` y `resumen_ventas` imprimen **y** regresan el texto. |
| `src/main.py` | Punto de entrada: menú interactivo por consola que orquesta los otros tres módulos usando `datos_ejemplo.json`. |
| `tests/` | Pruebas de caja negra (`test_gestor.py`, `test_almacen.py`, `test_reportes.py`). `conftest.py` añade `src/` al `sys.path` y llama a `gestor.reiniciar_sistema()` antes y después de cada prueba. |

Los módulos se importan como `import gestor` (no hay paquete): no conviertas a
imports relativos ni muevas archivos fuera de `src/`.

## 2. Comandos

Ejecutar desde la raíz del repo (Windows, entorno virtual `.venv`):

```powershell
.venv\Scripts\python -m pytest
.venv\Scripts\python -m ruff check src
```

Ambos deben terminar sin errores antes de cada commit.

## 3. Reglas inviolables

1. **No modificar** nada dentro de `tests/` ni `pyproject.toml` (se revisan en el PR).
   Para pasar ruff se corrige el código, nunca la configuración. Prohibido `# noqa`
   para esquivar reglas.
2. **Conservar** los nombres públicos `agregarProducto` y `buscarProducto` (los usan
   los tests y están en `ignore-names` de ruff).
3. **No cambiar el comportamiento observable**:
   - Valores de retorno: `True`/`False`, `None` en error, dicts de producto/venta con
     las mismas claves, tuplas `(codigo, unidades)` en `mas_vendidos`.
   - `ultimo_error`: mismos mensajes exactos (`"codigo vacio"`, `"el producto ya existe"`,
     `"precio invalido"`, `"stock invalido"`, `"producto no existe"`,
     `"el stock no puede quedar negativo"`, `"cantidad invalida"`, `"stock insuficiente"`,
     `"el archivo no existe"`, `"archivo corrupto"`) y el **mismo orden de validación**.
   - Formato del ticket: texto, saltos de línea, la línea `Descuento` solo si hay
     descuento, y montos formateados como `str(round(x, 2))` (no cambiar a `:.2f`).
   - Cálculos: umbrales de descuento (≥ 1000 → 10 %, ≥ 500 → 5 %), VIP +2 % si el
     cliente empieza con `"VIP"` y la base pasa de 200, IVA 16 %, redondeos en el
     mismo punto. `cotizar` **no** aplica VIP.
   - Estado global accesible como `gestor.INVENTARIO`, `gestor.VENTAS`,
     `gestor.ultimo_error` y `gestor.reiniciar_sistema()`; formato del JSON intacto.
4. Se puede eliminar código muerto (p. ej. `calcular_descuento_viejo`,
   `reporteViejoCSV`, el bloque comentado `exportar_txt`) solo si nada en `src/` ni
   `tests/` lo referencia, y dejándolo registrado en la bitácora.

## 4. Guía de estilo

- **PEP 8** y `line-length = 88`.
- **snake_case** para funciones y variables (excepto los dos nombres protegidos).
  Nombres descriptivos: nada de `x`, `aux`, `temp2`, `hacer_cosa`.
- **Type hints** en parámetros y retornos (`str | None`, `dict[str, ...]`, Python 3.10+).
- **f-strings** en lugar de concatenar con `+` y `str()`.
- **`with open(...)`** siempre; nunca `open` + `close` manual.
- **Constantes en MAYÚSCULAS** para números mágicos (`TASA_IVA = 0.16`,
  `STOCK_MINIMO = 5`, umbrales de descuento, `PREFIJO_VIP = "VIP"`).
- **Complejidad ciclomática ≤ 10** por función (regla `C90`): extraer funciones
  pequeñas, cláusulas de guarda en vez de `if` anidados.
- Usar built-ins idiomáticos (`sorted`, `dict.get`, comprensiones) cuando no
  cambien el resultado.

### Ejemplo antes / después

Antes:

```python
def reporteViejoCSV(ruta):
    f = open(ruta, "w", encoding="utf-8")
    f.write("codigo,nombre,stock\n")
    for k in gestor.INVENTARIO:
        p = gestor.INVENTARIO[k]
        f.write(p["codigo"] + "," + p["nombre"] + "," + str(p["stock"]) + "\n")
    f.close()
    return ruta

def productos_stock_bajo():
    temp2 = []
    for k in gestor.INVENTARIO:
        if gestor.INVENTARIO[k]["stock"] < 5:
            temp2.append(gestor.INVENTARIO[k])
    return temp2
```

Después:

```python
STOCK_MINIMO = 5


def exportar_inventario_csv(ruta: str) -> str:
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write("codigo,nombre,stock\n")
        for producto in gestor.INVENTARIO.values():
            archivo.write(
                f"{producto['codigo']},{producto['nombre']},{producto['stock']}\n"
            )
    return ruta


def productos_stock_bajo() -> list[dict]:
    """Regresa los productos con stock por debajo del mínimo."""
    return [p for p in gestor.INVENTARIO.values() if p["stock"] < STOCK_MINIMO]
```

## 5. Flujo de trabajo

El plan está en `docs/spec-driven-development/auditoria-calidad.md`: hallazgos, orden de
ejecución y las **fases R1–R24**. Cada fase es una sola refactorización y termina en un
solo commit. Ese historial es la evidencia de validación incremental (Criterio 3).

Antes de la primera fase: crear `.venv`, instalar `requirements.txt` y guardar una
salida de referencia (tickets, `resumen_ventas()`, mensajes de `ultimo_error`) con un
script que no esté en `tests/` ni en `src/`.

Para cada fase `Rn`:

1. **Un cambio a la vez**: aplicar solo lo que define la fase; no mezclar otras mejoras.
   Si una fase crece, dividirla en sub-fases (`R20a`, `R20b`) con su propio commit.
2. Ejecutar `.venv\Scripts\python -m pytest` → todos en verde.
3. Ejecutar `.venv\Scripts\python -m ruff check src` → sin errores nuevos
   (meta final: cero errores).
4. Comparar con la salida de referencia → idéntica. Si la fase toca `main.py`,
   probar además el menú a mano.
5. Si algo falla, revertir o corregir antes de seguir; nunca hacer commit de una fase
   en rojo ni acumular cambios rotos.
6. Registrar la fase en `docs/bitacora_josejuanmartinezmorales.md` (fila `n` = fase
   `Rn`: prompt, cambio, justificación, resultado de tests).
7. **Commit** del código y la bitácora juntos, con el formato
   `refactor(Rn): <descripción en español>`
   (p. ej. `refactor(R21): extraer cálculo de montos de la venta`).
   Los commits que no son de refactorización usan otro tipo (`docs:`, `chore:`).

## 6. Aclaraciones por iteración

> Estado final (R1–R24 hechas): esta sección es el historial de las instrucciones que
> se dieron en cada iteración. Los nombres viejos que aparecen aquí (`hayArchivo`,
> `contadorVentas`, `temp2`, `aux`, `reporteViejoCSV`, etc.) ya no existen en `src/`.
> Los únicos nombres públicos con camelCase que se conservan son `agregarProducto` y
> `buscarProducto`.

### Iteración 1 — Paso 0, R1, R2, R3

**Paso 0: script de referencia (`scripts/salida_referencia.py`)**

- **Escribe la salida a un archivo desde Python**, no con `>`: en Windows PowerShell
  `>` puede guardar en UTF-16 o con BOM, y entonces `git diff` lo trata como binario.
  El script recibe la ruta destino como argumento y usa
  `open(ruta, "w", encoding="utf-8")`. Los comandos quedan así:
  `.venv\Scripts\python scripts\salida_referencia.py scripts\referencia_base.txt`
  (y `scripts\referencia_actual.txt` en cada fase).
- **Nunca imprimas la clave `fecha`** de una venta (`datetime.now()`): la salida
  cambiaría en cada corrida. Imprime la venta sin esa clave, y lo mismo con el JSON
  guardado.
- Imprime las ventas y los resultados con `repr(...)`, no solo con `print`, para
  detectar cambios de tipo como `0` → `0.0` (importa en R18).
- Casos mínimos que debe cubrir, además de los de §4 del agente:
  - Bordes del descuento: subtotal exacto de 500, de 1000 y uno menor a 500.
  - VIP: `"VIP01"` con base mayor a 200; `"VIP01"` con subtotal exacto de 200 (no
    aplica, la condición es `> 200`); `"VIP01"` con 300 (solo VIP, sin volumen);
    `"vip01"` (minúsculas, no aplica); `"VI"`; `""`; `None`.
  - `cotizar` con los mismos montos (no aplica VIP) y con código `""` (da
    `"producto no existe"`, no `"codigo vacio"`).
  - Orden de validación: casos con **dos** errores a la vez (p. ej. código `""` y
    precio negativo → `"codigo vacio"`; producto inexistente y cantidad 0 →
    `"producto no existe"`).
  - `agregarProducto(0, ...)`: se acepta (protege contra cambiar a `not codigo`).
  - `mas_vendidos()` con un **empate** de unidades (protege R13).
  - `buscarProducto` con mayúsculas y minúsculas mezcladas.
  - `cargar_datos` con JSON inválido **y** con bytes que no son UTF-8 (`b"\xff\xfe"`):
    los dos dan `"archivo corrupto"`.
- **Menú:** ejecútalo con `subprocess.run([sys.executable, "<raíz>/src/main.py"],
  input=..., cwd=<carpeta temporal con una copia de datos_ejemplo.json>,
  env={..., "PYTHONIOENCODING": "utf-8"}, capture_output=True, text=True,
  encoding="utf-8")`. La entrada recorre 1 a 7, una opción inválida (`9`), un número
  inválido (`abc`) y termina con `8`. Si la entrada se acaba antes del `8`,
  `input()` lanza `EOFError`.
- Commit: `scripts/salida_referencia.py` y `scripts/referencia_base.txt`.
  `referencia_actual.txt` se borra después de comparar.

**R1 — cabeceras de codificación**

- Solo los 4 archivos de `src/`. `tests/conftest.py` también la tiene: **no se toca**.
- Se permite `ruff check src --fix --select UP009`. Nunca `--fix` sin `--select`.

**R2 — imports de `main`**

- Orden final: `almacen`, `gestor`, `reportes`, en un solo bloque. Se permite
  `--fix --select I001`.

**R3 — código muerto**

- Se borran: `calcular_descuento_viejo`, el bloque comentado `exportar_txt`,
  `reporteViejoCSV` y `MODO_DEBUG`.
- Se borra también `import os` de `reportes.py`: ya no se usa (`F401`) y la
  auditoría no lo listó. Anótalo en la bitácora como código muerto.
- No borres otros comentarios todavía (p. ej. el `TODO` de la burbuja se va en R13).

---

### Iteración 2 — R4, R5, R6

**Lecciones de la iteración anterior:** ninguna registrada en la iteración 1 (R1-R3 sin incidencias).

**General desde aquí:** los type hints se agregan **solo a las funciones que la fase
toca**, no a todo el archivo (el resto es R24). Si conviertes un comentario
`# hace X` de la primera línea de la función en docstring, hazlo solo en la función
que tocas.

**R4 — `main.py`**

- Solo `temp2` → `respuesta` en `pedir_numero` y `len(bajos) == 0` → `not bajos`.
  Las variables de `menu` (`c`, `n`, `p`, `op`, …) **no** se renombran aquí: se van
  en R23.
- Hint: `pedir_numero(mensaje: str) -> float`.

**R5 — `actualizar_stock`**

- Solo `aux` → `nuevo_stock` (+ hints). El mensaje y el orden de las validaciones no
  cambian.

**R6 — constantes en `gestor.py`**

- Ubicación: arriba de `gestor.py`, después de los imports y antes del estado global.
  Nombres: `UMBRAL_DESCUENTO_ALTO = 1000`, `TASA_DESCUENTO_ALTO = 0.10`,
  `UMBRAL_DESCUENTO_MEDIO = 500`, `TASA_DESCUENTO_MEDIO = 0.05`, `TASA_IVA = 0.16`,
  `PREFIJO_VIP = "VIP"`, `MONTO_MINIMO_VIP = 200`, `TASA_EXTRA_VIP = 0.02`.
- **Solo se sustituyen literales**; la estructura de los `if` queda igual (se
  simplifica en R18 y R19). El `3` y el `cliente[0:3]` del VIP se quedan como están
  hasta R19.
- No reescribas fórmulas: `base + base * TASA_IVA` **no** pasa a
  `base * (1 + TASA_IVA)`, porque con flotantes el resultado puede cambiar en el
  último decimal. Mismo orden de operaciones, solo cambia el nombre del número.

---

### Iteración 3 — R7, R8, R9

**Lecciones de la iteración anterior:** ninguna registrada en la iteración 2 (R4-R6 sin incidencias).

**R7 — `STOCK_MINIMO` en `reportes.py`**

- Una sola constante `STOCK_MINIMO = 5` arriba de `reportes.py`, usada en
  `productos_stock_bajo` **y** en `reporte_inventario`. Nada más cambia.

**R8 — `with open` en `almacen.py`**

- `guardar_datos`: `with open(ruta, "w", encoding="utf-8") as archivo:` y dentro el
  `json.dump` con los mismos argumentos (`indent=2, ensure_ascii=False`).
- `cargar_datos`: dentro del `with` va solo el `json.load` (con su `try`). La carga
  del estado (`clear` + asignación/`append`) va **después** del `with`, y sigue
  modificando en sitio: nunca `gestor.INVENTARIO = ...`.
- Se quita el modo `"r"` (`UP015`). Todavía **no** cambies `except Exception` (es R9).

**R9 — `except ValueError`**

- `except ValueError`, no `json.JSONDecodeError`: `ValueError` también atrapa el
  `UnicodeDecodeError` de un archivo con bytes inválidos. El caso `b"\xff\xfe"` del
  script de referencia lo comprueba.

---

### Iteración 4 — R10, R11, R12

**Lecciones de la iteración anterior:** ninguna registrada en la iteración 3 (R7-R9 sin incidencias).

**R10 — `hay_archivo`**

- `def hay_archivo(ruta: str) -> bool:` con `return os.path.exists(ruta)` y una
  docstring. Actualizar la llamada en `main.py` **en el mismo commit**.
- Comprueba con `Grep` que no quede ningún `hayArchivo` en `src/`.
- Esta fase toca `main.py`: además del script, el alumno prueba el menú a mano en el
  checkpoint.

**R11 — comprensiones en `reportes.py`**

- `productos_stock_bajo`: `[p for p in gestor.INVENTARIO.values() if p["stock"] <
  STOCK_MINIMO]` (mismo orden que el diccionario).
- `total_vendido`: `round(sum(v["total"] for v in gestor.VENTAS), 2)`. `sum` suma en
  el mismo orden que el bucle, así que el resultado es idéntico.

**R12 — `formatear_dinero`**

- `def formatear_dinero(monto: float) -> str:` y renombrar sus 4 usos.
- Se permite `f"${round(monto, 2)}"` (da el mismo texto que `"$" + str(...)`).
  Prohibido `:.2f`: cambiaría `$23.2` por `$23.20`.

---

### Iteración 5 — R13, R14, R15

**Lecciones de la iteración anterior:** ninguna de código en la iteración 4 (R10-R12
sin incidencias). Nota de proceso de la iteración 3: un `Remove-Item` encadenado con
otros comandos fue bloqueado por el sandbox; ejecuta cada paso por separado.

**R13 — `sorted` en `mas_vendidos`**

- Conteo: `conteo[codigo] = conteo.get(codigo, 0) + venta["cantidad"]`.
- Orden: `sorted(conteo.items(), key=lambda par: par[1], reverse=True)[:n]`.
  `reverse=True` respeta el orden original en los empates, igual que la burbuja (que
  solo intercambia con `<`). El caso de empate del script de referencia lo confirma.
- Se borra el comentario `TODO` de la burbuja. Hints: `n: int = 3` y
  `-> list[tuple[str, int]]`.

**R14 — f-strings en reportes**

- Solo `reporte_inventario` y `resumen_ventas`. Nombres: `s` → `reporte`,
  `aux` → `valor_total`, `t` → `total_dia`, `p` → `producto`, `v` → `venta`.
- Se mantienen el bucle, el `print(...)` **y** el `return` del texto.
- No reutilices `total_vendido()` dentro de `resumen_ventas`: redondea en otro punto
  y mezclaría dos cambios.
- Ojo con `line-length = 88`: si una f-string no cabe, pártela en dos líneas.

**R15 — dict literal en `agregarProducto`**

- El nombre `agregarProducto` **no** cambia.
- `codigo in (None, "")`, **no** `not codigo` (con `0` cambiaría el resultado; el
  script de referencia lo prueba).
- Mismo orden de validación: código vacío → ya existe → precio → stock.

---

### Iteración 6 — R16, R17, R18

**Lecciones de la iteración anterior:** ninguna de código en la iteración 5 (R13-R15
sin incidencias). Nota de proceso: ejecuta cada paso de PowerShell por separado (no
encadenes comandos como `Remove-Item` con otros).

**R16 — comprensión en `buscarProducto`**

- El nombre `buscarProducto` **no** cambia.
- Forma elegida: `[p for p in INVENTARIO.values() if texto.lower() in
  p["nombre"].lower()]`. La auditoría proponía calcular `texto.lower()` una sola vez
  antes; **no se hace**, porque con el inventario vacío y un `texto` que no es
  cadena el código original regresa `[]` y el nuevo lanzaría un error. Es un cambio
  de comportamiento, aunque sea pequeño, y la regla inviolable manda. Anótalo en la
  bitácora.

**R17 — `contador_ventas`**

- Renombrar en **todos** los sitios en el mismo commit: la declaración, los dos
  `global` (`reiniciar_sistema`, `registrar_venta`), sus usos en `registrar_venta`,
  y en `almacen.py` (`guardar_datos` y `cargar_datos`).
- La clave JSON sigue siendo `"contador"`. Al final, `Grep "contadorVentas" src`
  debe dar 0 resultados.

**R18 — `_descuento_por_volumen(subtotal)` compartida**

- La usan `registrar_venta` **y** `cotizar`. Con cláusulas de guarda:
  `if subtotal >= UMBRAL_DESCUENTO_ALTO: return subtotal * TASA_DESCUENTO_ALTO`,
  igual con el medio y al final **`return 0` (entero, no `0.0`)**. Con `0.0`, la
  venta guardaría `"descuento": 0.0` en vez de `0` y cambiaría el JSON (el `repr`
  del script de referencia lo detecta).
- Hint: `-> float` (un `int` es válido donde se espera `float`).
- El VIP no se toca aquí (es R19).

---

### Iteración 7 — R19, R20, R21

**Lecciones de la iteración anterior:** ninguna de código en la iteración 6 (R16-R18
sin incidencias). Notas de proceso: el `Read` avisó de un cambio en disco por una
edición propia, sin efecto; el aviso `LF → CRLF` de git es solo `autocrlf`.

**R19 — `_aplica_vip(cliente, base)`**

- `return bool(cliente) and cliente.startswith(PREFIJO_VIP) and base >
  MONTO_MINIMO_VIP`. `bool(cliente)` cubre `None` y `""`; `startswith` cubre el
  `len >= 3`.
- La `base` que recibe es `subtotal - descuento` **antes** de sumar el extra VIP. El
  extra se sigue calculando sobre el subtotal: `descuento + subtotal *
  TASA_EXTRA_VIP`.
- `cotizar` **no** llama a `_aplica_vip`.

**R20 — cláusulas de guarda en `registrar_venta`**

- Orden exacto: `codigo in (None, "")` → `"codigo vacio"`; `codigo not in INVENTARIO`
  → `"producto no existe"`; `cantidad is None or not cantidad > 0` →
  `"cantidad invalida"`; `INVENTARIO[codigo]["stock"] < cantidad` →
  `"stock insuficiente"`.
- Se permite renombrar `temp2` → `producto` en esta fase, porque desaparece el
  `temp2 = None` inicial.
- Solo se reordena la validación; los cálculos no se mueven (son R21).

**R21 — extraer el cálculo de montos**

- Una función, p. ej. `_calcular_montos(subtotal, cliente) -> tuple[float, float,
  float]`, que regrese `(descuento, impuesto, total)`.
- **Los redondeos quedan donde estaban:** `total` sale redondeado; `descuento` e
  `impuesto` salen **sin** redondear y se redondean al guardarlos en la venta. El
  ticket necesita el descuento sin redondear para la condición `> 0`.
- `aux` → `subtotal`, `desc` → `descuento`. No construyas el dict de la venta aquí.

---

### Iteración 8 — R22, R23, R24 y cierre

**Lecciones de la iteración anterior:** en la iteración 7, al validar `cantidad` con
`cantidad is None or cantidad <= 0` (R20) se perdió un caso del original: con `NaN`
el original rechazaba (`NaN > 0` es falso), pero `NaN <= 0` también es falso, así que
la versión nueva lo dejaba pasar. Se corrige en R22 con
`cantidad is None or not cantidad > 0` (en `registrar_venta` y `cotizar`), mismo
mensaje y mismo orden. Lección: al invertir una comparación, `not (a > b)` no es lo
mismo que `a <= b` cuando hay `NaN`.

**R22 — `_construir_ticket(venta, descuento)`**

- f-strings con exactamente las mismas líneas y `\n`. `f"{x}"` da el mismo texto que
  `str(x)` para `int` y `float`.
- La línea `Descuento: -$...` aparece solo si `descuento > 0`, con el descuento
  **sin redondear** (el que regresa `_calcular_montos`).

**R23 — menú con diccionario**

- Una función por opción (`_opcion_agregar_producto`, `_opcion_registrar_venta`,
  `_opcion_cotizar`, …) y `OPCIONES = {"1": ..., "7": ...}`. La opción `"8"` es un
  caso especial del bucle (guarda, imprime y hace `break`). Cualquier otra entrada
  imprime `"Opcion no valida."`.
- **Los textos no cambian ni un carácter:** prompts de `input`, mensajes,
  `print("")` y textos sin acentos (`"Opcion"`, `"Mas vendidos"`). No "corrijas" la
  ortografía de lo que ve el usuario.
- `print("Error:", gestor.ultimo_error)` puede quedarse con coma (el espacio lo pone
  `print`).
- Aquí sí se renombran `c`, `n`, `p`, `s`, `cant`, `cli`, `v`, `t`, `op`.
- `menu` debe quedar con complejidad ≤ 10. Prueba manual del menú en el checkpoint.

**R24 — type hints restantes**

- Solo las funciones que aún no tienen hints. Tipos simples: `str`, `int`, `float`,
  `bool`, `dict`, `list[dict]`, `str | None`, `dict | None`, `float | None`, `-> None`.
  Nada de `TypedDict` ni `typing.Any` (regla de lo más simple).
- Los hints no se comprueban al ejecutar: no cambian el comportamiento.
- Meta: `ruff check src` → `All checks passed!`.

**Cierre**

- Revisa que la sección `## 6. Aclaraciones por iteración` de `CLAUDE.md` siga
  siendo cierta con el código final (nombres viejos como `hayArchivo` o
  `contadorVentas` ya no existen) y corrígela en el commit `docs:` del cierre.

