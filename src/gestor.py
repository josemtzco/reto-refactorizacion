"""Modulo principal del gestor de inventario y ventas de "La Esquina".

Aqui vive casi toda la logica del negocio. Historicamente este archivo
lo fueron parchando varias personas, asi que hay de todo un poco.
"""

from datetime import datetime

UMBRAL_DESCUENTO_ALTO = 1000
TASA_DESCUENTO_ALTO = 0.10
UMBRAL_DESCUENTO_MEDIO = 500
TASA_DESCUENTO_MEDIO = 0.05
TASA_IVA = 0.16
PREFIJO_VIP = "VIP"
MONTO_MINIMO_VIP = 200
TASA_EXTRA_VIP = 0.02

# ---------------------------------------------------------------
# Estado global de la aplicacion (inventario, ventas y contadores)
# ---------------------------------------------------------------
INVENTARIO = {}
VENTAS = []
contador_ventas = 0
ultimo_error = ""


def reiniciar_sistema() -> None:
    """Borra todo el estado del sistema (inventario, ventas y folios)."""
    global contador_ventas, ultimo_error
    INVENTARIO.clear()
    VENTAS.clear()
    contador_ventas = 0
    ultimo_error = ""


def agregarProducto(codigo: str, nombre: str, precio: float, stock: int) -> bool:
    """Valida los datos y da de alta un producto en el inventario."""
    global ultimo_error
    if codigo in (None, ""):
        ultimo_error = "codigo vacio"
        return False
    if codigo in INVENTARIO:
        ultimo_error = "el producto ya existe"
        return False
    if precio <= 0:
        ultimo_error = "precio invalido"
        return False
    if stock < 0:
        ultimo_error = "stock invalido"
        return False
    INVENTARIO[codigo] = {
        "codigo": codigo,
        "nombre": nombre,
        "precio": precio,
        "stock": stock,
    }
    return True


def eliminar_producto(codigo: str) -> bool:
    """Quita un producto del inventario. Regresa False si no existe."""
    global ultimo_error
    if codigo in INVENTARIO:
        del INVENTARIO[codigo]
        return True
    ultimo_error = "producto no existe"
    return False


def actualizar_stock(codigo: str, cantidad: int) -> bool:
    """Suma unidades al stock (o resta si la cantidad es negativa)."""
    global ultimo_error
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return False
    nuevo_stock = INVENTARIO[codigo]["stock"] + cantidad
    if nuevo_stock < 0:
        ultimo_error = "el stock no puede quedar negativo"
        return False
    INVENTARIO[codigo]["stock"] = nuevo_stock
    return True


def buscarProducto(texto: str) -> list[dict]:
    """Busca productos cuyo nombre contenga el texto (sin importar mayusculas)."""
    return [
        producto
        for producto in INVENTARIO.values()
        if texto.lower() in producto["nombre"].lower()
    ]


def _descuento_por_volumen(subtotal: float) -> float:
    """Regresa el descuento que corresponde al subtotal (0 si no hay)."""
    if subtotal >= UMBRAL_DESCUENTO_ALTO:
        return subtotal * TASA_DESCUENTO_ALTO
    if subtotal >= UMBRAL_DESCUENTO_MEDIO:
        return subtotal * TASA_DESCUENTO_MEDIO
    return 0


def _aplica_vip(cliente: str | None, base: float) -> bool:
    """Dice si el cliente es VIP y su compra (ya con descuento) pasa del minimo."""
    return bool(cliente) and cliente.startswith(PREFIJO_VIP) and base > MONTO_MINIMO_VIP


def _calcular_montos(
    subtotal: float, cliente: str | None
) -> tuple[float, float, float]:
    """Regresa (descuento, impuesto, total) de una venta.

    El total sale redondeado; descuento e impuesto sin redondear.
    """
    descuento = _descuento_por_volumen(subtotal)
    # los clientes cuyo codigo empieza con VIP tienen un extra,
    # pero solo si su compra (ya con descuento) pasa de cierto monto
    if _aplica_vip(cliente, subtotal - descuento):
        descuento = descuento + subtotal * TASA_EXTRA_VIP
    base = subtotal - descuento
    impuesto = base * TASA_IVA
    total = round(base + impuesto, 2)
    return descuento, impuesto, total


def _construir_ticket(venta: dict, descuento: float) -> str:
    """Arma el ticket en texto plano.

    La linea de descuento aparece solo si el descuento (sin redondear) es mayor a 0.
    """
    ticket = "TIENDA LA ESQUINA\n"
    ticket += "----------------------------\n"
    ticket += f"Folio: {venta['folio']}\n"
    ticket += f"{venta['nombre']} x{venta['cantidad']}\n"
    ticket += f"Subtotal: ${venta['subtotal']}\n"
    if descuento > 0:
        ticket += f"Descuento: -${venta['descuento']}\n"
    ticket += f"IVA: ${venta['impuesto']}\n"
    ticket += f"TOTAL: ${venta['total']}\n"
    return ticket


def registrar_venta(
    codigo: str | None, cantidad: int | None, cliente: str | None = ""
) -> dict | None:
    """Registra una venta completa.

    Esta funcion hace de todo: valida los datos, calcula descuentos e
    impuestos, descuenta el stock, genera el folio, arma el ticket en
    texto y guarda el registro en la lista de ventas. Si algo falla
    regresa None y deja el motivo en ultimo_error.
    """
    global contador_ventas, ultimo_error
    if codigo in (None, ""):
        ultimo_error = "codigo vacio"
        return None
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return None
    if cantidad is None or not cantidad > 0:
        ultimo_error = "cantidad invalida"
        return None
    producto =INVENTARIO[codigo]
    if producto["stock"] < cantidad:
        ultimo_error = "stock insuficiente"
        return None
    subtotal = producto["precio"] * cantidad
    descuento, impuesto, total = _calcular_montos(subtotal, cliente)
    # descontar del inventario
    producto["stock"] = producto["stock"] - cantidad
    contador_ventas = contador_ventas + 1
    venta = {}
    venta["folio"] = contador_ventas
    venta["codigo"] = codigo
    venta["nombre"] = producto["nombre"]
    venta["cantidad"] = cantidad
    venta["subtotal"] = round(subtotal, 2)
    venta["descuento"] = round(descuento, 2)
    venta["impuesto"] = round(impuesto, 2)
    venta["total"] = total
    venta["cliente"] = cliente
    venta["fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    venta["ticket"] = _construir_ticket(venta, descuento)
    VENTAS.append(venta)
    return venta


def cotizar(codigo: str, cantidad: int | None) -> float | None:
    """Calcula cuanto costaria una compra sin registrar la venta."""
    global ultimo_error
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return None
    if cantidad is None or not cantidad > 0:
        ultimo_error = "cantidad invalida"
        return None
    aux =INVENTARIO[codigo]["precio"] * cantidad
    desc = _descuento_por_volumen(aux)
    base = aux - desc
    total = base + base * TASA_IVA
    return round(total, 2)
