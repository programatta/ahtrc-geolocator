"""
csv2imagenes.py

Descarga las imágenes referenciadas en el campo `urlimagen` de
docs/autores_clasicos.csv y las guarda en docs/imagenes/, nombradas
como "<autor>-<obra>" (slugificado). Las imágenes están alojadas en
Google My Maps y no se pueden cargar directamente desde el navegador
(bloqueo CORS/CORP del propio servidor de Google), de ahí que se
descarguen una vez a disco en vez de enlazarlas en caliente.
"""
import csv
import urllib.error
import urllib.request
from pathlib import Path

from django.utils.text import slugify

CSV_ORIGEN = Path('../docs/autores_clasicos.csv')
CARPETA_DESTINO = Path('../docs/imagenes')

EXTENSIONES_POR_TIPO = {
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/webp': '.webp',
    'image/gif': '.gif',
}
EXTENSION_POR_DEFECTO = '.jpg'

contador_slugs = {}


def nombre_disponible(slug: str, extension: str) -> str:
    """Da un nombre de fichero único para `slug`, añadiendo un sufijo
    numérico si ya se ha usado antes (varias imágenes en la misma fila,
    o dos filas con el mismo autor y la misma obra)."""
    n = contador_slugs.get(slug, 0) + 1
    contador_slugs[slug] = n
    sufijo = '' if n == 1 else f'-{n}'
    return f'{slug}{sufijo}{extension}'


def extension_para(content_type: str) -> str:
    tipo = content_type.split(';')[0].strip().lower()
    return EXTENSIONES_POR_TIPO.get(tipo, EXTENSION_POR_DEFECTO)


def descargar_imagen(url: str, destino: Path) -> None:
    peticion = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(peticion, timeout=15) as respuesta:
        contenido = respuesta.read()
        content_type = respuesta.headers.get('Content-Type', '')
    destino = destino.with_suffix(extension_para(content_type))
    destino.write_bytes(contenido)


def descargar_imagenes_csv(ruta_csv: Path, carpeta_destino: Path):
    carpeta_destino.mkdir(parents=True, exist_ok=True)

    descargadas = 0
    saltadas = 0
    fallidas = []

    with open(ruta_csv, encoding='utf-8') as archivo_csv:
        lector = csv.DictReader(archivo_csv, delimiter=';')
        for fila in lector:
            urls = fila['urlimagen'].split()
            if not urls:
                continue

            slug = f"{slugify(fila['autoractual'])}-{slugify(fila['obra'])}"

            for url in urls:
                # Nombre provisional (sin extensión definitiva, se ajusta
                # en descargar_imagen según el Content-Type real).
                nombre = nombre_disponible(slug, EXTENSION_POR_DEFECTO)
                destino = carpeta_destino / nombre

                ya_descargada = list(carpeta_destino.glob(destino.stem + '.*'))
                if ya_descargada:
                    saltadas += 1
                    continue

                try:
                    descargar_imagen(url, destino)
                    descargadas += 1
                except (urllib.error.URLError, OSError) as error:
                    fallidas.append((f"{fila['autoractual']} - {fila['obra']}", url, str(error)))

    print("Proceso completado.")
    print(f"Imágenes descargadas: {descargadas}")
    print(f"Imágenes ya existentes (saltadas): {saltadas}")
    print(f"Imágenes fallidas: {len(fallidas)}")
    for obra, url, error in fallidas:
        print(f"  - {obra}: {url} ({error})")


# --- EJECUCIÓN DEL SCRIPT ---
descargar_imagenes_csv(CSV_ORIGEN, CARPETA_DESTINO)
