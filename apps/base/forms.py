from django import forms
from django.contrib.admin.forms import AdminAuthenticationForm
from django.utils.translation import gettext_lazy as _


class OTPAdminAuthenticationForm(AdminAuthenticationForm):
    """Reemplaza el campo de contraseña del login del admin por el código de
    un solo uso enviado por email (ver apps.base.auth_backends.OTPBackend)."""

    password = forms.CharField(
        label=_('Access code'),
        strip=True,
        max_length=6,
        widget=forms.TextInput(
            attrs={
                'autofocus': True,
                'inputmode': 'numeric',
                'pattern': '[0-9]*',
                'autocomplete': 'one-time-code',
            }
        ),
    )

    error_messages = {
        **AdminAuthenticationForm.error_messages,
        'invalid_login': _(
            'Please enter the correct %(username)s and access code for a '
            'staff account. The code may have expired or already been used '
            '— request a new one.'
        ),
    }


class RequestLoginCodeForm(forms.Form):
    username = forms.CharField(label=_('Username'), max_length=150)
