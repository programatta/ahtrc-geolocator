"""
kmz2csv.py

Script para extraer datos del fichero kmz de Google Maps a un fichero csv.
"""
import csv
import zipfile
import xml.etree.ElementTree as ET

def limpiar_texto(texto:str)->str:
    """Elimina saltos de línea (\n y \r) y espacios dobles."""
    if not texto:
        return ""
    # Reemplazar saltos de línea por espacios simples
    texto_limpio = texto.replace('\n', ' ').replace('\r', ' ')
    # Limpiar espacios en blanco sobrantes a los lados y devolver
    return " ".join(texto_limpio.split())

def extraer_datos_kmz(ruta_kmz:str, ruta_csv:str):
    """Extra los datos del fichero kmz y los vuelva en un fichero csv"""
    columnas = [
        'autorclasico', 'autoractual', 'obra', 'descripcion', 
        'enlaces', 'urlimagen', 'longitud', 'latitud', 'altitud'
    ]
    filas_csv = []

    # 1. Abrir el archivo KMZ y leer el KML interno
    with zipfile.ZipFile(ruta_kmz, 'r') as z:
        kml_filename = next((f for f in z.namelist() if f.endswith('.kml')), None)
        if not kml_filename:
            print("Error: No se encontró ningún archivo KML válido dentro del KMZ.")
            return
        kml_data = z.read(kml_filename)

    # 2. Parsear el contenido XML
    root = ET.fromstring(kml_data)

    # Recorrer todos los elementos buscando nodos <Folder>
    for elem in root.iter():
        if elem.tag.endswith('Folder'):
            # Buscar el nombre del Folder (autorclasico)
            autor_clasico = ""
            for hijo in elem:
                if hijo.tag.endswith('name') and hijo.text:
                    autor_clasico = limpiar_texto(hijo.text)
                    break

            # Buscar todos los <Placemark> dentro de este Folder específico
            for placemark in elem.findall('.//{*}Placemark'):
                autor_actual = ""
                obra = ""
                descripcion = ""
                enlaces = []
                url_imagen = ""
                longitud, latitud, altitud = "", "", ""

                # Nombre del Placemark (autoractual)
                name_elem = placemark.find('{*}name')
                if name_elem is not None and name_elem.text:
                    autor_actual = limpiar_texto(name_elem.text)

                # Procesar datos extendidos <ExtendedData>
                extended_data = placemark.find('.//{*}ExtendedData')
                if extended_data is not None:
                    for data_elem in extended_data.findall('{*}Data'):
                        name_attr = data_elem.attrib.get('name')
                        value_elem = data_elem.find('{*}value')

                        if value_elem is not None and value_elem.text:
                            valor = limpiar_texto(value_elem.text)

                            if name_attr == 'Obra':
                                obra = valor
                            elif name_attr == 'Descripción':
                                descripcion = valor
                            elif name_attr == 'Enlaces':
                                enlaces.append(valor)
                            elif name_attr == 'gx_media_links':
                                url_imagen = valor

                # Procesar Coordenadas <Point><coordinates>
                coords_elem = placemark.find('.//{*}Point/{*}coordinates')
                if coords_elem is not None and coords_elem.text:
                    # Limpiamos posibles saltos de línea también en las coordenadas
                    coords_limpias = limpiar_texto(coords_elem.text)
                    partes_coords = coords_limpias.split(',')
                    if len(partes_coords) >= 2:
                        longitud = partes_coords[0].strip()
                        latitud = partes_coords[1].strip()
                    if len(partes_coords) >= 3:
                        altitud = partes_coords[2].strip()

                # Unificar los enlaces si existen varios, separados por comas
                enlaces_str = ", ".join(enlaces)

                # Guardar la fila procesada
                filas_csv.append([
                    autor_clasico,
                    autor_actual,
                    obra,
                    descripcion,
                    enlaces_str,
                    url_imagen,
                    longitud,
                    latitud,
                    altitud
                ])

    # 3. Volcar los datos procesados en el archivo CSV separado por punto y coma (;)
    with open(ruta_csv, mode='w', newline='', encoding='utf-8') as archivo_csv:
        # Se añade delimiter=';' para cumplir con el formato solicitado
        escritor = csv.writer(archivo_csv, delimiter=';')
        escritor.writerow(columnas)
        escritor.writerows(filas_csv)

    print("Proceso completado con éxito.")
    print(f"Se han procesado {len(filas_csv)} filas correctamente.")

# --- EJECUCIÓN DEL SCRIPT ---
ARCHIVO_ORIGEN = '../docs/AHTRC.kmz'
ARCHIVO_DESTINO = '../docs/autores_clasicos.csv'

extraer_datos_kmz(ARCHIVO_ORIGEN, ARCHIVO_DESTINO)
