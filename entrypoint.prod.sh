#!/bin/bash
set -euo pipefail

# Arregla el propietario de los volúmenes con nombre (static_data/media_data):
# Docker garantiza que el punto de montaje existe al arrancar el contenedor,
# pero puede tener contenido de un despliegue anterior corriendo como root, o
# ser un volumen nuevo que Docker crea como root. chown -R es idempotente y
# barato para el tamaño de estos volúmenes.
chown -R ahtrc:ahtrc /code/staticfiles /code/media

# Cede privilegios a ahtrc para el resto del arranque y para gunicorn.
# setpriv (paquete util-linux, ya en la imagen base) hace execve directo, sin
# el subshell intermedio de "su -c", así que gunicorn queda como PID 1 y
# recibe directamente las señales de "docker stop" (SIGTERM).
exec setpriv --reuid=ahtrc --regid=ahtrc --init-groups --inh-caps=-all \
    /bin/bash -c '
        set -euo pipefail
        python manage.py migrate --noinput
        python manage.py create_super_user
        python manage.py collectstatic --noinput
        python manage.py compilemessages
        exec gunicorn --bind :8000 conf.wsgi:application
    '
