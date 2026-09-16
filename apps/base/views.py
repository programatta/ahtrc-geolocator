from django.contrib import messages
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
