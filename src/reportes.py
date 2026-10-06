"""Reportes de la tienda: inventario, ventas y mas vendidos."""

import gestor

STOCK_MINIMO = 5


def formatear_dinero(monto: float) -> str:
    """Le da formato de dinero al numero."""
    return "$" + str(round(monto, 2))


def productos_stock_bajo() -> list[dict]:
    """Regresa la lista de productos con stock por debajo del minimo."""
    return [p for p in gestor.INVENTARIO.values() if p["stock"] < STOCK_MINIMO]


def reporte_inventario():
    """Arma el reporte del inventario, lo imprime y lo regresa como texto."""
    s = "===== INVENTARIO =====\n"
    aux = 0
    for k in gestor.INVENTARIO:
        p = gestor.INVENTARIO[k]
        linea = p["codigo"] + " | " + p["nombre"] + " | "
        linea = linea + formatear_dinero(p["precio"]) + " | stock: " + str(p["stock"])
        if p["stock"] < STOCK_MINIMO:
            linea = linea + "  <-- STOCK BAJO"
        s = s + linea + "\n"
        aux = aux + p["precio"] * p["stock"]
    s = s + "Valor total del inventario: " + formatear_dinero(aux) + "\n"
    print(s)
    return s


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


def resumen_ventas():
    """Arma el resumen de ventas del dia, lo imprime y lo regresa."""
    s = "===== RESUMEN DE VENTAS =====\n"
    t = 0
    for v in gestor.VENTAS:
        s = s + "Folio " + str(v["folio"]) + ": " + v["nombre"]
        s = s + " x" + str(v["cantidad"]) + " = " + formatear_dinero(v["total"]) + "\n"
        t = t + v["total"]
    s = s + "Numero de ventas: " + str(len(gestor.VENTAS)) + "\n"
    s = s + "Total del dia: " + formatear_dinero(t) + "\n"
    print(s)
    return s
