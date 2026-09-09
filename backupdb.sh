#!/bin/bash

# =============================================================================
# script: backupdb.sh
# -----------------------------------------------------------------------------
# Realiza la copia de la base de datos leyendo el fichero de variables de entor
# no.
# Se programa en cron de la siguiente forma (todos los dias a las 02:00 am):
# 0 2 * * * /root/app/ahtrc-geolocator/backupdb.sh > /dev/null 2>&1
# =============================================================================

set -o pipefail

# Rutas ancladas al directorio del script: cron no arranca en esta carpeta,
# sino en el $HOME del usuario del crontab, así que "./" apuntaría mal.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Configuración de rutas
RUTA_ENV="$SCRIPT_DIR/environment/.env-prod-db"
RESPALDO_DIR="$SCRIPT_DIR/backups"
FECHA=$(date +%Y%m%d_%H%M%S)
FICHERO_SALIDA="$RESPALDO_DIR/respaldo_$FECHA.sql.gz"

# 1. Extraer el usuario del archivo .env-prod-db (limpiando posibles comillas o espacios)
DB_USER=$(grep -v '^#' "$RUTA_ENV" | grep 'POSTGRES_USER=' | awk -F '=' '{print $2}' | tr -d '"'\'' ')

# Si no encuentra la variable en el .env, usa 'postgres' por defecto
if [ -z "$DB_USER" ]; then
    DB_USER="postgres"
fi

DB_NAME=$(grep -v '^#' "$RUTA_ENV" | grep 'POSTGRES_DB=' | awk -F '=' '{print $2}' | tr -d '"'\'' ')

# Si no encuentra la variable en el .env-prod-db, salimos
if [ -z "$DB_NAME" ]; then
    echo "ERROR: No hay nombre de base de datos. Respaldo cancelado."
    exit 1
fi

# 2. Buscar dinámicamente el nombre del contenedor de Postgres
CONTENEDOR_POSTGRES=$(docker ps --filter "label=com.docker.compose.service=postgres_service" --format "{{.Names}}" | head -n 1)

# 3. Validar si el contenedor está activo antes de continuar
if [ -z "$CONTENEDOR_POSTGRES" ]; then
    echo "ERROR: El contenedor de postgres_service no está corriendo. Respaldo cancelado."
    exit 1
fi

# 4. Asegurar que el directorio de backups existe
mkdir -p "$RESPALDO_DIR"

# 5. Ejecutar el volcado usando el usuario dinámico y comprimir
docker exec -i "$CONTENEDOR_POSTGRES" pg_dumpall -U "$DB_USER" | gzip > "$FICHERO_SALIDA"

# Con "set -o pipefail" este $? refleja el fallo de pg_dumpall, no solo de
# gzip (que casi siempre "tiene éxito" aunque el volcado falle).
if [ $? -ne 0 ]; then
    echo "ERROR: pg_dumpall falló. Respaldo cancelado."
    rm -f "$FICHERO_SALIDA"
    exit 1
fi

# 6. Borrar respaldos más viejos de 3 días
find "$RESPALDO_DIR" -type f -name "*.sql.gz" -mtime +3 -delete
