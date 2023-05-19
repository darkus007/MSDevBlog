from django.urls import path, include
from members.views import *


urlpatterns = [
    path('register/activate/<str:sign>/', user_email_activate, name='email-activate'),
    path('register/', UserRegistrationView.as_view(), name='register'),

    path('repeat-send-email/', send_email_activate_letter, name='repeat-send-email'),
    path('profile/', user_profile, name='profile'),

    path('password/', UserPasswordChangeView.as_view(), name='change-password'),
    path('password-success/', password_changed, name='password-changed'),

    path('', include('django.contrib.auth.urls')),
]
