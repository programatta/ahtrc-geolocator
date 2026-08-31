from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.genre import models as genremodels

# Create your models here.
class ClassicAuthor(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=256)
    genres = models.ManyToManyField(genremodels.Genre)

    def __str__(self)->str:
        return f"{self.name}"

    class Meta:
        verbose_name = _('ClassicAuthor')
        verbose_name_plural = _('ClassicAuthors')
        ordering = ['name']
