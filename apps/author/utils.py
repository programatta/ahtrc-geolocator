"""
utils.py

Funciones de utilidad compartida
"""
import os
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext

def path_and_rename(instance, filename):
    ext = filename.split('.')[-1]
    # set filename as random string
    filename = f'{uuid4().hex}.{ext}'
    # return the whole path to the file
    return os.path.join('files', filename)


MAX_IMAGE_SIZE_BYTES = 2 * 1024 * 1024


def validate_image_max_size(value):
    if value.size > MAX_IMAGE_SIZE_BYTES:
        raise ValidationError(
            gettext('File too large. Size should not exceed %(max_size)s.')
            % {'max_size': filesizeformat(MAX_IMAGE_SIZE_BYTES)}
        )
