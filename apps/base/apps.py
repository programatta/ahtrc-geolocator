from django.apps import AppConfig


class BaseConfig(AppConfig):
    name = 'apps.base'

    def ready(self):
        from django.contrib import admin

        from apps.base.forms import OTPAdminAuthenticationForm
        admin.site.login_form = OTPAdminAuthenticationForm

        from . import signals  # noqa: F401
