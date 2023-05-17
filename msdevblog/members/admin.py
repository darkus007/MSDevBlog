from django.contrib import admin

from .models import AdvUser


@admin.register(AdvUser)
class AdvUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name',
                    'last_name', 'email', 'is_email_activated']  # поля для отображения
    list_filter = ['username', 'email', 'is_email_activated']    # правая боковая панель для фильтрации по этим полям
    search_fields = ['username']   # поиск по этим полям
