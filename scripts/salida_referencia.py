"""Genera una salida determinista del comportamiento de src/ para compararla.

Uso: python scripts/salida_referencia.py <archivo_destino>

La salida se escribe desde Python en UTF-8 (no con ">") y nunca incluye la
clave "fecha" de las ventas, porque cambia en cada corrida.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))

import almacen
import gestor
import reportes

LINEAS: list[str] = []


def hay_archivo(ruta: str) -> bool:
    """Llama a hayArchivo o a hay_archivo, segun el nombre vigente."""
    funcion = getattr(almacen, "hay_archivo", None) or almacen.hayArchivo
    return funcion(ruta)


def escribir(texto: str) -> None:
    """Agrega una linea a la salida de referencia."""
    LINEAS.append(texto)


def sin_fecha(venta: dict | None) -> dict | None:
    """Regresa una copia de la venta sin la clave 'fecha'."""
    if venta is None:
        return None
    return {clave: valor for clave, valor in venta.items() if clave != "fecha"}


def preparar_inventario() -> None:
    """Reinicia el sistema y da de alta los productos de las pruebas."""
    gestor.reiniciar_sistema()
    gestor.agregarProducto("P1", "Cafe Molido", 100.0, 100)
    gestor.agregarProducto("P2", "Azucar", 32.5, 40)
    gestor.agregarProducto("P3", "Leche", 3.0, 3)
    gestor.agregarProducto("P4", "Galletas", 250.0, 50)


def bloque_ventas() -> None:
    """Tickets y ventas: bordes del descuento y casos VIP."""
    escribir("== VENTAS ==")
    casos = [
        ("P1", 1, ""),
        ("P1", 4, ""),
        ("P1", 5, ""),
        ("P1", 10, ""),
        ("P1", 6, "VIP01"),
        ("P1", 2, "VIP01"),
        ("P4", 1, "VIP01"),
        ("P4", 3, "VIP01"),
        ("P1", 3, "VIP01"),
        ("P1", 6, "vip01"),
        ("P1", 6, "VI"),
        ("P1", 6, ""),
        ("P1", 6, None),
        ("P2", 7, "VIP99"),
        ("P2", 3, "Ana"),
    ]
    for codigo, cantidad, cliente in casos:
        preparar_inventario()
        venta = gestor.registrar_venta(codigo, cantidad, cliente)
        escribir(f"venta{(codigo, cantidad, cliente)!r} -> {sin_fecha(venta)!r}")
        if venta is not None:
            escribir("ticket:\n" + venta["ticket"])
        escribir(f"ultimo_error={gestor.ultimo_error!r}")
        escribir(f"stock={gestor.INVENTARIO[codigo]['stock']!r}")
    # Subtotales exactos
    preparar_inventario()
    gestor.agregarProducto("E1", "Exacto 200", 200.0, 10)
    gestor.agregarProducto("E2", "Exacto 500", 500.0, 10)
    gestor.agregarProducto("E3", "Exacto 1000", 1000.0, 10)
    gestor.agregarProducto("E4", "Menor 500", 499.99, 10)
    for codigo in ("E1", "E2", "E3", "E4"):
        for cliente in ("", "VIP01"):
            preparar_inventario()
            gestor.agregarProducto("E1", "Exacto 200", 200.0, 10)
            gestor.agregarProducto("E2", "Exacto 500", 500.0, 10)
            gestor.agregarProducto("E3", "Exacto 1000", 1000.0, 10)
            gestor.agregarProducto("E4", "Menor 500", 499.99, 10)
            venta = gestor.registrar_venta(codigo, 1, cliente)
            escribir(f"exacto{(codigo, cliente)!r} -> {sin_fecha(venta)!r}")
            if venta is not None:
                escribir("ticket:\n" + venta["ticket"])


def bloque_errores_venta() -> None:
    """Errores de registrar_venta y cotizar, incluido el orden de validacion."""
    escribir("== ERRORES DE VENTA Y COTIZACION ==")
    casos = [
        ("", 1),
        (None, 1),
        ("", 0),
        ("NOEXISTE", 1),
        ("NOEXISTE", 0),
        ("P1", 0),
        ("P1", -2),
        ("P1", None),
        ("P3", 99),
    ]
    for codigo, cantidad in casos:
        preparar_inventario()
        venta = gestor.registrar_venta(codigo, cantidad)
        escribir(
            f"registrar_venta{(codigo, cantidad)!r} -> {venta!r} "
            f"error={gestor.ultimo_error!r}"
        )
        preparar_inventario()
        cotizacion = gestor.cotizar(codigo, cantidad)
        escribir(
            f"cotizar{(codigo, cantidad)!r} -> {cotizacion!r} "
            f"error={gestor.ultimo_error!r}"
        )


def bloque_cotizar() -> None:
    """Cotizaciones con los mismos montos (cotizar no aplica VIP)."""
    escribir("== COTIZAR ==")
    preparar_inventario()
    for codigo, cantidad in [("P1", 1), ("P1", 4), ("P1", 5), ("P1", 10), ("P4", 2)]:
        escribir(f"cotizar{(codigo, cantidad)!r} -> {gestor.cotizar(codigo, cantidad)!r}")
    gestor.agregarProducto("E1", "Exacto 200", 200.0, 10)
    gestor.agregarProducto("E2", "Exacto 500", 500.0, 10)
    gestor.agregarProducto("E3", "Exacto 1000", 1000.0, 10)
    gestor.agregarProducto("E4", "Menor 500", 499.99, 10)
    for codigo in ("E1", "E2", "E3", "E4"):
        escribir(f"cotizar{(codigo, 1)!r} -> {gestor.cotizar(codigo, 1)!r}")
    escribir(f"cotizar('', 1) -> {gestor.cotizar('', 1)!r} {gestor.ultimo_error!r}")


def bloque_productos() -> None:
    """Alta, baja, actualizacion y busqueda de productos."""
    escribir("== PRODUCTOS ==")
    gestor.reiniciar_sistema()
    intentos = [
        ("", "Sin codigo", 10.0, 1),
        (None, "Sin codigo", 10.0, 1),
        ("", "Sin codigo y precio malo", -1.0, 1),
        ("A1", "Cafe", 10.0, 5),
        ("A1", "Repetido", 10.0, 5),
        ("A1", "Repetido y precio malo", -1, -1),
        ("A2", "Precio cero", 0, 5),
        ("A3", "Precio negativo", -3.0, 5),
        ("A4", "Stock negativo", 3.0, -1),
        ("A5", "Precio y stock malos", -3.0, -1),
        ("A6", "Stock cero", 3.0, 0),
        (0, "Codigo cero", 3.0, 1),
    ]
    for intento in intentos:
        gestor.ultimo_error = ""
        resultado = gestor.agregarProducto(*intento)
        escribir(f"agregarProducto{intento!r} -> {resultado!r} {gestor.ultimo_error!r}")
    escribir(f"INVENTARIO={gestor.INVENTARIO!r}")
    for codigo, cantidad in [("A1", 5), ("A1", -5), ("A1", -50), ("ZZ", 1)]:
        gestor.ultimo_error = ""
        resultado = gestor.actualizar_stock(codigo, cantidad)
        escribir(
            f"actualizar_stock{(codigo, cantidad)!r} -> {resultado!r} "
            f"{gestor.ultimo_error!r} stock={gestor.INVENTARIO.get('A1')!r}"
        )
    for codigo in ("A6", "A6", ""):
        gestor.ultimo_error = ""
        resultado = gestor.eliminar_producto(codigo)
        escribir(f"eliminar_producto({codigo!r}) -> {resultado!r} {gestor.ultimo_error!r}")
    preparar_inventario()
    for texto in ("cafe", "CAFE", "cAfE", "a", "", "xyz", "LECHE"):
        escribir(f"buscarProducto({texto!r}) -> {gestor.buscarProducto(texto)!r}")


def bloque_reportes() -> None:
    """Reportes con ventas, incluido un empate en mas_vendidos."""
    escribir("== REPORTES ==")
    gestor.reiniciar_sistema()
    escribir(f"inventario vacio: {reportes.reporte_inventario()!r}")
    escribir(f"resumen vacio: {reportes.resumen_ventas()!r}")
    escribir(f"mas_vendidos vacio: {reportes.mas_vendidos()!r}")
    escribir(f"total vacio: {reportes.total_vendido()!r}")
    preparar_inventario()
    for codigo, cantidad, cliente in [
        ("P1", 5, ""),
        ("P2", 5, "VIP01"),
        ("P4", 2, ""),
        ("P1", 1, ""),
        ("P2", 1, ""),
        ("P4", 4, ""),
        ("P3", 1, ""),
    ]:
        gestor.registrar_venta(codigo, cantidad, cliente)
    escribir(f"reporte_inventario: {reportes.reporte_inventario()!r}")
    escribir(f"resumen_ventas: {reportes.resumen_ventas()!r}")
    escribir(f"mas_vendidos(): {reportes.mas_vendidos()!r}")
    escribir(f"mas_vendidos(1): {reportes.mas_vendidos(1)!r}")
    escribir(f"mas_vendidos(10): {reportes.mas_vendidos(10)!r}")
    escribir(f"total_vendido: {reportes.total_vendido()!r}")
    escribir(f"stock_bajo: {reportes.productos_stock_bajo()!r}")
    # Empate explicito de unidades
    preparar_inventario()
    for codigo, cantidad in [("P1", 2), ("P2", 2), ("P4", 2), ("P3", 1)]:
        gestor.registrar_venta(codigo, cantidad)
    escribir(f"mas_vendidos con empate: {reportes.mas_vendidos()!r}")


def bloque_almacen() -> None:
    """Errores de carga y ida y vuelta del JSON."""
    escribir("== ALMACEN ==")
    with tempfile.TemporaryDirectory() as carpeta:
        ruta_inexistente = os.path.join(carpeta, "no_existe.json")
        gestor.reiniciar_sistema()
        escribir(f"cargar inexistente: {almacen.cargar_datos(ruta_inexistente)!r}")
        escribir(f"error={gestor.ultimo_error!r}")
        escribir(f"hayArchivo inexistente: {hay_archivo(ruta_inexistente)!r}")

        ruta_malo = os.path.join(carpeta, "malo.json")
        with open(ruta_malo, "w", encoding="utf-8") as archivo:
            archivo.write("{esto no es json")
        gestor.reiniciar_sistema()
        escribir(f"cargar json invalido: {almacen.cargar_datos(ruta_malo)!r}")
        escribir(f"error={gestor.ultimo_error!r}")

        ruta_bytes = os.path.join(carpeta, "bytes.json")
        with open(ruta_bytes, "wb") as archivo:
            archivo.write(b"\xff\xfe")
        gestor.reiniciar_sistema()
        escribir(f"cargar bytes invalidos: {almacen.cargar_datos(ruta_bytes)!r}")
        escribir(f"error={gestor.ultimo_error!r}")

        # Ida y vuelta
        preparar_inventario()
        gestor.registrar_venta("P1", 6, "VIP01")
        gestor.registrar_venta("P4", 1)
        ruta_ok = os.path.join(carpeta, "datos.json")
        escribir(f"guardar: {almacen.guardar_datos(ruta_ok)!r}")
        escribir(f"hayArchivo existente: {hay_archivo(ruta_ok)!r}")
        with open(ruta_ok, encoding="utf-8") as archivo:
            guardado = json.load(archivo)
        for venta in guardado["ventas"]:
            venta.pop("fecha", None)
        escribir(f"json guardado: {json.dumps(guardado, sort_keys=True)}")
        with open(ruta_ok, encoding="utf-8") as archivo:
            texto_crudo = archivo.read()
        escribir(f"claves del json: {list(guardado.keys())!r}")
        escribir(f"json con indent=2: {texto_crudo.startswith('{' + chr(10) + '  ')}")
        gestor.reiniciar_sistema()
        inventario_vivo = gestor.INVENTARIO
        ventas_vivas = gestor.VENTAS
        escribir(f"cargar: {almacen.cargar_datos(ruta_ok)!r}")
        escribir(f"mismo objeto INVENTARIO: {inventario_vivo is gestor.INVENTARIO}")
        escribir(f"mismo objeto VENTAS: {ventas_vivas is gestor.VENTAS}")
        escribir(f"INVENTARIO={gestor.INVENTARIO!r}")
        escribir(f"VENTAS={[sin_fecha(v) for v in gestor.VENTAS]!r}")
        siguiente = gestor.registrar_venta("P2", 1)
        escribir(f"folio siguiente: {siguiente['folio']!r}")

        # JSON sin la clave "contador"
        ruta_sin_contador = os.path.join(carpeta, "sin_contador.json")
        with open(ruta_sin_contador, "w", encoding="utf-8") as archivo:
            json.dump({"inventario": {}, "ventas": []}, archivo)
        gestor.reiniciar_sistema()
        gestor.registrar_venta("X", 1)
        escribir(f"cargar sin contador: {almacen.cargar_datos(ruta_sin_contador)!r}")
        gestor.agregarProducto("Q", "Q", 1.0, 1)
        escribir(f"folio tras sin contador: {gestor.registrar_venta('Q', 1)['folio']!r}")


ENTRADA_MENU = "\n".join(
    [
        "1", "N01", "Producto nuevo", "abc", "12.5", "7",
        "1", "N01", "Duplicado", "5", "3",
        "1", "", "Sin codigo", "5", "3",
        "1", "N02", "Precio malo", "-5", "3",
        "2", "A001", "2", "",
        "2", "A001", "6", "VIP01",
        "2", "A001", "xyz", "0", "",
        "2", "A001", "0", "",
        "2", "NOEXISTE", "1", "",
        "2", "A003", "50", "",
        "3", "A001", "2",
        "3", "A001", "-1",
        "3", "NOEXISTE", "1",
        "4", "5", "6", "7",
        "9", "abc", "",
        "8",
    ]
) + "\n"


def bloque_menu() -> None:
    """Ejecuta main.py con entradas por stdin sobre una copia de los datos."""
    escribir("== MENU ==")
    with tempfile.TemporaryDirectory() as carpeta:
        shutil.copy(os.path.join(RAIZ, "datos_ejemplo.json"), carpeta)
        entorno = dict(os.environ, PYTHONIOENCODING="utf-8")
        resultado = subprocess.run(
            [sys.executable, os.path.join(RAIZ, "src", "main.py")],
            input=ENTRADA_MENU,
            cwd=carpeta,
            env=entorno,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        escribir(f"returncode={resultado.returncode!r}")
        escribir("stdout:\n" + resultado.stdout)
        escribir("stderr:\n" + resultado.stderr)
        with open(
            os.path.join(carpeta, "datos_ejemplo.json"), encoding="utf-8"
        ) as archivo:
            guardado = json.load(archivo)
        for venta in guardado["ventas"]:
            venta.pop("fecha", None)
        escribir(f"json final: {json.dumps(guardado, sort_keys=True)}")


def main() -> None:
    """Corre todos los bloques y escribe el resultado en el archivo destino."""
    if len(sys.argv) != 2:
        print("Uso: python scripts/salida_referencia.py <archivo_destino>")
        sys.exit(1)
    bloque_ventas()
    bloque_errores_venta()
    bloque_cotizar()
    bloque_productos()
    bloque_reportes()
    bloque_almacen()
    bloque_menu()
    with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as archivo:
        archivo.write("\n".join(LINEAS) + "\n")


if __name__ == "__main__":
    main()
