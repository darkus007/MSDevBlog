from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.views import LoginView
from django.urls import path, include

from .forms import CustomPasswordResetForm
from .views import UserRegistrationView, UserPasswordChangeView
from .views import user_email_activate, send_email_activate_letter, password_changed
from .views import user_profile, user_update_profile


urlpatterns = [
    path("login/", LoginView.as_view(extra_context={'selected': 'login'}), name="login"),
    path('register/activate/<str:sign>/', user_email_activate, name='email-activate'),
    path('register/', UserRegistrationView.as_view(), name='register'),

    path('repeat-send-email/', send_email_activate_letter, name='repeat-send-email'),
    path('profile/', user_profile, name='profile'),
    path('update-profile/', user_update_profile, name='update-profile'),

    path('password/', UserPasswordChangeView.as_view(), name='change-password'),
    path('password-success/', password_changed, name='password-changed'),
    path('password_reset/', PasswordResetView.as_view(form_class=CustomPasswordResetForm, ), name='password_reset'),
    path('', include('django.contrib.auth.urls')),
]
