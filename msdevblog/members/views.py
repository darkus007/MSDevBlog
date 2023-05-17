from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import UserRegistrationForm


class UserRegistrationView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')
