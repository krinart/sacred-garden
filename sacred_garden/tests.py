from django.test import TestCase

from sacred_garden import models

from unittest import mock


class UserCreateTestCase(TestCase):

    @mock.patch('sacred_garden.models.get_new_invite_code')
    def test_invite_code_is_populated(self, mocked_get_new_invite_code):
        mocked_get_new_invite_code.return_value = 'QWE123'

        user = models.User()
        user.save()

        user = models.User.objects.get(pk=user.pk)
        self.assertEqual(user.partner_invite_code, 'QWE123')


class UserUpdateTestCase(TestCase):
    @mock.patch('sacred_garden.models.get_new_invite_code')
    def test_invite_code_is_not_updatecd(self, mocked_get_new_invite_code):
        mocked_get_new_invite_code.return_value = 'QWE123'

        user = models.User(partner_invite_code='ALPHA5')
        user.save()

        user = models.User.objects.get(pk=user.pk)
        user.save()

        user = models.User.objects.get(pk=user.pk)
        self.assertEqual(user.partner_invite_code, 'ALPHA5')
