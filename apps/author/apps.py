from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuthorConfig(AppConfig):
    name = 'apps.author'
    verbose_name = _('Literary works')

    def ready(self):
        # Workaround: django-leaflet 0.34.0 builds PLUGINS[PLUGIN_FORMS]['js'/'css']
        # with lazy(static, str)(url), whose __proxy__ result isn't a real `str`
        # instance. Django's forms.widgets.Media (this Django version) requires a
        # literal `str` (wrapped into Script/Stylesheet) or an object with
        # __html__(), so rendering LeafletAdminWidget.media crashes otherwise.
        # Force-resolve those URLs to plain strings once apps are loaded.
        from leaflet import PLUGINS, PLUGIN_FORMS
        forms_plugin = PLUGINS.get(PLUGIN_FORMS, {})
        for key in ('js', 'css'):
            forms_plugin[key] = [str(url) for url in forms_plugin.get(key, [])]

        from . import signals  # noqa: F401
