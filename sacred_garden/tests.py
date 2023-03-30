from django.test import TestCase

from sacred_garden import models

from unittest import mock


class TestUserCreate(TestCase):

    @mock.patch('sacred_garden.models.get_new_invite_code')
    def test_invite_code_is_populated(self, mocked_get_new_invite_code):
        mocked_get_new_invite_code.return_value = 'QWE123'

        user = models.User()
        user.save()

        user = models.User.objects.get(pk=user.pk)
        self.assertEqual(user.partner_invite_code, 'QWE123')


class TestUserUpdate(TestCase):
    @mock.patch('sacred_garden.models.get_new_invite_code')
    def test_invite_code_is_not_updatecd(self, mocked_get_new_invite_code):
        mocked_get_new_invite_code.return_value = 'QWE123'

        user = models.User(partner_invite_code='ALPHA5')
        user.save()

        user = models.User.objects.get(pk=user.pk)
        user.save()

        user = models.User.objects.get(pk=user.pk)
        self.assertEqual(user.partner_invite_code, 'ALPHA5')


class TestConnectPartners(TestCase):

    def test_connect_partners(self):
        user1 = models.User(email='user1@example.com', partner_invite_code='CODE_1')
        user1.save()

        user2 = models.User(email='user2@example.com', partner_invite_code='CODE_2')
        user2.save()

        models.connect_partners(user1, user2)

        user1 = models.User.objects.get(pk=user1.pk)
        user2 = models.User.objects.get(pk=user2.pk)

        self.assertEqual(user1.partner_user, user2)
        self.assertEqual(user2.partner_user, user1)

        self.assertIsNone(user1.partner_invite_code)
        self.assertIsNone(user2.partner_invite_code)


class TestDisconnectPartners(TestCase):

    def test_disconnect_partners(self):
        user1 = models.User(email='user1@example.com', partner_invite_code='CODE_1')
        user1.save()

        user2 = models.User(email='user2@example.com', partner_invite_code='CODE_2')
        user2.save()

        models.connect_partners(user1, user2)
        models.disconnect_partners(user1, user2)

        user1 = models.User.objects.get(pk=user1.pk)
        user2 = models.User.objects.get(pk=user2.pk)

        self.assertIsNone(user1.partner_user)
        self.assertIsNone(user2.partner_user)

        self.assertIsNotNone(user1.partner_invite_code)
        self.assertIsNotNone(user2.partner_invite_code)
