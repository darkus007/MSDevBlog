from django.urls import path, include
from members.views import *


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('', include('django.contrib.auth.urls')),
]
