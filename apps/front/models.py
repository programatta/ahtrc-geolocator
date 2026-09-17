from django.db import models
from django.utils.translation import gettext_lazy as _


class MapConfig(models.Model):
    """
    MapConfig
    Modelo singleton (una única fila, pk=1): controla si el front
    muestra el mapa (is_open=True) o una landing page de "en construcción"
    (is_open=False).
    """
    is_open = models.BooleanField(verbose_name=_('is_open'), default=False)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return str(_('MapConfig'))

    class Meta:
        verbose_name = _('MapConfig')
        verbose_name_plural = _('MapConfig')

    @classmethod
    def load(cls):
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj
