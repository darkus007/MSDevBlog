from django.contrib.auth.models import AbstractUser
from django.db import models


class AdvUser(AbstractUser):
    email = models.EmailField(unique=True, max_length=254, verbose_name='E-mail')
    bio = models.TextField(null=True, blank=True, verbose_name='О себе')
    git = models.CharField(null=True, blank=True, max_length=255, verbose_name='git')
    is_email_activated = models.BooleanField(default=False, verbose_name='Прошел активацию email?')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
