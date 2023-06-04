from django import forms

from captcha.fields import CaptchaField
from django.core.exceptions import ValidationError
from django_ckeditor_5.widgets import CKEditor5Widget

from msdevblog.utilites import slugify
from .models import Post, Comment

from taggit.forms import TagWidget


class PostForm(forms.ModelForm):

    def clean_slug(self):
        # Не запускается, если поле "slug" пустое!!!
        # По этой причине оно скрыто и установлено значение 'none'.
        return slugify(self.cleaned_data['title'])

    def clean_tags(self):
        # Приложение виснет, если пытается записать теги с одинаковым slug
        # Например пользователь передан теги 'Flask' и 'Фласк',
        # дли них будет сформирован одинаковый slug = 'flask'
        # при попытке сохранения это приведет к зависанию приложения.
        tags = self.cleaned_data['tags']
        tags_slug = {slugify(tag) for tag in tags}
        if len(tags) != len(tags_slug):
            raise ValidationError("Проверьте поле Теги, возможно имеются теги с одинаковым смыслом.")
        return tags

    class Meta:
        model = Post
        fields = ('cat', 'title', 'slug', 'body', 'tags', 'status')

        widgets = {
            'cat': forms.Select(attrs={'class': 'required input_field'}),
            'title': forms.TextInput(attrs={'class': 'required input_field',
                                            'placeholder': 'Укажите название поста'}),
            # метод clean_slug не запускается, если поле "slug" пустое,
            # по этой причине оно скрыто и добавлено значение "none".
            'slug': forms.TextInput(attrs={'class': 'required input_field',
                                           'placeholder': 'URL-адрес поста (slug)',
                                           'value': 'none', 'type': 'hidden'}),
            'body': CKEditor5Widget(attrs={'class': 'django_ckeditor_5 input_field'}, config_name='extends'),
            'tags': TagWidget(attrs={'class': 'required input_field'}),
            'status': forms.Select(attrs={'class': 'required input_field'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
        labels = {'body': 'Ваш комментарий'}

        widgets = {
            'body': forms.Textarea(attrs={'class': 'required input_field'}),
        }


class FeedbackForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['captcha'].widget.attrs['class'] = 'required input_field'

    theme = forms.CharField(max_length=255, label='Тема сообщения',
                            widget=forms.TextInput(attrs={'class': 'required input_field'}))
    text = forms.CharField(widget=forms.Textarea, label='Текст сообщения')
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'required input_field'}),
                             label='Ваш e-mail для обратной связи')
    captcha = CaptchaField(label='Введите текст с картинки',
                           error_messages={'invalid': 'Неверно указан текст с картинки'})
