"""Menu principal y flujo general del programa."""

from tiendapy.inventario import (
    consultar_por_categoria,
    consultar_por_codigo,
    eliminar_del_inventario,
    listar_inventario,
    modificar_producto,
    registrar_producto,
)
from tiendapy.persistencia import cargar_inventario, guardar_inventario
from tiendapy.reportes import mostrar_alertas, mostrar_cierre
from tiendapy.validaciones import pedir_opcion
from tiendapy.ventas import procesar_venta

OPCIONES = [
    "Registrar producto",
    "Ver inventario",
    "Buscar por código",
    "Buscar por categoría",
    "Modificar producto",
    "Eliminar producto",
    "Registrar venta",
    "Alertas de stock",
    "Cierre del día",
    "Guardar inventario",
    "Salir",
]
OPCION_SALIR = len(OPCIONES)


def mostrar_menu():
    """Imprime las opciones del menu principal."""
    print("\n=== TiendaPy ===")
    for numero, texto in enumerate(OPCIONES, start=1):
        print(f"{numero}. {texto}")


def guardar(inventario):
    """Guarda el inventario e informa al usuario."""
    guardar_inventario(inventario)
    print("Inventario guardado.")


def ejecutar_opcion(opcion, inventario):
    """Llama a la funcion que corresponde a la opcion elegida."""
    if opcion == 1:
        registrar_producto(inventario)
    elif opcion == 2:
        listar_inventario(inventario)
    elif opcion == 3:
        consultar_por_codigo(inventario)
    elif opcion == 4:
        consultar_por_categoria(inventario)
    elif opcion == 5:
        modificar_producto(inventario)
    elif opcion == 6:
        eliminar_del_inventario(inventario)
    elif opcion == 7:
        procesar_venta(inventario)
    elif opcion == 8:
        mostrar_alertas(inventario)
    elif opcion == 9:
        mostrar_cierre(inventario)
    elif opcion == 10:
        guardar(inventario)


def ejecutar_menu(inventario):
    """Repite el menu hasta que el usuario elija salir."""
    while True:
        mostrar_menu()
        opcion = pedir_opcion("Opción: ", len(OPCIONES))
        if opcion == OPCION_SALIR:
            return

        # Aqui se capturan las reglas de negocio señaladas con raise.
        try:
            ejecutar_opcion(opcion, inventario)
        except ValueError as error:
            print(f"Error: {error}")
        except OSError as error:
            print(f"Error con los archivos: {error}")


def guardar_al_salir(inventario):
    """Intenta guardar sin detener el programa si el archivo falla."""
    try:
        guardar(inventario)
    except OSError as error:
        print(f"No se pudo guardar el inventario: {error}")


def main():
    """Carga los datos, atiende el menu y guarda al terminar."""
    try:
        inventario = cargar_inventario()
    except OSError as error:
        # No se sigue con un inventario vacio: al salir borraria el real.
        print(f"No se pudo leer el inventario: {error}")
        print("El programa se cierra para no dañar los datos.")
        return

    print(f"Inventario cargado: {len(inventario)} productos.")
    try:
        ejecutar_menu(inventario)
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C o el fin de la entrada no deben perder los cambios.
        print("\nEl programa se interrumpió.")
    finally:
        guardar_al_salir(inventario)
    print("Hasta luego.")


if __name__ == "__main__":
    main()
