from django.conf import settings
from django.db import models
from django.urls import reverse

# стандартная библиотека не работает с русскими символами, используем свою
from msdevblog.utilites import slugify


class PublishedManager(models.Manager):
    """ Менеджер для модели, возвращает только опубликованные посты """
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Category(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название категории')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='URL')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Черновик'           # Draft
        PUBLISHED = 'PB', 'Опубликовано'   # Published

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts', verbose_name='Автор поста')
    # on_delete=models.SET(1) - первая кат-рия будет "Все категории" задается в настройках
    cat = models.ForeignKey(Category, on_delete=models.SET(1),
                            related_name='posts', verbose_name='Категория')
    title = models.CharField(max_length=255, verbose_name='Название поста')
    slug = models.SlugField(max_length=255, unique_for_date='time_created', verbose_name='URL')
    body = models.TextField(verbose_name='Текст поста')
    time_created = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    time_updated = models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')
    status = models.CharField(max_length=2, choices=Status.choices,
                              default=Status.DRAFT, verbose_name='Статус')

    published = PublishedManager()
    objects = models.Manager()  # указываем и менеджер по умолчанию, иначе он будет недоступен

    def __str__(self):
        return f'{self.title} - {self.user}'

    def save(self, *args, **kwargs):
        """ Добавляем slug на основе поля title, если он не был передан """
        if not self.slug or self.slug == '':
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:post-detail', args=[self.slug])

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-time_created', 'cat']
