from django.contrib.auth.forms import UserCreationForm
from django import forms

from .models import AdvUser


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'required input_field'}))

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2')
        labels = {'username': 'Логин'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'required input_field'
        self.fields['email'].widget.attrs['class'] = 'required input_field'
        self.fields['password1'].widget.attrs['class'] = 'required input_field'
        self.fields['password2'].widget.attrs['class'] = 'required input_field'
