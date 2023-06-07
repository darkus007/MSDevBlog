from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from django.contrib.messages import get_messages

from captcha.conf import settings as captcha_settings

from blog.models import Category, Post, Comment


class ViewsTestSettings(TestCase):  # python manage.py test blog.tests.test_views
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        settings.SECRET_KEY = "some_test_secret_key!"  # до force_login иначе пользователь не зарегистрируется
        captcha_settings.CAPTCHA_TEST_MODE = True  # отключаем проверку captcha
        cls.user = get_user_model().objects.create_user(username='test_user',
                                                        email='test_user@mail.ru',
                                                        password='test_user_password')
        cls.not_owner_user = get_user_model().objects.create_user(username='test_not_owner_user',
                                                                  email='test_not_owner_user_password@mail.ru',
                                                                  password='test_not_owner_user_password')
        cls.user_is_email_activated_true = get_user_model().objects.create_user(username='email_activated_user',
                                                                                email='email_activated@mail.ru',
                                                                                password='email_activated_password',
                                                                                is_email_activated=True)

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
            tags='tag'
        )

        cls.post_published = Post.objects.create(
            user=cls.user,
            cat=cls.category,
            title='Название опубликованного поста',
            slug='nazvanie-opublikovannogo-posta',
            body='Текст опубликованного поста',
            status='PB'
        )
        cls.post_published.tags.add('tag')

        cls.client = Client()
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.auth_not_owner_user_client = Client()
        cls.auth_not_owner_user_client.force_login(cls.not_owner_user)
        cls.auth_email_activated_client = Client()
        cls.auth_email_activated_client.force_login(cls.user_is_email_activated_true)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        settings.SECRET_KEY = None
        captcha_settings.CAPTCHA_TEST_MODE = False

    def test_post_list_view(self):
        response = self.client.get(reverse('blog:home'))
        object_list = response.context.get('object_list')
        self.assertTrue(object_list)  # object_list не пуст
        self.assertEqual(response.context.get('selected'), 'home')  # extra_context содержит home
        self.assertTrue(len(object_list), 1)  # только опубликованные посты

    def test_post_list_view_queries(self):
        """ Тестируем количество запросов в БД. """
        with CaptureQueriesContext(connection) as queries:
            cache.delete('categories')  # может сохраниться от предыдущих запросов
            cache.delete('new_posts')
            cache.delete('tags')
            response = self.client.get(reverse('blog:home'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(queries), 6, "Увеличилось число запросов в БД!")

    def test_post_detail_get_published(self):
        response = self.client.get(reverse('blog:post-detail', kwargs={'slug': 'nazvanie-opublikovannogo-posta'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('object'), self.post_published)
        self.assertFalse(response.context.get('is_author'))

    def test_post_detail_get_draft(self):
        response = self.client.get(reverse('blog:post-detail', kwargs={'slug': 'nazvanie-posta'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('object'), self.post)
        self.assertFalse(response.context.get('is_author'))

    def test_post_detail_get_404(self):
        response = self.client.get(reverse('blog:post-detail', kwargs={'slug': 'not-found'}))
        self.assertTemplateUsed(response, 'blog/base.html', 'blog/includes/main_menu.html')
        self.assertEqual(response.status_code, 200)

    def test_post_detail__post_not_auth(self):
        form_data = {'body': 'Comment post_not_auth'}
        response = self.client.post(
            reverse('blog:post-detail', kwargs={'slug': 'nazvanie-opublikovannogo-posta'}), data=form_data)
        self.assertEqual(response.context.get('object'), self.post_published)
        self.assertFalse(Comment.objects.filter(body='Comment post_not_auth'))
        self.assertFalse(response.context.get('is_author'))

    def test_post_detail__post_auth_user_email_activated_false(self):
        form_data = {'body': 'Comment email_activated_false'}
        response = self.auth_client.post(    # у данного пользователя e-mail не подтвержден
            reverse('blog:post-detail', kwargs={'slug': 'nazvanie-opublikovannogo-posta'}), data=form_data)
        self.assertEqual(response.context.get('object'), self.post_published)
        self.assertFalse(Comment.objects.filter(body='Comment email_activated_false'))
        self.assertTrue(response.context.get('is_author'))

    def test_post_detail__post_auth_user_email_activated_true(self):
        form_data = {'body': 'Comment email_activated_false'}
        response = self.auth_email_activated_client.post(
            reverse('blog:post-detail', kwargs={'slug': 'nazvanie-opublikovannogo-posta'}), data=form_data)
        self.assertEqual(response.context.get('object'), self.post_published)
        self.assertTrue(Comment.objects.filter(body='Comment email_activated_false'))
        self.assertFalse(response.context.get('is_author'))

    def test_post_detail_view_queries(self):
        """ Тестируем количество запросов в БД. """
        with CaptureQueriesContext(connection) as queries:
            cache.delete('categories')  # может сохраниться от предыдущих запросов
            cache.delete('new_posts')
            cache.delete('tags')
            response = self.client.get(reverse('blog:post-detail', kwargs={'slug': 'nazvanie-opublikovannogo-posta'}))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(queries), 6, "Увеличилось число запросов в БД!")

    def test_post_create_view_not_auth_user(self):
        data = {
            'cat': self.category,
            'title': 'Post name',
            'slug': 'nazvanie-posta',
            'body': 'Post text.',
            'tags': 'tag',
            'status': 'PB'
        }
        expected_redirect_url = '/members/login/?next=%2Fblog%2Fnew-post%2F'
        response = self.client.post(reverse('blog:post-new'), data=data)
        self.assertRedirects(response,
                             expected_url=expected_redirect_url,
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)

    def test_post_create_view_auth_user_email_activated_true(self):
        data = {
            'cat': self.category.id,
            'title': 'Saved Post name',
            'slug': 'saved-post-name',
            'body': 'Post text.',
            'tags': 'tag',
            'status': 'DF'
        }
        response = self.auth_email_activated_client.post(reverse('blog:post-new'), data=data, follow=True)

        self.assertTrue(response.status_code, 200)
        saved_post = Post.objects.get(title='Saved Post name')
        self.assertEqual(saved_post.cat, self.category)
        self.assertEqual(saved_post.title, data['title'])
        self.assertEqual(saved_post.slug, data['slug'])
        self.assertEqual(saved_post.body, data['body'])
        self.assertEqual(saved_post.status, data['status'])

    def test_post_create_view_auth_user_email_activated_false(self):
        data = {
            'cat': self.category.id,
            'title': 'Saved Post name email_activated_false',
            'slug': 'saved-post-name-emailactivatedfalse',
            'body': 'Post text.',
            'tags': 'tag',
            'status': 'DF'
        }
        with self.assertRaises(ValidationError):
            self.auth_client.post(reverse('blog:post-new'), data=data, follow=True)

    def test_post_update_view_not_auth_user(self):
        data = {
            'cat': self.category.id,
            'title': 'Название поста',
            'slug': 'nazvanie-posta',
            'body': 'Текст поста modif',
            'tags': 'tag',
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
            'tags': 'tag',
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
            'tags': 'tag',
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

    def test_post_update_view_queries(self):
        """ Тестируем количество запросов в БД. """
        data = {
            'cat': self.category.id,
            'title': 'Название поста queries',
            'slug': 'nazvanie-posta-queries',
            'body': 'Текст поста modif',
            'tags': 'tag'
        }
        with CaptureQueriesContext(connection) as queries:
            cache.delete('categories')  # может сохраниться от предыдущих запросов
            cache.delete('new_posts')
            cache.delete('tags')
            response = self.auth_client.post(reverse('blog:post-update', kwargs={'slug': 'nazvanie-posta'}), data=data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(queries), 10, "Увеличилось число запросов в БД!")

    def test_post_by_category_list_view(self):
        response = self.client.get(reverse('blog:category', kwargs={'slug': self.category.slug}))
        object_list = response.context.get('object_list')
        self.assertEqual(len(object_list), 1)  # только опубликованные посты

    def test_post_by_category_list_view_queries(self):
        """ Тестируем количество запросов в БД. """
        with CaptureQueriesContext(connection) as queries:
            cache.delete('categories')  # может сохраниться от предыдущих запросов
            cache.delete('new_posts')
            cache.delete('tags')
            response = self.client.get(reverse('blog:category', kwargs={'slug': self.category.slug}))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(queries), 5, "Увеличилось число запросов в БД!")

    def test_post_by_tag_list_view(self):
        response = self.client.get(reverse('blog:tag', kwargs={'slug': 'tag'}))
        object_list = response.context.get('object_list')
        self.assertEqual(len(object_list), 1)  # только опубликованные посты с указанным tag

    def test_post_by_tag_list_view_queries(self):
        """ Тестируем количество запросов в БД. """
        with CaptureQueriesContext(connection) as queries:
            cache.delete('categories')  # может сохраниться от предыдущих запросов
            cache.delete('new_posts')
            cache.delete('tags')
            response = self.client.get(reverse('blog:tag', kwargs={'slug': 'tag'}))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(queries), 5, "Увеличилось число запросов в БД!")

    def test_feedback_get(self):
        response = self.client.get(reverse('blog:feedback'))
        self.assertEqual(response.status_code, 200)

    def test_feedback_post(self):
        form_data = {
            'theme': 'Feedback',
            'text': 'Feedback text',
            'email': 'Feedback@mail.ru',
            'captcha_0': 'dummy-value',
            'captcha_1': 'PASSED'
        }
        response = self.client.post(reverse('blog:feedback'), data=form_data)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Ваше сообщение отправлено!')

    def test_search_view_title(self):
        form_data = {
            'searched': 'Название опубликованного поста'
        }
        response = self.client.post(reverse('blog:post-search'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('object_list')[0], self.post_published)

    def test_search_view_body(self):
        form_data = {
            'searched': 'Текст опубликованного поста'
        }
        response = self.client.post(reverse('blog:post-search'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('object_list')[0], self.post_published)

    def test_search_view_empty(self):
        form_data = {
            'searched': ''
        }
        expected_redirect_url = '/blog/'
        response = self.client.post(reverse('blog:post-search'), data=form_data)
        self.assertRedirects(response,
                             expected_url=expected_redirect_url,
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)

    def test_paginator(self):
        for post in range(25):
            Post.objects.create(
                user=self.user,
                cat=self.category,
                title=f'Test paginator {post}',
                slug=f'test-paginator-{post}',
                body=f'Test paginator text {post}',
                status='PB'
            )
        response = self.client.get(reverse('blog:home'))
        self.assertEqual(len(response.context.get('object_list')), 25, msg='Проверка первой страницы')
        response = self.client.get('/blog/?page=2')
        self.assertEqual(len(response.context.get('object_list')), 1, msg='Проверка второй страницы')

    def test_about_view(self):
        response = self.client.get(reverse('blog:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/about.html')
