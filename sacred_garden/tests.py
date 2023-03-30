from unittest import mock

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate, APIClient

from sacred_garden import models, views


class TestUserCreate(TestCase):

    @mock.patch('sacred_garden.models.get_new_invite_code')
    def test_invite_code_is_populated(self, mocked_get_new_invite_code):
        mocked_get_new_invite_code.return_value = 'QWE123'

        user = models.User.objects.create()

        user = models.User.objects.get(pk=user.pk)
        self.assertEqual(user.partner_invite_code, 'QWE123')


class TestUserUpdate(TestCase):
    @mock.patch('sacred_garden.models.get_new_invite_code')
    def test_invite_code_is_not_updated(self, mocked_get_new_invite_code):
        mocked_get_new_invite_code.return_value = 'QWE123'

        user = models.User.objects.create(first_name='Jon', partner_invite_code='ALPHA5')

        user.first_name = 'John'
        user.save()

        user = models.User.objects.get(pk=user.pk)
        self.assertEqual(user.partner_invite_code, 'ALPHA5')


class TestConnectPartners(TestCase):

    def test_connect_partners(self):
        user1 = models.User.objects.create(email='user1@example.com', partner_invite_code='CODE_1')
        user2 = models.User.objects.create(email='user2@example.com', partner_invite_code='CODE_2')

        models.connect_partners(user1, user2)

        user1 = models.User.objects.get(pk=user1.pk)
        user2 = models.User.objects.get(pk=user2.pk)

        self.assertEqual(user1.partner_user, user2)
        self.assertEqual(user2.partner_user, user1)

        self.assertIsNone(user1.partner_invite_code)
        self.assertIsNone(user2.partner_invite_code)


class TestDisconnectPartners(TestCase):

    def test_disconnect_partners(self):
        user1 = models.User.objects.create(email='user1@example.com', partner_invite_code='CODE_1')
        user2 = models.User.objects.create(email='user2@example.com', partner_invite_code='CODE_2')

        models.connect_partners(user1, user2)
        models.disconnect_partners(user1, user2)

        user1 = models.User.objects.get(pk=user1.pk)
        user2 = models.User.objects.get(pk=user2.pk)

        self.assertIsNone(user1.partner_user)
        self.assertIsNone(user2.partner_user)

        self.assertIsNotNone(user1.partner_invite_code)
        self.assertIsNotNone(user2.partner_invite_code)


class ApiTestCase(TestCase):

    def request_get(self, url, auth_user=None):
        client = APIClient()
        if auth_user:
            client.force_authenticate(user=auth_user)

        return client.get(url)

    def assertSuccess(self, actual_response, expected_response=None, expected_status_code=200):
        self.assertEqual(actual_response.status_code, expected_status_code)

    def assertUnAuthorized(self, actual_response):
        pass


class TestUserViewSet(ApiTestCase):

    def setUp(self):
        self.user1 = models.User.objects.create(
            email='user1@example.com',
            first_name='John',
            partner_name='Eva_Love')

        self.user2 = models.User.objects.create(
            email='user2@example.com',
            first_name='Eva',
            partner_name='John_Love')

    def test_unauthorized(self):
        response = self.request_get('/api/sacred_garden/v1/users/me/')
        self.assertUnAuthorized(response)

    def test_success_without_partner(self):
        response = self.request_get('/api/sacred_garden/v1/users/me/', auth_user=self.user1)
        self.assertSuccess(response)

    def test_success_with_partner(self):
        models.connect_partners(self.user1, self.user2)
        response = self.request_get('/api/sacred_garden/v1/users/me/', auth_user=self.user1)
        self.assertSuccess(response)
