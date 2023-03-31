from unittest import mock

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from sacred_garden import models


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


class TestDisconnectPartner(TestCase):

    def test_disconnect_partner(self):
        user1 = models.User.objects.create(email='user1@example.com', partner_invite_code='CODE_1')
        user2 = models.User.objects.create(email='user2@example.com', partner_invite_code='CODE_2')

        models.connect_partners(user1, user2)
        models.disconnect_partner(user1)

        user1 = models.User.objects.get(pk=user1.pk)
        user2 = models.User.objects.get(pk=user2.pk)

        self.assertIsNone(user1.partner_user)
        self.assertIsNone(user2.partner_user)

        self.assertIsNotNone(user1.partner_invite_code)
        self.assertIsNotNone(user2.partner_invite_code)


class ApiTestCase(TestCase):

    def request_get(self, urlname, urlargs=None, auth_user=None):
        url = reverse(urlname, args=urlargs)

        client = APIClient()
        if auth_user:
            client.force_authenticate(user=auth_user)

        return client.get(url)

    def request_post(self, urlname, urlargs=None, auth_user=None, data=None):
        url = reverse(urlname, args=urlargs)

        client = APIClient()
        if auth_user:
            client.force_authenticate(user=auth_user)

        return client.post(url, data=data)

    def assertSuccess(self, response, expected_data=None, expected_status_code=200):
        self.assertEqual(response.status_code, expected_status_code, response.data)

        if expected_data is not None:
            self.assertEqual(response.data, expected_data)

    def assertBadRequest(self, response):
        self.assertEqual(response.status_code, 400)

    def assertUnAuthorized(self, response):
        self.assertEqual(response.status_code, 401)


class TestUserViewSet(ApiTestCase):

    def setUp(self):
        self.user1 = models.User.objects.create(
            email='user1@example.com',
            first_name='John',
            partner_name='Eva_Love',
            partner_invite_code='USER1_CODE')

        self.user2 = models.User.objects.create(
            email='user2@example.com',
            first_name='Eva',
            partner_name='John_Love',
            partner_invite_code='USER2_CODE')

    def test_me_unauthorized(self):
        response = self.request_get('user-me')
        self.assertUnAuthorized(response)

    def test_me_success_without_partner(self):
        response = self.request_get('user-me', auth_user=self.user1)

        expected_data = {
            'id': self.user1.id,
            'first_name': 'John',
            'partner_user': None,
            'partner_name': 'Eva_Love',
            'partner_invite_code': self.user1.partner_invite_code,
        }

        self.assertSuccess(response, expected_data=expected_data)

    def test_me_success_with_partner(self):
        models.connect_partners(self.user1, self.user2)
        response = self.request_get('user-me', auth_user=self.user1)

        expected_data = {
            'id': self.user1.id,
            'first_name': 'John',
            'partner_user': {
                'id': self.user2.id,
                'first_name': self.user2.first_name,
            },
            'partner_name': 'Eva_Love',
            'partner_invite_code': self.user1.partner_invite_code,
        }

        self.assertSuccess(response, expected_data=expected_data)

    def assertPartnersConnected(self, user1, user2):
        user1 = models.User.objects.get(id=user1.id)
        user2 = models.User.objects.get(id=user2.id)

        self.assertEqual(user1.partner_user, user2)
        self.assertEqual(user2.partner_user, user1)

    def assertNoPartner(self, user):
        user = models.User.objects.get(id=user.id)
        self.assertIsNone(user.partner_user)

    def test_connect_partner_success(self):
        response = self.request_post(
            'user-connect-partner',
            auth_user=self.user1,
            data={'invite_code': 'USER2_CODE'})

        self.assertSuccess(response)

        self.assertPartnersConnected(self.user1, self.user2)

    def test_connect_partner_error_invalid_invite_code(self):
        response = self.request_post(
            'user-connect-partner',
            auth_user=self.user1,
            data={'invite_code': '123'})

        self.assertBadRequest(response)

        self.assertNoPartner(self.user1)
        self.assertNoPartner(self.user2)

    def test_connect_partner_error_partner_already_connected(self):
        user3 = models.User.objects.create(
            email='user3@example.com', partner_invite_code='USER3_CODE')

        models.connect_partners(self.user1, self.user2)

        response = self.request_post(
            'user-connect-partner',
            auth_user=self.user1,
            data={'invite_code': 'USER3_CODE'})

        self.assertBadRequest(response)

        self.assertPartnersConnected(self.user1, self.user2)
        self.assertNoPartner(user3)

    def test_connect_partner_unauthorized(self):
        response = self.request_post(
            'user-connect-partner',
            data={'invite_code': 'USER2_CODE'})

        self.assertUnAuthorized(response)

        self.assertNoPartner(self.user1)
        self.assertNoPartner(self.user2)

    def test_disconnect_partner_success(self):
        models.connect_partners(self.user1, self.user2)

        response = self.request_post(
            'user-disconnect-partner',
            auth_user=self.user1)

        self.assertSuccess(response)

        self.assertNoPartner(self.user1)
        self.assertNoPartner(self.user2)

    def test_disconnect_partner_error_no_partner(self):
        response = self.request_post(
            'user-disconnect-partner',
            auth_user=self.user1)

        self.assertBadRequest(response)

        self.assertNoPartner(self.user1)
        self.assertNoPartner(self.user2)

    def test_disconnect_partner_unauthorized(self):
        response = self.request_post('user-disconnect-partner')

        self.assertUnAuthorized(response)

        self.assertNoPartner(self.user1)
        self.assertNoPartner(self.user2)
