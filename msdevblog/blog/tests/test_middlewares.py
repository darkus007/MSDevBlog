from django.contrib.auth import get_user_model
from django.test import TestCase
from django.conf import settings

from blog.models import Category, Post
from blog.middlewares import categories, new_posts, tags_list


class MiddlewaresTestCase(TestCase):   # python manage.py test blog.tests.test_middlewares
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        settings.SECRET_KEY = "some_test_secret_key!"
        cls.user = get_user_model().objects.create_user(username='test_user',
                                                        email='test_user@mail.ru',
                                                        password='test_user_password')

        cls.category = Category.objects.create(
            title='Тест категории',
            slug='test-category'
        )
        Post.objects.create(
            user=cls.user,
            cat=cls.category,
            title='Название поста',
            slug='None',
            body='Текст поста',
        )

        cls.post = Post.objects.create(
            user=cls.user,
            cat=cls.category,
            title=f'Название опубликованного поста',
            slug='nazvanie-opublikovannogo-posta',
            body='Текст опубликованного поста',
            status='PB'
        )
        cls.post.tags.add('tag')

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        settings.SECRET_KEY = None

    def test_categories(self):
        cats = categories(None)
        self.assertEqual(cats['categories'][0]['title'], self.category.title)
        self.assertEqual(cats['categories'][0]['slug'], self.category.slug)

    def test_tags_list(self):
        tags = tags_list(None)
        self.assertEqual(tags['tags_list'][0].name, 'tag')
        self.assertEqual(tags['tags_list'][0].slug, 'tag')

    def test_new_posts_fields(self):
        posts = new_posts(None)
        self.assertEqual(posts['new_posts'][0]['title'], self.post.title)
        self.assertEqual(posts['new_posts'][0]['slug'], self.post.slug)

    def test_new_posts_published_only(self):
        self.assertEqual(len(new_posts(None)['new_posts']), 1)

    def test_new_posts_max_length(self):
        for x in range(8):
            Post.objects.create(
                user=self.user,
                cat=self.category,
                title=f'Название опубликованного поста {x}',
                slug='nazvanie-opublikovannogo-posta',
                body='Текст опубликованного поста',
                status='PB'
            )
        self.assertEqual(len(Post.published.all()), 9)
        self.assertEqual(len(new_posts(None)['new_posts']), 5)
