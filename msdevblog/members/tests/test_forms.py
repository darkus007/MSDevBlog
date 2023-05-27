from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.conf import settings

from captcha.conf import settings as captcha_settings

from members.forms import UserRegistrationForm, UserProfileForm, UserPasswordChangeForm


class FormsTestCaseSettings(TestCase):  # python manage.py test members.tests.test_forms
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.client = Client()
        cls.user = get_user_model().objects.create_user(username='test_user',
                                                        email='test@testsite.ru',
                                                        password='test_user_password')
        settings.SECRET_KEY = "some_test_secret_key!"
        captcha_settings.CAPTCHA_TEST_MODE = True  # отключаем проверку captcha

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        settings.SECRET_KEY = None
        captcha_settings.CAPTCHA_TEST_MODE = False


class UserRegistrationFormTestCase(FormsTestCaseSettings):
    def test_save(self):
        form_data = {
            'username': 'test_user_form',
            'email': 'test2@testsite.ru',
            'password1': 'Password1$',
            'password2': 'Password1$',
            'captcha_0': 'dummy-value',
            'captcha_1': 'PASSED'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertTrue(get_user_model().objects.filter(username='test_user_form'))

    def test_is_email_activated_false(self):
        form_data = {
            'username': 'test_user_form2',
            'email': 'test3@testsite.ru',
            'is_email_activated': True,
            'password1': 'Password1$',
            'password2': 'Password1$',
            'captcha_0': 'dummy-value',
            'captcha_1': 'PASSED'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        saved_user = get_user_model().objects.get(username='test_user_form2')
        self.assertFalse(saved_user.is_email_activated)


class UserProfileFormTestCase(FormsTestCaseSettings):
    def test_fields_validation(self):
        form_data = {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'bio': 'About user',
            'git': 'www.github.com'
        }
        form = UserProfileForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)


class UserPasswordChangeFormTestCase(FormsTestCaseSettings):
    def test_save(self):
        form_data = {
            'old_password': 'test_user_password',
            'new_password1': 'Password2$',
            'new_password2': 'Password2$',
        }
        form = UserPasswordChangeForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        saved_user = get_user_model().objects.get(username='test_user')
        self.assertTrue(saved_user.check_password('Password2$'))
        