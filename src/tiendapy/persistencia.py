"""Lectura y escritura de los archivos de datos."""

import datetime
import os

from tiendapy.validaciones import (
    validar_categoria,
    validar_codigo,
    validar_decimal_positivo,
    validar_entero_no_negativo,
    validar_entero_positivo,
    validar_texto,
)

# Las rutas son relativas: el programa se ejecuta desde la raiz del proyecto.
CARPETA_DATOS = "data"
RUTA_INVENTARIO = "data/inventario.txt"
RUTA_VENTAS = "data/ventas.txt"
RUTA_OMITIDAS = "data/inventario_omitidas.txt"


# ---------------------------------------------------------------------------
# Inventario
# ---------------------------------------------------------------------------


def linea_a_producto(linea):
    """Convierte una linea del archivo en un diccionario de producto."""
    campos = linea.split("|")
    if len(campos) != 7:
        raise ValueError("Debe tener 7 campos separados por |.")

    # El stock puede ser cero: asi queda guardado un producto agotado.
    return {
        "codigo": validar_codigo(campos[0]),
        "nombre": validar_texto(campos[1]),
        "categoria": validar_categoria(campos[2]),
        "precio": validar_decimal_positivo(campos[3]),
        "stock": validar_entero_no_negativo(campos[4]),
        "stock_minimo": validar_entero_no_negativo(campos[5]),
        "proveedor": validar_texto(campos[6]),
    }


def producto_a_linea(producto):
    """Convierte un producto en una linea para el archivo."""
    return (
        f"{producto['codigo']}|{producto['nombre']}|{producto['categoria']}|"
        f"{producto['precio']}|{producto['stock']}|{producto['stock_minimo']}|"
        f"{producto['proveedor']}"
    )


def guardar_omitidas(lineas):
    """Aparta las lineas corruptas para que no se pierdan al guardar."""
    with open(RUTA_OMITIDAS, "a", encoding="utf-8") as archivo:
        for linea in lineas:
            archivo.write(linea + "\n")


def cargar_inventario():
    """Devuelve el inventario como diccionario: {codigo: producto}."""
    inventario = {}
    omitidas = []

    try:
        # errors="replace" evita que un caracter danado detenga la lectura.
        with open(RUTA_INVENTARIO, "r", encoding="utf-8", errors="replace") as archivo:
            for numero, linea in enumerate(archivo, start=1):
                linea = linea.strip()
                if linea == "":
                    continue
                try:
                    producto = linea_a_producto(linea)
                    if producto["codigo"] in inventario:
                        raise ValueError("El código está repetido.")
                    inventario[producto["codigo"]] = producto
                except ValueError as error:
                    print(f"Advertencia: se omitió la línea {numero} del inventario. {error}")
                    omitidas.append(linea)
    except FileNotFoundError:
        print(f"No se encontró {RUTA_INVENTARIO}. Se inicia con el inventario vacío.")

    if omitidas:
        guardar_omitidas(omitidas)
        print(f"Las líneas omitidas se copiaron en {RUTA_OMITIDAS}.")
    return inventario


def guardar_inventario(inventario):
    """Reescribe el archivo de inventario con los datos actuales."""
    os.makedirs(CARPETA_DATOS, exist_ok=True)

    # Se escribe primero en un archivo temporal. Si algo falla a mitad de
    # camino, el inventario original sigue intacto.
    ruta_temporal = RUTA_INVENTARIO + ".tmp"
    with open(ruta_temporal, "w", encoding="utf-8") as archivo:
        for producto in inventario.values():
            archivo.write(producto_a_linea(producto) + "\n")
    os.replace(ruta_temporal, RUTA_INVENTARIO)


# ---------------------------------------------------------------------------
# Ventas
# ---------------------------------------------------------------------------


def linea_a_venta(linea):
    """Convierte una linea del historial en un diccionario de venta."""
    campos = linea.split("|")
    if len(campos) != 3:
        raise ValueError("Debe tener 3 campos separados por |.")

    # fromisoformat lanza ValueError si la fecha no existe o esta mal escrita.
    fecha = datetime.date.fromisoformat(campos[0]).isoformat()
    total = validar_decimal_positivo(campos[1])

    items = {}
    for item in campos[2].split(";"):
        partes = item.split(":")
        if len(partes) != 2:
            raise ValueError("Cada producto debe tener el formato codigo:cantidad.")
        codigo = validar_codigo(partes[0])
        cantidad = validar_entero_positivo(partes[1])
        items[codigo] = items.get(codigo, 0) + cantidad

    return {"fecha": fecha, "total": total, "items": items}


def venta_a_linea(venta):
    """Convierte una venta en una linea para el historial."""
    detalle = []
    for codigo, cantidad in venta["items"].items():
        detalle.append(f"{codigo}:{cantidad}")
    return f"{venta['fecha']}|{venta['total']}|{';'.join(detalle)}"


def cargar_ventas():
    """Devuelve el historial como una lista de ventas."""
    ventas = []

    try:
        with open(RUTA_VENTAS, "r", encoding="utf-8", errors="replace") as archivo:
            for numero, linea in enumerate(archivo, start=1):
                linea = linea.strip()
                if linea == "":
                    continue
                try:
                    ventas.append(linea_a_venta(linea))
                except ValueError as error:
                    print(f"Advertencia: se omitió la línea {numero} de las ventas. {error}")
    except FileNotFoundError:
        # Es normal que todavia no exista: se crea con la primera venta.
        pass

    return ventas


def registrar_venta(venta):
    """Agrega una venta al final del historial."""
    os.makedirs(CARPETA_DATOS, exist_ok=True)
    with open(RUTA_VENTAS, "a", encoding="utf-8") as archivo:
        archivo.write(venta_a_linea(venta) + "\n")
