from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django import forms

from .models import AdvUser
from .utilities import send_activation_notification


class UserRegistrationForm(UserCreationForm):
    """ Форма регистрации пользователя. """
    # делаем поле обязательным
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'required input_field'}))

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2')
        labels = {'username': 'Логин'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'required input_field'
        self.fields['password1'].widget.attrs['class'] = 'required input_field'
        self.fields['password2'].widget.attrs['class'] = 'required input_field'

    def save(self, commit=True):
        """
        Переопределяем метод save для отправки сообщения
        активации (подтверждения) введенного при регистрации e-mail
        """
        user = super().save(commit=False)
        user.is_email_activated = False
        if commit:
            user.save()
        send_activation_notification(user)
        return user


class UserProfileForm(forms.Form):
    """ Форма обновления профиля пользователя. """
    first_name = forms.CharField(max_length=150, required=False, label='Имя',
                                 widget=forms.TextInput(attrs={'class': 'required input_field'}))
    last_name = forms.CharField(max_length=150, required=False, label='Фамилия',
                                widget=forms.TextInput(attrs={'class': 'required input_field'}))
    bio = forms.CharField(widget=forms.Textarea, required=False, label='О себе')
    git = forms.CharField(max_length=255, required=False, label='Git-репозиторий',
                          widget=forms.TextInput(attrs={'class': 'required input_field'}))


class UserPasswordChangeForm(PasswordChangeForm):
    """ Форма смены пароля пользователя. """
    old_password = forms.CharField(max_length=100,
                                   widget=forms.PasswordInput(attrs={'class': 'required input_field', 'type': 'password'}),
                                   label='Старый пароль')
    new_password1 = forms.CharField(max_length=100,
                                    widget=forms.PasswordInput(attrs={'class': 'required input_field', 'type': 'password'}),
                                    label='Новый пароль')
    new_password2 = forms.CharField(max_length=100,
                                    widget=forms.PasswordInput(attrs={'class': 'required input_field', 'type': 'password'}),
                                    label='Подтверждение нового пароля')

    class Meta:
        model = AdvUser
        fields = ('old_password', 'new_password1', 'new_password2')
