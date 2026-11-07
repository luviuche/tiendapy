"""Captura segura de los datos que digita el usuario."""

import math

CATEGORIAS = ["Lacteos", "Bebidas", "Aseo", "Abarrotes", "Snacks"]
TILDES = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u"}


# ---------------------------------------------------------------------------
# Validaciones: reciben un texto y devuelven el dato ya convertido.
# Si el dato no sirve lanzan ValueError con un mensaje para el usuario.
# Tambien las usa persistencia.py para revisar las lineas de los archivos.
# ---------------------------------------------------------------------------


def validar_texto(texto):
    """Revisa nombres y proveedores."""
    texto = texto.strip()
    if texto == "":
        raise ValueError("El dato no puede estar vacío.")
    # El caracter | separa los campos en inventario.txt.
    if "|" in texto:
        raise ValueError('El dato no puede contener el carácter "|".')
    return texto


def validar_codigo(texto):
    """Revisa un codigo de producto y lo devuelve en mayusculas."""
    codigo = validar_texto(texto).upper()
    if not codigo.isalnum():
        raise ValueError("El código solo puede tener letras y números.")
    return codigo


def validar_categoria(texto):
    """Devuelve la categoria oficial, sin importar mayusculas ni tildes."""
    buscada = texto.strip().lower()
    for con_tilde, sin_tilde in TILDES.items():
        buscada = buscada.replace(con_tilde, sin_tilde)

    for categoria in CATEGORIAS:
        if categoria.lower() == buscada:
            return categoria
    raise ValueError("La categoría no existe.")


def validar_decimal_positivo(texto):
    """Convierte precios y pagos, que deben ser mayores a cero."""
    try:
        numero = float(texto)
    except ValueError:
        raise ValueError("Debe ingresar un número, por ejemplo 4200.")

    # float() acepta "nan" e "inf", pero no son valores validos.
    if not math.isfinite(numero):
        raise ValueError("Debe ingresar un número, por ejemplo 4200.")
    if numero <= 0:
        raise ValueError("El valor debe ser mayor a cero.")
    return numero


def validar_entero(texto):
    """Convierte un texto a numero entero."""
    try:
        return int(texto)
    except ValueError:
        raise ValueError("Debe ingresar un número entero, por ejemplo 12.")


def validar_entero_positivo(texto):
    """Convierte cantidades y stock digitado, que deben ser mayores a cero."""
    numero = validar_entero(texto)
    if numero <= 0:
        raise ValueError("El valor debe ser mayor a cero.")
    return numero


def validar_entero_no_negativo(texto):
    """Convierte el stock minimo y el stock guardado, que pueden ser cero."""
    numero = validar_entero(texto)
    if numero < 0:
        raise ValueError("El valor no puede ser negativo.")
    return numero


# ---------------------------------------------------------------------------
# Captura: repiten la pregunta hasta que el usuario escriba un dato valido.
# ---------------------------------------------------------------------------


def pedir_dato(mensaje, validar):
    """Pregunta hasta que la funcion validar acepte lo que se digito."""
    while True:
        try:
            return validar(input(mensaje))
        except ValueError as error:
            print(f"Error: {error}")


def pedir_opcion(mensaje, cantidad):
    """Pide un numero de opcion entre 1 y cantidad."""
    while True:
        try:
            opcion = validar_entero_positivo(input(mensaje))
            if opcion > cantidad:
                raise ValueError(f"Elija una opción entre 1 y {cantidad}.")
            return opcion
        except ValueError as error:
            print(f"Error: {error}")


def pedir_categoria():
    """Muestra las categorias y devuelve la elegida."""
    for numero, categoria in enumerate(CATEGORIAS, start=1):
        print(f"{numero}. {categoria}")
    opcion = pedir_opcion("Categoría: ", len(CATEGORIAS))
    return CATEGORIAS[opcion - 1]


def pedir_confirmacion(mensaje):
    """Devuelve True si el usuario responde si, y False si responde no."""
    while True:
        respuesta = input(f"{mensaje} (s/n): ").strip().lower()
        if respuesta in ("s", "si", "sí"):
            return True
        if respuesta in ("n", "no"):
            return False
        print("Error: responda s o n.")
