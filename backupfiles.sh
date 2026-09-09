#!/bin/bash

# =============================================================================
# script: backupfiles.sh
# -----------------------------------------------------------------------------
# Realiza la copia de los ficheros de media/files.
# Se programa en cron de la siguiente forma (todos los dias a las 02:30 am):
# 30 2 * * * /root/app/ahtrc-geolocator/backupfiles.sh > /dev/null 2>&1
# =============================================================================

set -o pipefail

# Rutas ancladas al directorio del script: cron no arranca en esta carpeta,
# sino en el $HOME del usuario del crontab, así que "./" apuntaría mal.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Configuración de rutas
# media_data es un volumen nombrado de Docker (docker-compose.prod.yml), no
# un bind-mount a una carpeta del proyecto: no existe ninguna ruta de host
# equivalente. Se copia desde dentro del contenedor que sí tiene ese volumen
# montado en /code/media.
RESPALDO_DIR="$SCRIPT_DIR/backups/media"
FECHA=$(date +%Y%m%d_%H%M%S)
FICHERO_SALIDA="$RESPALDO_DIR/images_$FECHA.tar.gz"

# 1. Asegurar que el directorio de backups existe
mkdir -p "$RESPALDO_DIR"

# 2. Buscar dinámicamente el nombre del contenedor de ahtrc_service
CONTENEDOR_AHTRC=$(docker ps --filter "label=com.docker.compose.service=ahtrc_service" --format "{{.Names}}" | head -n 1)

# 3. Validar si el contenedor está activo antes de continuar
if [ -z "$CONTENEDOR_AHTRC" ]; then
    echo "ERROR: El contenedor de ahtrc_service no está corriendo. Respaldo cancelado."
    exit 1
fi

# 4. Crear el archivo comprimido .tar.gz desde dentro del contenedor
# Nota: -C cambia al directorio origen para que el .tar.gz no guarde rutas absolutas molestas
docker exec "$CONTENEDOR_AHTRC" tar -czf - -C /code/media . > "$FICHERO_SALIDA"

# El $? de la línea anterior ya refleja el fallo de "docker exec ... tar"
# (no hay pipe de por medio); se comprueba explícitamente en vez de asumir
# éxito silencioso.
if [ $? -ne 0 ]; then
    echo "ERROR: La copia de media falló. Respaldo cancelado."
    rm -f "$FICHERO_SALIDA"
    exit 1
fi

# 5. Borrar respaldos más viejos de 3 días
find "$RESPALDO_DIR" -type f -name "*.tar.gz" -mtime +3 -delete
