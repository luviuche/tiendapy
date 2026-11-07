"""Registro, consulta, modificacion y eliminacion de productos."""

from tabulate import tabulate

from tiendapy.validaciones import (
    pedir_categoria,
    pedir_confirmacion,
    pedir_dato,
    pedir_opcion,
    validar_codigo,
    validar_decimal_positivo,
    validar_entero_no_negativo,
    validar_entero_positivo,
    validar_texto,
)

ENCABEZADOS = ["Código", "Nombre", "Categoría", "Precio", "Stock", "Mínimo", "Proveedor"]
ALINEACION = ("left", "left", "left", "right", "right", "right", "left")
PREGUNTA_PRECIO = "Precio en COP (sin puntos ni comas): "


# ---------------------------------------------------------------------------
# Logica del negocio: trabaja sobre el diccionario y no usa print ni input.
# Las reglas que no se cumplen se señalan con raise y se capturan en el menu.
# ---------------------------------------------------------------------------


def verificar_codigo_libre(inventario, codigo):
    """Lanza ValueError si el codigo ya esta en uso."""
    if codigo in inventario:
        raise ValueError(f"Ya existe un producto con el código {codigo}.")


def agregar_producto(inventario, producto):
    """Agrega un producto nuevo al inventario."""
    verificar_codigo_libre(inventario, producto["codigo"])
    inventario[producto["codigo"]] = producto


def buscar_producto(inventario, codigo):
    """Devuelve el producto con ese codigo o lanza ValueError."""
    if codigo not in inventario:
        raise ValueError(f"No existe un producto con el código {codigo}.")
    return inventario[codigo]


def buscar_por_categoria(inventario, categoria):
    """Devuelve la lista de productos de una categoria."""
    encontrados = []
    for producto in inventario.values():
        if producto["categoria"] == categoria:
            encontrados.append(producto)
    return encontrados


def modificar_precio(inventario, codigo, precio):
    """Cambia el precio de un producto existente."""
    buscar_producto(inventario, codigo)["precio"] = precio


def modificar_stock(inventario, codigo, stock):
    """Cambia el stock de un producto existente."""
    buscar_producto(inventario, codigo)["stock"] = stock


def eliminar_producto(inventario, codigo):
    """Elimina un producto existente y lo devuelve."""
    buscar_producto(inventario, codigo)
    return inventario.pop(codigo)


# ---------------------------------------------------------------------------
# Presentacion
# ---------------------------------------------------------------------------


def formatear_dinero(valor):
    """Muestra un valor con el formato colombiano, por ejemplo $4.200."""
    return f"${valor:,.0f}".replace(",", ".")


def mostrar_productos(productos):
    """Imprime una lista de productos como tabla."""
    filas = []
    for producto in productos:
        filas.append(
            [
                producto["codigo"],
                producto["nombre"],
                producto["categoria"],
                formatear_dinero(producto["precio"]),
                producto["stock"],
                producto["stock_minimo"],
                producto["proveedor"],
            ]
        )
    # disable_numparse evita que tabulate cambie codigos como 007 o 1E5.
    print(tabulate(filas, headers=ENCABEZADOS, colalign=ALINEACION, disable_numparse=True))


# ---------------------------------------------------------------------------
# Opciones del menu: conversan con el usuario y usan la logica de arriba.
# ---------------------------------------------------------------------------


def registrar_producto(inventario):
    """Pide los datos de un producto nuevo y lo agrega."""
    codigo = pedir_dato("Código: ", validar_codigo)
    # Se revisa de una vez para no pedir el resto de datos en vano.
    verificar_codigo_libre(inventario, codigo)

    producto = {
        "codigo": codigo,
        "nombre": pedir_dato("Nombre: ", validar_texto),
        "categoria": pedir_categoria(),
        "precio": pedir_dato(PREGUNTA_PRECIO, validar_decimal_positivo),
        "stock": pedir_dato("Stock: ", validar_entero_positivo),
        "stock_minimo": pedir_dato("Stock mínimo: ", validar_entero_no_negativo),
        "proveedor": pedir_dato("Proveedor: ", validar_texto),
    }
    agregar_producto(inventario, producto)
    print(f"Producto {codigo} registrado.")


def listar_inventario(inventario):
    """Muestra todos los productos."""
    if len(inventario) == 0:
        print("El inventario está vacío.")
    else:
        mostrar_productos(inventario.values())


def consultar_por_codigo(inventario):
    """Muestra el producto que tenga el codigo digitado."""
    codigo = pedir_dato("Código: ", validar_codigo)
    mostrar_productos([buscar_producto(inventario, codigo)])


def consultar_por_categoria(inventario):
    """Muestra los productos de la categoria elegida."""
    categoria = pedir_categoria()
    encontrados = buscar_por_categoria(inventario, categoria)
    if len(encontrados) == 0:
        print(f"No hay productos en la categoría {categoria}.")
    else:
        mostrar_productos(encontrados)


def modificar_producto(inventario):
    """Cambia el precio o el stock de un producto."""
    codigo = pedir_dato("Código: ", validar_codigo)
    mostrar_productos([buscar_producto(inventario, codigo)])

    print("1. Modificar precio")
    print("2. Modificar stock")
    print("3. Cancelar")
    opcion = pedir_opcion("Opción: ", 3)

    if opcion == 1:
        modificar_precio(inventario, codigo, pedir_dato(PREGUNTA_PRECIO, validar_decimal_positivo))
        print("Precio actualizado.")
    elif opcion == 2:
        modificar_stock(inventario, codigo, pedir_dato("Stock: ", validar_entero_positivo))
        print("Stock actualizado.")


def eliminar_del_inventario(inventario):
    """Elimina un producto despues de confirmar con el usuario."""
    codigo = pedir_dato("Código: ", validar_codigo)
    mostrar_productos([buscar_producto(inventario, codigo)])

    if pedir_confirmacion("¿Eliminar este producto?"):
        eliminar_producto(inventario, codigo)
        print(f"Producto {codigo} eliminado.")
    else:
        print("No se eliminó el producto.")
