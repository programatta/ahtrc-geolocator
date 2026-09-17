from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from . import models


@admin.register(models.MapConfig)
class MapConfigAdmin(admin.ModelAdmin):
    """
    MapConfigAdmin
    Administración del singleton MapConfig: sin alta (ya existe la única
    fila desde la migración de datos) ni borrado, y el listado redirige
    directamente al formulario de edición de esa fila.
    """
    list_display = ['is_open']

    def has_add_permission(self, request):
        return not models.MapConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = models.MapConfig.load()
        return HttpResponseRedirect(
            reverse('admin:front_mapconfig_change', args=[obj.pk])
        )
