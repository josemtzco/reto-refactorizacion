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


def reiniciar_sistema():
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


def eliminar_producto(codigo):
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


def registrar_venta(codigo, cantidad, cliente=""):
    """Registra una venta completa.

    Esta funcion hace de todo: valida los datos, calcula descuentos e
    impuestos, descuenta el stock, genera el folio, arma el ticket en
    texto y guarda el registro en la lista de ventas. Si algo falla
    regresa None y deja el motivo en ultimo_error.
    """
    global contador_ventas, ultimo_error
    temp2 = None
    if codigo is not None and codigo != "":
        if codigo in INVENTARIO:
            if cantidad is not None and cantidad > 0:
                if INVENTARIO[codigo]["stock"] >= cantidad:
                    temp2 = INVENTARIO[codigo]
                else:
                    ultimo_error = "stock insuficiente"
                    return None
            else:
                ultimo_error = "cantidad invalida"
                return None
        else:
            ultimo_error = "producto no existe"
            return None
    else:
        ultimo_error = "codigo vacio"
        return None
    # calculo del subtotal
    aux = temp2["precio"] * cantidad
    # descuentos por volumen de compra
    desc = 0
    if aux >= UMBRAL_DESCUENTO_ALTO:
        desc = aux * TASA_DESCUENTO_ALTO
    else:
        if aux >= UMBRAL_DESCUENTO_MEDIO:
            desc = aux * TASA_DESCUENTO_MEDIO
        else:
            desc = 0
    # los clientes cuyo codigo empieza con VIP tienen un extra,
    # pero solo si su compra (ya con descuento) pasa de cierto monto
    if cliente != "" and cliente is not None:
        if len(cliente) >= 3:
            if cliente[0:3] == PREFIJO_VIP:
                if aux - desc > MONTO_MINIMO_VIP:
                    desc = desc + aux * TASA_EXTRA_VIP
    base = aux - desc
    impuesto = base * TASA_IVA
    total = round(base + impuesto, 2)
    # descontar del inventario
    temp2["stock"] = temp2["stock"] - cantidad
    contador_ventas = contador_ventas + 1
    venta = {}
    venta["folio"] = contador_ventas
    venta["codigo"] = codigo
    venta["nombre"] = temp2["nombre"]
    venta["cantidad"] = cantidad
    venta["subtotal"] = round(aux, 2)
    venta["descuento"] = round(desc, 2)
    venta["impuesto"] = round(impuesto, 2)
    venta["total"] = total
    venta["cliente"] = cliente
    venta["fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # armar el ticket en texto plano
    t = ""
    t = t + "TIENDA LA ESQUINA\n"
    t = t + "----------------------------\n"
    t = t + "Folio: " + str(venta["folio"]) + "\n"
    t = t + venta["nombre"] + " x" + str(cantidad) + "\n"
    t = t + "Subtotal: $" + str(venta["subtotal"]) + "\n"
    if desc > 0:
        t = t + "Descuento: -$" + str(venta["descuento"]) + "\n"
    t = t + "IVA: $" + str(venta["impuesto"]) + "\n"
    t = t + "TOTAL: $" + str(venta["total"]) + "\n"
    venta["ticket"] = t
    VENTAS.append(venta)
    return venta


def cotizar(codigo, cantidad):
    """Calcula cuanto costaria una compra sin registrar la venta."""
    global ultimo_error
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return None
    if cantidad is None or cantidad <= 0:
        ultimo_error = "cantidad invalida"
        return None
    aux = INVENTARIO[codigo]["precio"] * cantidad
    desc = 0
    if aux >= UMBRAL_DESCUENTO_ALTO:
        desc = aux * TASA_DESCUENTO_ALTO
    else:
        if aux >= UMBRAL_DESCUENTO_MEDIO:
            desc = aux * TASA_DESCUENTO_MEDIO
    base = aux - desc
    total = base + base * TASA_IVA
    return round(total, 2)
