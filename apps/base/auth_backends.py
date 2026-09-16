from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
from django.utils import timezone

from apps.base.models import LoginCode

UserModel = get_user_model()


class OTPBackend(ModelBackend):
    """Authenticates with a one-time code emailed to the user instead of
    their password (docs/DEUDA.md, 2026-09-15, OWASP A07)."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or not password:
            return None
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            # Ejecuta un hash igualmente para no filtrar por tiempo de
            # respuesta si el usuario existe o no (mismo idioma que
            # ModelBackend.authenticate).
            UserModel().set_password(password)
            return None

        login_code = (
            LoginCode.objects.filter(user=user, used_at__isnull=True)
            .order_by('-created_at')
            .first()
        )
        if login_code is None or not login_code.is_valid():
            return None

        if not check_password(password, login_code.code_hash):
            login_code.attempts += 1
            login_code.save(update_fields=['attempts'])
            return None

        login_code.used_at = timezone.now()
        login_code.save(update_fields=['used_at'])
        return user if self.user_can_authenticate(user) else None
