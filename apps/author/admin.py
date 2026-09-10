"""
admin.py
Vista de administración para:
- Autores
- Obras literarias.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from leaflet.admin import LeafletGeoAdmin
from . import models


#------------------------------------------------------------------------------
# Autores.
#------------------------------------------------------------------------------
@admin.register(models.Author)
class AuthorAdmin(admin.ModelAdmin):
    """
    AuthorAdmin
    Formulario para rellenar los datos del autor moderno.
    """
    list_display = ['first_name', 'last_name']
    search_fields = ['first_name', 'last_name']


#------------------------------------------------------------------------------
# Obras lierarias.
#------------------------------------------------------------------------------
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
class LiteraryWorkAdmin(LeafletGeoAdmin):
    """
    LiteraryWorkAdmin
    Formulario para rellenar los datos de la obra literária.
    """
    list_display = ['title', 'author', 'genre']
    search_fields = ['title', 'author__first_name', 'author__last_name']
    list_filter=['genre']
    autocomplete_fields = ['author', 'classic_author', 'genre']
    display_raw = True # Muestra las coordenadas debajo del mapa por si acaso
    settings_overrides = {
        'DEFAULT_CENTER': (40.4167, -3.7037), 
        'DEFAULT_ZOOM': 6,
        'MAX_ZOOM':14,
    }
    inlines = [ImageInline, LinkInline]

    class Media:
        js = (
            # Referenciamos el mismo asset que ya inyecta el widget (LeafletGeoAdmin,
            # via include_media) en vez de duplicarlo desde unpkg: Django lo
            # deduplica por URL y así garantizamos que window.L existe antes de
            # cargar Control.Geocoder.js, sin depender del orden de fusión de Media.
            'leaflet/leaflet.js',
            'https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.js',
            'admin/js/leaflet_setup.js',
        )
        css = {
            'all': ('https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.css',)
        }
