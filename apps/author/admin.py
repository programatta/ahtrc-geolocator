"""
admin.py
Vista de administración para:
- Autores
- Obras literarias.
"""
from django.contrib import admin
from django.contrib.postgres.search import TrigramSimilarity
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
    # unaccent cubre la búsqueda sin tildes (p. ej. "cortazar" -> "Cortázar");
    # como refuerzo, get_search_results() añade también una búsqueda por
    # similitud (pg_trgm) para lo que unaccent no resuelve por sí solo —
    # apellidos con puntuación irregular ("O’Neil", comillas incrustadas) o
    # errores tipográficos reales.
    search_fields = ['first_name__unaccent', 'last_name__unaccent']

    def get_search_results(self, request, queryset, search_term):
        exact_qs, may_have_duplicates = super().get_search_results(request, queryset, search_term)
        if search_term:
            trigram_qs = queryset.annotate(
                similarity=(
                    TrigramSimilarity('first_name', search_term)
                    + TrigramSimilarity('last_name', search_term)
                )
            ).filter(similarity__gt=0.3)
            exact_qs |= trigram_qs
            may_have_duplicates = True
        return exact_qs, may_have_duplicates


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
    list_display = ['title', 'author', 'genre', 'lwith_location']
    search_fields = ['title__unaccent', 'author__first_name__unaccent', 'author__last_name__unaccent']
    list_filter = ['genre', ('location', admin.EmptyFieldListFilter)]
    autocomplete_fields = ['author', 'classic_author', 'genre']
    display_raw = True # Muestra las coordenadas debajo del mapa por si acaso
    settings_overrides = {
        'DEFAULT_CENTER': (40.4167, -3.7037), 
        'DEFAULT_ZOOM': 6,
        'MAX_ZOOM':14,
    }
    inlines = [ImageInline, LinkInline]

    def lwith_location(self, obj):
        return obj.location is not None
    lwith_location.short_description = _('with_location')
    lwith_location.boolean = True

    class Media:
        js = (
            # Referenciamos el mismo asset que ya inyecta el widget (LeafletGeoAdmin,
            # via include_media) en vez de duplicarlo desde unpkg: Django lo
            # deduplica por URL y así garantizamos que window.L existe antes de
            # cargar Control.Geocoder.js, sin depender del orden de fusión de Media.
            'leaflet/leaflet.js',
            # leaflet-control-geocoder 4.0.0 servido en local (admin/vendor/) en vez de
            # unpkg.com sin versión fijada: evita depender de la disponibilidad del CDN
            # y de que no cambie de contenido entre despliegues.
            'admin/vendor/leaflet-control-geocoder/Control.Geocoder.js',
            'admin/js/leaflet_setup.js',
        )
        css = {
            'all': ('admin/vendor/leaflet-control-geocoder/Control.Geocoder.css',)
        }
