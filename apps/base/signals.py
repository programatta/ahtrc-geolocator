import logging

from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver

logger = logging.getLogger('django.security')


def _client_ip(request):
    if request is None:
        return None
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        # nginx (único proxy delante de la app) añade su propio remote_addr
        # al final de la cadena vía $proxy_add_x_forwarded_for; cualquier
        # valor anterior lo puede falsificar el propio cliente, así que solo
        # se confía en el último.
        return forwarded_for.split(',')[-1].strip()
    return request.META.get('REMOTE_ADDR')


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    username = credentials.get('username', '<unknown>')
    logger.warning('Failed login attempt for username=%r from %s', username, _client_ip(request))
