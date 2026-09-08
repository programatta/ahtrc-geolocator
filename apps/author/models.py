from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.contrib.gis.db import models as gis_models
from .utils import path_and_rename

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
    title = models.TextField(
        verbose_name=_('title')
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


class Imagen(models.Model):
    literary_work = models.ForeignKey(
        'author.LiteraryWork',
        verbose_name=_('literary_work'),
        on_delete=models.CASCADE,
        related_name='imagen_literarywork'
    )
    image = models.ImageField(
        upload_to=path_and_rename,
        blank=True,
        null=True,
        verbose_name=_('Image')
    )

    class Meta:
        verbose_name = _('Imagen')
        verbose_name_plural = _('Imagens')

    def image_tag(self):
        if not self.image:
            return ''
        return format_html('<img src="{}" style="width: 50px; height:50px;" />', self.image.url)
    image_tag.short_description = _('Image')


class Link(models.Model):
    literary_work = models.ForeignKey(
        'author.LiteraryWork',
        verbose_name=_('literary_work'),
        on_delete=models.CASCADE,
        related_name='link_literarywork'
    )
    link = models.CharField(
        verbose_name=_('link'),
        max_length=4096
    )

    class Meta:
        verbose_name = _('Link')
        verbose_name_plural = _('Links')
