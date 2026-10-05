# CLAUDE.md — Reto de refactorización "La Esquina"

## 1. Descripción del proyecto

Gestor de inventario y ventas en consola para la tienda "La Esquina". Es código
legado que se refactoriza como reto académico: el objetivo es mejorar la calidad
(legibilidad, estilo, complejidad) **sin cambiar el comportamiento**. Los tests de
`tests/` son de caja negra y son el contrato.

| Módulo | Responsabilidad |
|---|---|
| `src/gestor.py` | Núcleo del negocio. Estado global (`INVENTARIO`, `VENTAS`, `contadorVentas`, `ultimo_error`), alta/baja/actualización/búsqueda de productos, `registrar_venta` (validación, descuentos por volumen y VIP, IVA 16 %, folio, ticket) y `cotizar`. |
| `src/almacen.py` | Persistencia en JSON: `guardar_datos`, `cargar_datos` (claves `inventario`, `ventas`, `contador`) y `hayArchivo`. Escribe `gestor.ultimo_error` en fallos. |
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

1. **Un cambio a la vez**: una sola refactorización pequeña y enfocada por iteración.
2. Ejecutar `.venv\Scripts\python -m pytest` → todos en verde.
3. Ejecutar `.venv\Scripts\python -m ruff check src` → sin errores nuevos
   (meta final: cero errores).
4. Si algo falla, revertir o corregir antes de seguir; nunca acumular cambios rotos.
5. **Commit** con mensaje descriptivo en español
   (p. ej. `refactor(gestor): extraer cálculo de descuento`).
6. Registrar el cambio en `docs/bitacora_josejuanmartinezmorales.md`
   (prompt, cambio, justificación, resultado de tests).
