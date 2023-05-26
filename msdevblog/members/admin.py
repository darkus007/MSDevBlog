import datetime

from django.contrib import admin

from .models import AdvUser
from .utilities import send_activation_notification


@admin.action(description="Отправка писем для активации email")
def send_activation_email(modeladmin, request, queryset):
    for user in queryset:
        if not user.is_email_activated:
            send_activation_notification(user)
    modeladmin.message_user(request, 'Письма для активации email отправлены')


class NonActivatedFilter(admin.SimpleListFilter):
    title = 'Прошли активацию email?'
    parameter_name = 'actstate'

    def lookups(self, request, model_admin):
        return (
            ('activated', 'Прошли'),
            ('threedays', 'Не прошли более 3 дней'),
            ('week', 'Не прошли более недели'),
        )

    def queryset(self, request, queryset):
        val = self.value()
        if val == 'activated':
            return queryset.filter(is_active=True, is_email_activated=True)
        elif val == 'threedays':
            d = datetime.date.today() - datetime.timedelta(days=3)
            return queryset.filter(is_active=True, is_email_activated=False,
                                   date_joined__date__lt=d)
        elif val == 'week':
            d = datetime.date.today() - datetime.timedelta(weeks=1)
            return queryset.filter(is_active=True, is_email_activated=False,
                                   date_joined__date__lt=d)


@admin.register(AdvUser)
class AdvUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name',
                    'last_name', 'email', 'is_email_activated']  # поля для отображения
    list_filter = [NonActivatedFilter]    # правая боковая панель для фильтрации по этим полям
    search_fields = ['username']   # поиск по этим полям
    actions = (send_activation_email, )
