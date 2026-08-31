from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Genre(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=256)

    def __str__(self)->str:
        return f"{self.name}"

    class Meta:
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')
        ordering = ['name']
