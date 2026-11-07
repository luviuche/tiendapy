# TiendaPy

Aplicación de consola en Python para controlar el inventario y las ventas de una tienda de barrio. Es el proyecto final del curso **Python 0 a 100** (Curso ACM, Universidad Distrital Francisco José de Caldas).

Don Aurelio atiende unos 80 clientes al día y lleva sus cuentas en un cuaderno. Eso le causa desabastecimiento inesperado, errores de cálculo, pérdida de información y días sin cierre de caja. TiendaPy reemplaza ese cuaderno con un programa pensado para personas sin formación técnica: un error de digitación no lo detiene.

## Funcionalidades

- **Inventario:** registrar, consultar, modificar y eliminar productos; buscar por código o por categoría.
- **Ventas:** carrito con varios productos, descuentos automáticos, pago y cálculo del cambio.
- **Alertas:** productos con stock menor o igual al mínimo, agrupados por proveedor e identificando los agotados.
- **Cierre del día:** total vendido, número de ventas, ticket promedio, producto más vendido, productos sin ventas y categorías con movimiento.
- **Persistencia:** los datos se conservan en archivos de texto plano entre ejecuciones.

## Requisitos

- Python 3.10 o superior.
- La librería [tabulate](https://pypi.org/project/tabulate/), usada para mostrar tablas en consola. Está declarada en `requirements.txt`.

## Instalación y ejecución

Primero clone el repositorio. Ejecute el programa siempre desde la raíz del proyecto, porque los datos se buscan en la carpeta `data/`.

```bash
git clone https://github.com/luviuche/tiendapy.git
cd tiendapy
```

### Opción 1: con venv y pip

En Linux o macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python -m tiendapy
```

En Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m tiendapy
```

### Opción 2: con uv

```bash
uv run tiendapy
```

`uv` crea el entorno virtual e instala las dependencias automáticamente.

## Uso

Al iniciar, el programa carga el inventario y muestra el menú, que se repite hasta elegir **Salir**:

```text
=== TiendaPy ===
1. Registrar producto
2. Ver inventario
3. Buscar por código
4. Buscar por categoría
5. Modificar producto
6. Eliminar producto
7. Registrar venta
8. Alertas de stock
9. Cierre del día
10. Guardar inventario
11. Salir
```

El inventario se guarda al salir, con la opción 10 y después de cada venta. Si el programa se interrumpe con Ctrl+C, también guarda antes de cerrarse.

## Reglas de negocio

- No se puede vender más que el stock disponible.
- Los precios y las cantidades deben ser mayores a cero.
- Las compras con subtotal desde $50.000 COP tienen 5 % de descuento, y desde $100.000 COP, 10 %.
- El pago no puede ser inferior al total.
- Los códigos de producto no se pueden repetir.
- Un producto con stock en cero aparece en las alertas como `AGOTADO`.

## Archivos de datos

Los datos están en `data/`. El repositorio incluye 20 productos y 4 ventas de ejemplo.

`data/inventario.txt` guarda un producto por línea, con los campos `codigo|nombre|categoria|precio|stock|stock_minimo|proveedor`:

```text
LAC001|Leche entera 1L|Lacteos|4200.0|35|10|Alqueria
```

`data/ventas.txt` guarda una venta por línea, con el formato `fecha|total|codigo:cantidad;codigo:cantidad`:

```text
2026-11-04|14200.0|LAC001:2;BEB003:1
```

Si una línea está dañada, se omite con una advertencia y el programa continúa. Las líneas omitidas del inventario se copian en `data/inventario_omitidas.txt` para que no se pierdan al guardar.

## Estructura del proyecto

```text
tiendapy/
├── README.md
├── pyproject.toml
├── requirements.txt
├── uv.lock
├── data/
│   ├── inventario.txt
│   └── ventas.txt
└── src/
    └── tiendapy/
        ├── __init__.py
        ├── __main__.py       # permite ejecutar python -m tiendapy
        ├── main.py           # menú principal y flujo general
        ├── inventario.py     # CRUD de productos
        ├── ventas.py         # carrito, descuentos y cambio
        ├── reportes.py       # alertas y cierre del día
        ├── persistencia.py   # lectura y escritura de archivos
        └── validaciones.py   # captura segura de datos
```

## Decisiones de diseño

- **Diccionarios y funciones, sin clases.** Los productos y las ventas son diccionarios, y el inventario es un diccionario `{codigo: producto}` para buscar directamente por código.
- **Reglas de negocio con `raise`.** Cada regla incumplida lanza `ValueError`, y el menú principal la captura. El registro de ventas también captura los errores del carrito, para no perder la venta por un producto sin stock.
- **Stock en cero.** Al digitar, el stock debe ser mayor a cero; al leer el archivo se acepta el cero, porque así queda un producto agotado.
- **Total redondeado al peso.** El peso colombiano no usa centavos en la práctica, así que el total a pagar se redondea a pesos enteros.
- **Guardado seguro.** El inventario se escribe primero en un archivo temporal y luego reemplaza al original. Si algo falla a mitad de camino, el archivo anterior queda intacto.
- **Productos eliminados.** Siguen apareciendo en el historial de ventas, y el cierre los muestra como `CODIGO (eliminado)`.

## Desarrollo

El proyecto se gestiona con Git: cada funcionalidad se desarrolla en su propia rama (`feature/...`, `docs/...`) y se integra a `main` con `git merge --no-ff`, para que el historial conserve cada rama.

Si agrega una dependencia con `uv add`, actualice también `requirements.txt`:

```bash
uv export --no-hashes --no-dev --no-emit-project -o requirements.txt
```
