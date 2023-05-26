from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings

from blog.models import Category, Post


class ViewsTestSettings(TestCase):   # python manage.py test blog.tests.test_views
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        settings.SECRET_KEY = "some_test_secret_key!"   # до force_login иначе последний не сработает
        cls.user = get_user_model().objects.create_user(username='test_user',
                                                        email='test_user@mail.ru',
                                                        password='test_user_password')
        cls.not_owner_user = get_user_model().objects.create_user(username='test_not_owner_user',
                                                                  email='test_not_owner_user_password@mail.ru',
                                                                  password='test_not_owner_user_password')

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

        cls.client = Client()
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.auth_not_owner_user_client = Client()
        cls.auth_not_owner_user_client.force_login(cls.not_owner_user)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        settings.SECRET_KEY = None

    def test_post_list_view(self):
        response = self.client.get(reverse('blog:home'))
        object_list = response.context.get('object_list')
        self.assertTrue(object_list)                                # object_list не пуст
        self.assertEqual(response.context.get('selected'), 'home')  # extra_context содержит home
        self.assertTrue(len(object_list), 1)                        # только опубликованные посты

    def test_post_detail_view(self):
        response = self.client.get(reverse('blog:post-detail', kwargs={'slug': 'nazvanie-opublikovannogo-posta'}))
        self.assertEqual(response.context.get('object'), self.post_published)
        self.assertEqual(response.context.get('selected'), 'detail')    # extra_context содержит detail

    def test_post_create_view_not_auth_user(self):
        data = {
            'cat': self.category,
            'title': 'Post name',
            'slug': 'nazvanie-posta',
            'body': 'Post text.',
            'status': 'PB'
        }
        expected_redirect_url = '/members/login/?next=%2Fblog%2Fnew-post%2F'
        response = self.client.post(reverse('blog:post-new'), data=data)
        self.assertRedirects(response,
                             expected_url=expected_redirect_url,
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)

    def test_post_create_view_auth_user(self):
        data = {
            'cat': self.category.id,
            'title': 'Saved Post name',
            'slug': 'saved-post-name',
            'body': 'Post text.',
            'status': 'DF'
        }
        response = self.auth_client.post(reverse('blog:post-new'), data=data, follow=True)

        if response.context.get('form'):
            print(f"\nОшибка при валидации формы: {response.context.get('form').errors}")

        self.assertTrue(response.status_code, 200)
        saved_post = Post.objects.get(title='Saved Post name')
        self.assertEqual(saved_post.cat, self.category)
        self.assertEqual(saved_post.title, data['title'])
        self.assertEqual(saved_post.slug, data['slug'])
        self.assertEqual(saved_post.body, data['body'])
        self.assertEqual(saved_post.status, data['status'])

    def test_post_update_view_not_auth_user(self):
        data = {
            'cat': self.category.id,
            'title': 'Название поста',
            'slug': 'nazvanie-posta',
            'body': 'Текст поста modif',
            'status': 'PB'
        }
        expected_redirect_url = '/members/login/?next=/blog/update-post/nazvanie-posta/'
        response = self.client.post(reverse('blog:post-update', kwargs={'slug': 'nazvanie-posta'}), data=data)
        self.assertRedirects(response,
                             expected_url=expected_redirect_url,
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)

    def test_post_update_view_auth_user_not_owner(self):
        data = {
            'cat': self.category.id,
            'title': 'Название поста',
            'slug': 'nazvanie-posta',
            'body': 'Текст поста modif',
            'status': 'PB'
        }
        response = self.auth_not_owner_user_client.post(reverse('blog:post-update', kwargs={'slug': 'nazvanie-posta'}),
                                                        data=data)
        self.assertEqual(response.status_code, 403)

    def test_post_update_view_auth_user_owner(self):
        data = {
            'cat': self.category.id,
            'title': 'Название поста',
            'slug': 'nazvanie-posta',
            'body': 'Текст поста modif',
            'status': 'PB'
        }
        response = self.auth_client.post(reverse('blog:post-update', kwargs={'slug': 'nazvanie-posta'}), data=data)

        self.assertTrue(response.status_code, 200)
        saved_post = Post.objects.get(title='Название поста')
        self.assertEqual(saved_post.cat, self.category)
        self.assertEqual(saved_post.title, data['title'])
        self.assertEqual(saved_post.slug, data['slug'])
        self.assertEqual(saved_post.body, data['body'])
        self.assertEqual(saved_post.status, data['status'])

    def test_post_by_category_list_view(self):
        response = self.client.get(reverse('blog:category', kwargs={'slug': self.category.slug}))
        object_list = response.context.get('object_list')
        self.assertTrue(object_list)                                # object_list не пуст
        self.assertTrue(len(object_list), 1)                        # только опубликованные посты
