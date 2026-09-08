from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GenreConfig(AppConfig):
    name = 'apps.genre'
    verbose_name = _('Genres')
