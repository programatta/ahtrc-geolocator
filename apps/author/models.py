from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.gis.db import models as gis_models

# Create your models here.
class Author(models.Model):
    first_name = models.CharField(
        verbose_name=_('first_name'),
        max_length=64
    )
    last_name = models.CharField(
        verbose_name=_('last_name'),
        max_length=128
    )

    def __str__(self)->str:
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _('Author')
        verbose_name_plural = _('Authors')
        ordering = ['last_name']


class LiteraryWork(models.Model):
    title = models.CharField(
        verbose_name=_('title'),
        max_length=128
    )
    author = models.ForeignKey(
        'author.Author',
        verbose_name=_('author'),
        on_delete=models.CASCADE,
        related_name='literarywork_author'
    )
    classic_author = models.ForeignKey(
        'classicauthor.ClassicAuthor',
        verbose_name=_('classic_author'),
        on_delete=models.CASCADE,
        related_name='literarywork_classicauthor'
    )
    genre = models.ForeignKey(
        'genre.Genre',
        verbose_name=_('genre'),
        on_delete=models.CASCADE,
        related_name='literarywork_genre'
    )
    description = models.TextField(
        verbose_name=_('description'),
        blank=True,
        null=True
    )
    location = gis_models.PointField(
        verbose_name=_('location'),
        blank=True,
        null=True
    )

    def __str__(self)->str:
        return f"{self.title}"

    class Meta:
        verbose_name = _('LiteraryWork')
        verbose_name_plural = _('LiteraryWorks')
        ordering = ['title']
