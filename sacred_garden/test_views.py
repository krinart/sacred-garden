from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from sacred_garden import models


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

    def request_patch(self, urlname, urlargs=None, auth_user=None, data=None):
        url = reverse(urlname, args=urlargs)

        client = APIClient()
        if auth_user:
            client.force_authenticate(user=auth_user)

        return client.patch(url, data=data)

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

    def test_update_user_success(self):
        response = self.request_patch(
            'user-detail',
            urlargs=[self.user1.id],
            auth_user=self.user1,
            data={'first_name': 'Jon', 'partner_name': 'Eva'})
        self.assertSuccess(response)

        updated_user = models.User.objects.get(id=self.user1.id)
        self.assertEqual(updated_user.first_name, 'Jon')
        self.assertEqual(updated_user.partner_name, 'Eva')

    def test_update_user_unauthorized(self):
        response = self.request_patch(
            'user-detail',
            urlargs=[self.user1.id],
            data={'first_name': 'Jon', 'partner_name': 'Eva'})
        self.assertUnAuthorized(response)

        updated_user = models.User.objects.get(id=self.user1.id)
        self.assertEqual(updated_user.first_name, 'John')
        self.assertEqual(updated_user.partner_name, 'Eva_Love')

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
            'emotional_needs': [],
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
                'emotional_needs': [],
            },
            'partner_name': 'Eva_Love',
            'partner_invite_code': self.user1.partner_invite_code,
            'emotional_needs': [],
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
            data={'invite_code': 'USER2_CODE'},
            auth_user=self.user1)

        self.assertSuccess(response)

        self.assertPartnersConnected(self.user1, self.user2)

    def test_error_connect_partner_error_invalid_invite_code(self):
        response = self.request_post(
            'user-connect-partner',
            data={'invite_code': '123'},
            auth_user=self.user1)

        self.assertBadRequest(response)

        self.assertNoPartner(self.user1)
        self.assertNoPartner(self.user2)

    def test_error_connect_partner_error_partner_already_connected(self):
        user3 = models.User.objects.create(
            email='user3@example.com', partner_invite_code='USER3_CODE')

        models.connect_partners(self.user1, self.user2)

        response = self.request_post(
            'user-connect-partner',
            data={'invite_code': 'USER3_CODE'},
            auth_user=self.user1)

        self.assertBadRequest(response)

        self.assertPartnersConnected(self.user1, self.user2)
        self.assertNoPartner(user3)

    def test_connect_partner_self(self):
        response = self.request_post(
            'user-connect-partner',
            data={'invite_code': 'USER1_CODE'},
            auth_user=self.user1,
        )

        self.assertBadRequest(response)

        self.assertNoPartner(self.user1)
        self.assertNoPartner(self.user2)

    def test_error_connect_partner_unauthorized(self):
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


class TestEmotionalNeedViewSet(ApiTestCase):

    def setUp(self):
        self.user = models.User.objects.create(
            email='user1@example.com',
            first_name='John',
            partner_name='Eva_Love')

    def test_create_success(self):
        response = self.request_post(
            'emotionalneed-list', data={'name': 'Hug'}, auth_user=self.user)
        self.assertSuccess(response, expected_status_code=201)

        eneed = models.EmotionalNeed.objects.get()
        self.assertEqual(response.data, {'name': 'Hug', 'id': eneed.id})

    def test_unauthorized(self):
        response = self.request_post(
            'emotionalneed-list', data={'name': 'Hug'})
        self.assertUnAuthorized(response)

        self.assertEqual(models.EmotionalNeed.objects.count(), 0)


class TestEmotionalNeedValueViewSet(ApiTestCase):

    def setUp(self):
        self.user = models.User.objects.create(
            email='user1@example.com',
            first_name='John',
            partner_name='Eva_Love')

        self.eneed = models.EmotionalNeed.objects.create(
            user=self.user,
            name='Hug',
        )

    def test_create_with_partner_success(self):
        partner = models.User.objects.create()

        models.connect_partners(self.user, partner)

        response = self.request_post(
            'emotionalneedvalue-list',
            data={
                'emotional_need_id': self.eneed.id,
                'value': -2,
            },
            auth_user=self.user,
        )
        self.assertSuccess(response, expected_status_code=201)

        eneed = models.EmotionalNeed.objects.get()
        eneed_value = models.EmotionalNeedValue.objects.get()
        self.assertEqual(
            response.data,
            {'emotional_need_id': eneed.id, 'id': eneed_value.id, 'value': -2})

        self.assertEqual(eneed_value.value, -2)
        self.assertTrue(eneed_value.is_current)
        self.assertEqual(eneed_value.partner_user, partner)

    def test_create_no_partner_success(self):
        response = self.request_post(
            'emotionalneedvalue-list',
            data={
                'emotional_need_id': self.eneed.id,
                'value': -2,
            },
            auth_user=self.user,
        )
        self.assertSuccess(response, expected_status_code=201)

        eneed = models.EmotionalNeed.objects.get()
        eneed_value = models.EmotionalNeedValue.objects.get()
        self.assertEqual(
            response.data,
            {'emotional_need_id': eneed.id, 'id': eneed_value.id, 'value': -2})

        self.assertEqual(eneed_value.value, -2)
        self.assertTrue(eneed_value.is_current)
        self.assertIsNone(eneed_value.partner_user)

    def test_error_unathorized_access(self):
        other_user = models.User.objects.create()

        response = self.request_post(
            'emotionalneedvalue-list',
            data={
                'emotional_need_id': self.eneed.id,
                'value': -2,
            },
            auth_user=other_user,
        )
        self.assertBadRequest(response)
        self.assertEqual(models.EmotionalNeedValue.objects.count(), 0)

    def test_unauthorized(self):
        response = self.request_post(
            'emotionalneedvalue-list', data={
                'emotional_need_id': self.eneed.id,
                'value': -2,
            })
        self.assertUnAuthorized(response)

        self.assertEqual(models.EmotionalNeedValue.objects.count(), 0)
