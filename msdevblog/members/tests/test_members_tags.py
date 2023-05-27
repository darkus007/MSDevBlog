from django.test import TestCase

from members.templatetags.members_tags import value_or_empty


class MembersTagsTestCase(TestCase):  # python manage.py test members.tests.test_members_tags

    def test_value_or_empty__value_passed(self):
        value = 'Some text'
        self.assertEqual(value_or_empty(value), value)

    def test_value_or_empty__empty_passed(self):
        self.assertEqual(value_or_empty([]), '----------------')
