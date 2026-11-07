"""Carrito de compras, descuentos, pago y cambio."""

import datetime

from tabulate import tabulate

from tiendapy.inventario import buscar_producto, formatear_dinero
from tiendapy.persistencia import guardar_inventario, registrar_venta
from tiendapy.validaciones import (
    pedir_confirmacion,
    pedir_dato,
    pedir_opcion,
    validar_codigo,
    validar_decimal_positivo,
    validar_entero_positivo,
)

UMBRAL_DESCUENTO_5 = 50000
UMBRAL_DESCUENTO_10 = 100000
PREGUNTA_PAGO = "Pago en COP (sin puntos ni comas): "


# ---------------------------------------------------------------------------
# Logica del negocio. El carrito es un diccionario: {codigo: cantidad}.
# ---------------------------------------------------------------------------


def agregar_al_carrito(inventario, carrito, codigo, cantidad):
    """Suma un producto al carrito si hay stock suficiente."""
    producto = buscar_producto(inventario, codigo)
    # Se cuenta lo que ya estaba en el carrito: el mismo producto puede
    # agregarse varias veces y entre todas no pueden superar el stock.
    pedido = carrito.get(codigo, 0) + cantidad
    if pedido > producto["stock"]:
        raise ValueError(
            f"Stock insuficiente de {producto['nombre']}: "
            f"hay {producto['stock']} y se piden {pedido}."
        )
    carrito[codigo] = pedido


def calcular_subtotal(inventario, carrito):
    """Suma el valor de todos los productos del carrito."""
    subtotal = 0
    for codigo, cantidad in carrito.items():
        subtotal += inventario[codigo]["precio"] * cantidad
    return round(subtotal, 2)


def calcular_porcentaje_descuento(subtotal):
    """Devuelve el descuento que corresponde al subtotal."""
    if subtotal >= UMBRAL_DESCUENTO_10:
        return 0.10
    if subtotal >= UMBRAL_DESCUENTO_5:
        return 0.05
    return 0


def calcular_total(subtotal):
    """Aplica el descuento y redondea al peso, porque no hay centavos."""
    porcentaje = calcular_porcentaje_descuento(subtotal)
    return float(round(subtotal * (1 - porcentaje)))


def calcular_cambio(total, pago):
    """Devuelve el cambio, o lanza ValueError si el pago no alcanza."""
    if pago < total:
        raise ValueError(
            f"El pago de {formatear_dinero(pago)} no alcanza "
            f"para el total de {formatear_dinero(total)}."
        )
    return pago - total


def descontar_stock(inventario, carrito):
    """Resta del inventario lo que se vendio."""
    for codigo, cantidad in carrito.items():
        inventario[codigo]["stock"] -= cantidad


# ---------------------------------------------------------------------------
# Conversacion con el usuario
# ---------------------------------------------------------------------------


def mostrar_carrito(inventario, carrito):
    """Imprime el detalle del carrito con subtotal, descuento y total."""
    filas = []
    for codigo, cantidad in carrito.items():
        producto = inventario[codigo]
        filas.append(
            [
                producto["nombre"],
                cantidad,
                formatear_dinero(producto["precio"]),
                formatear_dinero(producto["precio"] * cantidad),
            ]
        )
    print(
        tabulate(
            filas,
            headers=["Producto", "Cantidad", "Precio", "Valor"],
            colalign=("left", "right", "right", "right"),
            disable_numparse=True,
        )
    )

    subtotal = calcular_subtotal(inventario, carrito)
    porcentaje = calcular_porcentaje_descuento(subtotal)
    total = calcular_total(subtotal)
    print(f"Subtotal: {formatear_dinero(subtotal)}")
    print(f"Descuento ({porcentaje:.0%}): {formatear_dinero(subtotal - total)}")
    print(f"Total: {formatear_dinero(total)}")


def agregar_producto_al_carrito(inventario, carrito):
    """Pide un producto y una cantidad y los suma al carrito."""
    codigo = pedir_dato("Código: ", validar_codigo)
    producto = buscar_producto(inventario, codigo)
    print(f"{producto['nombre']}: {producto['stock']} disponibles.")

    cantidad = pedir_dato("Cantidad: ", validar_entero_positivo)
    agregar_al_carrito(inventario, carrito, codigo, cantidad)
    mostrar_carrito(inventario, carrito)


def recibir_pago(total):
    """Devuelve el cambio, o None si el cliente no puede pagar."""
    while True:
        pago = pedir_dato(PREGUNTA_PAGO, validar_decimal_positivo)
        try:
            return calcular_cambio(total, pago)
        except ValueError as error:
            print(f"Error: {error}")
            # Sin esta salida, el programa se quedaria pidiendo el pago
            # para siempre si el cliente no tiene con que pagar.
            if not pedir_confirmacion("¿Intentar de nuevo?"):
                return None


def cobrar(inventario, carrito):
    """Recibe el pago y, si se confirma, deja registrada la venta."""
    total = calcular_total(calcular_subtotal(inventario, carrito))

    cambio = recibir_pago(total)
    if cambio is None:
        print("Venta cancelada. El inventario no cambió.")
        return

    print(f"Cambio: {formatear_dinero(cambio)}")
    if not pedir_confirmacion("¿Confirmar la venta?"):
        print("Venta cancelada. El inventario no cambió.")
        return

    venta = {
        "fecha": datetime.date.today().isoformat(),
        "total": total,
        "items": carrito,
    }
    # Primero el historial: si no se puede escribir, el stock no se toca.
    registrar_venta(venta)
    descontar_stock(inventario, carrito)
    # Se guarda ya para que inventario e historial no queden desfasados.
    guardar_inventario(inventario)
    print("Venta registrada.")


def procesar_venta(inventario):
    """Arma el carrito hasta que el usuario cobre o cancele la venta."""
    carrito = {}

    while True:
        print("1. Agregar producto")
        print("2. Cobrar")
        print("3. Cancelar venta")
        opcion = pedir_opcion("Opción: ", 3)

        if opcion == 1:
            # Se captura aqui para no perder el carrito por un producto
            # que no existe o que no tiene stock suficiente.
            try:
                agregar_producto_al_carrito(inventario, carrito)
            except ValueError as error:
                print(f"Error: {error}")
        elif opcion == 3:
            print("Venta cancelada. El inventario no cambió.")
            return
        elif len(carrito) == 0:
            print("El carrito está vacío.")
        else:
            cobrar(inventario, carrito)
            return
