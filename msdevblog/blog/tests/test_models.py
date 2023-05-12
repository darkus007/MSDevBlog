"""
Тест models приложения blog.

Тестируем методы моделей Category и Post,
некоторые настройки полей этих моделей.

Примечание:
При использовании методов класса setUpClass() и tearDownClass()
обязательно вызываем в них super(): super().setUpClass() и super().tearDownClass().
Без вызова super() все тесты сработают нормально, но получим ошибку:

AttributeError: type object '<имя_класса>' has no attribute 'cls_atomics'

Эта ошибка возникает именно в Django: в Unittest для Python такой проблемы нет.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from blog.models import Category, Post


class Settings(TestCase):   # python manage.py test blog.tests.test_models
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(username='test_user', password='test_user_password')

        cls.category = Category.objects.create(
            title='Тест категории',
            slug='test-category'
        )

        cls.post = Post.objects.create(
            user=cls.user,
            cat=cls.category,
            title='Название поста',
            slug='nazvanie-posta',
            body='Текст поста',
        )

        cls.post_published = Post.objects.create(
            user=cls.user,
            cat=cls.category,
            title='Название опубликованного поста',
            slug='nazvanie-opublikovannogo-posta',
            body='Текст опубликованного поста',
            status='PB'
        )

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()


class PostTestCase(Settings):
    def test_auto_add_slug(self):
        post = Post.objects.create(
            user=self.user,
            cat=self.category,
            title='Название статьи 2',
            body='Текст статьи 2'
        )
        post.save()
        self.assertEqual(post.slug, 'nazvanie-stati-2')

    def test_published_manager(self):
        self.assertEqual(len(Post.published.all()), 1)

    def test_default_manager(self):
        self.assertEqual(len(Post.objects.all()), 2)

    def test_related_name_for_user_model(self):
        self.assertTrue(self.user.posts.all())

    def test_related_name_for_category_model(self):
        self.assertTrue(self.category.posts.all())

    def test_str(self):
        self.assertEqual(f'{self.post.title} - {self.post.user}', self.post.__str__())

    def test_slug_field(self):
        """
        Если класс SlugField изменится на другой, проверяем, что поле проиндексировано и уникально.
        """
        self.assertTrue(self.post._meta.get_field('slug').unique_for_date)
        self.assertTrue(self.post._meta.get_field('slug').db_index)

    def test_verbose_name(self):
        """ verbose_name в полях совпадает с ожидаемым. """
        field_verbose = {
            'user': 'Автор поста',
            'cat': 'Категория',
            'title': 'Название поста',
            'slug': 'URL',
            'body': 'Текст поста',
            'time_created': 'Время создания',
            'time_updated': 'Время последнего изменения',
            'status': 'Статус'
        }
        for field, expected_value in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name, expected_value)


class CategoryTestCase(Settings):
    def test_fields(self):
        self.assertEqual(self.category._meta.get_field('title').verbose_name, 'Название категории')
        self.assertEqual(self.category._meta.get_field('slug').verbose_name, 'URL')
        self.assertEqual(self.category._meta.get_field('slug').unique, True)
        self.assertEqual(self.category._meta.get_field('slug').db_index, True)

    def test_str(self):
        self.assertEqual(self.category.title, self.category.__str__())
