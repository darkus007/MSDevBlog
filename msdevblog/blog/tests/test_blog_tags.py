from django.test import TestCase

from blog.templatetags.blog_tags import extra_space, FIELD_LENGTH


class BlogTagsTestCase(TestCase):  # python manage.py test blog.tests.test_blog_tags

    def test_extra_space(self):
        value = 'Some text'
        expected_len = FIELD_LENGTH + 1
        self.assertEqual(len(extra_space(value)), expected_len)
