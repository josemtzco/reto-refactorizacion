"""Reportes de la tienda: inventario, ventas y mas vendidos."""

import gestor

STOCK_MINIMO = 5


def formatear_dinero(monto: float) -> str:
    """Le da formato de dinero al numero."""
    return "$" + str(round(monto, 2))


def productos_stock_bajo() -> list[dict]:
    """Regresa la lista de productos con stock por debajo del minimo."""
    return [p for p in gestor.INVENTARIO.values() if p["stock"] < STOCK_MINIMO]


def reporte_inventario() -> str:
    """Arma el reporte del inventario, lo imprime y lo regresa como texto."""
    reporte = "===== INVENTARIO =====\n"
    valor_total = 0
    for producto in gestor.INVENTARIO.values():
        precio = formatear_dinero(producto["precio"])
        linea = f"{producto['codigo']} | {producto['nombre']} | {precio}"
        linea = f"{linea} | stock: {producto['stock']}"
        if producto["stock"] < STOCK_MINIMO:
            linea = f"{linea}  <-- STOCK BAJO"
        reporte = f"{reporte}{linea}\n"
        valor_total = valor_total + producto["precio"] * producto["stock"]
    reporte = f"{reporte}Valor total del inventario: {formatear_dinero(valor_total)}\n"
    print(reporte)
    return reporte


def total_vendido() -> float:
    """Suma el total (con IVA) de todas las ventas registradas."""
    return round(sum(v["total"] for v in gestor.VENTAS), 2)


def mas_vendidos(n: int = 3) -> list[tuple[str, int]]:
    """Regresa los n productos mas vendidos como lista de (codigo, unidades)."""
    conteo = {}
    for venta in gestor.VENTAS:
        codigo = venta["codigo"]
        conteo[codigo] = conteo.get(codigo, 0) + venta["cantidad"]
    ordenados = sorted(conteo.items(), key=lambda par: par[1], reverse=True)
    return ordenados[:n]


def resumen_ventas() -> str:
    """Arma el resumen de ventas del dia, lo imprime y lo regresa."""
    reporte = "===== RESUMEN DE VENTAS =====\n"
    total_dia = 0
    for venta in gestor.VENTAS:
        total = formatear_dinero(venta["total"])
        reporte = f"{reporte}Folio {venta['folio']}: {venta['nombre']}"
        reporte = f"{reporte} x{venta['cantidad']} = {total}\n"
        total_dia = total_dia + venta["total"]
    reporte = f"{reporte}Numero de ventas: {len(gestor.VENTAS)}\n"
    reporte = f"{reporte}Total del dia: {formatear_dinero(total_dia)}\n"
    print(reporte)
    return reporte
