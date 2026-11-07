"""Alertas de stock y cierre del dia."""

import datetime

from tabulate import tabulate

from tiendapy.inventario import formatear_dinero
from tiendapy.persistencia import cargar_ventas


# ---------------------------------------------------------------------------
# Alertas de stock
# ---------------------------------------------------------------------------


def productos_en_alerta(inventario):
    """Devuelve los productos con stock menor o igual al minimo."""
    alertas = []
    for producto in inventario.values():
        if producto["stock"] <= producto["stock_minimo"]:
            alertas.append(producto)
    return alertas


def agrupar_por_proveedor(productos):
    """Devuelve un diccionario: {proveedor: lista de productos}."""
    grupos = {}
    for producto in productos:
        proveedor = producto["proveedor"]
        if proveedor not in grupos:
            grupos[proveedor] = []
        grupos[proveedor].append(producto)
    return grupos


def estado_producto(producto):
    """Indica si el producto esta agotado o solo tiene poco stock."""
    if producto["stock"] == 0:
        return "AGOTADO"
    return "Stock bajo"


def mostrar_alertas(inventario):
    """Imprime los productos por pedir, separados por proveedor."""
    grupos = agrupar_por_proveedor(productos_en_alerta(inventario))
    if len(grupos) == 0:
        print("No hay productos con stock bajo.")
        return

    for proveedor in sorted(grupos):
        filas = []
        for producto in grupos[proveedor]:
            filas.append(
                [
                    producto["codigo"],
                    producto["nombre"],
                    producto["stock"],
                    producto["stock_minimo"],
                    estado_producto(producto),
                ]
            )
        print(f"\nProveedor: {proveedor}")
        print(
            tabulate(
                filas,
                headers=["Código", "Nombre", "Stock", "Mínimo", "Estado"],
                colalign=("left", "left", "right", "right", "left"),
                disable_numparse=True,
            )
        )


# ---------------------------------------------------------------------------
# Cierre del dia
# ---------------------------------------------------------------------------


def filtrar_por_fecha(ventas, fecha):
    """Devuelve solo las ventas de una fecha."""
    del_dia = []
    for venta in ventas:
        if venta["fecha"] == fecha:
            del_dia.append(venta)
    return del_dia


def contar_unidades(ventas):
    """Devuelve las unidades vendidas de cada producto: {codigo: unidades}."""
    unidades = {}
    for venta in ventas:
        for codigo, cantidad in venta["items"].items():
            unidades[codigo] = unidades.get(codigo, 0) + cantidad
    return unidades


def buscar_mas_vendidos(unidades):
    """Devuelve los codigos con mas unidades: puede haber empate."""
    if len(unidades) == 0:
        return []

    maximo = max(unidades.values())
    mas_vendidos = []
    for codigo, cantidad in unidades.items():
        if cantidad == maximo:
            mas_vendidos.append(codigo)
    return mas_vendidos


def buscar_sin_ventas(inventario, unidades):
    """Devuelve los codigos que estan en inventario y no se vendieron."""
    return sorted(set(inventario) - set(unidades))


def contar_por_categoria(inventario, unidades):
    """Devuelve las unidades vendidas por categoria: {categoria: unidades}."""
    categorias = {}
    for codigo, cantidad in unidades.items():
        # Un producto eliminado sigue en el historial, pero ya no se sabe
        # a que categoria pertenecia.
        if codigo in inventario:
            categoria = inventario[codigo]["categoria"]
            categorias[categoria] = categorias.get(categoria, 0) + cantidad
    return categorias


def calcular_cierre(inventario, ventas, fecha):
    """Calcula los datos del cierre de una fecha."""
    del_dia = filtrar_por_fecha(ventas, fecha)
    unidades = contar_unidades(del_dia)

    total = 0
    for venta in del_dia:
        total += venta["total"]

    # Si no hubo ventas no se puede dividir entre cero.
    ticket_promedio = 0
    if len(del_dia) > 0:
        ticket_promedio = total / len(del_dia)

    return {
        "fecha": fecha,
        "total": total,
        "transacciones": len(del_dia),
        "ticket_promedio": ticket_promedio,
        "unidades": unidades,
        "mas_vendidos": buscar_mas_vendidos(unidades),
        "sin_ventas": buscar_sin_ventas(inventario, unidades),
        "categorias": contar_por_categoria(inventario, unidades),
    }


def nombre_producto(inventario, codigo):
    """Devuelve el nombre del producto, aunque ya se haya eliminado."""
    if codigo in inventario:
        return inventario[codigo]["nombre"]
    return f"{codigo} (eliminado)"


def mostrar_cierre(inventario):
    """Imprime el cierre del dia de hoy."""
    hoy = datetime.date.today().isoformat()
    cierre = calcular_cierre(inventario, cargar_ventas(), hoy)

    print(f"\nCierre del día {cierre['fecha']}")
    print(f"Total vendido: {formatear_dinero(cierre['total'])}")
    print(f"Número de ventas: {cierre['transacciones']}")
    print(f"Ticket promedio: {formatear_dinero(cierre['ticket_promedio'])}")

    if cierre["transacciones"] == 0:
        print("Producto más vendido: ninguno")
        print("Categorías con movimiento: ninguna")
    else:
        for codigo in cierre["mas_vendidos"]:
            nombre = nombre_producto(inventario, codigo)
            print(f"Producto más vendido: {nombre} ({cierre['unidades'][codigo]} und.)")

        print("Categorías con movimiento:")
        for categoria in sorted(cierre["categorias"]):
            print(f"  {categoria}: {cierre['categorias'][categoria]} und.")

    if len(cierre["sin_ventas"]) == 0:
        print("Todos los productos tuvieron ventas.")
    else:
        filas = []
        for codigo in cierre["sin_ventas"]:
            filas.append([codigo, inventario[codigo]["nombre"]])
        print("\nProductos sin ventas:")
        print(tabulate(filas, headers=["Código", "Nombre"], disable_numparse=True))
