from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.conf import settings

from blog.forms import PostForm, CommentForm
from blog.models import Post, Category, Comment


class FormsTestCaseSettings(TestCase):  # python manage.py test blog.tests.test_forms
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        settings.SECRET_KEY = "some_test_secret_key!"

        cls.user = get_user_model().objects.create_user(username='test_user',
                                                        email='test@testsite.ru',
                                                        password='test_user_password')
        cls.client = Client()
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

        cls.category = Category.objects.create(
            title='Category name',
            slug='category-name'
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
        settings.SECRET_KEY = None


class PostFormTestCase(FormsTestCaseSettings):
    def test_save(self):
        form_data = {
            'cat': self.category,
            'title': 'Post name',
            'slug': 'nazvanie-posta',
            'body': 'Post text.',
            'status': 'PB'
        }

        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        form.instance.user = self.user      # передаем пользователя
        form.save()
        self.assertTrue(Post.objects.filter(title='Post name'))

    def test_auto_add_slug(self):
        form_data = {
            'cat': self.category,
            'title': 'Post name slug тест',
            'slug': 'none',
            'body': 'Post text.',
            'status': 'PB'
        }

        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        form.instance.user = self.user      # передаем пользователя
        form.save()
        saved_post = Post.objects.get(title='Post name slug тест')
        self.assertTrue(saved_post.slug, 'post-name-slug-test')


class CommentFormTestCase(FormsTestCaseSettings):
    def test_save(self):
        form_data = {
            'body': 'New comment.'
        }

        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        form.instance.user = self.user              # передаем пользователя
        form.instance.post = self.post_published    # передаем пост
        form.save()
        self.assertTrue(Comment.objects.filter(body='New comment.'))
