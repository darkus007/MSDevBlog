from django import forms

from msdevblog.utilites import slugify
from .models import Post


class PostForm(forms.ModelForm):

    def clean_slug(self):
        """
        Не запускается, если поле "slug" пустое!!!
        По этой причине оно скрыто и добавлено значение none.
        """
        return slugify(self.cleaned_data['title'])

    class Meta:
        model = Post
        fields = ('cat', 'title', 'slug', 'body', 'status')

        widgets = {
            'cat': forms.Select(attrs={'class': 'required input_field'}),
            'title': forms.TextInput(attrs={'class': 'required input_field',
                                            'placeholder': 'Укажите название поста'}),
            # метод clean_slug не запускается, если поле "slug" пустое,
            # по этой причине оно скрыто и добавлено значение "none".
            'slug': forms.TextInput(attrs={'class': 'required input_field',
                                           'placeholder': 'URL-адрес поста (slug)',
                                           'value': 'none', 'type': 'hidden'}),
            'body': forms.Textarea(attrs={'class': 'required input_field'}),
            'status': forms.Select(attrs={'class': 'required input_field'}),
        }
