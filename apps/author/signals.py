"""
signals.py
Acciones sobre el modelo Image para evitar el incremento de imagenes huerfanas
de las registradas en la base de datos.
"""
import os

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import Imagen


@receiver(post_delete, sender=Imagen)
def delete_imagen_file(sender, instance, **kwargs):
    """
    Elimina del sistema de archivos la imagen eliminada de la base de datos.
    """
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)

@receiver(pre_save, sender=Imagen)
def delete_old_imagen_when_edit(sender, instance, **kwargs):
    """
    Elimina del sistema de archivos la imagen antigua asociada al registro de 
    la base de datos y establece la nueva imagen.
    """
    # Si el registro es nuevo, no hay imagen vieja que borrar
    if not instance.pk:
        return False

    try:
        # Obtenemos el registro tal y como está en la base de datos actualmente
        old_image = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return False

    # Comparamos el archivo viejo con el nuevo
    old_image_file = old_image.image
    new_image_file = instance.image

    if old_image_file and old_image_file != new_image_file:
        if os.path.isfile(old_image_file.path):
            os.remove(old_image_file.path)
