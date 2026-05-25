"""
Organizador de archivos por extensión.

Uso:
  python organizar.py                    # organiza ./descargas (solo raíz)
  python organizar.py -c "C:\\Descargas" -r
  python organizar.py --deshacer
  python organizar.py --notificar

Integración (fuera del script):
  Windows: PyInstaller + Programador de tareas
  Linux/macOS: cron (ej. 0 * * * * /usr/bin/python3 /ruta/organizar.py -c ~/Downloads)

Notificaciones opcionales: pip install plyer
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

CATEGORIAS = {
    "Imagenes": [".png", ".jpg", ".jpeg", ".gif"],
    "Documentos": [".pdf", ".docx", ".txt", ".xlsx", ".py"],
    "Videos": [".mp4", ".avi", ".mkv"],
    "Musica": [".mp3", ".wav"],
}
CATEGORIA_OTROS = "Otros"
HISTORIAL_NOMBRE = ".organizar_historial.json"

CARPETA_PREDETERMINADA = Path(__file__).resolve().parent / "descargas"


def construir_mapa_extensiones() -> dict[str, str]:
    mapa: dict[str, str] = {}
    for categoria, extensiones in CATEGORIAS.items():
        for ext in extensiones:
            mapa[ext.lower()] = categoria
    return mapa


def nombres_categorias() -> set[str]:
    return set(CATEGORIAS) | {CATEGORIA_OTROS}


def categoria_de(archivo: Path, mapa: dict[str, str]) -> str:
    return mapa.get(archivo.suffix.lower(), CATEGORIA_OTROS)


def ruta_historial(carpeta: Path) -> Path:
    return carpeta / HISTORIAL_NOMBRE


def iterar_archivos(carpeta: Path, recursivo: bool):
    """Archivos a organizar. En modo recursivo no entra en carpetas de categoría."""
    if not carpeta.is_dir():
        raise NotADirectoryError(f"No es una carpeta: {carpeta}")

    if not recursivo:
        for entrada in carpeta.iterdir():
            if entrada.is_file():
                yield entrada
        return

    categorias = nombres_categorias()
    for dirpath, dirnames, filenames in os.walk(carpeta):
        dirnames[:] = [d for d in dirnames if d not in categorias]
        base = Path(dirpath)
        for nombre in filenames:
            yield base / nombre


def destino_seguro(
    origen: Path,
    destino: Path,
    sobrescribir: bool,
) -> Path | None:
    if not destino.exists():
        return destino
    if sobrescribir:
        destino.unlink()
        return destino
    print(f"Omitido (ya existe): {destino.name} en {destino.parent.name}/")
    return None


def guardar_movimiento(historial: list[dict], origen: Path, destino: Path) -> None:
    historial.append(
        {
            "origen": str(origen.resolve()),
            "destino": str(destino.resolve()),
            "fecha": datetime.now(timezone.utc).isoformat(),
        }
    )


def organizar(
    carpeta: Path,
    *,
    recursivo: bool = False,
    sobrescribir: bool = False,
    registrar: bool = True,
) -> tuple[int, int]:
    carpeta.mkdir(parents=True, exist_ok=True)
    mapa = construir_mapa_extensiones()
    movidos = 0
    omitidos = 0
    historial: list[dict] = []

    for archivo in iterar_archivos(carpeta, recursivo):
        if archivo.name == HISTORIAL_NOMBRE:
            continue
        categoria = categoria_de(archivo, mapa)
        destino_dir = carpeta / categoria
        destino_dir.mkdir(exist_ok=True)
        destino = destino_dir / archivo.name

        destino_final = destino_seguro(archivo, destino, sobrescribir)
        if destino_final is None:
            omitidos += 1
            continue

        origen = archivo.resolve()
        archivo.rename(destino_final)
        print(f"Movido {origen.name} -> {categoria}/")
        if registrar:
            guardar_movimiento(historial, origen, destino_final)
        movidos += 1

    if registrar and historial:
        ruta = ruta_historial(carpeta)
        sesiones: list = []
        if ruta.exists():
            try:
                sesiones = json.loads(ruta.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                sesiones = []
        sesiones.append({"movimientos": historial})
        ruta.write_text(json.dumps(sesiones, indent=2, ensure_ascii=False), encoding="utf-8")

    return movidos, omitidos


def deshacer(carpeta: Path) -> int:
    ruta = ruta_historial(carpeta)
    if not ruta.exists():
        print("No hay historial para deshacer.")
        return 0

    sesiones = json.loads(ruta.read_text(encoding="utf-8"))
    if not sesiones:
        print("El historial está vacío.")
        return 0

    ultima = sesiones.pop()
    restaurados = 0
    for registro in reversed(ultima["movimientos"]):
        destino = Path(registro["destino"])
        origen = Path(registro["origen"])
        if not destino.exists():
            print(f"No encontrado (ya deshecho?): {destino.name}")
            continue
        origen.parent.mkdir(parents=True, exist_ok=True)
        if origen.exists():
            print(f"Conflicto al deshacer {destino.name}: ya existe en origen.")
            continue
        destino.rename(origen)
        print(f"Restaurado {destino.name} -> {origen.parent}")
        restaurados += 1

    if sesiones:
        ruta.write_text(json.dumps(sesiones, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        ruta.unlink(missing_ok=True)

    return restaurados


def enviar_notificacion(titulo: str, mensaje: str) -> None:
    try:
        from plyer import notification

        notification.notify(title=titulo, message=mensaje, app_name="Organizador", timeout=8)
    except Exception as exc:
        print(f"(Notificación no disponible: {exc}. Instala con: pip install plyer)")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Organiza archivos por extensión en subcarpetas.",
        epilog="Prueba primero en una carpeta de prueba. Usa -c para no tocar archivos reales.",
    )
    parser.add_argument(
        "-c",
        "--carpeta",
        type=Path,
        default=CARPETA_PREDETERMINADA,
        help=f"Carpeta a organizar (predeterminado: {CARPETA_PREDETERMINADA})",
    )
    parser.add_argument(
        "-r",
        "--recursivo",
        action="store_true",
        help="Incluye subcarpetas (excepto Imagenes, Documentos, Videos, Musica, Otros)",
    )
    parser.add_argument(
        "--sobrescribir",
        action="store_true",
        help="Reemplaza archivos si ya existen en la carpeta de destino",
    )
    parser.add_argument(
        "--deshacer",
        action="store_true",
        help="Restaura el último lote de movimientos registrado",
    )
    parser.add_argument(
        "--notificar",
        action="store_true",
        help="Muestra una notificación al terminar (requiere plyer)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    carpeta = args.carpeta.resolve()

    try:
        if args.deshacer:
            n = deshacer(carpeta)
            resumen = f"Restaurados: {n} archivo(s)."
            print(resumen)
            if args.notificar:
                enviar_notificacion("Organizador", resumen)
            return 0

        movidos, omitidos = organizar(
            carpeta,
            recursivo=args.recursivo,
            sobrescribir=args.sobrescribir,
        )
        resumen = f"Listo: {movidos} movido(s), {omitidos} omitido(s)."
        print(resumen)
        if args.notificar:
            enviar_notificacion("Organizador", resumen)
        return 0
    except NotADirectoryError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
