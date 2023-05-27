from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse
from django.core.signing import Signer

signer = Signer()


class ViewsTestCase(TestCase):  # python manage.py test members.tests.test_views
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

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        settings.SECRET_KEY = None

    def test_user_registration_view(self):
        response = self.client.get('/members/login/')
        self.assertEqual(response.status_code, 200)

    def test_user_password_change_view_not_logged(self):
        response = self.client.get('/members/password/')
        self.assertRedirects(response,
                             expected_url='/members/login/?next=/members/password/',
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)

    def test_user_password_change_view_logged(self):
        response = self.auth_client.get('/members/password/')
        self.assertEqual(response.status_code, 200)

    def test_password_changed(self):
        response = self.auth_client.get('/members/password-success/')
        self.assertEqual(response.status_code, 200)

    def test_user_profile_get_page_not_logged(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response,
                             expected_url='/members/login/?next=/members/profile/',
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)

    def test_user_profile_get_page_logged(self):
        response = self.auth_client.get(reverse('profile'))
        # Проверка, что пользователь залогинился
        self.assertEqual(str(response.context['user']), 'test_user')
        self.assertEqual(response.status_code, 200)

    def test_user_update_profile_get_page_not_logged(self):
        response = self.client.get(reverse('update-profile'))
        self.assertRedirects(response,
                             expected_url='/members/login/?next=/members/update-profile/',
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)

    def test_user_update_profile_post_data_logged(self):
        form_data = {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'bio': 'About user',
            'git': 'www.github.com'
        }
        response = self.auth_client.post(reverse('update-profile'), data=form_data)

        self.assertRedirects(response,
                             expected_url='/members/profile/',
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'first_name')
        self.assertEqual(self.user.last_name, 'last_name')
        self.assertEqual(self.user.bio, 'About user')
        self.assertEqual(self.user.git, 'www.github.com')

    def test_user_email_activate_get(self):
        response = self.client.get(reverse('email-activate', kwargs={'sign': 'some'}))
        self.assertEqual(response.status_code, 405)

    def test_user_email_activate_post_bad_signature(self):
        response = self.client.post(reverse('email-activate', kwargs={'sign': 'some'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/bad_signature.html')

    def test_user_email_activate_post_activation_done(self):
        sign = signer.sign(self.user.username)
        response = self.client.post(reverse('email-activate', kwargs={'sign': sign}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/activation_done.html')

    def test_user_email_activate_post_user_is_activated(self):
        user = get_user_model().objects.create_user(username='test_user_is_email_activated',
                                                    email='test_is_email_activated@testsite.ru',
                                                    password='test_user_password',
                                                    is_email_activated=True)
        sign = signer.sign(user.username)
        response = self.client.post(reverse('email-activate', kwargs={'sign': sign}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/user_is_activated.html')

    def test_send_email_activate_letter_not_logged(self):
        response = self.client.get(reverse('repeat-send-email'))
        self.assertRedirects(response,
                             expected_url='/members/login/?next=/members/repeat-send-email/',
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)

    def test_send_email_activate_letter_logged(self):
        response = self.auth_client.get(reverse('repeat-send-email'))
        self.assertEqual(str(response.context['user']), 'test_user')
        self.assertRedirects(response,
                             expected_url=reverse('profile'),
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)
