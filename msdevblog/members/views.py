from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_POST, require_GET
from django.views.generic import CreateView
from django.core.signing import BadSignature
from django.contrib import messages
from django.forms.models import model_to_dict

from .forms import UserRegistrationForm, UserProfileForm, UserPasswordChangeForm
from .models import AdvUser
from .utilities import signer, send_activation_notification
from blog.models import Post


class UserRegistrationView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')
    extra_context = {'selected': 'register'}


class UserPasswordChangeView(PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = 'registration/change_password.html'
    success_url = reverse_lazy('password-changed')


def password_changed(request):
    return render(request, 'registration/password_changed.html')


@login_required(login_url=reverse_lazy('login'))
@require_GET
def user_profile(request):
    """ Отображение профиля пользователя. """
    user_posts = Post.objects.filter(user=request.user).values('title', 'status', 'slug')
    return render(request, 'registration/user_profile.html', {'user_posts': user_posts, 'selected': 'profile'})


@login_required(login_url=reverse_lazy('login'))
def user_update_profile(request):
    """ Обновление профиля пользователя. """
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            # Поля формы успешно прошли валидацию, обновляем пользователя
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.bio = form.cleaned_data['bio']
            request.user.git = form.cleaned_data['git']
            request.user.save()
            messages.add_message(request, messages.SUCCESS, f'Профиль обновлен.')
            return redirect(reverse('profile'))
    else:
        form = UserProfileForm(data=model_to_dict(request.user))
    return render(request, 'registration/user_update_profile.html', {'form': form, 'selected': 'profile'})


@require_GET
def user_email_activate(request, sign):
    """
    Функция для активации e-mail пользователя.
    Принимает сообщение о подтверждении адреса электронной почты
    и если все верно и подпись не скомпрометирована, активирует e-mail пользователя.
    """
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'registration/bad_signature.html')
    user = get_object_or_404(AdvUser, username=username)
    if user.is_email_activated:
        template = 'registration/user_is_activated.html'
    else:
        template = 'registration/activation_done.html'
        user.is_email_activated = True
        user.save()
    return render(request, template)


@login_required(login_url=reverse_lazy('login'))
def send_email_activate_letter(request):
    """
    Повторно отправляет письмо для подтверждения e-mail.
    """
    send_activation_notification(request.user)
    messages.add_message(request, messages.SUCCESS,
                         f'Электронной письмо отправлено. Проверьте почтовый ящик "{request.user.email}".')
    return HttpResponseRedirect(reverse('profile'))
