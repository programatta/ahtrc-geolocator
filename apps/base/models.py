import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _


class LoginCodeManager(models.Manager):
    COOLDOWN_SECONDS = 60

    def create_for_user(self, user):
        last = self.filter(user=user).order_by('-created_at').first()
        if last and (timezone.now() - last.created_at).total_seconds() < self.COOLDOWN_SECONDS:
            return None

        code = f'{secrets.randbelow(1_000_000):06d}'
        login_code = self.create(
            user=user,
            code_hash=make_password(code),
            expires_at=timezone.now() + timedelta(minutes=LoginCode.VALID_MINUTES),
        )
        send_mail(
            subject=gettext('Your access code'),
            message=gettext(
                'Your access code is %(code)s. It expires in %(minutes)d minutes.'
            ) % {'code': code, 'minutes': LoginCode.VALID_MINUTES},
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        return login_code


class LoginCode(models.Model):
    MAX_ATTEMPTS = 5
    VALID_MINUTES = 5

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
        related_name='login_codes',
    )
    code_hash = models.CharField(verbose_name=_('code hash'), max_length=128)
    created_at = models.DateTimeField(verbose_name=_('created at'), auto_now_add=True)
    expires_at = models.DateTimeField(verbose_name=_('expires at'))
    used_at = models.DateTimeField(verbose_name=_('used at'), null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(verbose_name=_('attempts'), default=0)

    objects = LoginCodeManager()

    def is_valid(self) -> bool:
        return (
            self.used_at is None
            and self.attempts < self.MAX_ATTEMPTS
            and timezone.now() < self.expires_at
        )

    def __str__(self) -> str:
        return f"{self.user} ({self.created_at:%Y-%m-%d %H:%M})"

    class Meta:
        verbose_name = _('Login code')
        verbose_name_plural = _('Login codes')
        ordering = ['-created_at']
