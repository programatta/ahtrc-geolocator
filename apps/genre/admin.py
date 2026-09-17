from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name__unaccent']
    readonly_fields = ['is_unassigned']

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if not request.user.is_superuser and 'is_unassigned' in fields:
            fields.remove('is_unassigned')
        return fields

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.is_unassigned and not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)
