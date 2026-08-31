from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.ClassicAuthor)
class ClassicAuthorAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
