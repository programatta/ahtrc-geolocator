from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
