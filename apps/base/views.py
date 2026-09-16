from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.utils.translation import gettext
from django.views.generic import FormView

from apps.base.forms import RequestLoginCodeForm
from apps.base.models import LoginCode

UserModel = get_user_model()


class RequestLoginCodeView(FormView):
    template_name = 'base/request_login_code.html'
    form_class = RequestLoginCodeForm
    success_url = reverse_lazy('admin:login')

    def get_context_data(self, **kwargs):
        # Al no ser una vista del admin, no pasa por AdminSite.each_context()
        # de forma automática: sin esto, site_header/site_title/index_title
        # (conf/urls.py) caen a los valores por defecto de Django en esta
        # plantilla, en vez de los del proyecto. "title" tampoco lo pone
        # nadie por defecto (admin.site.login() sí lo hace para su propia
        # vista) — lo usa el <title> del tab del navegador.
        context = {**admin.site.each_context(self.request), **super().get_context_data(**kwargs)}
        context['title'] = gettext('Request code')
        return context

    def form_valid(self, form):
        username = form.cleaned_data['username']
        user = UserModel._default_manager.filter(
            **{UserModel.USERNAME_FIELD: username}
        ).first()
        if user is not None and user.is_active and user.is_staff and user.email:
            LoginCode.objects.create_for_user(user)

        # Mismo mensaje exista o no el usuario, para no filtrar qué nombres
        # de usuario son válidos (evita enumeración de usuarios).
        messages.success(
            self.request,
            gettext('If the user exists, an access code has been sent to their email.'),
        )
        return super().form_valid(form)
