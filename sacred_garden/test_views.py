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

    def request_put(self, urlname, urlargs=None, auth_user=None, data=None):
        url = reverse(urlname, args=urlargs)

        client = APIClient()
        if auth_user:
            client.force_authenticate(user=auth_user)

        return client.put(url, data=data)

    def request_delete(self, urlname, urlargs=None, auth_user=None):
        url = reverse(urlname, args=urlargs)

        client = APIClient()
        if auth_user:
            client.force_authenticate(user=auth_user)

        return client.delete(url)

    def assertSuccess(self, response, expected_data=None, expected_status_code=200):
        self.assertEqual(response.status_code, expected_status_code, response.data)

        if expected_data is not None:
            self.assertEqual(response.data, expected_data)

    def assertBadRequest(self, response):
        self.assertEqual(response.status_code, 400)

    def assertUnAuthorized(self, response):
        self.assertEqual(response.status_code, 401)

    def assertForbidden(self, response):
        self.assertEqual(response.status_code, 403)


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
            email='user1@example.com')

        self.partner = models.User.objects.create(
            email='user2@example.com')

    def test_create_success_no_initial_status(self):
        response = self.request_post(
            'emotionalneed-list',
            data={'name': 'Hug', 'state_value_type': 0},
            auth_user=self.user)
        self.assertSuccess(response, expected_status_code=201)

        eneed = models.EmotionalNeed.objects.get()
        self.assertEqual(response.data, {'name': 'Hug', 'id': eneed.id, 'state_value_type': 0})

        self.assertEqual(models.EmotionalNeedState.objects.count(), 0)

    def test_create_success_with_initial_status(self):
        response = self.request_post(
            'emotionalneed-list',
            data={'name': 'Hug', 'state_value_type': 0, 'initial_status': 0},
            auth_user=self.user)
        self.assertSuccess(response, expected_status_code=201)

        eneed = models.EmotionalNeed.objects.get()
        self.assertEqual(response.data, {'name': 'Hug', 'id': eneed.id, 'state_value_type': 0})

        self.assertEqual(models.EmotionalNeedState.objects.count(), 1)

    def test_create_unauthorized(self):
        response = self.request_post(
            'emotionalneed-list', data={'name': 'Hug'})
        self.assertUnAuthorized(response)

        self.assertEqual(models.EmotionalNeed.objects.count(), 0)

    def test_history_self_success(self):
        eneed = models.EmotionalNeed.objects.create(user=self.user, name='Hugs', state_value_type=0)

        ens1 = models.create_emotional_need_state(self.user, eneed, -1, None, 0, "", "")
        ens2 = models.create_emotional_need_state(self.user, eneed, -1, None, 0, "", "")
        models.connect_partners(self.user, self.partner)
        ens3 = models.create_emotional_need_state(self.user, eneed, 1, None, 0, "", "")

        response = self.request_get(
            'emotionalneed-state-history', urlargs=[eneed.id], auth_user=self.user)
        self.assertSuccess(response, expected_status_code=200)

        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['id'], ens1.id)
        self.assertEqual(response.data[1]['id'], ens2.id)
        self.assertEqual(response.data[2]['id'], ens3.id)

    def test_history_partner_success(self):
        eneed = models.EmotionalNeed.objects.create(user=self.user, name='Hugs', state_value_type=0)

        ens1 = models.create_emotional_need_state(self.user, eneed, -1, 1, 0, "", "")
        ens2 = models.create_emotional_need_state(self.user, eneed, -1, 1, 0, "", "")
        models.connect_partners(self.user, self.partner)
        ens3 = models.create_emotional_need_state(self.user, eneed, 1, 0, 0, "", "")

        response = self.request_get(
            'emotionalneed-state-history', urlargs=[eneed.id], auth_user=self.partner)
        self.assertSuccess(response, expected_status_code=200)

        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['id'], ens2.id)
        self.assertEqual(response.data[1]['id'], ens3.id)

    def test_history_forbidden(self):
        eneed = models.EmotionalNeed.objects.create(user=self.user, name='Hugs', state_value_type=0)
        response = self.request_get(
            'emotionalneed-state-history', urlargs=[eneed.id], auth_user=self.partner)
        self.assertForbidden(response)

    def test_get_success(self):
        eneed = models.EmotionalNeed.objects.create(user=self.user, name='Hugs', state_value_type=0)

        ens1 = models.create_emotional_need_state(self.user, eneed, -1, None, 0, "", "")
        ens2 = models.create_emotional_need_state(self.user, eneed, -2, None, 0, "", "")

        response = self.request_get(
            'emotionalneed-detail', urlargs=[eneed.id], auth_user=self.user)
        self.assertSuccess(response)

        data = response.data

        del data['current_state']['created_at']

        self.assertEqual(
            data,
            {
                'id': eneed.id,
                'name': 'Hugs',
                'state_value_type': 0,
                'current_state': {
                    'id': ens2.id,
                    'emotional_need_id': eneed.id,
                    'status': -2,
                    'is_initial_state': False,
                    'value_abs': None,
                    'value_rel': 0,
                    'text': '',
                    'appreciation_text': '',
                }
            }
        )

    def test_get_success_as_partner(self):
        models.connect_partners(self.user, self.partner)
        eneed = models.EmotionalNeed.objects.create(user=self.user, name='Hugs', state_value_type=0)

        ens1 = models.create_emotional_need_state(self.user, eneed, -1, None, 0, "", "")
        ens2 = models.create_emotional_need_state(self.user, eneed, -2, None, 0, "", "")

        response = self.request_get(
            'emotionalneed-detail', urlargs=[eneed.id], auth_user=self.partner)
        self.assertSuccess(response)

        data = response.data

        del data['current_state']['created_at']

        self.assertEqual(
            data,
            {
                'id': eneed.id,
                'name': 'Hugs',
                'state_value_type': 0,
                'current_state': {
                    'id': ens2.id,
                    'emotional_need_id': eneed.id,
                    'status': -2,
                    'value_abs': None,
                    'value_rel': 0,
                    'is_initial_state': False,
                    'text': '',
                    'appreciation_text': '',
                }
            }
        )

    def test_get_forbidden(self):
        eneed = models.EmotionalNeed.objects.create(user=self.user, name='Hugs', state_value_type=0)

        ens1 = models.create_emotional_need_state(self.user, eneed, -1, None, 0, "", "")
        ens2 = models.create_emotional_need_state(self.user, eneed, -2, None, 0, "", "")

        response = self.request_get(
            'emotionalneed-detail', urlargs=[eneed.id], auth_user=self.partner)
        self.assertForbidden(response)


