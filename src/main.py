"""Punto de entrada del gestor de tienda (menu interactivo en consola)."""

import almacen
import gestor
import reportes

ARCHIVO = "datos_ejemplo.json"


def pedir_numero(mensaje: str) -> float:
    """Pide un numero al usuario hasta que escriba algo valido."""
    while True:
        respuesta = input(mensaje)
        try:
            return float(respuesta)
        except ValueError:
            print("Eso no es un numero, intenta de nuevo.")


def _opcion_agregar_producto() -> None:
    """Opcion 1: pide los datos y da de alta un producto."""
    codigo = input("Codigo: ")
    nombre = input("Nombre: ")
    precio = pedir_numero("Precio: ")
    stock = int(pedir_numero("Stock inicial: "))
    if gestor.agregarProducto(codigo, nombre, precio, stock):
        print("Producto agregado.")
    else:
        print("Error:", gestor.ultimo_error)


def _opcion_registrar_venta() -> None:
    """Opcion 2: pide los datos y registra una venta."""
    codigo = input("Codigo del producto: ")
    cantidad = int(pedir_numero("Cantidad: "))
    cliente = input("Codigo de cliente (enter si no tiene): ")
    venta = gestor.registrar_venta(codigo, cantidad, cliente)
    if venta is not None:
        print(venta["ticket"])
    else:
        print("Error:", gestor.ultimo_error)


def _opcion_cotizar() -> None:
    """Opcion 3: pide los datos y muestra el total estimado."""
    codigo = input("Codigo del producto: ")
    cantidad = int(pedir_numero("Cantidad: "))
    total = gestor.cotizar(codigo, cantidad)
    if total is not None:
        print(f"Total estimado (con IVA): ${total}")
    else:
        print("Error:", gestor.ultimo_error)


def _opcion_reporte_inventario() -> None:
    """Opcion 4: imprime el reporte de inventario."""
    reportes.reporte_inventario()


def _opcion_resumen_ventas() -> None:
    """Opcion 5: imprime el resumen de ventas."""
    reportes.resumen_ventas()


def _opcion_mas_vendidos() -> None:
    """Opcion 6: imprime los productos mas vendidos."""
    for codigo, unidades in reportes.mas_vendidos():
        print(codigo, "->", unidades, "unidades")


def _opcion_stock_bajo() -> None:
    """Opcion 7: avisa de los productos con stock bajo."""
    bajos = reportes.productos_stock_bajo()
    if not bajos:
        print("No hay productos con stock bajo.")
        return
    for producto in bajos:
        print("OJO:", producto["nombre"], "solo tiene", producto["stock"], "unidades")


OPCIONES = {
    "1": _opcion_agregar_producto,
    "2": _opcion_registrar_venta,
    "3": _opcion_cotizar,
    "4": _opcion_reporte_inventario,
    "5": _opcion_resumen_ventas,
    "6": _opcion_mas_vendidos,
    "7": _opcion_stock_bajo,
}


def _mostrar_opciones() -> None:
    """Imprime el menu de opciones."""
    print("")
    print("1) Agregar producto")
    print("2) Registrar venta")
    print("3) Cotizar")
    print("4) Reporte de inventario")
    print("5) Resumen de ventas")
    print("6) Mas vendidos")
    print("7) Alertas de stock bajo")
    print("8) Guardar y salir")


def menu() -> None:
    """Muestra el menu en bucle hasta que el usuario elige guardar y salir."""
    print("Bienvenido al gestor de la tienda La Esquina")
    if almacen.hay_archivo(ARCHIVO):
        almacen.cargar_datos(ARCHIVO)
        print("Datos cargados de", ARCHIVO)
    while True:
        _mostrar_opciones()
        opcion = input("Opcion: ")
        if opcion == "8":
            almacen.guardar_datos(ARCHIVO)
            print("Datos guardados. Hasta luego.")
            break
        accion = OPCIONES.get(opcion)
        if accion is None:
            print("Opcion no valida.")
        else:
            accion()


if __name__ == "__main__":
    menu()
