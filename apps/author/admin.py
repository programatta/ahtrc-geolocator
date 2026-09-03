from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from leaflet.admin import LeafletGeoAdmin
from . import models


# Register your models here.
@admin.register(models.Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name']
    search_fields = ['first_name', 'last_name']



class ImageInline(admin.TabularInline):
    model = models.Imagen
    fields = ['image_tag', 'image']
    readonly_fields = ['image_tag']
    extra = 0
    verbose_name = _('ImageInline')
    verbose_name_plural = _('ImagesInline')

class LinkInline(admin.TabularInline):
    model = models.Link
    fields = []
    extra = 0
    verbose_name = _('LinkInline')
    verbose_name_plural = _('LinksInlines')

@admin.register(models.LiteraryWork)
class LiteraryAdmin(LeafletGeoAdmin):
    list_display = ['title', 'author', 'genre']
    search_fields = ['title', 'author__first_name', 'author__last_name']
    list_filter=['genre']
    autocomplete_fields = ['author', 'classic_author', 'genre']
    display_raw_point = True # Muestra las coordenadas debajo del mapa por si acaso
    settings_overrides = {
        'DEFAULT_CENTER': (40.4167, -3.7037), 
        'DEFAULT_ZOOM': 6,
    }
    inlines = [ImageInline, LinkInline]

    class Media:
        js = (
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
            'https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.js',
            'admin/js/leaflet_setup.js', # Un pequeño script que crearemos ahora
        )
        css = {
            'all': ('https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.css',)
        }