class TestEmotionalNeedStateViewSet(ApiTestCase):

    def setUp(self):
        self.user = models.User.objects.create(
            email='user1@example.com',
            first_name='John',
            partner_name='Eva_Love')

        self.eneed = models.EmotionalNeed.objects.create(
            user=self.user,
            name='Hug',
            state_value_type=0,
        )

    def test_create_with_partner_success(self):
        partner = models.User.objects.create()

        models.connect_partners(self.user, partner)

        response = self.request_post(
            'emotionalneedstate-list',
            data={
                'emotional_need_id': self.eneed.id,
                'status': -20,
                'value_rel': 1,
                'text': 'Please help',
                'appreciation_text': 'I love you',
            },
            auth_user=self.user,
        )
        self.assertSuccess(response, expected_status_code=201)
        del response.data['created_at']

        eneed = models.EmotionalNeed.objects.get()
        eneed_status = models.EmotionalNeedState.objects.get(id=response.data['id'])
        self.assertEqual(
            response.data,
            {'emotional_need_id': eneed.id, 'id': eneed_status.id, 'status': -20,
             'text': 'Please help', 'appreciation_text': 'I love you',
             'value_rel': 1, 'value_abs': None, 'is_initial_state': False})

        self.assertEqual(eneed_status.status, -20)
        self.assertTrue(eneed_status.is_current)
        self.assertEqual(eneed_status.partner_user, partner)

    def test_create_no_partner_success(self):
        response = self.request_post(
            'emotionalneedstate-list',
            data={
                'emotional_need_id': self.eneed.id,
                'status': -20,
                'text': 'Please help',
                'appreciation_text': 'I love you',
                'value_rel': 1,
            },
            auth_user=self.user,
        )
        self.assertSuccess(response, expected_status_code=201)
        del response.data['created_at']

        eneed = models.EmotionalNeed.objects.get()
        eneed_status = models.EmotionalNeedState.objects.get(id=response.data['id'])
        self.assertEqual(
            response.data,
            {'emotional_need_id': eneed.id, 'id': eneed_status.id, 'status': -20,
             'text': 'Please help', 'appreciation_text': 'I love you',
             'value_rel': 1, 'value_abs': None, 'is_initial_state': False,})

        self.assertEqual(eneed_status.status, -20)
        self.assertTrue(eneed_status.is_current)
        self.assertIsNone(eneed_status.partner_user)

    def test_create_error_forbidden(self):
        other_user = models.User.objects.create()

        response = self.request_post(
            'emotionalneedstate-list',
            data={
                'emotional_need_id': self.eneed.id,
                'status': -10,
                'text': 'Please help',
                'appreciation_text': 'I love you',
                'value_abs': 1,
                'value_rel': 1,
            },
            auth_user=other_user,
        )

        self.assertForbidden(response)
        self.assertEqual(models.EmotionalNeedState.objects.count(), 0)

    def test_create_unauthorized(self):
        response = self.request_post(
            'emotionalneedstate-list', data={
                'emotional_need_id': self.eneed.id,
                'status': -2,
                'text': 'Please help'
            })
        self.assertUnAuthorized(response)

        self.assertEqual(models.EmotionalNeedState.objects.count(), 0)

    def test_delete_success(self):
        ens = models.create_emotional_need_state(self.user, self.eneed, -10, 0, 0, "", "")

        response = self.request_delete(
            'emotionalneedstate-detail', urlargs=[ens.id], auth_user=self.user)
        self.assertSuccess(response, expected_status_code=204)

        self.assertEqual(models.EmotionalNeedState.objects.count(), 0)

    def test_delete_forbidden(self):
        other_user = models.User.objects.create(email='user2@example.com')
        ens = models.create_emotional_need_state(self.user, self.eneed, -10, 0, 0, "", "")

        response = self.request_delete(
            'emotionalneedstate-detail', urlargs=[ens.id], auth_user=other_user)
        self.assertForbidden(response)

        self.assertEqual(models.EmotionalNeedState.objects.count(), 1)

    def test_delete_unauthorized(self):
        ens = models.create_emotional_need_state(self.user, self.eneed, -10, 0, 0, "", "")

        response = self.request_delete(
            'emotionalneedstate-detail', urlargs=[ens.id])
        self.assertUnAuthorized(response)

        self.assertEqual(models.EmotionalNeedState.objects.count(), 1)

    def test_update_success(self):
        ens = models.create_emotional_need_state(self.user, self.eneed, -10, 0, 0, "", "")

        response = self.request_put(
            'emotionalneedstate-detail',
            urlargs=[ens.id],
            data={
                'status': -20,
                'value_rel': 1,
                'text': 'Please help',
                'appreciation_text': 'I love you',
            },
            auth_user=self.user,
        )
        self.assertSuccess(response, expected_status_code=200)

        updated_ens = models.EmotionalNeedState.objects.get()
        self.assertEqual(updated_ens.status, -20)
        self.assertEqual(updated_ens.value_rel, 1)
        self.assertEqual(updated_ens.text, 'Please help')
        self.assertEqual(updated_ens.appreciation_text, 'I love you')

    def test_update_emotional_need_id_is_ignored(self):
        ens = models.create_emotional_need_state(self.user, self.eneed, -10, 0, 0, "", "")

        response = self.request_put(
            'emotionalneedstate-detail',
            urlargs=[ens.id],
            data={
                'status': -20,
                'value_rel': 1,
                'text': 'Please help',
                'appreciation_text': 'I love you',
                'emotional_need_id': 20,
            },
            auth_user=self.user,
        )
        self.assertSuccess(response, expected_status_code=200)

        updated_ens = models.EmotionalNeedState.objects.get()
        self.assertEqual(updated_ens.status, -20)
        self.assertEqual(updated_ens.value_rel, 1)
        self.assertEqual(updated_ens.text, 'Please help')
        self.assertEqual(updated_ens.appreciation_text, 'I love you')

    def test_update_forbidden(self):
        other_user = models.User.objects.create(email='user2@example.com')
        ens = models.create_emotional_need_state(self.user, self.eneed, -10, 0, 0, "", "")

        response = self.request_put(
            'emotionalneedstate-detail',
            urlargs=[ens.id],
            data={
                'status': -20,
                'value_rel': 1,
                'text': 'Please help',
                'appreciation_text': 'I love you',
            },
            auth_user=other_user,
        )
        self.assertForbidden(response)

        updated_ens = models.EmotionalNeedState.objects.get()
        self.assertEqual(updated_ens.status, -10)
        self.assertEqual(updated_ens.value_rel, 0)
        self.assertEqual(updated_ens.text, '')
        self.assertEqual(updated_ens.appreciation_text, '')
