# Organizador de archivos

Script en Python que **ordena archivos sueltos por extensión** en subcarpetas (`Imagenes`, `Documentos`, `Videos`, `Musica`, `Otros`). Útil para limpiar Descargas o cualquier carpeta con muchos archivos mezclados.

## Requisitos

- Python 3.10 o superior
- Solo biblioteca estándar para el uso básico
- [plyer](https://pypi.org/project/plyer/) (opcional) para notificaciones de escritorio

## Instalación

```bash
git clone https://github.com/Adonai24/analisar.git
cd analisar
```

Notificaciones (opcional):

```bash
pip install -r requirements.txt
```

## Uso rápido

Por defecto organiza la carpeta `descargas/` junto al script (solo archivos en la raíz):

```bash
python organizar.py
```

Ejemplo de salida:

```
Movido foto.jpg -> Imagenes/
Movido informe.pdf -> Documentos/
Listo: 2 movido(s), 0 omitido(s).
```

## Categorías

| Carpeta      | Extensiones                          |
|-------------|---------------------------------------|
| Imagenes    | `.png`, `.jpg`, `.jpeg`, `.gif`      |
| Documentos  | `.pdf`, `.docx`, `.txt`, `.xlsx`, `.py` |
| Videos      | `.mp4`, `.avi`, `.mkv`               |
| Musica      | `.mp3`, `.wav`                       |
| Otros       | Cualquier otra extensión             |

Puedes editar el diccionario `CATEGORIAS` en `organizar.py` para añadir más tipos.

## Opciones de línea de comandos

| Opción | Descripción |
|--------|-------------|
| `-c`, `--carpeta RUTA` | Carpeta a organizar (por defecto: `./descargas`) |
| `-r`, `--recursivo` | Incluye subcarpetas; **no** entra en las carpetas de categoría |
| `--sobrescribir` | Reemplaza archivos si ya existen en destino |
| `--deshacer` | Restaura el último lote de movimientos |
| `--notificar` | Notificación al terminar (requiere `plyer`) |
| `-h`, `--help` | Muestra la ayuda |

### Ejemplos

```bash
# Carpeta personalizada (por ejemplo Descargas de Windows)
python organizar.py -c "%USERPROFILE%\Downloads"

# Incluir subcarpetas
python organizar.py -r

# Combinado con notificación
python organizar.py -c "D:\Descargas" -r --notificar

# Deshacer el último organize
python organizar.py --deshacer
```

## Modo recursivo

Con `-r`, el script recorre subcarpetas pero **ignora** `Imagenes`, `Documentos`, `Videos`, `Musica` y `Otros`, para no mover otra vez archivos ya organizados.

## Deshacer

Cada ejecución guarda los movimientos en `.organizar_historial.json` dentro de la carpeta objetivo. `--deshacer` revierte solo el **último** lote. Sirve para practicar; no sustituye una copia de seguridad.

## Automatización (opcional)

**Windows:** empaqueta con [PyInstaller](https://pyinstaller.org/) y programa una tarea en el Programador de tareas.

**Linux / macOS:** añade una entrada en `cron`, por ejemplo cada hora:

```cron
0 * * * * /usr/bin/python3 /ruta/a/organizar.py -c ~/Downloads -r
```

## Seguridad

- Prueba primero en una carpeta de prueba (`descargas/` del proyecto).
- En carpetas reales, haz copia de seguridad antes de usar `--sobrescribir`.
- El script **mueve** archivos (`rename`); no los copia ni los borra.

## Estructura del proyecto

```
.
├── organizar.py      # Script principal
├── requirements.txt  # Dependencias opcionales
├── descargas/        # Carpeta de prueba (ignorada por git)
└── README.md
```

## Licencia

Uso libre para aprendizaje y proyectos personales.
